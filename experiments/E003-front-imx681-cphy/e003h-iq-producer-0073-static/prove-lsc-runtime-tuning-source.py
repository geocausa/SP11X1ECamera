#!/usr/bin/env python3
"""Fail-closed proof of the live Windows LSC41 runtime tuning source.

This proof supersedes the earlier hypothesis that the Surface runtime transforms
serialized IMX681 LSC leaves before generic interpolation.  The live generic
interpolation result is reproduced byte-for-byte from two exact 0xdf0 region
payloads serialized in the Surface rear OV13858 tuning package, using the exact
front-stream trigger vector captured from Windows and the exact arithmetic used
by DeviceMFT's generic interpolation callback.

No Linux camera runtime is performed or authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

FRONT_SHA256 = "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d"
REAR_SHA256 = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
A_SHA256 = "d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d"
B_SHA256 = "f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8"
A_SID = 0x2A0
B_SID = 0x2A4
A_ABS_OFFSET = 1008426
B_ABS_OFFSET = 1012018
LSC_MODULE_SID = 0x29
REVISION_SID = 0x293
CONTROL_SID = 0x294
TRIGGER_ROOT_SID = 0x295
LSC_CONTROLS = (8, 2, 5, 100, 0, 6)
LSC_VECTOR_INDICES = (8, 2, 5, 19, 20, 21, 0, 6)
EXPECTED_X22 = {
    "request5": "e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de",
    "request6": "3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8",
}
EXPECTED_VECTOR = {
    "request5": [400.93280029296875,18.924766540527344,1.0,1.0,1.0,1.0,4999.0,0.0,370.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
    "request6": [400.27227783203125,27.208637237548828,1.0,1.0,1.0,1.0,4999.0,0.0,370.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
}
CAPTURE_FILES = {
    "request5": ("REQ5_TRIGVEC_DATA_0100.bin", "REQ5_X22_RAW_0DF0.bin"),
    "request6": ("REQ6_TRIGVEC_DATA_0100.bin", "REQ6_X22_RAW_0DF0.bin"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def load_decoder(path: Path):
    spec = importlib.util.spec_from_file_location("chromatix_decode", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tuning decoder")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record_bytes(blob: bytes, objsec: dict, rec: dict) -> bytes:
    start = objsec["offset"] + rec["data_offset"]
    return blob[start:start + rec["data_bytes"]]


def assert_u32_words(raw: bytes, expected: tuple[int, ...], label: str) -> None:
    got = struct.unpack("<" + "I" * (len(raw) // 4), raw)
    if got != expected:
        raise RuntimeError(f"{label}: serialized words drift: {got!r}")


def interpolate_callback(a: bytes, b: bytes, ratio: float) -> bytes:
    """Reproduce DeviceMFT RVA 0x93c940 arithmetic.

    ARM64 converts each float32 endpoint and the float32 ratio to float64,
    evaluates (B-A)*ratio + A in float64, then converts once to float32.
    The eight integer tail words are equal for the two selected regions in this
    live branch, so their interpolated result is exactly the same tail.
    """
    if len(a) != 0xDF0 or len(b) != 0xDF0:
        raise RuntimeError("interpolation inputs are not 0xdf0 bytes")
    af = struct.unpack("<884f", a[:0xDD0])
    bf = struct.unpack("<884f", b[:0xDD0])
    out = bytearray(0xDF0)
    for i, (av, bv) in enumerate(zip(af, bf)):
        value = f32((float(bv) - float(av)) * float(ratio) + float(av))
        struct.pack_into("<f", out, i * 4, value)
    if a[0xDD0:] != b[0xDD0:]:
        raise RuntimeError("selected region tail words unexpectedly differ")
    out[0xDD0:] = a[0xDD0:]
    return bytes(out)


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--front-tuning", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin"))
    ap.add_argument("--rear-tuning", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin"))
    ap.add_argument("--decoder", type=Path, default=here / "decode_imx681_chromatix.py")
    ap.add_argument("--capture-dir", type=Path, default=Path("/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_LSCTRIGSRC"))
    ap.add_argument("--callback-dir", type=Path, default=Path("/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_LSCCALLBACK"))
    ap.add_argument("--out", type=Path, default=here / "lsc-runtime-tuning-source-oracle.json")
    args = ap.parse_args()

    if sha_file(args.front_tuning) != FRONT_SHA256:
        raise RuntimeError("front IMX681 tuning SHA mismatch")
    if sha_file(args.rear_tuning) != REAR_SHA256:
        raise RuntimeError("rear OV13858 tuning SHA mismatch")

    dec = load_decoder(args.decoder)
    rear = args.rear_tuning.read_bytes()
    front = args.front_tuning.read_bytes()
    header = dec.parse_header(rear)
    if header["module_name"] != "com.surface.tuned.rfc_ov13858":
        raise RuntimeError("rear tuning module-name drift")
    records, _ = dec.parse_symbol_table(rear, header["sections"][0], header["sections"][1])
    objsec = header["sections"][1]

    module = records[LSC_MODULE_SID]
    if module["type"] != "lsc41_ife_v2" or module["mode_symbol_id"] != 2:
        raise RuntimeError("rear default LSC41 module identity drift")
    module_raw = record_bytes(rear, objsec, module)
    if len(module_raw) != 68:
        raise RuntimeError("rear LSC41 module size drift")
    words = struct.unpack("<17I", module_raw)
    if words[6] != REVISION_SID or words[8] != CONTROL_SID or words[16] != TRIGGER_ROOT_SID:
        raise RuntimeError("rear LSC41 module pointer chain drift")

    controls = record_bytes(rear, objsec, records[CONTROL_SID])
    got_controls = struct.unpack("<6I", controls)
    if got_controls != LSC_CONTROLS:
        raise RuntimeError(f"rear LSC controls drift: {got_controls!r}")

    # Exact selected trigger topology.  Each 24-byte tuple is
    # start(float), end(float), child-trigger-count, child-trigger-SID,
    # region-count, region-SID.  The 0x299 level is selector 0 from the
    # control vector, i.e. live trigger-vector index 0.  Its two populated
    # bands leave a [340,430] interpolation gap.
    assert_u32_words(record_bytes(rear, objsec, records[0x295]),
                     (0x3F800000,0x42C80000,1,0x296,0,0x2A9), "sid 0x295")
    assert_u32_words(record_bytes(rear, objsec, records[0x296]),
                     (0x3F800000,0x42C80000,1,0x297,0,0x2A8), "sid 0x296")
    assert_u32_words(record_bytes(rear, objsec, records[0x297]),
                     (0x3F800000,0x42800000,1,0x298,0,0x2A7), "sid 0x297")
    assert_u32_words(record_bytes(rear, objsec, records[0x298]),
                     (0,0,2,0x299,0,0x2A6), "sid 0x298")
    assert_u32_words(record_bytes(rear, objsec, records[0x299]),
                     (0x3F800000,0x43AA0000,3,0x29A,0,0x2A1,
                      0x43D70000,0x44610000,1,0x2A2,0,0x2A5), "sid 0x299")
    assert_u32_words(record_bytes(rear, objsec, records[0x29A]),
                     (0x3F800000,0x4541C000,0,0x29B,1,0x29C,
                      0x455AC000,0x45834000,0,0x29D,1,0x29E,
                      0x45960000,0x461C4000,0,0x29F,1,0x2A0), "sid 0x29a")
    assert_u32_words(record_bytes(rear, objsec, records[0x2A2]),
                     (0x3F800000,0x461C4000,0,0x2A3,1,0x2A4), "sid 0x2a2")

    arec = records[A_SID]
    brec = records[B_SID]
    if (arec["type"], arec["data_bytes"], arec["data_abs_offset"]) != ("region", 0xDF0, A_ABS_OFFSET):
        raise RuntimeError("rear A-region metadata drift")
    if (brec["type"], brec["data_bytes"], brec["data_abs_offset"]) != ("region", 0xDF0, B_ABS_OFFSET):
        raise RuntimeError("rear B-region metadata drift")
    a = record_bytes(rear, objsec, arec)
    b = record_bytes(rear, objsec, brec)
    if sha(a) != A_SHA256 or sha(b) != B_SHA256:
        raise RuntimeError("rear selected region SHA drift")
    if front.find(a) != -1:
        raise RuntimeError("runtime A region unexpectedly exists in front IMX681 tuning")

    requests = {}
    for req, (vec_name, x22_name) in CAPTURE_FILES.items():
        vec_raw = (args.capture_dir / vec_name).read_bytes()
        x22 = (args.capture_dir / x22_name).read_bytes()
        if len(vec_raw) != 0x100 or len(x22) != 0xDF0:
            raise RuntimeError(f"{req}: capture size drift")
        vec = list(struct.unpack("<64f", vec_raw))[:42]
        if vec != EXPECTED_VECTOR[req]:
            raise RuntimeError(f"{req}: live trigger-vector drift")
        if sha(x22) != EXPECTED_X22[req]:
            raise RuntimeError(f"{req}: live x22 SHA drift")

        mapped = [vec[i] for i in LSC_VECTOR_INDICES]
        # The first four selector levels each have a single live child.  The
        # selector-0 level at sid 0x299 consumes vec[0].  At CCT=vec[6]=4999,
        # its lower child resolves sid 0x2a0 (4800..10000) while the upper
        # child resolves sid 0x2a4 (1..10000).
        if vec[6] < 4800.0 or vec[6] > 10000.0:
            raise RuntimeError(f"{req}: CCT left the proven A-region band")
        trigger = f32(vec[0])
        if not (340.0 < trigger < 430.0):
            raise RuntimeError(f"{req}: selector-0 trigger left interpolation gap")
        ratio = f32(f32(trigger - f32(340.0)) / f32(f32(430.0) - f32(340.0)))
        replay = interpolate_callback(a, b, ratio)
        replay_sha = sha(replay)
        if replay != x22:
            raise RuntimeError(f"{req}: rear-tree replay is not byte-exact ({replay_sha})")
        requests[req] = {
            "trigger_vector_42": vec,
            "lsc_mapped_values": mapped,
            "selector0_trigger": trigger,
            "lower_band_end": 340.0,
            "upper_band_start": 430.0,
            "ratio_float32": ratio,
            "cct": vec[6],
            "lower_selected_region_sid": A_SID,
            "upper_selected_region_sid": B_SID,
            "replay_x22_sha256": replay_sha,
            "windows_x22_sha256": sha(x22),
            "byte_exact": True,
        }

    callback_observation = None
    a_cap = args.callback_dir / "REQ5_CB01_A_0DF0.bin"
    b_cap = args.callback_dir / "REQ5_CB01_B_0DF0.bin"
    if a_cap.exists() and b_cap.exists():
        ac = a_cap.read_bytes(); bc = b_cap.read_bytes()
        if ac != a or bc != b:
            raise RuntimeError("Windows generic-callback leaf capture disagrees with rear tuning regions")
        callback_observation = {
            "capture_session": args.callback_dir.name,
            "request5_call1_A_sha256": sha(ac),
            "request5_call1_B_sha256": sha(bc),
            "matches_rear_serialized_regions_byte_for_byte": True,
            "raw_capture_committed": False,
        }

    oracle = {
        "schema": "sp11-e003h-lsc-runtime-tuning-source-v1",
        "accepted": True,
        "classification": "CLOSED BYTE-EXACT LSC41 RUNTIME INTERPOLATION SOURCE: the live front stream's generic pre-calibration x22 is reproduced exactly from Surface rear OV13858 default LSC41 regions 0x2a0/0x2a4, selected by the exact live front trigger vector and DeviceMFT interpolation arithmetic.",
        "front_tuning_sha256": FRONT_SHA256,
        "rear_tuning": {
            "sha256": REAR_SHA256,
            "module_name": header["module_name"],
            "default_lsc41_symbol_id": LSC_MODULE_SID,
            "revision_symbol_id": REVISION_SID,
            "control_symbol_id": CONTROL_SID,
            "trigger_root_symbol_id": TRIGGER_ROOT_SID,
            "controls": list(LSC_CONTROLS),
            "runtime_A_region": {"symbol_id": A_SID, "abs_offset": A_ABS_OFFSET, "sha256": A_SHA256},
            "runtime_B_region": {"symbol_id": B_SID, "abs_offset": B_ABS_OFFSET, "sha256": B_SHA256},
            "runtime_A_absent_from_front_imx681_blob": True,
        },
        "selection": {
            "lsc_vector_indices": list(LSC_VECTOR_INDICES),
            "selector0_interpolation_gap": [340.0, 430.0],
            "lower_branch_cct_region": [4800.0, 10000.0],
            "upper_branch_cct_region": [1.0, 10000.0],
            "callback_rva": "0x93c940",
            "callback_arithmetic": "float32 ratio; endpoints converted float32->float64; (B-A)*ratio+A in float64; one float64->float32 conversion",
        },
        "requests": requests,
        "callback_observation": callback_observation,
        "supersedes": "The prior hypothesis that runtime Chromatix must numerically transform the five serialized IMX681 LSC leaves. The missing A leaf is exact serialized data from the rear/default Surface LSC41 package, not a transformed IMX681 mesh.",
        "remaining_provenance_question": "Why the front stream's resolved tuning root exposes the rear/default LSC41 branch is still an object-loader/overlay provenance question. It no longer blocks reproducing LSC41 x22 byte-for-byte.",
        "cross_session_correction": {
            "tintctx_camera_identity": "OV13858 rear mode1, not verified front",
            "proof": "prove-lsc-tintctx-camera-identity.py",
            "live_golden_proof": "prove-lsc-live-golden-authority.py",
        },
        "next_gate": "Keep this byte-exact front x22 source with recovered front x23/geometry/staging evidence and mine a same-front-stream Tintless bridge. Do not splice the rear-mode1 TINTCTX sequential replay into front LSCTRIGSRC. Keep Linux request6 fail-closed.",
        "safety": {"linux_camera_runtime": False, "linux_request6_executed": False, "linux_request6_authorized": False},
    }
    args.out.write_text(json.dumps(oracle, indent=2) + "\n")
    print("PASS byte-exact live LSC41 runtime tuning source")
    print("  rear A", A_SHA256, "sid=0x2a0 off=1008426")
    print("  rear B", B_SHA256, "sid=0x2a4 off=1012018")
    for req in ("request5", "request6"):
        row = requests[req]
        print(" ", req, "trigger", row["selector0_trigger"], "ratio", row["ratio_float32"], "x22", row["replay_x22_sha256"], "BYTE-EXACT")
    print("  oracle", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
