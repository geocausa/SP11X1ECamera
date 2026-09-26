/* SPDX-License-Identifier: MIT */
/*
 * E007s compile-only rear zero-stable DMI binding.
 *
 * E007r proves two remaining "stable" identities are exact all-zero payloads
 * in rear startup/steady state and byte-identical to the accepted front path:
 *   PDPC 0x3d08 selector 1: 512 bytes
 *   LSC  0x4308 selector 3: 884 bytes
 *
 * Other stable identities remain delegated and fail closed if absent.
 */

#define E007S_PDPC_DMI_REG 0x3d08
#define E007S_LSC_DMI_REG  0x4308
#define E007S_PDPC_BYTES   512

struct e007s_rear_remaining_ops {
	int (*stable_nonzero)(void *ctx, u16 dmi_reg, u8 selector,
			      u8 *dst, size_t bytes);
};

struct e007s_rear_dmi_state {
	struct e007q_rear_dmi_state dmi;
	const struct e007s_rear_remaining_ops *remaining;
	void *stable_ctx;
};

static int
e007s_rear_stable(void *ctx, u16 dmi_reg, u8 selector,
		  u8 *dst, size_t bytes)
{
	struct e007s_rear_dmi_state *s = ctx;

	if (!s || !dst)
		return -EINVAL;

	if (dmi_reg == E007S_PDPC_DMI_REG && selector == 1) {
		if (bytes != E007S_PDPC_BYTES)
			return -EINVAL;
		memset(dst, 0, bytes);
		return 0;
	}

	if (dmi_reg == E007S_LSC_DMI_REG && selector == 3) {
		if (bytes != E006G_LSC_BYTES)
			return -EINVAL;
		memset(dst, 0, bytes);
		return 0;
	}

	if (!s->remaining || !s->remaining->stable_nonzero)
		return -EOPNOTSUPP;

	return s->remaining->stable_nonzero(s->stable_ctx, dmi_reg,
					    selector, dst, bytes);
}

static const struct e007q_rear_remaining_ops
e007s_rear_e007q_remaining_ops = {
	.stable = e007s_rear_stable,
};

static int
e007s_rear_bind(struct e007s_rear_dmi_state *s)
{
	if (!s)
		return -EINVAL;

	s->dmi.remaining = &e007s_rear_e007q_remaining_ops;
	s->dmi.stable_ctx = s;
	return 0;
}

static int
e007s_rear_validate_request(struct e007s_rear_dmi_state *s,
			    u64 expected_request_id)
{
	int ret;

	if (!s)
		return -EINVAL;

	/*
	 * The two zero identities are closed here, but a complete request still
	 * needs BPC/ABF, Gamma and DSX. Refuse to advertise completeness until
	 * their shared nonzero provider is installed.
	 */
	if (!s->remaining || !s->remaining->stable_nonzero)
		return -EOPNOTSUPP;

	ret = e007s_rear_bind(s);
	if (ret)
		return ret;

	return e007q_rear_validate_request(&s->dmi, expected_request_id);
}

static int
e007s_rear_prepare_dynamic(struct e007s_rear_dmi_state *s,
			   u64 expected_request_id,
			   struct e006g_rear_dynamic_payloads *out)
{
	int ret;

	ret = e007s_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007q_rear_prepare_dynamic(&s->dmi, expected_request_id, out);
}

static int
e007s_rear_fill_slot(struct e007s_rear_dmi_state *s,
		     u64 expected_request_id,
		     const struct e006g_rear_dynamic_payloads *dyn,
		     const struct e006g_rear_dmi_slot *slot,
		     struct e006g_rear_slot_buffer *out)
{
	int ret;

	ret = e007s_rear_validate_request(s, expected_request_id);
	if (ret)
		return ret;

	return e007q_rear_fill_slot(&s->dmi, expected_request_id,
				    dyn, slot, out);
}

struct e007s_rear_zero_stable_ops {
	int (*validate)(struct e007s_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007s_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007s_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007s_rear_zero_stable_ops
e007s_rear_zero_stable_recipe __used = {
	.validate = e007s_rear_validate_request,
	.prepare_dynamic = e007s_rear_prepare_dynamic,
	.fill_slot = e007s_rear_fill_slot,
};
