/* SPDX-License-Identifier: MIT */
/*
 * E007q compile-only rear GTM DMI handoff.
 *
 * Userspace owns TMC141 + GTM131 adaptive math. This boundary accepts one
 * source-proven 2048-byte GTM wire payload for one exact request and binds it
 * through E007i -> E007f -> E006g. No DMI submission is introduced here.
 */

#define E007Q_GTM_VALID BIT(0)

struct e007q_rear_gtm_wire_state {
	u64 request_id;
	u32 valid_mask;
	u8 payload[E006G_GTM_BYTES];
};

struct e007q_rear_remaining_ops {
	int (*stable)(void *ctx, u16 dmi_reg, u8 selector,
		      u8 *dst, size_t bytes);
};

struct e007q_rear_dmi_state {
	struct e007i_rear_dmi_state dmi;
	struct e007q_rear_gtm_wire_state gtm;
	const struct e007q_rear_remaining_ops *remaining;
	void *stable_ctx;
};

static int
e007q_rear_gtm(void *ctx, u8 *dst, size_t bytes)
{
	const struct e007q_rear_gtm_wire_state *s = ctx;

	if (!s || !dst || bytes != E006G_GTM_BYTES)
		return -EINVAL;
	if (s->valid_mask != E007Q_GTM_VALID)
		return -EAGAIN;

	memcpy(dst, s->payload, E006G_GTM_BYTES);
	return 0;
}

static int
e007q_rear_stable(void *ctx, u16 dmi_reg, u8 selector,
		  u8 *dst, size_t bytes)
{
	struct e007q_rear_dmi_state *s = ctx;

	if (!s || !s->remaining || !s->remaining->stable)
		return -EOPNOTSUPP;

	return s->remaining->stable(s->stable_ctx, dmi_reg, selector,
				    dst, bytes);
}

static const struct e007i_rear_remaining_ops
e007q_rear_e007i_remaining_ops = {
	.gtm = e007q_rear_gtm,
	.stable = e007q_rear_stable,
};

static int
e007q_rear_bind(struct e007q_rear_dmi_state *s)
{
	if (!s)
		return -EINVAL;

	s->dmi.remaining = &e007q_rear_e007i_remaining_ops;
	s->dmi.gtm_ctx = &s->gtm;
	s->dmi.stable_ctx = s;
	return 0;
}

static int
e007q_rear_validate_request(struct e007q_rear_dmi_state *s,
			    u64 expected_request_id)
{
	int ret;

	if (!s || expected_request_id < 4)
		return -EINVAL;
	if (s->gtm.request_id != expected_request_id)
		return -EPROTO;
	if (s->gtm.valid_mask != E007Q_GTM_VALID)
		return -EAGAIN;
	if (!s->remaining || !s->remaining->stable)
		return -EOPNOTSUPP;

	ret = e007q_rear_bind(s);
	if (ret)
		return ret;

	return e007i_rear_validate_request(&s->dmi, expected_request_id);
}

static int
e007q_rear_prepare_dynamic(struct e007q_rear_dmi_state *s,
			   u64 expected_request_id,
			   struct e006g_rear_dynamic_payloads *out)
{
	int ret;

	ret = e007q_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007i_rear_prepare_dynamic(&s->dmi, expected_request_id, out);
}

static int
e007q_rear_fill_slot(struct e007q_rear_dmi_state *s,
		     u64 expected_request_id,
		     const struct e006g_rear_dynamic_payloads *dyn,
		     const struct e006g_rear_dmi_slot *slot,
		     struct e006g_rear_slot_buffer *out)
{
	int ret;

	ret = e007q_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007i_rear_fill_slot(&s->dmi, expected_request_id,
				    dyn, slot, out);
}

struct e007q_rear_gtm_handoff_ops {
	int (*validate)(struct e007q_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007q_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007q_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007q_rear_gtm_handoff_ops
e007q_rear_gtm_handoff_recipe __used = {
	.validate = e007q_rear_validate_request,
	.prepare_dynamic = e007q_rear_prepare_dynamic,
	.fill_slot = e007q_rear_fill_slot,
};
