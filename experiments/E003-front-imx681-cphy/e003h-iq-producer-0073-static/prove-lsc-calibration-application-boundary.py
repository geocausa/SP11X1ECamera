#!/usr/bin/env python3
"""Fail-closed proof of the Surface IFELSC411 calibration application boundary.

This proves the exact Surface calibration/golden path used before Tintless:
  formatted EEPROM slot -> golden/EEPROM ratios -> LSC41 Chromatix -> green
  averaging -> geometry/Tintless/HW downstream.

Raw live Windows captures and proprietary binaries remain local/untracked.  The
tracked oracle contains only hashes, scalar facts, symbol metadata and static
instruction-byte assertions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

try:
    import pefile
except Exception as exc:
    raise SystemExit(f"missing proof dependency pefile: {exc}")

DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNING_SHA256 = "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d"
COMMON_SHA256 = {
    4: "646e62de0d5192129ba03bcc285cc5928c231ab24bf1d83ed236513c59c20535",
    5: "39c51103c2a92c566ff4493ede1a25a594d089b2e79a46857105f84f15ca2798",
    6: "038c2d066873604fd0c1003e897c8d63159e14fd9b5f9680be5fd0fb0dc5fd9d",
}

# Exact ARM64 instruction bytes from the SHA-pinned DeviceMFT.  Assertions are
# intentionally chosen at semantic boundaries rather than trusting decompiler
# pointer types.
CODE_BYTES = {
    # CheckAndUpdateChromatixData: resolve lscgolden41_ife_v2 and publish it at common+0x10.
    0xA0252C: "884b00f0",  # adrp string page
    0xA02530: "01610c91",  # add x1,#0x318 -> lscgolden41_ife_v2 string
    0xA02534: "31c5f397",  # bl GetModule
    0xA026B4: "6a0940f9",  # ldr x10,[common,#0x10]
    0xA026D0: "6c0900f9",  # str x12,[common,#0x10]
    # TranslateCalibrationTableToCommonLibrary: first slot source/copy + array pointers.
    0xA02B18: "883a50f9",  # ldr x8,[ISPInputData,#0x2070] formatted EEPROM object
    0xA02B1C: "01a10591",  # add x1,x8,#0x168 first formatted slot
    0xA02B30: "02be8152",  # mov w2,#0xdf0 exact slot copy size
    0xA02B40: "09a12991",  # slot+0xa68 channel pointer
    0xA02B54: "09310091",  # slot+0x0c channel pointer
    0xA02B68: "09d11b91",  # slot+0x6f4 channel pointer
    0xA02B7C: "09010e91",  # slot+0x380 channel pointer
    # Remaining four candidate slots are exactly 0xdf0 apart.
    0xA02B94: "01613d91",  # +0xf58
    0xA02C40: "08a983d2",  # 0x1d48 immediate
    0xA02CF0: "086785d2",  # 0x2b38 immediate
    0xA02DA0: "082587d2",  # 0x3928 immediate
    # Publish calibration count and enable/application flags.
    0xA02E50: "156900b9",  # str w21,[common,#0x68]
    0xA02EC4: "096d00b9",  # str 1,[common,#0x6c]
    0xA02ECC: "098100b9",  # str 1,[common,#0x80]
    # LSC411Interpolation calibration gate and golden/EEPROM ratio formation.
    0x93C3C0: "a86e40b9",  # ldr calibration enable +0x6c
    0x93C3D0: "a88240b9",  # ldr apply flag +0x80
    0x93C3DC: "ab0a40f9",  # ldr golden root common+0x10
    0x93C46C: "ac3240f9",  # ldr calibration descriptor common+0x60
    0x93C494: "907543bd",  # golden channel load
    0x93C498: "101a311e",  # fdiv golden / EEPROM
    0x93C4C8: "900140bd",  # golden channel load
    0x93C4CC: "101a311e",  # fdiv golden / EEPROM
    0x93C4F8: "d0696dbc",  # golden channel load
    0x93C4FC: "101a311e",  # fdiv golden / EEPROM
    0x93C530: "900140bd",  # golden channel load
    0x93C534: "101a311e",  # fdiv golden / EEPROM
    # Application path: two green corrections are summed then multiplied by 0.5,
    # and the same result is written to both green output meshes.
    0x93C6DC: "11102c1e",  # fmov s17,#0.5
    0x93C7D0: "720a321e",  # corrected second green
    0x93C7D4: "522a341e",  # add corrected greens
    0x93C7D8: "520a311e",  # *0.5
    0x93C7DC: "12692cbc",  # write one green output
    0x93C7E4: "d2682ebc",  # write same averaged green to other output
    # EEPROM formatter: raw extracted integers are converted directly to float.
    0x7241E8: "f001221e",  # scvtf s16,w15
    0x72423C: "5001221e",  # scvtf s16,w10
    0x724294: "b001221e",  # scvtf s16,w13
    0x7242E8: "b001221e",  # scvtf s16,w13
}

GOLDEN_ROOT = {
    "symbol_id": 42,
    "type": "lscgolden41_ife_v2",
    "version_raw": 65540,
    "data_abs_offset": 6189808,
    "data_bytes": 44,
    "data_sha256": "ff88c8bee7a23f82aced465d148e960ba12d4c2e8c30db32c8b78edf259f01a7",
}
GOLDEN_REGION = {
    "symbol_id": 1229,
    "data_abs_offset": 3318926,
    "data_bytes": 3536,
    "data_sha256": "b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def parse_tuning_golden(path: Path) -> dict:
    raw = path.read_bytes()
    if sha_bytes(raw) != TUNING_SHA256:
        raise RuntimeError("front tuning SHA-256 mismatch")
    if not raw.startswith(b"QTI Chromatix Header"):
        raise RuntimeError("unexpected tuning header")
    header_bytes = u32(raw, 0xA0)
    nsec = u32(raw, 0xA4)
    if header_bytes != 0xA8 or nsec != 3:
        raise RuntimeError("unexpected tuning container layout")
    sections = []
    for i in range(3):
        tag, off, size = struct.unpack_from("<3I", raw, header_bytes + i * 12)
        if tag != i:
            raise RuntimeError("tuning section tag drift")
        sections.append((off, size))
    sym_off, sym_size = sections[0]
    obj_off, obj_size = sections[1]
    if sym_size % 56:
        raise RuntimeError("symbol table record size drift")
    records = {}
    for off in range(sym_off, sym_off + sym_size, 56):
        sid = u32(raw, off)
        typ = raw[off + 4:off + 36].split(b"\0", 1)[0].decode("ascii", "replace")
        version, mode_id, mode_sid, data_off, data_bytes = struct.unpack_from("<5I", raw, off + 36)
        records[sid] = {
            "symbol_id": sid,
            "type": typ,
            "version_raw": version,
            "mode_id": mode_id,
            "mode_symbol_id": mode_sid,
            "data_abs_offset": obj_off + data_off,
            "data_bytes": data_bytes,
        }
    roots = [r for r in records.values() if r["type"] == "lscgolden41_ife_v2"]
    if len(roots) != 1:
        raise RuntimeError(f"expected one lscgolden41_ife_v2 root, found {len(roots)}")
    root = roots[0]
    root_data = raw[root["data_abs_offset"]:root["data_abs_offset"] + root["data_bytes"]]
    root_public = {**root, "data_sha256": sha_bytes(root_data)}
    for k, expected in GOLDEN_ROOT.items():
        if root_public.get(k) != expected:
            raise RuntimeError(f"golden root {k} drift: {root_public.get(k)!r} != {expected!r}")

    refs = []
    for off in range(0, len(root_data) - 3, 4):
        sid = u32(root_data, off)
        if sid in records and sid >= 0x400:
            refs.append((off, sid, records[sid]["type"]))
    expected_refs = [(16, 1225, "revision"), (24, 1226, "control_var_type"), (40, 1227, "mod_lscgolden41_trigger_data")]
    if refs != expected_refs:
        raise RuntimeError(f"golden root refs drift: {refs!r}")

    trigger = records[1227]
    trig_data = raw[trigger["data_abs_offset"]:trigger["data_abs_offset"] + trigger["data_bytes"]]
    trig_refs = []
    for off in range(0, len(trig_data) - 3, 4):
        sid = u32(trig_data, off)
        if sid in records and sid >= 0x400:
            trig_refs.append((off, sid, records[sid]["type"]))
    if trig_refs != [(12, 1228, "trigger"), (20, 1229, "region")]:
        raise RuntimeError(f"golden trigger refs drift: {trig_refs!r}")

    region = records[1229]
    region_data = raw[region["data_abs_offset"]:region["data_abs_offset"] + region["data_bytes"]]
    region_public = {**region, "data_sha256": sha_bytes(region_data)}
    for k, expected in GOLDEN_REGION.items():
        if region_public.get(k) != expected:
            raise RuntimeError(f"golden region {k} drift: {region_public.get(k)!r} != {expected!r}")
    if len(region_data) != 4 * 221 * 4:
        raise RuntimeError("golden region is not 4x221 float32")
    vals = struct.unpack("<884f", region_data)
    if not all(math.isfinite(v) and v == float(int(v)) for v in vals):
        raise RuntimeError("golden region lost integer-valued float32 invariant")
    if min(vals) != 133.0 or max(vals) != 1023.0:
        raise RuntimeError("golden region min/max drift")
    return {
        "root": root_public,
        "root_refs": [{"at": off, "symbol_id": sid, "type": typ} for off, sid, typ in refs],
        "trigger_refs": [{"at": off, "symbol_id": sid, "type": typ} for off, sid, typ in trig_refs],
        "region": {
            **region_public,
            "float32_values": len(vals),
            "mesh": "4x221",
            "integer_valued": True,
            "min_float": min(vals),
            "max_float": max(vals),
            "first_12": list(vals[:12]),
        },
    }


def verify_device_mft(path: Path) -> dict:
    if sha_file(path) != DEVICE_MFT_SHA256:
        raise RuntimeError("DeviceMFT SHA-256 mismatch")
    pe = pefile.PE(str(path), fast_load=True)
    raw = path.read_bytes()
    proved = {}
    for rva, expected in CODE_BYTES.items():
        off = pe.get_offset_from_rva(rva)
        actual = raw[off:off + 4].hex()
        if actual != expected:
            raise RuntimeError(f"DeviceMFT code mismatch RVA 0x{rva:x}: {actual} != {expected}")
        proved[f"0x{rva:x}"] = actual
    for rva, expected in {
        0x1375390: b"lsc41_ife_v2\0",
        0x1375938: b"tintless23_sw_v2\0",
        0x1375318: b"lscgolden41_ife_v2\0",
    }.items():
        off = pe.get_offset_from_rva(rva)
        if raw[off:off + len(expected)] != expected:
            raise RuntimeError(f"DeviceMFT string mismatch RVA 0x{rva:x}")
    return proved


def verify_live_common(capture_dir: Path) -> dict:
    out = {}
    for request in (4, 5, 6):
        path = capture_dir / f"REQ{request}_LSC_COMMON.bin"
        data = path.read_bytes()
        if len(data) != 0x1E8 or sha_bytes(data) != COMMON_SHA256[request]:
            raise RuntimeError(f"request{request}: LSC common size/hash mismatch")
        facts = {
            "calibration_descriptor_capacity": data[0x58],
            "valid_calibration_slots": u32(data, 0x68),
            "calibration_enabled": u32(data, 0x6C),
            "calibration_applied": u32(data, 0x80),
        }
        expected = {
            "calibration_descriptor_capacity": 5,
            "valid_calibration_slots": 1,
            "calibration_enabled": 1,
            "calibration_applied": 1,
        }
        if facts != expected:
            raise RuntimeError(f"request{request}: live calibration branch drift: {facts!r}")
        out[f"request{request}"] = {"common_sha256": sha_bytes(data), **facts}
    return out


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--device-mft", type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
    )
    ap.add_argument(
        "--tuning", type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin"),
    )
    ap.add_argument("--capture-dir", type=Path, default=here / "windows-adaptive-live-20260902")
    ap.add_argument("--out", type=Path, default=here / "lsc-calibration-application-oracle.json")
    args = ap.parse_args()

    code = verify_device_mft(args.device_mft)
    golden = parse_tuning_golden(args.tuning)
    live = verify_live_common(args.capture_dir)

    slot_offsets = [0x168, 0xF58, 0x1D48, 0x2B38, 0x3928]
    if any(b - a != 0xDF0 for a, b in zip(slot_offsets, slot_offsets[1:])):
        raise RuntimeError("slot spacing invariant failed")

    oracle = {
        "schema": "sp11-e003h-lsc-calibration-application-boundary-v1",
        "accepted": True,
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA256,
            "front_tuning_sha256": TUNING_SHA256,
            "capture_session": "E003H_ADAPTIVE_0073_LIVE_20260902",
            "same_stream_required": True,
        },
        "exact_functions": {
            "ife_lsc411_check_update_chromatix_rva": "0xa02420",
            "ife_lsc411_check_dependence_change_rva": "0xa028b0",
            "lsc411_interpolation_rva": "0x93c1b0",
            "eeprom_format_lsc_data_rva": "0x723e40",
        },
        "code_byte_proofs": code,
        "golden_chromatix": golden,
        "formatted_eeprom_contract": {
            "isp_input_formatted_eeprom_pointer_byte_offset": "0x2070",
            "candidate_slot_offsets": [f"0x{x:x}" for x in slot_offsets],
            "candidate_slot_stride": "0xdf0",
            "candidate_slots": 5,
            "valid_slot_test": "first dword == 1",
            "copied_slot_bytes": "0xdf0",
            "module_copy_base": "IFELSC411 module+0x1978",
            "descriptor_base": "common+0x60",
            "descriptor_capacity_byte": "common+0x58 == 5",
            "per_slot_descriptor_bytes": "0x20",
            "channel_pointer_offsets_within_copied_slot": ["0x0c", "0x380", "0x6f4", "0xa68"],
            "channel_bytes": "0x374 = 221 float32",
            "valid_slot_count": "common+0x68",
            "calibration_enable": "common+0x6c",
            "calibration_apply": "common+0x80",
            "formatter_numeric_contract": "FormatLSCData converts extracted integer channel values directly with SCVTF into float32; no gain-scale multiply is present at the asserted conversion sites.",
        },
        "live_branch": {
            "requests": live,
            "classification": "ONE VALID SLOT ONLY: request4/5/6 all report capacity=5, valid count=1, calibration enable=1 and calibration apply=1.",
            "multi_slot_interpolation_required_for_this_stream": False,
        },
        "calibration_application_math": {
            "ratio_direction": "golden / formatted_EEPROM",
            "channel0": "ratio0 * interpolated LSC channel0",
            "channel3": "ratio3 * interpolated LSC channel3",
            "green_rule": "channel1 and channel2 are both replaced by 0.5 * (ratio1*tuning_ch1 + ratio2*tuning_ch2)",
            "green_output_equal_after_calibration": True,
            "application_precedes_geometry_resample": True,
            "application_precedes_tintless": True,
        },
        "capture_reduction": {
            "old_conservative_calibration_bytes": "0x45b0 = five candidate slots",
            "new_exact_required_bytes_for_this_physical_stream": "0xdf0 = one valid formatted slot",
            "preferred_capture": "After IFELSC411 calibration translation has established common+0x68==1, dump module+0x1978 for exactly 0xdf0 bytes. This avoids pointer-unit ambiguity at ISPInputData+0x2070 and captures the exact copied slot consumed by interpolation.",
        },
        "classification": "CLOSED STATIC/LIVE LSC CALIBRATION-APPLICATION BOUNDARY: exact Surface code proves lscgolden41_ife_v2, one valid formatted EEPROM slot, golden/EEPROM ratio direction, two-green averaging, and pre-geometry/pre-Tintless placement.",
        "next_gate": "Acquire only the single 0xdf0 copied formatted calibration slot from the same Windows stream, then replay exact LSC interpolation + calibration + geometry + sequential Tintless + Q10 staging. Staging-to-wire and GTM are already closed. Linux request6 remains forbidden.",
        "safety": {
            "linux_camera_runtime": False,
            "linux_request6_executed": False,
            "raw_windows_capture_committed": False,
        },
    }
    args.out.write_text(json.dumps(oracle, indent=2) + "\n")
    print("PASS exact LSC calibration application boundary")
    print("  lscgolden41 region:", golden["region"]["data_sha256"], "4x221", golden["region"]["min_float"], golden["region"]["max_float"])
    print("  live valid calibration slots: request4=1 request5=1 request6=1")
    print("  minimal same-stream calibration capture: 0xdf0 bytes")
    print("  oracle:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
