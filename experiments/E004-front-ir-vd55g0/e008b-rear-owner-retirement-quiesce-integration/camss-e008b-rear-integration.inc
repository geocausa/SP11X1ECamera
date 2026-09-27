/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008b: build-only composition of:
 *   - E005y shared VFE1 FRONT/REAR owner epoch,
 *   - E007z ten-WM exact consumed-IOVA retirement ledger,
 *   - E008a CSID1 quiesce + VFE1 BUS-stop/IRQ-drain helpers.
 *
 * No runtime call site is installed.  No DMA mapping is released or reused,
 * and RT-CDM stop/close remains a separate later gate.
 */
#ifndef VFE680_E008B_REAR_OWNER_RETIREMENT_QUIESCE_INC
#define VFE680_E008B_REAR_OWNER_RETIREMENT_QUIESCE_INC

int csid680_e008a_rear_quiesce(struct csid_device *csid,
			       bool exact_rear_owner);
int vfe680_e008a_rear_bus_stop(struct vfe_device *vfe,
			       bool exact_rear_owner);

struct e008b_rear_irq_snapshot {
	u32 csid_buf_done_status;
	u16 valid_consumed_mask;
	u32 last_consumed_iova[E007Z_REAR_WMS];
};

struct e008b_rear_quiesce_proof {
	u64 owner_epoch;
	u64 request_generation;
	bool csid_quiesced;
	bool vfe_bus_stopped;
	bool ledger_retireable;
};

static bool
e008b_rear_owner_matches(struct e005y_vfe1_owner *owner, u64 owner_epoch)
{
	unsigned long flags;
	bool ok;

	if (!owner || !owner_epoch)
		return false;

	spin_lock_irqsave(&owner->lock, flags);
	ok = !owner->unsafe_stop_pinned &&
	     owner->active_owner == E005Y_VFE1_OWNER_REAR &&
	     owner->active_epoch == owner_epoch;
	spin_unlock_irqrestore(&owner->lock, flags);
	return ok;
}

static void
e008b_rear_pin_fault(struct e005y_vfe1_owner *owner,
		     struct e007z_rear_frame *frame,
		     u64 owner_epoch, u64 request_generation)
{
	if (frame && frame->active &&
	    frame->owner_epoch == owner_epoch &&
	    frame->request_generation == request_generation)
		(void)e007z_rear_mark_fault(frame, owner_epoch,
					    request_generation);

	/*
	 * A failed hardware teardown must not relinquish the shared VFE1 owner.
	 * E005y's false-safe release path pins ownership until reboot.
	 */
	if (owner && owner_epoch)
		(void)e005y_vfe1_owner_release(owner, E005Y_VFE1_OWNER_REAR,
					      owner_epoch, false);
}

/*
 * Consume one caller-owned snapshot that was collected from the already
 * latched/ACKed CSID BUF_DONE path.  This function performs no MMIO or IRQ
 * acknowledgement.
 *
 * Every still-pending WM whose source-pinned completion-group bit is asserted
 * must have its own last-consumed sample.  Shared group bits never imply that
 * all members completed.
 */
static int __used
e008b_rear_observe_snapshot(struct e005y_vfe1_owner *owner,
			    struct e007z_rear_frame *frame,
			    bool exact_rear_route_now,
			    u64 request_generation,
			    const struct e008b_rear_irq_snapshot *snapshot)
{
	u64 owner_epoch = 0;
	u64 owner_epoch_after = 0;
	u16 pending_before;
	bool wm16_completed_now = false;
	u32 wm16_consumed = 0;
	unsigned int i;
	int ret;

	if (!owner || !frame || !snapshot || !exact_rear_route_now ||
	    !request_generation || !frame->active || frame->faulted)
		return -EINVAL;
	if (snapshot->valid_consumed_mask & ~E007Z_REAR_ALL_DONE)
		return -EINVAL;

	if (!e005y_vfe1_rear_sample_begin(owner, exact_rear_route_now,
					  &owner_epoch))
		return -ESTALE;
	if (frame->owner_epoch != owner_epoch ||
	    frame->request_generation != request_generation) {
		(void)e007z_rear_mark_fault(frame, frame->owner_epoch,
					    frame->request_generation);
		return -ESTALE;
	}

	pending_before = frame->pending;
	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct e007z_rear_wm_desc *desc = &e007z_rear_wm_descs[i];

		if (!(pending_before & BIT(i)))
			continue;
		if (!(snapshot->csid_buf_done_status & BIT(desc->comp_group)))
			continue;
		if (!(snapshot->valid_consumed_mask & BIT(i))) {
			e008b_rear_pin_fault(owner, frame, owner_epoch,
					     request_generation);
			return -EIO;
		}

		ret = e007z_rear_observe(frame, owner_epoch,
					request_generation,
					snapshot->csid_buf_done_status,
					desc->wm,
					snapshot->last_consumed_iova[i]);
		if (ret) {
			e008b_rear_pin_fault(owner, frame, owner_epoch,
					     request_generation);
			return ret;
		}

		if (desc->wm == 16) {
			wm16_completed_now = true;
			wm16_consumed = snapshot->last_consumed_iova[i];
		}
	}

	/*
	 * Preserve E005y BF/WM16 accounting only after E007z accepted the exact
	 * programmed image IOVA for WM16.  A duplicate later bit7 cannot count
	 * again because wm16_completed_now is true only if WM16 was pending when
	 * this snapshot began.
	 */
	if (wm16_completed_now) {
		enum e005y_bf_observation obs;

		obs = e005y_vfe1_observe_bf(owner, false, exact_rear_route_now,
					   snapshot->csid_buf_done_status,
					   owner_epoch, true, wm16_consumed);
		if (obs != E005Y_BF_REAR) {
			e008b_rear_pin_fault(owner, frame, owner_epoch,
					     request_generation);
			return -ESTALE;
		}
	}

	if (!e005y_vfe1_rear_sample_begin(owner, exact_rear_route_now,
					  &owner_epoch_after) ||
	    owner_epoch_after != owner_epoch) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -ESTALE;
	}

	return 0;
}

/*
 * Prove the E007z independent teardown predicates in the same REAR ownership
 * epoch.  This intentionally stops at "retireable": it does NOT release the
 * E007z ledger or E005y owner because RT-CDM stop/close and complete outer
 * resource teardown remain separate gates.
 *
 * Source-accepted normal stop prefix is CSID1 -> BUS/IFE -> RT-CDM, so E008b
 * performs E008a CSID quiescence before E008a VFE BUS stop.
 */
static int __used
e008b_rear_quiesce_and_prove(struct e005y_vfe1_owner *owner,
			     struct e007z_rear_frame *frame,
			     struct csid_device *csid,
			     struct vfe_device *vfe,
			     bool exact_rear_route_now,
			     u64 request_generation,
			     struct e008b_rear_quiesce_proof *proof)
{
	u64 owner_epoch = 0;
	int ret;

	if (!owner || !frame || !csid || !vfe || !proof ||
	    !exact_rear_route_now || !request_generation)
		return -EINVAL;
	memset(proof, 0, sizeof(*proof));

	if (!e005y_vfe1_rear_sample_begin(owner, exact_rear_route_now,
					  &owner_epoch))
		return -ESTALE;
	if (!frame->active || frame->faulted || frame->pending ||
	    frame->owner_epoch != owner_epoch ||
	    frame->request_generation != request_generation)
		return -EAGAIN;

	proof->owner_epoch = owner_epoch;
	proof->request_generation = request_generation;

	ret = csid680_e008a_rear_quiesce(csid, true);
	if (ret) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return ret;
	}
	proof->csid_quiesced = true;

	if (!e008b_rear_owner_matches(owner, owner_epoch)) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -ESTALE;
	}

	ret = vfe680_e008a_rear_bus_stop(vfe, true);
	if (ret) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return ret;
	}
	proof->vfe_bus_stopped = true;

	if (!e008b_rear_owner_matches(owner, owner_epoch)) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -ESTALE;
	}

	proof->ledger_retireable =
		e007z_rear_retireable(frame, owner_epoch, request_generation,
				      true, true);
	if (!proof->ledger_retireable) {
		e008b_rear_pin_fault(owner, frame, owner_epoch,
				     request_generation);
		return -EBUSY;
	}

	return 0;
}

static int __used e008b_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

struct e008b_rear_integration_ops {
	int (*observe_snapshot)(struct e005y_vfe1_owner *owner,
				struct e007z_rear_frame *frame,
				bool exact_rear_route_now,
				u64 request_generation,
				const struct e008b_rear_irq_snapshot *snapshot);
	int (*quiesce_and_prove)(struct e005y_vfe1_owner *owner,
				 struct e007z_rear_frame *frame,
				 struct csid_device *csid,
				 struct vfe_device *vfe,
				 bool exact_rear_route_now,
				 u64 request_generation,
				 struct e008b_rear_quiesce_proof *proof);
};

static const struct e008b_rear_integration_ops
e008b_rear_integration_recipe __used = {
	.observe_snapshot = e008b_rear_observe_snapshot,
	.quiesce_and_prove = e008b_rear_quiesce_and_prove,
};

#endif /* VFE680_E008B_REAR_OWNER_RETIREMENT_QUIESCE_INC */
