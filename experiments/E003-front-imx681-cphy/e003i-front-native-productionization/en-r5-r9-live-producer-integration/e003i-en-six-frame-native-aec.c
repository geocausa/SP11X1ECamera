// SPDX-License-Identifier: GPL-2.0-only
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/v4l2-controls.h>
#include <linux/videodev2.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>

#include "native-db-schedule.h"
#include "native-raw-control-join.h"
#include "gain-feed.h"

#define QC10C_WIDTH 2560U
#define QC10C_HEIGHT 1440U
#define QC10C_STRIDE 3584U
#define QC10C_BYTES 0x76b000U
#define BUFFER_COUNT 4U
#define FRAME_COUNT 6U
#define DQBUF_POLL_TIMEOUT_MS 5000
#define PAIR_POLL_US 2000U
#define PAIR_TIMEOUT_MS 5000U
#define CONTROL_GATE_TIMEOUT_MS 5000U
#define IQ_BYTES 41088U
#define V4L2_CID_QCOM_CAMSS_X1E_IQ_CAPSULE (V4L2_CID_USER_BASE + 0x1240)
#define V4L2_CID_QCOM_CAMSS_X1E_TLBG_SNAPSHOT (V4L2_CID_USER_BASE + 0x1241)
#define V4L2_CID_QCOM_CAMSS_X1E_3A_SNAPSHOT (V4L2_CID_USER_BASE + 0x1242)
#define TLBG_HEADER_BYTES 32U
#define TLBG_RAW_BYTES 0xF000U
#define TLBG_BYTES (TLBG_HEADER_BYTES + TLBG_RAW_BYTES)
#define TLBG_MAGIC 0x47424c54U
#define STATS3A_HEADER_BYTES 64U
#define STATS3A_AEC_BYTES 0x14000U
#define STATS3A_BHIST_BYTES 0x1000U
#define STATS3A_AWB_BYTES 0x3C000U
#define STATS3A_RAW_BYTES 0x51000U
#define STATS3A_BYTES (STATS3A_HEADER_BYTES + STATS3A_RAW_BYTES)
#define STATS3A_MAGIC 0x54534133U

static int xioctl(int fd, unsigned long req, void *arg)
{
	int ret;
	do { ret = ioctl(fd, req, arg); } while (ret < 0 && errno == EINTR);
	return ret;
}

_Static_assert(STATS3A_BYTES == E003I_STATS3A_BYTES, "native/raw STATS3A size mismatch");

static int apply_sensor_controls(int fd, const struct e003i_imx681_controls *c)
{
	struct v4l2_ext_control ctrl[4] = {
		{ .id = V4L2_CID_VBLANK, .value = (int)c->vertical_blanking },
		{ .id = V4L2_CID_EXPOSURE, .value = (int)c->exposure_lines },
		{ .id = V4L2_CID_ANALOGUE_GAIN, .value = (int)c->analogue_gain_code },
		{ .id = V4L2_CID_DIGITAL_GAIN, .value = (int)c->digital_gain_code },
	};
	struct v4l2_ext_controls ctrls = {
		.which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 4,
		.controls = ctrl,
	};

	if (fd < 0 || c == NULL)
		return -EINVAL;
	if (xioctl(fd, VIDIOC_S_EXT_CTRLS, &ctrls))
		return -errno;
	return 0;
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

static int get_stats3a(int fd, uint8_t *snapshot, uint64_t *generation,
		       uint32_t *source_seq, uint32_t *slot)
{
	struct v4l2_ext_control ctrl = { .id = V4L2_CID_QCOM_CAMSS_X1E_3A_SNAPSHOT,
		.size = STATS3A_BYTES, .ptr = snapshot };
	struct v4l2_ext_controls ctrls = { .which = V4L2_CTRL_WHICH_CUR_VAL,
		.count = 1, .controls = &ctrl };
	if (xioctl(fd, VIDIOC_G_EXT_CTRLS, &ctrls))
		return -errno;
	if (le32(snapshot) != STATS3A_MAGIC || le16(snapshot + 4) != 1 ||
	    le16(snapshot + 6) != STATS3A_HEADER_BYTES ||
	    le32(snapshot + 24) != 0 || le32(snapshot + 28) != STATS3A_AEC_BYTES ||
	    le32(snapshot + 32) != STATS3A_AEC_BYTES ||
	    le32(snapshot + 36) != STATS3A_BHIST_BYTES ||
	    le32(snapshot + 40) != STATS3A_AEC_BYTES + STATS3A_BHIST_BYTES ||
	    le32(snapshot + 44) != STATS3A_AWB_BYTES || !(le32(snapshot + 48) & 1))
		return -EPROTO;
	*generation = le64(snapshot + 8);
	*source_seq = le32(snapshot + 16);
	*slot = le32(snapshot + 20);
	return *generation && *source_seq && *slot < 2 ? 0 : -EPROTO;
}

struct pair_audit_ctx {
	int fd;
	int sensor_fd;
	int gain_fd;
	uint8_t *tlbg;
	uint8_t *stats3a;
	const char *tlbg_prefix;
	const char *stats3a_prefix;
	struct e003i_request_loop_state aec_state;
	struct e003i_db_schedule_state schedule;
	struct e003i_raw_control_output aec_output[FRAME_COUNT];
	struct e003i_db_apply_event apply_event[FRAME_COUNT];
	atomic_uint video_completed_generation;
	int status;
	unsigned int completed;
};

static int persist_failure_pair(const struct pair_audit_ctx *ctx,
				unsigned int generation,
				const uint8_t *tlbg, const uint8_t *stats3a)
{
	char tlbg_path[4096], stats3a_path[4096];
	int n1, n2, rc1, rc2;

	if (ctx->tlbg_prefix == NULL || ctx->stats3a_prefix == NULL)
		return -EINVAL;
	n1 = snprintf(tlbg_path, sizeof(tlbg_path), "%s-FAIL-G%u.bin",
		      ctx->tlbg_prefix, generation);
	n2 = snprintf(stats3a_path, sizeof(stats3a_path), "%s-FAIL-G%u.bin",
		      ctx->stats3a_prefix, generation);
	if (n1 < 0 || (size_t)n1 >= sizeof(tlbg_path) ||
	    n2 < 0 || (size_t)n2 >= sizeof(stats3a_path))
		return -ENAMETOOLONG;

	rc1 = save_file(tlbg_path, tlbg, TLBG_BYTES);
	rc2 = save_file(stats3a_path, stats3a, STATS3A_BYTES);
	if (rc1 || rc2)
		return rc1 ? rc1 : rc2;
	fprintf(stderr,
		"DB_FAIL_PAIR_SAVED G=%u TLBG=%s STATS3A=%s BYTES=%u/%u\n",
		generation, tlbg_path, stats3a_path, TLBG_BYTES, STATS3A_BYTES);
	fflush(stderr);
	return 0;
}

static int release_control_at_video_boundary(struct pair_audit_ctx *ctx,
					     unsigned int after_generation)
{
	struct e003i_db_apply_event *ev = &ctx->apply_event[after_generation - 1U];
	uint64_t deadline = mono_ns() + (uint64_t)CONTROL_GATE_TIMEOUT_MS * 1000000ULL;
	uint64_t start_ns, end_ns;
	unsigned int completed;
	int rc;

	memset(ev, 0, sizeof(*ev));
	for (;;) {
		completed = atomic_load_explicit(&ctx->video_completed_generation,
						 memory_order_acquire);
		if (completed >= after_generation)
			break;
		if (mono_ns() >= deadline)
			return -ETIMEDOUT;
		usleep(100);
	}
	/* Missing the exact DQBUF window is a hard no-write failure. */
	if (completed != after_generation)
		return -ETIME;

	rc = e003i_db_schedule_release(&ctx->schedule, after_generation, ev);
	if (rc)
		return rc;
	if (!ev->apply || ev->write_after_generation != after_generation)
		return -EPROTO;

	completed = atomic_load_explicit(&ctx->video_completed_generation,
					 memory_order_acquire);
	if (completed != after_generation)
		return -ETIME;
	printf("DB_VIDEO_GATE_PASS SOURCE=%u AFTER_G=%u COMPLETED_G=%u\n",
	       ev->source_generation, after_generation, completed);
	fflush(stdout);

	start_ns = mono_ns();
	rc = apply_sensor_controls(ctx->sensor_fd, &ev->controls);
	end_ns = mono_ns();
	if (rc)
		return rc;
	completed = atomic_load_explicit(&ctx->video_completed_generation,
					 memory_order_acquire);
	printf("DB_SENSOR_WRITE_OK SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u FLL=%u EXP=%u AGAIN=%u DGAIN=%u START_NS=%llu END_NS=%llu ELAPSED_NS=%llu COMPLETED_G=%u\n",
	       ev->source_generation, after_generation,
	       (unsigned long long)ev->logical_request_frame,
	       ev->expected_effect_generation, ev->controls.frame_length_lines,
	       ev->controls.exposure_lines, ev->controls.analogue_gain_code,
	       ev->controls.digital_gain_code,
	       (unsigned long long)start_ns, (unsigned long long)end_ns,
	       (unsigned long long)(end_ns - start_ns), completed);
	fflush(stdout);
	/* A next DQBUF during the ioctl means timing was not tightly bounded. */
	if (completed != after_generation)
		return -ETIME;
	return 0;
}

static void *pair_audit_thread(void *opaque)
{
	struct pair_audit_ctx *ctx = opaque;
	unsigned int target;

	ctx->status = 0;
	ctx->completed = 0;
	for (target = 1; target <= FRAME_COUNT; target++) {
		uint8_t *stats = ctx->stats3a + (size_t)(target - 1) * STATS3A_BYTES;
		uint8_t *tlbg = ctx->tlbg + (size_t)(target - 1) * TLBG_BYTES;
		uint64_t deadline = mono_ns() + (uint64_t)PAIR_TIMEOUT_MS * 1000000ULL;
		uint64_t g3 = 0, gt = 0;
		uint32_t s3 = 0, st = 0, slot3 = 0, slott = 0;

		for (;;) {
			int rc = get_stats3a(ctx->fd, stats, &g3, &s3, &slot3);

			if (rc == -EAGAIN) {
				if (mono_ns() >= deadline) { ctx->status = -ETIMEDOUT; return NULL; }
				usleep(PAIR_POLL_US);
				continue;
			}
			if (rc) { ctx->status = rc; return NULL; }
			if (g3 < target) {
				if (mono_ns() >= deadline) { ctx->status = -ETIMEDOUT; return NULL; }
				usleep(PAIR_POLL_US);
				continue;
			}
			if (g3 > target) { ctx->status = -ERANGE; return NULL; }

			/*
			 * The runner publishes TL_BG immediately before 3A for the same
			 * source sequence/slot. Once target 3A is visible, target TL_BG
			 * is already published and remains valid until the next frame.
			 */
			rc = get_tlbg(ctx->fd, tlbg, &gt, &st, &slott);
			if (rc == -EAGAIN) {
				if (mono_ns() >= deadline) { ctx->status = -ETIMEDOUT; return NULL; }
				usleep(100);
				continue;
			}
			if (rc) { ctx->status = rc; return NULL; }
			if (gt > target) { ctx->status = -ERANGE; return NULL; }
			if (gt < target) {
				if (mono_ns() >= deadline) { ctx->status = -ETIMEDOUT; return NULL; }
				usleep(100);
				continue;
			}
			if (g3 != gt || s3 != st || slot3 != slott ||
			    g3 != target || s3 != target || slot3 != ((target - 1U) & 1U)) {
				ctx->status = -EPROTO;
				e003i_db_schedule_fail(&ctx->schedule);
				return NULL;
			}

			{
				struct e003i_raw_request_input rin = {
					.frame_id = (uint64_t)target - 1U,
					.stats3a = stats,
					.stats3a_bytes = STATS3A_BYTES,
				};
				struct e003i_raw_control_output *aout = &ctx->aec_output[target - 1U];
				struct e003i_db_apply_event *ev = &ctx->apply_event[target - 1U];
				int rc = e003i_raw_request_to_imx681_controls(&ctx->aec_state, &rin, aout);

				if (rc) {
					int evidence_rc;

					ctx->status = rc;
					e003i_db_schedule_fail(&ctx->schedule);
					fprintf(stderr, "DB_AEC_FAIL G=%u RC=%d WRITES=%u\n",
						target, rc, ctx->schedule.released_writes);
					fflush(stderr);
					evidence_rc = persist_failure_pair(ctx, target, tlbg, stats);
					if (evidence_rc) {
						fprintf(stderr,
							"DB_FAIL_PAIR_SAVE_ERROR G=%u RC=%d\n",
							target, evidence_rc);
						fflush(stderr);
					}
					return NULL;
				}
				if (aout->raw.stats_generation != (uint64_t)target ||
				    aout->stats_owned_request_frame != (uint64_t)target + E003I_DB_STATS_TO_REQUEST_DELAY ||
				    aout->sensor_pipeline_delay_frames != E003I_DB_WRITE_TO_EFFECT_DELAY ||
				    aout->camx_history_realign_frames != 0U) {
					ctx->status = -EPROTO;
					e003i_db_schedule_fail(&ctx->schedule);
					fprintf(stderr, "DB_AEC_OWNERSHIP_FAIL G=%u REQUEST=%llu PIPE=%u REALIGN=%u\n",
						target, (unsigned long long)aout->stats_owned_request_frame,
						aout->sensor_pipeline_delay_frames, aout->camx_history_realign_frames);
					fflush(stderr);
					return NULL;
				}
				rc = e003i_db_schedule_queue(&ctx->schedule, target, &aout->controls);
				if (rc) {
					ctx->status = rc;
					e003i_db_schedule_fail(&ctx->schedule);
					fprintf(stderr, "DB_SCHEDULE_QUEUE_FAIL G=%u RC=%d WRITES=%u\n",
						target, rc, ctx->schedule.released_writes);
					fflush(stderr);
					return NULL;
				}
				if (target <= 6U) {
					rc = e003i_gain_feed_publish(ctx->gain_fd, target,
						(uint32_t)aout->stats_owned_request_frame, aout->controls.isp_gain);
					if (rc) {
						ctx->status = rc;
						e003i_db_schedule_fail(&ctx->schedule);
						fprintf(stderr, "EN_GAIN_FEED_FAIL G=%u REQUEST=%llu RC=%d\n",
							target, (unsigned long long)aout->stats_owned_request_frame, rc);
						fflush(stderr);
						return NULL;
					}
				}
				/*
				 * DZ ordering: publish current-generation CQ residual gain first so
				 * the IQ producer can compose/submit concurrently with the previous
				 * generation's sensor ioctl. The completed-DQBUF boundary and N+2
				 * sensor-effect law are unchanged.
				 */
				if (target >= 2U && target <= 4U) {
					rc = release_control_at_video_boundary(ctx, target);
					if (rc) {
						ctx->status = rc;
						e003i_db_schedule_fail(&ctx->schedule);
						fprintf(stderr, "DZ_BOUNDARY_RELEASE_FAIL AFTER_G=%u RC=%d WRITES=%u\n",
							target, rc, ctx->schedule.released_writes);
						fflush(stderr);
						return NULL;
					}
				}
				{
					uint32_t isp_bits;
					memcpy(&isp_bits, &aout->controls.isp_gain, sizeof(isp_bits));
					printf("DZ_AEC_ACCEPT G=%u REQUEST=%llu FLL=%u VB=%u EXP=%u AGAIN=%u DGAIN=%u ISP=0x%08x RELEASED_AT_G=%u RELEASE_SOURCE=%u EFFECT=%u\n",
					       target, (unsigned long long)aout->stats_owned_request_frame,
					       aout->controls.frame_length_lines, aout->controls.vertical_blanking,
					       aout->controls.exposure_lines, aout->controls.analogue_gain_code,
					       aout->controls.digital_gain_code, isp_bits,
					       ev->apply ? ev->write_after_generation : 0U,
					       ev->apply ? ev->source_generation : 0U,
					       ev->apply ? ev->expected_effect_generation : 0U);
					fflush(stdout);
				}

			}
			ctx->completed = target;
			break;
		}
	}
	return NULL;
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
	uint8_t *iq = NULL, *audit_tlbg = NULL, *audit_stats3a = NULL;
	const char *video, *sensor, *tlbg_prefix, *stats3a_prefix;
	enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
	int vfd = -1, sfd = -1, ret = 1, ready_pipe[2] = { -1, -1 }, gain_pipe[2] = { -1, -1 };
	pid_t producer_pid = -1; int producer_reaped = 0, producer_status = 0;
	pthread_t audit_thread;
	struct pair_audit_ctx audit = { 0 };
	int audit_started = 0, audit_joined = 0;
	unsigned int i;

	if (argc != 14) {
		fprintf(stderr, "usage: %s /dev/videoN R4.bin producer.py producer-out producer-manifest TLBG-prefix 3A-prefix out0 out1 out2 out3 out4 out5\n", argv[0]);
		return 2;
	}
	video = argv[1]; tlbg_prefix = argv[6]; stats3a_prefix = argv[7];
	sensor = getenv("DB_SUBDEV");
	if (sensor == NULL || sensor[0] != '/') {
		fprintf(stderr, "DB_SUBDEV missing or not absolute\n");
		return 3;
	}
	vfd = open(video, O_RDWR | O_CLOEXEC);
	if (vfd < 0) { perror("open video"); return 1; }
	sfd = open(sensor, O_RDWR | O_CLOEXEC);
	if (sfd < 0) { perror("open sensor subdev"); goto out; }
	iq = malloc(IQ_BYTES);
	audit_tlbg = malloc((size_t)FRAME_COUNT * TLBG_BYTES);
	audit_stats3a = malloc((size_t)FRAME_COUNT * STATS3A_BYTES);
	if (!iq || !audit_tlbg || !audit_stats3a) { perror("malloc control buffers"); goto out; }

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

	/* Start the live producer and require it to finish all imports/native builds/static recipe work before STREAMON. */
	if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) { perror("ignore SIGPIPE"); goto out; }
	if (pipe2(ready_pipe, O_CLOEXEC)) { perror("producer ready pipe"); goto out; }
	if (pipe2(gain_pipe, O_CLOEXEC)) { perror("AEC gain pipe"); goto out; }
	producer_pid = fork();
	if (producer_pid < 0) { perror("fork producer"); goto out; }
	if (producer_pid == 0) {
		char fdarg[32], readyarg[32], gainarg[32]; int fl;
		close(ready_pipe[0]);
		close(gain_pipe[1]);
		fl = fcntl(vfd, F_GETFD); if (fl >= 0) fcntl(vfd, F_SETFD, fl & ~FD_CLOEXEC);
		fl = fcntl(ready_pipe[1], F_GETFD); if (fl >= 0) fcntl(ready_pipe[1], F_SETFD, fl & ~FD_CLOEXEC);
		fl = fcntl(gain_pipe[0], F_GETFD); if (fl >= 0) fcntl(gain_pipe[0], F_SETFD, fl & ~FD_CLOEXEC);
		snprintf(fdarg, sizeof(fdarg), "%d", vfd); snprintf(readyarg, sizeof(readyarg), "%d", ready_pipe[1]);
		snprintf(gainarg, sizeof(gainarg), "%d", gain_pipe[0]);
		execlp("python3", "python3", argv[3], "--mode", "live", "--fd", fdarg, "--ready-fd", readyarg,
		       "--aec-gain-fd", gainarg, "--output-dir", argv[4], "--manifest", argv[5], (char *)NULL);
		perror("exec producer"); _exit(127);
	}
	close(ready_pipe[1]); ready_pipe[1] = -1;
	close(gain_pipe[0]); gain_pipe[0] = -1;
	{
		struct pollfd rp = { .fd = ready_pipe[0], .events = POLLIN }; char ch = 0; int pr = poll(&rp, 1, 20000);
		if (pr != 1 || !(rp.revents & POLLIN) || read(ready_pipe[0], &ch, 1) != 1 || ch != 'R') {
			fprintf(stderr, "producer did not become ready before STREAMON\n"); goto out;
		}
		close(ready_pipe[0]); ready_pipe[0] = -1;
	}
	printf("DZ_PRODUCER_CHILD_READY PID=%d\n", (int)producer_pid); fflush(stdout);
	audit.fd = vfd; audit.sensor_fd = sfd; audit.gain_fd = gain_pipe[1]; audit.tlbg = audit_tlbg; audit.stats3a = audit_stats3a;
	audit.tlbg_prefix = tlbg_prefix; audit.stats3a_prefix = stats3a_prefix;
	atomic_init(&audit.video_completed_generation, 0U);
	if (e003i_request_loop_init(&audit.aec_state)) {
		fprintf(stderr, "native AEC state init failed\n"); goto out;
	}
	e003i_db_schedule_init(&audit.schedule);
	if (pthread_create(&audit_thread, NULL, pair_audit_thread, &audit)) {
		perror("pthread_create pair audit"); goto out;
	}
	audit_started = 1;
	printf("AO_PAIR_AUDIT_THREAD_READY ORDER=3A_THEN_TLBG TARGETS=1..6\n"); fflush(stdout);
	if (read_exact(argv[2], iq, IQ_BYTES) || submit_iq(vfd, iq)) {
		perror("submit template-free R4 before STREAMON"); goto out;
	}
	printf("IQ_R4_TEMPLATE_FREE_SUBMITTED_PRE_STREAMON\n"); fflush(stdout);
	if (xioctl(vfd, VIDIOC_STREAMON, &type)) {
		perror("VIDIOC_STREAMON"); pin_until_reboot("STREAMON failed; preserve driver-owned DMA");
	}
	printf("STREAMON_OK_ASYNC MONO_NS=%llu\n", (unsigned long long)mono_ns()); fflush(stdout);

	for (i = 0; i < FRAME_COUNT; i++) {
		struct pollfd pfd = { .fd = vfd, .events = POLLIN };
		struct v4l2_plane plane = { 0 }; struct v4l2_buffer b = { 0 };
		uint64_t ps = mono_ns(); int pr = poll(&pfd, 1, DQBUF_POLL_TIMEOUT_MS); uint64_t pe = mono_ns();
		printf("POLL%u_START_NS=%llu END_NS=%llu ELAPSED_NS=%llu RC=%d REVENTS=0x%x\n", i,
		       (unsigned long long)ps, (unsigned long long)pe, (unsigned long long)(pe-ps), pr, pfd.revents);
		fflush(stdout);
		if (pr <= 0) pin_until_reboot(pr == 0 ? "DQBUF poll timeout" : "DQBUF poll error");
		b.type = type; b.memory = V4L2_MEMORY_MMAP; b.length = 1; b.m.planes = &plane;
		if (xioctl(vfd, VIDIOC_DQBUF, &b)) { perror("VIDIOC_DQBUF"); pin_until_reboot("DQBUF failed"); }
		if (b.index != expect_index[i] || plane.bytesused != QC10C_BYTES || b.sequence != i)
			pin_until_reboot("unexpected completed buffer ordering");
		atomic_store_explicit(&audit.video_completed_generation, i + 1U, memory_order_release);
		printf("DQBUF%u_INDEX=%u BYTESUSED=%u SEQUENCE=%u\n", i, b.index, plane.bytesused, b.sequence);
		printf("DB_VIDEO_COMPLETION_PUBLISH G=%u\n", i + 1U);
		if (producer_pid > 0 && !producer_reaped) {
			pid_t wp = waitpid(producer_pid, &producer_status, WNOHANG);
			if (wp == producer_pid) {
				producer_reaped = 1;
				if (!WIFEXITED(producer_status) || WEXITSTATUS(producer_status) != 0)
					pin_until_reboot("live producer exited with failure");
				printf("AE_PRODUCER_EXIT_OK\n"); fflush(stdout);
			}
		}

		if (i == 0 || i == 1) {
			void *snapshot = i == 0 ? first_snapshot : second_snapshot;
			memcpy(snapshot, map[i], QC10C_BYTES); memset(map[i], 0, QC10C_BYTES);
			if (qbuf_index(vfd, type, i)) pin_until_reboot("live re-QBUF failed");
			printf("LIVE_REQUEUE_INDEX=%u AFTER_SEQUENCE=%u\n", i, i); fflush(stdout);
		}
	}
	if (!audit_started || pthread_join(audit_thread, NULL))
		pin_until_reboot("paired-stats audit thread join failed");
	audit_joined = 1;
	if (audit.status || audit.completed != FRAME_COUNT)
		pin_until_reboot("paired-stats/native-AEC collector failed or missed a generation");
	if (audit.schedule.failed || audit.schedule.queued_generation != FRAME_COUNT ||
	    audit.schedule.released_writes != E003I_DB_WRITTEN_SOURCE_GENERATIONS)
		pin_until_reboot("native-AEC delayed sensor schedule did not release exactly G1..G3");
	printf("DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..6 WRITES=%u RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6\n",
	       audit.schedule.released_writes);
	fflush(stdout);
	for (i = 0; i < FRAME_COUNT; i++) {
		uint8_t *t = audit_tlbg + (size_t)i * TLBG_BYTES;
		uint8_t *s3 = audit_stats3a + (size_t)i * STATS3A_BYTES;
		uint64_t gt = le64(t + 8), g3 = le64(s3 + 8);
		uint32_t st = le32(t + 16), sseq3 = le32(s3 + 16);
		uint32_t slott = le32(t + 20), slot3 = le32(s3 + 20);
		char path[4096];

		if (gt != i + 1 || g3 != gt || st != i + 1 || sseq3 != st ||
		    slott != (i & 1U) || slot3 != slott)
			pin_until_reboot("stored paired-stats identity outside exact bounded run");
		snprintf(path, sizeof(path), "%s-%u.bin", tlbg_prefix, i);
		if (save_file(path, t, TLBG_BYTES)) pin_until_reboot("TL_BG snapshot save failed");
		snprintf(path, sizeof(path), "%s-%u.bin", stats3a_prefix, i);
		if (save_file(path, s3, STATS3A_BYTES)) pin_until_reboot("3A snapshot save failed");
		printf("TLBG_READ%u_GENERATION=%llu SOURCE_SEQ=%u SLOT=%u BYTES=%u\n", i,
		       (unsigned long long)gt, st, slott, TLBG_BYTES);
		printf("STATS3A_READ%u_GENERATION=%llu SOURCE_SEQ=%u SLOT=%u BYTES=%u\n", i,
		       (unsigned long long)g3, sseq3, slot3, STATS3A_BYTES);
	}
	fflush(stdout);
	if (producer_pid > 0 && !producer_reaped) {
		if (waitpid(producer_pid, &producer_status, 0) != producer_pid) pin_until_reboot("waitpid producer failed");
		producer_reaped = 1;
	}
	if (producer_pid <= 0 || !WIFEXITED(producer_status) || WEXITSTATUS(producer_status) != 0)
		pin_until_reboot("live producer did not complete successfully");
	if (xioctl(vfd, VIDIOC_STREAMOFF, &type)) { perror("VIDIOC_STREAMOFF"); pin_until_reboot("STREAMOFF failed"); }
	printf("STREAMOFF_OK\n"); fflush(stdout);
	if (save_file(argv[8], first_snapshot, QC10C_BYTES) || save_file(argv[9], second_snapshot, QC10C_BYTES) ||
	    save_file(argv[10], map[2], QC10C_BYTES) || save_file(argv[11], map[3], QC10C_BYTES) ||
	    save_file(argv[12], map[0], QC10C_BYTES) || save_file(argv[13], map[1], QC10C_BYTES)) {
		perror("save QC10C output"); goto out;
	}
	printf("PASS: six-frame regression plus producer-derived R5/R6 and paired TL_BG/3A generations 1..6 (AO collector)\n");
	ret = 0;
out:
	/* The audit thread owns the gain-pipe writer. Stop that owner before
	 * closing shared descriptors so pre-stream failures cannot race EBADF. */
	if (audit_started && !audit_joined) { pthread_cancel(audit_thread); pthread_join(audit_thread, NULL); audit_joined = 1; }
	if (ready_pipe[0] >= 0) close(ready_pipe[0]);
	if (ready_pipe[1] >= 0) close(ready_pipe[1]);
	if (gain_pipe[0] >= 0) close(gain_pipe[0]);
	if (gain_pipe[1] >= 0) close(gain_pipe[1]);
	if (producer_pid > 0 && !producer_reaped) { kill(producer_pid, SIGTERM); waitpid(producer_pid, NULL, 0); producer_reaped = 1; }
	if (iq) memset(iq, 0, IQ_BYTES);
	free(audit_stats3a); free(audit_tlbg); free(iq); free(second_snapshot); free(first_snapshot);
	for (i = 0; i < BUFFER_COUNT; i++) if (map[i] != MAP_FAILED) munmap(map[i], map_len[i]);
	if (sfd >= 0) close(sfd);
	if (vfd >= 0) close(vfd);
	return ret;
}
