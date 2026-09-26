#!/usr/bin/env python3
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
SRC = R / "experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"
OUT = HERE / "camss-e006g-rear-materializer.inc"

j = json.loads(SRC.read_text())
steady = {}
for x in j["steady"]["main_variants"]:
    steady.setdefault(x["main_bytes"], x["dmi_shape"])

expected = [0xac8, 0xa98, 0x8f0, 0x658]
assert set(expected) <= set(steady), (expected, sorted(steady))

def kind(reg, sel):
    reg = int(reg, 16) if isinstance(reg, str) else int(reg)
    sel = int(sel)
    if reg == 0x4308 and sel in (1, 2):
        return "E006G_PAYLOAD_LSC"
    if reg == 0x4708 and sel == 1:
        return "E006G_PAYLOAD_LSC_GIC_ALIAS"
    if reg == 0x5a08 and sel == 1:
        return "E006G_PAYLOAD_GTM"
    if reg == 0xbc08 and sel == 1:
        return "E006G_PAYLOAD_BF_ROI"
    if reg == 0xbc08 and sel == 2:
        return "E006G_PAYLOAD_BF_GAMMA"
    return "E006G_PAYLOAD_STABLE"

def arr(name, main):
    ds = steady[main]
    lines = [f"static const struct e006g_rear_dmi_slot e006g_rear_{name}_slots[] = {{"]
    for d in ds:
        reg = int(d["dmi_register_offset"], 16)
        sel = int(d["selector"])
        n = int(d["payload_bytes"])
        lines.append(f"\tE006G_SLOT(0x{reg:04x}, {sel}, {n}, {kind(reg, sel)}),")
    lines.append("};")
    return "\n".join(lines)

arrays = "\n\n".join([
    arr("ac8", 0xac8),
    arr("a98", 0xa98),
    arr("8f0", 0x8f0),
    arr("658", 0x658),
])

text = """/* SPDX-License-Identifier: MIT */
/*
 * E006g compile-only rear RT-CDM materializer contract.
 *
 * Generated from E006a safe structural decode plus E006d/E006f producer
 * classifications. No Windows payload bytes, pointers or IOVAs are present.
 * This include is intentionally retained but unreachable: no probe, stream,
 * ioctl, RT-CDM submit, MMIO write or module-init path references it.
 */

enum e006g_rear_payload_kind {
\tE006G_PAYLOAD_STABLE = 0,
\tE006G_PAYLOAD_LSC,
\tE006G_PAYLOAD_LSC_GIC_ALIAS,
\tE006G_PAYLOAD_GTM,
\tE006G_PAYLOAD_BF_ROI,
\tE006G_PAYLOAD_BF_GAMMA,
};

struct e006g_rear_dmi_slot {
\tu16 dmi_reg;
\tu16 payload_bytes;
\tu8 selector;
\tu8 kind;
};

struct e006g_rear_variant {
\tu16 main_bytes;
\tu8 dmi_count;
\tconst struct e006g_rear_dmi_slot *slots;
};

struct e006g_rear_bl_shape {
\tu16 len[6];
\tu8 count;
};

#define E006G_SLOT(_reg, _sel, _bytes, _kind) \\
\t{ .dmi_reg = (_reg), .selector = (_sel), .payload_bytes = (_bytes), .kind = (_kind) }

""" + arrays + """

static_assert(ARRAY_SIZE(e006g_rear_ac8_slots) == 16);
static_assert(ARRAY_SIZE(e006g_rear_a98_slots) == 15);
static_assert(ARRAY_SIZE(e006g_rear_8f0_slots) == 13);
static_assert(ARRAY_SIZE(e006g_rear_658_slots) == 3);

static const struct e006g_rear_variant e006g_rear_variants[] = {
\t{ .main_bytes = 0x0ac8, .dmi_count = ARRAY_SIZE(e006g_rear_ac8_slots),
\t  .slots = e006g_rear_ac8_slots },
\t{ .main_bytes = 0x0a98, .dmi_count = ARRAY_SIZE(e006g_rear_a98_slots),
\t  .slots = e006g_rear_a98_slots },
\t{ .main_bytes = 0x08f0, .dmi_count = ARRAY_SIZE(e006g_rear_8f0_slots),
\t  .slots = e006g_rear_8f0_slots },
\t{ .main_bytes = 0x0658, .dmi_count = ARRAY_SIZE(e006g_rear_658_slots),
\t  .slots = e006g_rear_658_slots },
};

static const struct e006g_rear_bl_shape e006g_rear_startup_bl[] = {
\t{ .len = { 0x4, 0xf1c, 0x4, 0x3c }, .count = 4 },
\t{ .len = { 0x4, 0xebc, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
\t{ .len = { 0x4, 0xa00, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
\t{ .len = { 0x4, 0x658, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
};

static_assert(ARRAY_SIZE(e006g_rear_startup_bl) == 4);

/*
 * Boundary to accepted producer families:
 *  - lsc: stateful LSC411/Tintless producer;
 *  - gtm: request-time GTM131/TMC producer;
 *  - bfstats: BFStats25 AF-request ROI/gamma producer;
 *  - stable: independently-derived stable payload provider.
 *
 * The kernel skeleton does not implement those algorithms or ingest raw
 * Windows payloads. The explicit contract prevents stale snapshot replay.
 */
struct e006g_rear_producer_ops {
\tint (*lsc)(void *ctx, u8 selector, u8 *dst, size_t bytes);
\tint (*gtm)(void *ctx, u8 *dst, size_t bytes);
\tint (*bfstats)(void *ctx, u8 selector, u8 *dst, size_t bytes);
\tint (*stable)(void *ctx, u16 dmi_reg, u8 selector, u8 *dst, size_t bytes);
};

#define E006G_LSC_BYTES         884
#define E006G_GIC_BYTES         512
#define E006G_GIC_LSC0_OFFSET   558
#define E006G_GIC_LSC0_BYTES    326
#define E006G_GIC_LSC1_BYTES    186
#define E006G_GTM_BYTES         2048
#define E006G_BF_ROI_BYTES      300
#define E006G_BF_GAMMA_BYTES    128

static_assert(E006G_GIC_LSC0_BYTES + E006G_GIC_LSC1_BYTES == E006G_GIC_BYTES);
static_assert(E006G_GIC_LSC0_OFFSET + E006G_GIC_LSC0_BYTES == E006G_LSC_BYTES);

struct e006g_rear_dynamic_payloads {
\tu8 lsc1[E006G_LSC_BYTES];
\tu8 lsc2[E006G_LSC_BYTES];
\tu8 gic_alias[E006G_GIC_BYTES];
\tu8 gtm[E006G_GTM_BYTES];
\tu8 bf_roi[E006G_BF_ROI_BYTES];
\tu8 bf_gamma[E006G_BF_GAMMA_BYTES];
\tbool materialized;
};

struct e006g_rear_slot_buffer {
\tu8 *cpu;
\tsize_t bytes;
};

static int e006g_rear_validate_contract(void)
{
\tunsigned int v, i;

\tfor (v = 0; v < ARRAY_SIZE(e006g_rear_variants); v++) {
\t\tconst struct e006g_rear_variant *variant = &e006g_rear_variants[v];

\t\tif (!variant->slots || !variant->dmi_count || !variant->main_bytes)
\t\t\treturn -EINVAL;
\t\tfor (i = 0; i < variant->dmi_count; i++) {
\t\t\tconst struct e006g_rear_dmi_slot *s = &variant->slots[i];

\t\t\tif (!s->dmi_reg || !s->selector || !s->payload_bytes)
\t\t\t\treturn -EINVAL;
\t\t\tswitch (s->kind) {
\t\t\tcase E006G_PAYLOAD_STABLE:
\t\t\t\tbreak;
\t\t\tcase E006G_PAYLOAD_LSC:
\t\t\t\tif (s->dmi_reg != 0x4308 ||
\t\t\t\t    (s->selector != 1 && s->selector != 2) ||
\t\t\t\t    s->payload_bytes != E006G_LSC_BYTES)
\t\t\t\t\treturn -EINVAL;
\t\t\t\tbreak;
\t\t\tcase E006G_PAYLOAD_LSC_GIC_ALIAS:
\t\t\t\tif (s->dmi_reg != 0x4708 || s->selector != 1 ||
\t\t\t\t    s->payload_bytes != E006G_GIC_BYTES)
\t\t\t\t\treturn -EINVAL;
\t\t\t\tbreak;
\t\t\tcase E006G_PAYLOAD_GTM:
\t\t\t\tif (s->dmi_reg != 0x5a08 || s->selector != 1 ||
\t\t\t\t    s->payload_bytes != E006G_GTM_BYTES)
\t\t\t\t\treturn -EINVAL;
\t\t\t\tbreak;
\t\t\tcase E006G_PAYLOAD_BF_ROI:
\t\t\t\tif (s->dmi_reg != 0xbc08 || s->selector != 1 ||
\t\t\t\t    s->payload_bytes != E006G_BF_ROI_BYTES)
\t\t\t\t\treturn -EINVAL;
\t\t\t\tbreak;
\t\t\tcase E006G_PAYLOAD_BF_GAMMA:
\t\t\t\tif (s->dmi_reg != 0xbc08 || s->selector != 2 ||
\t\t\t\t    s->payload_bytes != E006G_BF_GAMMA_BYTES)
\t\t\t\t\treturn -EINVAL;
\t\t\t\tbreak;
\t\t\tdefault:
\t\t\t\treturn -EINVAL;
\t\t\t}
\t\t}
\t}

\treturn 0;
}

static int e006g_rear_prepare_dynamic(const struct e006g_rear_producer_ops *ops,
\t\t\t\t      void *ctx,
\t\t\t\t      struct e006g_rear_dynamic_payloads *out)
{
\tint ret;

\tif (!ops || !ops->lsc || !ops->gtm || !ops->bfstats || !out ||
\t    out->materialized)
\t\treturn -EINVAL;

\tret = ops->lsc(ctx, 1, out->lsc1, sizeof(out->lsc1));
\tif (ret)
\t\treturn ret;
\tret = ops->lsc(ctx, 2, out->lsc2, sizeof(out->lsc2));
\tif (ret)
\t\tgoto err_zero;

\t/* Exact Surface/Titan680 GIC wire alias proven in E006d. */
\tmemcpy(out->gic_alias, out->lsc1 + E006G_GIC_LSC0_OFFSET,
\t       E006G_GIC_LSC0_BYTES);
\tmemcpy(out->gic_alias + E006G_GIC_LSC0_BYTES, out->lsc2,
\t       E006G_GIC_LSC1_BYTES);

\tret = ops->gtm(ctx, out->gtm, sizeof(out->gtm));
\tif (ret)
\t\tgoto err_zero;
\tret = ops->bfstats(ctx, 1, out->bf_roi, sizeof(out->bf_roi));
\tif (ret)
\t\tgoto err_zero;
\tret = ops->bfstats(ctx, 2, out->bf_gamma, sizeof(out->bf_gamma));
\tif (ret)
\t\tgoto err_zero;

\tout->materialized = true;
\treturn 0;

err_zero:
\tmemzero_explicit(out, sizeof(*out));
\treturn ret;
}

static int e006g_rear_fill_slot(const struct e006g_rear_producer_ops *ops,
\t\t\t\tvoid *ctx,
\t\t\t\tconst struct e006g_rear_dynamic_payloads *dyn,
\t\t\t\tconst struct e006g_rear_dmi_slot *slot,
\t\t\t\tstruct e006g_rear_slot_buffer *out)
{
\tconst u8 *src = NULL;

\tif (!ops || !dyn || !dyn->materialized || !slot || !out || !out->cpu ||
\t    out->bytes != slot->payload_bytes)
\t\treturn -EINVAL;

\tswitch (slot->kind) {
\tcase E006G_PAYLOAD_STABLE:
\t\tif (!ops->stable)
\t\t\treturn -EOPNOTSUPP;
\t\treturn ops->stable(ctx, slot->dmi_reg, slot->selector,
\t\t\t\t   out->cpu, out->bytes);
\tcase E006G_PAYLOAD_LSC:
\t\tsrc = slot->selector == 1 ? dyn->lsc1 : dyn->lsc2;
\t\tbreak;
\tcase E006G_PAYLOAD_LSC_GIC_ALIAS:
\t\tsrc = dyn->gic_alias;
\t\tbreak;
\tcase E006G_PAYLOAD_GTM:
\t\tsrc = dyn->gtm;
\t\tbreak;
\tcase E006G_PAYLOAD_BF_ROI:
\t\tsrc = dyn->bf_roi;
\t\tbreak;
\tcase E006G_PAYLOAD_BF_GAMMA:
\t\tsrc = dyn->bf_gamma;
\t\tbreak;
\tdefault:
\t\treturn -EINVAL;
\t}

\tmemcpy(out->cpu, src, out->bytes);
\treturn 0;
}

static int e006g_rear_steady_bl_shape(const struct e006g_rear_variant *variant,
\t\t\t\t      struct e006g_rear_bl_shape *out)
{
\tif (!variant || !out)
\t\treturn -EINVAL;

\tmemset(out, 0, sizeof(*out));
\tout->len[0] = 0x4;
\tout->len[1] = variant->main_bytes;
\tout->len[2] = 0xc;
\tout->len[3] = 0x4;
\tout->len[4] = 0x10;
\tout->len[5] = 0x14;
\tout->count = 6;
\treturn 0;
}

struct e006g_rear_materializer_static_ops {
\tint (*validate)(void);
\tint (*prepare_dynamic)(const struct e006g_rear_producer_ops *ops,
\t\t\t       void *ctx, struct e006g_rear_dynamic_payloads *out);
\tint (*fill_slot)(const struct e006g_rear_producer_ops *ops, void *ctx,
\t\t\t const struct e006g_rear_dynamic_payloads *dyn,
\t\t\t const struct e006g_rear_dmi_slot *slot,
\t\t\t struct e006g_rear_slot_buffer *out);
\tint (*steady_bl_shape)(const struct e006g_rear_variant *variant,
\t\t\t       struct e006g_rear_bl_shape *out);
};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006g_rear_materializer_static_ops
e006g_rear_materializer_recipe __used = {
\t.validate = e006g_rear_validate_contract,
\t.prepare_dynamic = e006g_rear_prepare_dynamic,
\t.fill_slot = e006g_rear_fill_slot,
\t.steady_bl_shape = e006g_rear_steady_bl_shape,
};
"""
OUT.write_text(text)
print(OUT)
