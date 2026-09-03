#!/usr/bin/env python3
"""Fail-closed native replay of the verified-front request4 LSC pre-Tintless bridge.

This proof performs no Linux camera runtime.  It derives request4's exact generic
LSC triggers from the captured front ISPInputData, walks the already-identified
rear/default LSC41 tree, applies the proven rear/default golden + rear runtime
EEPROM calibration authority, then executes the exact Surface ARM64 geometry
resampler (QcDeviceMFT8380.dll RVA 0x9b6048) under Unicorn.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

try:
    import pefile
except Exception as exc:
    raise SystemExit(f"missing proof dependency pefile: {exc}")

HERE = Path(__file__).resolve().parent
DEVICE_MFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
REAR_TUNING_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
REAR_GOLDEN_SHA = "f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6"
REAR_SLOT_SHA = "fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18"
REQ4_ISP_SHA = "775adcc5fe378bcd4105c8abdef5c5a745c155f58a4bd5c27de4f55fc09a60d3"
REQ4_COMMON_SHA = "646e62de0d5192129ba03bcc285cc5928c231ab24bf1d83ed236513c59c20535"
EXPECTED_X22_SHA = "99bf4e1dd6d500aa81cdb4f6e0f6e0b1f23bb953748be84ff451f6a71fe3d84f"
EXPECTED_X23_SHA = "a24bba7c3d9cd6db545f65801006defd154f2da412bb101805cf9b45e23dfcde"
EXPECTED_PRETINT_SHA = "839cae7d7b1c884b77068f0cb76d6ce34fbed562ac1328a59ea4373a30ab88c9"
EXPECTED_CHANNEL_SHA = (
    "d0b36a767d3aadb35ec8b6ead29d97f67a11575d43a7d945e455fc5148b995a8",
    "c6cdd5199db09233dce2bef205521041f4fa5e69f1b399705d26d4d7e62b2e28",
    "c6cdd5199db09233dce2bef205521041f4fa5e69f1b399705d26d4d7e62b2e28",
    "20f2ef9db2c811a983f1a31fdbb38c222de8a205fdba26474e6a3995bff6b9f2",
)
EXPECTED_REGIONS = {
    0x29E: "be1cd0ee75cbb06f3923948195ae4b95f516d29997c4af2501b3fd5ae72a78c7",
    0x2A0: "d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d",
    0x2A4: "f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8",
}
# Raw PE byte slices, not disassembler word order.
CODE = {
    # ldr w8,[x19,#0x108]; mov x0,x19; cmp w8,#1; b.ne 0x1809b4d54
    0x9B4C68: "680a41b9e00313aa1f05007101070054",
    # active common+0x108 != 1 branch begins with resample, then config/Tintless setup
    0x9B4D54: "e10314aa86070094e7d30091ff0300b9e6e30091e5f30091e4030191e30316aae20317aae10315aae00313aa72030094",
    # exact Surface resampler entry prefix
    0x9B6048: "7f2303d5fd7bb6a9f35301a9f55b02a9f76303a9f96b04a9fb2b00f9e8a7056d",
}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def need(value, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def verify_code(dll: Path) -> dict[str, str]:
    need(sha_file(dll) == DEVICE_MFT_SHA, "DeviceMFT SHA mismatch")
    raw = dll.read_bytes()
    pe = pefile.PE(str(dll), fast_load=True)
    out = {}
    for rva, expected in CODE.items():
        size = len(expected) // 2
        got = raw[pe.get_offset_from_rva(rva):pe.get_offset_from_rva(rva) + size].hex()
        need(got == expected, f"code mismatch RVA 0x{rva:x}: {got} != {expected}")
        out[f"0x{rva:x}"] = got
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device-mft", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"))
    ap.add_argument("--rear-tuning", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin"))
    ap.add_argument("--out", type=Path, default=HERE / "lsc-front-request4-pretintless-bridge-oracle.json")
    args = ap.parse_args()

    code = verify_code(args.device_mft)
    need(sha_file(args.rear_tuning) == REAR_TUNING_SHA, "rear tuning SHA mismatch")
    rt = load_module("runtime_lsc", HERE / "prove-lsc-runtime-tuning-source.py")
    ga = load_module("golden_lsc", HERE / "prove-lsc-live-golden-authority.py")
    em = load_module("surface_emu", HERE / "prove-gtm-live-exact-replay.py")
    ca = load_module("calibration_authority", HERE / "prove-lsc-front-rear-calibration-authority.py")

    # Exact rear/default LSC41 serialized regions.
    blob = args.rear_tuning.read_bytes()
    dec = rt.load_decoder(HERE / "decode_imx681_chromatix.py")
    header = dec.parse_header(blob)
    records, _ = dec.parse_symbol_table(blob, header["sections"][0], header["sections"][1])
    objsec = header["sections"][1]

    def region(sid: int) -> bytes:
        raw = rt.record_bytes(blob, objsec, records[sid])
        need(len(raw) == 0xDF0, f"region 0x{sid:x} size drift")
        need(sha_bytes(raw) == EXPECTED_REGIONS[sid], f"region 0x{sid:x} SHA drift")
        return raw

    # Front request4 inputs. SetupGenericTrigger mapping is independently pinned by
    # prove-lsc-front-rear-calibration-authority.py: vector0=+0x20b8, vector6=+0x20c8.
    cap = HERE / "windows-adaptive-live-20260902"
    isp_path = cap / "REQ4_ISPINPUT.bin"
    common_path = cap / "REQ4_LSC_COMMON.bin"
    need(sha_file(isp_path) == REQ4_ISP_SHA, "request4 ISPInput SHA mismatch")
    need(sha_file(common_path) == REQ4_COMMON_SHA, "request4 LSC common SHA mismatch")
    isp = isp_path.read_bytes()
    common = common_path.read_bytes()
    need(len(isp) >= 0x20CC and len(common) == 0x1E8, "request4 capture size drift")
    lux = struct.unpack_from("<f", isp, 0x20B8)[0]
    cct = struct.unpack_from("<f", isp, 0x20C8)[0]
    need(struct.pack("<f", lux) == struct.pack("<f", 355.14508056640625), f"request4 lux drift {lux}")
    need(struct.pack("<f", cct) == struct.pack("<f", 4712.0), f"request4 CCT drift {cct}")

    geometry = struct.unpack_from("<9I", common, 0x1C)
    expected_geometry = (4048, 3152, 3840, 2160, 104, 496, 0, 0, 1)
    need(geometry == expected_geometry, f"request4 geometry drift {geometry!r}")
    tintless_enable = struct.unpack_from("<I", common, 0xC0)[0]
    resample_after_tintless_selector = struct.unpack_from("<I", common, 0x108)[0]
    need(tintless_enable == 1, "request4 Tintless enable drift")
    need(resample_after_tintless_selector == 0, "request4 common+0x108 branch drift")

    f32 = rt.f32
    def sub(a, b): return f32(f32(a) - f32(b))
    def div(a, b): return f32(f32(a) / f32(b))

    cct_ratio = div(sub(cct, f32(4200.0)), sub(f32(4800.0), f32(4200.0)))
    lux_ratio = div(sub(lux, f32(340.0)), sub(f32(430.0), f32(340.0)))
    need(struct.pack("<f", cct_ratio) == struct.pack("<f", 0.8533333539962769), "request4 CCT ratio drift")
    need(struct.pack("<f", lux_ratio) == struct.pack("<f", 0.16827867925167084), "request4 lux ratio drift")

    lower = rt.interpolate_callback(region(0x29E), region(0x2A0), cct_ratio)
    x22 = rt.interpolate_callback(lower, region(0x2A4), lux_ratio)
    need(sha_bytes(x22) == EXPECTED_X22_SHA, f"request4 x22 SHA drift {sha_bytes(x22)}")

    golden_info = ga.parse_golden(args.rear_tuning)
    need(golden_info and golden_info["golden_region_sha256"] == REAR_GOLDEN_SHA, "rear golden authority drift")
    slot_path = HERE / "oracle-vss-20260902-local" / "REQ1_LSC_CAL_SLOT_0DF0.bin"
    need(sha_file(slot_path) == REAR_SLOT_SHA, "rear runtime slot SHA drift")
    channels, _ = ca.parse_slot(slot_path.read_bytes())
    eeprom_flat = [float(v) for ch in channels for v in ch]
    x23 = ca.calibrate_full(x22, golden_info["values"], eeprom_flat)
    need(sha_bytes(x23) == EXPECTED_X23_SHA, f"request4 calibrated x23 SHA drift {sha_bytes(x23)}")
    x23f = struct.unpack("<884f", x23[:0xDD0])
    need(x23f[221:442] == x23f[442:663], "calibrated request4 green planes differ")

    # Execute the exact native Surface resampler for each calibrated channel.
    surface = em.SurfaceEmu(args.device_mft)
    uc = surface.uc
    src = surface.heap + 0x10000
    dst = surface.heap + 0x20000
    sp = surface.stack + 0x3FF000
    # AAPCS64 stack args for 0x9b6048: param9=scale=1, param10=scale=1,
    # param11/12 unused here, param13=0 selects the normal gain clamp path.
    uc.mem_write(sp, struct.pack("<QQQQQ", 1, 1, 0, 0, 0))
    channel_raw = []
    channel_summary = []
    for channel in range(4):
        in_raw = struct.pack("<221f", *x23f[channel * 221:(channel + 1) * 221])
        uc.mem_write(src, in_raw)
        uc.mem_write(dst, bytes(0x374))
        surface.run(
            0x9B6048,
            xargs=(src, dst, 4048, 3152, 3840, 2160, 104, 496),
            instruction_limit=20_000_000,
        )
        raw = bytes(uc.mem_read(dst, 0x374))
        digest = sha_bytes(raw)
        need(digest == EXPECTED_CHANNEL_SHA[channel], f"native resampler channel{channel} SHA drift {digest}")
        values = struct.unpack("<221f", raw)
        channel_raw.append(raw)
        channel_summary.append({
            "channel": channel,
            "sha256": digest,
            "min_float": min(values),
            "max_float": max(values),
            "first8": list(values[:8]),
        })

    pretint = b"".join(channel_raw)
    need(len(pretint) == 0xDD0, "pre-Tintless mesh size drift")
    need(sha_bytes(pretint) == EXPECTED_PRETINT_SHA, f"pre-Tintless mesh SHA drift {sha_bytes(pretint)}")
    need(channel_raw[1] == channel_raw[2], "native resampler broke equal green planes")

    oracle = {
        "schema": "sp11-e003h-lsc-front-request4-pretintless-bridge-v1",
        "status": "PASS",
        "classification": "CLOSED OFFLINE FRONT REQUEST4 PRE-TINTLESS BRIDGE: exact request4 generic triggers select rear/default LSC41 x22, rear/default golden plus the proven rear runtime EEPROM slot produce calibrated x23, and native Surface RVA 0x9b6048 produces the deterministic front geometry-resampled Tintless input.",
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA,
            "rear_tuning_sha256": REAR_TUNING_SHA,
            "rear_golden_region_sha256": REAR_GOLDEN_SHA,
            "rear_runtime_slot_sha256": REAR_SLOT_SHA,
            "request4_ispinput_sha256": REQ4_ISP_SHA,
            "request4_lsc_common_sha256": REQ4_COMMON_SHA,
        },
        "active_branch": {
            "tintless_enable_common_0xc0": tintless_enable,
            "common_0x108": resample_after_tintless_selector,
            "ordering": "common+0x108 == 0: Surface executes geometry resample before the Tintless call",
            "code_byte_proofs": code,
        },
        "request4": {
            "generic_trigger_vector0_lux": lux,
            "generic_trigger_vector6_cct": cct,
            "cct_interpolation": {"lower_end": 4200.0, "upper_start": 4800.0, "ratio_float32": cct_ratio, "regions": ["0x29e", "0x2a0"]},
            "lux_interpolation": {"lower_end": 340.0, "upper_start": 430.0, "ratio_float32": lux_ratio, "upper_region": "0x2a4"},
            "geometry": {"full": [4048, 3152], "output": [3840, 2160], "offset": [104, 496], "scale_x": 0, "scale_y": 0, "scale": 1},
            "x22_sha256": EXPECTED_X22_SHA,
            "calibrated_x23_sha256": EXPECTED_X23_SHA,
            "native_resampler_rva": "0x9b6048",
            "pre_tintless_mesh_bytes": len(pretint),
            "pre_tintless_mesh_sha256": EXPECTED_PRETINT_SHA,
            "green_planes_equal": True,
            "channels": channel_summary,
        },
        "capture_timing_boundary": {
            "correction_tables": "REQ4_LSC_CAL0..3 were captured at CalculateSetting entry and are pre-request state",
            "staging": "REQ4_LSC_STAGING was captured after IQInterface LSC411 calculation at caller RVA 0xa03b34 and is post-request state",
            "rule": "Do not divide/multiply these pre-request correction snapshots against post-request staging as if they were same-request Tintless ratios.",
        },
        "next_gate": "Capture or recover a genuine verified-front sequential Tintless wrapper-entry capsule (config, validated stats, input/output meshes, and persistent state) and require native RVA 0xc95fd0 replay to bridge this pre-Tintless target into the captured front staging. Linux request6 remains forbidden.",
        "safety": {"linux_camera_runtime": False, "linux_request6_executed": False, "runtime_authorized": False},
    }
    args.out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS front request4 pre-Tintless bridge")
    print("  x22", EXPECTED_X22_SHA)
    print("  x23", EXPECTED_X23_SHA)
    print("  pre-Tintless", EXPECTED_PRETINT_SHA)
    print("  native channels", [x["sha256"] for x in channel_summary])
    print("  oracle", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
