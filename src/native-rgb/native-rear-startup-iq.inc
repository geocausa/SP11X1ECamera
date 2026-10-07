/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Rear startup BF finalization and explicit calculated tuning input.
 * Caller/IPA owns AF rectangles and CST/BPC-ABF tuning calculations.
 * Kernel admits integers only; no captured coordinates, float policy or MMIO.
 * Sleepable, transactional, four-packet input. Does not seal/authorize hardware.
 */
#ifndef NATIVE_REAR_STARTUP_IQ_INC
#define NATIVE_REAR_STARTUP_IQ_INC

struct native_rear_af_rect {
	u16 x, y, width, height;
};

struct native_rear_packet_iq_input {
	u64 request_id;
	u8 phase;
	u16 active_width, active_height;
	struct native_rear_af_rect af;
	struct e006r_cst12_state cst;
	struct e007a_bpcabf411_calc_state bpcabf;
	bool controls_valid;
};

struct native_rear_startup_iq_input {
	struct native_rear_packet_iq_input packet[E007Y_STARTUP_PACKETS];
};

struct native_rear_iq_work {
	struct native_rear_startup_iq_input input;
	struct e008o_rear_packet_semantics pending[E007Y_STARTUP_PACKETS];
};

/* Interior, non-stripe source slice E009C/E008X; reject unsupported clamps.
 * AF -> even BAF rectangle -> 5x5 cells -> BF boundary adjustment.
 * Division by 5 equals the source float32 multiply for these bounded extents.
 */
static int native_rear_finalize_bf_roi(struct e007e_bf_dmi_state *d,
				      const struct native_rear_af_rect *af,
				      u32 active_width, u32 active_height)
{
	u32 x, y, width, height, cell_w, cell_h;
	unsigned int row, col;

	if (!d || !af || d->roi_count != E007E_BF_ROI_COUNT ||
	    !d->gamma_valid || !af->width || !af->height ||
	    active_width != 4064 || active_height != 2286)
		return -EINVAL;
	if ((u32)af->x + af->width > active_width ||
	    (u32)af->y + af->height > active_height)
		return -ERANGE;
	x = af->x & ~1U;
	y = af->y & ~1U;
	width = af->width & ~1U;
	height = (af->height & ~1U) + 16U;
	if (x < 76 || y < 64 || x + width > active_width - 12 ||
	    y + height > active_height)
		return -ERANGE;
	cell_w = width / 5U;
	cell_h = height / 5U;
	if (cell_w < 6 || cell_h < 8)
		return -ERANGE;
	/* Validate all produced records before touching the destination. */
	for (row = 0; row < 5; row++)
		for (col = 0; col < 5; col++) {
			u32 left = x + col * cell_w;
			u32 top = (y + row * cell_h) & ~1U;
			u32 w = (cell_w & ~1U) - 1U;
			u32 h = (cell_h & ~1U) - 1U;

			if (left + w + 1 > active_width ||
			    top + h + 1 > active_height ||
			    left > 0x1fff || top > 0x3fff ||
			    w > 0x0fff || h > 0x1fff)
				return -ERANGE;
		}
	for (row = 0; row < 5; row++)
		for (col = 0; col < 5; col++) {
			struct e007e_bf_roi *r = &d->roi[row * 5 + col];

			r->left = x + col * cell_w;
			r->top = (y + row * cell_h) & ~1U;
			r->width = (cell_w & ~1U) - 1U;
			r->height = (cell_h & ~1U) - 1U;
		}
	return 0;
}

static int __maybe_unused
native_rear_bind_startup_iq(
	struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct native_rear_startup_iq_input *input)
{
	struct native_rear_iq_work *work;
	unsigned int p;
	int ret = 0;

	if (!base || !input)
		return -EINVAL;
	work = kzalloc(sizeof(*work), GFP_KERNEL);
	if (!work)
		return -ENOMEM;
	work->input = *input;
	memcpy(work->pending, base, sizeof(work->pending));
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		const struct native_rear_packet_iq_input *i = &work->input.packet[p];
		struct e008o_rear_packet_semantics *candidate = &work->pending[p];
		struct e007e_bf_dmi_state *bf = e008t_rear_bf_dmi(&candidate->dmi);

		if (candidate->ready || i->phase != p || i->request_id < 4 ||
		    i->request_id != candidate->request_id ||
		    candidate->regs.scalar.epoch_kind != E006Z_EPOCH_STARTUP ||
		    candidate->regs.scalar.startup_phase != p ||
		    candidate->regs.scalar.request_id != i->request_id) {
			ret = -EPROTO;
			goto out;
		}
		if (!i->controls_valid) {
			ret = -EAGAIN;
			goto out;
		}
		if (i->active_width != 4064 || i->active_height != 2286 ||
		    candidate->regs.mnds.input_width != i->active_width ||
		    candidate->regs.mnds.input_height != i->active_height) {
			ret = -ERANGE;
			goto out;
		}
		ret = e006r_cst12_validate(&i->cst);
		if (ret)
			goto out;
		ret = e007a_bpcabf411_validate(&i->bpcabf);
		if (ret)
			goto out;
		ret = e008t_rear_seed_packet_bf(candidate, p, i->active_width,
					       i->active_height);
		if (ret)
			goto out;
		if (p) {
			ret = native_rear_finalize_bf_roi(bf, &i->af, i->active_width,
							 i->active_height);
			if (ret)
				goto out;
		} else if (i->af.x || i->af.y || i->af.width || i->af.height) {
			/* Bootstrap has its own source-defined hardcode ROI. */
			ret = -EINVAL;
			goto out;
		}
        if (!p) {
            ret = e011as_rear_mark_cold_gamma_inactive(candidate);
            if (ret)
                goto out;
        }
		if (!!candidate->regs.bfstats.gamma_lut_enable != bf->gamma_valid ||
		    candidate->regs.bfstats.dmi_lut_bank != (p & 1) ||
		    candidate->regs.bfstats.module_lut_bank != (p & 1)) {
			ret = -EPROTO;
			goto out;
		}
		candidate->regs.cst = i->cst;
		candidate->regs.bpcabf = i->bpcabf;
	}
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		base[p].regs.cst = work->pending[p].regs.cst;
		base[p].regs.bpcabf = work->pending[p].regs.bpcabf;
		base[p].regs.bfstats = work->pending[p].regs.bfstats;
		*e008t_rear_bf_dmi(&base[p].dmi) =
			*e008t_rear_bf_dmi(&work->pending[p].dmi);
	}
out:
	memzero_explicit(work, sizeof(*work));
	kfree(work);
	return ret;
}
#endif
