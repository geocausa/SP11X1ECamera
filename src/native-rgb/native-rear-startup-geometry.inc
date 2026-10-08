/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Internal source contract for the retained rear 4K, 10-bit ISP surface.
 * This surface is not linear NV12. No UAPI, MMIO, readiness or submit grant.
 * Dimensions come from the Linux sensor mode and reviewed CSID/output targets;
 * register words are produced by the retained semantic packers.
 */
struct native_rear_geometry_mode {
	u16 sensor_width;
	u16 sensor_height;
	u16 isp_width;
	u16 isp_height;
	u16 output_width;
	u16 output_height;
	u8 bit_width;
	u64 request_id[E007Y_STARTUP_PACKETS];
};

static void
native_rear_geometry_path(struct e006p_output_path *path,
			  u16 width, u16 height, u8 bit_width)
{
	memset(path, 0, sizeof(*path));
	path->luma.last_pixel = width - 1;
	path->luma.last_line = height - 1;
	path->chroma.last_pixel = width / 2 - 1;
	path->chroma.last_line = height / 2 - 1;
	path->bit_width = bit_width;
	path->enabled = true;
}

static int
native_rear_bind_startup_geometry(
	struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct native_rear_geometry_mode *mode)
{
	struct native_rear_geometry_mode selected;
	struct e006p_rear_geometry geometry = {};
	struct e006q_mnds23_state mnds = {};
	struct e007c_period_cfg_state period = {};
	struct e006s_bc101_state bc101 = {};
	struct e006t_small_iq_state small_iq = {};
	unsigned int p;
	u16 ds4_height, ds16_height;
	int ret;

	if (!base || !mode)
		return -EINVAL;
	selected = *mode;
	/*
	 * Fail closed against this backend's existing fixed CSID crop and ten-WM
	 * surface. A different crop, mode, format or stripe needs its own contract.
	 * CSID starts at (0,0). The 4064x2286 sensor mode supplies its own crop;
	 * the legacy full sensor mode is retained for source comparisons.
	 */
	if (!((selected.sensor_width == 4076 && selected.sensor_height == 2806) ||
	      (selected.sensor_width == 4064 && selected.sensor_height == 2286)) ||
	    selected.isp_width != 4064 || selected.isp_height != 2286 ||
	    selected.output_width != 3840 || selected.output_height != 2160 ||
	    selected.bit_width != 10)
		return -EOPNOTSUPP;

	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		if (base[p].ready)
			return -EBUSY;
		if (selected.request_id[p] < 4 ||
		    base[p].request_id != selected.request_id[p])
			return -ESTALE;
	}
	/* DS paths use ceil division and even luma height for 4:2:0 chroma. */
	ds4_height = (((selected.output_height + 3) / 4) + 1) & ~1U;
	ds16_height = (((selected.output_height + 15) / 16) + 1) & ~1U;
	native_rear_geometry_path(&geometry.full, selected.output_width,
				  selected.output_height, selected.bit_width);
	native_rear_geometry_path(&geometry.ds4, selected.output_width / 4,
				  ds4_height, selected.bit_width);
	native_rear_geometry_path(&geometry.ds16, selected.output_width / 16,
				  ds16_height, selected.bit_width);

	mnds.input_width = selected.isp_width;
	mnds.input_height = selected.isp_height;
	mnds.luma_width = selected.output_width;
	mnds.luma_height = selected.output_height;
	mnds.chroma_h_div = 2;
	mnds.chroma_v_div = 2;
	mnds.pre_crop.last_pixel = selected.isp_width - 1;
	mnds.pre_crop.last_line = selected.isp_height - 1;
	mnds.enabled = true;
	ret = e006q_mnds23_validate(&mnds);
	if (ret)
		return ret;
	/* Ordinary non-HFR startup: no batch suppression, BC/small IQ disabled. */
	ret = e007w_period_cfg_state_init(&period, 1);
	if (ret)
		return ret;

	/* All admission and production precede mutation; unrelated state survives. */
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		base[p].regs.geometry = geometry;
		base[p].regs.mnds = mnds;
		base[p].regs.period = period;
		base[p].regs.bc101 = bc101;
		base[p].regs.small_iq = small_iq;
	}
	return 0;
}

static typeof(&native_rear_bind_startup_geometry)
native_rear_startup_geometry_recipe __used = native_rear_bind_startup_geometry;
