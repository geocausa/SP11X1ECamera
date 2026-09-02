#!/usr/bin/env python3
"""Fail-closed proof of the live IFELSC411 Tintless-only stats boundary.

Raw Windows producer captures and proprietary DeviceMFT bytes remain local and
untracked.  The generated oracle records only hashes, scalar branch facts and
exact read bounds derived from the SHA-pinned Surface binary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    import pefile
except Exception as exc:
    raise SystemExit(f"missing proof dependency pefile: {exc}")

DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
CAPTURE_ZIP_SHA256 = "429102b00ca808bd9680ae9f1d309610c701ff541763f1236fd2a0dea342cb71"

COMMON_SHA256 = {
    4: "646e62de0d5192129ba03bcc285cc5928c231ab24bf1d83ed236513c59c20535",
    5: "39c51103c2a92c566ff4493ede1a25a594d089b2e79a46857105f84f15ca2798",
    6: "038c2d066873604fd0c1003e897c8d63159e14fd9b5f9680be5fd0fb0dc5fd9d",
}
STAGING_SHA256 = {
    4: "c67b893c5b32b6fdf343875cd4f2921f97429d98922d2b4d555c5bb36f4602bc",
    5: "5c07dca5e0e44e1fc3df026396643a255fc7fb1445a70e27934e9e6c6c49d766",
    6: "e8526f3f3676802b9596fadd0bc479df2a6e531bf587c9278e8729a10e2daa6e",
}
CAL_SHA256 = {
    0: "9002f20bedf10461e010f9afd9fcd158a24904883cc714b065473c01c19a7906",
    1: "70d1f77698110e092263bca78317b84c703b75c5f9419c9425c7f31037aac26a",
    2: "70d1f77698110e092263bca78317b84c703b75c5f9419c9425c7f31037aac26a",
    3: "9675845e633fc2ea807e1e586a4ea423ef5226684e6f2edc17ae0bc4fe1e02e1",
}

# Exact raw ARM64 instruction bytes from the SHA-pinned DeviceMFT.  These pin
# both the wrapper ABI and the two independent stats consumers.
CODE_BYTES = {
    # TintlessAlgorithmWrapper::Process: x1 config, x2 stats, x3 input, x4 output.
    0xC95FF4: "f50301aa",  # mov x21,x1
    0xC95FF8: "e20f00f9",  # str x2,[sp,#0x18]
    0xC95FFC: "f90303aa",  # mov x25,x3
    0xC96000: "f80304aa",  # mov x24,x4
    0xC9600C: "160c40f9",  # ldr x22,[x0,#0x18] wrapper context
    0xC9609C: "b4720091",  # add x20,x21,#0x1c
    0xC960AC: "820780d2",  # mov x2,#0x3c (second config chunk)
    0xC96160: "b4620191",  # add x20,x21,#0x58
    0xC96170: "021b80d2",  # mov x2,#0xd8 (final config chunk through +0x130)
    0xC96358: "88d640b9",  # ldr w8,[x20,#0xd4] => x21+0x12c..+0x130
    0xC96D78: "c09640f9",  # ldr x0,[x22,#0x128] lazy core state
    0xC96D80: "e80f40f9",  # ldr x8,[sp,#0x18] saved stats pointer
    0xC96D98: "e81300f9",  # str x8,[sp,#0x20] local stats wrapper +0
    0xC96D9C: "080540b9",  # ldr w8,[x8,#4] stats record count
    0xC96DB0: "28034079",  # ldrh input mesh count [x25]
    0xC96DB8: "29a340a9",  # ldp input mesh ptr0/ptr1 [x25,#8]
    0xC96DC0: "29a341a9",  # ldp input mesh ptr2/ptr3 [x25,#0x18], ends +0x28
    0xC96DC8: "08034079",  # ldrh output mesh count [x24]
    0xC96DD0: "09a340a9",  # ldp output mesh ptr0/ptr1 [x24,#8]
    0xC96DD8: "09a341a9",  # ldp output mesh ptr2/ptr3 [x24,#0x18], ends +0x28
    0xC96DE0: "f4240094",  # bl embedded core 0xca01b0
    # Preprocessor: exactly 0x300 records; stride 0x32 or 0x64 from bit1.
    0xC9F47C: "0d608052",  # mov w13,#0x300
    0xC9F488: "880c80d2",  # mov x8,#0x64
    0xC9F490: "3f011f72",  # tst w9,#2
    0xC9F494: "490680d2",  # mov x9,#0x32
    0xC9F4A8: "48914079",  # ldrh +0x48
    0xC9F4BC: "480d42a9",  # ldp +0x20/+0x28
    0xC9F4CC: "48994079",  # ldrh +0x4c
    0xC9F4DC: "481543a9",  # ldp +0x30/+0x38
    0xC9F4F0: "489d4079",  # ldrh +0x4e
    0xC9F510: "48954079",  # ldrh +0x4a
    0xC9F560: "2df9ff35",  # cbnz w13, loop
    # Embedded core: independently uses same layout selector/count structure.
    0xCA02B8: "080b40b9",  # ldr w8,[x24,#8]
    0xCA02BC: "1f010c71",  # cmp w8,#0x300
    0xCA0318: "4f0680d2",  # mov x15,#0x32
    0xCA0324: "8e0c80d2",  # mov x14,#0x64
    0xCA0330: "080340f9",  # ldr x8,[x24] actual stats pointer
    0xCA0338: "0d0140b9",  # ldr w13,[x8] stats word0
    0xCA033C: "ad011f12",  # and w13,w13,#2
    0xCA034C: "19018052",  # mov w25,#8 inner iterations
    0xCA0364: "459c4079",  # ldrh +0x4e highest u16 read
    0xCA0370: "431443a9",  # ldp +0x30/+0x38
    0xCA0390: "45984079",  # ldrh +0x4c
    0xCA0518: "ff600071",  # cmp w7,#0x18 outer iterations
}

GEOMETRY = {
    "full_width": 4048,
    "full_height": 3152,
    "output_width": 3840,
    "output_height": 2160,
    "offset_x": 104,
    "offset_y": 496,
    "scale": 1,
}
GEOMETRY_OFFSETS = {
    "full_width": 0x1C,
    "full_height": 0x20,
    "output_width": 0x24,
    "output_height": 0x28,
    "offset_x": 0x2C,
    "offset_y": 0x30,
    "scale": 0x3C,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def u64(buf: bytes, off: int) -> int:
    return struct.unpack_from("<Q", buf, off)[0]


def verify_code_bytes(dll: Path) -> dict[str, str]:
    if sha256_file(dll) != DEVICE_MFT_SHA256:
        raise RuntimeError("DeviceMFT SHA-256 mismatch")
    pe = pefile.PE(str(dll), fast_load=True)
    raw = dll.read_bytes()
    proved = {}
    for rva, expected_hex in CODE_BYTES.items():
        off = pe.get_offset_from_rva(rva)
        actual = raw[off:off + 4].hex()
        if actual != expected_hex:
            raise RuntimeError(f"code mismatch at RVA 0x{rva:x}: {actual} != {expected_hex}")
        proved[f"0x{rva:x}"] = actual
    return proved


def decode_common(capture_dir: Path, request: int) -> dict:
    common_path = capture_dir / f"REQ{request}_LSC_COMMON.bin"
    staging_path = capture_dir / f"REQ{request}_LSC_STAGING.bin"
    common = common_path.read_bytes()
    staging = staging_path.read_bytes()
    if len(common) != 0x1E8:
        raise RuntimeError(f"request{request}: LSC common size {len(common):#x} != 0x1e8")
    if len(staging) < 0xDF0:
        raise RuntimeError(f"request{request}: LSC staging too short")
    if sha256_bytes(common) != COMMON_SHA256[request]:
        raise RuntimeError(f"request{request}: LSC common SHA mismatch")
    if sha256_bytes(staging) != STAGING_SHA256[request]:
        raise RuntimeError(f"request{request}: LSC staging SHA mismatch")

    geometry = {name: u32(common, off) for name, off in GEOMETRY_OFFSETS.items()}
    if geometry != GEOMETRY:
        raise RuntimeError(f"request{request}: geometry mismatch {geometry!r}")

    state = {
        "config_pointer": u64(common, 0x90),
        "wrapper_config_pointer": u64(common, 0x98),
        "tintless_stats_pointer": u64(common, 0xA0),
        "alsc_awbbg_pointer": u64(common, 0xA8),
        "tintless_interface_pointer": u64(common, 0xB0),
        "alsc_interface_pointer": u64(common, 0xB8),
        "tintless_enable": u32(common, 0xC0),
        "correction_table_pointers": [u64(common, off) for off in (0xD0, 0xD8, 0xE0, 0xE8)],
        "alsc_scratch_pointer": u64(common, 0xF8),
        "alsc_scratch_bytes": u32(common, 0x100),
        "alsc_enable": u32(common, 0x10C),
        "alsc_state_words": [u32(common, off) for off in (0x110, 0x114, 0x118, 0x11C, 0x120)],
        "alsc_metadata_halfwords": [u16(common, 0x128), u16(common, 0x12A)],
    }
    if not state["config_pointer"] or not state["wrapper_config_pointer"]:
        raise RuntimeError(f"request{request}: required LSC config pointers are null")
    if not state["tintless_stats_pointer"] or not state["tintless_interface_pointer"]:
        raise RuntimeError(f"request{request}: Tintless pointers are null")
    if state["tintless_enable"] != 1:
        raise RuntimeError(f"request{request}: Tintless not enabled")
    if state["alsc_awbbg_pointer"] != 0 or state["alsc_interface_pointer"] != 0 or state["alsc_enable"] != 0:
        raise RuntimeError(f"request{request}: live session is no longer Tintless-only")
    if any(state["alsc_state_words"]) or any(state["alsc_metadata_halfwords"]):
        raise RuntimeError(f"request{request}: unexpected ALSC state")
    if not all(state["correction_table_pointers"]):
        raise RuntimeError(f"request{request}: correction table pointer is null")
    if state["alsc_scratch_bytes"] != 0xC000:
        raise RuntimeError(f"request{request}: ALSC scratch size changed")

    return {
        "geometry": geometry,
        "state": state,
        "common_sha256": sha256_bytes(common),
        "staging_sha256": sha256_bytes(staging),
        "staging_dynamic_prefix_sha256": sha256_bytes(staging[:0xDF0]),
        "staging_static_tail_sha256": sha256_bytes(staging[0xDF0:]),
    }


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--device-mft",
        type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
    )
    parser.add_argument("--capture-dir", type=Path, default=here / "windows-adaptive-live-20260902")
    parser.add_argument("--out", type=Path, default=here / "lsc-live-tintless-boundary-oracle.json")
    args = parser.parse_args()

    code_proofs = verify_code_bytes(args.device_mft)
    requests = {r: decode_common(args.capture_dir, r) for r in (4, 5, 6)}

    # Request-local stats buffers must really be request-local in this capture.
    stats_ptrs = [requests[r]["state"]["tintless_stats_pointer"] for r in (4, 5, 6)]
    if len(set(stats_ptrs)) != 3:
        raise RuntimeError("Tintless stats pointers unexpectedly alias across requests4/5/6")

    # Stable producer objects/tables across the three observed requests.
    for field in ("config_pointer", "wrapper_config_pointer", "tintless_interface_pointer", "correction_table_pointers"):
        values = [requests[r]["state"][field] for r in (4, 5, 6)]
        if not all(v == values[0] for v in values[1:]):
            raise RuntimeError(f"expected stable field changed across requests: {field}")

    # The exact readers process record indices 0..767.  Their highest per-record
    # access ends at +0x50, independently proved in both preprocessor and core.
    records = 0x300
    highest_read_end = 0x50
    ordinary_stride = 0x32
    saturated_stride = 0x64
    ordinary_bound = (records - 1) * ordinary_stride + highest_read_end
    saturated_bound = (records - 1) * saturated_stride + highest_read_end
    if ordinary_bound != 0x961E or saturated_bound != 0x12BEC:
        raise RuntimeError("Tintless stats-bound arithmetic regression")

    cal = {}
    for index in range(4):
        path = args.capture_dir / f"REQ4_LSC_CAL{index}.bin"
        data = path.read_bytes()
        if len(data) != 0x374 or sha256_bytes(data) != CAL_SHA256[index]:
            raise RuntimeError(f"REQ4_LSC_CAL{index}: size/hash mismatch")
        values = struct.unpack("<221f", data)
        cal[str(index)] = {
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "min_float": min(values),
            "max_float": max(values),
        }

    # Do not serialize ASLR/process addresses into the tracked oracle; only their
    # null/stability/request-local classification is useful beyond this run.
    public_requests = {}
    for r in (4, 5, 6):
        state = requests[r]["state"]
        public_requests[f"request{r}"] = {
            "common_sha256": requests[r]["common_sha256"],
            "staging_sha256": requests[r]["staging_sha256"],
            "staging_dynamic_prefix_sha256": requests[r]["staging_dynamic_prefix_sha256"],
            "staging_static_tail_sha256": requests[r]["staging_static_tail_sha256"],
            "geometry": requests[r]["geometry"],
            "tintless_enable": state["tintless_enable"],
            "tintless_stats_pointer_nonzero": bool(state["tintless_stats_pointer"]),
            "tintless_interface_pointer_nonzero": bool(state["tintless_interface_pointer"]),
            "alsc_awbbg_pointer_null": state["alsc_awbbg_pointer"] == 0,
            "alsc_interface_pointer_null": state["alsc_interface_pointer"] == 0,
            "alsc_enable": state["alsc_enable"],
            "alsc_state_zero": not any(state["alsc_state_words"] + state["alsc_metadata_halfwords"]),
            "correction_table_pointers_nonzero": all(state["correction_table_pointers"]),
        }

    oracle = {
        "schema": "sp11-e003h-0073-lsc-live-tintless-boundary-v1",
        "accepted": True,
        "classification": "CLOSED LIVE/STATIC INPUT BOUNDARY: the 2026-09-02 IFELSC411 adaptive path is Tintless-only (ALSC disabled), and the exact request-local Tintless stats object is bounded to 0x961e or 0x12bec bytes after a 0x300-record/bit1 layout check.",
        "safety": {
            "linux_camera_runtime_executed": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
            "raw_windows_captures_tracked": False,
        },
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA256,
            "capture_zip_sha256": CAPTURE_ZIP_SHA256,
            "capture_session": "E003H_ADAPTIVE_0073_LIVE_20260902",
        },
        "exact_functions": {
            "tintless_wrapper_process_rva": "0xc95fd0",
            "tintless_stats_preprocess_rva": "0xc9f438",
            "embedded_tintless_core_rva": "0xca01b0",
            "embedded_tintless_fuse_stats_rva": "0xca1410",
        },
        "capture_abi_code_byte_proofs": code_proofs,
        "wrapper_entry_capture_contract": {
            "entry_rva": "0xc95fd0",
            "x0": "Tintless interface object; wrapper context pointer is poi(x0+0x18)",
            "x1_config_bytes": "0x130",
            "x1_config_proof": "wrapper compares/copies chunks through final x1+0x58 length 0xd8 and directly reads through x1+0x12c; end-exclusive bound is 0x130",
            "x2_stats_bytes": "conditional 0x961e or 0x12bec after record-count/bit1 validation",
            "x3_input_mesh_descriptor_bytes": "0x28",
            "x4_output_mesh_descriptor_bytes": "0x28",
            "mesh_count_required": 221,
            "mesh_arrays": "four pointers per descriptor at +0x08,+0x10,+0x18,+0x20; each points to 221 float32 values = 0x374 bytes",
            "input_mesh_payload_bytes": "0xdf0 total across four 0x374 arrays",
            "post_call_validation_payload_bytes": "0xdf0 total across four output arrays",
            "capture_use": "At wrapper entry this isolates the exact adaptive transform from earlier Chromatix/calibration interpolation. Capture x1, validated x2, x3 descriptor+four input meshes and persistent wrapper/core state; after return hash/dump the four x4 output meshes.",
        },
        "stats_contract": {
            "stats_record_count_dword_offset": "0x4",
            "required_record_count": 768,
            "layout_selector": "bit1 of first dword at stats+0",
            "ordinary_stride_bytes": ordinary_stride,
            "ordinary_max_read_bytes": ordinary_bound,
            "ordinary_max_read_hex": f"0x{ordinary_bound:x}",
            "saturated_stride_bytes": saturated_stride,
            "saturated_max_read_bytes": saturated_bound,
            "saturated_max_read_hex": f"0x{saturated_bound:x}",
            "highest_per_record_read_end": "0x50",
            "records_covered": "indices 0..767",
            "fail_closed_sequence": [
                "Read stats+4 first and require exactly 0x300 records.",
                "Read stats word0 and inspect bit1.",
                "If bit1 is clear, capture exactly 0x961e bytes from stats base.",
                "If bit1 is set, capture exactly 0x12bec bytes from stats base.",
                "Do not classify or replay an object that fails those checks as this Surface Tintless layout.",
            ],
        },
        "live_path": {
            "geometry": GEOMETRY,
            "tintless_enabled": True,
            "tintless_stats_request_local": True,
            "tintless_interface_stable": True,
            "alsc_enabled": False,
            "alsc_awbbg_pointer_present": False,
            "alsc_interface_present": False,
            "correction_table_pointers_stable": True,
            "req4_correction_table_snapshots": cal,
        },
        "requests": public_requests,
        "validation_shortcut_state": {
            "tintless_interface_source": "common+0xb0",
            "wrapper_context_pointer": "poi(tintless_interface+0x18)",
            "wrapper_context_bytes": "0x1090",
            "lazy_core_state_pointer": "poi(wrapper_context+0x128)",
            "lazy_core_state_bytes_when_nonnull": "0x126e8",
            "previous_mesh_history_bytes": "0xdf0 within wrapper context",
            "policy": "A pre-request context snapshot is validation-only. Final Linux parity must evolve the same Tintless state sequentially.",
        },
        "next_capture": {
            "preferred": "In one Windows stream, hook TintlessAlgorithmWrapper::Process at RVA 0xc95fd0 from stream creation through the target request. Per call capture x1[0:0x130], validated x2 stats at 0x961e/0x12bec, x3[0:0x28] plus its four 0x374 input meshes, and same-stream output meshes/wire LSC correlation.",
            "validation_shortcut": "Capture a pre-request wrapper context (0x1090) and non-null lazy core state (0x126e8), then capture validated request-local Tintless stats for requests4/5/6.",
            "also_preserve": "For full pre-wrapper reconstruction, preserve upstream calibration/config state separately. For isolating Tintless itself, the exact wrapper-entry x1 bound is now 0x130 and the four input meshes total 0xdf0 bytes; do not infer bytes from process pointers alone.",
            "not_needed_in_this_session": "ALSC/AWB-BG stats, because common+0xa8/common+0xb8 are null and common+0x10c is zero for requests4/5/6.",
        },
        "gate": "Tintless input sizing and the ALSC-disabled branch are closed. The next parity gate is one atomic same-stream LSC capture/replay: calibration/config + exact 4048x3152/(104,496)->3840x2160 geometry + sequential Tintless state/stats must reproduce LSC0/LSC1 byte-for-byte. Wire GIC follows the proven LSC alias. Linux request6 remains forbidden.",
    }

    args.out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS live Tintless boundary")
    print(f"  ordinary stats bound: 0x{ordinary_bound:x} ({ordinary_bound} bytes)")
    print(f"  saturated stats bound: 0x{saturated_bound:x} ({saturated_bound} bytes)")
    print(f"  geometry: {GEOMETRY}")
    print("  live adaptive branch: Tintless=on ALSC=off")
    print(f"  oracle: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
