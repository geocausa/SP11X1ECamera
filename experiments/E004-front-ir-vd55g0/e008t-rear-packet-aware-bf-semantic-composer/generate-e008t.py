#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNING = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
TUNING_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
DEC = REPO / "experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py"

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def q14(v: float) -> int:
    return int(round(v * 16384.0))

dll = DLL.read_bytes()
assert sha(dll) == DLL_SHA
tuning = TUNING.read_bytes()
assert sha(tuning) == TUNING_SHA
D = load_module(DEC, "e008t_chromatix")
h = D.parse_header(tuning)
assert h["module_name"] == "com.surface.tuned.rfc_ov13858"
recs, _ = D.parse_symbol_table(tuning, h["sections"][0], h["sections"][1])
obj = h["sections"][1]

# Normal rear gamma preset 0.
gamma_raw = D.data_bytes(tuning, obj, recs[0x1BC1])
gamma_words = list(struct.unpack("<66I", gamma_raw))
assert gamma_words[0] == 1 and gamma_words[33] == 1
gamma = gamma_words[1:33]
assert len(gamma) == 32 and max(gamma) <= 0x3fff

# Normal rear IIR block 1, Titan680 register ordering from E008q/r.
filter_raw = D.data_bytes(tuning, obj, recs[0x1BC4])
raw = filter_raw[52:104]
u = struct.unpack("<13I", raw)
f = struct.unpack("<13f", raw)
assert u[0] == 1
qb = [q14(x) for x in f[1:11]]
qa = [qb[i] for i in [0, 1, 2, 7, 3, 4, 5, 6, 8, 9]]

# Normal coring record 0.
coring_raw = D.data_bytes(tuning, obj, recs[0x1BC9])
c0 = list(struct.unpack("<20I", coring_raw[:80]))
assert c0[0] == 1
normal_lanes = c0[1:18]
normal_scalar = c0[18]
assert len(normal_lanes) == 17

# All normal configure modes use shifts 3/3.
configure = D.data_bytes(tuning, obj, recs[0x1BBF])
cfg = [struct.unpack("<12I", configure[i*48:(i+1)*48]) for i in range(4)]
assert [(x[7], x[11]) for x in cfg] == [(3, 3)] * 4

# HAF seed policy: centered 25% window, 5x5, zero overlap.
haf = D.data_bytes(tuning, obj, recs[0xB6])
haf_window = struct.unpack_from("<2f", haf, 0x28)
haf_grid = struct.unpack_from("<2f", haf, 0x34)
haf_overlap = struct.unpack_from("<2f", haf, 0x3C)
assert all(abs(x - 0.25) < 1e-6 for x in haf_window)
assert all(abs(x - 0.2) < 1e-6 for x in haf_grid)
assert all(abs(x) < 1e-6 for x in haf_overlap)

# Packet0 IFE hardcode float block at RVA 0x763788.
block_rva = 0x763788
block_off = 0x400 + (block_rva - 0x1000)
hard = struct.unpack("<20f", dll[block_off:block_off + 80])
C = [q14(x) for x in hard]

# H1 semantic slots + Titan A permutation.
h_sem = [C[0], 0, C[1], C[6], C[7], C[2], 0, C[3], C[4], C[5]]
hard_a = [h_sem[i] for i in [0, 1, 2, 7, 3, 4, 5, 6, 8, 9]]

# V semantic slots are sourced by the final hardcode filter object.
hard_b = [C[16], C[17], C[16], C[18], C[19], C[2], 0, C[3], C[4], C[5]]

# Immediate values in IFENode hardcode helper RVA 0x7635A8.
hard_fir = [-1, -2, -1, 1, 5, 8, 10, 8, 5, 1, -1, -2, -1]
hard_lanes = [0] + [16] * 16
hard_scalar = 0x10000

def carr(name: str, ctype: str, vals) -> str:
    body = ", ".join(str(int(v)) for v in vals)
    return f"static const {ctype} {name}[] = {{ {body} }};\n"

inc = """/* SPDX-License-Identifier: MIT */
/*
 * E008t rear packet-aware BF semantic composer.
 *
 * Generated only from the pinned DeviceMFT and rear tuning sources.
 * No captured Windows register words or DMI payload bytes are embedded.
 *
 * Scope: populate the BF semantic seed inside E008o's already-isolated
 * per-packet states. BFStats25 ROI validation/adjustment and final DMI parity
 * remain a later gate. No runtime caller is introduced here.
 */

#define E008T_REAR_STARTUP_PACKETS 4
#define E008T_REAR_GRID_COUNT 5

"""
inc += carr("e008t_normal_gamma", "u16", gamma)
inc += carr("e008t_normal_iir_a", "s16", qa)
inc += carr("e008t_normal_iir_b", "s16", qb)
inc += carr("e008t_normal_coring_lanes", "u8", normal_lanes)
inc += carr("e008t_hardcode_fir", "s8", hard_fir)
inc += carr("e008t_hardcode_iir_a", "s16", hard_a)
inc += carr("e008t_hardcode_iir_b", "s16", hard_b)
inc += carr("e008t_hardcode_coring_lanes", "u8", hard_lanes)
inc += f"""
#define E008T_NORMAL_CORING_SCALAR {normal_scalar}U
#define E008T_HARDCODE_CORING_SCALAR {hard_scalar}U

static struct e007e_bf_dmi_state *
e008t_rear_bf_dmi(struct e007v_rear_dmi_state *s)
{{
    if (!s)
        return NULL;
    return &s->dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
}}

static int
e008t_rear_seed_roi_common(struct e007e_bf_dmi_state *d,
                           u32 left, u32 top, u32 cell_w, u32 cell_h)
{{
    unsigned int row, col, idx = 0;

    if (!d || !cell_w || !cell_h)
        return -EINVAL;
    if (cell_w - 1 > 0x0fff || cell_h - 1 > 0x1fff)
        return -ERANGE;

    for (row = 0; row < E008T_REAR_GRID_COUNT; row++) {{
        for (col = 0; col < E008T_REAR_GRID_COUNT; col++) {{
            struct e007e_bf_roi *r = &d->roi[idx];
            u32 x = left + col * cell_w;
            u32 y = top + row * cell_h;

            if (x > 0x1fff || y > 0x3fff)
                return -ERANGE;
            r->left = x;
            r->top = y;
            r->width = cell_w - 1;
            r->height = cell_h - 1;
            r->rid = idx;
            r->oid = idx;
            r->merge = false;
            r->type = false;
            idx++;
        }}
    }}
    d->roi_count = idx;
    return idx == E007E_BF_ROI_COUNT ? 0 : -EINVAL;
}}

static int
e008t_rear_seed_packet0_roi(struct e007e_bf_dmi_state *d,
                            u32 camif_w, u32 camif_h)
{{
    u32 cell_w, cell_h, left, top;

    if (!d || !camif_w || !camif_h)
        return -EINVAL;

    /* IFENode::hardcode BF ROI helper RVA 0x7637D8. */
    cell_w = ((camif_w * 25U) / 500U) & ~1U;
    cell_h = ((camif_h * 25U) / 500U) & ~1U;
    if (!cell_w || !cell_h ||
        camif_w < cell_w * E008T_REAR_GRID_COUNT ||
        camif_h < cell_h * E008T_REAR_GRID_COUNT)
        return -ERANGE;

    left = (camif_w - cell_w * E008T_REAR_GRID_COUNT) >> 1;
    top = (camif_h - cell_h * E008T_REAR_GRID_COUNT) >> 1;

    /* The hardcode helper forces each generated origin even. */
    left &= ~1U;
    top &= ~1U;
    return e008t_rear_seed_roi_common(d, left, top, cell_w, cell_h);
}}

static int
e008t_rear_seed_normal_roi(struct e007e_bf_dmi_state *d,
                           u32 camif_w, u32 camif_h)
{{
    u32 roi_w, roi_h, left, top, cell_w, cell_h;

    if (!d || !camif_w || !camif_h)
        return -EINVAL;

    /* AF default window = centered 25%; HAF grid = 5x5, zero overlap. */
    roi_w = camif_w / 4U;
    roi_h = camif_h / 4U;
    if (!roi_w || !roi_h)
        return -ERANGE;
    left = (camif_w - roi_w) >> 1;
    top = (camif_h - roi_h) >> 1;
    cell_w = roi_w / E008T_REAR_GRID_COUNT;
    cell_h = roi_h / E008T_REAR_GRID_COUNT;

    return e008t_rear_seed_roi_common(d, left, top, cell_w, cell_h);
}}

static void
e008t_rear_seed_common_registers(struct e007b_bfstats25_calc_state *b,
                                 u8 packet)
{{
    memset(b, 0, sizeof(*b));
    b->dmi_lut_bank = packet & 1;
    b->module_lut_bank = packet & 1;
    b->luma_select = 0;
    b->luma_conversion_enable = 0;
    b->scale_enable = 0;
}}

static int
e008t_rear_seed_packet_bf(struct e008o_rear_packet_state *p,
                          u8 packet, u32 camif_w, u32 camif_h)
{{
    struct e007b_bfstats25_calc_state *b;
    struct e007e_bf_dmi_state *d;
    int ret;

    if (!p || packet >= E008T_REAR_STARTUP_PACKETS)
        return -EINVAL;

    b = &p->regs.bfstats;
    d = e008t_rear_bf_dmi(&p->dmi);
    if (!d)
        return -EINVAL;

    e008t_rear_seed_common_registers(b, packet);
    memset(d, 0, sizeof(*d));

    if (packet == 0) {{
        b->gamma_lut_enable = 0;
        b->filter0_enable = 1;
        b->filter1_enable = 1;
        b->filter3_enable = 1;
        memcpy(b->signed6, e008t_hardcode_fir, sizeof(b->signed6));
        memcpy(b->quant16_a, e008t_hardcode_iir_a, sizeof(b->quant16_a));
        memcpy(b->quant16_b, e008t_hardcode_iir_b, sizeof(b->quant16_b));
        b->signed4[0] = -3;
        b->signed4[1] = 0;
        b->tail_scalar17[0] = E008T_HARDCODE_CORING_SCALAR;
        b->tail_scalar17[1] = E008T_HARDCODE_CORING_SCALAR;
        memcpy(b->tail_lane5[0], e008t_hardcode_coring_lanes,
               sizeof(b->tail_lane5[0]));
        memcpy(b->tail_lane5[1], e008t_hardcode_coring_lanes,
               sizeof(b->tail_lane5[1]));
        d->gamma_valid = false;
        ret = e008t_rear_seed_packet0_roi(d, camif_w, camif_h);
    }} else {{
        b->gamma_lut_enable = 1;
        b->filter0_enable = 0;
        b->filter1_enable = 1;
        b->filter3_enable = 1;
        memcpy(b->quant16_a, e008t_normal_iir_a, sizeof(b->quant16_a));
        memcpy(b->quant16_b, e008t_normal_iir_b, sizeof(b->quant16_b));
        b->signed4[0] = 3;
        b->signed4[1] = 3;
        b->tail_scalar17[0] = E008T_NORMAL_CORING_SCALAR;
        b->tail_scalar17[1] = E008T_NORMAL_CORING_SCALAR;
        memcpy(b->tail_lane5[0], e008t_normal_coring_lanes,
               sizeof(b->tail_lane5[0]));
        memcpy(b->tail_lane5[1], e008t_normal_coring_lanes,
               sizeof(b->tail_lane5[1]));
        memcpy(d->gamma, e008t_normal_gamma, sizeof(d->gamma));
        d->gamma_valid = true;
        ret = e008t_rear_seed_normal_roi(d, camif_w, camif_h);
    }}

    if (ret)
        return ret;
    return e007b_bfstats25_validate(b);
}}

static int
e008t_rear_seed_bootstrap_bf(struct e008o_rear_bootstrap *s,
                             u32 camif_w, u32 camif_h)
{{
    unsigned int packet;
    int ret;

    if (!s || !s->initialized || s->next_packet)
        return -EINVAL;

    for (packet = 0; packet < E008T_REAR_STARTUP_PACKETS; packet++) {{
        ret = e008t_rear_seed_packet_bf(&s->packet[packet], packet,
                                        camif_w, camif_h);
        if (ret)
            return ret;
    }}
    return 0;
}}

struct e008t_rear_bf_semantic_static_ops {{
    int (*seed)(struct e008o_rear_bootstrap *s, u32 camif_w, u32 camif_h);
}};

static const struct e008t_rear_bf_semantic_static_ops
e008t_rear_bf_semantic_recipe __used = {{
    .seed = e008t_rear_seed_bootstrap_bf,
}};
"""

(HERE / "camss-vfe-e008t-rear-bf-semantic.inc").write_text(inc)

safe = {
    "schema": "E008T-source-authority-v1",
    "status": "PASS",
    "parent": "E008s",
    "pinned_dll_sha256": DLL_SHA,
    "pinned_tuning_sha256": TUNING_SHA,
    "packet0": {
        "producer": "IFENode_hardcode",
        "fir_enabled": True,
        "iir_enabled": [True, True],
        "iir_shifts": [-3, 0],
        "gamma_valid": False,
        "roi_seed": "centered_5x5_IFE_hardcode"
    },
    "packet1_plus": {
        "producer": "AF_BAF_default",
        "fir_enabled": False,
        "iir_enabled": [True, True],
        "iir_shifts": [3, 3],
        "gamma_valid": True,
        "roi_seed": "centered_25pct_5x5_zero_overlap"
    },
    "bank_sequence": [0, 1, 0, 1],
    "normal_gamma_samples": len(gamma),
    "normal_coring_lanes": len(normal_lanes),
    "hardcode_fir_taps": len(hard_fir),
    "hardcode_float_constants": len(hard),
    "final_bfstats_roi_adjustment_applied": False,
    "final_selector1_dmi_parity_claimed": False,
    "captured_windows_register_values_embedded": False,
    "captured_windows_dmi_bytes_embedded": False,
    "private_decompilation_embedded": False,
    "runtime_actions_performed": False
}
(HERE / "SAFE-SOURCE-AUTHORITY.json").write_text(
    json.dumps(safe, indent=2, sort_keys=True) + "\n"
)
print("E008T_GENERATE_PASS packet0=hardcode packet1plus=normal roi=semantic_seed_only")
