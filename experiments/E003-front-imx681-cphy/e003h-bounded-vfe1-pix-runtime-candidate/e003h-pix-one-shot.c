// SPDX-License-Identifier: GPL-2.0-only
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
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
	const char *video, *trigger, *output;
	int tfd = -1, vfd = -1, ret = 1;
	unsigned int i;

	if (argc != 4) {
		fprintf(stderr, "usage: %s /dev/videoN /sys/.../e003h_pix_run_once output.qc10c\n", argv[0]);
		return 2;
	}
	video = argv[1]; trigger = argv[2]; output = argv[3];
	vfd = open(video, O_RDWR | O_CLOEXEC);
	if (vfd < 0) { perror("open video"); goto out; }

	fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
	fmt.fmt.pix_mp.width = QC10C_WIDTH;
	fmt.fmt.pix_mp.height = QC10C_HEIGHT;
	fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_QC10C;
	fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
	if (xioctl(vfd, VIDIOC_S_FMT, &fmt)) { perror("VIDIOC_S_FMT"); goto out; }
	if (fmt.fmt.pix_mp.width != QC10C_WIDTH || fmt.fmt.pix_mp.height != QC10C_HEIGHT ||
	    fmt.fmt.pix_mp.pixelformat != V4L2_PIX_FMT_QC10C || fmt.fmt.pix_mp.num_planes != 1 ||
	    fmt.fmt.pix_mp.plane_fmt[0].bytesperline != QC10C_STRIDE ||
	    fmt.fmt.pix_mp.plane_fmt[0].sizeimage != QC10C_BYTES) {
		fprintf(stderr, "unexpected QC10C format %ux%u fourcc=%08x planes=%u stride=%u size=%u\n",
			fmt.fmt.pix_mp.width, fmt.fmt.pix_mp.height, fmt.fmt.pix_mp.pixelformat,
			fmt.fmt.pix_mp.num_planes, fmt.fmt.pix_mp.plane_fmt[0].bytesperline,
			fmt.fmt.pix_mp.plane_fmt[0].sizeimage);
		goto out;
	}

	req.count = 2;
	req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
	req.memory = V4L2_MEMORY_MMAP;
	if (xioctl(vfd, VIDIOC_REQBUFS, &req)) { perror("VIDIOC_REQBUFS"); goto out; }
	if (req.count != 2) { fprintf(stderr, "REQBUFS returned %u, expected 2\n", req.count); goto out; }

	for (i = 0; i < 2; i++) {
		struct v4l2_plane plane = { 0 };
		struct v4l2_buffer buf = { 0 };
		buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
		buf.memory = V4L2_MEMORY_MMAP;
		buf.index = i;
		buf.length = 1;
		buf.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_QUERYBUF, &buf)) { perror("VIDIOC_QUERYBUF"); goto out; }
		if (plane.length < QC10C_BYTES) { fprintf(stderr, "buffer%u length %u too small\n", i, plane.length); goto out; }
		map_len[i] = plane.length;
		map[i] = mmap(NULL, map_len[i], PROT_READ | PROT_WRITE, MAP_SHARED, vfd, plane.m.mem_offset);
		if (map[i] == MAP_FAILED) { perror("mmap"); goto out; }
		memset(map[i], 0, QC10C_BYTES);
	}

	/* Deliberately no VIDIOC_QBUF and no VIDIOC_STREAMON: kernel 0035 owns the one-shot. */
	tfd = open(trigger, O_WRONLY | O_CLOEXEC);
	if (tfd < 0) { perror("open trigger"); goto out; }
	if (write(tfd, "RUN\n", 4) != 4) { perror("write trigger"); goto out; }
	close(tfd); tfd = -1;

	if (save_file(output, map[0], QC10C_BYTES)) { perror("save output"); goto out; }
	printf("PASS: saved %u-byte QC10C slot0 without QBUF/STREAMON\n", QC10C_BYTES);
	ret = 0;

out:
	if (tfd >= 0) close(tfd);
	for (i = 0; i < 2; i++) if (map[i] != MAP_FAILED) munmap(map[i], map_len[i]);
	if (vfd >= 0) {
		struct v4l2_requestbuffers free_req = { .count = 0, .type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE, .memory = V4L2_MEMORY_MMAP };
		xioctl(vfd, VIDIOC_REQBUFS, &free_req);
		close(vfd);
	}
	return ret;
}
