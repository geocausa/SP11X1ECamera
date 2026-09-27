#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
RT_DEC = REPO / "experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
PRIVATE_REG = REPO.parent / "private/e006a/E006A-PRIVATE-RECORDS-v2.json"
PRIVATE_DMI = REPO.parent / "private/e006b"
DMI_META = REPO / "experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def sx(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

dll = DLL.read_bytes()
assert sha(dll) == DLL_SHA
block_rva = 0x763788
block_off = 0x400 + (block_rva - 0x1000)
q = [round(v * 16384.0) for v in struct.unpack("<20f", dll[block_off:block_off + 80])]

# Reconstruct the two Titan coefficient orders from the static hardcode helper.
h_semantic = [q[0], 0, q[1], q[6], q[7], q[2], 0, q[3], q[4], q[5]]
h_titan = [h_semantic[i] for i in [0, 1, 2, 7, 3, 4, 5, 6, 8, 9]]
v_titan = [q[16], q[17], q[16], q[18], q[19], q[2], 0, q[3], q[4], q[5]]

RT = load_module(RT_DEC, "e008s_rt")
records = json.load(open(PRIVATE_REG, encoding="utf-8-sig"))["records"]
bf = []
for rec in records:
    if rec.get("idx") != 1 or not rec.get("complete"):
        continue
    vals = {r: v for r, v, *_ in RT.decode(bytes.fromhex(rec["hex"]))["writes"]}
    if 0xBCD0 not in vals:
        continue
    h_obs = []
    for reg in [0xBC7C, 0xBC80, 0xBC84, 0xBC88, 0xBC8C]:
        h_obs += [sx(vals[reg], 16), sx(vals[reg] >> 16, 16)]
    v_obs = [
        sx(vals[0xBC90], 16), sx(vals[0xBC90] >> 16, 16), sx(vals[0xBC94], 16),
        sx(vals[0xBC98], 16), sx(vals[0xBC98] >> 16, 16), sx(vals[0xBC9C], 16),
        sx(vals[0xBC9C] >> 16, 16), sx(vals[0xBCA0], 16), sx(vals[0xBCA4], 16),
        sx(vals[0xBCA4] >> 16, 16)
    ]
    shifts = (sx(vals[0xBCA8], 4), sx(vals[0xBCA8] >> 4, 4))
    def tail(scalar, regs):
        lanes = []
        for reg, count in zip(regs, (5, 5, 5, 2)):
            lanes += [(vals[reg] >> (6 * i)) & 0x1F for i in range(count)]
        return vals[scalar] & 0x1FFFF, lanes
    bf.append({
        "n": rec.get("n"),
        "h": h_obs,
        "v": v_obs,
        "shifts": shifts,
        "tail0": tail(0xBCAC, [0xBCB0, 0xBCB4, 0xBCB8, 0xBCBC]),
        "tail1": tail(0xBCC0, [0xBCC4, 0xBCC8, 0xBCCC, 0xBCD0]),
    })

assert len(bf) == 35
packet0 = [x for x in bf if x["n"] == 0]
assert len(packet0) == 1
p0 = packet0[0]
expected_tail = (65536, [0] + [16] * 16)
assert p0["h"] == h_titan
assert p0["v"] == v_titan
assert p0["shifts"] == (-3, 0)
assert p0["tail0"] == expected_tail and p0["tail1"] == expected_tail

normal = [x for x in bf if x["n"] != 0]
assert len(normal) == 34
assert all(x["shifts"] == (3, 3) for x in normal)

meta = json.load(open(DMI_META))
source_files = {
    "startup0": "E006B-START0-SOURCE.bin",
    "startup1": "E006B-START1-SOURCE.bin",
    "startup2": "E006B-START2-SOURCE.bin",
    "startup3": "E006B-START3-SOURCE.bin",
    "steady_ac8": "E006B-STEADY-AC8-SOURCE.bin",
}
roi_hashes = []
gamma_present = {}
for cap in meta["captured"]["captures"]:
    label = cap["label"]
    if label not in source_files:
        continue
    blob = (PRIVATE_DMI / source_files[label]).read_bytes()
    base = int(cap["captured_source_window_base"], 16)
    roi = next((x for x in cap["payloads"]
                if x["dmi_register_offset"] == "0xbc08" and x["selector"] == 1), None)
    assert roi is not None and roi["payload_bytes"] == 300
    rel = int(roi["source_offset"], 16) - base
    payload = blob[rel:rel + roi["payload_bytes"]]
    assert len(payload) == 300
    roi_hashes.append(sha(payload))
    gamma_present[label] = any(
        x["dmi_register_offset"] == "0xbc08" and x["selector"] == 2 and x["payload_bytes"] == 128
        for x in cap["payloads"]
    )

assert gamma_present == {
    "startup0": False,
    "startup1": True,
    "startup2": True,
    "startup3": True,
    "steady_ac8": True,
}

safe = {
    "schema": "E008S-private-validation-safe-v1",
    "status": "PASS",
    "bf_register_records_checked": len(bf),
    "packet0_hardcode_filter_exact_matches": 1,
    "packet0_hardcode_shift_exact_matches": 1,
    "packet0_hardcode_coring_exact_matches": 1,
    "normal_shift_records_checked": len(normal),
    "normal_shift_exact_matches": len(normal),
    "roi_selector1_payloads_checked": len(roi_hashes),
    "roi_selector1_all_300_bytes": True,
    "roi_selector1_unique_payload_count": len(set(roi_hashes)),
    "gamma_phase_matches_source_policy": True,
    "captured_windows_register_values_emitted": False,
    "captured_windows_dmi_bytes_emitted": False,
    "private_payload_hashes_emitted": False,
    "runtime_actions_performed": False
}
(HERE / "PRIVATE-VALIDATION-SAFE.json").write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
print("E008S_PRIVATE_AUDIT_PASS packet0=1/1 normal_shifts=34/34 roi=5 gamma_phase=true")
