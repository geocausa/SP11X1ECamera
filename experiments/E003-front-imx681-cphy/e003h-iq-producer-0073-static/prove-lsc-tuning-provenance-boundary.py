#!/usr/bin/env python3
"""Fail-closed static proof for the E003h LSC tuning provenance boundary.

This proof does not claim to close why a front IMX681 stream resolves the rear
OV13858 LSC41 leaf.  It pins the exact binary identities and the discriminating
byte provenance needed for that question, and verifies the front configuration
and driver/DeviceMFT markers used by the static ownership trace.

No camera runtime is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    "device_mft": "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35",
    "front_kmd": "80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03",
    "front_tuning": "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d",
    "rear_tuning": "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635",
    "platform_default": "aa685fb55e528e717eaf115112dd08bffb5d15c7cd00c4570282163667008150",
    "rear_default": "ca620fbcfd9bde3c25157289ac7172244fb39744b36d293ea53ab94422eea634",
    "front_scfg": "e6e3d828a1e4f5bc94c545848a091c20be399a4b22c938ed4a3df072dd033d99",
}

A_SHA = "d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d"
B_SHA = "f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8"
A_REAR_OFFSET = 1_008_426
B_REAR_OFFSET = 1_012_018
REGION_SIZE = 0xDF0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def all_offsets(haystack: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = haystack.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


def require_hash(name: str, path: Path) -> bytes:
    data = path.read_bytes()
    got = sha(data)
    want = EXPECTED[name]
    if got != want:
        raise RuntimeError(f"{name} SHA drift: {got} != {want}: {path}")
    return data


def require_strings(name: str, data: bytes, strings: list[bytes]) -> None:
    for s in strings:
        if s not in data:
            raise RuntimeError(f"{name}: missing exact marker {s!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    base = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
    here = Path(__file__).resolve().parent
    ap.add_argument("--device-mft", type=Path, default=base / "surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
    ap.add_argument("--front-kmd", type=Path, default=base / "surfacecamfrontsensor8380.inf_arm64_747e2ddb5eb5a22b/surfacecamfrontsensor8380.sys")
    ap.add_argument("--front-tuning", type=Path, default=base / "surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin")
    ap.add_argument("--rear-tuning", type=Path, default=base / "surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
    ap.add_argument("--platform-default", type=Path, default=base / "qccamplatform8380.inf_arm64_16d44e9aca3becfb/com.qti.tuned.default.bin")
    ap.add_argument("--rear-default", type=Path, default=base / "surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.qti.tuned.default.bin")
    ap.add_argument("--front-scfg", type=Path, default=base / "surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/SCFG_FRONT_MSHW0490.bin")
    ap.add_argument("--out", type=Path, default=here / "lsc-tuning-provenance-boundary-oracle.json")
    args = ap.parse_args()

    device_mft = require_hash("device_mft", args.device_mft)
    front_kmd = require_hash("front_kmd", args.front_kmd)
    front = require_hash("front_tuning", args.front_tuning)
    rear = require_hash("rear_tuning", args.rear_tuning)
    platform_default = require_hash("platform_default", args.platform_default)
    rear_default = require_hash("rear_default", args.rear_default)
    scfg = require_hash("front_scfg", args.front_scfg)

    a = rear[A_REAR_OFFSET:A_REAR_OFFSET + REGION_SIZE]
    b = rear[B_REAR_OFFSET:B_REAR_OFFSET + REGION_SIZE]
    if len(a) != REGION_SIZE or sha(a) != A_SHA:
        raise RuntimeError("rear A leaf identity/offset drift")
    if len(b) != REGION_SIZE or sha(b) != B_SHA:
        raise RuntimeError("rear B leaf identity/offset drift")

    corpus = {
        "front_imx681": front,
        "rear_ov13858": rear,
        "platform_default": platform_default,
        "rear_default": rear_default,
    }
    occurrences = {
        name: {"A": all_offsets(data, a), "B": all_offsets(data, b)}
        for name, data in corpus.items()
    }
    if occurrences["front_imx681"]["A"]:
        raise RuntimeError("discriminating runtime A unexpectedly exists in front IMX681 tuning")
    if occurrences["rear_ov13858"]["A"] != [A_REAR_OFFSET]:
        raise RuntimeError(f"rear A occurrence drift: {occurrences['rear_ov13858']['A']}")
    if any(occurrences[name]["A"] for name in ("platform_default", "rear_default")):
        raise RuntimeError("discriminating runtime A unexpectedly exists in generic default tuning")

    require_strings("front SCFG", scfg, [
        b"com.surface.sensormodule.ffc_imx681.bin\x00",
        b"com.surface.tuned.ffc_imx681.bin\x00",
    ])
    if b"rfc_ov13858" in scfg:
        raise RuntimeError("front SCFG unexpectedly names rear OV13858")

    require_strings("front sensor KMD", front_kmd, [
        b"SensorTuningData\x00",
        b"com.qti.tuned.default.bin\x00",
        b"Loading sensor tuning binary %s failed. Loading default tuning bianry file instead.\x00",
        b"CameraSensorDriver_GetInitParams() Entering CameraSensorDriver_GetInitParams ...\x00",
    ])
    require_strings("DeviceMFT", device_mft, [
        b"SensorTuningData\x00",
        b"InitParams\x00",
        b"SensorInfo\x00",
        b"DataManager::LoadDataFromDriver\x00",
        b"CamX::TuningDataManager::CreateTunedModeTree\x00",
        b"CaptureDevice::ConstructReal\x00",
        b"%s:%d ### INFO ### Camera Sensor ID:%d\n\x00",
    ])

    oracle = {
        "schema": "sp11-e003h-lsc-tuning-provenance-boundary-v1",
        "accepted": True,
        "classification": "STATIC PROVENANCE BOUNDARY: live LSC A is rear-OV13858-only among the exact front/rear/default tuning authorities, while the front SCFG explicitly selects IMX681. DeviceMFT and front KMD statically pin the SensorTuningData handoff; the remaining question is which selected-sensor provider/tuning manager instance reaches IFELSC411 in the live front stream.",
        "source_authority": {
            name: {"path": str(getattr(args, name)), "sha256": EXPECTED[name]}
            for name in ("device_mft", "front_kmd", "front_tuning", "rear_tuning", "platform_default", "rear_default", "front_scfg")
        },
        "runtime_leaf_identity": {
            "A_sha256": A_SHA,
            "A_size": REGION_SIZE,
            "A_rear_offset": A_REAR_OFFSET,
            "B_sha256": B_SHA,
            "B_size": REGION_SIZE,
            "B_rear_offset": B_REAR_OFFSET,
            "full_blob_occurrences": occurrences,
        },
        "front_configuration": {
            "sensor_module": "com.surface.sensormodule.ffc_imx681.bin",
            "tuning": "com.surface.tuned.ffc_imx681.bin",
            "rear_name_present": False,
        },
        "static_flow": {
            "front_kmd_init_rva": "0x8a50",
            "front_kmd_get_init_params_rva": "0xa350",
            "front_kmd_tuning_storage": "device+0x80 pointer, device+0x88 size",
            "front_kmd_tuning_filename": "device+0x21a within the copied sensor init configuration",
            "front_kmd_fallback": "com.qti.tuned.default.bin only if the selected sensor tuning binary load fails",
            "devicemft_load_data_from_driver_rva": "0x7165a8",
            "devicemft_sensor_tuning_storage": "DataManager+0x38 pointer, DataManager+0x30 size",
            "devicemft_create_tuning_manager": "DataManager::Construct passes +0x38/+0x30 into a per-CaptureDevice TuningDataManager and creates its tuned-mode tree",
            "capturedevice_construct_real_rva": "0x291c00",
            "capturedevice_datamanager_storage": "CaptureDevice+0x60 (param_1[0xc])",
            "capturedevice_provider": "CaptureDevice+0x10 is passed to the DataManager and is also used by CaptureDevice::Construct for selected Sensor ID/platform queries",
        },
        "closed_exclusions": [
            "front SCFG directly points at rear OV13858 tuning",
            "runtime A is hidden elsewhere in the exact front IMX681 tuning file",
            "runtime A comes from either tested com.qti.tuned.default.bin fallback",
            "one global TuningDataManager is unconditionally shared by all CaptureDevice instances: ConstructReal allocates a DataManager per CaptureDevice",
        ],
        "next_gate": "Trace the CaptureDevice+0x10 selected-sensor provider through its InitParams response and the IFELSC411 tuning-manager handoff. Prefer static ownership/call tracing. If static proof cannot distinguish the live provider, capture only selected Sensor ID plus the exact TuningDataManager/source-buffer identity in one Windows front-stream session. Do not run Linux request6.",
        "safety": {"linux_camera_runtime": False, "linux_request6_executed": False, "linux_request6_authorized": False},
    }
    args.out.write_text(json.dumps(oracle, indent=2) + "\n")
    print("PASS LSC tuning provenance boundary")
    print("  A rear-only:", A_SHA, "rear offset", A_REAR_OFFSET)
    print("  front A hits:", occurrences["front_imx681"]["A"])
    print("  platform/rear-default A hits:", occurrences["platform_default"]["A"], occurrences["rear_default"]["A"])
    print("  front SCFG: IMX681 sensor+tuning exact")
    print("  oracle", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
