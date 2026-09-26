#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
a=json.load(open(D/'AUTHORITY-SAFE.json'))
vals=a['curve']['samples']
lines=[]
for i in range(0,len(vals),12):
    lines.append('\t'+', '.join(str(x) for x in vals[i:i+12])+',')
arr='\n'.join(lines)
src='''/* SPDX-License-Identifier: MIT */
/*
 * E007t compile-only rear Gamma151 clean provider.
 *
 * Semantic authority: 257 integral 12-bit samples derived from the selected
 * OV13858 Gamma1.5 tuning region. These are tuning semantics, not captured
 * Windows DMI words.
 */
#define E007T_GAMMA_DMI_REG 0x5f08
#define E007T_GAMMA_BYTES   1024
#define E007T_GAMMA_SAMPLES 257

static const u16 e007t_gamma_curve[E007T_GAMMA_SAMPLES] = {
__ARRAY__
};

static int
e007t_gamma151_pack(u8 *dst, size_t bytes)
{
\tunsigned int i;

\tif (!dst || bytes != E007T_GAMMA_BYTES)
\t\treturn -EINVAL;

\tfor (i = 0; i < 256; i++) {
\t\tint x = e007t_gamma_curve[i];
\t\tint y = e007t_gamma_curve[i + 1];
\t\tint d = y - x;
\t\tu32 word;

\t\tif (d < -2048)
\t\t\td = -2048;
\t\telse if (d > 2047)
\t\t\td = 2047;

\t\tword = (u32)x | (((u32)d & 0xfff) << 12);
\t\tmemcpy(dst + i * sizeof(word), &word, sizeof(word));
\t}

\treturn 0;
}

struct e007t_rear_remaining_ops {
\tint (*stable_non_gamma)(void *ctx, u16 dmi_reg, u8 selector,
\t\t\t\t u8 *dst, size_t bytes);
};

struct e007t_rear_dmi_state {
\tstruct e007s_rear_dmi_state dmi;
\tconst struct e007t_rear_remaining_ops *remaining;
\tvoid *stable_ctx;
};

static int
e007t_rear_stable_nonzero(void *ctx, u16 dmi_reg, u8 selector,
\t\t\t u8 *dst, size_t bytes)
{
\tstruct e007t_rear_dmi_state *s = ctx;

\tif (!s || !dst)
\t\treturn -EINVAL;

\tif (dmi_reg == E007T_GAMMA_DMI_REG &&
\t    selector >= 1 && selector <= 3)
\t\treturn e007t_gamma151_pack(dst, bytes);

\tif (!s->remaining || !s->remaining->stable_non_gamma)
\t\treturn -EOPNOTSUPP;

\treturn s->remaining->stable_non_gamma(s->stable_ctx, dmi_reg,
\t\t\t\t\t      selector, dst, bytes);
}

static const struct e007s_rear_remaining_ops
e007t_rear_e007s_remaining_ops = {
\t.stable_nonzero = e007t_rear_stable_nonzero,
};

static int
e007t_rear_bind(struct e007t_rear_dmi_state *s)
{
\tif (!s)
\t\treturn -EINVAL;

\ts->dmi.remaining = &e007t_rear_e007s_remaining_ops;
\ts->dmi.stable_ctx = s;
\treturn 0;
}

static int
e007t_rear_validate_request(struct e007t_rear_dmi_state *s,
\t\t\t    u64 expected_request_id)
{
\tint ret;

\tif (!s)
\t\treturn -EINVAL;

\t/* BPC/ABF and DSX remain mandatory first-frame dependencies. */
\tif (!s->remaining || !s->remaining->stable_non_gamma)
\t\treturn -EOPNOTSUPP;

\tret = e007t_rear_bind(s);
\tif (ret)
\t\treturn ret;

\treturn e007s_rear_validate_request(&s->dmi, expected_request_id);
}

static int
e007t_rear_prepare_dynamic(struct e007t_rear_dmi_state *s,
\t\t\t   u64 expected_request_id,
\t\t\t   struct e006g_rear_dynamic_payloads *out)
{
\tint ret = e007t_rear_validate_request(s, expected_request_id);

\tif (ret)
\t\treturn ret;

\treturn e007s_rear_prepare_dynamic(&s->dmi, expected_request_id, out);
}

static int
e007t_rear_fill_slot(struct e007t_rear_dmi_state *s,
\t\t     u64 expected_request_id,
\t\t     const struct e006g_rear_dynamic_payloads *dyn,
\t\t     const struct e006g_rear_dmi_slot *slot,
\t\t     struct e006g_rear_slot_buffer *out)
{
\tint ret = e007t_rear_validate_request(s, expected_request_id);

\tif (ret)
\t\treturn ret;

\treturn e007s_rear_fill_slot(&s->dmi, expected_request_id,
\t\t\t\t    dyn, slot, out);
}

struct e007t_rear_gamma_ops {
\tint (*validate)(struct e007t_rear_dmi_state *s, u64 request_id);
\tint (*prepare_dynamic)(struct e007t_rear_dmi_state *s, u64 request_id,
\t\t\t       struct e006g_rear_dynamic_payloads *out);
\tint (*fill_slot)(struct e007t_rear_dmi_state *s, u64 request_id,
\t\t\t const struct e006g_rear_dynamic_payloads *dyn,
\t\t\t const struct e006g_rear_dmi_slot *slot,
\t\t\t struct e006g_rear_slot_buffer *out);
};

static const struct e007t_rear_gamma_ops
e007t_rear_gamma_recipe __used = {
\t.validate = e007t_rear_validate_request,
\t.prepare_dynamic = e007t_rear_prepare_dynamic,
\t.fill_slot = e007t_rear_fill_slot,
};
'''.replace('__ARRAY__',arr)
(D/'camss-e007t-gamma151.inc').write_text(src)
print('E007T_PROVIDER_GENERATED samples=257')
