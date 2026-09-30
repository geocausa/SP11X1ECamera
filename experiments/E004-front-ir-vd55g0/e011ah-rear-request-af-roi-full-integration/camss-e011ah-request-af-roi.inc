/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E011AH: detached L4 request AF rectangle -> L2 BF ROI geometry.
 * Integer-only lowering of the supported E009c/E008x interior, zero-overlap
 * 5x5 branch. No AF algorithm, floating point, packet-output calibration,
 * allocation, hardware access, submission or camera runtime call site.
 */
#ifndef VFE680_E011AH_REQUEST_AF_ROI_INC
#define VFE680_E011AH_REQUEST_AF_ROI_INC

struct e011ah_af_rect {
	u16 x, y, width, height;
};

struct e011ah_request_af_roi {
	u64 caller_request_id;
	u16 camif_width, camif_height;
	u8 startup_phase;
	struct e011ah_af_rect af;
};

/* Validate the complete supported rectangle before modifying output.
 * In this bounded domain, floor(float32(n) * float32(1/5)) == n/5;
 * the private host check proves all n in [0,16384]. */
static int e011ah_map_af_rect(const struct e011ah_request_af_roi *in,
			     struct e011ah_af_rect out[E007E_BF_ROI_COUNT])
{
	struct e011ah_af_rect mapped[E007E_BF_ROI_COUNT];
	u32 x, y, w, h, cell_w, cell_h;
	unsigned int row, col;

	if (!in || !out || in->camif_width < 88 ||
	    in->camif_height < 80 || in->camif_width > 8192 ||
	    in->camif_height > 16384 || !in->af.width || !in->af.height ||
	    (u32)in->af.x + in->af.width > in->camif_width ||
	    (u32)in->af.y + in->af.height > in->camif_height)
		return -EINVAL;
	x = in->af.x & ~1U;
	y = in->af.y & ~1U;
	w = in->af.width & ~1U;
	h = (in->af.height & ~1U) + 5U + 11U;
	if (x < 76 || y < 64 || x + w > in->camif_width - 12U ||
	    y + h > in->camif_height)
		return -ERANGE;
	cell_w = w / 5U;
	cell_h = h / 5U;
	if (cell_w < 6 || cell_h < 8)
		return -ERANGE;
	for (row = 0; row < 5; row++)
		for (col = 0; col < 5; col++) {
			u32 left = x + col * cell_w;
			u32 top = y + row * cell_h;
			u32 width = cell_w - 1U, height = cell_h - 1U;
			unsigned int i = row * 5 + col;

			if (left + width > 8191 || top + height > 16383 ||
			    width > 0x0fff || height > 0x1fff)
				return -ERANGE;
			mapped[i].x = left;
			mapped[i].y = top & ~1U;
			mapped[i].width = width - (!(width & 1U));
			mapped[i].height = height - (!(height & 1U));
		}
	memcpy(out, mapped, sizeof(mapped));
	return 0;
}

/* Caller owns valid, disjoint objects and serializes detached preparation.
 * All three normal requests are checked before any packet changes. Cold ROI,
 * ROI IDs/flags, gamma, registers, other DMI families and readiness are kept.
 * A caller must bind BEFORE sealing/materializing/exposing any output arena.
 * Rejection preserves every input packet, including on a late phase error.
 */
static int e011ah_rear_bind_request_af_roi(
	struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct e011ah_request_af_roi normal[3])
{
	struct e011ah_af_rect mapped[3][E007E_BF_ROI_COUNT];
	unsigned int p, i, q;
	int ret;

	if (!base || !normal ||
	    e011ag_overlap(base, sizeof(*base) * E007Y_STARTUP_PACKETS,
			   normal, sizeof(*normal) * 3))
		return -EINVAL;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		const struct e006z_rear_scalar_state *scalar = &base[p].regs.scalar;
		if (base[p].ready || base[p].request_id < E007Y_STARTUP_PACKETS ||
		    scalar->epoch_kind != E006Z_EPOCH_STARTUP ||
		    scalar->startup_phase != p ||
		    scalar->request_id != base[p].request_id)
			return -EINVAL;
		for (q = 0; q < p; q++)
			if (base[q].request_id == base[p].request_id)
				return -EINVAL;
		if (!p)
			continue;
		if (normal[p - 1].startup_phase != p ||
		    normal[p - 1].caller_request_id != base[p].request_id ||
		    normal[p - 1].camif_width != base[p].regs.mnds.input_width ||
		    normal[p - 1].camif_height != base[p].regs.mnds.input_height ||
		    base[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25.roi_count !=
			E007E_BF_ROI_COUNT ||
		    !base[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25.gamma_valid)
			return -EINVAL;
		ret = e011ah_map_af_rect(&normal[p - 1], mapped[p - 1]);
		if (ret)
			return ret;
	}
	for (p = 1; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007e_bf_dmi_state *d =
			&base[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
		for (i = 0; i < E007E_BF_ROI_COUNT; i++) {
			d->roi[i].left = mapped[p - 1][i].x;
			d->roi[i].top = mapped[p - 1][i].y;
			d->roi[i].width = mapped[p - 1][i].width;
			d->roi[i].height = mapped[p - 1][i].height;
		}
	}
	return 0;
}

struct e011ah_rear_af_roi_ops {
	int (*bind)(struct e008o_rear_packet_semantics *,
		    const struct e011ah_request_af_roi *);
};
static const struct e011ah_rear_af_roi_ops e011ah_rear_af_roi_recipe __used = {
	.bind = e011ah_rear_bind_request_af_roi,
};

static int __used e011ah_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
