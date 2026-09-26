/* SPDX-License-Identifier: MIT */
/*
 * E006v compile-only Titan680 RSStats14 startup packer.
 *
 * Inputs are adjusted semantic RS state.  No captured Windows register words
 * or command bytes are embedded.  Upstream AFD/stripe policy remains a
 * separate producer concern.
 */
struct e006v_rs14_state {
	u16 h_num;
	u16 v_num;
	u16 region_width;
	u16 region_height;
	u16 h_offset;
	u16 v_offset;
	bool enabled;
	bool color_conversion;
};

static u8 e006v_rs14_shift_bits(u32 width, u32 height)
{
	u32 area = width * height;
	u8 bits = 0;

	while (area) {
		bits++;
		area >>= 1;
	}

	return bits > 4 ? bits - 4 : 0;
}

static int e006v_rs14_validate(const struct e006v_rs14_state *s)
{
	if (!s)
		return -EINVAL;
	if (!s->enabled)
		return -EOPNOTSUPP;
	if (!s->h_num || s->h_num > 16 ||
	    !s->v_num || s->v_num > 1024)
		return -ERANGE;
	if (s->region_width < 2 || s->region_width > 0x2000 ||
	    s->region_height < 2 || s->region_height > 16 ||
	    (s->region_height & 1))
		return -ERANGE;
	if (s->h_offset > 0x1fff || s->v_offset > 0x3fff ||
	    (s->v_offset & 1))
		return -ERANGE;
	if (e006v_rs14_shift_bits(s->region_width, s->region_height) > 0xf)
		return -ERANGE;

	return 0;
}

static int e006v_rs14_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006v_rs14_state *s = ctx;
	u32 shift;
	int ret;

	if (!value)
		return -EINVAL;

	ret = e006v_rs14_validate(s);
	if (ret)
		return ret;

	shift = e006v_rs14_shift_bits(s->region_width, s->region_height);

	switch (reg) {
	case 0xbe60:
		*value = 1U |
			 (s->color_conversion ? 0x10U : 0U) |
			 ((shift & 0xfU) << 8);
		return 0;
	case 0xbe68:
		*value = ((u32)s->v_offset << 16) | s->h_offset;
		return 0;
	case 0xbe6c:
		*value = (((u32)s->v_num - 1U) << 16) |
			 ((u32)s->h_num - 1U);
		return 0;
	case 0xbe70:
		*value = (((u32)s->region_height - 1U) << 16) |
			 ((u32)s->region_width - 1U);
		return 0;
	default:
		return -ENOENT;
	}
}

/* Compile/link type check against E006m callback signature. */
static e006m_scalar_fn e006v_rs_stats14_recipe __used =
	e006v_rs14_lookup;
