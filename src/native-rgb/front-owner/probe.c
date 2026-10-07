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
#define FRAMES 4U
#define BYTES 5529600U
#define Y_BYTES 3686400U
#define IQ_BYTES 41088U
#define IQ_ID (V4L2_CID_USER_BASE + 0x1240)
#define TYPE V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
#define D "/var/lib/sp11-camera-native-owner-20261007-01/"
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
		token |= !strcmp(p, "sp11_camera_native_owner_20261007_01=1");
		entry |= !strcmp(p, "sp11_entry=7.1.5-sp11-camera-native-owner-20261007-01");
	}
	return token && entry;
}
static int write_all(int fd, const unsigned char *p, size_t n)
{
	while (n) {
		ssize_t v = write(fd, p, n);
		if (v < 0 && errno == EINTR)
			continue;
		if (v <= 0)
			return -1;
		p += v;
		n -= v;
	}
	return 0;
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
	void *memory[FRAMES] = { 0 };
	unsigned lengths[FRAMES] = { 0 };
	struct plane_stats ys[FRAMES], cs[FRAMES];
	int fd = -1, sfd = -1, cfd = -1, rc = 1, streaming = 0;
	unsigned completed = 0;
	const char *phase = "dedicated_boot_guard";
	unsigned char capsule[IQ_BYTES];
	enum v4l2_buf_type type = TYPE;
	struct stat st;
	struct v4l2_format fmt = { .type = TYPE };
	struct v4l2_requestbuffers req = { .count = FRAMES, .type = TYPE, .memory = V4L2_MEMORY_MMAP };
	double times[FRAMES];

	if (argc != 4 || geteuid() || !boot_allowed())
		return 1; /* Refuse Golden before opening any device or pixel file. */
	phase = "bootstrap_read";
	cfd = open(argv[3], O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
	if (cfd < 0 || fstat(cfd, &st) || !S_ISREG(st.st_mode) || st.st_size != IQ_BYTES)
		goto out;
	size_t have = 0;
	while (have < IQ_BYTES) {
		ssize_t n = read(cfd, capsule + have, IQ_BYTES - have);
		if (n < 0 && errno == EINTR) continue;
		if (n <= 0) goto out;
		have += n;
	}
	close(cfd); cfd = -1;

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
	if (call(fd, VIDIOC_S_EXT_CTRLS, &iq_controls) ||
	    call(fd, VIDIOC_REQBUFS, &req) || req.count != FRAMES)
		goto out;
	phase = "buffer_allocate_and_queue";
	for (unsigned i = 0; i < FRAMES; i++) {
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
		    b.sequence != i || b.index != i || b.length != 1 || plane.bytesused != BYTES ||
		    plane.data_offset || (b.flags & V4L2_BUF_FLAG_ERROR) ||
		    (b.flags & V4L2_BUF_FLAG_TIMESTAMP_MASK) != V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC)
			goto out;
		times[i] = b.timestamp.tv_sec + b.timestamp.tv_usec / 1000000.0;
		if (i && times[i] <= times[i - 1])
			goto out;
		ys[i] = stats(memory[i], Y_BYTES);
		cs[i] = stats((unsigned char *)memory[i] + Y_BYTES, BYTES - Y_BYTES);
		if (ys[i].poison == Y_BYTES || cs[i].poison == BYTES - Y_BYTES)
			goto out;
		char path[256];
		snprintf(path, sizeof(path), D "PRIVATE-FRAME-%u.nv12", i);
		cfd = open(path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
		if (cfd < 0 || write_all(cfd, memory[i], BYTES) || fsync(cfd))
			goto out;
		close(cfd); cfd = -1;
		completed++;
	}
	phase = "streamoff";
	if (call(fd, VIDIOC_STREAMOFF, &type))
		goto out;
	streaming = 0;
	for (unsigned i = 0; i < FRAMES; i++) {
		if (munmap(memory[i], lengths[i]))
			goto out;
		memory[i] = NULL;
	}
	req.count = 0;
	if (call(fd, VIDIOC_REQBUFS, &req))
		goto out;
	printf("{\"status\":\"PASS_FOUR_NATIVE_NV12_BUFFERS\",\"frames\":4,"
	       "\"streamoff\":true,\"private_pixel_files_only\":true,\"buffer_bytes\":%u,"
	       "\"width\":2560,\"height\":1440,\"stride\":2560,\"observations\":[", BYTES);
	for (unsigned i = 0; i < FRAMES; i++)
		printf("%s{\"sequence\":%u,\"timestamp\":%.6f,\"y_mean\":%.6f,"
		       "\"y_min\":%u,\"y_max\":%u,\"uv_mean\":%.6f,\"uv_min\":%u,"
		       "\"uv_max\":%u,\"y_poison_bytes\":%lu,\"uv_poison_bytes\":%lu}",
		       i ? "," : "", i, times[i], ys[i].mean, ys[i].min, ys[i].max,
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
	for (unsigned i = 0; i < FRAMES; i++)
		if (memory[i]) munmap(memory[i], lengths[i]);
	if (fd >= 0) close(fd);
	if (sfd >= 0) close(sfd);
	memset(capsule, 0, sizeof(capsule));
	return rc;
}
