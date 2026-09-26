/* SPDX-License-Identifier: MIT */
/*
 * E007i compile-only rear LSC DMI handoff.
 *
 * Userspace owns adaptive LSC/Tintless math.  This boundary accepts only the
 * two proven 884-byte dynamic LSC wire payloads for one exact request.
 * E006g derives the GIC alias itself.
 */

#define E007I_LSC_VALID_SELECTOR1 BIT(0)
#define E007I_LSC_VALID_SELECTOR2 BIT(1)
#define E007I_LSC_VALID_ALL (E007I_LSC_VALID_SELECTOR1 | E007I_LSC_VALID_SELECTOR2)

struct e007i_rear_lsc_wire_state {
	u64 request_id;
	u32 valid_mask;
	u8 selector1[E006G_LSC_BYTES];
	u8 selector2[E006G_LSC_BYTES];
};

struct e007i_rear_remaining_ops {
	int (*gtm)(void *ctx, u8 *dst, size_t bytes);
	int (*stable)(void *ctx, u16 dmi_reg, u8 selector,
		      u8 *dst, size_t bytes);
};

struct e007i_rear_dmi_state {
	struct e007f_rear_dmi_state dmi;
	struct e007i_rear_lsc_wire_state lsc;
	const struct e007i_rear_remaining_ops *remaining;
	void *gtm_ctx;
	void *stable_ctx;
};

static int
e007i_rear_lsc(void *ctx, u8 selector, u8 *dst, size_t bytes)
{
	const struct e007i_rear_lsc_wire_state *s = ctx;
	const u8 *src;

	if (!s || !dst || bytes != E006G_LSC_BYTES)
		return -EINVAL;
	if (s->valid_mask != E007I_LSC_VALID_ALL)
		return -EAGAIN;

	switch (selector) {
	case 1:
		src = s->selector1;
		break;
	case 2:
		src = s->selector2;
		break;
	default:
		return -EINVAL;
	}

	memcpy(dst, src, E006G_LSC_BYTES);
	return 0;
}

static int
e007i_rear_gtm(void *ctx, u8 *dst, size_t bytes)
{
	struct e007i_rear_dmi_state *s = ctx;

	if (!s || !s->remaining || !s->remaining->gtm)
		return -EOPNOTSUPP;

	return s->remaining->gtm(s->gtm_ctx, dst, bytes);
}

static int
e007i_rear_stable(void *ctx, u16 dmi_reg, u8 selector,
		   u8 *dst, size_t bytes)
{
	struct e007i_rear_dmi_state *s = ctx;

	if (!s || !s->remaining || !s->remaining->stable)
		return -EOPNOTSUPP;

	return s->remaining->stable(s->stable_ctx, dmi_reg, selector,
				    dst, bytes);
}

static const struct e007f_rear_dmi_upstream_ops
e007i_rear_upstream_ops = {
	.lsc = e007i_rear_lsc,
	.gtm = e007i_rear_gtm,
	.stable = e007i_rear_stable,
};

static int
e007i_rear_bind(struct e007i_rear_dmi_state *s)
{
	if (!s)
		return -EINVAL;

	s->dmi.upstream = &e007i_rear_upstream_ops;
	s->dmi.lsc_ctx = &s->lsc;
	s->dmi.gtm_ctx = s;
	s->dmi.stable_ctx = s;
	return 0;
}

static int
e007i_rear_validate_request(struct e007i_rear_dmi_state *s,
			    u64 expected_request_id)
{
	int ret;

	if (!s || expected_request_id < 4)
		return -EINVAL;
	if (s->lsc.request_id != expected_request_id)
		return -EPROTO;
	if (s->lsc.valid_mask != E007I_LSC_VALID_ALL)
		return -EAGAIN;
	if (!s->remaining || !s->remaining->gtm || !s->remaining->stable)
		return -EOPNOTSUPP;

	ret = e007i_rear_bind(s);
	if (ret)
		return ret;

	return e007f_rear_validate_dmi_integration(&s->dmi);
}

static int
e007i_rear_prepare_dynamic(struct e007i_rear_dmi_state *s,
			   u64 expected_request_id,
			   struct e006g_rear_dynamic_payloads *out)
{
	int ret;

	ret = e007i_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007f_rear_prepare_dynamic(&s->dmi, out);
}

static int
e007i_rear_fill_slot(struct e007i_rear_dmi_state *s,
		     u64 expected_request_id,
		     const struct e006g_rear_dynamic_payloads *dyn,
		     const struct e006g_rear_dmi_slot *slot,
		     struct e006g_rear_slot_buffer *out)
{
	int ret;

	ret = e007i_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007f_rear_fill_slot(&s->dmi, dyn, slot, out);
}

struct e007i_rear_lsc_handoff_ops {
	int (*validate)(struct e007i_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007i_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007i_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007i_rear_lsc_handoff_ops
e007i_rear_lsc_handoff_recipe __used = {
	.validate = e007i_rear_validate_request,
	.prepare_dynamic = e007i_rear_prepare_dynamic,
	.fill_slot = e007i_rear_fill_slot,
};
