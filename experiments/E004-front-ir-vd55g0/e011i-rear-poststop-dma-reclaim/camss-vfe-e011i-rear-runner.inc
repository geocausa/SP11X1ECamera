/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008k: complete rear two-slot runner orchestration, deliberately unreachable.
 *
 * This file is included only in a fresh isolated build.  It composes the
 * already accepted E007y/E008a/E008h/E008i/E008j contracts but installs no
 * module parameter, probe hook, V4L2 callback or other runtime call site.
 */
#ifndef VFE680_E008K_REAR_COMPLETE_RUNNER_INC
#define VFE680_E008K_REAR_COMPLETE_RUNNER_INC

#include "camss-e008k-rear-bridge.h"

#define E008K_REAR_EPOCH_TIMEOUT_US	500000UL
#define E008K_REAR_DONE_TIMEOUT_US	1000000UL

struct e008k_rear_request {
	struct v4l2_subdev *sensor;
	struct e007d_rear_register_state *regs;
	struct e007v_rear_dmi_state *dmi_state;
	struct e007y_rear_startup_output packet[E007Y_STARTUP_PACKETS];
	u64 packet_request_id[E007Y_STARTUP_PACKETS];
	u64 first_request_generation;
	unsigned long epoch_timeout_us;
	unsigned long done_timeout_us;
};

struct e008k_rear_result {
	u64 owner_epoch;
	u32 epoch0_seq;
	u32 done_events;
	bool packet_submitted[E007Y_STARTUP_PACKETS];
	bool slot0_enabled;
	bool slot1_programmed;
	bool both_frames_complete;
	bool csid_quiesced;
	bool bus_stopped;
	bool rtcdm_stopped;
	bool source_stopped;
	bool ledgers_released;
	bool owner_released;
	bool dma_intentionally_pinned;
	bool dma_reclaimed;
};

static int
e008k_rear_submit_packet(struct camss *camss,
			 const struct e007y_rear_startup_output *out)
{
	unsigned int i;
	int ret;

	if (!camss || !out || !out->bl_count || out->bl_count > E007Y_MAX_BL)
		return -EINVAL;
	for (i = 0; i < out->bl_count; i++) {
		if (!out->bl[i].dma || !out->bl[i].bytes)
			return -EINVAL;
		ret = e008k_rear_rtcdm_submit_bl(camss, out->bl[i].dma,
						 out->bl[i].bytes);
		if (ret)
			return ret;
	}
	return 0;
}

static int
e008k_rear_materialize_all(struct e008k_rear_request *req)
{
	unsigned int p;
	int ret;

	if (!req || !req->sensor || !req->regs || !req->dmi_state ||
	    !req->first_request_generation)
		return -EINVAL;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		if (!req->packet_request_id[p])
			return -EINVAL;
		ret = e007y_rear_materialize(req->regs, req->dmi_state,
					     req->packet_request_id[p], p,
					     &req->packet[p]);
		if (ret)
			return ret;
	}
	return 0;
}

static int
e008k_rear_collect_done(struct csid_device *csid,
			struct e008h_rear_prime_pair *pair,
			u64 owner_epoch, unsigned long timeout_us,
			u32 *cursor)
{
	while (!e008h_rear_both_complete(pair, owner_epoch)) {
		u32 count = csid680_e008i_rear_done_count(csid);
		int ret;

		while (*cursor < count) {
			struct e008i_rear_done_event evt;
			unsigned int i;

			ret = csid680_e008i_rear_done_event(csid, *cursor, &evt);
			if (ret)
				return ret;
			if (evt.owner_epoch != owner_epoch)
				return -ESTALE;

			for (i = 0; i < E008I_REAR_WMS; i++) {
				if (!(evt.wm_mask & BIT(i)))
					continue;
				ret = e008h_rear_observe_consumed(
					pair, owner_epoch,
					evt.raw_buf_done_status,
					e008i_rear_wm[i],
					evt.addr_status0[i]);
				if (ret && ret != -EALREADY)
					return ret;
			}
			(*cursor)++;
			if (e008h_rear_both_complete(pair, owner_epoch))
				return 0;
		}

		ret = csid680_e008i_rear_poll_done(csid, count, timeout_us);
		if (ret)
			return ret;
	}
	return 0;
}

/*
 * Source-only post-stop reclaim. All evidence is produced inside the runner:
 * the owner is still exclusive, both exact-IOVA ledgers completed, CSID/BUS
 * IRQs have been drained, RT-CDM and both sources are stopped. Recheck every
 * allocation before freeing any of them. A failure leaves all DMA pinned.
 * This does not establish hardware completion by itself.
 */
static int
e011i_rear_reclaim_after_stop(struct camss *camss, struct vfe_device *vfe,
                             struct e008h_rear_prime_pair *pair,
                             u64 owner_epoch,
                             const struct e008k_rear_result *result)
{
    u64 current_epoch;
    unsigned int s, i;

    if (!camss || !vfe || vfe->camss != camss ||
        !vfe680_e004nt_rear_4k_target(vfe) || !pair || !owner_epoch || !result ||
        !result->csid_quiesced || !result->bus_stopped ||
        !result->rtcdm_stopped || !result->source_stopped ||
        result->owner_released || result->dma_reclaimed ||
        !e008h_rear_both_complete(pair, owner_epoch) ||
        !e005y_vfe1_rear_sample_begin(&camss->e005y_vfe1_owner,
                                      true, &current_epoch) ||
        current_epoch != owner_epoch)
        return -EBUSY;

    for (s = 0; s < E008H_REAR_SLOTS; s++) {
        const struct e008d_rear_dma_set *set = &pair->dma[s];

        if (!set->allocated || !set->prepared_disabled ||
            !set->full.in_flight || !set->full.cpu ||
            set->full.size != VFE680_E004NT_REAR_TOTAL_BYTES ||
            pair->frame[s].owner_epoch != owner_epoch ||
            !pair->frame[s].request_generation || pair->frame[s].pending ||
            pair->frame[s].faulted)
            return -EPROTO;
        for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {
            const struct vfe680_e004nu_rear_wm_static *c;

            c = e008d_rear_contract_for_wm(set->aux[i].wm);
            if (!c || !set->aux[i].cpu ||
                set->aux[i].size != c->frame_incr)
                return -EPROTO;
        }
    }

    for (s = 0; s < E008H_REAR_SLOTS; s++) {
        pair->dma[s].full.in_flight = false;
        e008d_rear_release_partial(vfe, &pair->dma[s]);
    }
    return 0;
}

static int
e008k_rear_pair_stop_release(struct camss *camss,
			     struct vfe_device *vfe,
			     struct csid_device *csid,
			     struct csiphy_device *csiphy,
			     struct v4l2_subdev *sensor,
			     struct e008h_rear_prime_pair *pair,
			     struct media_entity *video_entity,
			     u64 owner_epoch,
			     bool *pipeline_powered,
			     bool *rtcdm_started,
			     bool *csiphy_streaming,
			     bool *sensor_streaming,
			     struct e008k_rear_result *result)
{
	unsigned int s;
	int ret, stop_ret;

	if (!camss || !vfe || !csid || !csiphy || !sensor || !pair ||
	    !video_entity || !owner_epoch || !pipeline_powered ||
	    !*pipeline_powered || !rtcdm_started || !*rtcdm_started ||
	    !csiphy_streaming || !*csiphy_streaming ||
	    !sensor_streaming || !*sensor_streaming || !result)
		return -EINVAL;
	if (!e008h_rear_both_complete(pair, owner_epoch))
		return -EBUSY;

	ret = csid680_e008a_rear_quiesce(csid, true);
	if (ret)
		return ret;
	result->csid_quiesced = true;

	ret = vfe680_e008a_rear_bus_stop(vfe, true);
	if (ret)
		return ret;
	result->bus_stopped = true;

	for (s = 0; s < E008H_REAR_SLOTS; s++)
		if (!e007z_rear_retireable(&pair->frame[s], owner_epoch,
					   pair->frame[s].request_generation,
					   true, true))
			return -EBUSY;

	e008k_rear_rtcdm_stop_close(camss);
	if (!e008k_rear_rtcdm_stopped(camss))
		return -EIO;
	*rtcdm_started = false;
	result->rtcdm_stopped = true;

	/* Preserve accepted E008c source stop order: CSIPHY then sensor. */
	stop_ret = e008k_rear_subdev_stream(&csiphy->subdev, false);
	if (!stop_ret)
		*csiphy_streaming = false;
	ret = e008k_rear_subdev_stream(sensor, false);
	if (!ret)
		*sensor_streaming = false;
	if (stop_ret || ret)
		return stop_ret ? stop_ret : ret;
	result->source_stopped = true;

	ret = e011i_rear_reclaim_after_stop(camss, vfe, pair, owner_epoch,
					    result);
	if (ret)
		return ret;
	result->dma_reclaimed = true;

	for (s = 0; s < E008H_REAR_SLOTS; s++) {
		ret = e007z_rear_release_ledger(
			&pair->frame[s], owner_epoch,
			pair->frame[s].request_generation, true, true);
		if (ret)
			return ret;
	}
	result->ledgers_released = true;

	e008k_rear_pipeline_pm_put(video_entity);
	*pipeline_powered = false;
	ret = e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,
				       E005Y_VFE1_OWNER_REAR,
				       owner_epoch, true);
	if (ret)
		return ret;
	result->owner_released = true;

	/* Output mappings were reclaimed while REAR ownership was exclusive. */
	return 0;
}

static void
e008k_rear_emergency_pin(struct camss *camss,
			 struct vfe_device *vfe,
			 struct csid_device *csid,
			 struct csiphy_device *csiphy,
			 struct v4l2_subdev *sensor,
			 struct e008h_rear_prime_pair *pair,
			 u64 owner_epoch,
			 bool rtcdm_started,
			 bool bus_may_be_enabled,
			 bool csid_streaming,
			 bool csiphy_streaming,
			 bool sensor_streaming)
{
	if (owner_epoch && pair)
		e008h_rear_fault_ledgers(pair, owner_epoch);
	if (csid_streaming)
		(void)csid680_e008a_rear_quiesce(csid, true);
	if (bus_may_be_enabled)
		(void)vfe680_e008a_rear_bus_stop(vfe, true);
	if (rtcdm_started)
		e008k_rear_rtcdm_stop_close(camss);
	if (csiphy_streaming)
		(void)e008k_rear_subdev_stream(&csiphy->subdev, false);
	if (sensor_streaming)
		(void)e008k_rear_subdev_stream(sensor, false);
	if (owner_epoch)
		(void)e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,
					      E005Y_VFE1_OWNER_REAR,
					      owner_epoch, false);
}

/*
 * Complete orchestration exists only as an unreachable build symbol.
 * Caller must provide already allocated/mapped E007y command buffers in req.
 */
static int __used
e008k_rear_run_unreachable(struct vfe_device *vfe,
			    struct e008k_rear_request *req,
			    struct e008k_rear_result *result)
{
	struct camss *camss;
	struct csid_device *csid;
	struct csiphy_device *csiphy;
	struct media_entity *video_entity;
	struct e008h_rear_prime_pair *pair = NULL;
	u64 owner_epoch = 0;
	u32 epoch_seq = 0, done_cursor = 0;
	unsigned long epoch_timeout, done_timeout;
	bool owner_granted = false;
	bool pair_allocated = false;
	bool hardware_touched = false;
	bool pipeline_powered = false;
	bool rtcdm_started = false;
	bool bus_may_be_enabled = false;
	bool csid_streaming = false;
	bool csiphy_streaming = false;
	bool sensor_streaming = false;
	int ret;

	if (!vfe || !req || !result || !vfe->camss)
		return -EINVAL;
	memset(result, 0, sizeof(*result));
	camss = vfe->camss;
	if (vfe != &camss->vfe[1])
		return -EINVAL;
	csid = &camss->csid[1];
	csiphy = &camss->csiphy[1];
	video_entity = &vfe->line[VFE_LINE_PIX].video_out.vdev.entity;
	epoch_timeout = req->epoch_timeout_us ?: E008K_REAR_EPOCH_TIMEOUT_US;
	done_timeout = req->done_timeout_us ?: E008K_REAR_DONE_TIMEOUT_US;

	ret = e008k_rear_validate_route(camss, req->sensor);
	if (ret)
		return ret;
	ret = e008k_rear_materialize_all(req);
	if (ret)
		return ret;

	pair = kzalloc(sizeof(*pair), GFP_KERNEL);
	if (!pair)
		return -ENOMEM;

	ret = e005y_vfe1_owner_acquire(&camss->e005y_vfe1_owner,
				       E005Y_VFE1_OWNER_REAR, true,
				       &owner_epoch);
	if (ret)
		goto out_free_pair;
	owner_granted = true;
	result->owner_epoch = owner_epoch;

	ret = e008j_rear_alloc_pair_no_mmio(vfe, pair);
	if (ret)
		goto out_release_clean_owner;
	pair_allocated = true;
	ret = e008j_rear_bind_pair_no_mmio(pair, owner_epoch,
					   req->first_request_generation);
	if (ret)
		goto out_release_clean_pair;

	ret = e008k_rear_pipeline_pm_get(video_entity);
	if (ret)
		goto out_release_clean_pair;
	pipeline_powered = true;

	ret = csid680_e008i_rear_reset(csid, owner_epoch);
	if (ret)
		goto out_clean_power;

	ret = e008k_rear_rtcdm_open_start(camss);
	if (ret)
		goto out_pin;
	rtcdm_started = true;
	hardware_touched = true;

	/* E008g/E008j exact rear prefix: packet0 precedes all BUS setup. */
	ret = e008k_rear_submit_packet(camss, &req->packet[0]);
	if (ret)
		goto out_pin;
	result->packet_submitted[0] = true;

	ret = e008j_rear_prepare_slot0_after_packet0(vfe, pair);
	if (ret)
		goto out_pin;
	bus_may_be_enabled = true; /* MMIO is now exposed; pin on all failures. */

	ret = e008h_rear_enable_slot0(vfe, pair);
	if (ret)
		goto out_pin;
	result->slot0_enabled = true;

	ret = e008k_rear_submit_packet(camss, &req->packet[1]);
	if (ret)
		goto out_pin;
	result->packet_submitted[1] = true;

	/*
	 * Packet0/1 RT-CDM wrappers own rear CSID startup programming. Only the
	 * source-locked enable is applied here; do not replay E004ns final-state
	 * prepare out of its observed order.
	 */
	ret = csid680_e008k_rear_enable(csid);
	if (ret)
		goto out_pin;
	csid_streaming = true;

	ret = e008k_rear_subdev_stream(&csiphy->subdev, true);
	if (ret)
		goto out_pin;
	csiphy_streaming = true;
	ret = e008k_rear_subdev_stream(req->sensor, true);
	if (ret)
		goto out_pin;
	sensor_streaming = true;

	/* First Epoch0 owns slot1 address retarget, then E007y packet2. */
	ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch_seq,
						  epoch_timeout);
	if (ret)
		goto out_pin;
	epoch_seq++;
	ret = e008h_rear_epoch0_retarget_slot1(vfe, pair);
	if (ret)
		goto out_pin;
	result->slot1_programmed = true;
	ret = e008k_rear_submit_packet(camss, &req->packet[2]);
	if (ret)
		goto out_pin;
	result->packet_submitted[2] = true;

	/* Second Epoch0 consumes startup packet3; BATCH4 is steady boundary. */
	ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch_seq,
						  epoch_timeout);
	if (ret)
		goto out_pin;
	epoch_seq++;
	ret = e008k_rear_submit_packet(camss, &req->packet[3]);
	if (ret)
		goto out_pin;
	result->packet_submitted[3] = true;
	result->epoch0_seq = epoch_seq;

	ret = e008k_rear_collect_done(csid, pair, owner_epoch,
				      done_timeout, &done_cursor);
	if (ret)
		goto out_pin;
	result->done_events = done_cursor;
	result->both_frames_complete = true;

	ret = e008k_rear_pair_stop_release(
		camss, vfe, csid, csiphy, req->sensor, pair, video_entity,
		owner_epoch, &pipeline_powered, &rtcdm_started,
		&csiphy_streaming, &sensor_streaming, result);
	if (ret)
		goto out_pin;

	/* The two DMA sets have been reclaimed; discard the software wrapper. */
	kfree(pair);
	return 0;

out_pin:
	if (hardware_touched || pair->slot0_preloaded_disabled ||
	    pair->enabled || csid_streaming || csiphy_streaming ||
	    sensor_streaming) {
		e008k_rear_emergency_pin(camss, vfe, csid, csiphy, req->sensor,
					 pair, owner_epoch, rtcdm_started,
					 bus_may_be_enabled || pair->enabled,
					 csid_streaming, csiphy_streaming,
					 sensor_streaming);
		/* PM ref + DMA stay pinned intentionally until reboot. */
		kfree(pair);
		return ret ? ret : -EIO;
	}
out_clean_power:
	if (pipeline_powered)
		e008k_rear_pipeline_pm_put(video_entity);
out_release_clean_pair:
	if (pair_allocated)
		e008h_rear_release_before_mmio(vfe, pair);
out_release_clean_owner:
	if (owner_granted)
		(void)e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,
					      E005Y_VFE1_OWNER_REAR,
					      owner_epoch, true);
out_free_pair:
	kfree(pair);
	return ret;
}

struct e008k_rear_runner_ops {
	int (*run_unreachable)(struct vfe_device *, struct e008k_rear_request *,
			       struct e008k_rear_result *);
};

static const struct e008k_rear_runner_ops e008k_rear_runner_recipe __used = {
	.run_unreachable = e008k_rear_run_unreachable,
};

static int __used e008k_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
