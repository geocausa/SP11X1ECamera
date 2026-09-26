/* SPDX-License-Identifier: MIT */
/*
 * E007b compile-only rear BFStats25 calculated-output provider.
 *
 * This is the exact Titan680 register packing boundary after AF/BF request
 * policy has produced the low-level BF state. It does not generate ROI/gamma
 * DMI, choose AF ROIs, or embed captured Windows register words.
 */

struct e007b_bfstats25_calc_state {
	u8 dmi_lut_bank;
	u8 module_lut_bank;
	u8 luma_select;
	u8 gamma_lut_enable;
	u8 luma_conversion_enable;
	u8 scale_enable;
	u8 filter0_enable;
	u8 filter1_enable;
	u8 filter3_enable;
	s8 signed6[13];
	s16 quant16_a[10];
	s16 quant16_b[10];
	s8 signed4[2];
	u32 tail_scalar17[2];
	u8 tail_lane5[2][17];
};

static int e007b_bfstats25_validate(const struct e007b_bfstats25_calc_state *s)
{
	unsigned int i, b;

	if (!s)
		return -EINVAL;

	if (s->dmi_lut_bank > 1 || s->module_lut_bank > 1 ||
	    s->luma_select > 1 || s->gamma_lut_enable > 1 ||
	    s->luma_conversion_enable > 1 || s->scale_enable > 1 ||
	    s->filter0_enable > 1 || s->filter1_enable > 1 ||
	    s->filter3_enable > 1)
		return -ERANGE;

	for (i = 0; i < ARRAY_SIZE(s->signed6); i++)
		if (s->signed6[i] < -32 || s->signed6[i] > 31)
			return -ERANGE;

	for (i = 0; i < ARRAY_SIZE(s->signed4); i++)
		if (s->signed4[i] < -8 || s->signed4[i] > 7)
			return -ERANGE;

	for (b = 0; b < 2; b++) {
		if (s->tail_scalar17[b] > 0x1ffff)
			return -ERANGE;
		for (i = 0; i < 17; i++)
			if (s->tail_lane5[b][i] > 0x1f)
				return -ERANGE;
	}

	return 0;
}

static u32 e007b_pack_signed6(const s8 *v, unsigned int count)
{
	u32 out = 0;
	unsigned int i;

	for (i = 0; i < count; i++)
		out |= ((u32)(u8)v[i] & 0x3f) << (i * 8);

	return out;
}

static u32 e007b_pack_s16_pair(s16 lo, s16 hi)
{
	return (u32)(u16)lo | ((u32)(u16)hi << 16);
}

static u32 e007b_pack_tail5(const u8 *v, unsigned int count)
{
	u32 out = 0;
	unsigned int i;

	for (i = 0; i < count; i++)
		out |= (u32)v[i] << (i * 6);

	return out;
}

static u32 e007b_bfstats25_cfg(const struct e007b_bfstats25_calc_state *s)
{
	return BIT(0) |
	       ((u32)s->luma_select << 8) |
	       ((u32)s->gamma_lut_enable << 9) |
	       ((u32)s->luma_conversion_enable << 12) |
	       ((u32)s->scale_enable << 13) |
	       ((u32)s->filter0_enable << 16) |
	       ((u32)s->filter1_enable << 17) |
	       ((u32)s->filter3_enable << 21);
}

static int e007b_bfstats25_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e007b_bfstats25_calc_state *s = ctx;
	int ret;

	if (!value)
		return -EINVAL;
	ret = e007b_bfstats25_validate(s);
	if (ret)
		return ret;

	switch (reg) {
	case 0xbc58:
		*value = s->dmi_lut_bank;
		return 0;
	case 0xbc5c:
		*value = s->module_lut_bank;
		return 0;
	case 0xbc60:
		*value = e007b_bfstats25_cfg(s);
		return 0;
	case 0xbc6c:
		*value = e007b_pack_signed6(&s->signed6[0], 4);
		return 0;
	case 0xbc70:
		*value = e007b_pack_signed6(&s->signed6[4], 4);
		return 0;
	case 0xbc74:
		*value = e007b_pack_signed6(&s->signed6[8], 4);
		return 0;
	case 0xbc78:
		*value = e007b_pack_signed6(&s->signed6[12], 1);
		return 0;
	case 0xbc7c:
		*value = e007b_pack_s16_pair(s->quant16_a[0], s->quant16_a[1]);
		return 0;
	case 0xbc80:
		*value = e007b_pack_s16_pair(s->quant16_a[2], s->quant16_a[3]);
		return 0;
	case 0xbc84:
		*value = e007b_pack_s16_pair(s->quant16_a[4], s->quant16_a[5]);
		return 0;
	case 0xbc88:
		*value = e007b_pack_s16_pair(s->quant16_a[6], s->quant16_a[7]);
		return 0;
	case 0xbc8c:
		*value = e007b_pack_s16_pair(s->quant16_a[8], s->quant16_a[9]);
		return 0;
	case 0xbc90:
		*value = e007b_pack_s16_pair(s->quant16_b[0], s->quant16_b[1]);
		return 0;
	case 0xbc94:
		*value = (u32)(u16)s->quant16_b[2];
		return 0;
	case 0xbc98:
		*value = e007b_pack_s16_pair(s->quant16_b[3], s->quant16_b[4]);
		return 0;
	case 0xbc9c:
		*value = e007b_pack_s16_pair(s->quant16_b[5], s->quant16_b[6]);
		return 0;
	case 0xbca0:
		*value = (u32)(u16)s->quant16_b[7];
		return 0;
	case 0xbca4:
		*value = e007b_pack_s16_pair(s->quant16_b[8], s->quant16_b[9]);
		return 0;
	case 0xbca8:
		*value = ((u32)(u8)s->signed4[0] & 0xf) |
			 (((u32)(u8)s->signed4[1] & 0xf) << 4);
		return 0;
	case 0xbcac:
		*value = s->tail_scalar17[0];
		return 0;
	case 0xbcb0:
		*value = e007b_pack_tail5(&s->tail_lane5[0][0], 5);
		return 0;
	case 0xbcb4:
		*value = e007b_pack_tail5(&s->tail_lane5[0][5], 5);
		return 0;
	case 0xbcb8:
		*value = e007b_pack_tail5(&s->tail_lane5[0][10], 5);
		return 0;
	case 0xbcbc:
		*value = e007b_pack_tail5(&s->tail_lane5[0][15], 2);
		return 0;
	case 0xbcc0:
		*value = s->tail_scalar17[1];
		return 0;
	case 0xbcc4:
		*value = e007b_pack_tail5(&s->tail_lane5[1][0], 5);
		return 0;
	case 0xbcc8:
		*value = e007b_pack_tail5(&s->tail_lane5[1][5], 5);
		return 0;
	case 0xbccc:
		*value = e007b_pack_tail5(&s->tail_lane5[1][10], 5);
		return 0;
	case 0xbcd0:
		*value = e007b_pack_tail5(&s->tail_lane5[1][15], 2);
		return 0;
	default:
		return -ENOENT;
	}
}

static const u16 e007b_bfstats25_closed_regs[] = {
	0xbc58, 0xbc5c, 0xbc60,
	0xbc6c, 0xbc70, 0xbc74, 0xbc78, 0xbc7c, 0xbc80, 0xbc84,
	0xbc88, 0xbc8c, 0xbc90, 0xbc94, 0xbc98, 0xbc9c, 0xbca0,
	0xbca4, 0xbca8, 0xbcac, 0xbcb0, 0xbcb4, 0xbcb8, 0xbcbc,
	0xbcc0, 0xbcc4, 0xbcc8, 0xbccc, 0xbcd0,
};

static_assert(ARRAY_SIZE(e007b_bfstats25_closed_regs) == 29);

struct e007b_bfstats25_static_ops {
	int (*lookup)(void *ctx, u16 reg, u32 *value);
};

static const struct e007b_bfstats25_static_ops
e007b_bfstats25_provider_recipe __used = {
	.lookup = e007b_bfstats25_lookup,
};
