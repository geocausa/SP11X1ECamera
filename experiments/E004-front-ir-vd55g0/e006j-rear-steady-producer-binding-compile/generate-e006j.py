#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
R=D.parents[2]
SRC=R/"experiments/E004-front-ir-vd55g0/e006h-rear-steady-main-symbolic-recipe/STEADY-SYMBOLIC-RECIPE.json"
OUT=D/"camss-e006j-rear-register-bindings.inc"

j=json.loads(SRC.read_text())
owners={}
for v in j["variants"].values():
    for c in v["commands"]:
        if c["command"]!="REG_CONT":
            continue
        for x in c["values"]:
            if x["source"]!="DYNAMIC_PROVIDER":
                continue
            reg=int(x["register_offset"],16)
            prod=x["producer"]
            old=owners.setdefault(reg,prod)
            assert old==prod,(hex(reg),old,prod)

assert not j["unresolved_dynamic_register_owners"]
expected={
  0x3b70:"DEMUX_BLS",0x3b74:"DEMUX_BLS",
  0x3d58:"PDPC",0x3d5c:"PDPC",0x3d7c:"PDPC",0x3d84:"PDPC",
  0x4358:"LSC",0x435c:"LSC",
  0x456c:"WB",
  0x4758:"GIC",0x475c:"GIC",
  0x4958:"BPC_ABF",0x495c:"BPC_ABF",0x49b8:"BPC_ABF",0x49bc:"BPC_ABF",
  0x5a58:"GTM",0x5a5c:"GTM",
  0x5f58:"GAMMA",0x5f5c:"GAMMA",
  0xa058:"DSX",0xa05c:"DSX",0xa258:"DSX",0xa25c:"DSX",
  0xbc58:"BFSTATS25",0xbc5c:"BFSTATS25",
}
assert owners==expected,(owners,expected)

enum_order=["DEMUX_BLS","PDPC","LSC","WB","GIC","BPC_ABF","GTM","GAMMA","DSX","BFSTATS25"]
enum_lines=["\tE006J_PRODUCER_"+x+"," for x in enum_order]
map_lines=[
    f"\t{{ .reg = 0x{reg:04x}, .producer = E006J_PRODUCER_{prod} }},"
    for reg,prod in sorted(owners.items())
]

text="""/* SPDX-License-Identifier: MIT */
/*
 * E006j compile-only rear dynamic-register producer binding.
 *
 * Generated exclusively from the safe E006h symbolic recipe and E006i
 * ownership closure. No raw Windows command bytes, addresses, pointers or
 * observed dynamic register values are embedded.
 *
 * This file is intentionally unreachable at runtime.
 */

enum e006j_rear_producer {
"""+"\n".join(enum_lines)+"""
\tE006J_PRODUCER_COUNT,
};

struct e006j_rear_reg_owner {
\tu16 reg;
\tu8 producer;
};

static const struct e006j_rear_reg_owner e006j_rear_reg_owners[] = {
"""+"\n".join(map_lines)+"""
};

static_assert(ARRAY_SIZE(e006j_rear_reg_owners) == 25);

typedef int (*e006j_scalar_fn)(void *ctx, u16 reg, u32 *value);

struct e006j_rear_scalar_ops {
\te006j_scalar_fn demux_bls;
\te006j_scalar_fn pdpc;
\te006j_scalar_fn lsc;
\te006j_scalar_fn wb;
\te006j_scalar_fn gic;
\te006j_scalar_fn bpc_abf;
\te006j_scalar_fn gtm;
\te006j_scalar_fn gamma;
\te006j_scalar_fn dsx;
\te006j_scalar_fn bfstats25;
};

/*
 * E006g owns DMI/payload production. E006j adds the steady dynamic scalar
 * register side. Keeping them in one bundle makes omission of BPC/ABF411's
 * rear-only 0x49B8/0x49BC words visible to the compiler contract.
 */
struct e006j_rear_producer_bundle {
\tstruct e006g_rear_producer_ops payload;
\tstruct e006j_rear_scalar_ops scalar;
};

static e006j_scalar_fn
e006j_rear_scalar_fn_for(const struct e006j_rear_scalar_ops *ops, u8 producer)
{
\tif (!ops)
\t\treturn NULL;

\tswitch (producer) {
\tcase E006J_PRODUCER_DEMUX_BLS:
\t\treturn ops->demux_bls;
\tcase E006J_PRODUCER_PDPC:
\t\treturn ops->pdpc;
\tcase E006J_PRODUCER_LSC:
\t\treturn ops->lsc;
\tcase E006J_PRODUCER_WB:
\t\treturn ops->wb;
\tcase E006J_PRODUCER_GIC:
\t\treturn ops->gic;
\tcase E006J_PRODUCER_BPC_ABF:
\t\treturn ops->bpc_abf;
\tcase E006J_PRODUCER_GTM:
\t\treturn ops->gtm;
\tcase E006J_PRODUCER_GAMMA:
\t\treturn ops->gamma;
\tcase E006J_PRODUCER_DSX:
\t\treturn ops->dsx;
\tcase E006J_PRODUCER_BFSTATS25:
\t\treturn ops->bfstats25;
\tdefault:
\t\treturn NULL;
\t}
}

static int
e006j_rear_validate_scalar_contract(const struct e006j_rear_scalar_ops *ops)
{
\tunsigned int i;
\tbool saw_49b8 = false;
\tbool saw_49bc = false;

\tif (!ops)
\t\treturn -EINVAL;

\tfor (i = 0; i < ARRAY_SIZE(e006j_rear_reg_owners); i++) {
\t\tconst struct e006j_rear_reg_owner *o = &e006j_rear_reg_owners[i];

\t\tif (i && e006j_rear_reg_owners[i - 1].reg >= o->reg)
\t\t\treturn -EINVAL;
\t\tif (!e006j_rear_scalar_fn_for(ops, o->producer))
\t\t\treturn -EOPNOTSUPP;
\t\tif (o->reg == 0x49b8) {
\t\t\tif (o->producer != E006J_PRODUCER_BPC_ABF)
\t\t\t\treturn -EINVAL;
\t\t\tsaw_49b8 = true;
\t\t}
\t\tif (o->reg == 0x49bc) {
\t\t\tif (o->producer != E006J_PRODUCER_BPC_ABF)
\t\t\t\treturn -EINVAL;
\t\t\tsaw_49bc = true;
\t\t}
\t}

\treturn saw_49b8 && saw_49bc ? 0 : -EINVAL;
}

static int
e006j_rear_fill_scalar(const struct e006j_rear_scalar_ops *ops,
\t\t\tvoid *ctx, u16 reg, u32 *value)
{
\tunsigned int i;

\tif (!ops || !value)
\t\treturn -EINVAL;

\tfor (i = 0; i < ARRAY_SIZE(e006j_rear_reg_owners); i++) {
\t\tconst struct e006j_rear_reg_owner *o = &e006j_rear_reg_owners[i];
\t\te006j_scalar_fn fn;

\t\tif (o->reg != reg)
\t\t\tcontinue;
\t\tfn = e006j_rear_scalar_fn_for(ops, o->producer);
\t\tif (!fn)
\t\t\treturn -EOPNOTSUPP;
\t\treturn fn(ctx, reg, value);
\t}

\treturn -ENOENT;
}

struct e006j_rear_binding_static_ops {
\tint (*validate_scalar)(const struct e006j_rear_scalar_ops *ops);
\tint (*fill_scalar)(const struct e006j_rear_scalar_ops *ops,
\t\t\t   void *ctx, u16 reg, u32 *value);
};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006j_rear_binding_static_ops
e006j_rear_binding_recipe __used = {
\t.validate_scalar = e006j_rear_validate_scalar_contract,
\t.fill_scalar = e006j_rear_fill_scalar,
};
"""
OUT.write_text(text)
print("E006J_GENERATE_PASS")
print("dynamic_registers",len(owners))
print("producer_families",len(enum_order))
print("bpc_abf_regs",[hex(x) for x in sorted(r for r,p in owners.items() if p=="BPC_ABF")])
