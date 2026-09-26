/* SPDX-License-Identifier: MIT */
/*
 * E007d compile-only rear register-provider integration.
 *
 * This file contains no new hardware formulas and no captured Windows values.
 * It only adapts one aggregate Linux-owned semantic state object onto the
 * already-verified E006/E007 provider callbacks.
 */

struct e007d_rear_register_state {
	struct e006z_rear_scalar_state scalar;
	struct e007a_bpcabf411_calc_state bpcabf;
	struct e007b_bfstats25_calc_state bfstats;
	struct e006p_rear_geometry geometry;
	struct e006q_mnds23_state mnds;
	struct e006r_cst12_state cst;
	struct e006s_bc101_state bc101;
	struct e006t_small_iq_state small_iq;
	struct e006u_bhist16_state bhist;
	struct e006v_rs14_state rs;
	struct e006w_aecbe17_state aec_be;
	struct e006w_aecbe17_state tintless_bg;
	struct e006w_aecbe17_state awb_bg;
	struct e007c_period_cfg_state period;
};

static int e007d_scalar_bank(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;

	if (!s)
		return -EINVAL;
	return e006z_rear_clean_scalar_bank_lookup(&s->scalar, reg, value);
}

static int e007d_bpc_abf(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	int ret;

	if (!s)
		return -EINVAL;

	ret = e006z_rear_clean_scalar_bank_lookup(&s->scalar, reg, value);
	if (ret != -ENOENT)
		return ret;

	return e007a_bpcabf411_lookup(&s->bpcabf, reg, value);
}

static int e007d_bfstats25(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;

	if (!s)
		return -EINVAL;
	return e007b_bfstats25_lookup(&s->bfstats, reg, value);
}

static int e007d_singleton(void *ctx, u16 reg, u32 *value)
{
	(void)ctx;
	return e006o_rear_steady_singleton_lookup(NULL, reg, value);
}

static int e007d_bc101(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006s_bc101_lookup(&s->bc101, reg, value) : -EINVAL;
}

static int e007d_bayer_gtm101(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006t_bayer_gtm101_lookup(&s->small_iq, reg, value) : -EINVAL;
}

static int e007d_bayer_ltm101(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006t_bayer_ltm101_lookup(&s->small_iq, reg, value) : -EINVAL;
}

static int e007d_lcac111(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006t_lcac111_lookup(&s->small_iq, reg, value) : -EINVAL;
}

static int e007d_cst12(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006r_cst12_lookup(&s->cst, reg, value) : -EINVAL;
}

static int e007d_uv_gamma101(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006t_uv_gamma101_lookup(&s->small_iq, reg, value) : -EINVAL;
}

static int e007d_mnds23(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006q_mnds23_lookup(&s->mnds, reg, value) : -EINVAL;
}

static int e007d_round_clamp12(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006p_roundclamp12_lookup(&s->geometry, reg, value) : -EINVAL;
}

static int e007d_crop12(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006p_crop12_lookup(&s->geometry, reg, value) : -EINVAL;
}

static int e007d_aec_be17(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006w_aecbe17_lookup(&s->aec_be, reg, value) : -EINVAL;
}

static int e007d_bhist16(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006u_bhist16_lookup(&s->bhist, reg, value) : -EINVAL;
}

static int e007d_tintless_bg17(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006x_tintless_bg17_lookup(&s->tintless_bg, reg, value) : -EINVAL;
}

static int e007d_awb_bg17(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006y_awbbg17_lookup(&s->awb_bg, reg, value) : -EINVAL;
}

static int e007d_rs14(void *ctx, u16 reg, u32 *value)
{
	struct e007d_rear_register_state *s = ctx;
	return s ? e006v_rs14_lookup(&s->rs, reg, value) : -EINVAL;
}

/*
 * Deliberately unusable through E006m's old packet-blind scalar path.
 * E007d startup fill always goes through E007c's packet-aware wrapper.
 */
static int e007d_period_requires_packet(void *ctx, u16 reg, u32 *value)
{
	(void)ctx;
	(void)reg;
	(void)value;
	return -EOPNOTSUPP;
}

static const struct e006m_rear_startup_bundle e007d_rear_bundle = {
	.steady = {
		.demux_bls = e007d_scalar_bank,
		.pdpc = e007d_scalar_bank,
		.lsc = e007d_scalar_bank,
		.wb = e007d_scalar_bank,
		.gic = e007d_scalar_bank,
		.bpc_abf = e007d_bpc_abf,
		.gtm = e007d_scalar_bank,
		.gamma = e007d_scalar_bank,
		.dsx = e007d_scalar_bank,
		.bfstats25 = e007d_bfstats25,
	},
	.extra = {
		.steady_singleton = e007d_singleton,
		.bc101 = e007d_bc101,
		.bayer_gtm101 = e007d_bayer_gtm101,
		.bayer_ltm101 = e007d_bayer_ltm101,
		.lcac111 = e007d_lcac111,
		.cst12 = e007d_cst12,
		.uv_gamma101 = e007d_uv_gamma101,
		.mnds23 = e007d_mnds23,
		.round_clamp12 = e007d_round_clamp12,
		.crop12 = e007d_crop12,
		.aec_be_stats17 = e007d_aec_be17,
		.bhist_stats16 = e007d_bhist16,
		.tintless_bg_stats17 = e007d_tintless_bg17,
		.awb_bg_stats17 = e007d_awb_bg17,
		.rs_stats14 = e007d_rs14,
		.period_cfg = e007d_period_requires_packet,
	},
};

static int
e007d_rear_validate_register_integration(void)
{
	return e006m_rear_validate_startup_contract(&e007d_rear_bundle);
}

static int
e007d_rear_fill_steady(struct e007d_rear_register_state *s,
		       u16 reg, u32 *value)
{
	if (!s)
		return -EINVAL;
	return e006j_rear_fill_scalar(&e007d_rear_bundle.steady, s, reg, value);
}

static int
e007d_rear_fill_startup(struct e007d_rear_register_state *s,
			u8 packet, u16 reg, u32 *value)
{
	struct e007c_rear_startup_context ctx;

	if (!s)
		return -EINVAL;

	ctx.producer_ctx = s;
	ctx.period = s->period;
	return e007c_rear_fill_startup_packet(&e007d_rear_bundle,
					     &ctx, packet, reg, value);
}

struct e007d_rear_register_integration_ops {
	int (*validate)(void);
	int (*steady)(struct e007d_rear_register_state *s,
		      u16 reg, u32 *value);
	int (*startup)(struct e007d_rear_register_state *s,
		       u8 packet, u16 reg, u32 *value);
};

static const struct e007d_rear_register_integration_ops
e007d_rear_register_integration_recipe __used = {
	.validate = e007d_rear_validate_register_integration,
	.steady = e007d_rear_fill_steady,
	.startup = e007d_rear_fill_startup,
};
