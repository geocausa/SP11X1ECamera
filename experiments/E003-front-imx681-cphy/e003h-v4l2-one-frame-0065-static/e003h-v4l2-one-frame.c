// SPDX-License-Identifier: GPL-2.0-only
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

#define QC10C_WIDTH 2560U
#define QC10C_HEIGHT 1440U
#define QC10C_STRIDE 3584U
#define QC10C_BYTES 0x76b000U

static int xioctl(int fd, unsigned long req, void *arg)
{
	int ret;
	do { ret = ioctl(fd, req, arg); } while (ret < 0 && errno == EINTR);
	return ret;
}

static void pin_until_reboot(const char *why)
{
	fprintf(stderr, "PINNED_FOR_REBOOT: %s\n", why);
	fflush(stderr);
	for (;;)
		pause();
}

static int save_file(const char *path, const void *data, size_t bytes)
{
	const uint8_t *p = data;
	int fd = open(path, O_CREAT | O_TRUNC | O_WRONLY | O_CLOEXEC, 0600);
	if (fd < 0) return -errno;
	while (bytes) {
		ssize_t n = write(fd, p, bytes);
		if (n < 0) { int e = -errno; close(fd); return e; }
		p += n; bytes -= (size_t)n;
	}
	if (fsync(fd)) { int e = -errno; close(fd); return e; }
	return close(fd) ? -errno : 0;
}

int main(int argc, char **argv)
{
	struct v4l2_requestbuffers req = { 0 };
	struct v4l2_format fmt = { 0 };
	void *map[2] = { MAP_FAILED, MAP_FAILED };
	size_t map_len[2] = { 0, 0 };
	const char *video, *output;
	enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
	int vfd = -1, ret = 1;
	unsigned int i;

	if (argc != 3) {
		fprintf(stderr, "usage: %s /dev/videoN output.qc10c\n", argv[0]);
		return 2;
	}
	video = argv[1]; output = argv[2];
	vfd = open(video, O_RDWR | O_CLOEXEC);
	if (vfd < 0) { perror("open video"); return 1; }

	fmt.type = type;
	fmt.fmt.pix_mp.width = QC10C_WIDTH;
	fmt.fmt.pix_mp.height = QC10C_HEIGHT;
	fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_QC10C;
	fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
	if (xioctl(vfd, VIDIOC_S_FMT, &fmt)) { perror("VIDIOC_S_FMT"); goto out; }
	if (fmt.fmt.pix_mp.width != QC10C_WIDTH || fmt.fmt.pix_mp.height != QC10C_HEIGHT ||
	    fmt.fmt.pix_mp.pixelformat != V4L2_PIX_FMT_QC10C || fmt.fmt.pix_mp.num_planes != 1 ||
	    fmt.fmt.pix_mp.plane_fmt[0].bytesperline != QC10C_STRIDE ||
	    fmt.fmt.pix_mp.plane_fmt[0].sizeimage != QC10C_BYTES) {
		fprintf(stderr, "unexpected QC10C format\n"); goto out;
	}

	req.count = 2; req.type = type; req.memory = V4L2_MEMORY_MMAP;
	if (xioctl(vfd, VIDIOC_REQBUFS, &req)) { perror("VIDIOC_REQBUFS"); goto out; }
	if (req.count != 2) { fprintf(stderr, "REQBUFS=%u expected 2\n", req.count); goto out; }

	for (i = 0; i < 2; i++) {
		struct v4l2_plane plane = { 0 };
		struct v4l2_buffer b = { 0 };
		b.type = type; b.memory = V4L2_MEMORY_MMAP; b.index = i; b.length = 1; b.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_QUERYBUF, &b)) { perror("VIDIOC_QUERYBUF"); goto out; }
		if (plane.length < QC10C_BYTES) { fprintf(stderr, "buffer too small\n"); goto out; }
		map_len[i] = plane.length;
		map[i] = mmap(NULL, map_len[i], PROT_READ | PROT_WRITE, MAP_SHARED, vfd, plane.m.mem_offset);
		if (map[i] == MAP_FAILED) { perror("mmap"); goto out; }
		memset(map[i], 0, QC10C_BYTES);
		if (xioctl(vfd, VIDIOC_QBUF, &b)) { perror("VIDIOC_QBUF"); goto out; }
	}

	printf("QBUF_COUNT=2\n"); fflush(stdout);
	if (xioctl(vfd, VIDIOC_STREAMON, &type)) {
		perror("VIDIOC_STREAMON");
		pin_until_reboot("STREAMON failed; preserve driver-owned DMA");
	}
	printf("STREAMON_OK\n"); fflush(stdout);

	{
		struct pollfd pfd = { .fd = vfd, .events = POLLIN };
		struct v4l2_plane plane = { 0 };
		struct v4l2_buffer b = { 0 };
		int pr = poll(&pfd, 1, 1000);
		if (pr <= 0) pin_until_reboot(pr == 0 ? "DQBUF poll timeout" : "DQBUF poll error");
		b.type = type; b.memory = V4L2_MEMORY_MMAP; b.length = 1; b.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_DQBUF, &b)) { perror("VIDIOC_DQBUF"); pin_until_reboot("DQBUF failed"); }
		if (b.index != 0 || plane.bytesused != QC10C_BYTES) {
			fprintf(stderr, "unexpected DQBUF index=%u bytesused=%u\n", b.index, plane.bytesused);
			pin_until_reboot("unexpected completed buffer");
		}
		printf("DQBUF_INDEX=%u BYTESUSED=%u SEQUENCE=%u\n", b.index, plane.bytesused, b.sequence);
		if (xioctl(vfd, VIDIOC_STREAMOFF, &type)) { perror("VIDIOC_STREAMOFF"); pin_until_reboot("STREAMOFF failed"); }
		printf("STREAMOFF_OK\n"); fflush(stdout);
		if (save_file(output, map[b.index], QC10C_BYTES)) { perror("save output"); goto out; }
	}

	printf("PASS: ordinary V4L2 QBUF/STREAMON/DQBUF/STREAMOFF one-frame capture\n");
	ret = 0;
out:
	for (i = 0; i < 2; i++) if (map[i] != MAP_FAILED) munmap(map[i], map_len[i]);
	if (vfd >= 0) close(vfd);
	return ret;
}
