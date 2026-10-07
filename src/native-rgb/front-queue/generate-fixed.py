#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Private fixed-IQ cadence fixture; no device access or product 3A claims."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "src/front-imx681/userspace/iq/vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization"
SEED_SHA = "1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa"
BYTES = 41088

def constants(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("source constant absent: " + name)

def generate(seed, last):
    if len(seed) != BYTES or hashlib.sha256(seed).hexdigest() != SEED_SHA:
        raise ValueError("private R4 seed identity")
    if seed[:8] != b"E3HPIX01" or struct.unpack_from("<Q", seed, 44)[0] != 4:
        raise ValueError("capsule framing")
    count = struct.unpack_from("<I", seed, 20)[0]
    if count != 36 or not 8 <= last <= 128:
        raise ValueError("section/request bounds")
    sections = [struct.unpack_from("<IIII", seed, 64 + 16*i) for i in range(count)]
    modules = [(o,n) for t,i,o,n in sections if t == 4 and i == 0]
    if len(modules) != 1 or modules[0][1] != 288:
        raise ValueError("module section shape")
    offset = modules[0][0]
    if offset + 288 > BYTES:
        raise ValueError("module bounds")
    slots = constants(BASE / "e-template-free-capsule/build-template-free-0076-capsules.py", "REG_SLOT")
    banks = constants(BASE / "f-native-iq-backends/generate-steady-scalar-state.py", "BANK_REGS")
    fields = []
    for module, registers in banks.items():
        inverse = module in ("GTM", "GAMMA")
        for register in registers:
            mi, si = slots[register]
            loc = offset + 32*mi + 4 + 4*si
            if not seed[offset + 32*mi] & (1 << si):
                raise ValueError("bank field absent from mask")
            expected = 0 if inverse else 1
            if struct.unpack_from("<I", seed, loc)[0] != expected:
                raise ValueError("R4 source-qualified bank mismatch")
            fields.append((loc,inverse))
    if len(fields) != 16 or len({x[0] for x in fields}) != 16:
        raise ValueError("bank field coverage")
    capsules = []
    for request in range(4,last + 1):
        capsule = bytearray(seed)
        struct.pack_into("<Q", capsule, 44, request)
        for loc,inverse in fields:
            struct.pack_into("<I", capsule, loc, (request if inverse else request + 1) & 1)
        capsules.append(bytes(capsule))
    if capsules[0] != seed:
        raise ValueError("R4 fixture changed")
    return b"".join(capsules)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--last", type=int, default=96)
    args = ap.parse_args()
    data = generate(args.seed.read_bytes(), args.last)
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(data)
    print(json.dumps({"status":"PASS_PRIVATE_FIXED_IQ_BANK_CADENCE", "first_request":4,
                      "last_request":args.last, "capsules":args.last-3, "bank_fields":16,
                      "sha256":hashlib.sha256(data).hexdigest(), "live_3a":False}))
if __name__ == "__main__":
    main()
