#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
a=json.load(open(D/'AUTHORITY-SAFE.json'))
pts=a['common_setting']['transformed_points']
lines=[]
for i in range(0,len(pts),12): lines.append('\t'+', '.join(str(x) for x in pts[i:i+12])+',')
arr='\n'.join(lines)
src='''/* SPDX-License-Identifier: MIT */
#define E007U_BPCABF_DMI_REG 0x4908
#define E007U_BPCABF_BYTES 256
#define E007U_BPCABF_POINTS 65

static const u16 e007u_bpcabf_points[E007U_BPCABF_POINTS] = {
__ARRAY__
};

static int e007u_bpcabf411_pack(u8 *dst, size_t bytes)
{
\tunsigned int i;
\tif (!dst || bytes != E007U_BPCABF_BYTES)
\t\treturn -EINVAL;
\tfor (i = 0; i < 64; i++) {
\t\tu32 a = min_t(u32, e007u_bpcabf_points[i], 511);
\t\tu32 b = min_t(u32, e007u_bpcabf_points[i + 1], 511);
\t\tu32 d = a > b ? a - b : b - a;
\t\tu32 word = a | (min_t(u32, d, 511) << 9);
\t\tmemcpy(dst + i * sizeof(word), &word, sizeof(word));
\t}
\treturn 0;
}

struct e007u_rear_remaining_ops {
\tint (*stable_non_bpcabf)(void *ctx, u16 dmi_reg, u8 selector,
\t\t\t\t   u8 *dst, size_t bytes);
};
struct e007u_rear_dmi_state {
\tstruct e007t_rear_dmi_state dmi;
\tconst struct e007u_rear_remaining_ops *remaining;
\tvoid *stable_ctx;
};
static int e007u_rear_stable_non_gamma(void *ctx, u16 dmi_reg, u8 selector,
\t\t\t\t      u8 *dst, size_t bytes)
{
\tstruct e007u_rear_dmi_state *s = ctx;
\tif (!s || !dst) return -EINVAL;
\tif (dmi_reg == E007U_BPCABF_DMI_REG && selector == 1)
\t\treturn e007u_bpcabf411_pack(dst, bytes);
\tif (!s->remaining || !s->remaining->stable_non_bpcabf)
\t\treturn -EOPNOTSUPP;
\treturn s->remaining->stable_non_bpcabf(s->stable_ctx, dmi_reg, selector, dst, bytes);
}
static const struct e007t_rear_remaining_ops e007u_rear_e007t_remaining_ops = {
\t.stable_non_gamma = e007u_rear_stable_non_gamma,
};
static int e007u_rear_bind(struct e007u_rear_dmi_state *s)
{
\tif (!s) return -EINVAL;
\ts->dmi.remaining = &e007u_rear_e007t_remaining_ops;
\ts->dmi.stable_ctx = s;
\treturn 0;
}
static int e007u_rear_validate_request(struct e007u_rear_dmi_state *s, u64 request_id)
{
\tint ret;
\tif (!s) return -EINVAL;
\t/* DSX remains the only nonzero stable-DMI first-frame dependency. */
\tif (!s->remaining || !s->remaining->stable_non_bpcabf)
\t\treturn -EOPNOTSUPP;
\tret = e007u_rear_bind(s);
\tif (ret) return ret;
\treturn e007t_rear_validate_request(&s->dmi, request_id);
}
static int e007u_rear_prepare_dynamic(struct e007u_rear_dmi_state *s, u64 request_id,
\t\t\t\t      struct e006g_rear_dynamic_payloads *out)
{
\tint ret = e007u_rear_validate_request(s, request_id);
\tif (ret) return ret;
\treturn e007t_rear_prepare_dynamic(&s->dmi, request_id, out);
}
static int e007u_rear_fill_slot(struct e007u_rear_dmi_state *s, u64 request_id,
\t\t\t\t const struct e006g_rear_dynamic_payloads *dyn,
\t\t\t\t const struct e006g_rear_dmi_slot *slot,
\t\t\t\t struct e006g_rear_slot_buffer *out)
{
\tint ret = e007u_rear_validate_request(s, request_id);
\tif (ret) return ret;
\treturn e007t_rear_fill_slot(&s->dmi, request_id, dyn, slot, out);
}
struct e007u_rear_bpcabf_ops {
\tint (*validate)(struct e007u_rear_dmi_state *s, u64 request_id);
\tint (*prepare_dynamic)(struct e007u_rear_dmi_state *s, u64 request_id,
\t\t\t       struct e006g_rear_dynamic_payloads *out);
\tint (*fill_slot)(struct e007u_rear_dmi_state *s, u64 request_id,
\t\t\t const struct e006g_rear_dynamic_payloads *dyn,
\t\t\t const struct e006g_rear_dmi_slot *slot,
\t\t\t struct e006g_rear_slot_buffer *out);
};
static const struct e007u_rear_bpcabf_ops e007u_rear_bpcabf_recipe __used = {
\t.validate = e007u_rear_validate_request,
\t.prepare_dynamic = e007u_rear_prepare_dynamic,
\t.fill_slot = e007u_rear_fill_slot,
};
'''.replace('__ARRAY__',arr)
(D/'camss-e007u-bpcabf411.inc').write_text(src)
print('E007U_PROVIDER_GENERATED points=65')
