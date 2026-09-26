#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
R=D.parents[2]
H=R/"experiments/E004-front-ir-vd55g0/e006h-rear-steady-main-symbolic-recipe/STEADY-SYMBOLIC-RECIPE.json"
L=R/"experiments/E004-front-ir-vd55g0/e006l-rear-startup-register-ownership/STARTUP-REGISTER-OWNER-MAP.json"
OUT=D/"camss-e006o-rear-steady-singletons.inc"

h=json.loads(H.read_text())
l=json.loads(L.read_text())
want={int(x,16) for x in l["reusable_steady_singleton_offsets"]}

seen={}
for v in h["variants"].values():
    for c in v["commands"]:
        if c["command"]!="REG_CONT":
            continue
        for x in c["values"]:
            if x["source"]!="STABLE_OBSERVED":
                continue
            reg=int(x["register_offset"],16)
            val=int(x["value"],16)
            seen.setdefault(reg,set()).add(val)

assert len(want)==468
assert all(len(seen.get(r,set()))==1 for r in want)
rows=[(r,next(iter(seen[r]))) for r in sorted(want)]

body="\n".join(
    f"\t{{ .reg = 0x{reg:04x}, .value = 0x{value:08x} }},"
    for reg,value in rows
)

text=f'''/* SPDX-License-Identifier: MIT */
/*
 * E006o compile-only rear steady-singleton provider.
 *
 * Generated solely from the committed E006h safe symbolic recipe and the
 * E006l startup-reuse proof. These values are already committed derived
 * hardware-register observations; no private Windows buffer is read here.
 * No runtime caller is wired.
 */

struct e006o_rear_singleton {{
\tu16 reg;
\tu32 value;
}};

static const struct e006o_rear_singleton e006o_rear_singletons[] = {{
{body}
}};

static_assert(ARRAY_SIZE(e006o_rear_singletons) == 468);

static int
e006o_rear_steady_singleton_lookup(void *ctx, u16 reg, u32 *value)
{{
\tunsigned int lo = 0;
\tunsigned int hi = ARRAY_SIZE(e006o_rear_singletons);

\t(void)ctx;
\tif (!value)
\t\treturn -EINVAL;

\twhile (lo < hi) {{
\t\tunsigned int mid = lo + (hi - lo) / 2;
\t\tconst struct e006o_rear_singleton *s = &e006o_rear_singletons[mid];

\t\tif (reg < s->reg) {{
\t\t\thi = mid;
\t\t}} else if (reg > s->reg) {{
\t\t\tlo = mid + 1;
\t\t}} else {{
\t\t\t*value = s->value;
\t\t\treturn 0;
\t\t}}
\t}}

\treturn -ENOENT;
}}

/*
 * Type-check against E006m's startup singleton callback contract and retain
 * the provider for compile/link inspection only.
 */
static e006m_scalar_fn e006o_rear_steady_singleton_recipe __used =
\te006o_rear_steady_singleton_lookup;
'''
OUT.write_text(text)
print(OUT)
