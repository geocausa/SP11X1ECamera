#!/usr/bin/env python3
"""Fail-closed proof of the exact Surface IFELSC411 embedded Tintless/ALSC path.

This is static/offline only. It proves that the exact IFELSC411 Create/RunCalculation
path uses in-image adaptive interfaces and bounds the ALSC AWB-BG grid read footprint.
It authorizes no camera runtime and no Linux request6.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

DEVICEMFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"

# Exact ARM64 bytes in the SHA-pinned Surface DeviceMFT.
CODE = {
    # IFELSC411::Create installs the two adaptive interface objects directly.
    0xA01AE4: "083483d2",  # mov x8,#0x19a0 : tintless interface member
    0xA01AEC: "db550a94",  # bl  0xc97258 : embedded Tintless interface ctor
    0xA01B38: "083383d2",  # mov x8,#0x1998 : ALSC interface member
    0xA01B40: "3a560a94",  # bl  0xc97428 : embedded ALSC interface ctor

    # Tintless interface construction: shared internal context + embedded entrypoints.
    0xC97284: "a1000094",  # bl 0xc97508 : allocate/init 0x1090 context
    0xC972A0: "692200a9",  # stp x9,x8,[x19] : Process/Destroy pointers
    0xC972AC: "680a00f9",  # str x8,[x19,#0x10] : FuseStats pointer

    # ALSC interface construction and exact embedded process dispatch.
    0xC97464: "29000094",  # bl 0xc97508 : allocate/init 0x1090 context
    0xC97480: "692200a9",  # stp x9,x8,[x19] : ALSCProcess/Destroy pointers
    0xC97304: "bb000094",  # bl 0xc975f0 : exact embedded ALSC core

    # Tintless embedded process/fusion cores.
    0xC96DE0: "f4240094",  # bl 0xca01b0 : exact Tintless core
    0xC97140: "b4280094",  # bl 0xca1410 : exact Tintless stats fusion core

    # IFELSC411::RunCalculation wires those interfaces into the common input.
    0xA0384C: "68d24cf9",  # ldr x8,[x19,#0x19a0]
    0xA03850: "285900f9",  # str x8,[x9,#0xb0] : common Tintless interface
    0xA03A64: "68064ef9",  # ldr x8,[x19,#0x1c08] : AWB-BG stats source
    0xA03A78: "68ce4cf9",  # ldr x8,[x19,#0x1998]
    0xA03A7C: "285d00f9",  # str x8,[x9,#0xb8] : common ALSC interface

    # LSC411Setting invokes ALSC with the exact 64x48 geometry constant.
    0x9B5570: "605e40f9",  # ldr x0,[x19,#0xb8] : ALSC interface
    0x9B5578: "615640f9",  # ldr x1,[x19,#0xa8] : AWB-BG stats
    0x9B557C: "03088052",  # mov w3,#0x40
    0x9B5580: "0306a072",  # movk w3,#0x30,lsl#16 => 0x00300040

    # Common internal context and lazily allocated Tintless core state sizes.
    0xC97518: "001282d2",  # mov x0,#0x1090
    0xC96480: "00dd84d2",  # mov x0,#0x26e8
    0xC96484: "2000a0f2",  # movk x0,#1,lsl#16 => 0x126e8

    # Persistent previous-Tintless mesh history offsets in the 0x1090 wrapper context.
    0xC96E50: "c83a50b9",  # ldr w8,[x22,#0x1038] : previous-output-valid
    0xC96E58: "cca20991",  # add x12,x22,#0x268
    0xC96E5C: "ca721791",  # add x10,x22,#0x5dc
    0xC96E60: "cb422591",  # add x11,x22,#0x950
    0xC96E64: "c9123391",  # add x9,x22,#0xcc4

    # Embedded ALSC geometry and stats format selection.
    0xC97728: "693e0053",  # uxth w9,w19 : low16 geometry = 0x40
    0xC977AC: "687e1053",  # lsr w8,w19,#16 : high16 geometry = 0x30
    0xC977B4: "337d081b",  # mul w19,w9,w8 : 64*48 = 3072 regions
    0xC97800: "0c050153",  # ubfx w12,w8,#1,#1 : saturated-info format bit
    0xC9783C: "0c0e80d2",  # mov x12,#0x70 : saturated record stride
    0xC978DC: "ac1d4179",  # ldrh w12,[x13,#0x8e] : highest saturated read
    0xC97908: "0c0780d2",  # mov x12,#0x38 : ordinary record stride
    0xC97958: "acad4079",  # ldrh w12,[x13,#0x56] : highest ordinary read
}

REQUIRED_STRINGS = [
    b"CamX::TintlessAlgorithmWrapper::Process",
    b"CamX::TintlessAlgorithmWrapper::ALSCProcess",
    b"CamX::TintlessAlgorithmWrapper::FuseStats",
    b"camxtintlessalgowrapper.cpp",
    b"camxchitintlessinterface.cpp",
]

EXACT = {
    "ifel_lsc411_create_rva": 0xA01A20,
    "tintless_interface_ctor_rva": 0xC97258,
    "alsc_interface_ctor_rva": 0xC97428,
    "shared_adaptive_context_ctor_rva": 0xC97508,
    "tintless_process_rva": 0xC95FD0,
    "tintless_fuse_stats_rva": 0xC97110,
    "tintless_core_rva": 0xCA01B0,
    "tintless_fusion_core_rva": 0xCA1410,
    "alsc_process_rva": 0xC972E0,
    "alsc_core_rva": 0xC975F0,
    "lsc_run_calculation_rva": 0xA03790,
    "lsc_hw_setting_rva": 0x9B4BA0,
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rva_to_off(pe: bytes, rva: int) -> int:
    if pe[:2] != b"MZ":
        raise ValueError("not PE/MZ")
    peoff = struct.unpack_from("<I", pe, 0x3C)[0]
    if pe[peoff:peoff + 4] != b"PE\0\0":
        raise ValueError("bad PE signature")
    nsec = struct.unpack_from("<H", pe, peoff + 6)[0]
    optsz = struct.unpack_from("<H", pe, peoff + 20)[0]
    sh = peoff + 24 + optsz
    for i in range(nsec):
        o = sh + i * 40
        vsize, va, rawsz, raw = struct.unpack_from("<IIII", pe, o + 8)
        if va <= rva < va + max(vsize, rawsz):
            return raw + rva - va
    raise ValueError(f"RVA 0x{rva:x} not mapped")


def assert_code(pe: bytes) -> dict[str, str]:
    out = {}
    for rva, hx in CODE.items():
        want = bytes.fromhex(hx)
        off = rva_to_off(pe, rva)
        got = pe[off:off + len(want)]
        if got != want:
            raise ValueError(f"code mismatch RVA 0x{rva:x}: {got.hex()} != {want.hex()}")
        out[f"0x{rva:x}"] = got.hex()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--devicemft", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    pe = a.devicemft.read_bytes()
    if sha256(pe) != DEVICEMFT_SHA:
        raise SystemExit("exact Surface DeviceMFT SHA mismatch")
    missing = [s.decode("ascii") for s in REQUIRED_STRINGS if s not in pe]
    if missing:
        raise SystemExit(f"required embedded adaptive strings missing: {missing}")
    code = assert_code(pe)

    # The LSC hardware setting passes w3 = 0x00300040 to ALSCProcess.
    width = 0x40
    height = 0x30
    regions = width * height
    ordinary_stride = 0x38
    ordinary_highest_read_end = 0x56 + 2
    saturated_stride = 0x70
    saturated_highest_read_end = 0x8E + 2
    ordinary_capture = (regions - 1) * ordinary_stride + ordinary_highest_read_end
    saturated_capture = (regions - 1) * saturated_stride + saturated_highest_read_end
    if ordinary_capture != 0x2A020 or saturated_capture != 0x54020:
        raise SystemExit("ALSC stats footprint arithmetic drift")

    history_offsets = [0x268, 0x5DC, 0x950, 0xCC4]
    if any(b - a != 0x374 for a, b in zip(history_offsets, history_offsets[1:])):
        raise SystemExit("Tintless persistent mesh spacing drift")
    if history_offsets[-1] + 0x374 != 0x1038:
        raise SystemExit("Tintless history end/valid flag boundary drift")

    result = {
        "schema": "sp11-e003h-lsc-embedded-adaptive-core-v1",
        "status": "PASS",
        "accepted": True,
        "offline_only": True,
        "surface_devicemft_sha256": DEVICEMFT_SHA,
        "exact_rvas": {k: f"0x{v:x}" for k, v in EXACT.items()},
        "code_byte_proofs": code,
        "embedded_interface_proof": {
            "ifelsc411_tintless_member": "module+0x19a0",
            "ifelsc411_alsc_member": "module+0x1998",
            "run_calculation_common_tintless_interface": "common+0xb0 <- module+0x19a0",
            "run_calculation_common_alsc_interface": "common+0xb8 <- module+0x1998",
            "run_calculation_alsc_awb_bg_stats": "common+0xa8 <- module+0x1c08 when ALSC is enabled and stats are present",
            "shared_wrapper_context_bytes": "0x1090",
            "tintless_lazy_core_state_bytes": "0x126e8",
            "classification": "Exact IFELSC411 constructs and dispatches embedded Tintless/ALSC interfaces from QcDeviceMFT8380.dll. Older dynamic libcamxtintlessalgo paths present elsewhere in the image are not the IFELSC411 Create path.",
        },
        "tintless_statefulness": {
            "previous_mesh_offsets": [f"0x{x:x}" for x in history_offsets],
            "mesh_bytes_each": "0x374",
            "contiguous_previous_mesh_bytes": "0xdf0",
            "previous_output_valid_flag_offset": "0x1038",
            "consequence": "Request6 offline reproduction must preserve Tintless history from stream start or begin from an exact pre-request context checkpoint; request6 cannot be treated as a stateless one-frame calculation.",
        },
        "alsc_awb_bg_read_boundary": {
            "geometry_word": "0x00300040",
            "width": width,
            "height": height,
            "regions": regions,
            "format_select": "stats word0 bit1",
            "ordinary": {
                "record_stride": "0x38",
                "highest_read_end_within_record_addressing": "0x58",
                "bounded_bytes_from_stats_base": "0x2a020",
            },
            "saturated_info": {
                "record_stride": "0x70",
                "highest_read_end_within_record_addressing": "0x90",
                "bounded_bytes_from_stats_base": "0x54020",
            },
            "capture_rule": "Validate stats word0 bit1, then capture the corresponding exact bound; 0x54020 is a safe fail-closed maximum for this 64x48 Surface path.",
        },
        "revised_offline_strategy": {
            "algorithm_implementation": "Recoverable from the exact embedded Surface DeviceMFT; no external Tintless/ALSC DLL oracle is required for IFELSC411.",
            "dynamic_inputs_still_required": [
                "Tintless config/stats and prior-frame state (or stream-start sequence)",
                "ALSC 64x48 AWB-BG parsed stats when enabled",
                "per-device LSC EEPROM calibration",
                "LSC request geometry",
            ],
            "preferred_validation": "Capture adaptive inputs from stream start through Windows request6, port/replay the embedded cores offline, and require byte-for-byte LSC0/LSC1 equality. A pre-request4 context checkpoint is an acceptable validation shortcut but not a substitute for the final Linux implementation.",
        },
        "policy": {
            "windows_camera_runtime_performed": False,
            "linux_camera_runtime_performed": False,
            "linux_request6_generated": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
        },
    }
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "embedded": result["embedded_interface_proof"]["classification"],
        "tintless_history_bytes": result["tintless_statefulness"]["contiguous_previous_mesh_bytes"],
        "alsc_max_stats_bytes": result["alsc_awb_bg_read_boundary"]["saturated_info"]["bounded_bytes_from_stats_base"],
        "next": result["revised_offline_strategy"]["preferred_validation"],
    }, indent=2))


if __name__ == "__main__":
    main()
