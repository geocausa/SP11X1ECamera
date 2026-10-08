/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Observe the first rear replacement boundary while the ISP is still running.
 * This is deliberately read-only. A successful observation does not retire a
 * ledger, put a DMA-BUF lease, complete a vb2 buffer, or grant live reuse.
 * The existing physical-stop reclamation remains the only release authority.
 */
#ifndef NATIVE_REAR_LIVE_OBSERVE_INC
#define NATIVE_REAR_LIVE_OBSERVE_INC

struct native_rear_live_observation {
	u32 produced, consumed, cursor, epoch_before, epoch_after;
	u16 enabled_mask, programmed_mask, consumed_mask;
	bool owner_current, old_complete, next_complete, receipts_complete;
};

static bool
native_rear_live_owner_matches(struct camss *camss, u64 epoch)
{
	struct e005y_vfe1_owner *o = &camss->e005y_vfe1_owner;
	unsigned long flags;
	bool match;

	spin_lock_irqsave(&o->lock, flags);
	match = o->active_owner == E005Y_VFE1_OWNER_REAR &&
		o->active_epoch == epoch && !o->unsafe_stop_pinned;
	spin_unlock_irqrestore(&o->lock, flags);
	return match;
}

static int
native_rear_live_replacement_read(struct vfe_device *vfe,
				 struct csid_device *csid,
				 const struct e008h_rear_prime_pair *pair,
				 const struct e008k_rear_result *result,
				 u32 cursor,
				 struct native_rear_live_observation *out)
{
	struct camss *camss;
	unsigned int i, j;
	u64 owner;

	if (!out)
		return -EINVAL;
	memset(out, 0, sizeof(*out));
	out->cursor = cursor;
	if (!vfe || !vfe->camss || !csid || !pair || !result)
		return -EINVAL;
	camss = vfe->camss;
	owner = result->owner_epoch;
	if (vfe != &camss->vfe[1] || csid != &camss->csid[1] ||
	    !vfe680_e004nt_rear_4k_target(vfe) ||
	    !csid680_e008k_rear_mode0(csid) || !csid->irq || !owner)
		return -EINVAL;
	/* This check must never be mistaken for a post-stop observation. */
	if (result->csid_quiesced || result->bus_stopped ||
	    result->rtcdm_stopped || result->source_stopped ||
	    result->dma_reclaimed || result->owner_released)
		return -ESHUTDOWN;
	if (!pair->allocated || !pair->enabled || !pair->ledgers_bound ||
	    !pair->programmed[0] || !pair->programmed[1] || pair->faulted)
		return -EPROTO;
	out->owner_current = native_rear_live_owner_matches(camss, owner);
	if (!out->owner_current ||
	    READ_ONCE(csid->e008i_rear_owner_epoch) != owner)
		return -ESTALE;
	for (i = 0; i < E008H_REAR_SLOTS; i++) {
		const struct e007z_rear_frame *f = &pair->frame[i];

		if (!f->active || f->faulted || f->owner_epoch != owner ||
		    !f->request_generation || f->pending)
			return -EBUSY;
		for (j = 0; j < E007Z_REAR_WMS; j++) {
			const struct e007z_rear_wm_desc *d = &e007z_rear_wm_descs[j];
			const struct e007z_rear_slot *s = &f->slot[j];
			struct e007z_rear_binding binding = {
				.wm = d->wm,
				.owned_base_iova = s->owned_base_iova,
				.owned_bytes = s->owned_bytes,
				.programmed_image_iova = s->programmed_image_iova,
			};
			int ai = e008h_rear_addr_index(&pair->addr[i], d->wm);

			if (ai < 0 || e007z_rear_validate_binding(d, &binding) ||
			    pair->addr[i].image[ai] != s->programmed_image_iova)
				return -EPROTO;
		}
	}
	if (pair->frame[0].request_generation == U64_MAX ||
	    pair->frame[1].request_generation !=
	    pair->frame[0].request_generation + 1)
		return -ESTALE;
	out->old_complete = true;
	out->next_complete = true;
	/* Both generations must have completely distinct owned DMA spans. */
	for (i = 0; i < E007Z_REAR_WMS; i++)
		for (j = 0; j < E007Z_REAR_WMS; j++)
			if (e007z_rear_spans_overlap(
				    pair->frame[0].slot[i].owned_base_iova,
				    pair->frame[0].slot[i].owned_bytes,
				    pair->frame[1].slot[j].owned_base_iova,
				    pair->frame[1].slot[j].owned_bytes))
				return -EADDRINUSE;
	for (i = 0; i < E007Y_STARTUP_PACKETS; i++)
		if (!result->packet_submitted[i])
			return -EINPROGRESS;
	/* Submit success follows synchronous FIFO BL_DONE for every BL. */
	out->receipts_complete = true;
	if (csid680_e008i_rear_done_overflow(csid) ||
	    csid680_e008i_rear_latch_errors(csid))
		return -EOVERFLOW;
	/* Wait only for an executing ISR; do not disable or acknowledge IRQs. */
	synchronize_irq(csid->irq);
	out->produced = csid680_e008i_rear_done_count(csid);
	out->consumed = READ_ONCE(csid->native_rear_done_consumed);
	out->epoch_before = csid680_e008i_rear_epoch0_seq(csid);
	if (!out->produced || out->produced == U32_MAX ||
	    out->consumed != cursor || out->produced != cursor ||
	    out->epoch_before < 2 || out->epoch_before == U32_MAX)
		return -EAGAIN;

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct e007z_rear_wm_desc *d = &e007z_rear_wm_descs[i];
		const struct e007z_rear_slot *s = &pair->frame[1].slot[i];
		const struct vfe680_e004nu_rear_wm_static *c;
		struct e007z_rear_binding binding;
		void __iomem *cfg;
		u32 cfg_now;
		int ai;

		c = e008d_rear_contract_for_wm(d->wm);
		ai = e008h_rear_addr_index(&pair->addr[1], d->wm);
		if (!c || ai < 0)
			return -EINVAL;
		binding = (struct e007z_rear_binding) {
			.wm = d->wm,
			.owned_base_iova = s->owned_base_iova,
			.owned_bytes = s->owned_bytes,
			.programmed_image_iova = s->programmed_image_iova,
		};
		if (e007z_rear_validate_binding(d, &binding) ||
		    pair->addr[1].image[ai] != s->programmed_image_iova)
			return -EPROTO;
		cfg = vfe680_x1e_bus_reg(vfe, d->wm, 0);
		cfg_now = readl_relaxed(cfg + VFE680_X1E_BUS_CFG);
		if (!(cfg_now & VFE_BUS_WRITE_CLIENT_CFG_EN) ||
		    (cfg_now & ~VFE_BUS_WRITE_CLIENT_CFG_EN) !=
		    (c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN))
			return -EIO;
		out->enabled_mask |= BIT(i);
		if (readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR) !=
		    s->programmed_image_iova)
			return -EIO;
		out->programmed_mask |= BIT(i);
		if (readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS0) !=
		    s->programmed_image_iova)
			return -EIO;
		out->consumed_mask |= BIT(i);
	}
	out->epoch_after = csid680_e008i_rear_epoch0_seq(csid);
	if (!native_rear_live_owner_matches(camss, owner) ||
	    READ_ONCE(csid->e008i_rear_owner_epoch) != owner)
		return -ESTALE;
	if (csid680_e008i_rear_done_overflow(csid) ||
	    csid680_e008i_rear_latch_errors(csid))
		return -EOVERFLOW;
	if (out->epoch_after != out->epoch_before ||
	    csid680_e008i_rear_done_count(csid) != out->produced ||
	    READ_ONCE(csid->native_rear_done_consumed) != out->consumed)
		return -EAGAIN;
	return 0;
}

static void
native_rear_live_replacement_observe(struct vfe_device *vfe,
				    struct csid_device *csid,
				    const struct e008h_rear_prime_pair *pair,
				    const struct e008k_rear_result *result,
				    u32 cursor)
{
	struct native_rear_live_observation out;
	int ret = native_rear_live_replacement_read(vfe, csid, pair, result,
						    cursor, &out);

	dev_info(vfe->camss->dev,
		 "NATIVE_REAR_LIVE_REPLACEMENT ret=%d owner=%u old_complete=%u next_complete=%u receipts=%u enabled=%u programmed=%u consumed_addr=%u published=%u consumed=%u cursor=%u epoch_before=%u epoch_after=%u live_release=0\n",
		 ret, out.owner_current, out.old_complete, out.next_complete,
		 out.receipts_complete, out.enabled_mask, out.programmed_mask,
		 out.consumed_mask, out.produced, out.consumed, out.cursor,
		 out.epoch_before, out.epoch_after);
}
#endif
