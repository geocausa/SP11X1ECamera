#!/usr/bin/env python3
"""Fail-closed static proof of the exact Surface GTM131 <- TMC read boundary.

No camera runtime is performed or authorized. The proof pins the SHA-identified
Surface DeviceMFT, the IFE GTM conversion/call ABI, the GTM131 HW-setting vtable
slot, and the exact TMC-v5 data ranges consumed by the GTM hardware calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

DEVICEMFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
IMAGE_BASE = 0x180000000

EXACT_RVAS = {
    "ife_gtm_execute": 0xA28B00,
    "published_to_internal_tmc_copy": 0x898738,
    "gtm_interpolation": 0x93BF30,
    "gtm_hw_setting": 0x9AA6E0,
    "gtm_titan680_packer": 0xB5B3D0,
    "ife_gtm_hw_call_return": 0xA28F2C,
    "bps_tmc_metadata_post": 0x78E0F0,
}

# Full binary SHA pins the image; these short instruction proofs pin the exact
# ABI and branch points used by the capture contract independently.
ABI_CODE_PROOFS = {
    0xA28E40: bytes.fromhex("819a40f9"),  # ldr x1,[x20,#0x130] internal selected-TMC buffer
    0xA28E44: bytes.fromhex("010100f9"),  # str x1,[x8] where x8 == GTM common +0x50 slot
    0xA28E48: bytes.fromhex("60ea50f9"),  # ldr x0,[x19,#0x21d0] published TMC output
    0xA28E4C: bytes.fromhex("080c40b9"),  # ldr w8,[x0,#0xc] published enable/state
    0xA28E50: bytes.fromhex("1f050071"),  # cmp w8,#1
    0xA28E58: bytes.fromhex("38bef997"),  # bl published->internal TMC copy
    0xA28F10: bytes.fromhex("085d42f9"),  # ldr x8,[x8,#0x4b8] GTM HW-setting vtable slot
    0xA28F28: bytes.fromhex("e0013fd6"),  # blr x15; IFE return is RVA 0xa28f2c
    0x9AA920: bytes.fromhex("8b2a40f9"),  # ldr x11,[x20,#0x50] selected internal TMC pointer
    0x9AA928: bytes.fromhex("681140b9"),  # ldr w8,[x11,#0x10] validity/enable
    0x9AA93C: bytes.fromhex("680940b9"),  # ldr w8,[x11,#0x8] TMC generation
    0x9AA940: bytes.fromhex("1f150071"),  # cmp w8,#5
    0x9AA948: bytes.fromhex("687540b9"),  # ldr w8,[x11,#0x74] curve mode
    0x9AA94C: bytes.fromhex("8a208ad2"),  # mov x10,#0x5104
    0x9AA950: bytes.fromhex("09248ad2"),  # mov x9,#0x5120
    0x9AA964: bytes.fromhex("08368ad2"),  # mov x8,#0x51b0
    0x9AA998: bytes.fromhex("08458cd2"),  # mov x8,#0x6228
    0x9A55F4: bytes.fromhex("080f40b9"),  # helper: ldr w8,[x24,#0xc]
    0x9A5644: bytes.fromhex("080f40b9"),  # helper: re-read internal TMC hw version
    0x9A5664: bytes.fromhex("3601881a"),  # csel w22,0x100,0x400 depending +0xc == 0x60400
    0x9A56E0: bytes.fromhex("149f50bd"),  # ldr s20,[x24,#0x109c]
    0x9A56EC: bytes.fromhex("14a350bd"),  # ldr s20,[x24,#0x10a0]
    0x78E14C: bytes.fromhex("024f90d2"),  # mov x2,#0x8278 published TMC metadata object size
}

# PTR_FUN_18161fe70 + 0x4b0/+0x4b8. These are image RVAs because the
# DeviceMFT image base is 0x180000000.
POINTER_PROOFS = {
    0x1620320: 0x18093BF30,  # GTM131 interpolation
    0x1620328: 0x1809AA6E0,  # GTM131 hardware setting
}

# Exact v5 internal-layout reads. The two 7-float arrays are consumed by both
# mode paths. The 15-float coefficient block is used when +0x74 == 2. The
# +0x6228 domain is 256 floats only for hw-version 0x60400; every other exact
# branch uses 1024 floats, so the capture contract takes the fail-safe maximum.
TMC_V5_RANGES = [
    (0x0008, 0x000C, "generation/hardware-version/valid header dwords"),
    (0x0074, 0x0004, "curve interpolation mode"),
    (0x109C, 0x0008, "two GTM blend scalars"),
    (0x5104, 0x001C, "seven-float source knot array"),
    (0x5120, 0x001C, "seven-float target knot array"),
    (0x51B0, 0x003C, "15-float cubic coefficient block (mode 2)"),
    (0x6228, 0x1000, "maximum 1024-float dynamic tone-curve domain"),
]

GTM_COMMON_INPUT_OFFSETS = {
    "bank_or_lut_selector": 0x14,
    "pipeline_format_halfword": 0x2A,
    "titan_hw_version": 0x34,
    "curve_postprocess_enable": 0x70,
    "curve_postprocess_strength": 0x74,
    "curve_postprocess_limit": 0x78,
    "selected_internal_tmc_pointer": 0x50,
}


def sha(b: bytes) -> str:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--devicemft", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pe = args.devicemft.read_bytes()
    if sha(pe) != DEVICEMFT_SHA:
        raise SystemExit("exact Surface DeviceMFT SHA mismatch")

    code = {}
    for rva, want in ABI_CODE_PROOFS.items():
        off = rva_to_off(pe, rva)
        got = pe[off:off + len(want)]
        if got != want:
            raise SystemExit(f"code proof mismatch RVA 0x{rva:x}: {got.hex()} != {want.hex()}")
        code[f"0x{rva:x}"] = got.hex()

    ptrs = {}
    for rva, want in POINTER_PROOFS.items():
        off = rva_to_off(pe, rva)
        got = struct.unpack_from("<Q", pe, off)[0]
        if got != want:
            raise SystemExit(f"pointer proof mismatch RVA 0x{rva:x}: 0x{got:x} != 0x{want:x}")
        ptrs[f"0x{rva:x}"] = f"0x{got:x}"

    if b"tmc14_sw_v2" not in pe or b"CamX::IQInterface::TMC141CalculateSetting" not in pe:
        raise SystemExit("exact TMC14 provenance strings missing")

    sparse = sum(n for _, n, _ in TMC_V5_RANGES)
    if sparse != 0x108C:
        raise SystemExit(f"sparse TMC range accounting drift: 0x{sparse:x}")

    result = {
        "schema": "sp11-e003h-gtm-tmc-read-boundary-v1",
        "status": "PASS",
        "accepted": True,
        "offline_only": True,
        "devicemft_sha256": DEVICEMFT_SHA,
        "exact_rvas": {k: f"0x{v:x}" for k, v in EXACT_RVAS.items()},
        "code_byte_proofs": code,
        "dispatch_pointer_proofs": ptrs,
        "producer_flow": [
            "ISPInputData+0x21d0 is the published TMC/ADRC output pointer.",
            "IFE GTM selects module+0x130 as its internal TMC buffer and stores that pointer into GTM common-input +0x50.",
            "When published TMC +0x0c == 1, RVA 0x898738 converts/copies the published 0x8278-byte layout into the internal layout before GTM calculation.",
            "IFE GTM calls the exact GTM131 hardware setting through dispatch slot +0x4b8; the slot resolves to RVA 0x9aa6e0.",
        ],
        "preferred_windows_capture": {
            "breakpoint_rva": "0x9aa6e0",
            "ife_caller_filter_lr": "0x180a28f2c",
            "arguments": {
                "x0": "GTM common input; capture 0x7c bytes locally and decode only the proven fields",
                "x1": "0x404-byte / 257-float interpolated GTM region input",
                "x2": "capture first dword (GTM calculation flags)",
                "x3": "capture halfword at +0x4 used by the exact setting output",
                "x4": "GTM unpacked output destination; save pointer for post-return validation",
            },
            "selected_internal_tmc": "poi(x0+0x50)",
            "fail_closed_checks": [
                "selected_internal_tmc is non-null",
                "dwo(selected_internal_tmc+0x10) is non-zero",
                "dwo(selected_internal_tmc+0x08) == 5 before applying the v5 sparse-range contract",
                "if the generation is not 5, stop and revise the static capture contract rather than over-reading an assumed layout",
            ],
        },
        "gtm_common_input_reads": {k: f"0x{v:x}" for k, v in GTM_COMMON_INPUT_OFFSETS.items()},
        "tmc_v5_internal_read_ranges": [
            {"offset": f"0x{o:x}", "bytes": f"0x{n:x}", "purpose": why}
            for o, n, why in TMC_V5_RANGES
        ],
        "tmc_v5_branch_details": {
            "mode_field": "dwo(tmc+0x74)",
            "mode_2": "uses the two seven-float knot arrays plus the 15-float coefficient block",
            "other_mode": "uses the two seven-float knot arrays and derives its interpolation internally",
            "domain_selection": "tmc+0x0c == 0x60400 selects 256 floats; otherwise the exact helper selects 1024 floats",
            "capture_policy": "capture the maximum 0x1000 bytes at tmc+0x6228 regardless, so no target-version assumption is required",
        },
        "size_reduction": {
            "published_tmc_object_bytes": "0x8278",
            "max_sparse_internal_tmc_bytes": "0x108c",
            "max_sparse_internal_tmc_percent_of_full": sparse / 0x8278 * 100.0,
            "common_input_plus_sparse_tmc_bytes": "0x1108",
            "common_plus_sparse_plus_interpolated_plus_aux_input_bytes": "0x1512",
        },
        "post_return_validation": {
            "ife_post_hw_result_rva": "0xa2908c",
            "cached_final_gtm_staging_rva": "0xa290a8",
            "cached_final_gtm_staging": "IFEGTM131 module+0x138, exactly 0x800 bytes",
            "requirement": "hash/dump the 0x800-byte staging for requests 4/5/6 and compare request6 to the matched Windows GTM0 oracle; raw memory remains local/untracked",
        },
        "gate": "Capture the exact request4/5/6 v5 sparse TMC ranges plus GTM common/aux inputs at the GTM131 HW-setting entry, port the exact v5 math, and reproduce GTM0 byte-for-byte offline. Linux request6 remains blocked.",
        "policy": {
            "windows_camera_runtime_performed_by_this_proof": False,
            "linux_camera_runtime_performed": False,
            "linux_request6_generated": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
        },
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "hw_setting": result["exact_rvas"]["gtm_hw_setting"],
        "ife_lr_filter": result["preferred_windows_capture"]["ife_caller_filter_lr"],
        "max_sparse_tmc_bytes": result["size_reduction"]["max_sparse_internal_tmc_bytes"],
        "full_tmc_bytes": result["size_reduction"]["published_tmc_object_bytes"],
        "gate": result["gate"],
    }, indent=2))


if __name__ == "__main__":
    main()
