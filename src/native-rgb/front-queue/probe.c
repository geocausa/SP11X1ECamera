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
#define BUFFERS 4U
#define FRAMES 80U
#define CAPSULES 93U
#define BYTES 5529600U
#define Y_BYTES 3686400U
#define IQ_BYTES 41088U
#define IQ_ID (V4L2_CID_USER_BASE + 0x1240)
#define TYPE V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
#define D "/var/lib/sp11-camera-native-queue-20261007-01/"
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
		token |= !strcmp(p, "sp11_camera_native_queue_20261007_01=1");
		entry |= !strcmp(p, "sp11_entry=7.1.5-sp11-camera-native-queue-20261007-01");
	}
	return token && entry;
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
	int fd = -1, sfd = -1, cfd = -1, rc = 1, streaming = 0;
	unsigned completed = 0, held = 0;
	const char *phase = "dedicated_boot_guard";
	unsigned char capsule[IQ_BYTES];
	enum v4l2_buf_type type = TYPE;
	struct stat st;
	struct v4l2_format fmt = { .type = TYPE };
	struct v4l2_requestbuffers req = { .count = BUFFERS, .type = TYPE, .memory = V4L2_MEMORY_MMAP };
	double times[FRAMES];
	unsigned indices[FRAMES];

	if (argc != 4 || geteuid() || !boot_allowed())
		return 1; /* Refuse Golden before opening any device or pixel file. */
	phase = "bootstrap_read";
	cfd = open(argv[3], O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
	if (cfd < 0 || fstat(cfd, &st) || !S_ISREG(st.st_mode) || st.st_size != (off_t)(IQ_BYTES * CAPSULES))
		goto out;
	size_t have = 0;
	while (have < IQ_BYTES) {
		ssize_t n = read(cfd, capsule + have, IQ_BYTES - have);
		if (n < 0 && errno == EINTR) continue;
		if (n <= 0) goto out;
		have += n;
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
	phase = "bootstrap_iq_control";
	struct v4l2_ext_control iq = { .id = IQ_ID, .size = IQ_BYTES, .ptr = capsule };
	struct v4l2_ext_controls iq_controls = {
		.count = 1, .controls = &iq, .which = V4L2_CTRL_WHICH_CUR_VAL,
	};
	for (unsigned request = 4; request <= 8; request++) {
        if (pread(cfd, capsule, IQ_BYTES, (off_t)(request - 4) * IQ_BYTES) != IQ_BYTES ||
            call(fd, VIDIOC_S_EXT_CTRLS, &iq_controls))
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
        /* Queue IQ ahead of use; only the DMI bank selection changes. */
        unsigned request = 9 + i;
        if (pread(cfd, capsule, IQ_BYTES, (off_t)(request - 4) * IQ_BYTES) != IQ_BYTES ||
            call(fd, VIDIOC_S_EXT_CTRLS, &iq_controls))
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
	phase = "streamoff";
	if (call(fd, VIDIOC_STREAMOFF, &type))
		goto out;
	streaming = 0;
	for (unsigned i = 0; i < BUFFERS; i++) {
		if (munmap(memory[i], lengths[i]))
			goto out;
		memory[i] = NULL;
	}
	req.count = 0;
	if (call(fd, VIDIOC_REQBUFS, &req))
		goto out;
	printf("{\"status\":\"PASS_80_NATIVE_NV12_QUEUE_FRAMES\",\"frames\":80,"
	       "\"streamoff\":true,\"reordered_first_pair\":true,\"private_pixel_files_only\":true,\"buffer_bytes\":%u,"
	       "\"width\":2560,\"height\":1440,\"stride\":2560,\"observations\":[", BYTES);
	for (unsigned i = 0; i < FRAMES; i++)
		printf("%s{\"sequence\":%u,\"index\":%u,\"timestamp\":%.6f,\"y_mean\":%.6f,"
		       "\"y_min\":%u,\"y_max\":%u,\"uv_mean\":%.6f,\"uv_min\":%u,"
		       "\"uv_max\":%u,\"y_poison_bytes\":%lu,\"uv_poison_bytes\":%lu}",
		       i ? "," : "", i, indices[i], times[i], ys[i].mean, ys[i].min, ys[i].max,
		       cs[i].mean, cs[i].min, cs[i].max, ys[i].poison, cs[i].poison);
	puts("]}");
	rc = 0;
out:
	if (rc)
		fprintf(stderr, "NATIVE_NV12_CAPTURE_FAILED phase=%s errno=%d completed=%u streaming=%d\n",
			phase, errno, completed, streaming);
	if (streaming && call(fd, VIDIOC_STREAMOFF, &type))
		fputs("NATIVE_NV12_STOP_FAILED_REBOOT_REQUIRED\n", stderr);
	if (cfd >= 0) close(cfd);
	for (unsigned i = 0; i < BUFFERS; i++)
		if (memory[i]) munmap(memory[i], lengths[i]);
	if (fd >= 0) close(fd);
	if (sfd >= 0) close(sfd);
	memset(capsule, 0, sizeof(capsule));
	return rc;
}
