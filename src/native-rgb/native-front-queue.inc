/* SPDX-License-Identifier: GPL-2.0-only */
/* Included after the real front startup/result types and CDM/owner primitives. */
static int native_front_queue_complete(struct camss *camss,
				      const struct camss_x1e_pix_runner_request *req,
				      struct camss_x1e_pix_runner_result *result,
				      struct vfe680_x1e_pix_runtime *pix,
				      struct csid_device *csid, unsigned int slot,
				      u32 frame, u32 base)
{
	struct camss_buffer *done = NULL;
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
	bool bl_complete[2] = { true, true };
	u32 frame;
	int ret;

	if (!req->native_queue || !req->live_video ||
	    !camss_x1e_native_front_queue_trial_allowed(camss) ||
	    result->live_completed != 3 || !epoch0_seq)
		return -EINVAL;
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

		if (READ_ONCE(req->live_video->x1e_pix_stop_requested))
			return 0;
		if (frame == U32_MAX || frame > U32_MAX - video_base)
			return -EOVERFLOW;
		if (result->native_inflight[slot] || !bl_complete[slot])
			return -EBUSY;
		buffer = camss_x1e_pix_v4l2_wait_pending(req->live_video,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (IS_ERR(buffer))
			return PTR_ERR(buffer) == -ECANCELED ? 0 : PTR_ERR(buffer);
		result->native_inflight[slot] = buffer;
		ret = camss_x1e_pix_v4l2_buffer(req->live_video, buffer);
		if (ret)
			return ret;

		/* Previous owner retired and all five BL_DONE receipts arrived. */
		camss_x1e_epoch0_release(camss, &commands[slot]);
		ret = camss_x1e_pix_iq_provider_next_steady(camss, req->live_video,
							  frame, &commands[slot]);
		if (ret)
			return ret == -ECANCELED ? 0 : ret;
		if (READ_ONCE(req->live_video->x1e_pix_stop_requested))
			return 0;
		ret = csid680_x1e_front_poll_next_epoch0(csid, *epoch0_seq,
						       CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			return ret;
		*epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, slot, buffer);
		if (ret)
			return ret;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, slot);
		if (ret)
			return ret;
		bl_complete[slot] = false;
		ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss, &commands[slot]);
		if (ret)
			return ret;
		/* fifo0_commit() synchronously verifies BL_DONE for every BL. */
		bl_complete[slot] = true;
		ret = native_front_queue_complete(camss, req, result, pix, csid,
						 slot ^ 1, frame - 1, video_base);
		if (ret)
			return ret;
	}
}
