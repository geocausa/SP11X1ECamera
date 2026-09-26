/* SPDX-License-Identifier: MIT */
/*
 * E006r compile-only Titan680 CST12 packer.
 *
 * Inputs are semantic CST12 state. The reserve values are sourced from the
 * selected rear Surface tuning package; captured Windows register words are
 * used only as a private validation oracle and are not embedded here.
 */

struct e006r_cst12_state {
	bool enabled;
	u16 c00;
	u16 c10;
	u16 c20;
	u16 c01;
	u16 c11;
	u16 c21;
	s16 m00;
	s16 m01;
	s16 m02;
	s16 m10;
	s16 m11;
	s16 m12;
	s16 m20;
	s16 m21;
	s16 m22;
	s16 o0;
	s16 o1;
	s16 o2;
	s16 s0;
	s16 s1;
	s16 s2;
};

static bool e006r_cst12_s13_ok(s16 v)
{
	return v >= -4096 && v <= 4095;
}

static int e006r_cst12_validate(const struct e006r_cst12_state *s)
{
	if (!s)
		return -EINVAL;
	if (s->c00 > 0x0fff || s->c10 > 0x0fff ||
	    s->c20 > 0x0fff || s->c01 > 0x0fff ||
	    s->c11 > 0x0fff || s->c21 > 0x0fff)
		return -ERANGE;
	if (!e006r_cst12_s13_ok(s->m00) ||
	    !e006r_cst12_s13_ok(s->m01) ||
	    !e006r_cst12_s13_ok(s->m02) ||
	    !e006r_cst12_s13_ok(s->m10) ||
	    !e006r_cst12_s13_ok(s->m11) ||
	    !e006r_cst12_s13_ok(s->m12) ||
	    !e006r_cst12_s13_ok(s->m20) ||
	    !e006r_cst12_s13_ok(s->m21) ||
	    !e006r_cst12_s13_ok(s->m22) ||
	    !e006r_cst12_s13_ok(s->o0) ||
	    !e006r_cst12_s13_ok(s->o1) ||
	    !e006r_cst12_s13_ok(s->o2) ||
	    !e006r_cst12_s13_ok(s->s0) ||
	    !e006r_cst12_s13_ok(s->s1) ||
	    !e006r_cst12_s13_ok(s->s2))
		return -ERANGE;

	return 0;
}

static u32 e006r_cst12_s13(s16 v)
{
	return (u32)(u16)v & 0x1fffU;
}

static u32 e006r_cst12_pair(s16 lo, s16 hi)
{
	return e006r_cst12_s13(lo) |
	       (e006r_cst12_s13(hi) << 16);
}

static u32 e006r_cst12_hi13(s16 v)
{
	return e006r_cst12_s13(v) << 19;
}

static u32 e006r_cst12_clamp12(u16 v)
{
	return ((u32)v & 0x0fffU) << 20;
}

static int e006r_cst12_word(const struct e006r_cst12_state *s,
			    u8 index, u32 *value)
{
	int ret;

	if (!value || index > 18)
		return -EINVAL;

	ret = e006r_cst12_validate(s);
	if (ret)
		return ret;

	switch (index) {
	case 0:
		*value = s->enabled ? 1U : 0U;
		break;
	case 1:
		*value = e006r_cst12_pair(s->m00, s->m01);
		break;
	case 2:
		*value = e006r_cst12_s13(s->m02);
		break;
	case 3:
		*value = e006r_cst12_hi13(s->o0);
		break;
	case 4:
		*value = e006r_cst12_hi13(s->s0);
		break;
	case 5:
		*value = e006r_cst12_clamp12(s->c00);
		break;
	case 6:
		*value = e006r_cst12_clamp12(s->c01);
		break;
	case 7:
		*value = e006r_cst12_pair(s->m10, s->m11);
		break;
	case 8:
		*value = e006r_cst12_s13(s->m12);
		break;
	case 9:
		*value = e006r_cst12_hi13(s->o1);
		break;
	case 10:
		*value = e006r_cst12_hi13(s->s1);
		break;
	case 11:
		*value = e006r_cst12_clamp12(s->c10);
		break;
	case 12:
		*value = e006r_cst12_clamp12(s->c11);
		break;
	case 13:
		*value = e006r_cst12_pair(s->m20, s->m21);
		break;
	case 14:
		*value = e006r_cst12_s13(s->m22);
		break;
	case 15:
		*value = e006r_cst12_hi13(s->o2);
		break;
	case 16:
		*value = e006r_cst12_hi13(s->s2);
		break;
	case 17:
		*value = e006r_cst12_clamp12(s->c20);
		break;
	case 18:
		*value = e006r_cst12_clamp12(s->c21);
		break;
	default:
		return -EINVAL;
	}

	return 0;
}

static int e006r_cst12_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006r_cst12_state *s = ctx;
	u8 index;

	if (reg == 0x6160)
		index = 0;
	else if (reg >= 0x6168 && reg <= 0x61ac && !(reg & 3))
		index = 1 + (reg - 0x6168) / 4;
	else
		return -ENOENT;

	return e006r_cst12_word(s, index, value);
}

/* Compile/link type check against E006m callback signature. */
static e006m_scalar_fn e006r_cst12_recipe __used = e006r_cst12_lookup;
