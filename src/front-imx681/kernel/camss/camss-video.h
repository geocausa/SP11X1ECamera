/* SPDX-License-Identifier: GPL-2.0 */
/*
 * camss-video.h
 *
 * Qualcomm MSM Camera Subsystem - V4L2 device node
 *
 * Copyright (c) 2013-2015, The Linux Foundation. All rights reserved.
 * Copyright (C) 2015-2018 Linaro Ltd.
 */
#ifndef QC_MSM_CAMSS_VIDEO_H
#define QC_MSM_CAMSS_VIDEO_H

#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/wait.h>
#include <linux/workqueue.h>
#include <linux/videodev2.h>
#include <media/media-entity.h>
#include <media/v4l2-ctrls.h>
#include <media/v4l2-dev.h>
#include <media/v4l2-device.h>
#include <media/v4l2-fh.h>
#include <media/v4l2-mediabus.h>
#include <media/videobuf2-v4l2.h>

#define CAMSS_X1E_TLBG_RAW_BYTES		0x0000f000
#define CAMSS_X1E_TLBG_SNAPSHOT_HEADER_BYTES	32
#define CAMSS_X1E_TLBG_SNAPSHOT_BYTES		\
	(CAMSS_X1E_TLBG_SNAPSHOT_HEADER_BYTES + CAMSS_X1E_TLBG_RAW_BYTES)

#define CAMSS_X1E_3A_AEC_BE_RAW_BYTES		0x00014000
#define CAMSS_X1E_3A_BHIST_RAW_BYTES		0x00001000
#define CAMSS_X1E_3A_AWB_BG_RAW_BYTES		0x0003c000
#define CAMSS_X1E_3A_RAW_BYTES			0x00051000
#define CAMSS_X1E_3A_SNAPSHOT_HEADER_BYTES	64
#define CAMSS_X1E_3A_SNAPSHOT_BYTES		\
	(CAMSS_X1E_3A_SNAPSHOT_HEADER_BYTES + CAMSS_X1E_3A_RAW_BYTES)

struct camss_buffer {
	struct vb2_v4l2_buffer vb;
	dma_addr_t addr[3];
	struct list_head queue;
};

struct camss_video;

struct camss_video_ops {
	int (*queue_buffer)(struct camss_video *vid, struct camss_buffer *buf);
	int (*flush_buffers)(struct camss_video *vid,
			     enum vb2_buffer_state state);
};

struct camss_video {
	struct camss *camss;
	struct vb2_queue vb2_q;
	struct video_device vdev;
	struct media_pad pad;
	struct v4l2_format active_fmt;
	enum v4l2_buf_type type;
	struct media_pipeline pipe;
	const struct camss_video_ops *ops;
	struct v4l2_ctrl_handler ctrl_handler;
	struct mutex lock;
	struct mutex q_lock;
	unsigned int bpl_alignment;
	unsigned int line_based;
	/* E003h bounded V4L2 bridge state; software ownership only. */
	bool x1e_pix_runner_stopped;
	bool x1e_pix_runner_pinned;
	/* E003h 0071 bounded asynchronous live-requeue state. */
	struct work_struct x1e_pix_work;
	wait_queue_head_t x1e_pix_buf_wait;
	bool x1e_pix_worker_started;
	bool x1e_pix_live_active;
	bool x1e_pix_stop_requested;
	int x1e_pix_worker_ret;
	/* E003h 0072 provider-owned steady IQ packet FIFO; software only. */
	struct list_head x1e_pix_iq_pending;
	struct mutex x1e_pix_iq_lock;
	wait_queue_head_t x1e_pix_iq_wait;
	u64 x1e_pix_iq_last_enqueued;
	u64 x1e_pix_iq_last_dequeued;
	unsigned int x1e_pix_iq_depth;
	bool x1e_pix_iq_closed;
	/* E003i-Q latest completed TL_BG snapshot; generation-tagged, read-only. */
	struct mutex x1e_tlbg_lock;
	u8 *x1e_tlbg_snapshot;
	u64 x1e_tlbg_generation;
	u32 x1e_tlbg_source_seq;
	u32 x1e_tlbg_slot;
	bool x1e_tlbg_valid;
	/* E003i-Y latest completed AEC/BHist/AWB bundle; source-sequence tagged. */
	struct mutex x1e_3a_lock;
	u8 *x1e_3a_snapshot;
	u64 x1e_3a_generation;
	u32 x1e_3a_source_seq;
	u32 x1e_3a_slot;
	bool x1e_3a_valid;
	const struct camss_format_info *formats;
	unsigned int nformats;
};

int msm_video_register(struct camss_video *video, struct v4l2_device *v4l2_dev,
		       const char *name);

void msm_video_unregister(struct camss_video *video);
void camss_x1e_tlbg_reset(struct camss_video *video);
int camss_x1e_tlbg_publish(struct camss_video *video, const void *raw,
			   size_t raw_size, u32 source_seq, u32 slot);
void camss_x1e_3a_reset(struct camss_video *video);
int camss_x1e_3a_publish(struct camss_video *video,
			 const void *aec_be, size_t aec_be_size,
			 const void *bhist, size_t bhist_size,
			 const void *awb_bg, size_t awb_bg_size,
			 u32 source_seq, u32 slot);

#endif /* QC_MSM_CAMSS_VIDEO_H */
