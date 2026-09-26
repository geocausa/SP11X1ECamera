/* SPDX-License-Identifier: MIT */
/*
 * E006y compile-only Titan680 AWBBGStats17 startup packer.
 *
 * Direct Titan680 decompilation proves AWB BG uses the same semantic
 * 18-word Bayer-grid field layout as E006w AECBEStats17, translated
 * from 0xb060..0xb0a4 to 0xb860..0xb8a4.
 */
static int e006y_awbbg17_lookup(void *ctx, u16 reg, u32 *value)
{
	if (reg < 0xb860 || reg > 0xb8a4 || ((reg - 0xb860) & 3))
		return -ENOENT;

	return e006w_aecbe17_lookup(ctx, reg - 0x800, value);
}

static e006m_scalar_fn e006y_awbbg_stats17_recipe __used =
	e006y_awbbg17_lookup;
