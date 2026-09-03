#!/usr/bin/env python3
"""Fail-closed static/runtime-evidence proof of front LSC calibration object ownership.

This does *not* prove why the verified-front calibration bytes are rear/default-
equivalent.  It proves the normal DeviceMFT object/pointer path is camera-local:

  cameraId-strided HWEnvironment slot
    -> EEPROMData::FormatLSCData camera-local formatted LSC slot0
    -> ImageSensorData::GetSensorStaticCapability camera-local pOTPData copy
    -> IFENode::FetchSensorInfo m_pOTPData
    -> per-request ISPInputData+0x2070
    -> IFELSC411 +0x168 slot0 consumer.

Verified-front captured ISPInputData has camera=2; the preserved rear VSS
ISPInputData has camera=0.  Therefore an ordinary rear-camera0 formatted OTP
object/pointer cannot alias the front-camera2 object on this normal path.
No camera runtime is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile

DEVICE_MFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
CAL_BOUNDARY_PROOF_SHA = "5a5d5ef6534298c1c71f1b18344d75ac31af92b0d87e82a6fcb52fc50f18b48f"
CAL_BOUNDARY_ORACLE_SHA = "619f4338031c00cd50cbb8f6dfd652bfe8428db35ad0583dff45352c7cb63275"
AUTH_PROOF_SHA = "eb3f0738b5eeafca67bcac0b32eeb1b77d782935aa2ffb20d14adf01d7d7f575"
AUTH_ORACLE_SHA = "7da1adc5acfcb266a5167ffbbcb5b0b788b6bacff390fa907ba9c3b051722042"
REQ4_BRIDGE_PROOF_SHA = "677ed7834bdefe4d8d1f3548038475586a8f3130cdacb67c048003bb135d9093"
REQ4_BRIDGE_ORACLE_SHA = "d3dcb3eebfdf1f6bda13ab220c27573c5cd2308577214721c49ffa84fdc0926b"

FRONT_ISP = {
    4: ("REQ4_ISPINPUT.bin", "775adcc5fe378bcd4105c8abdef5c5a745c155f58a4bd5c27de4f55fc09a60d3"),
    5: ("REQ5_ISPINPUT.bin", "7328b1902709ad981ae180ddf600288890399987547ad7b338a0ba298b12886b"),
    6: ("REQ6_ISPINPUT.bin", "c51a7b54cf03683fd86df0967c82f358e2332d00d382c2f5cdb1c020b6cca874"),
}
REAR_ISP = {
    1: ("REQ1_ISPINPUT_2400.bin", "14637c3eb118ff284cfae31206d311557f1fc4b62e233ccf9698a2761ad1a1b5"),
    6: ("REQ6_ISPINPUT_PRE_2400.bin", "1cf44712660479d7f5d2ac131e068d146f213be44dd726176d8b1266d54a4606"),
}

CAMERA_ID_OFF = 0x80
SENSOR_AR_OFF = 0x944
CAMERA_SLOT_STRIDE = 0xEBE8
EEPROMDATA_BASE_OFF = 0xFA18
STATIC_CAP_POTP_SOURCE_BASE_OFF = 0xFA28
FORMAT_LSC_STORE_OFF = 0x3FD8
STATIC_CAP_OTP_OFF = 0x3E60
POTP_SLOT0_OFF = 0x168
ISPINPUT_POTP_OFF = 0x2070
REQUEST_LOCAL_BASE = 0x1EF8
REQUEST_LOCAL_POTP = 0x3F68
REQUEST_OBJECT_SIZE = 0x17E60
POTP_OBJECT_SIZE = 0xAC90

# Exact ARM64 bytes in the SHA-pinned QcDeviceMFT8380.dll.
SIGS = {
    # DataManager::Construct: cameraSlot = HWEnvironment + cameraId * 0xebe8;
    # retain cameraSlot+0xfa18 for ImageSensorModuleData/EEPROMData construction.
    0x180713734: "087d9dd25f2300b93503a89b08439fd25b5700b919244e91a97700f036c10791b702088ba84a4091591700f9b87a4091570b00f9",
    # EEPROMData construction: ldp values saved at DataManager locals +0x10,
    # then stp x9,x8 -> EEPROMData+0x10/+0x18. x8 is cameraSlot+0xfa18.
    0x1807139E8: "482741a97fae01f95fcb00b95fdf00b9692201a9",
    # EEPROMData::FormatLSCData: x20 = EEPROMData+0x18 + 0x3fd8.
    0x180723E64: "b32641a908fb87d23401088bb40000b4",
    # ImageSensorData::GetSensorStaticCapability:
    # source = HWEnvironment + cameraId*0xebe8 + 0xfa28 + 0x3e60;
    # destination = SensorStaticCapability +0x3e60; memcpy 0xac90.
    0x18071B304: "087d9dd2c902a89b08459fd22901088b08cc87d22101088b6002088b810000b4600000b4029295d255082194",
    # IFENode::FetchSensorInfo: if IFENode+0x3638 is null, bind it to
    # IFENode+0xa028 (SensorStaticCapability) +0x3e60.
    0x18075E920: "681e5bf9e80200b5080594d2696a68f8a90000b408cc87d22801088b681e1bf9",
    # IFE request builder: object base x26+0x1ef8, memset size 0x17e60.
    0x180745AAC: "11df83d24003118b02cc8fd22200a0f201008052080540f909090012",
    # Same builder: load IFENode+0x3638 and store at x26+0x3f68.
    0x180745CC0: "550340f9a84a4191087140f9483700f9a81e5bf948b71ff9",
    # IFELSC411: load ISPInputData+0x2070, add +0x168 formatted slot0.
    0x180A02B18: "883a50f901a10591280040b9",
    # Existing request-time tuning manager ownership anchor.
    0x180A02448: "97f64ff9f30300aa",
}


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def read_u32(b: bytes, off: int) -> int:
    need(len(b) >= off + 4, f"short ISPInputData for offset {off:#x}")
    return struct.unpack_from("<I", b, off)[0]


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--device-mft",
        type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
    )
    ap.add_argument("--front-capture", type=Path, default=here / "windows-adaptive-live-20260902")
    ap.add_argument("--rear-capture", type=Path, default=here / "oracle-vss-20260902-local")
    ap.add_argument("--out", type=Path, default=here / "lsc-front-calibration-object-ownership-oracle.json")
    args = ap.parse_args()

    prereqs = {
        here / "prove-lsc-calibration-application-boundary.py": CAL_BOUNDARY_PROOF_SHA,
        here / "lsc-calibration-application-oracle.json": CAL_BOUNDARY_ORACLE_SHA,
        here / "prove-lsc-front-rear-calibration-authority.py": AUTH_PROOF_SHA,
        here / "lsc-front-rear-calibration-authority-oracle.json": AUTH_ORACLE_SHA,
        here / "prove-lsc-front-request4-pretintless-bridge.py": REQ4_BRIDGE_PROOF_SHA,
        here / "lsc-front-request4-pretintless-bridge-oracle.json": REQ4_BRIDGE_ORACLE_SHA,
    }
    for p, expected in prereqs.items():
        need(sha_file(p) == expected, f"prerequisite drift: {p.name}")

    need(sha_file(args.device_mft) == DEVICE_MFT_SHA, "DeviceMFT SHA drift")
    data = args.device_mft.read_bytes()
    pe = pefile.PE(str(args.device_mft), fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase

    def read_va(va: int, n: int) -> bytes:
        off = pe.get_offset_from_rva(va - base)
        return data[off : off + n]

    observed = {}
    for va, hx in SIGS.items():
        want = bytes.fromhex(hx)
        got = read_va(va, len(want))
        need(got == want, f"instruction signature drift at {va:#x}: {got.hex()} != {hx}")
        observed[f"{va:#x}"] = got.hex()

    for marker in (
        b"DataManager::Construct\x00",
        b"CamX::EEPROMData::FormatLSCData\x00",
        b"CamX::ImageSensorData::GetSensorStaticCapability\x00",
        b"CamX::IFENode::FetchSensorInfo\x00",
        b"CamX::IFENode::ExecuteProcessRequest\x00",
        b"CamX::IFELSC411::CheckAndUpdateChromatixData\x00",
        b"Sensor static capabilities not available",
    ):
        need(marker in data, f"missing binary semantic marker {marker!r}")

    # Layout algebra: both producer and static-capability copier target the same
    # camera-local pOTPData slot0.
    formatted_lsc_abs = EEPROMDATA_BASE_OFF + FORMAT_LSC_STORE_OFF
    potp_base_abs = STATIC_CAP_POTP_SOURCE_BASE_OFF + STATIC_CAP_OTP_OFF
    need(formatted_lsc_abs == 0x139F0, f"formatted LSC absolute offset drift: {formatted_lsc_abs:#x}")
    need(potp_base_abs == 0x13888, f"pOTPData absolute offset drift: {potp_base_abs:#x}")
    need(formatted_lsc_abs - potp_base_abs == POTP_SLOT0_OFF, "FormatLSCData no longer lands at pOTPData+0x168")

    # Request-local algebra: the machine-code store at x26+0x3f68 is exactly
    # ISPInputData+0x2070 relative to the zeroed object at x26+0x1ef8.
    need(REQUEST_LOCAL_POTP - REQUEST_LOCAL_BASE == ISPINPUT_POTP_OFF, "request pOTPData field offset drift")

    # The prerequisite calibration boundary already pins IFELSC411's slot0
    # semantics. Re-check its machine-code bytes above and its recorded slot list.
    cal_oracle = json.loads((here / "lsc-calibration-application-oracle.json").read_text())
    slots = cal_oracle.get("formatted_eeprom_contract", {}).get("candidate_slot_offsets")
    if slots is None:
        # Fail closed across older equivalent schema spelling only.
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ("candidate_slot_offsets", "slot_offsets"):
                        return v
                    q = walk(v)
                    if q is not None:
                        return q
            elif isinstance(x, list):
                for v in x:
                    q = walk(v)
                    if q is not None:
                        return q
            return None
        slots = walk(cal_oracle)
    need(slots is not None and "0x168" in [str(x).lower() for x in slots], "calibration oracle slot0 +0x168 drift")

    # Verified-front capture identity and preserved rear VSS identity.
    front = {}
    for req, (name, expected_sha) in FRONT_ISP.items():
        p = args.front_capture / name
        need(sha_file(p) == expected_sha, f"front request{req} ISPInputData SHA drift")
        b = p.read_bytes()
        camera = read_u32(b, CAMERA_ID_OFF)
        sensor_ar = read_u32(b, SENSOR_AR_OFF)
        need(camera == 2, f"front request{req} camera field drift: {camera}")
        need(sensor_ar == 1, f"front request{req} sensorAR drift: {sensor_ar}")
        front[f"request{req}"] = {
            "file": name,
            "sha256": expected_sha,
            "camera": camera,
            "sensor_ar": sensor_ar,
            "previous_tintless_cache_key": sensor_ar + camera * 2,
        }

    rear = {}
    for req, (name, expected_sha) in REAR_ISP.items():
        p = args.rear_capture / name
        need(sha_file(p) == expected_sha, f"rear request{req} ISPInputData SHA drift")
        b = p.read_bytes()
        camera = read_u32(b, CAMERA_ID_OFF)
        sensor_ar = read_u32(b, SENSOR_AR_OFF)
        need(camera == 0, f"rear request{req} camera field drift: {camera}")
        need(sensor_ar == 1, f"rear request{req} sensorAR drift: {sensor_ar}")
        rear[f"request{req}"] = {
            "file": name,
            "sha256": expected_sha,
            "camera": camera,
            "sensor_ar": sensor_ar,
            "previous_tintless_cache_key": sensor_ar + camera * 2,
        }

    need({v["previous_tintless_cache_key"] for v in front.values()} == {5}, "front previous-Tintless key drift")
    need({v["previous_tintless_cache_key"] for v in rear.values()} == {1}, "rear previous-Tintless key drift")

    camera0_potp = 0 * CAMERA_SLOT_STRIDE + potp_base_abs
    camera2_potp = 2 * CAMERA_SLOT_STRIDE + potp_base_abs
    need(camera2_potp - camera0_potp == 2 * CAMERA_SLOT_STRIDE, "camera slot separation arithmetic drift")
    need(camera0_potp != camera2_potp, "camera0/camera2 pOTPData unexpectedly alias")

    oracle = {
        "schema": "sp11-e003h-lsc-front-calibration-object-ownership-v1",
        "status": "PASS",
        "classification": (
            "CLOSED NORMAL-PATH CAMERA-LOCAL CALIBRATION OBJECT OWNERSHIP: the SHA-pinned Surface DeviceMFT "
            "formats LSC slot0 into a cameraId-strided pOTPData object, copies that camera-local object into "
            "SensorStaticCapability, binds IFENode to its +0x3e60 OTP payload, stores the same pointer at "
            "ISPInputData+0x2070, and IFELSC411 consumes +0x168. Verified-front request4/5/6 ISPInputData "
            "uses camera=2 while preserved rear VSS uses camera=0, so ordinary rear-camera0 formatted-OTP "
            "object/pointer aliasing into the front-camera2 request is excluded on the normal path. This does "
            "not identify why camera2's calibration bytes are byte-equivalent to the rear/default authority."
        ),
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA,
            "prerequisites": {p.name: h for p, h in prereqs.items()},
            "front_ispinput": front,
            "rear_vss_ispinput": rear,
        },
        "machine_code": {
            "signatures": observed,
            "functions": {
                "DataManager::Construct": "0x180712f50",
                "CamX::EEPROMData::FormatLSCData": "0x180723e40",
                "CamX::ImageSensorData::GetSensorStaticCapability": "0x18071b270",
                "CamX::IFENode::FetchSensorInfo": "0x18075dcf8",
                "CamX::IFENode::ExecuteProcessRequest": "0x1807453d0",
                "CamX::IFELSC411::CheckAndUpdateChromatixData": "0x180a02420",
            },
        },
        "layout": {
            "camera_slot_stride": hex(CAMERA_SLOT_STRIDE),
            "eepromdata_field3_camera_slot_offset": hex(EEPROMDATA_BASE_OFF),
            "format_lsc_destination_from_field3": hex(FORMAT_LSC_STORE_OFF),
            "format_lsc_camera_slot_absolute": hex(formatted_lsc_abs),
            "static_caps_potp_source_camera_slot_offset": hex(STATIC_CAP_POTP_SOURCE_BASE_OFF),
            "static_caps_otp_offset": hex(STATIC_CAP_OTP_OFF),
            "potp_camera_slot_absolute": hex(potp_base_abs),
            "potp_lsc_slot0_offset": hex(POTP_SLOT0_OFF),
            "potp_object_copy_bytes": hex(POTP_OBJECT_SIZE),
            "request_local_object_base": hex(REQUEST_LOCAL_BASE),
            "request_local_potp_store": hex(REQUEST_LOCAL_POTP),
            "request_object_zeroed_bytes": hex(REQUEST_OBJECT_SIZE),
            "ispinput_potp_offset": hex(ISPINPUT_POTP_OFF),
            "camera0_potp_relative_to_hwenv": hex(camera0_potp),
            "camera2_potp_relative_to_hwenv": hex(camera2_potp),
            "camera2_minus_camera0": hex(camera2_potp - camera0_potp),
        },
        "excluded": [
            "normal-path camera0 formatted pOTPData object pointer being reused as camera2 pOTPData",
            "previous-Tintless global cache alias between preserved rear key1 and verified-front key5",
        ],
        "not_proven": [
            "the upstream raw OTP/InitParams bytes used to populate camera2",
            "why camera2's formatted LSC payload is byte-equivalent to the preserved rear/default calibration authority",
            "the live verified-front private DataManager tuning source-buffer identity",
            "verified-front sequential Tintless config/stats/state/output",
        ],
        "next_gate": (
            "Trace the camera2 EEPROMData raw input selection/population upstream of FormatLSCData: distinguish physical EEPROM read "
            "from InitParams-provided OTP/default/fallback content and pin the source bytes/owner. In parallel retain the genuine-front "
            "sequential Tintless gate. Linux request6 remains forbidden."
        ),
    }
    args.out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS front calibration object ownership")
    print(f"  camera0 pOTPData rel HWEnv {camera0_potp:#x}")
    print(f"  camera2 pOTPData rel HWEnv {camera2_potp:#x}")
    print(f"  separation {camera2_potp-camera0_potp:#x}")
    print("  verified-front camera/key", 2, 5)
    print("  rear VSS camera/key", 0, 1)
    print("  oracle", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
