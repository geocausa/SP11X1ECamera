#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define DB_BOOTSTRAP_VBLANK 1402
#define DB_BOOTSTRAP_EXPOSURE 3554
#define DB_BOOTSTRAP_AGAIN 0
#define DB_BOOTSTRAP_DGAIN 256

static int xioctl(int fd, unsigned long request, void *arg)
{
	int rc;

	do {
		rc = ioctl(fd, request, arg);
	} while (rc < 0 && errno == EINTR);
	return rc;
}

int main(int argc, char **argv)
{
	struct v4l2_ext_control controls[4] = {
		{ .id = V4L2_CID_VBLANK, .value = DB_BOOTSTRAP_VBLANK },
		{ .id = V4L2_CID_EXPOSURE, .value = DB_BOOTSTRAP_EXPOSURE },
		{ .id = V4L2_CID_ANALOGUE_GAIN, .value = DB_BOOTSTRAP_AGAIN },
		{ .id = V4L2_CID_DIGITAL_GAIN, .value = DB_BOOTSTRAP_DGAIN },
	};
	struct v4l2_ext_controls set = {
		.which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 4,
		.controls = controls,
	};
	struct v4l2_ext_control readback[4] = {
		{ .id = V4L2_CID_VBLANK },
		{ .id = V4L2_CID_EXPOSURE },
		{ .id = V4L2_CID_ANALOGUE_GAIN },
		{ .id = V4L2_CID_DIGITAL_GAIN },
	};
	struct v4l2_ext_controls get = {
		.which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 4,
		.controls = readback,
	};
	int fd;

	if (argc != 2 || argv[1][0] != '/') {
		fprintf(stderr, "usage: %s /dev/v4l-subdevN\n", argv[0]);
		return 2;
	}
	fd = open(argv[1], O_RDWR | O_CLOEXEC);
	if (fd < 0) {
		perror("open sensor subdev");
		return 3;
	}
	if (xioctl(fd, VIDIOC_S_EXT_CTRLS, &set)) {
		int saved_errno = errno;
		fprintf(stderr, "DB_BOOTSTRAP_S_EXT_FAIL errno=%d error_idx=%u (%s)\n",
			saved_errno, set.error_idx, strerror(saved_errno));
		close(fd);
		return 4;
	}
	if (xioctl(fd, VIDIOC_G_EXT_CTRLS, &get)) {
		perror("DB_BOOTSTRAP_G_EXT_FAIL");
		close(fd);
		return 5;
	}
	close(fd);
	if (readback[0].value != DB_BOOTSTRAP_VBLANK ||
	    readback[1].value != DB_BOOTSTRAP_EXPOSURE ||
	    readback[2].value != DB_BOOTSTRAP_AGAIN ||
	    readback[3].value != DB_BOOTSTRAP_DGAIN) {
		fprintf(stderr,
			"DB_BOOTSTRAP_READBACK_FAIL VB=%d EXP=%d AGAIN=%d DGAIN=%d\n",
			readback[0].value, readback[1].value,
			readback[2].value, readback[3].value);
		return 6;
	}
	printf("DB_BOOTSTRAP_EXT_PASS VB=%d EXP=%d AGAIN=%d DGAIN=%d\n",
		readback[0].value, readback[1].value,
		readback[2].value, readback[3].value);
	return 0;
}
