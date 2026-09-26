/* SPDX-License-Identifier: MIT */
/*
 * E006u compile-only Titan680 BHistStats16 startup provider.
 *
 * The two startup1-only DMI-side words are the zero-initialized register
 * image emitted by CreateCmdList. The region-count word is generated from
 * Linux-owned BHist ROI geometry using the exact BHistStats16 calculation
 * and Titan680 packing rules.
 */

struct e006u_bhist16_state {
	u32 roi_width;
	u32 roi_height;
};

static int e006u_bhist16_region_word(const struct e006u_bhist16_state *s,
				     u32 *value)
{
	u32 half_w, half_h;
	u32 h_num, v_num;

	if (!s || !value || !s->roi_width || !s->roi_height)
		return -EINVAL;

	half_w = s->roi_width >> 1;
	half_h = s->roi_height >> 1;

	/* BHistStats16::CalculateRegionConfiguration. */
	h_num = half_w > 2 ? half_w - 1 : 1;
	v_num = half_h > 0 ? half_h - 1 : 0;

	/* IFEBHistStats16Titan680::PackIQRegisterSetting. */
	*value = (h_num & 0x1fff) | ((v_num & 0x1fff) << 16);
	return 0;
}

static int e006u_bhist16_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006u_bhist16_state *s = ctx;

	if (!value)
		return -EINVAL;

	switch (reg) {
	case 0xb258:
	case 0xb25c:
		/*
		 * These words exist only in startup1. Titan680 construction zeroes
		 * the complete 0x50-byte register image; the packer only clears
		 * bit 0 before this DMI-side range is emitted.
		 */
		*value = 0;
		return 0;
	case 0xb26c:
		return e006u_bhist16_region_word(s, value);
	default:
		return -ENOENT;
	}
}

static e006m_scalar_fn e006u_bhist16_recipe __used = e006u_bhist16_lookup;
