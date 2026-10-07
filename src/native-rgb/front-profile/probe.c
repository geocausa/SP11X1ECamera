/* SPDX-License-Identifier: GPL-2.0-only
 * Development-only hardware NV12 check. Pixel files stay private on SP11.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <limits.h>
#include <openssl/sha.h>
#include "../native-front-profile.h"
#include "../native-front-stats.h"
#include "../native-front-params.h"
#include "../../front-imx681/userspace/runtime/native-stats3a.h"
#define BUFFERS 4U
#define FRAMES 80U
#define BYTES 5529600U
#define Y_BYTES 3686400U
#define IQ_ID (V4L2_CID_USER_BASE + 0x1240)
#define PARAM_ID (V4L2_CID_USER_BASE + 0x1243)
#define TYPE V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
#define D "/var/lib/sp11-camera-native-profile-20261007-01/"
static int call(int fd, unsigned long command, void *value)
{
	int rc;
	do rc = ioctl(fd, command, value); while (rc < 0 && errno == EINTR);
	return rc;
}
static int boot_allowed(void)
{
	char line[8192];
	FILE *f = fopen("/proc/cmdline", "r");
	if (!f)
		return 0;
	char *got = fgets(line, sizeof(line), f);
	fclose(f);
	if (!got)
		return 0;
	int token = 0, entry = 0;
	for (char *p = strtok(line, " \n"); p; p = strtok(NULL, " \n")) {
		token |= !strcmp(p, "sp11_camera_native_profile_20261007_01=1");
		entry |= !strcmp(p, "sp11_entry=7.1.5-sp11-camera-native-profile-20261007-01");
	}
	return token && entry;
}
static unsigned short base_demux[4];
static void put_le(unsigned char *p, unsigned offset, unsigned long long value, unsigned n)
{
    for (unsigned i = 0; i < n; i++)
        p[offset + i] = value >> (8*i);
}
static int params(unsigned char packet[64], unsigned request)
{
    memset(packet, 0, 64);
    put_le(packet, 0, NATIVE_FRONT_PARAMS_MAGIC, 4);
    put_le(packet, 4, 1, 2);
    put_le(packet, 6, 64, 2);
    put_le(packet, 8, request, 8);
    /* A measured gain step: repeat the complete per-frame overlay, then reset. */
    if (request >= 32 && request < 64) {
        put_le(packet, 16, NATIVE_FRONT_PARAMS_DEMUX, 4);
        for (unsigned i = 0; i < 4; i++)
            put_le(packet, 24 + 2*i, 2 * base_demux[i], 2);
    }
    return native_front_params_validate(packet, 64);
}
static int reject(int fd, struct v4l2_ext_controls *controls, int expected)
{
    int rc = call(fd, VIDIOC_S_EXT_CTRLS, controls);
    return rc == -1 && errno == expected ? 0 : -1;
}
/* Restore the original file before returning even when a negative case fails.
 * The one-use root service also restores from its verified private copy if this
 * process is killed. No system suspend/hibernate or firmware-cache test is used.
 */
static int reject_profiles(int fd, struct v4l2_ext_controls *controls,
                           const char *name, unsigned char *profile)
{
    char backup[PATH_MAX];
    struct stat st;
    int wfd = -1, rc = -1;
    if (snprintf(backup, sizeof(backup), "%s.native-profile-negative", name) >= (int)sizeof(backup) ||
        lstat(backup, &st) == 0 || errno != ENOENT || rename(name, backup))
        return -1;
    if (reject(fd, controls, ENOENT))
        goto restore;
    wfd = open(name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (wfd < 0)
        goto restore;
    profile[NATIVE_FRONT_PROFILE_BYTES-1] ^= 1;
    size_t have = 0;
    while (have < NATIVE_FRONT_PROFILE_BYTES) {
        ssize_t n = write(wfd, profile+have, NATIVE_FRONT_PROFILE_BYTES-have);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) break;
        have += n;
    }
    profile[NATIVE_FRONT_PROFILE_BYTES-1] ^= 1;
    if (have != NATIVE_FRONT_PROFILE_BYTES || fsync(wfd))
        goto restore;
    if (close(wfd)) { wfd = -1; goto restore; }
    wfd = -1;
    rc = reject(fd, controls, EKEYREJECTED);
restore:
    if (wfd >= 0) close(wfd);
    if (unlink(name) && errno != ENOENT) rc = -1;
    if (rename(backup, name)) rc = -1;
    return rc;
}
struct plane_stats {
	unsigned min, max;
	unsigned long zero, full, poison;
	double mean;
};
static struct plane_stats stats(const unsigned char *p, unsigned n)
{
	struct plane_stats s = { .min = 255 };
	unsigned long long sum = 0;
	for (unsigned i = 0; i < n; i++) {
		unsigned v = p[i];
		if (v < s.min) s.min = v;
		if (v > s.max) s.max = v;
		sum += v;
		s.zero += !v;
		s.full += v == 255;
		s.poison += v == 0xa5;
	}
	s.mean = (double)sum / n;
	return s;
}
int main(int argc, char **argv)
{
	void *memory[BUFFERS] = { 0 };
	unsigned lengths[BUFFERS] = { 0 };
	struct plane_stats ys[FRAMES], cs[FRAMES];
	int fd = -1, sfd = -1, cfd = -1, mfd = -1, rc = 1, streaming = 0, meta_streaming = 0;
    void *meta_memory[BUFFERS] = { 0 };
    unsigned meta_lengths[BUFFERS] = { 0 };
    unsigned meta_completed = 0;
    uint64_t meta_stream = 0;
    unsigned meta_source_base = 0;
    float frame_lumas[FRAMES];
	unsigned completed = 0, held = 0;
	const char *phase = "dedicated_boot_guard";
	unsigned char profile[NATIVE_FRONT_PROFILE_BYTES];
	enum v4l2_buf_type type = TYPE;
	struct stat st;
	struct v4l2_format fmt = { .type = TYPE };
	struct v4l2_requestbuffers req = { .count = BUFFERS, .type = TYPE, .memory = V4L2_MEMORY_MMAP };
	double times[FRAMES];
	unsigned indices[FRAMES];

	if (argc != 5 || geteuid() || !boot_allowed())
		return 1; /* Refuse Golden before opening any device or pixel file. */
    phase = "data_only_profile_read";
    cfd = open(argv[3], O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (cfd < 0 || fstat(cfd, &st) || !S_ISREG(st.st_mode) || st.st_size != NATIVE_FRONT_PROFILE_BYTES)
        goto out;
    size_t have = 0;
    while (have < NATIVE_FRONT_PROFILE_BYTES) {
        ssize_t n = read(cfd, profile+have, NATIVE_FRONT_PROFILE_BYTES-have);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) goto out;
        have += n;
    }
    unsigned char digest[32];
    if (!SHA256(profile, sizeof(profile), digest) ||
        native_front_profile_validate(profile, sizeof(profile), digest))
        goto out;
    unsigned reg0 = native_nv12_le32(profile+NATIVE_FRONT_PROFILE_DEMUX_OFFSET);
    unsigned reg1 = native_nv12_le32(profile+NATIVE_FRONT_PROFILE_DEMUX_OFFSET+4);
    base_demux[0] = reg0 >> 16;
    base_demux[1] = reg0 & 0xffff;
    base_demux[2] = reg1 & 0xffff;
    base_demux[3] = reg1 >> 16;
    for (unsigned i = 0; i < 4; i++) {
        if (!base_demux[i] || base_demux[i] > 0x3fff)
            goto out;
    }
	phase = "sensor_controls";
	sfd = open(argv[2], O_RDWR | O_NOFOLLOW | O_CLOEXEC);
	if (sfd < 0 || fstat(sfd, &st) || !S_ISCHR(st.st_mode))
		goto out;
	struct v4l2_ext_control sensor_values[4] = {
		{ .id = V4L2_CID_VBLANK, .value = 1394 },
		{ .id = V4L2_CID_EXPOSURE, .value = 1000 },
		{ .id = V4L2_CID_ANALOGUE_GAIN, .value = 0 },
		{ .id = V4L2_CID_DIGITAL_GAIN, .value = 256 },
	};
	struct v4l2_ext_controls sensor_controls = {
		.count = 4, .controls = sensor_values, .which = V4L2_CTRL_WHICH_CUR_VAL,
	};
	if (call(sfd, VIDIOC_S_EXT_CTRLS, &sensor_controls))
		goto out;
	close(sfd); sfd = -1;

	phase = "video_format";
	fd = open(argv[1], O_RDWR | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
	if (fd < 0 || fstat(fd, &st) || !S_ISCHR(st.st_mode) || call(fd, VIDIOC_G_FMT, &fmt))
		goto out;
	struct v4l2_pix_format_mplane *p = &fmt.fmt.pix_mp;
	if (p->width != 2560 || p->height != 1440 || p->pixelformat != V4L2_PIX_FMT_NV12 ||
	    p->num_planes != 1 || p->plane_fmt[0].bytesperline != 2560 ||
	    p->plane_fmt[0].sizeimage != BYTES)
		goto out;
    phase = "raw_command_control_absent";
    struct v4l2_query_ext_ctrl raw_query = { .id = IQ_ID };
    if (call(fd, VIDIOC_QUERY_EXT_CTRL, &raw_query) != -1 || errno != EINVAL)
        goto out;
    unsigned char packet[64], bad[64];
    struct v4l2_ext_control param = { .id = PARAM_ID, .size = 64, .ptr = packet };
    struct v4l2_ext_controls param_controls = {
        .count = 1, .controls = &param, .which = V4L2_CTRL_WHICH_CUR_VAL
    };
    phase = "typed_negative_controls";
    if (params(packet, 5))
        goto out;
    memcpy(bad, packet, 64); param.ptr = bad;
    put_le(bad, 16, 8, 4); /* Unknown update flag. */
    if (reject(fd, &param_controls, EINVAL))
        goto out;
    memcpy(bad, packet, 64); put_le(bad, 20, 1, 4);
    if (reject(fd, &param_controls, EINVAL))
        goto out;
    memcpy(bad, packet, 64); put_le(bad, 16, 1, 4);
    for (unsigned i = 0; i < 4; i++) put_le(bad, 24 + 2*i, 1024, 2);
    put_le(bad, 24, 0x8000, 2);
    if (reject(fd, &param_controls, ERANGE))
        goto out;
    memcpy(bad, packet, 64); put_le(bad, 16, 4, 4);
    if (reject(fd, &param_controls, EINVAL))
        goto out;
    param.ptr = packet;
    phase = "missing_and_corrupt_profile_rejected";
    if (reject_profiles(fd, &param_controls, argv[3], profile))
        goto out;
    phase = "typed_initial_parameters";
    for (unsigned request = 5; request <= 8; request++) {
        if (params(packet, request) || call(fd, VIDIOC_S_EXT_CTRLS, &param_controls))
            goto out;
    }
	if (call(fd, VIDIOC_REQBUFS, &req) || req.count != BUFFERS) {
		goto out;
	}
	phase = "buffer_allocate_and_queue";
	for (unsigned i = 0; i < BUFFERS; i++) {
		struct v4l2_plane plane = { 0 };
		struct v4l2_buffer b = { .type = TYPE, .memory = V4L2_MEMORY_MMAP,
			.index = i, .length = 1, .m.planes = &plane };
		if (call(fd, VIDIOC_QUERYBUF, &b) || plane.length < BYTES)
			goto out;
		memory[i] = mmap(NULL, plane.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, plane.m.mem_offset);
		if (memory[i] == MAP_FAILED) { memory[i] = NULL; goto out; }
		lengths[i] = plane.length;
		memset(memory[i], 0xa5, BYTES); /* Detect an untouched DMA region. */
		if (call(fd, VIDIOC_QBUF, &b))
			goto out;
	}
    phase = "metadata_allocate";
    mfd = open(argv[4], O_RDWR | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    struct v4l2_capability mcap = { 0 };
    struct v4l2_format mfmt = { .type = V4L2_BUF_TYPE_META_CAPTURE };
    struct v4l2_requestbuffers mreq = {
        .count = BUFFERS, .type = V4L2_BUF_TYPE_META_CAPTURE, .memory = V4L2_MEMORY_MMAP
    };
    enum v4l2_buf_type mtype = V4L2_BUF_TYPE_META_CAPTURE;
    if (mfd < 0 || fstat(mfd, &st) || !S_ISCHR(st.st_mode) ||
        call(mfd, VIDIOC_QUERYCAP, &mcap) ||
        !(mcap.device_caps & V4L2_CAP_META_CAPTURE) ||
        call(mfd, VIDIOC_G_FMT, &mfmt) ||
        mfmt.fmt.meta.dataformat != NATIVE_FRONT_STATS_MAGIC ||
        mfmt.fmt.meta.buffersize != NATIVE_FRONT_STATS_BYTES ||
        call(mfd, VIDIOC_REQBUFS, &mreq) || mreq.count != BUFFERS)
        goto out;
    for (unsigned i = 0; i < BUFFERS; i++) {
        struct v4l2_buffer b = {
            .type = mtype, .memory = V4L2_MEMORY_MMAP, .index = i
        };
        if (call(mfd, VIDIOC_QUERYBUF, &b) || b.length < NATIVE_FRONT_STATS_BYTES)
            goto out;
        meta_memory[i] = mmap(NULL, b.length, PROT_READ | PROT_WRITE,
                              MAP_SHARED, mfd, b.m.offset);
        if (meta_memory[i] == MAP_FAILED) { meta_memory[i] = NULL; goto out; }
        meta_lengths[i] = b.length;
        memset(meta_memory[i], 0xa5, NATIVE_FRONT_STATS_BYTES);
        if (call(mfd, VIDIOC_QBUF, &b))
            goto out;
    }
    phase = "metadata_streamon";
    if (call(mfd, VIDIOC_STREAMON, &mtype))
        goto out;
    meta_streaming = 1;
	phase = "streamon";
	if (call(fd, VIDIOC_STREAMON, &type))
		goto out;
	streaming = 1;
	phase = "dequeue_and_private_save";
	for (unsigned i = 0; i < FRAMES; i++) {
		struct pollfd ready = { .fd = fd, .events = POLLIN };
		struct v4l2_plane plane = { 0 };
		struct v4l2_buffer b = { .type = TYPE, .memory = V4L2_MEMORY_MMAP,
			.length = 1, .m.planes = &plane };
		int n;
		do n = poll(&ready, 1, 5000); while (n < 0 && errno == EINTR);
		if (n != 1 || !(ready.revents & POLLIN) ||
		    (ready.revents & (POLLERR | POLLHUP | POLLNVAL)) || call(fd, VIDIOC_DQBUF, &b) ||
		    b.sequence != i || b.index >= BUFFERS || b.length != 1 || plane.bytesused != BYTES ||
		    plane.data_offset || (b.flags & V4L2_BUF_FLAG_ERROR) ||
		    (b.flags & V4L2_BUF_FLAG_TIMESTAMP_MASK) != V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC)
			goto out;
		indices[i] = b.index;
		if ((i == 4 && b.index != 1) || (i == 5 && b.index != 0))
			goto out;
		times[i] = b.timestamp.tv_sec + b.timestamp.tv_usec / 1000000.0;
		if (i && times[i] <= times[i - 1])
			goto out;
		ys[i] = stats(memory[b.index], Y_BYTES);
		cs[i] = stats((unsigned char *)memory[b.index] + Y_BYTES, BYTES - Y_BYTES);
		if (ys[i].poison == Y_BYTES || cs[i].poison == BYTES - Y_BYTES)
			goto out;
        phase = "matching_frame_metadata";
        struct pollfd mready = { .fd = mfd, .events = POLLIN };
        struct v4l2_buffer mb = { .type = mtype, .memory = V4L2_MEMORY_MMAP };
        do n = poll(&mready, 1, 5000); while (n < 0 && errno == EINTR);
        if (n != 1 || !(mready.revents & POLLIN) ||
            (mready.revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            call(mfd, VIDIOC_DQBUF, &mb) || mb.index >= BUFFERS || mb.sequence != i ||
            mb.bytesused != NATIVE_FRONT_STATS_BYTES || (mb.flags & V4L2_BUF_FLAG_ERROR) ||
            mb.timestamp.tv_sec != b.timestamp.tv_sec ||
            mb.timestamp.tv_usec != b.timestamp.tv_usec)
            goto out;
        const unsigned char *meta = meta_memory[mb.index];
        if (!i) {
            meta_stream = native_front_stats_u64(meta + 8);
            meta_source_base = native_front_stats_u32(meta + 28);
        }
        if (native_front_stats_validate(meta, mb.bytesused, meta_stream, i) ||
            native_front_stats_u32(meta + 28) != meta_source_base + i ||
            native_front_stats_u64(meta + 16) / 1000 !=
                (uint64_t)b.timestamp.tv_sec * 1000000 + b.timestamp.tv_usec ||
            e003i_aecbe_frame_luma(meta + NATIVE_FRONT_STATS_HEADER_BYTES, &frame_lumas[i]) ||
            !isfinite(frame_lumas[i]) || frame_lumas[i] < 0.0f ||
            call(mfd, VIDIOC_QBUF, &mb))
            goto out;
        meta_completed++;
        phase = "dequeue_and_requeue_video";
        /* Queue IQ ahead of use; only the DMI bank selection changes. */
        unsigned request = 9 + i;
        if (params(packet, request) ||
            call(fd, VIDIOC_S_EXT_CTRLS, &param_controls))
            goto out;
        /* Swap the first returned pair to prove queue-order admission. */
        if (i == 0) {
            held = b.index;
        } else {
            if (call(fd, VIDIOC_QBUF, &b))
                goto out;
            if (i == 1) {
                b.index = held;
                if (call(fd, VIDIOC_QBUF, &b))
                    goto out;
            }
        }
		completed++;
	}
    double base_y = 0.0, gain_y = 0.0, reset_y = 0.0;
    for (unsigned i = 8; i < 20; i++) base_y += ys[i].mean / 12.0;
    for (unsigned i = 40; i < 56; i++) gain_y += ys[i].mean / 16.0;
    for (unsigned i = 68; i < 80; i++) reset_y += ys[i].mean / 12.0;
    phase = "typed_gain_response";
    if (!(base_y > 0.0) || gain_y < base_y * 1.4 || reset_y > gain_y * 0.8) {
        goto out;
    }
	phase = "streamoff";
	if (call(fd, VIDIOC_STREAMOFF, &type))
		goto out;
	streaming = 0;
    phase = "metadata_streamoff";
    if (call(mfd, VIDIOC_STREAMOFF, &mtype))
        goto out;
    meta_streaming = 0;
    for (unsigned i = 0; i < BUFFERS; i++) {
        if (munmap(meta_memory[i], meta_lengths[i]))
            goto out;
        meta_memory[i] = NULL;
    }
    mreq.count = 0;
    if (call(mfd, VIDIOC_REQBUFS, &mreq)) {
        goto out;
    }
	for (unsigned i = 0; i < BUFFERS; i++) {
		if (munmap(memory[i], lengths[i]))
			goto out;
		memory[i] = NULL;
	}
	req.count = 0;
	if (call(fd, VIDIOC_REQBUFS, &req))
		goto out;
	printf("{\"status\":\"PASS_80_NATIVE_FIRMWARE_PROFILE_FRAMES\",\"frames\":80,"
	       "\"streamoff\":true,\"metadata_streamoff\":true,\"metadata_pairs\":80,\"negative_control_cases\":5,\"firmware_negative_cases\":2,\"raw_command_control_present\":false,\"reordered_first_pair\":true,\"private_pixel_files_only\":true,\"buffer_bytes\":%u,"
	       "\"width\":2560,\"height\":1440,\"stride\":2560,\"observations\":[", BYTES);
	for (unsigned i = 0; i < FRAMES; i++)
		printf("%s{\"sequence\":%u,\"index\":%u,\"aec_luma\":%.6f,\"timestamp\":%.6f,\"y_mean\":%.6f,"
		       "\"y_min\":%u,\"y_max\":%u,\"uv_mean\":%.6f,\"uv_min\":%u,"
		       "\"uv_max\":%u,\"y_poison_bytes\":%lu,\"uv_poison_bytes\":%lu}",
		       i ? "," : "", i, indices[i], frame_lumas[i], times[i], ys[i].mean, ys[i].min, ys[i].max,
		       cs[i].mean, cs[i].min, cs[i].max, ys[i].poison, cs[i].poison);
	printf("],\"typed_gain_response\":{\"baseline_y_mean\":%.6f,\"gain2_y_mean\":%.6f,\"reset_y_mean\":%.6f}}\n", base_y, gain_y, reset_y);
	rc = 0;
out:
	if (rc)
		fprintf(stderr, "NATIVE_NV12_CAPTURE_FAILED phase=%s errno=%d completed=%u streaming=%d metadata_pairs=%u\n",
			phase, errno, completed, streaming, meta_completed);
	if (streaming && call(fd, VIDIOC_STREAMOFF, &type))
		fputs("NATIVE_NV12_STOP_FAILED_REBOOT_REQUIRED\n", stderr);
    if (meta_streaming && call(mfd, VIDIOC_STREAMOFF, &mtype))
        fputs("NATIVE_META_STOP_FAILED\n", stderr);
    for (unsigned i = 0; i < BUFFERS; i++)
        if (meta_memory[i]) munmap(meta_memory[i], meta_lengths[i]);
    if (mfd >= 0) close(mfd);
	if (cfd >= 0) close(cfd);
	for (unsigned i = 0; i < BUFFERS; i++)
		if (memory[i]) munmap(memory[i], lengths[i]);
	if (fd >= 0) close(fd);
	if (sfd >= 0) close(sfd);
	memset(profile, 0, sizeof(profile));
	return rc;
}
