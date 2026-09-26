/* SPDX-License-Identifier: MIT */
/*
 * E006s compile-only Titan680 BC101 provider.
 *
 * The active state is semantic. For the selected rear tuning, BC101 is
 * disabled; the three-word startup disable write is therefore generated from
 * module state rather than copied from a Windows command buffer.
 */

struct e006s_bc101_state {
	bool enabled;
	u16 bin0;
	u16 bin1;
	u16 bin2;
	u16 bin3;
};

static u8 e006s_bc101_clamp(u16 value)
{
	if (value > 0x80)
		return 0x80;

	return (u8)value;
}

static int e006s_bc101_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006s_bc101_state *s = ctx;
	u8 b0, b1, b2, b3;

	if (!s || !value)
		return -EINVAL;

	if (reg != 0x3f60 && reg != 0x3f64 && reg != 0x3f68)
		return -ENOENT;

	/*
	 * Windows leaves the freshly zeroed register image intact when BC101 is
	 * disabled, then emits the exact three-word disable range.
	 */
	if (!s->enabled) {
		*value = 0;
		return 0;
	}

	b0 = e006s_bc101_clamp(s->bin0);
	b1 = e006s_bc101_clamp(s->bin1);
	b2 = e006s_bc101_clamp(s->bin2);
	b3 = e006s_bc101_clamp(s->bin3);

	switch (reg) {
	case 0x3f60:
		*value = 1;
		return 0;
	case 0x3f64:
		*value = (u32)b0 | ((u32)b1 << 16);
		return 0;
	case 0x3f68:
		*value = (u32)b2 | ((u32)b3 << 16);
		return 0;
	default:
		return -ENOENT;
	}
}

/* Compile/link type check against E006m callback signature. */
static e006m_scalar_fn e006s_bc101_recipe __used = e006s_bc101_lookup;
