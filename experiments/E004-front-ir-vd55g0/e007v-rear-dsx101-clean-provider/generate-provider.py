#!/usr/bin/env python3
from pathlib import Path
import json,textwrap
D=Path(__file__).resolve().parent
A=json.load(open(D/'AUTHORITY-SAFE.json'))
def arr(name,vals):
 rows=[]
 for i in range(0,len(vals),12):
  rows.append('\t'+', '.join(str(x) for x in vals[i:i+12])+',')
 return f'static const s16 {name}[{len(vals)}] = {{\n'+'\n'.join(rows)+'\n};\n'
s='''/* SPDX-License-Identifier: MIT */
/* E007v clean DSX101 provider for the source-locked exact-4x path. */
#define E007V_DSX_LUMA_REG 0xa008
#define E007V_DSX_CHROMA_REG 0xa208
#define E007V_DSX_LUMA_COEFFS 192
#define E007V_DSX_CHROMA_COEFFS 96
#define E007V_DSX_LUMA_BYTES 768
#define E007V_DSX_CHROMA_BYTES 384

'''
s+=arr('e007v_dsx_luma',A['luma_coefficients'])+'\n'
s+=arr('e007v_dsx_chroma',A['chroma_coefficients'])+'\n'
s+=r'''
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
'''
(D/'camss-e007v-dsx101.inc').write_text(s)
print('E007V_PROVIDER_GENERATED')
