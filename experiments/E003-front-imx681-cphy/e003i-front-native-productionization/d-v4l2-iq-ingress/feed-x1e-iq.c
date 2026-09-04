// SPDX-License-Identifier: GPL-2.0
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>

#include <linux/videodev2.h>

#include "qcom-camss-x1e-iq.h"

static int read_exact(const char *path, uint8_t *buf, size_t size)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC);
	ssize_t n;
	size_t off = 0;

	if (fd < 0) {
		perror(path);
		return -1;
	}
	while (off < size) {
		n = read(fd, buf + off, size - off);
		if (n < 0 && errno == EINTR)
			continue;
		if (n <= 0) {
			fprintf(stderr, "%s: expected %zu bytes, got %zu\n", path, size, off);
			close(fd);
			return -1;
		}
		off += (size_t)n;
	}
	for (;;) {
		uint8_t extra;
		n = read(fd, &extra, 1);
		if (n < 0 && errno == EINTR)
			continue;
		if (n != 0) {
			fprintf(stderr, "%s: file is larger than %zu bytes\n", path, size);
			close(fd);
			return -1;
		}
		break;
	}
	close(fd);
	return 0;
}

static int submit_capsule(int fd, uint8_t *capsule)
{
	struct v4l2_ext_control ctrl = {
		.id = V4L2_CID_QCOM_CAMSS_X1E_IQ_CAPSULE,
		.size = QCOM_CAMSS_X1E_IQ_CAPSULE_BYTES,
		.ptr = capsule,
	};
	struct v4l2_ext_controls ctrls = {
		.which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 1,
		.controls = &ctrl,
	};

	if (ioctl(fd, VIDIOC_S_EXT_CTRLS, &ctrls) < 0) {
		perror("VIDIOC_S_EXT_CTRLS(X1E IQ capsule)");
		return -1;
	}
	return 0;
}

int main(int argc, char **argv)
{
	uint8_t *capsule;
	int fd, i;

	if (argc != 5) {
		fprintf(stderr, "usage: %s /dev/videoX request4.bin request5.bin request6.bin\n", argv[0]);
		return 2;
	}
	fd = open(argv[1], O_RDWR | O_CLOEXEC);
	if (fd < 0) {
		perror(argv[1]);
		return 1;
	}
	capsule = malloc(QCOM_CAMSS_X1E_IQ_CAPSULE_BYTES);
	if (!capsule) {
		perror("malloc");
		close(fd);
		return 1;
	}
	for (i = 2; i < 5; i++) {
		if (read_exact(argv[i], capsule, QCOM_CAMSS_X1E_IQ_CAPSULE_BYTES) ||
		    submit_capsule(fd, capsule)) {
			memset(capsule, 0, QCOM_CAMSS_X1E_IQ_CAPSULE_BYTES);
			free(capsule);
			close(fd);
			return 1;
		}
	}
	memset(capsule, 0, QCOM_CAMSS_X1E_IQ_CAPSULE_BYTES);
	free(capsule);
	printf("primed X1E IQ requests 4,5,6; STREAMON is intentionally not issued\n");
	close(fd);
	return 0;
}
