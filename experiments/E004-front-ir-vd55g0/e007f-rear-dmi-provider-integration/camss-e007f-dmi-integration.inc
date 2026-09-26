/* SPDX-License-Identifier: MIT */
/*
 * E007f compile-only rear DMI producer integration.
 *
 * E006g intentionally exposes one opaque producer context for all DMI
 * families. E007f adapts that interface to separate semantic producer
 * contexts and binds the proven E007e BFStats25 DMI encoder directly.
 *
 * No DMI or RT-CDM submission is introduced here.
 */

struct e007f_rear_dmi_upstream_ops {
	int (*lsc)(void *ctx, u8 selector, u8 *dst, size_t bytes);
	int (*gtm)(void *ctx, u8 *dst, size_t bytes);
	int (*stable)(void *ctx, u16 dmi_reg, u8 selector,
		      u8 *dst, size_t bytes);
};

struct e007f_rear_dmi_state {
	const struct e007f_rear_dmi_upstream_ops *upstream;
	void *lsc_ctx;
	void *gtm_ctx;
	void *stable_ctx;
	struct e007e_bf_dmi_state bfstats25;
};

static int
e007f_rear_lsc(void *ctx, u8 selector, u8 *dst, size_t bytes)
{
	struct e007f_rear_dmi_state *s = ctx;

	if (!s || !s->upstream || !s->upstream->lsc)
		return -EOPNOTSUPP;

	return s->upstream->lsc(s->lsc_ctx, selector, dst, bytes);
}

static int
e007f_rear_gtm(void *ctx, u8 *dst, size_t bytes)
{
	struct e007f_rear_dmi_state *s = ctx;

	if (!s || !s->upstream || !s->upstream->gtm)
		return -EOPNOTSUPP;

	return s->upstream->gtm(s->gtm_ctx, dst, bytes);
}

static int
e007f_rear_bfstats(void *ctx, u8 selector, u8 *dst, size_t bytes)
{
	struct e007f_rear_dmi_state *s = ctx;

	if (!s)
		return -EINVAL;

	return e007e_bfstats25_dmi(&s->bfstats25, selector, dst, bytes);
}

static int
e007f_rear_stable(void *ctx, u16 dmi_reg, u8 selector,
		   u8 *dst, size_t bytes)
{
	struct e007f_rear_dmi_state *s = ctx;

	if (!s || !s->upstream || !s->upstream->stable)
		return -EOPNOTSUPP;

	return s->upstream->stable(s->stable_ctx, dmi_reg, selector,
				   dst, bytes);
}

static const struct e006g_rear_producer_ops
e007f_rear_dmi_ops = {
	.lsc = e007f_rear_lsc,
	.gtm = e007f_rear_gtm,
	.bfstats = e007f_rear_bfstats,
	.stable = e007f_rear_stable,
};

static int
e007f_rear_validate_dmi_integration(const struct e007f_rear_dmi_state *s)
{
	int ret;

	if (!s || !s->upstream)
		return -EINVAL;
	if (!s->upstream->lsc || !s->upstream->gtm || !s->upstream->stable)
		return -EOPNOTSUPP;

	ret = e006g_rear_validate_contract();
	if (ret)
		return ret;

	if (s->bfstats25.roi_count != E007E_BF_ROI_COUNT)
		return -EINVAL;
	if (!s->bfstats25.gamma_valid)
		return -EOPNOTSUPP;

	return 0;
}

static int
e007f_rear_prepare_dynamic(struct e007f_rear_dmi_state *s,
			   struct e006g_rear_dynamic_payloads *out)
{
	int ret;

	ret = e007f_rear_validate_dmi_integration(s);
	if (ret)
		return ret;

	return e006g_rear_prepare_dynamic(&e007f_rear_dmi_ops, s, out);
}

static int
e007f_rear_fill_slot(struct e007f_rear_dmi_state *s,
		     const struct e006g_rear_dynamic_payloads *dyn,
		     const struct e006g_rear_dmi_slot *slot,
		     struct e006g_rear_slot_buffer *out)
{
	int ret;

	ret = e007f_rear_validate_dmi_integration(s);
	if (ret)
		return ret;

	return e006g_rear_fill_slot(&e007f_rear_dmi_ops, s,
				    dyn, slot, out);
}

struct e007f_rear_dmi_integration_ops {
	int (*validate)(const struct e007f_rear_dmi_state *s);
	int (*prepare_dynamic)(struct e007f_rear_dmi_state *s,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007f_rear_dmi_state *s,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007f_rear_dmi_integration_ops
e007f_rear_dmi_integration_recipe __used = {
	.validate = e007f_rear_validate_dmi_integration,
	.prepare_dynamic = e007f_rear_prepare_dynamic,
	.fill_slot = e007f_rear_fill_slot,
};
