/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Rear statistics configuration from explicit caller-owned semantic inputs.
 * Internal source contract, not UAPI. Integer geometry belongs in the driver;
 * thresholds/black reference/weights and cold/normal selection belong to IPA.
 * No pixels, register replay, automatic 3A, DMA, readiness or hardware grant.
 */
enum native_rear_stats_geometry_preset {
	NATIVE_REAR_STATS_COLD = 0,
	NATIVE_REAR_STATS_NORMAL = 1,
};
struct native_rear_stats_roi {
	u16 left, top, width, height;
};
struct native_rear_bg_input {
	struct native_rear_stats_roi roi;
	u16 h_num, v_num;
	u32 threshold_r, threshold_b, threshold_gr, threshold_gb;
	u32 black_level_offset;
	u8 y_weight_q4[3];
	bool quad_sync_enable, enabled, controls_valid;
};
struct native_rear_rs_input {
	struct native_rear_stats_roi roi;
	u16 h_num, v_num;
	bool color_conversion;
};
struct native_rear_packet_stats_input {
	u64 request_id;
	u8 phase;
	u16 active_width, active_height;
	struct native_rear_stats_roi bhist;
	struct native_rear_rs_input rs;
	struct native_rear_bg_input aec, tintless, awb;
};
struct native_rear_startup_stats_input {
	struct native_rear_packet_stats_input packet[E007Y_STARTUP_PACKETS];
};
struct native_rear_stats_candidate {
	struct e006u_bhist16_state bhist;
	struct e006v_rs14_state rs;
	struct e006w_aecbe17_state aec, tintless, awb;
};

/* Only geometry changes: no implicit threshold, black, weight or control seed. */
static int
native_rear_stats_geometry_preset(struct native_rear_packet_stats_input *input,
				 enum native_rear_stats_geometry_preset preset)
{
	struct native_rear_stats_roi full, cold;

	if (!input || input->active_width != 4064 ||
	    input->active_height != 2286 ||
	    (preset != NATIVE_REAR_STATS_COLD && preset != NATIVE_REAR_STATS_NORMAL))
		return -EINVAL;
	full = (struct native_rear_stats_roi) {
		.width = input->active_width, .height = input->active_height,
	};
	cold = full;
	cold.width -= cold.width / 10;
	cold.height -= cold.height / 10;
	input->bhist = preset == NATIVE_REAR_STATS_COLD ? cold : full;
	input->aec.roi = preset == NATIVE_REAR_STATS_COLD ? cold : full;
	input->aec.h_num = preset == NATIVE_REAR_STATS_COLD ? 64 : 32;
	input->aec.v_num = preset == NATIVE_REAR_STATS_COLD ? 48 : 32;
	input->awb.roi = preset == NATIVE_REAR_STATS_COLD ? cold : full;
	input->awb.h_num = 64;
	input->awb.v_num = 48;
	input->tintless.roi = full;
	input->tintless.h_num = 32;
	input->tintless.v_num = 24;
	input->rs.roi = full;
	input->rs.h_num = 16;
	input->rs.v_num = 1024;
	return 0;
}

static int
native_rear_stats_roi_validate(const struct native_rear_stats_roi *roi,
			       u16 active_width, u16 active_height)
{
	if (!roi || !roi->width || !roi->height)
		return -EINVAL;
	if (roi->left >= active_width || roi->top >= active_height ||
	    roi->width > active_width - roi->left ||
	    roi->height > active_height - roi->top)
		return -ERANGE;
	/* Conservative current-mode contract: explicit Bayer-aligned origin. */
	if ((roi->left | roi->top) & 1U)
		return -ERANGE;
	return 0;
}

/*
 * Linux normal non-stripe policy: floor to even cell sizes; reject unsupported
 * shapes instead of guessing OEM clamp/stripe/ROI override behavior.
 */
static int
native_rear_stats_make_bg(const struct native_rear_bg_input *input,
			  u16 active_width, u16 active_height,
			  struct e006w_aecbe17_state *out)
{
	struct e006w_aecbe17_state pending = {};
	int ret;

	if (!input || !out || !input->controls_valid)
		return -EINVAL;
	ret = native_rear_stats_roi_validate(&input->roi, active_width, active_height);
	if (ret)
		return ret;
	if (!input->h_num || !input->v_num)
		return -EINVAL;
	pending.h_num = input->h_num;
	pending.v_num = input->v_num;
	pending.h_offset = input->roi.left;
	pending.v_offset = input->roi.top;
	pending.region_width = (input->roi.width / input->h_num) & ~1U;
	pending.region_height = (input->roi.height / input->v_num) & ~1U;
	pending.threshold_r = input->threshold_r;
	pending.threshold_b = input->threshold_b;
	pending.threshold_gr = input->threshold_gr;
	pending.threshold_gb = input->threshold_gb;
	pending.black_level_offset = input->black_level_offset;
	memcpy(pending.y_weight_q4, input->y_weight_q4, sizeof(pending.y_weight_q4));
	pending.quad_sync_enable = input->quad_sync_enable;
	pending.enabled = input->enabled;
	ret = e006w_aecbe17_validate(&pending);
	if (ret)
		return ret;
	*out = pending;
	return 0;
}

static int
native_rear_stats_make_candidate(const struct native_rear_packet_stats_input *input,
				 struct native_rear_stats_candidate *out)
{
	struct native_rear_stats_candidate pending = {};
	int ret;

	if (!input || !out || input->active_width != 4064 ||
	    input->active_height != 2286)
		return -EOPNOTSUPP;
	/*
	 * Bound cell counts to the cold/normal shapes used with the existing
	 * retained ten-WM allocation contract. A new shape needs its own layout
	 * proof; register field fit alone is insufficient.
	 */
	if (!((input->aec.h_num == 64 && input->aec.v_num == 48) ||
	      (input->aec.h_num == 32 && input->aec.v_num == 32)) ||
	    input->tintless.h_num != 32 || input->tintless.v_num != 24 ||
	    input->awb.h_num != 64 || input->awb.v_num != 48)
		return -EOPNOTSUPP;
	/* Cold RS16/1024 is a capability preset, not a permanent AFD policy. */
	if (!input->rs.h_num || input->rs.h_num > 16 ||
	    !input->rs.v_num || input->rs.v_num > 1024)
		return -ERANGE;
	ret = native_rear_stats_roi_validate(&input->bhist,
					    input->active_width, input->active_height);
	if (ret)
		return ret;
	/* E006U covers dimensions only; other BHist words assume zero origin. */
	if (input->bhist.left || input->bhist.top)
		return -EOPNOTSUPP;
	pending.bhist.roi_width = input->bhist.width;
	pending.bhist.roi_height = input->bhist.height;

	ret = native_rear_stats_roi_validate(&input->rs.roi,
					    input->active_width, input->active_height);
	if (ret)
		return ret;
	pending.rs.h_num = input->rs.h_num;
	pending.rs.v_num = input->rs.v_num;
	pending.rs.h_offset = input->rs.roi.left;
	pending.rs.v_offset = input->rs.roi.top;
	pending.rs.region_width = input->rs.roi.width / input->rs.h_num;
	pending.rs.region_height = (input->rs.roi.height / input->rs.v_num) & ~1U;
	pending.rs.enabled = true;
	pending.rs.color_conversion = input->rs.color_conversion;
	ret = e006v_rs14_validate(&pending.rs);
	if (ret)
		return ret;
	ret = native_rear_stats_make_bg(&input->aec,
				       input->active_width, input->active_height, &pending.aec);
	if (ret)
		return ret;
	ret = native_rear_stats_make_bg(&input->tintless,
				       input->active_width, input->active_height, &pending.tintless);
	if (ret)
		return ret;
	ret = native_rear_stats_make_bg(&input->awb,
				       input->active_width, input->active_height, &pending.awb);
	if (ret)
		return ret;
	*out = pending;
	return 0;
}

struct native_rear_stats_work {
	struct native_rear_startup_stats_input snapshot;
	struct native_rear_stats_candidate pending[E007Y_STARTUP_PACKETS];
};

/* Sleepable startup control context only; never call from an ISR. */
static int
native_rear_bind_startup_statistics(
	struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct native_rear_startup_stats_input *input)
{
	struct native_rear_stats_work *work;
	unsigned int p;
	int ret;

	if (!base || !input)
		return -EINVAL;
	work = kzalloc(sizeof(*work), GFP_KERNEL);
	if (!work)
		return -ENOMEM;
	work->snapshot = *input;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		const struct native_rear_packet_stats_input *packet = &work->snapshot.packet[p];
		if (base[p].ready) {
			ret = -EBUSY;
			goto out;
		}
		if (packet->phase != p) {
			ret = -EPROTO;
			goto out;
		}
		if (packet->request_id < 4 || packet->request_id != base[p].request_id) {
			ret = -ESTALE;
			goto out;
		}
		if (packet->active_width != base[p].regs.mnds.input_width ||
		    packet->active_height != base[p].regs.mnds.input_height) {
			ret = -EPROTO;
			goto out;
		}
		ret = native_rear_stats_make_candidate(packet, &work->pending[p]);
		if (ret)
			goto out;
	}
	/* All packet identities, controls and geometry validated before mutation. */
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		base[p].regs.bhist = work->pending[p].bhist;
		base[p].regs.rs = work->pending[p].rs;
		base[p].regs.aec_be = work->pending[p].aec;
		base[p].regs.tintless_bg = work->pending[p].tintless;
		base[p].regs.awb_bg = work->pending[p].awb;
	}
	ret = 0;
out:
	memzero_explicit(work, sizeof(*work));
	kfree(work);
	return ret;
}
static typeof(&native_rear_bind_startup_statistics)
native_rear_startup_statistics_recipe __used = native_rear_bind_startup_statistics;
static typeof(&native_rear_stats_geometry_preset)
native_rear_stats_geometry_preset_recipe __used = native_rear_stats_geometry_preset;
