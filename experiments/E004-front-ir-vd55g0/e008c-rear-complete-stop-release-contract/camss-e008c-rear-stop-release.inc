/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008c: build-only complete rear stop/release contract.
 *
 * Composition:
 *   E008b: owner + exact consumed IOVA + CSID/VFE quiescence
 *   accepted RT-CDM1 stop/close
 *   accepted V4L2 subdevice stream-off tail
 *   E007z ledger release
 *   pipeline PM put
 *   E005y safe owner release
 *
 * No runtime call site is installed by this checkpoint.
 */
#ifndef VFE680_E008C_REAR_COMPLETE_STOP_RELEASE_INC
#define VFE680_E008C_REAR_COMPLETE_STOP_RELEASE_INC

struct e008c_rear_stop_proof {
	u64 owner_epoch;
	u64 request_generation;
	bool csid_quiesced;
	bool vfe_bus_stopped;
	bool ledger_retireable;
	bool rtcdm_stopped;
	bool csiphy_stopped;
	bool sensor_stopped;
	bool ledger_released;
	bool pipeline_power_released;
	bool owner_released;
};

static bool
e008c_rear_rtcdm_stopped(struct camss *camss)
{
	struct camss_rtcdm *rt;
	bool stopped;

	if (!camss)
		return false;
	rt = &camss->rtcdm1;
	if (!rt->present || !rt->base)
		return false;

	mutex_lock(&rt->lock);
	stopped = !READ_ONCE(rt->irq_armed) &&
		  readl(rt->base + CAMSS_RTCDM_IRQ0_MASK) == 0;
	mutex_unlock(&rt->lock);
	return stopped;
}

/*
 * Complete only the already source-locked successful rear stop path.
 *
 * The post-frame path requires every hardware/resource stage to have been
 * active. Failure at any stage leaves the shared owner pinned and the ledger
 * unreleased, matching the accepted front fail-closed policy.
 */
static int __used
e008c_rear_complete_stop_release(struct camss *camss,
				 struct e005y_vfe1_owner *owner,
				 struct e007z_rear_frame *frame,
				 struct csid_device *csid,
				 struct vfe_device *vfe,
				 struct v4l2_subdev *csiphy_sd,
				 struct v4l2_subdev *sensor_sd,
				 struct media_entity *video_entity,
				 bool exact_rear_route_now,
				 u64 request_generation,
				 bool rtcdm_started,
				 bool csiphy_streaming,
				 bool sensor_streaming,
				 bool pipeline_powered,
				 struct e008c_rear_stop_proof *proof)
{
	struct e008b_rear_quiesce_proof q = { 0 };
	u64 owner_epoch;
	int first_err = 0;
	int ret;

	if (!camss || !owner || !frame || !csid || !vfe || !csiphy_sd ||
	    !sensor_sd || !video_entity || !proof || !exact_rear_route_now ||
	    !request_generation || !rtcdm_started || !csiphy_streaming ||
	    !sensor_streaming || !pipeline_powered)
		return -EINVAL;
	memset(proof, 0, sizeof(*proof));

	/* Source-locked successful stop prefix: CSID -> BUS/IFE. */
	ret = e008b_rear_quiesce_and_prove(owner, frame, csid, vfe,
					   exact_rear_route_now,
					   request_generation, &q);
	if (ret)
		return ret;

	owner_epoch = q.owner_epoch;
	proof->owner_epoch = owner_epoch;
	proof->request_generation = request_generation;
	proof->csid_quiesced = q.csid_quiesced;
	proof->vfe_bus_stopped = q.vfe_bus_stopped;
	proof->ledger_retireable = q.ledger_retireable;

	/*
	 * CDM is third in the source-locked stop prefix. The accepted helper masks
	 * RT-CDM IRQ0 and closes Linux IRQ ownership. Verify both before proceeding.
	 */
	camss_x1e_pix_rtcdm_stop_close(camss);
	if (!e008c_rear_rtcdm_stopped(camss)) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -EIO;
	}
	proof->rtcdm_stopped = true;

	/*
	 * Accepted native front tail: CSIPHY then sensor. Attempt both so a first
	 * failure does not prevent the other producer from being asked to stop.
	 * Any failure still pins ownership and forbids ledger/power release.
	 */
	ret = camss_x1e_pix_runner_stream(csiphy_sd, false);
	if (ret)
		first_err = ret;
	else
		proof->csiphy_stopped = true;

	ret = camss_x1e_pix_runner_stream(sensor_sd, false);
	if (ret && !first_err)
		first_err = ret;
	else if (!ret)
		proof->sensor_stopped = true;

	if (first_err) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return first_err;
	}

	if (!e008b_rear_owner_matches(owner, owner_epoch)) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -ESTALE;
	}

	/*
	 * Only now may the evidence ledger be cleared. This still does not free or
	 * unmap any DMA object; the eventual runtime owner of those mappings must
	 * use this contract as its prerequisite.
	 */
	ret = e007z_rear_release_ledger(frame, owner_epoch, request_generation,
					true, true);
	if (ret) {
		(void)e005y_vfe1_owner_release(owner, E005Y_VFE1_OWNER_REAR,
					      owner_epoch, false);
		return ret;
	}
	proof->ledger_released = true;

	/*
	 * Match the accepted front success tail: release media-pipeline power only
	 * after hardware producers and command processing are stopped.
	 */
	v4l2_pipeline_pm_put(video_entity);
	proof->pipeline_power_released = true;

	ret = e005y_vfe1_owner_release(owner, E005Y_VFE1_OWNER_REAR,
				       owner_epoch, true);
	if (ret)
		return ret;
	proof->owner_released = true;

	return 0;
}

static int __used e008c_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

struct e008c_rear_stop_ops {
	int (*complete_stop_release)(struct camss *camss,
				     struct e005y_vfe1_owner *owner,
				     struct e007z_rear_frame *frame,
				     struct csid_device *csid,
				     struct vfe_device *vfe,
				     struct v4l2_subdev *csiphy_sd,
				     struct v4l2_subdev *sensor_sd,
				     struct media_entity *video_entity,
				     bool exact_rear_route_now,
				     u64 request_generation,
				     bool rtcdm_started,
				     bool csiphy_streaming,
				     bool sensor_streaming,
				     bool pipeline_powered,
				     struct e008c_rear_stop_proof *proof);
};

static const struct e008c_rear_stop_ops e008c_rear_stop_recipe __used = {
	.complete_stop_release = e008c_rear_complete_stop_release,
};

#endif /* VFE680_E008C_REAR_COMPLETE_STOP_RELEASE_INC */
