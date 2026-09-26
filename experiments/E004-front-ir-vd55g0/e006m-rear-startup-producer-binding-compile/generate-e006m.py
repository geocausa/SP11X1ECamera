#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
L=D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json"
OUT=D/"camss-e006m-rear-startup-bindings.inc"
j=json.loads(L.read_text())

shared={"PDPC","WB","BPC_ABF","BFSTATS25"}
extra={
 "BC101","BAYER_GTM101","BAYER_LTM101","LCAC111","CST12","UV_GAMMA101",
 "MNDS23","ROUND_CLAMP12","CROP12","AEC_BE_STATS17","BHIST_STATS16",
 "TINTLESS_BG_STATS17","AWB_BG_STATS17","RS_STATS14","VFE680_PERIOD_CFG"
}
all_owners=sorted(shared|extra)
owner_id={name:i+1 for i,name in enumerate(all_owners)}

rows=[]
for s in j["reusable_steady_singleton_offsets"]:
    rows.append((int(s,16),"E006M_SOURCE_STEADY_SINGLETON","E006M_OWNER_NONE"))
for x in j["steady_dynamic"]:
    rows.append((int(x["register"],16),"E006M_SOURCE_STEADY_DYNAMIC","E006M_OWNER_NONE"))
for x in j["startup_differs_from_steady"]:
    owner=x["owner"]
    src="E006M_SOURCE_SHARED_STARTUP" if owner in shared else "E006M_SOURCE_EXTRA_STARTUP"
    rows.append((int(x["register"],16),src,"E006M_OWNER_"+owner))
for x in j["startup_only"]:
    owner=x["owner"]
    rows.append((int(x["register"],16),"E006M_SOURCE_EXTRA_STARTUP","E006M_OWNER_"+owner))
rows.sort()
assert len(rows)==714
assert len({r for r,_,_ in rows})==714

owner_enum=["\tE006M_OWNER_NONE = 0,"]+[f"\tE006M_OWNER_{x}," for x in all_owners]+["\tE006M_OWNER_COUNT,"]
table="\n".join(f"\t{{ .reg = 0x{r:04x}, .source = {s}, .owner = {o} }}," for r,s,o in rows)

extra_fields={
 "BC101":"bc101",
 "BAYER_GTM101":"bayer_gtm101",
 "BAYER_LTM101":"bayer_ltm101",
 "LCAC111":"lcac111",
 "CST12":"cst12",
 "UV_GAMMA101":"uv_gamma101",
 "MNDS23":"mnds23",
 "ROUND_CLAMP12":"round_clamp12",
 "CROP12":"crop12",
 "AEC_BE_STATS17":"aec_be_stats17",
 "BHIST_STATS16":"bhist_stats16",
 "TINTLESS_BG_STATS17":"tintless_bg_stats17",
 "AWB_BG_STATS17":"awb_bg_stats17",
 "RS_STATS14":"rs_stats14",
 "VFE680_PERIOD_CFG":"period_cfg",
}

shared_cases={
 "PDPC":"pdpc",
 "WB":"wb",
 "BPC_ABF":"bpc_abf",
 "BFSTATS25":"bfstats25",
}
extra_struct="\n".join(f"\te006m_scalar_fn {field};" for _,field in extra_fields.items())
shared_switch="\n".join(
 f"\tcase E006M_OWNER_{owner}:\n\t\treturn ops->{field};"
 for owner,field in shared_cases.items())
extra_switch="\n".join(
 f"\tcase E006M_OWNER_{owner}:\n\t\treturn ops->{field};"
 for owner,field in extra_fields.items())

text=f'''/* SPDX-License-Identifier: MIT */
/*
 * E006m compile-only rear startup-register binding.
 *
 * Generated from the safe E006l owner map. No captured Windows values,
 * pointers, IOVAs or command bytes are embedded. This file is unreachable
 * at runtime and exists only to make startup ownership compiler-visible.
 */

enum e006m_rear_startup_source {{
\tE006M_SOURCE_STEADY_SINGLETON = 0,
\tE006M_SOURCE_STEADY_DYNAMIC,
\tE006M_SOURCE_SHARED_STARTUP,
\tE006M_SOURCE_EXTRA_STARTUP,
}};

enum e006m_rear_startup_owner {{
{chr(10).join(owner_enum)}
}};

struct e006m_rear_startup_reg {{
\tu16 reg;
\tu8 source;
\tu8 owner;
}};

static const struct e006m_rear_startup_reg e006m_rear_startup_regs[] = {{
{table}
}};

static_assert(ARRAY_SIZE(e006m_rear_startup_regs) == 714);

typedef int (*e006m_scalar_fn)(void *ctx, u16 reg, u32 *value);

struct e006m_rear_extra_scalar_ops {{
\te006m_scalar_fn steady_singleton;
{extra_struct}
}};

struct e006m_rear_startup_bundle {{
\tstruct e006j_rear_scalar_ops steady;
\tstruct e006m_rear_extra_scalar_ops extra;
}};

static e006m_scalar_fn
e006m_shared_fn_for(const struct e006j_rear_scalar_ops *ops, u8 owner)
{{
\tif (!ops)
\t\treturn NULL;

\tswitch (owner) {{
{shared_switch}
\tdefault:
\t\treturn NULL;
\t}}
}}

static e006m_scalar_fn
e006m_extra_fn_for(const struct e006m_rear_extra_scalar_ops *ops, u8 owner)
{{
\tif (!ops)
\t\treturn NULL;

\tswitch (owner) {{
{extra_switch}
\tdefault:
\t\treturn NULL;
\t}}
}}

static int
e006m_rear_validate_startup_contract(const struct e006m_rear_startup_bundle *b)
{{
\tunsigned int i;
\tunsigned int n_singleton = 0, n_dynamic = 0, n_shared = 0, n_extra = 0;
\tbool saw_period = false;

\tif (!b || !b->extra.steady_singleton)
\t\treturn -EINVAL;
\tif (e006j_rear_validate_scalar_contract(&b->steady))
\t\treturn -EOPNOTSUPP;

\tfor (i = 0; i < ARRAY_SIZE(e006m_rear_startup_regs); i++) {{
\t\tconst struct e006m_rear_startup_reg *r = &e006m_rear_startup_regs[i];

\t\tif (i && e006m_rear_startup_regs[i - 1].reg >= r->reg)
\t\t\treturn -EINVAL;

\t\tswitch (r->source) {{
\t\tcase E006M_SOURCE_STEADY_SINGLETON:
\t\t\tif (r->owner != E006M_OWNER_NONE)
\t\t\t\treturn -EINVAL;
\t\t\tn_singleton++;
\t\t\tbreak;
\t\tcase E006M_SOURCE_STEADY_DYNAMIC:
\t\t\tif (r->owner != E006M_OWNER_NONE)
\t\t\t\treturn -EINVAL;
\t\t\tn_dynamic++;
\t\t\tbreak;
\t\tcase E006M_SOURCE_SHARED_STARTUP:
\t\t\tif (!e006m_shared_fn_for(&b->steady, r->owner))
\t\t\t\treturn -EOPNOTSUPP;
\t\t\tn_shared++;
\t\t\tbreak;
\t\tcase E006M_SOURCE_EXTRA_STARTUP:
\t\t\tif (!e006m_extra_fn_for(&b->extra, r->owner))
\t\t\t\treturn -EOPNOTSUPP;
\t\t\tif (r->owner == E006M_OWNER_VFE680_PERIOD_CFG)
\t\t\t\tsaw_period = true;
\t\t\tn_extra++;
\t\t\tbreak;
\t\tdefault:
\t\t\treturn -EINVAL;
\t\t}}
\t}}

\tif (n_singleton != 468 || n_dynamic != 25 ||
\t    n_shared != 35 || n_extra != 186 || !saw_period)
\t\treturn -EINVAL;

\treturn 0;
}}

static int
e006m_rear_fill_startup_scalar(const struct e006m_rear_startup_bundle *b,
\t\t\t\tvoid *ctx, u16 reg, u32 *value)
{{
\tunsigned int i;
\te006m_scalar_fn fn;

\tif (!b || !value)
\t\treturn -EINVAL;

\tfor (i = 0; i < ARRAY_SIZE(e006m_rear_startup_regs); i++) {{
\t\tconst struct e006m_rear_startup_reg *r = &e006m_rear_startup_regs[i];

\t\tif (r->reg != reg)
\t\t\tcontinue;

\t\tswitch (r->source) {{
\t\tcase E006M_SOURCE_STEADY_SINGLETON:
\t\t\treturn b->extra.steady_singleton(ctx, reg, value);
\t\tcase E006M_SOURCE_STEADY_DYNAMIC:
\t\t\treturn e006j_rear_fill_scalar(&b->steady, ctx, reg, value);
\t\tcase E006M_SOURCE_SHARED_STARTUP:
\t\t\tfn = e006m_shared_fn_for(&b->steady, r->owner);
\t\t\tbreak;
\t\tcase E006M_SOURCE_EXTRA_STARTUP:
\t\t\tfn = e006m_extra_fn_for(&b->extra, r->owner);
\t\t\tbreak;
\t\tdefault:
\t\t\treturn -EINVAL;
\t\t}}
\t\tif (!fn)
\t\t\treturn -EOPNOTSUPP;
\t\treturn fn(ctx, reg, value);
\t}}

\treturn -ENOENT;
}}

struct e006m_rear_startup_binding_static_ops {{
\tint (*validate)(const struct e006m_rear_startup_bundle *b);
\tint (*fill)(const struct e006m_rear_startup_bundle *b,
\t\t    void *ctx, u16 reg, u32 *value);
}};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006m_rear_startup_binding_static_ops
e006m_rear_startup_binding_recipe __used = {{
\t.validate = e006m_rear_validate_startup_contract,
\t.fill = e006m_rear_fill_startup_scalar,
}};
'''
OUT.write_text(text)
print(OUT)
