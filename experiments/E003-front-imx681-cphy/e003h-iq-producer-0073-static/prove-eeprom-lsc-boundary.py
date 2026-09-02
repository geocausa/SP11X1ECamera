#!/usr/bin/env python3
"""Fail-closed static proof of the Surface IMX681 EEPROM -> LSC411 boundary.

This proof intentionally stops before reading the physical per-device EEPROM.
It proves the static descriptor, the exact DeviceMFT formatter layout, and the
exact IFELSC411 calibration-table consumption ABI needed for an offline oracle.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

from decode_imx681_chromatix import parse_header, parse_symbol_table, data_bytes

SENSOR_SHA = "f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c"
DEVICEMFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
EEPROM_ROOT_SHA = "9928dd5b36aad01d5d191a76d2832770c7b1697832aac129f551238043499ae1"
LIGHTINFO_SHA = "bbe16d1678d41c05bb885d4b1680b6be9b86e32e20a67d15576b5a6e764d4599"

# Generated Parameter Parser ordering pins these serialized offsets to the
# runtime EEPROMDriverData fields used by FormatLSCData.
SER = {
    "format_pair": 0x116,       # runtime +0x160/+0x164, two u32
    "light_count": 0x11E,       # runtime +0x168
    "light_symbol": 0x122,      # pointer entry feeding runtime +0x170
    "mesh_size": 0x126,         # runtime +0x178, u16
    "stride0": 0x128,           # runtime +0x17a, u16
    "stride1": 0x12A,           # runtime +0x17c, u16
    "stride2": 0x12C,           # runtime +0x17e, u16
    "stride3": 0x12E,           # runtime +0x180, u16
}

# Exact Surface ARM64 instructions anchoring the runtime contract. These are
# deliberately sparse semantic anchors rather than a copied code body.
CODE_PROOFS = {
    # IFELSC411::CheckDependenceChange: pOTPData, slot spacing, channel pointers.
    0xA02B18: bytes.fromhex("883a50f9"),  # ldr x8,[x20,#0x2070] (ISPInputData pOTPData)
    0xA02B1C: bytes.fromhex("01a10591"),  # add x1,x8,#0x168 (first OTP LSC slot)
    0xA02B30: bytes.fromhex("02be8152"),  # mov w2,#0xdf0 (one runtime LSC table)
    0xA02B40: bytes.fromhex("09a12991"),  # copied table +0xa68
    0xA02B54: bytes.fromhex("09310091"),  # copied table +0x0c
    0xA02B68: bytes.fromhex("09d11b91"),  # copied table +0x6f4
    0xA02B7C: bytes.fromhex("09010e91"),  # copied table +0x380
    0xA02B94: bytes.fromhex("01613d91"),  # second OTP slot +0xf58
    0xA02C40: bytes.fromhex("08a983d2"),  # third OTP slot +0x1d48
    0xA02CF0: bytes.fromhex("086785d2"),  # fourth OTP slot +0x2b38
    0xA02DA0: bytes.fromhex("082587d2"),  # fifth OTP slot +0x3928
    0xA02E50: bytes.fromhex("156900b9"),  # common +0x68 = available table count
    # EEPROMData::FormatLSCData: runtime descriptor, 221 mesh, output geometry.
    0x72406C: bytes.fromhex("1f050071"),  # format/type == 1
    0x724074: bytes.fromhex("68ba40f9"),  # runtime +0x170 lightInfo pointer
    0x72407C: bytes.fromhex("686a41b9"),  # runtime +0x168 light count
    0x724084: bytes.fromhex("69f24279"),  # runtime +0x178 mesh size
    0x7240EC: bytes.fromhex("a91b8052"),  # clamp mesh to 0xdd == 221
    0x724150: bytes.fromhex("0bbe81d2"),  # output slot stride 0xdf0
    0x724188: bytes.fromhex("6a2940b9"),  # lightInfo descriptor pair offset +0x28
    0x72418C: bytes.fromhex("826f80d2"),  # 0x37c = table channel+header span used in indexing
    0x724300: bytes.fromhex("6af64279"),  # runtime stride0 +0x17a
    0x724318: bytes.fromhex("6afa4279"),  # runtime stride1 +0x17c
    0x724324: bytes.fromhex("65fe4279"),  # runtime stride2 +0x17e
    0x724340: bytes.fromhex("6c024379"),  # runtime stride3 +0x180
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rva_to_off(pe: bytes, rva: int) -> int:
    if pe[:2] != b"MZ":
        raise ValueError("not PE/MZ")
    peoff = struct.unpack_from("<I", pe, 0x3C)[0]
    if pe[peoff:peoff+4] != b"PE\0\0":
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
    for rva, want in CODE_PROOFS.items():
        off = rva_to_off(pe, rva)
        got = pe[off:off+len(want)]
        if got != want:
            raise ValueError(f"code proof mismatch 0x{rva:x}: {got.hex()} != {want.hex()}")
        out[f"0x{rva:x}"] = got.hex()
    return out


def u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensor-module", type=Path, required=True)
    ap.add_argument("--devicemft", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    sensor = a.sensor_module.read_bytes()
    pe = a.devicemft.read_bytes()
    if sha(sensor) != SENSOR_SHA:
        raise SystemExit("exact Surface IMX681 sensor-module SHA mismatch")
    if sha(pe) != DEVICEMFT_SHA:
        raise SystemExit("exact Surface DeviceMFT SHA mismatch")

    h = parse_header(sensor)
    recs, _ = parse_symbol_table(sensor, h["sections"][0], h["sections"][1])
    obj = h["sections"][1]
    if recs[3]["type"] != "EEPROMDriverData":
        raise SystemExit("symbol 3 is not EEPROMDriverData")
    root = data_bytes(sensor, obj, recs[3])
    if len(root) != 1162 or sha(root) != EEPROM_ROOT_SHA:
        raise SystemExit("EEPROMDriverData identity mismatch")

    fmt = [u32(root, SER["format_pair"]), u32(root, SER["format_pair"] + 4)]
    count = u32(root, SER["light_count"])
    sid = u32(root, SER["light_symbol"])
    mesh = u16(root, SER["mesh_size"])
    strides = [u16(root, SER[f"stride{i}"]) for i in range(4)]
    if fmt[0] != 1 or count != 1 or sid != 3010 or mesh != 221 or strides != [2,2,2,2]:
        raise SystemExit(f"unexpected serialized LSC descriptor: fmt={fmt} count={count} sid={sid} mesh={mesh} strides={strides}")
    if recs[sid]["type"] != "lightInfo":
        raise SystemExit("LSC child symbol is not lightInfo")
    light = data_bytes(sensor, obj, recs[sid])
    if len(light) != 100 or sha(light) != LIGHTINFO_SHA:
        raise SystemExit("LSC lightInfo identity mismatch")

    light_type = u32(light, 0)
    descriptors = []
    for i in range(8):
        o = 4 + 12*i
        descriptors.append({"offset":u32(light,o), "mask":u32(light,o+4), "signed":u32(light,o+8)})
    expected_offsets = [0x103e,0x103d,0x11f8,0x11f7,0x13b2,0x13b1,0x156c,0x156b]
    if light_type != 3:
        raise SystemExit(f"unexpected light type {light_type}")
    if [d["offset"] for d in descriptors] != expected_offsets:
        raise SystemExit("unexpected EEPROM LSC byte offsets")
    if any(d["mask"] != 0xff or d["signed"] != 0 for d in descriptors):
        raise SystemExit("unexpected EEPROM LSC byte masks/sign flags")

    # FormatLSCData combines each adjacent descriptor pair as low byte from the
    # lower address and high byte from the higher address, then adds stride 2.
    low_starts = [descriptors[i]["offset"] for i in (1,3,5,7)]
    high_starts = [descriptors[i]["offset"] for i in (0,2,4,6)]
    if any(hh != lo + 1 for lo, hh in zip(low_starts, high_starts)):
        raise SystemExit("LSC descriptors are not adjacent 16-bit samples")
    channel_bytes = mesh * 2
    if any(low_starts[i+1] != low_starts[i] + channel_bytes for i in range(3)):
        raise SystemExit("LSC channel arrays are not contiguous")
    raw_start = low_starts[0]
    raw_bytes = channel_bytes * 4
    raw_end_exclusive = raw_start + raw_bytes
    if raw_end_exclusive != 0x1725:
        raise SystemExit("unexpected raw EEPROM LSC range")

    code = assert_code(pe)
    result = {
        "schema":"sp11-e003h-eeprom-lsc-boundary-v1",
        "status":"PASS",
        "surface_sensor_module_sha256":SENSOR_SHA,
        "surface_devicemft_sha256":DEVICEMFT_SHA,
        "serialized_eeprom_driver":{
            "symbol_id":3,
            "bytes":len(root),
            "sha256":sha(root),
            "lsc_runtime_format_pair":fmt,
            "lsc_light_count":count,
            "lsc_light_symbol_id":sid,
            "mesh_hw_rolloff_size":mesh,
            "per_channel_byte_stride":strides,
        },
        "lsc_light_info":{
            "symbol_id":sid,
            "bytes":len(light),
            "sha256":sha(light),
            "light_type":light_type,
            "byte_descriptors":[
                {"index":i, "offset":f"0x{d['offset']:x}", "mask":f"0x{d['mask']:x}", "signed":d["signed"]}
                for i,d in enumerate(descriptors)
            ],
            "decoded_raw_eeprom_geometry":{
                "samples_per_channel":mesh,
                "sample_encoding":"u16 little-endian assembled from two 0xff byte descriptors",
                "channel_count":4,
                "channel_start_offsets":[f"0x{x:x}" for x in low_starts],
                "bytes_per_channel":channel_bytes,
                "contiguous_range":f"0x{raw_start:x}..0x{raw_end_exclusive-1:x}",
                "total_bytes":raw_bytes,
            },
        },
        "runtime_otp_lsc_layout":{
            "max_slots":5,
            "slot_offsets_from_potpdata":["0x168","0xf58","0x1d48","0x2b38","0x3928"],
            "slot_bytes":"0xdf0",
            "availability_field":"slot +0x0 == 1",
            "light_type_field":"slot +0x4",
            "mesh_size_field":"slot +0x8",
            "channel_float_offsets":["0x0c","0x380","0x6f4","0xa68"],
            "channel_float_samples":221,
            "common_pointer_record_bytes":"0x20",
            "common_available_count_offset":"0x68",
            "common_calibration_enable_offsets":["0x6c","0x80"],
        },
        "capture_abi_code_byte_proofs":code,
        "producer_reduction":{
            "static_eeprom_descriptor_closed":True,
            "physical_device_eeprom_bytes_captured":False,
            "raw_lsc_calibration_bytes_needed":"0x6e8 bytes at EEPROM 0x103d..0x1724",
            "remaining_lsc_dynamic_inputs":[
                "same-device physical EEPROM calibration bytes (unless recovered from an existing Windows cache/capture)",
                "request-local Tintless/ALSC adaptive state",
                "request-local LSC geometry/scale",
            ],
            "remaining_gtm_dynamic_input":"request-local TMC state",
        },
        "policy":{
            "offline_only":True,
            "camera_runtime_performed":False,
            "linux_request6_authorized":False,
            "linux_request6_executed":False,
        },
    }
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"raw_lsc":result["lsc_light_info"]["decoded_raw_eeprom_geometry"],"producer_reduction":result["producer_reduction"]},indent=2))

if __name__ == "__main__":
    main()
