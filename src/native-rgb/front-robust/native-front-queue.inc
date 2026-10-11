/* SPDX-License-Identifier: GPL-2.0-only */
/* Included after the real front startup/result types and CDM/owner primitives. */

/*
 * Robust front queue (native_front_queue_robust). Without it the serialized
 * queue stops the stream as soon as the consumer is late: it needs a returned
 * V4L2 buffer and the next IQ packet for every frame. With it a frame without a
 * consumer buffer is written to a driver-owned scratch buffer and dropped, and a
 * frame without a new IQ packet reuses the newest parameters received. Frame
 * pacing against the hardware is unchanged; only the two consumer waits change.
 */
static bool native_front_queue_robust;
module_param(native_front_queue_robust, bool, 0400);
MODULE_PARM_DESC(native_front_queue_robust,
		 "Front queue: drop frames to a scratch buffer and reuse the last IQ parameters instead of stopping");
static unsigned int native_front_queue_wait_us = 15000;
module_param(native_front_queue_wait_us, uint, 0400);
MODULE_PARM_DESC(native_front_queue_wait_us,
		 "Robust front queue: longest wait for a consumer buffer before dropping the frame");

#define NATIVE_FRONT_SCRATCH_BYTES 5529600U
#define NATIVE_FRONT_SCRATCH_UV 3686400U

static struct camss_buffer *native_front_scratch;
static struct device *native_front_scratch_dev;

/*
 * The scratch buffer is device-managed: the hardware may still write to it
 * until the outer runner has stopped the pipeline, so it is never freed while
 * the device is bound.
 */
static struct camss_buffer *native_front_scratch_get(struct camss *camss)
{
	struct camss_buffer *b;
	dma_addr_t dma;
	void *cpu;

	if (native_front_scratch && native_front_scratch_dev == camss->dev)
		return native_front_scratch;
	b = devm_kzalloc(camss->dev, sizeof(*b), GFP_KERNEL);
	if (!b)
		return NULL;
	cpu = dmam_alloc_coherent(camss->dev, NATIVE_FRONT_SCRATCH_BYTES, &dma, GFP_KERNEL);
	if (!cpu)
		return NULL;
	b->addr[0] = dma;
	b->addr[1] = dma + NATIVE_FRONT_SCRATCH_UV;
	b->vb.vb2_buf.num_planes = 1;
	b->vb.vb2_buf.planes[0].length = NATIVE_FRONT_SCRATCH_BYTES;
	native_front_scratch = b;
	native_front_scratch_dev = camss->dev;
	return b;
}

static int native_front_queue_complete(struct camss *camss,
				      const struct camss_x1e_pix_runner_request *req,
				      struct camss_x1e_pix_runner_result *result,
				      struct vfe680_x1e_pix_runtime *pix,
				      struct csid_device *csid, unsigned int slot,
				      u32 frame, u32 base)
{
	struct camss_buffer *done = NULL;
	bool scratch;
	u32 seq, target;
	int ret;

	if (slot >= 2 || !result->native_inflight[slot] || frame > U32_MAX - base)
		return -EPROTO;
	target = base + frame;
	seq = csid680_x1e_front_video_seq(csid);
	if (seq > target)
		return -EPROTO;
	if (seq < target) {
		ret = csid680_x1e_front_poll_video(csid, seq,
						 CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			return ret;
	}
	if (csid680_x1e_front_video_seq(csid) != target)
		return -EPROTO;
	ret = csid680_x1e_front_poll_all_done(csid, target,
					    CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
	if (ret)
		return ret;
	/* The actual retirement functions enforce IRQ-latched consumed IOVAs. */
	ret = vfe680_x1e_pix_runtime_retire_video(pix, slot, &done);
	if (ret)
		return ret;
	if (done != result->native_inflight[slot])
		return -EPROTO;
	scratch = native_front_scratch && done == native_front_scratch;
	/*
	 * The statistics snapshots advance on every hardware frame (their
	 * generation tracks the frame sequence); a dropped frame only skips the
	 * image and metadata completion below.
	 */
	ret = camss_x1e_pix_publish_tlbg(req->live_video, pix, slot, target);
	if (ret)
		return ret;
	ret = camss_x1e_pix_publish_3a(req->live_video, pix, slot, target);
	if (ret)
		return ret;
	ret = vfe680_x1e_pix_runtime_retire_aux(pix, slot);
	if (ret)
		return ret;
	result->native_inflight[slot] = NULL;
	if (!scratch)
		camss_x1e_pix_v4l2_complete_live(result, done, frame - 1);
	return 0;
}

static int native_front_queue_run(struct camss *camss,
				 const struct camss_x1e_pix_runner_request *req,
				 struct camss_x1e_pix_runner_result *result,
				 struct vfe680_x1e_pix_runtime *pix,
				 struct csid_device *csid, struct vfe_device *vfe,
				 u32 *epoch0_seq, u32 video_base)
{
	struct camss_x1e_epoch0_materialized *commands;
	struct camss_buffer *scratch = NULL;
	bool bl_complete[2] = { true, true };
	unsigned int dropped = 0, reused = 0;
	u32 frame;
	int ret;

	if (!req->native_queue || !req->live_video ||
	    !camss_x1e_native_front_queue_trial_allowed(camss) ||
	    result->live_completed != 3 || !epoch0_seq)
		return -EINVAL;
	if (native_front_queue_robust) {
		scratch = native_front_scratch_get(camss);
		if (!scratch)
			return -ENOMEM;
		camss_x1e_pix_iq_robust_reset();
	}
	commands = kcalloc(2, sizeof(*commands), GFP_KERNEL);
	if (!commands)
		return -ENOMEM;
	/* The outer runner owns this memory through hardware stop on every exit. */
	result->native_commands = commands;
	result->native_inflight[1] = req->video[3];

	/* Frame4 is already bound to slot1. Always queue N before retiring N-1. */
	for (frame = 5; ; frame++) {
		struct camss_buffer *buffer;
		unsigned int slot = (frame - 1) & 1;
		bool iq_reused = false;

		if (READ_ONCE(req->live_video->x1e_pix_stop_requested)) {
			ret = 0;
			break;
		}
		if (frame == U32_MAX || frame > U32_MAX - video_base) {
			ret = -EOVERFLOW;
			break;
		}
		if (result->native_inflight[slot] || !bl_complete[slot]) {
			ret = -EBUSY;
			break;
		}
		if (scratch) {
			buffer = camss_x1e_pix_v4l2_wait_pending(req->live_video,
								 native_front_queue_wait_us);
			if (IS_ERR(buffer)) {
				if (PTR_ERR(buffer) == -ECANCELED) {
					ret = 0;
					break;
				}
				buffer = scratch;
				dropped++;
			}
		} else {
			buffer = camss_x1e_pix_v4l2_wait_pending(req->live_video,
								 CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (IS_ERR(buffer)) {
				ret = PTR_ERR(buffer) == -ECANCELED ? 0 : PTR_ERR(buffer);
				break;
			}
		}
		result->native_inflight[slot] = buffer;
		if (buffer != scratch) {
			ret = camss_x1e_pix_v4l2_buffer(req->live_video, buffer);
			if (ret)
				break;
		}

		/* Previous owner retired and all five BL_DONE receipts arrived. */
		camss_x1e_epoch0_release(camss, &commands[slot]);
		if (scratch)
			ret = camss_x1e_pix_iq_provider_next_robust(camss, req->live_video,
								    frame, &commands[slot],
								    &iq_reused);
		else
			ret = camss_x1e_pix_iq_provider_next_steady(camss, req->live_video,
								  frame, &commands[slot]);
		if (ret) {
			if (ret == -ECANCELED)
				ret = 0;
			break;
		}
		if (iq_reused)
			reused++;
		if (READ_ONCE(req->live_video->x1e_pix_stop_requested)) {
			ret = 0;
			break;
		}
		ret = csid680_x1e_front_poll_next_epoch0(csid, *epoch0_seq,
						       CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			break;
		*epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, slot, buffer);
		if (ret)
			break;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, slot);
		if (ret)
			break;
		bl_complete[slot] = false;
		ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss, &commands[slot]);
		if (ret)
			break;
		/* fifo0_commit() synchronously verifies BL_DONE for every BL. */
		bl_complete[slot] = true;
		ret = native_front_queue_complete(camss, req, result, pix, csid,
						 slot ^ 1, frame - 1, video_base);
		if (ret)
			break;
	}
	if (scratch) {
		camss_x1e_pix_iq_robust_reset();
		dev_info(camss->dev,
			 "NATIVE_FRONT_QUEUE_ROBUST frames=%u dropped=%u iq_reused=%u ret=%d\n",
			 frame - 5, dropped, reused, ret);
	}
	return ret;
}
