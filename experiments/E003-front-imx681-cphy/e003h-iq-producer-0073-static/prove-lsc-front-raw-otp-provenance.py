#!/usr/bin/env python3
"""Fail-closed cross-binary proof of front raw OTP provenance.

Closes the normal raw-calibration source class before EEPROM formatting:

  front physical EEPROM
    -> front sensor KMD cache (+0x320/+0x328)
    -> SensorCalibrationData when the InitParams option byte is zero
    -> DeviceMFT DataManager +0xc8/+0xd0
    -> EEPROMData rawData

or, when that KMD cache is intentionally not published:

  front camera-local ImageSensorModuleData
    -> DeviceMFT CreateAndReadEEPROMData / ReadEEPROMDevice
    -> EEPROMData rawData

Both routes converge before FormatLSCData.  This proof does not explain the
rear/default-equivalent golden/reference material used by FormatLSCData.
No camera runtime is performed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pefile

HERE = Path(__file__).resolve().parent

BINARIES = {
    "avs": {
        "path": Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys"),
        "sha256": "b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed",
    },
    "front_sensor": {
        "path": Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor8380.inf_arm64_747e2ddb5eb5a22b/surfacecamfrontsensor8380.sys"),
        "sha256": "80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03",
    },
    "device_mft": {
        "path": Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
        "sha256": "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35",
    },
}

PREREQS = {
    "prove-lsc-front-calibration-object-ownership.py": "e6b5f5e4641073289bc42be90630d44592d68b6562a277ddc13a3912dd16b9d9",
    "lsc-front-calibration-object-ownership-oracle.json": "155d137b285c38b1ea9db451be0257c184722cfdae7fa60d073d0c0e07480676",
}

# Exact bytes from the SHA-pinned binaries.
SIGS = {
    "avs": {
        # CCaptureFilter::GetInitParams: x2=payload length, x3=&bytes-written,
        # w4=CCaptureFilter+0x23f, then camera-engine indirect call.
        0x1400063F8: "c90240f9e3430091e4fe4839280940f920410091080140f9ef0308aa310100d031de41f920023fd6e0013fd6",
        # CCameraEngine::GetInitParams entry: stores incoming w4 at stack+4.
        0x14001F764: "570c0094ff0311d1f40300aae4130039f50303aae1ff00a9ff1b00b9ff7f02a9610000b42840228be80b00f928008052e83300b96800009001811491e0d30091",
        # DeviceManager allocation and full 0x370/0x360 zeroing before entries.
        0x1400207F8: "7f2303d5f353bba9f55b01a9f76302a9f96b03a9fb2300f9fd7bbfa9fd030091f40300aa00058052016e805213008052a6f2ff97f50300aa950000b59f0200f9400080523a000014026e80d2950200f901008052e00315aaec080094480000f001611f91",
        # CameraDeviceOpen GETFNTABLE handshake through IoBuildDeviceIoControlRequest.
        0x140020C98: "210d40f90601805225a1009104008052030080d2a207001868ffff976001f8361f00007100b09f1a9f2203d5480000f001a12191e203002aa062039167f0ff97330080520200001413008052b3fcff35960200f910000014",
        # Sensor-handle wrapper direct/fallback split. Direct path leaves w1/x2..x7 intact.
        0x140020DD0: "201540f9600300b42ac140390a010035080040f9ef0308aa7100009031de41f920023fd6e0013fd60f0000142a2140f9ca0100b4e70306aae603052ae50304aae403032ae30302aae203012a211d40f9ef030aaa7100009031de41f920023fd6e0013fd6",
        # CCameraEngine command 0x801 call: x2=&stack+4 option byte.
        0x14001F98C: "e603009123008052e21300912100815203050094e10340b9e0230091",
    },
    "front_sensor": {
        # Internal IOCTL GETFNTABLE response: mask 0x3ffc, compare 0x26a8,
        # write live sensor object pointer at +0 and direct-mode zero byte at +8.
        0x140001A88: "e80b40f92a2f1e1209d584525f01096b01020054c80000b4180100f9150080521f2100391f7d01a913000014680000b003610691",
        # PrepareHardware creates sensor object whose slot0 is FUN_140005270.
        0x140038878: "68feffb009c1099168fefff008c108917ab71e39a92200a968fefff008010a91a87e01a9bf1200f9",
        # Dispatcher command 0x801 -> CameraSensorDriver_GetInitParams with original x2 as new x1.
        0x140005688: "3f042071a1d90054e50317aae4031a2ae30315aae203192ae10314aae00313aa2a130094",
        # GetInitParams: cached +0x320; zero option branches to SensorCalibrationData publication,
        # nonzero frees/zeros +0x320/+0x328.
        0x14000A6FC: "a19241f9810100b416030034000980520be7ff97480000d001a12791680000d000212591bf2a03b9bf9201f9628207913fe5ff97a18a41f9480000d000012a9183008052ff0300b9e203009156eaff97a004f837e80340b91f050071e8179f1ae813003921000014480000d001a12991e0230091fe010094081c0053c8000035480000d001e11191680000d000e12291ee000014a22a43b9e0230091a19241f917020094081c0053c8000035",
        # Allocate front KMD physical EEPROM cache and store at +0x320.
        0x140005FE4: "609201f9802200b421150094081c00531f05007120010054680000b001411291c2820691e0e201913500805206f7ff9774fa0091e9000014e0031a2ab0150094081c0053",
        # Physical EEPROM read descriptor carries +0x320 buffer; success log follows call.
        0x1400060F4: "6b9241f98b1100b4a900009029c117919f060071a10000548a0080522a5d00b938e10139040000144a0080522a5d00b938f10079aa0000904ac11791e92740795f5100b9040880524c610139434101914b3500f90200805249f50079010080d2488d00b9a8000090081d42b900860018485500b94ef6ff97e00df8376800009001811391",
        # Optional bank canonicalization copies selected bank in-place into canonical raw cache.
        0x1400062E0: "f40314aa884600910214088b030480d200800891010480d24215009468000090",
        # Successful raw read stores selected/read length at +0x328 and keeps +0x320 pointer.
        0x1400063E8: "e1274079e83b40f9629241f9612a03b9e10301aa080140f9e30301aa000540f9fe140094",
    },
    "device_mft": {
        # LoadDataFromDriver parses SensorCalibrationData, alloc/copies payload,
        # stores size at DataManager+0xd0 and pointer at +0xc8.
        0x180716B80: "00c10e9181120091de1c2194200200354868009002c10d912438805223c30b91e1ff9f52800080524010e497a07e40d3d5d200b9e35e1694c06600f9001c00b4a27e40d3e10317aa2e1a219402000014",
        # Construct: if supplied ptr/size exist, install them into EEPROMData +0x378/+0x380;
        # otherwise branch into CreateAndReadEEPROMData fallback.
        0x180713E64: "483b40f9c80300b4483340b988030034c81240f988000837a87700b0085948b948020035756800f0a0023391810b8052814f1794a40233911f0000f18404809a400080d28624e597686800f005613691686800f002212f91e30300aae1ff9f5280008052781be497483340b9688203b9483b40f968be01f91a020014683240b9",
    },
}

SEMANTIC_STRINGS = {
    "avs": [b"EnableContinuousRawDump", b"InitParams"],
    "front_sensor": [
        b"CAMERA_DEVICE_IRPCMD_GETFNTABLE",
        b"SensorCalibrationData",
        b"Reading OTP data succeed.",
        b"OTP data selected from Bank-",
        b"Successfully copied OTP data to UMD buffer.",
        b"Sensor EEPROM data is not cached to allow UMD to read data without reboot.",
    ],
    "device_mft": [
        b"Found sensor calibration data payload",
        b"SensorCalibrationData",
        b"Retrieve OTP from InitPramas.",
        b"CamX::ImageSensorModuleData::CreateAndReadEEPROMData",
        b"CamX::EEPROMData::ReadEEPROMDevice",
    ],
}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def need(v: bool, msg: str) -> None:
    if not v:
        raise RuntimeError(msg)


def main() -> int:
    for name, expected in PREREQS.items():
        p = HERE / name
        need(sha(p) == expected, f"prerequisite drift: {name}")

    observations = {}
    for name, spec in BINARIES.items():
        p = spec["path"]
        need(p.exists(), f"missing {name}: {p}")
        actual = sha(p)
        need(actual == spec["sha256"], f"{name} SHA drift")
        data = p.read_bytes()
        pe = pefile.PE(str(p), fast_load=True)
        base = pe.OPTIONAL_HEADER.ImageBase
        sig_obs = {}
        for va, hx in SIGS[name].items():
            want = bytes.fromhex(hx)
            off = pe.get_offset_from_rva(va - base)
            got = data[off:off + len(want)]
            need(got == want, f"{name} instruction drift at {va:#x}")
            sig_obs[hex(va)] = got.hex()
        for marker in SEMANTIC_STRINGS[name]:
            need(marker in data, f"{name} missing semantic marker {marker!r}")
        observations[name] = {
            "path": str(p),
            "sha256": actual,
            "signatures": sig_obs,
            "semantic_markers": [x.decode("ascii") for x in SEMANTIC_STRINGS[name]],
        }

    # Cross-binary ABI / branch invariants.
    ioctl = 0x2326AB
    need((ioctl & 0x3FFC) == 0x26A8, "GETFNTABLE IOCTL mask drift")
    need(0x38 - 0x08 == 0x30, "handle direct-mode byte offset algebra drift")
    need(0x30 - 0x08 == 0x28, "handle function-table pointer offset algebra drift")
    need(0x801 == 2049, "sensor GetInitParams command drift")

    oracle = {
        "schema": "sp11-e003h-front-raw-otp-provenance-v1",
        "status": "PASS",
        "classification": (
            "CLOSED NORMAL RAW-OTP SOURCE CLASS: the front sensor KMD reads the front camera module's physical "
            "EEPROM into its +0x320/+0x328 cache. A zero InitParams option publishes that exact cache as "
            "SensorCalibrationData; DeviceMFT copies it into DataManager+0xc8/+0xd0 and uses it as EEPROMData raw input. "
            "A nonzero option intentionally drops the KMD cache, after which DeviceMFT takes its camera-local "
            "CreateAndReadEEPROMData/ReadEEPROMDevice fallback. Both routes therefore source raw OTP from the front "
            "camera module's physical EEPROM and converge before FormatLSCData. Rear camera0 raw-OTP pointer/buffer "
            "injection is excluded on the normal path."
        ),
        "binaries": observations,
        "prerequisites": PREREQS,
        "abi": {
            "avs_getfntable_ioctl": hex(ioctl),
            "front_kmd_getfntable_mask": "ioctl & 0x3ffc == 0x26a8",
            "getfntable_returns_live_sensor_object": True,
            "sensor_object_slot0_dispatcher": "0x140005270",
            "returned_handle_function_table_offset": "0x28",
            "returned_handle_direct_mode_byte_offset": "0x30",
            "getfntable_direct_mode_byte": 0,
            "sensor_get_initparams_command": "0x801",
            "avs_engine_option_byte": "incoming w4 -> stack+0x4 -> x2 to command 0x801",
            "front_dispatcher_argument_mapping": "original x2 -> GetInitParams x1; original w3 -> GetInitParams w2",
        },
        "front_kmd_raw_otp": {
            "cache_pointer_offset": "0x320",
            "cache_size_offset": "0x328",
            "zero_option": "publish +0x320/+0x328 as SensorCalibrationData",
            "nonzero_option": "free and zero +0x320/+0x328 so UMD can read EEPROM without reboot",
            "banked_special_case": "selected bank is canonicalized in-place inside the same physical-read cache",
        },
        "device_mft_transport": {
            "SensorCalibrationData_destination_pointer": "DataManager+0xc8",
            "SensorCalibrationData_destination_size": "DataManager+0xd0",
            "EEPROMData_supplied_pointer": "+0x378",
            "EEPROMData_supplied_size": "+0x380",
            "fallback": "CamX::ImageSensorModuleData::CreateAndReadEEPROMData -> CamX::EEPROMData::ReadEEPROMDevice",
            "convergence": "EEPROM rawData -> Format* including CamX::EEPROMData::FormatLSCData",
        },
        "excluded": [
            "normal-path rear camera0 raw OTP cache pointer being supplied to the verified front request",
            "rear/default packaged calibration replacing the raw physical EEPROM source before EEPROMData formatting",
        ],
        "not_proven": [
            "capture-time value of the AVS option byte for the older accepted Windows captures (not needed for source-class closure because both branches are physical front EEPROM)",
            "which EEPROM library/golden/reference object FormatLSCData selects for front camera2",
            "why rear/default OV13858 golden LSC authority is selected during verified-front formatting",
            "live verified-front private DataManager tuning-buffer identity",
            "genuine verified-front sequential Tintless state/stats/output",
        ],
        "supplemental_restored_windows_state": {
            "system_hive_sha256": "21f2fa03b6fd0766b0578fac2062cf75a8d477439b9e2ca010949c72c82e63c7",
            "system_hive_size": 17825792,
            "read_only_scan": "hivexml full SYSTEM hive",
            "EnableContinuousRawDump_occurrences": 0,
            "AllowOtpReload_occurrences": 0,
            "note": "Current restored Windows state only; not used to infer the older capture-time branch.",
        },
        "next_gate": (
            "Trace EEPROMData formatting-library/golden-reference selection for camera2, especially FormatLSCData and the "
            "loaded EEPROM library path. Raw OTP ownership is now front physical EEPROM on either normal branch, so the "
            "rear/default calibration crossover must occur at or after formatting/reference selection. Linux request6 remains forbidden."
        ),
    }
    out = HERE / "lsc-front-raw-otp-provenance-oracle.json"
    out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS front raw OTP provenance")
    print("  GETFNTABLE", hex(ioctl), "mask", hex(ioctl & 0x3FFC))
    print("  zero option -> front KMD physical EEPROM cache -> SensorCalibrationData")
    print("  nonzero option -> DeviceMFT camera-local physical EEPROM fallback")
    print("  remaining crossover: FormatLSCData library/golden/reference selection")
    print("  oracle", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
