/* SPDX-License-Identifier: MIT */
/*
 * E006x compile-only Titan680 TintlessBGStats17 startup packer.
 *
 * Direct Titan680 decompilation proves the Tintless BG register image uses
 * the same 18-word semantic field layout as E006w AECBEStats17, translated
 * from 0xb060..0xb0a4 to 0xb660..0xb6a4.
 */
static int e006x_tintless_bg17_lookup(void *ctx, u16 reg, u32 *value)
{
	if (reg < 0xb660 || reg > 0xb6a4 || ((reg - 0xb660) & 3))
		return -ENOENT;

	return e006w_aecbe17_lookup(ctx, reg - 0x600, value);
}

static e006m_scalar_fn e006x_tintless_bg_stats17_recipe __used =
	e006x_tintless_bg17_lookup;
