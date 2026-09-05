// SPDX-License-Identifier: GPL-2.0-only
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/v4l2-controls.h>
#include <linux/videodev2.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define QC10C_WIDTH 2560U
#define QC10C_HEIGHT 1440U
#define QC10C_STRIDE 3584U
#define QC10C_BYTES 0x76b000U
#define BUFFER_COUNT 4U
#define FRAME_COUNT 6U
#define DQBUF_POLL_TIMEOUT_MS 5000
#define IQ_BYTES 41088U
#define V4L2_CID_QCOM_CAMSS_X1E_IQ_CAPSULE (V4L2_CID_USER_BASE + 0x1240)
#define V4L2_CID_QCOM_CAMSS_X1E_TLBG_SNAPSHOT (V4L2_CID_USER_BASE + 0x1241)
#define TLBG_HEADER_BYTES 32U
#define TLBG_RAW_BYTES 0x25800U
#define TLBG_BYTES (TLBG_HEADER_BYTES + TLBG_RAW_BYTES)
#define TLBG_MAGIC 0x47424c54U

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

static uint64_t mono_ns(void)
{
	struct timespec ts;
	if (clock_gettime(CLOCK_MONOTONIC, &ts))
		return 0;
	return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static uint16_t le16(const uint8_t *p)
{
	return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t le32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
	       ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t le64(const uint8_t *p)
{
	return (uint64_t)le32(p) | ((uint64_t)le32(p + 4) << 32);
}

static int read_exact(const char *path, uint8_t *buf, size_t size)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC);
	size_t off = 0;
	if (fd < 0)
		return -errno;
	while (off < size) {
		ssize_t n = read(fd, buf + off, size - off);
		if (n < 0 && errno == EINTR)
			continue;
		if (n <= 0) { int e = n < 0 ? -errno : -EIO; close(fd); return e; }
		off += (size_t)n;
	}
	{
		uint8_t extra;
		ssize_t n;
		do { n = read(fd, &extra, 1); } while (n < 0 && errno == EINTR);
		if (n != 0) { int e = n < 0 ? -errno : -EFBIG; close(fd); return e; }
	}
	return close(fd) ? -errno : 0;
}

static int save_file(const char *path, const void *data, size_t bytes)
{
	const uint8_t *p = data;
	int fd = open(path, O_CREAT | O_TRUNC | O_WRONLY | O_CLOEXEC, 0600);
	if (fd < 0)
		return -errno;
	while (bytes) {
		ssize_t n = write(fd, p, bytes);
		if (n < 0 && errno == EINTR)
			continue;
		if (n <= 0) { int e = n < 0 ? -errno : -EIO; close(fd); return e; }
		p += n; bytes -= (size_t)n;
	}
	if (fsync(fd)) { int e = -errno; close(fd); return e; }
	return close(fd) ? -errno : 0;
}

static int submit_iq(int fd, const uint8_t *capsule)
{
	struct v4l2_ext_control ctrl = { .id = V4L2_CID_QCOM_CAMSS_X1E_IQ_CAPSULE,
		.size = IQ_BYTES, .ptr = (void *)capsule };
	struct v4l2_ext_controls ctrls = { .which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 1, .controls = &ctrl };
	return xioctl(fd, VIDIOC_S_EXT_CTRLS, &ctrls);
}

static int get_tlbg(int fd, uint8_t *snapshot, uint64_t *generation,
		    uint32_t *source_seq, uint32_t *slot)
{
	struct v4l2_ext_control ctrl = { .id = V4L2_CID_QCOM_CAMSS_X1E_TLBG_SNAPSHOT,
		.size = TLBG_BYTES, .ptr = snapshot };
	struct v4l2_ext_controls ctrls = { .which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 1, .controls = &ctrl };
	if (xioctl(fd, VIDIOC_G_EXT_CTRLS, &ctrls))
		return -errno;
	if (le32(snapshot) != TLBG_MAGIC || le16(snapshot + 4) != 1 ||
	    le16(snapshot + 6) != TLBG_HEADER_BYTES ||
	    le32(snapshot + 24) != TLBG_RAW_BYTES || !(le32(snapshot + 28) & 1))
		return -EPROTO;
	*generation = le64(snapshot + 8);
	*source_seq = le32(snapshot + 16);
	*slot = le32(snapshot + 20);
	return *generation && *source_seq && *slot < 2 ? 0 : -EPROTO;
}

static int qbuf_index(int fd, enum v4l2_buf_type type, unsigned int index)
{
	struct v4l2_plane plane = { 0 };
	struct v4l2_buffer b = { 0 };
	b.type = type; b.memory = V4L2_MEMORY_MMAP; b.index = index;
	b.length = 1; b.m.planes = &plane;
	return xioctl(fd, VIDIOC_QBUF, &b);
}

int main(int argc, char **argv)
{
	static const unsigned int expect_index[FRAME_COUNT] = { 0, 1, 2, 3, 0, 1 };
	struct v4l2_requestbuffers req = { 0 };
	struct v4l2_format fmt = { 0 };
	void *map[BUFFER_COUNT] = { MAP_FAILED, MAP_FAILED, MAP_FAILED, MAP_FAILED };
	size_t map_len[BUFFER_COUNT] = { 0 };
	void *first_snapshot = NULL, *second_snapshot = NULL;
	uint8_t *iq = NULL, *tlbg = NULL;
	uint64_t last_generation = 0;
	const char *video, *tlbg_prefix;
	enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
	int vfd = -1, ret = 1;
	unsigned int i;

	if (argc != 12) {
		fprintf(stderr, "usage: %s /dev/videoN R4.bin R5.bin R6.bin TLBG-prefix out0 out1 out2 out3 out4 out5\n", argv[0]);
		return 2;
	}
	video = argv[1]; tlbg_prefix = argv[5];
	vfd = open(video, O_RDWR | O_CLOEXEC);
	if (vfd < 0) { perror("open video"); return 1; }
	iq = malloc(IQ_BYTES); tlbg = malloc(TLBG_BYTES);
	if (!iq || !tlbg) { perror("malloc control buffers"); goto out; }

	fmt.type = type; fmt.fmt.pix_mp.width = QC10C_WIDTH; fmt.fmt.pix_mp.height = QC10C_HEIGHT;
	fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_QC10C; fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
	if (xioctl(vfd, VIDIOC_S_FMT, &fmt)) { perror("VIDIOC_S_FMT"); goto out; }
	if (fmt.fmt.pix_mp.width != QC10C_WIDTH || fmt.fmt.pix_mp.height != QC10C_HEIGHT ||
	    fmt.fmt.pix_mp.pixelformat != V4L2_PIX_FMT_QC10C || fmt.fmt.pix_mp.num_planes != 1 ||
	    fmt.fmt.pix_mp.plane_fmt[0].bytesperline != QC10C_STRIDE ||
	    fmt.fmt.pix_mp.plane_fmt[0].sizeimage != QC10C_BYTES) {
		fprintf(stderr, "unexpected QC10C format\n"); goto out;
	}

	req.count = BUFFER_COUNT; req.type = type; req.memory = V4L2_MEMORY_MMAP;
	if (xioctl(vfd, VIDIOC_REQBUFS, &req) || req.count != BUFFER_COUNT) {
		perror("VIDIOC_REQBUFS"); goto out;
	}
	for (i = 0; i < BUFFER_COUNT; i++) {
		struct v4l2_plane plane = { 0 }; struct v4l2_buffer b = { 0 };
		b.type = type; b.memory = V4L2_MEMORY_MMAP; b.index = i; b.length = 1; b.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_QUERYBUF, &b) || plane.length < QC10C_BYTES) {
			perror("VIDIOC_QUERYBUF"); goto out;
		}
		map_len[i] = plane.length;
		map[i] = mmap(NULL, map_len[i], PROT_READ | PROT_WRITE, MAP_SHARED, vfd, plane.m.mem_offset);
		if (map[i] == MAP_FAILED) { perror("mmap"); goto out; }
		memset(map[i], 0, QC10C_BYTES);
		if (qbuf_index(vfd, type, i)) { perror("VIDIOC_QBUF initial"); goto out; }
	}
	first_snapshot = malloc(QC10C_BYTES); second_snapshot = malloc(QC10C_BYTES);
	if (!first_snapshot || !second_snapshot) { perror("malloc frame snapshot"); goto out; }

	if (read_exact(argv[2], iq, IQ_BYTES) || submit_iq(vfd, iq)) {
		perror("submit R4 before STREAMON"); goto out;
	}
	printf("IQ_R4_SUBMITTED_PRE_STREAMON\n"); fflush(stdout);
	if (xioctl(vfd, VIDIOC_STREAMON, &type)) {
		perror("VIDIOC_STREAMON"); pin_until_reboot("STREAMON failed; preserve driver-owned DMA");
	}
	printf("STREAMON_OK_ASYNC MONO_NS=%llu\n", (unsigned long long)mono_ns()); fflush(stdout);

	for (i = 0; i < FRAME_COUNT; i++) {
		struct pollfd pfd = { .fd = vfd, .events = POLLIN };
		struct v4l2_plane plane = { 0 }; struct v4l2_buffer b = { 0 };
		uint64_t gen = 0; uint32_t source_seq = 0, slot = 0; char path[4096];
		uint64_t ps = mono_ns(); int pr = poll(&pfd, 1, DQBUF_POLL_TIMEOUT_MS); uint64_t pe = mono_ns();
		printf("POLL%u_START_NS=%llu END_NS=%llu ELAPSED_NS=%llu RC=%d REVENTS=0x%x\n", i,
		       (unsigned long long)ps, (unsigned long long)pe, (unsigned long long)(pe-ps), pr, pfd.revents);
		fflush(stdout);
		if (pr <= 0) pin_until_reboot(pr == 0 ? "DQBUF poll timeout" : "DQBUF poll error");
		b.type = type; b.memory = V4L2_MEMORY_MMAP; b.length = 1; b.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_DQBUF, &b)) { perror("VIDIOC_DQBUF"); pin_until_reboot("DQBUF failed"); }
		if (b.index != expect_index[i] || plane.bytesused != QC10C_BYTES || b.sequence != i)
			pin_until_reboot("unexpected completed buffer ordering");
		printf("DQBUF%u_INDEX=%u BYTESUSED=%u SEQUENCE=%u\n", i, b.index, plane.bytesused, b.sequence);
		if (get_tlbg(vfd, tlbg, &gen, &source_seq, &slot))
			pin_until_reboot("generation-tagged TL_BG read/ABI validation failed");
		if (gen < last_generation || gen > FRAME_COUNT || source_seq > FRAME_COUNT)
			pin_until_reboot("TL_BG generation/source sequence outside bounded run");
		last_generation = gen;
		snprintf(path, sizeof(path), "%s-%u.bin", tlbg_prefix, i);
		if (save_file(path, tlbg, TLBG_BYTES)) pin_until_reboot("TL_BG snapshot save failed");
		printf("TLBG_READ%u_GENERATION=%llu SOURCE_SEQ=%u SLOT=%u BYTES=%u\n", i,
		       (unsigned long long)gen, source_seq, slot, TLBG_BYTES); fflush(stdout);

		if (i == 0) {
			if (read_exact(argv[3], iq, IQ_BYTES) || submit_iq(vfd, iq))
				pin_until_reboot("live R5 IQ submission failed");
			printf("IQ_R5_SUBMITTED_AFTER_DQBUF0\n"); fflush(stdout);
		} else if (i == 1) {
			if (read_exact(argv[4], iq, IQ_BYTES) || submit_iq(vfd, iq))
				pin_until_reboot("live R6 IQ submission failed");
			printf("IQ_R6_SUBMITTED_AFTER_DQBUF1\n"); fflush(stdout);
		}
		if (i == 0 || i == 1) {
			void *snapshot = i == 0 ? first_snapshot : second_snapshot;
			memcpy(snapshot, map[i], QC10C_BYTES); memset(map[i], 0, QC10C_BYTES);
			if (qbuf_index(vfd, type, i)) pin_until_reboot("live re-QBUF failed");
			printf("LIVE_REQUEUE_INDEX=%u AFTER_SEQUENCE=%u\n", i, i); fflush(stdout);
		}
	}
	if (last_generation != FRAME_COUNT)
		pin_until_reboot("final TL_BG generation is not six");
	if (xioctl(vfd, VIDIOC_STREAMOFF, &type)) { perror("VIDIOC_STREAMOFF"); pin_until_reboot("STREAMOFF failed"); }
	printf("STREAMOFF_OK\n"); fflush(stdout);
	if (save_file(argv[6], first_snapshot, QC10C_BYTES) || save_file(argv[7], second_snapshot, QC10C_BYTES) ||
	    save_file(argv[8], map[2], QC10C_BYTES) || save_file(argv[9], map[3], QC10C_BYTES) ||
	    save_file(argv[10], map[0], QC10C_BYTES) || save_file(argv[11], map[1], QC10C_BYTES)) {
		perror("save QC10C output"); goto out;
	}
	printf("PASS: six-frame regression plus live R5/R6 controls and final TL_BG generation 6\n");
	ret = 0;
out:
	if (iq) memset(iq, 0, IQ_BYTES);
	free(tlbg); free(iq); free(second_snapshot); free(first_snapshot);
	for (i = 0; i < BUFFER_COUNT; i++) if (map[i] != MAP_FAILED) munmap(map[i], map_len[i]);
	if (vfd >= 0) close(vfd);
	return ret;
}
