/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E007z: build-only rear VFE680 ten-WM Linux ownership / consumed-IOVA
 * retirement ledger. No MMIO, IRQ ACK, DMA allocation/free, stream start,
 * RT-CDM submission, requeue, vb2 completion or hardware activation.
 *
 * Physical completion group numbers are source-pinned to VFE680. A group
 * bit is necessary but never sufficient: retirement of each WM additionally
 * requires exact ADDR_STATUS0 / last-consumed identity against the Linux-owned
 * programmed image IOVA for the same owner epoch and request generation.
 */
#ifndef VFE680_E007Z_REAR_RETIREMENT_INC
#define VFE680_E007Z_REAR_RETIREMENT_INC

#define E007Z_REAR_WMS 10U
#define E007Z_REAR_ALL_DONE ((1U << E007Z_REAR_WMS) - 1U)

struct e007z_rear_wm_desc {
	u8 wm;
	u8 comp_group;
	u32 required_bytes;
	u32 image_offset;
};

static const struct e007z_rear_wm_desc
e007z_rear_wm_descs[E007Z_REAR_WMS] = {
	{ .wm = 0,  .comp_group = 0, .required_bytes = 0x00a9d000U, .image_offset = 0x00011000U },
	{ .wm = 1,  .comp_group = 0, .required_bytes = 0x00559000U, .image_offset = 0x00009000U },
	{ .wm = 2,  .comp_group = 0, .required_bytes = 0x0010e000U, .image_offset = 0x00000000U },
	{ .wm = 3,  .comp_group = 0, .required_bytes = 0x00018000U, .image_offset = 0x00000000U },
	{ .wm = 11, .comp_group = 4, .required_bytes = 0x000a0000U, .image_offset = 0x00000000U },
	{ .wm = 12, .comp_group = 4, .required_bytes = 0x00001800U, .image_offset = 0x00000000U },
	{ .wm = 13, .comp_group = 5, .required_bytes = 0x00048000U, .image_offset = 0x00000000U },
	{ .wm = 14, .comp_group = 6, .required_bytes = 0x00151800U, .image_offset = 0x00000000U },
	{ .wm = 16, .comp_group = 7, .required_bytes = 0x00002d00U, .image_offset = 0x00000000U },
	{ .wm = 18, .comp_group = 9, .required_bytes = 0x00010000U, .image_offset = 0x00000000U },
};
static_assert(ARRAY_SIZE(e007z_rear_wm_descs) == E007Z_REAR_WMS);

struct e007z_rear_binding {
	u8 wm;
	u32 owned_base_iova;
	u32 owned_bytes;
	u32 programmed_image_iova;
};

struct e007z_rear_slot {
	u32 owned_base_iova;
	u32 owned_bytes;
	u32 programmed_image_iova;
};

struct e007z_rear_frame {
	u64 owner_epoch;
	u64 request_generation;
	struct e007z_rear_slot slot[E007Z_REAR_WMS];
	u16 pending;
	bool active;
	bool faulted;
};

static int e007z_rear_index(u8 wm)
{
	unsigned int i;

	for (i = 0; i < E007Z_REAR_WMS; i++)
		if (e007z_rear_wm_descs[i].wm == wm)
			return i;
	return -ENOENT;
}

static bool
e007z_rear_spans_overlap(u32 a, u32 asz, u32 b, u32 bsz)
{
	u64 ae = (u64)a + asz;
	u64 be = (u64)b + bsz;

	return (u64)a < be && (u64)b < ae;
}

static int
e007z_rear_validate_binding(const struct e007z_rear_wm_desc *desc,
			    const struct e007z_rear_binding *binding)
{
	u64 end;
	u64 expected_image;

	if (!desc || !binding || binding->wm != desc->wm ||
	    !binding->owned_base_iova || !binding->owned_bytes ||
	    !binding->programmed_image_iova)
		return -EINVAL;
	if ((binding->owned_base_iova | binding->programmed_image_iova) & 3U)
		return -EINVAL;
	if (binding->owned_bytes < desc->required_bytes)
		return -ENOSPC;

	end = (u64)binding->owned_base_iova + binding->owned_bytes;
	if (end > 0x100000000ULL)
		return -ERANGE;

	expected_image = (u64)binding->owned_base_iova + desc->image_offset;
	if (expected_image >= end ||
	    binding->programmed_image_iova != (u32)expected_image)
		return -ERANGE;

	return 0;
}

static int __used
e007z_rear_bind(struct e007z_rear_frame *frame,
		u64 owner_epoch, u64 request_generation,
		const struct e007z_rear_binding binding[E007Z_REAR_WMS])
{
	u16 seen = 0;
	unsigned int i, j;

	if (!frame || !binding || !owner_epoch || !request_generation ||
	    frame->active || frame->pending)
		return -EINVAL;

	memset(frame, 0, sizeof(*frame));
	for (i = 0; i < E007Z_REAR_WMS; i++) {
		int idx = e007z_rear_index(binding[i].wm);
		int ret;

		if (idx < 0) {
			memset(frame, 0, sizeof(*frame));
			return idx;
		}
		if (seen & BIT(idx)) {
			memset(frame, 0, sizeof(*frame));
			return -EEXIST;
		}
		ret = e007z_rear_validate_binding(&e007z_rear_wm_descs[idx],
						 &binding[i]);
		if (ret) {
			memset(frame, 0, sizeof(*frame));
			return ret;
		}
		frame->slot[idx].owned_base_iova = binding[i].owned_base_iova;
		frame->slot[idx].owned_bytes = binding[i].owned_bytes;
		frame->slot[idx].programmed_image_iova =
			binding[i].programmed_image_iova;
		seen |= BIT(idx);
	}

	if (seen != E007Z_REAR_ALL_DONE) {
		memset(frame, 0, sizeof(*frame));
		return -EINVAL;
	}

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		for (j = i + 1; j < E007Z_REAR_WMS; j++) {
			if (e007z_rear_spans_overlap(
				    frame->slot[i].owned_base_iova,
				    frame->slot[i].owned_bytes,
				    frame->slot[j].owned_base_iova,
				    frame->slot[j].owned_bytes)) {
				memset(frame, 0, sizeof(*frame));
				return -EADDRINUSE;
			}
		}
	}

	frame->owner_epoch = owner_epoch;
	frame->request_generation = request_generation;
	frame->pending = E007Z_REAR_ALL_DONE;
	frame->active = true;
	return 0;
}

/*
 * csid_buf_done_status is the already-latched/ACKed external CSID680
 * BUF_DONE status. This function does not read or acknowledge hardware.
 * Shared completion bits (group0 and group4) are deliberately handled one
 * WM at a time: each WM must independently match its own consumed IOVA.
 */
static int __used
e007z_rear_observe(struct e007z_rear_frame *frame,
		   u64 owner_epoch, u64 request_generation,
		   u32 csid_buf_done_status, u8 wm,
		   u32 last_consumed_iova)
{
	const struct e007z_rear_wm_desc *desc;
	int idx;

	if (!frame || !frame->active || frame->faulted)
		return -EINVAL;
	if (frame->owner_epoch != owner_epoch ||
	    frame->request_generation != request_generation)
		return -ESTALE;

	idx = e007z_rear_index(wm);
	if (idx < 0)
		return idx;
	desc = &e007z_rear_wm_descs[idx];

	if (!(csid_buf_done_status & BIT(desc->comp_group)))
		return -EAGAIN;
	if (!(frame->pending & BIT(idx)))
		return -EALREADY;
	if (!last_consumed_iova ||
	    last_consumed_iova != frame->slot[idx].programmed_image_iova) {
		frame->faulted = true;
		return -EIO;
	}

	frame->pending &= ~BIT(idx);
	return 0;
}

static int __used
e007z_rear_mark_fault(struct e007z_rear_frame *frame,
		      u64 owner_epoch, u64 request_generation)
{
	if (!frame || !frame->active)
		return -EINVAL;
	if (frame->owner_epoch != owner_epoch ||
	    frame->request_generation != request_generation)
		return -ESTALE;
	frame->faulted = true;
	return 0;
}

/*
 * "Retireable" means only that ledger evidence is complete. The caller must
 * independently prove BUS stop and IRQ drain before it may release or reuse
 * any DMA mapping. No freeing/requeueing happens here.
 */
static bool __used
e007z_rear_retireable(const struct e007z_rear_frame *frame,
		      u64 owner_epoch, u64 request_generation,
		      bool independently_verified_bus_stopped,
		      bool independently_verified_irqs_drained)
{
	return frame && frame->active && !frame->faulted &&
	       frame->owner_epoch == owner_epoch &&
	       frame->request_generation == request_generation &&
	       !frame->pending &&
	       independently_verified_bus_stopped &&
	       independently_verified_irqs_drained;
}

static int __used
e007z_rear_release_ledger(struct e007z_rear_frame *frame,
			  u64 owner_epoch, u64 request_generation,
			  bool independently_verified_bus_stopped,
			  bool independently_verified_irqs_drained)
{
	if (!e007z_rear_retireable(frame, owner_epoch, request_generation,
				   independently_verified_bus_stopped,
				   independently_verified_irqs_drained))
		return -EBUSY;
	memset(frame, 0, sizeof(*frame));
	return 0;
}

static int __used e007z_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

struct e007z_rear_retirement_ops {
	int (*bind)(struct e007z_rear_frame *frame,
		    u64 owner_epoch, u64 request_generation,
		    const struct e007z_rear_binding binding[E007Z_REAR_WMS]);
	int (*observe)(struct e007z_rear_frame *frame,
		       u64 owner_epoch, u64 request_generation,
		       u32 csid_buf_done_status, u8 wm,
		       u32 last_consumed_iova);
	bool (*retireable)(const struct e007z_rear_frame *frame,
			   u64 owner_epoch, u64 request_generation,
			   bool independently_verified_bus_stopped,
			   bool independently_verified_irqs_drained);
};

static const struct e007z_rear_retirement_ops
e007z_rear_retirement_recipe __used = {
	.bind = e007z_rear_bind,
	.observe = e007z_rear_observe,
	.retireable = e007z_rear_retireable,
};

#endif /* VFE680_E007Z_REAR_RETIREMENT_INC */
