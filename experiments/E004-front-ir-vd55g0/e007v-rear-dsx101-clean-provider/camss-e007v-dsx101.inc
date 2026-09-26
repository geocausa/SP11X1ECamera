/* SPDX-License-Identifier: MIT */
/* E007v clean DSX101 provider for the source-locked exact-4x path. */
#define E007V_DSX_LUMA_REG 0xa008
#define E007V_DSX_CHROMA_REG 0xa208
#define E007V_DSX_LUMA_COEFFS 192
#define E007V_DSX_CHROMA_COEFFS 96
#define E007V_DSX_LUMA_BYTES 768
#define E007V_DSX_CHROMA_BYTES 384

static const s16 e007v_dsx_luma[192] = {
	152, 153, 153, 153, 153, 153, 153, 152, 153, 152, 153, 153,
	152, 152, 152, 152, 152, 152, 152, 152, 152, 152, 152, 151,
	152, 151, 152, 152, 152, 152, 151, 151, 151, 151, 151, 151,
	151, 150, 150, 150, 149, 149, 148, 148, 147, 147, 146, 145,
	144, 143, 142, 140, 139, 137, 136, 134, 132, 130, 128, 126,
	124, 121, 119, 117, 115, 113, 111, 109, 106, 105, 103, 101,
	99, 98, 96, 95, 94, 93, 92, 91, 91, 91, 91, 91,
	92, 93, 94, 96, 97, 99, 101, 102, 104, 106, 108, 110,
	113, 115, 116, 118, 120, 122, 123, 125, 126, 127, 127, 128,
	128, 128, 127, 126, 125, 123, 121, 119, 116, 113, 110, 106,
	102, 98, 93, 89, 84, 79, 75, 70, 65, 60, 55, 50,
	45, 40, 35, 31, 26, 22, 18, 14, 11, 8, 5, 2,
	0, -2, -3, -5, -6, -7, -8, -8, -9, -9, -9, -9,
	-9, -9, -9, -8, -8, -7, -7, -6, -5, -5, -4, -4,
	-3, -2, -2, -1, -1, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};

static const s16 e007v_dsx_chroma[96] = {
	256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256,
	256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256,
	256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256,
	256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256,
	256, 248, 240, 232, 224, 216, 208, 200, 192, 184, 176, 168,
	160, 152, 144, 136, 128, 120, 112, 104, 96, 88, 80, 72,
	64, 56, 48, 40, 32, 24, 16, 8, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};


static int e007v_dsx_pack_bank(const s16 *coeff, unsigned int count,
			       u8 *dst, size_t bytes)
{
	unsigned int i, entries;

	if (!coeff || !dst || (count & 1))
		return -EINVAL;
	entries = count / 2;
	if (bytes != entries * sizeof(u64))
		return -EINVAL;

	for (i = 0; i < entries; i++) {
		u64 word = (u64)((u32)coeff[2 * i] & 0xfff) |
			   ((u64)((u32)coeff[2 * i + 1] & 0xfff) << 12);

		if (i + 1 < entries)
			word |= (u64)((u32)coeff[2 * i + 2] & 0xfff) << 24;
		memcpy(dst + i * sizeof(word), &word, sizeof(word));
	}
	return 0;
}

static int e007v_dsx101_pack(u16 dmi_reg, u8 selector, u8 *dst, size_t bytes)
{
	if (selector != 1 && selector != 2)
		return -ENOENT;
	if (dmi_reg == E007V_DSX_LUMA_REG)
		return e007v_dsx_pack_bank(e007v_dsx_luma,
					   E007V_DSX_LUMA_COEFFS,
					   dst, bytes);
	if (dmi_reg == E007V_DSX_CHROMA_REG)
		return e007v_dsx_pack_bank(e007v_dsx_chroma,
					   E007V_DSX_CHROMA_COEFFS,
					   dst, bytes);
	return -ENOENT;
}

struct e007v_rear_dmi_state {
	struct e007u_rear_dmi_state dmi;
};

static int e007v_rear_dsx(void *ctx, u16 dmi_reg, u8 selector,
			  u8 *dst, size_t bytes)
{
	struct e007v_rear_dmi_state *s = ctx;

	if (!s)
		return -EINVAL;
	return e007v_dsx101_pack(dmi_reg, selector, dst, bytes);
}

static const struct e007u_rear_remaining_ops e007v_rear_e007u_remaining_ops = {
	.stable_non_bpcabf = e007v_rear_dsx,
};

static int e007v_rear_bind(struct e007v_rear_dmi_state *s)
{
	if (!s)
		return -EINVAL;
	s->dmi.remaining = &e007v_rear_e007u_remaining_ops;
	s->dmi.stable_ctx = s;
	return 0;
}

static int e007v_rear_validate_request(struct e007v_rear_dmi_state *s,
				       u64 request_id)
{
	int ret = e007v_rear_bind(s);

	if (ret)
		return ret;
	return e007u_rear_validate_request(&s->dmi, request_id);
}

static int e007v_rear_prepare_dynamic(struct e007v_rear_dmi_state *s,
				      u64 request_id,
				      struct e006g_rear_dynamic_payloads *out)
{
	int ret = e007v_rear_validate_request(s, request_id);

	if (ret)
		return ret;
	return e007u_rear_prepare_dynamic(&s->dmi, request_id, out);
}

static int e007v_rear_fill_slot(struct e007v_rear_dmi_state *s,
				u64 request_id,
				const struct e006g_rear_dynamic_payloads *dyn,
				const struct e006g_rear_dmi_slot *slot,
				struct e006g_rear_slot_buffer *out)
{
	int ret = e007v_rear_validate_request(s, request_id);

	if (ret)
		return ret;
	return e007u_rear_fill_slot(&s->dmi, request_id, dyn, slot, out);
}

struct e007v_rear_dsx_ops {
	int (*validate)(struct e007v_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007v_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007v_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007v_rear_dsx_ops e007v_rear_dsx_recipe __used = {
	.validate = e007v_rear_validate_request,
	.prepare_dynamic = e007v_rear_prepare_dynamic,
	.fill_slot = e007v_rear_fill_slot,
};
