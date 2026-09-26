/* SPDX-License-Identifier: MIT */
/*
 * E006w compile-only Titan680 AECBEStats17 startup packer.
 *
 * Inputs are adjusted semantic AEC BE state. No captured Windows register
 * words or command bytes are embedded. Upstream AEC/stripe/ROI policy remains
 * a separate producer concern.
 */
#define E006W_AECBE17_SAMPLE_PATTERN 0xffffU

struct e006w_aecbe17_state {
	u16 h_num;
	u16 v_num;
	u16 h_offset;
	u16 v_offset;
	u16 region_width;
	u16 region_height;
	u32 threshold_r;
	u32 threshold_b;
	u32 threshold_gr;
	u32 threshold_gb;
	u32 black_level_offset;
	u8 y_weight_q4[3];
	bool quad_sync_enable;
	bool enabled;
};

static int e006w_aecbe17_validate(const struct e006w_aecbe17_state *s)
{
	unsigned int i;

	if (!s)
		return -EINVAL;
	if (!s->h_num || s->h_num > 64 ||
	    !s->v_num || s->v_num > 64)
		return -ERANGE;
	if (s->region_width < 16 || s->region_width > 512 ||
	    s->region_height < 16 || s->region_height > 512)
		return -ERANGE;
	if (s->h_offset > 0x3ffe || s->v_offset > 0x3ffe ||
	    (s->h_offset & 1) || (s->v_offset & 1))
		return -ERANGE;
	if (s->threshold_r > 0x3ffff ||
	    s->threshold_b > 0x3ffff ||
	    s->threshold_gr > 0x3ffff ||
	    s->threshold_gb > 0x3ffff ||
	    s->black_level_offset > 0x3ffff)
		return -ERANGE;
	for (i = 0; i < ARRAY_SIZE(s->y_weight_q4); i++)
		if (s->y_weight_q4[i] > 0x7f)
			return -ERANGE;

	return 0;
}

static u32 e006w_aecbe17_min_word(u32 black_level_offset)
{
	return 0U - (black_level_offset << 13);
}

static int e006w_aecbe17_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006w_aecbe17_state *s = ctx;
	u32 min_word;
	int ret;

	if (!value)
		return -EINVAL;

	ret = e006w_aecbe17_validate(s);
	if (ret)
		return ret;

	min_word = e006w_aecbe17_min_word(s->black_level_offset);

	switch (reg) {
	case 0xb060:
		*value = E006W_AECBE17_SAMPLE_PATTERN << 16 |
			 (s->quad_sync_enable ? BIT(9) : 0U) |
			 (s->enabled ? BIT(0) : 0U);
		return 0;
	case 0xb064:
		*value = s->black_level_offset << 14;
		return 0;
	case 0xb068:
		*value = (u32)s->y_weight_q4[0] << 9 |
			 (u32)s->y_weight_q4[1] << 17 |
			 (u32)s->y_weight_q4[2] << 25;
		return 0;
	case 0xb06c:
		*value = ((u32)(s->h_num - 1U) << 16) |
			 (s->h_offset & 0x3ffeU);
		return 0;
	case 0xb070:
		*value = (u32)s->region_width - 1U;
		return 0;
	case 0xb074:
		*value = ((u32)(s->v_num - 1U) << 16) |
			 (s->v_offset & 0x3ffeU);
		return 0;
	case 0xb078:
		*value = (u32)s->region_height - 1U;
		return 0;
	case 0xb07c:
		*value = 0;
		return 0;
	case 0xb080:
		*value = s->threshold_gr << 14;
		return 0;
	case 0xb084:
		*value = s->threshold_r << 14;
		return 0;
	case 0xb088:
		*value = s->threshold_gb << 14;
		return 0;
	case 0xb08c:
		*value = s->threshold_b << 14;
		return 0;
	case 0xb090:
		*value = s->threshold_gb << 14;
		return 0;
	case 0xb094:
	case 0xb098:
	case 0xb09c:
	case 0xb0a0:
	case 0xb0a4:
		*value = min_word;
		return 0;
	default:
		return -ENOENT;
	}
}

/* Compile/link type check against E006m callback signature. */
static e006m_scalar_fn e006w_aecbe_stats17_recipe __used =
	e006w_aecbe17_lookup;
