/* SPDX-License-Identifier: MIT */
/*
 * E006t compile-only Titan680 rear startup providers for four small IQ
 * configuration words.
 *
 * The selected rear startup state is disabled for all four modules. The
 * Windows Titan680 objects zero-initialize their register images and their
 * disabled CreateSubCmdList paths emit the zero image. Do not guess enabled
 * configuration state: those paths remain explicit -EOPNOTSUPP here.
 */
struct e006t_small_iq_state {
	bool bayer_gtm101_enabled;
	bool bayer_ltm101_enabled;
	bool lcac111_enabled;
	bool uv_gamma101_enabled;
};

static int e006t_disabled_word(bool enabled, u32 *value)
{
	if (!value)
		return -EINVAL;
	if (enabled)
		return -EOPNOTSUPP;

	*value = 0;
	return 0;
}

static int e006t_bayer_gtm101_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006t_small_iq_state *s = ctx;

	if (!s || reg != 0x4d60)
		return -ENOENT;
	return e006t_disabled_word(s->bayer_gtm101_enabled, value);
}

static int e006t_bayer_ltm101_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006t_small_iq_state *s = ctx;

	if (!s || reg != 0x5260)
		return -ENOENT;
	return e006t_disabled_word(s->bayer_ltm101_enabled, value);
}

static int e006t_lcac111_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006t_small_iq_state *s = ctx;

	if (!s || reg != 0x5460)
		return -ENOENT;
	return e006t_disabled_word(s->lcac111_enabled, value);
}

static int e006t_uv_gamma101_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006t_small_iq_state *s = ctx;

	if (!s || reg != 0x6360)
		return -ENOENT;
	return e006t_disabled_word(s->uv_gamma101_enabled, value);
}

/* Compile/link type checks against E006m callback signature. */
static e006m_scalar_fn e006t_bayer_gtm101_recipe __used =
	e006t_bayer_gtm101_lookup;
static e006m_scalar_fn e006t_bayer_ltm101_recipe __used =
	e006t_bayer_ltm101_lookup;
static e006m_scalar_fn e006t_lcac111_recipe __used =
	e006t_lcac111_lookup;
static e006m_scalar_fn e006t_uv_gamma101_recipe __used =
	e006t_uv_gamma101_lookup;
