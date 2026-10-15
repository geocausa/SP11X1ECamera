/* SPDX-License-Identifier: MIT */
#define E007U_BPCABF_DMI_REG 0x4908
#define E007U_BPCABF_BYTES 256
#define E007U_BPCABF_POINTS 65

static const u16 e007u_bpcabf_points[E007U_BPCABF_POINTS] = {
	/* our rear noise model, ov13858-rear-abf-v1.json */
	388, 294, 246, 216, 195, 179, 166, 156, 147, 140, 134, 128, 123, 119, 115, 111, 108, 105, 102, 100, 97, 95, 93, 91, 89, 88, 86, 85, 83, 82, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 68, 67, 66, 65, 65, 64, 63, 63, 62, 62, 61, 60, 60, 59, 59, 58, 58, 57, 57, 57, 56, 56,
};

static int e007u_bpcabf411_pack(u8 *dst, size_t bytes)
{
	unsigned int i;
	if (!dst || bytes != E007U_BPCABF_BYTES)
		return -EINVAL;
	for (i = 0; i < 64; i++) {
		u32 a = min_t(u32, e007u_bpcabf_points[i], 511);
		u32 b = min_t(u32, e007u_bpcabf_points[i + 1], 511);
		u32 d = a > b ? a - b : b - a;
		u32 word = a | (min_t(u32, d, 511) << 9);
		memcpy(dst + i * sizeof(word), &word, sizeof(word));
	}
	return 0;
}

struct e007u_rear_remaining_ops {
	int (*stable_non_bpcabf)(void *ctx, u16 dmi_reg, u8 selector,
				   u8 *dst, size_t bytes);
};
struct e007u_rear_dmi_state {
	struct e007t_rear_dmi_state dmi;
	const struct e007u_rear_remaining_ops *remaining;
	void *stable_ctx;
};
static int e007u_rear_stable_non_gamma(void *ctx, u16 dmi_reg, u8 selector,
				      u8 *dst, size_t bytes)
{
	struct e007u_rear_dmi_state *s = ctx;
	if (!s || !dst) return -EINVAL;
	if (dmi_reg == E007U_BPCABF_DMI_REG && selector == 1)
		return e007u_bpcabf411_pack(dst, bytes);
	if (!s->remaining || !s->remaining->stable_non_bpcabf)
		return -EOPNOTSUPP;
	return s->remaining->stable_non_bpcabf(s->stable_ctx, dmi_reg, selector, dst, bytes);
}
static const struct e007t_rear_remaining_ops e007u_rear_e007t_remaining_ops = {
	.stable_non_gamma = e007u_rear_stable_non_gamma,
};
static int e007u_rear_bind(struct e007u_rear_dmi_state *s)
{
	if (!s) return -EINVAL;
	s->dmi.remaining = &e007u_rear_e007t_remaining_ops;
	s->dmi.stable_ctx = s;
	return 0;
}
static int e007u_rear_validate_request(struct e007u_rear_dmi_state *s, u64 request_id)
{
	int ret;
	if (!s) return -EINVAL;
	/* DSX remains the only nonzero stable-DMI first-frame dependency. */
	if (!s->remaining || !s->remaining->stable_non_bpcabf)
		return -EOPNOTSUPP;
	ret = e007u_rear_bind(s);
	if (ret) return ret;
	return e007t_rear_validate_request(&s->dmi, request_id);
}
static int e007u_rear_prepare_dynamic(struct e007u_rear_dmi_state *s, u64 request_id,
				      struct e006g_rear_dynamic_payloads *out)
{
	int ret = e007u_rear_validate_request(s, request_id);
	if (ret) return ret;
	return e007t_rear_prepare_dynamic(&s->dmi, request_id, out);
}
static int e007u_rear_fill_slot(struct e007u_rear_dmi_state *s, u64 request_id,
				 const struct e006g_rear_dynamic_payloads *dyn,
				 const struct e006g_rear_dmi_slot *slot,
				 struct e006g_rear_slot_buffer *out)
{
	int ret = e007u_rear_validate_request(s, request_id);
	if (ret) return ret;
	return e007t_rear_fill_slot(&s->dmi, request_id, dyn, slot, out);
}
struct e007u_rear_bpcabf_ops {
	int (*validate)(struct e007u_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007u_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007u_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};
static const struct e007u_rear_bpcabf_ops e007u_rear_bpcabf_recipe __used = {
	.validate = e007u_rear_validate_request,
	.prepare_dynamic = e007u_rear_prepare_dynamic,
	.fill_slot = e007u_rear_fill_slot,
};
