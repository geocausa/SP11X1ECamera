/* SPDX-License-Identifier: MIT */
/*
 * E007a compile-only rear BPC/ABF411 calculated-output provider.
 *
 * These fields are outputs of the source-locked BPCABF411 common calculation,
 * not captured Windows register words. Full interpolation/tuning/DMI production
 * remains an upstream Linux parity responsibility.
 */

struct e007a_bpcabf411_calc_state {
	s16 signed10[2];
	u16 unsigned9[2];
	u8 nibble4[2];
	u8 byte_group0[2][4];
	u8 byte_group1[2][4];
	u8 nibble_group[2][4];
};

static int e007a_bpcabf411_validate(const struct e007a_bpcabf411_calc_state *s)
{
	unsigned int c, i;

	if (!s)
		return -EINVAL;

	for (c = 0; c < 2; c++) {
		if (s->signed10[c] < -512 || s->signed10[c] > 511)
			return -ERANGE;
		if (s->unsigned9[c] > 0x1ff || s->nibble4[c] > 0xf)
			return -ERANGE;
		for (i = 0; i < 4; i++)
			if (s->nibble_group[c][i] > 0xf)
				return -ERANGE;
	}
	return 0;
}

static u32 e007a_pack_bytes(const u8 v[4])
{
	return (u32)v[0] |
	       ((u32)v[1] << 8) |
	       ((u32)v[2] << 16) |
	       ((u32)v[3] << 24);
}

static int e007a_bpcabf411_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e007a_bpcabf411_calc_state *s = ctx;
	u32 v;
	int ret;
	unsigned int i;

	if (!value)
		return -EINVAL;
	ret = e007a_bpcabf411_validate(s);
	if (ret)
		return ret;

	switch (reg) {
	case 0x49b8:
		*value = ((u32)(u16)s->signed10[0] & 0x3ff) |
			 ((u32)s->unsigned9[0] << 16) |
			 ((u32)s->nibble4[0] << 28);
		return 0;
	case 0x49bc:
		*value = ((u32)(u16)s->signed10[1] & 0x3ff) |
			 ((u32)s->unsigned9[1] << 16) |
			 ((u32)s->nibble4[1] << 28);
		return 0;
	case 0x49d0:
		*value = e007a_pack_bytes(s->byte_group0[0]);
		return 0;
	case 0x49d4:
		*value = e007a_pack_bytes(s->byte_group0[1]);
		return 0;
	case 0x49d8:
		*value = e007a_pack_bytes(s->byte_group1[0]);
		return 0;
	case 0x49dc:
		*value = e007a_pack_bytes(s->byte_group1[1]);
		return 0;
	case 0x49e0:
		v = 0;
		for (i = 0; i < 4; i++) {
			v |= (u32)s->nibble_group[0][i] << (i * 4);
			v |= (u32)s->nibble_group[1][i] << ((i + 4) * 4);
		}
		*value = v;
		return 0;
	default:
		return -ENOENT;
	}
}

static const u16 e007a_bpcabf411_closed_regs[] = {
	0x49b8, 0x49bc, 0x49d0, 0x49d4, 0x49d8, 0x49dc, 0x49e0,
};

static_assert(ARRAY_SIZE(e007a_bpcabf411_closed_regs) == 7);

struct e007a_bpcabf411_static_ops {
	int (*lookup)(void *ctx, u16 reg, u32 *value);
};

static const struct e007a_bpcabf411_static_ops
e007a_bpcabf411_provider_recipe __used = {
	.lookup = e007a_bpcabf411_lookup,
};
