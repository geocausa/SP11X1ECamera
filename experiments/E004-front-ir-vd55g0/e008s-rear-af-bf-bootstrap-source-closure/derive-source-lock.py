#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNING = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
TUNING_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
DEC = REPO / "experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=1e-6)

def f32(value: float) -> float:
    """Round a Python float to the IEEE-754 binary32 operation used by DeviceMFT."""
    return struct.unpack("<f", struct.pack("<f", value))[0]

dll = DLL.read_bytes()
assert sha(dll) == DLL_SHA
tuning = TUNING.read_bytes()
assert sha(tuning) == TUNING_SHA

D = load_module(DEC, "e008s_chromatix")
header = D.parse_header(tuning)
assert header["module_name"] == "com.surface.tuned.rfc_ov13858"
records, _ = D.parse_symbol_table(tuning, header["sections"][0], header["sections"][1])
obj = header["sections"][1]
assert records[0xB2]["type"] == "BAF"
assert records[0xB6]["type"] == "HAF"

configure = D.data_bytes(tuning, obj, records[0x1BBF])
assert len(configure) == 4 * 48
configure_records = [struct.unpack("<12I", configure[i*48:(i+1)*48]) for i in range(4)]
assert configure_records[0][0] == 0
shift_pairs = [(r[7], r[11]) for r in configure_records]
assert shift_pairs == [(3, 3)] * 4

gamma = D.data_bytes(tuning, obj, records[0x1BC1])
assert struct.unpack_from("<I", gamma, 0)[0] == 1

scale = D.data_bytes(tuning, obj, records[0x1BC2])
assert struct.unpack_from("<3I", scale, 0) == (0, 1, 1)

fir = D.data_bytes(tuning, obj, records[0x1BC3])
assert struct.unpack_from("<I", fir, 0)[0] == 0

iir = D.data_bytes(tuning, obj, records[0x1BC4])
assert len(iir) == 4 * 52
assert struct.unpack_from("<I", iir, 52)[0] == 1

haf = D.data_bytes(tuning, obj, records[0xB6])
haf_window = struct.unpack_from("<2f", haf, 0x28)
haf_grid_enable = struct.unpack_from("<f", haf, 0x30)[0]
haf_grid = struct.unpack_from("<2f", haf, 0x34)
haf_overlap = struct.unpack_from("<2f", haf, 0x3C)
assert close(haf_window[0], 0.25) and close(haf_window[1], 0.25)
assert close(haf_grid_enable, 1.0)
assert close(haf_grid[0], 0.2) and close(haf_grid[1], 0.2)
assert close(haf_overlap[0], 0.0) and close(haf_overlap[1], 0.0)
haf_grid_count = [int(f32(1.0 / haf_grid[0])), int(f32(1.0 / haf_grid[1]))]
assert haf_grid_count == [5, 5]

# The hardcode filter coefficient source block is in .text. The PE mapping for
# this pinned binary is .text RVA 0x1000 -> file offset 0x400.
block_rva = 0x763788
block_off = 0x400 + (block_rva - 0x1000)
hardcode_block = dll[block_off:block_off + 20 * 4]
assert len(hardcode_block) == 80
hardcode_floats = struct.unpack("<20f", hardcode_block)
hardcode_q14 = [round(v * 16384.0) for v in hardcode_floats]
assert len(hardcode_q14) == 20
assert hardcode_q14[0] == -hardcode_q14[1]
assert hardcode_q14[2] == -hardcode_q14[3]
assert hardcode_q14[4] > 0 and hardcode_q14[5] < 0
assert hardcode_q14[16] > 0 and hardcode_q14[17] < 0

safe = {
    "schema": "E008S-source-derivation-safe-v1",
    "status": "PASS",
    "pinned_dll_sha256": DLL_SHA,
    "pinned_tuning_sha256": TUNING_SHA,
    "normal_configure_records_checked": len(configure_records),
    "normal_all_mode_shift_pair": [3, 3],
    "normal_gamma_enabled": True,
    "normal_scale_enabled": False,
    "normal_fir_enabled": False,
    "normal_iir_enabled": True,
    "haf_default_window_fraction": [0.25, 0.25],
    "haf_grid_fraction": [0.2, 0.2],
    "haf_grid_overlap": [0.0, 0.0],
    "haf_grid_count": haf_grid_count,
    "hardcode_filter_constant_count": len(hardcode_q14),
    "hardcode_filter_constant_block_sha256": sha(hardcode_block),
    "captured_windows_values_read": False,
    "captured_windows_values_emitted": False,
    "runtime_actions_performed": False
}
(HERE / "SOURCE-DERIVATION-SAFE.json").write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
print("E008S_SOURCE_DERIVATION_PASS normal_shifts=3/3 haf_grid=5x5 hardcode_constants=20")
