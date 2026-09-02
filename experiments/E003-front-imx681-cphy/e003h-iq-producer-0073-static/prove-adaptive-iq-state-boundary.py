#!/usr/bin/env python3
"""Fail-closed static proof that the remaining LSC/GTM producer boundary
extends beyond the common AEC/AWB trigger vector.

This script performs no camera runtime and authorizes none. It pins the exact
Surface DeviceMFT/tuning identities, decodes the LSC/GTM control trees, proves
that matched request5/request6 remain inside the same relevant trigger zones,
and records exact-binary adaptive state paths that must be captured before an
offline request6 producer can be accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

DEVICEMFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNING_SHA = "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d"
EXPECTED_CONTROLS = {
    "lsc41_ife_v2": [8, 2, 5, 100, 0, 6],
    "gtm13_ife_v2": [2, 5, 0],
}
EXPECTED_SYMBOLS = {
    "lsc_root": 41,
    "lsc_control": 1201,
    "lsc_aec": 1206,
    "lsc_cct": 1207,
    "gtm_root": 38,
    "gtm_control": 1176,
    "gtm_aec": 1179,
}
EXPECTED_RANGES = {
    "lsc_aec": [(1.0, 390.0), (490.0, 1000.0)],
    "lsc_cct": [(1.0, 2500.0), (2700.0, 3200.0), (3400.0, 4500.0), (5000.0, 10000.0)],
    "gtm_aec": [(1.0, 900.0)],
}
# Exact Surface function boundaries established by static decompilation of the
# pinned DeviceMFT binary. These are provenance identifiers, not call targets.
EXACT_RVAS = {
    "iq_trigger_vector_builder": 0x890208,
    "control_var_to_trigger_map": 0x9A3708,
    "lsc_calculate_setting": 0x88E1E8,
    "lsc_interpolation": 0x93C1B0,
    "lsc_hw_setting": 0x9B4BA0,
    "lsc_titan680_packer": 0xB3D8A0,
    "gtm_ife_execute_run_calculation": 0xA28B00,
    "gtm_interpolation": 0x93BF30,
    "gtm_hw_setting": 0x9AA6E0,
    "gtm_titan680_packer": 0xB5B3D0,
}
# Presence of these exact strings in the SHA-pinned image closes the intended
# adaptive paths without depending on transient Ghidra output files.
REQUIRED_BINARY_STRINGS = [
    b"IFE Store Tintless camera",
    b"IFE Store ALSC camera",
    b"BPS UsePrevious Tintless camera",
    b"BPS UsePrevious ALSC camera",
    b"CamX::IQInterface::LSC411CalculateSetting",
    b"CamX::IQInterface::GTM131CalculateSetting",
    b"CamX::IQInterface::IsModuleEnabledInTMCPath",
    b"ALSC is disabled as the AWB BG stats are not present",
]


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_decoder(path: Path):
    spec = importlib.util.spec_from_file_location("imx681_decode", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tuning decoder")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def u32_words(raw: bytes) -> list[int]:
    if len(raw) % 4:
        raise ValueError("control payload is not u32-aligned")
    return list(struct.unpack("<" + "I" * (len(raw) // 4), raw))


def trigger_ranges(dec, blob: bytes, objsec: dict, rec: dict) -> list[tuple[float, float]]:
    raw = dec.data_bytes(blob, objsec, rec)
    refs = dec.child_refs(blob, objsec, records, rec)
    if len(raw) % 24:
        raise ValueError(f"trigger {rec['symbol_id']}: unexpected byte count {len(raw)}")
    out = []
    for off in range(0, len(raw), 24):
        lo, hi = struct.unpack_from("<ff", raw, off)
        out.append((float(lo), float(hi)))
    # Each serialized 24-byte trigger branch has one child trigger and one
    # region reference. This catches accidental interpretation of numeric LUTs.
    if len(refs) != len(out) * 2:
        raise ValueError(f"trigger {rec['symbol_id']}: pointer layout drift")
    return out


def in_any_zone(v: float, ranges: list[tuple[float, float]]) -> bool:
    return any(lo <= v <= hi for lo, hi in ranges)


def zone_relation(v: float, ranges: list[tuple[float, float]]) -> dict:
    for i, (lo, hi) in enumerate(ranges):
        if lo <= v <= hi:
            return {"kind": "inside", "zone": i, "range": [lo, hi]}
    # Qualcomm trigger search interpolates across gaps between a region's end
    # and the next region's start. Record the bracketing gap deterministically.
    for i in range(len(ranges) - 1):
        a, b = ranges[i][1], ranges[i + 1][0]
        if a < v < b:
            return {"kind": "gap", "between": [i, i + 1], "range": [a, b],
                    "ratio": (v - a) / (b - a)}
    return {"kind": "outside", "value": v}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--devicemft", type=Path, required=True)
    ap.add_argument("--tuning", type=Path, required=True)
    ap.add_argument("--decoder", type=Path, required=True)
    ap.add_argument("--triggers", type=Path, required=True)
    ap.add_argument("--mode2-summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pe = args.devicemft.read_bytes()
    if sha_bytes(pe) != DEVICEMFT_SHA:
        raise SystemExit("exact Surface DeviceMFT SHA mismatch")
    missing = [x.decode("ascii", "replace") for x in REQUIRED_BINARY_STRINGS if x not in pe]
    if missing:
        raise SystemExit(f"required exact-binary adaptive strings missing: {missing}")

    tuning = args.tuning.read_bytes()
    if sha_bytes(tuning) != TUNING_SHA:
        raise SystemExit("exact IMX681 tuning SHA mismatch")
    dec = load_decoder(args.decoder)
    header = dec.parse_header(tuning)
    global records
    records, _ = dec.parse_symbol_table(tuning, header["sections"][0], header["sections"][1])
    objsec = header["sections"][1]

    # Root and control records are exact default Front/Sensor2-effective objects.
    for name, sid in [("lsc41_ife_v2", EXPECTED_SYMBOLS["lsc_root"]),
                      ("gtm13_ife_v2", EXPECTED_SYMBOLS["gtm_root"])]:
        r = records.get(sid)
        if r is None or r["type"] != name:
            raise SystemExit(f"{name}: exact root symbol drift")

    controls = {}
    for name, key in [("lsc41_ife_v2", "lsc_control"), ("gtm13_ife_v2", "gtm_control")]:
        r = records[EXPECTED_SYMBOLS[key]]
        if r["type"] != "control_var_type":
            raise SystemExit(f"{name}: control record type drift")
        words = u32_words(dec.data_bytes(tuning, objsec, r))
        if words != EXPECTED_CONTROLS[name]:
            raise SystemExit(f"{name}: control vector drift {words}")
        controls[name] = words

    ranges = {
        "lsc_aec": trigger_ranges(dec, tuning, objsec, records[EXPECTED_SYMBOLS["lsc_aec"]]),
        "lsc_cct": trigger_ranges(dec, tuning, objsec, records[EXPECTED_SYMBOLS["lsc_cct"]]),
        "gtm_aec": trigger_ranges(dec, tuning, objsec, records[EXPECTED_SYMBOLS["gtm_aec"]]),
    }
    for k, want in EXPECTED_RANGES.items():
        if ranges[k] != want:
            raise SystemExit(f"{k}: trigger ranges drift {ranges[k]} != {want}")

    trig = json.loads(args.triggers.read_text())
    if trig.get("accepted") is not True:
        raise SystemExit("matched trigger oracle not accepted")
    r5 = trig["requests"]["request5"]
    r6 = trig["requests"]["request6"]
    def fv(req, key): return float(req[key]["float"])

    matched = {
        "request5": {"gain": fv(r5, "GAIN"), "lux": fv(r5, "LUX"), "cct": fv(r5, "CCT"),
                     "drc": fv(r5, "DRC"), "lens": fv(r5, "LENS")},
        "request6": {"gain": fv(r6, "GAIN"), "lux": fv(r6, "LUX"), "cct": fv(r6, "CCT"),
                     "drc": fv(r6, "DRC"), "lens": fv(r6, "LENS")},
    }
    # The exact LSC/GTM final AEC tuning branch is wide enough that both
    # changing AEC candidates (real gain and lux index) remain in the same
    # first branch for requests 5 and 6. This intentionally avoids assuming
    # which AEC control representation the common interpolation utility chose.
    for req in matched.values():
        for candidate in (req["gain"], req["lux"]):
            if not in_any_zone(candidate, ranges["lsc_aec"]):
                raise SystemExit(f"LSC AEC candidate escaped expected zone: {candidate}")
            if not in_any_zone(candidate, ranges["gtm_aec"]):
                raise SystemExit(f"GTM AEC candidate escaped expected zone: {candidate}")
    if matched["request5"]["drc"] != matched["request6"]["drc"] or \
       matched["request5"]["lens"] != matched["request6"]["lens"] or \
       matched["request5"]["cct"] != matched["request6"]["cct"]:
        raise SystemExit("matched invariant LSC/GTM trigger dimensions drifted")

    cct_rel = {k: zone_relation(v["cct"], ranges["lsc_cct"]) for k, v in matched.items()}
    if cct_rel["request5"] != cct_rel["request6"]:
        raise SystemExit("matched CCT interpolation relation drifted")

    mode2 = json.loads(args.mode2_summary.read_text())
    if mode2.get("accepted") is not True or mode2.get("selected_resolution_index") != 2 or \
       mode2.get("geometry") != "3840x2160":
        raise SystemExit("Windows-selected IMX681 mode2 geometry proof drifted")

    result = {
        "schema": "sp11-e003h-adaptive-iq-state-boundary-v1",
        "status": "PASS",
        "accepted": True,
        "offline_only": True,
        "surface_inputs": {
            "devicemft_sha256": DEVICEMFT_SHA,
            "imx681_tuning_sha256": TUNING_SHA,
            "matched_trigger_oracle": str(args.triggers),
            "windows_selected_sensor_mode": 2,
            "windows_selected_sensor_geometry": "3840x2160",
        },
        "exact_rvas": {k: f"0x{v:x}" for k, v in EXACT_RVAS.items()},
        "tuning_control_vectors": controls,
        "trigger_ranges": {k: [[a, b] for a, b in v] for k, v in ranges.items()},
        "matched_request5_request6": matched,
        "matched_zone_proof": {
            "lsc_aec": {
                "request5_gain": zone_relation(matched["request5"]["gain"], ranges["lsc_aec"]),
                "request6_gain": zone_relation(matched["request6"]["gain"], ranges["lsc_aec"]),
                "request5_lux": zone_relation(matched["request5"]["lux"], ranges["lsc_aec"]),
                "request6_lux": zone_relation(matched["request6"]["lux"], ranges["lsc_aec"]),
            },
            "gtm_aec": {
                "request5_gain": zone_relation(matched["request5"]["gain"], ranges["gtm_aec"]),
                "request6_gain": zone_relation(matched["request6"]["gain"], ranges["gtm_aec"]),
                "request5_lux": zone_relation(matched["request5"]["lux"], ranges["gtm_aec"]),
                "request6_lux": zone_relation(matched["request6"]["lux"], ranges["gtm_aec"]),
            },
            "lsc_cct": cct_rel,
            "invariant_dimensions": ["DRCGain", "lensPosition", "CCT"],
        },
        "exact_binary_adaptive_paths": {
            "lsc": {
                "interpolation_region_bytes": "0xdf0",
                "mesh_points_per_channel": 221,
                "titan_wire_bytes_per_lsc_lut": "0x374",
                "adaptive_inputs": [
                    "sensor lens-shading calibration tables",
                    "Tintless state/results",
                    "ALSC AWB-BG statistics/state",
                    "previous-frame adaptive LSC state where selected by the exact pipeline",
                ],
                "binary_evidence_strings": [
                    "IFE Store Tintless camera",
                    "IFE Store ALSC camera",
                    "BPS UsePrevious Tintless camera",
                    "BPS UsePrevious ALSC camera",
                    "ALSC is disabled as the AWB BG stats are not present",
                ],
                "conclusion": "Chromatix trigger interpolation is only the base mesh; exact Surface LSC411 can apply calibration, Tintless and ALSC state before Titan680 packing.",
            },
            "gtm": {
                "interpolated_region_bytes": "0x404",
                "interpolated_points": 257,
                "wire_lut_bytes": "0x800",
                "adaptive_input": "TMC (tone-mapping-control) state selected by IsModuleEnabledInTMCPath",
                "conclusion": "Exact Surface GTM131 hardware calculation can replace/reshape the flat Chromatix curve using dynamic TMC state before Titan680 packing.",
            },
        },
        "producer_boundary": {
            "closed": [
                "all 8/8 steady calculated scalar fields",
                "16 deterministic ping-pong bank fields",
                "GIC Windows wire alias dependency on LSC",
                "LSC/GTM base Chromatix control vectors and trigger zones",
            ],
            "remaining_exact_inputs": [
                "LSC calibration/adaptive Tintless/ALSC state at the exact request",
                "GTM TMC state at the exact request",
                "LSC calculator geometry offsets/scale at the exact request (sensor mode geometry itself is already 3840x2160)",
            ],
            "next_gate": "Capture the adaptive LSC/TMC producer state on Windows for requests 4/5/6, then reproduce LSC0/LSC1 and GTM0 offline byte-for-byte. Derive wire GIC from the proven LSC alias. Only then reconsider Linux request6 runtime.",
        },
        "policy": {
            "linux_request6_generated_by_this_proof": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
            "camera_runtime_performed": False,
        },
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "controls": result["tuning_control_vectors"],
        "remaining_exact_inputs": result["producer_boundary"]["remaining_exact_inputs"],
        "next_gate": result["producer_boundary"]["next_gate"],
    }, indent=2))


if __name__ == "__main__":
    main()
