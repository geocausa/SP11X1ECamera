/* SPDX-License-Identifier: MIT */
/*
 * E006q compile-only Titan680 MNDS23 Video Full packer.
 *
 * Inputs are semantic Linux-owned geometry. The normal non-stripe path is
 * implemented; captured Windows register words/command bytes are not embedded.
 */

struct e006q_crop_info {
	u16 first_pixel;
	u16 first_line;
	u16 last_pixel;
	u16 last_line;
};

struct e006q_mnds23_state {
	u16 input_width;
	u16 input_height;
	u16 luma_width;
	u16 luma_height;
	u8 chroma_h_div;
	u8 chroma_v_div;
	struct e006q_crop_info pre_crop;
	bool enabled;
	bool stripe_override;
};

static u32 e006q_div_round_u64(u64 numerator, u32 denominator)
{
	return (u32)((numerator + denominator / 2U) / denominator);
}

static int e006q_mnds23_validate(const struct e006q_mnds23_state *s)
{
	if (!s)
		return -EINVAL;
	if (!s->enabled || s->stripe_override)
		return -EOPNOTSUPP;
	if (!s->input_width || !s->input_height ||
	    !s->luma_width || !s->luma_height ||
	    !s->chroma_h_div || !s->chroma_v_div)
		return -EINVAL;
	if (s->input_width > 0x4000 || s->input_height > 0x4000 ||
	    s->luma_width > 0x4000 || s->luma_height > 0x4000)
		return -ERANGE;
	if (s->luma_width % s->chroma_h_div ||
	    s->luma_height % s->chroma_v_div)
		return -EINVAL;
	if (s->pre_crop.first_pixel > 0x3fff ||
	    s->pre_crop.last_pixel > 0x3fff ||
	    s->pre_crop.first_line > 0x3fff ||
	    s->pre_crop.last_line > 0x3fff ||
	    s->pre_crop.first_pixel > s->pre_crop.last_pixel ||
	    s->pre_crop.first_line > s->pre_crop.last_line)
		return -ERANGE;

	return 0;
}

static u32 e006q_mnds23_interp(u32 input, u32 output)
{
	if ((u64)input > (u64)output * 64U)
		return 0U;
	if ((u64)input > (u64)output * 32U)
		return 1U;
	if ((u64)input > (u64)output * 16U)
		return 2U;
	return 3U;
}

static u32 e006q_mnds23_phase(u32 input, u32 output)
{
	u32 phase;

	phase = e006q_div_round_u64((u64)input << 21, output);
	return (e006q_mnds23_interp(input, output) << 30) |
	       (phase & 0x1fffffffU);
}

static bool e006q_mnds23_sub2(u32 input, u32 output)
{
	return input > output && (u64)input < (u64)output * 2U;
}

static u32 e006q_mnds23_phase_init(u32 input, u32 output)
{
	u32 magnitude;

	if (!e006q_mnds23_sub2(input, output))
		return 0;

	magnitude = e006q_div_round_u64(
		((u64)output * 2U - input) << 20, output);
	return (0U - magnitude) & 0x1fffffffU;
}

static u32 e006q_mnds23_frac(u32 input, u32 output)
{
	if (!e006q_mnds23_sub2(input, output))
		return 0;

	return e006q_div_round_u64(
		((u64)output * 2U - input) * 16U, output) & 0xfU;
}

static int e006q_mnds23_word(const struct e006q_mnds23_state *s,
			     bool chroma, u8 index, u32 *value)
{
	u32 out_w, out_h;
	int ret;

	if (!value || index > 9)
		return -EINVAL;

	ret = e006q_mnds23_validate(s);
	if (ret)
		return ret;

	out_w = s->luma_width;
	out_h = s->luma_height;
	if (chroma) {
		out_w /= s->chroma_h_div;
		out_h /= s->chroma_v_div;
	}
	if (!out_w || !out_h)
		return -EINVAL;

	switch (index) {
	case 0:
		*value = 1U;
		break;
	case 1:
		*value = 0x600U;
		break;
	case 2:
		*value = ((u32)(s->input_width - 1U) << 16) |
			 (s->input_height - 1U);
		break;
	case 3:
		*value = e006q_mnds23_phase(s->input_width, out_w);
		break;
	case 4:
		*value = e006q_mnds23_phase_init(s->input_width, out_w);
		break;
	case 5:
		*value = e006q_mnds23_phase(s->input_height, out_h);
		break;
	case 6:
		*value = e006q_mnds23_phase_init(s->input_height, out_h);
		break;
	case 7:
		*value = ((u32)s->pre_crop.first_line << 16) |
			 s->pre_crop.last_line;
		break;
	case 8:
		*value = ((u32)s->pre_crop.first_pixel << 16) |
			 s->pre_crop.last_pixel;
		break;
	case 9:
		*value = (e006q_mnds23_frac(s->input_width, out_w) << 16) |
			 e006q_mnds23_frac(s->input_height, out_h);
		break;
	default:
		return -EINVAL;
	}

	return 0;
}

static int e006q_mnds23_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006q_mnds23_state *s = ctx;
	u16 base;
	bool chroma;

	if (reg >= 0x9860 && reg <= 0x9884) {
		base = 0x9860;
		chroma = false;
	} else if (reg >= 0x9a60 && reg <= 0x9a84) {
		base = 0x9a60;
		chroma = true;
	} else {
		return -ENOENT;
	}
	if ((reg - base) & 3)
		return -ENOENT;

	return e006q_mnds23_word(s, chroma, (reg - base) / 4, value);
}

/* Compile/link type check against E006m callback signature. */
static e006m_scalar_fn e006q_mnds23_recipe __used = e006q_mnds23_lookup;
