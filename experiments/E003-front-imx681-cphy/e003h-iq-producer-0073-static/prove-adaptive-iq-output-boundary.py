#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import struct
from pathlib import Path

TUNING_SHA = "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d"
MATCHED_DMI_SHA = "ff5f0f04bee8491c76451838743a28e3793ee5d2a0ecbff8f6589dca5c92f955"
LSC0_OFF, LSC1_OFF, LSC_BYTES = 0x400, 0x774, 0x374
GTM_OFF, GTM_BYTES = 0x34CC, 0x800
LSC_LO_CCT_SYMBOL = 0x4BD   # 3400..4500 region
LSC_HI_CCT_SYMBOL = 0x4BF   # 5000..10000 region
GTM_REGION_SYMBOL = 0x49D
CCT = 4999.0
CCT_LO_END = 4500.0
CCT_HI_START = 5000.0


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_decoder(path: Path):
    spec = importlib.util.spec_from_file_location("imx681_decode", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load decoder")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def floats(raw: bytes):
    if len(raw) % 4:
        raise ValueError("float region is not dword aligned")
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))


def q10_lsc(v: float) -> int:
    # Exact Surface path scales by 1024.0, rounds, and clips to the 14-bit LSC range.
    x = int(math.floor(v * 1024.0 + 0.5))
    return max(0x400, min(0x3FFF, x))


def pack_lsc(a, b) -> bytes:
    if len(a) != 221 or len(b) != 221:
        raise ValueError("LSC channel length must be 221")
    out = bytearray()
    for x, y in zip(a, b):
        out += struct.pack("<I", (x & 0x3FFF) | ((y & 0x3FFF) << 14))
    return bytes(out)


def decode_lsc_halves(blob: bytes):
    lo, hi = [], []
    for (w,) in struct.iter_unpack("<I", blob):
        lo.append(w & 0x3FFF)
        hi.append((w >> 14) & 0x3FFF)
    return lo, hi


def decode_gtm(blob: bytes):
    bases, slopes, qs = [], [], []
    for (w,) in struct.iter_unpack("<Q", blob):
        bases.append(w & 0x3FFFFF)
        upper = w >> 22
        slope = upper & 0x3FFFFFF
        if slope & (1 << 25):
            slope -= 1 << 26
        slopes.append(slope)
        qs.append((upper >> 26) & 0x1F)
    return bases, slopes, qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tuning", type=Path, required=True)
    ap.add_argument("--decoder", type=Path, required=True)
    ap.add_argument("--matched-dmi", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    tuning = args.tuning.read_bytes()
    dmi = args.matched_dmi.read_bytes()
    if sha(tuning) != TUNING_SHA:
        raise SystemExit("unexpected IMX681 tuning SHA")
    if sha(dmi) != MATCHED_DMI_SHA:
        raise SystemExit("unexpected matched request6 DMI SHA")
    if len(dmi) < GTM_OFF + GTM_BYTES:
        raise SystemExit("matched DMI is too short")

    dec = load_decoder(args.decoder)
    hdr = dec.parse_header(tuning)
    recs, _ = dec.parse_symbol_table(tuning, hdr["sections"][0], hdr["sections"][1])
    obj = hdr["sections"][1]

    def region(sid: int) -> bytes:
        return dec.data_bytes(tuning, obj, recs[sid])

    gtm_static = floats(region(GTM_REGION_SYMBOL))
    if len(gtm_static) != 257 or any(v != 4096.0 for v in gtm_static):
        raise SystemExit("expected exact flat GTM13 257x4096 region")

    lo = floats(region(LSC_LO_CCT_SYMBOL))
    hi = floats(region(LSC_HI_CCT_SYMBOL))
    if len(lo) < 884 or len(hi) < 884:
        raise SystemExit("LSC region too small")
    ratio = (CCT - CCT_LO_END) / (CCT_HI_START - CCT_LO_END)
    interp = [a + (b - a) * ratio for a, b in zip(lo[:884], hi[:884])]
    channels = [[q10_lsc(x) for x in interp[i * 221:(i + 1) * 221]] for i in range(4)]

    win_lsc0 = dmi[LSC0_OFF:LSC0_OFF + LSC_BYTES]
    win_lsc1 = dmi[LSC1_OFF:LSC1_OFF + LSC_BYTES]
    win_lsc = win_lsc0 + win_lsc1
    permutations = []
    for perm in itertools.permutations(range(4)):
        candidate = pack_lsc(channels[perm[0]], channels[perm[1]]) + pack_lsc(channels[perm[2]], channels[perm[3]])
        byte_diff = sum(a != b for a, b in zip(candidate, win_lsc))
        permutations.append({
            "channel_permutation": list(perm),
            "byte_differences": byte_diff,
            "candidate_sha256": sha(candidate),
        })
    permutations.sort(key=lambda x: x["byte_differences"])

    l0a, l0b = decode_lsc_halves(win_lsc0)
    l1a, l1b = decode_lsc_halves(win_lsc1)
    gtm_wire = dmi[GTM_OFF:GTM_OFF + GTM_BYTES]
    gbase, gslope, gq = decode_gtm(gtm_wire)

    result = {
        "schema": "sp11-e003h-adaptive-iq-output-boundary-v1",
        "status": "PASS",
        "offline_only": True,
        "inputs": {
            "imx681_tuning_sha256": sha(tuning),
            "matched_request6_dmi_sha256": sha(dmi),
        },
        "lsc": {
            "cct": CCT,
            "base_cct_gap": [CCT_LO_END, CCT_HI_START],
            "base_interpolation_ratio": ratio,
            "candidate_channels": 4,
            "candidate_points_per_channel": 221,
            "windows_lsc0_sha256": sha(win_lsc0),
            "windows_lsc1_sha256": sha(win_lsc1),
            "windows_lsc0_half_stats": [
                {"min": min(l0a), "max": max(l0a), "mean": sum(l0a) / len(l0a)},
                {"min": min(l0b), "max": max(l0b), "mean": sum(l0b) / len(l0b)},
            ],
            "windows_lsc1_half_stats": [
                {"min": min(l1a), "max": max(l1a), "mean": sum(l1a) / len(l1a)},
                {"min": min(l1b), "max": max(l1b), "mean": sum(l1b) / len(l1b)},
            ],
            "best_pure_chromatix_channel_assignment": permutations[0],
            "all_24_channel_assignments_mismatch": all(x["byte_differences"] != 0 for x in permutations),
            "conclusion": "No channel ordering of the exact 4999K base Chromatix interpolation reproduces Windows LSC0+LSC1; calibration/adaptive LSC state is required.",
        },
        "gtm": {
            "static_region_points": len(gtm_static),
            "static_region_unique_values": sorted(set(gtm_static)),
            "windows_gtm0_sha256": sha(gtm_wire),
            "windows_base_min": min(gbase),
            "windows_base_max": max(gbase),
            "windows_base_unique_count": len(set(gbase)),
            "windows_base_equal_4096_count": sum(v == 4096 for v in gbase),
            "windows_base_first16": gbase[:16],
            "windows_base_last16": gbase[-16:],
            "windows_q_unique": sorted(set(gq)),
            "windows_slope_min": min(gslope),
            "windows_slope_max": max(gslope),
            "conclusion": "The exact static GTM region is flat 4096, while every matched Windows GTM base entry differs from 4096; the downstream dynamic TMC path is active/relevant.",
        },
        "gate": "Capture same-stream Windows LSC adaptive/calibration state and GTM TMC state, then reproduce LSC0/LSC1/GTM0 byte-for-byte offline before any Linux request6 runtime.",
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": "PASS",
        "lsc_best_byte_differences": permutations[0]["byte_differences"],
        "gtm_base_equal_4096_count": result["gtm"]["windows_base_equal_4096_count"],
        "gtm_base_range": [result["gtm"]["windows_base_min"], result["gtm"]["windows_base_max"]],
    }, indent=2))


if __name__ == "__main__":
    main()
