#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate the open SP11 front ISP start-up profile from published sources.

Inputs (all in this repository):
  schema   kernel native-front-profile-schema.h (instruction topology, no data)
  regs     front-ae/tuning/imx681-front-isp-regs.txt (register configuration)
  lsc      front-ae/tuning/imx681-front-lsc-v1.txt (our measured shading mesh)
  abf      front-ae/tuning/imx681-front-abf-v1.json (our noise LUT, gen-abf-lut.py)
Generated here:
  gamma    start-up GLUT: the sRGB transfer curve (the IPA replaces it every frame)
  zeros    tables of modules switched off (PDPC, GIC, 0x5408, GTM), the unused
           DS4/DS16 filter tables and the unused BF statistics tables

Usage: gen-front-open-profile.py schema regs lsc abf out.bin [lsc.bin abf.bin]
(the optional outputs are the packed LSC/ABF tables for native_front_lsc/abf).
Prints the SHA-256 of the result. Every profile word must come from exactly one
of the sources above; unused register lines are an error.
"""
import hashlib
import struct
import sys
from frontprof import HEADER, MAGIC, TABLES, Schema, read_regs, reg_value

LSC_TABLE = 884


def srgb_gamma12():
    """257 points of the sRGB OETF on a 12-bit scale, packed base12 | delta12 << 12."""
    pts = []
    for i in range(257):
        x = i / 256.0
        y = 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
        pts.append(min(4095, int(round(y * 4095))))
    words = [pts[i] | (((pts[i + 1] - pts[i]) & 0xFFF) << 12) for i in range(256)]
    return struct.pack("<256I", *words)


def load_lsc(path):
    """imx681-front-lsc-v1.txt (13x17 Q10 gains per colour) or its packed .bin."""
    if not path.endswith(".txt"):
        return open(path, "rb").read()
    grids, cur = {}, None
    for ln in open(path):
        ln = ln.split("#", 1)[0].strip()
        if not ln:
            continue
        if ln.endswith(":"):
            cur = grids.setdefault(ln[:-1], [])
        else:
            cur.extend(int(x) for x in ln.split())
    r, g, b = grids["red"], grids["green"], grids["blue"]
    if not len(r) == len(g) == len(b) == 13 * 17 or max(r + g + b) >= 1 << 13:
        raise ValueError("LSC text: expected 13x17 Q10 grids below 8192")
    s1 = struct.pack("<221I", *[r[i] | g[i] << 14 for i in range(221)])
    s2 = struct.pack("<221I", *[b[i] | g[i] << 14 for i in range(221)])
    return s1 + s2 + bytes(LSC_TABLE)


def load_abf(path):
    """imx681-front-abf-v1.json (64 non-increasing values, open-profile/gen-abf-lut.py) or .bin."""
    if not path.endswith(".json"):
        return open(path, "rb").read()
    import json
    v = json.load(open(path))["values"]
    if len(v) != 64 or any(not 1 <= x <= 511 for x in v) or any(v[i + 1] > v[i] for i in range(63)):
        raise ValueError("ABF json: expected 64 non-increasing values in 1..511")
    return struct.pack("<64I", *[v[i] | ((v[i] - v[i + 1]) << 9 if i < 63 else 0) for i in range(64)])


def tables(lsc, abf):
    if len(lsc) != 3 * LSC_TABLE or any(lsc[2 * LSC_TABLE:]):
        raise ValueError("LSC: expected 3 x 884 bytes with a zero third selector")
    if len(abf) != 256:
        raise ValueError("ABF: expected 256 bytes")
    gamma = srgb_gamma12()
    return {
        ("LSC", 1): lsc[:LSC_TABLE], ("LSC", 2): lsc[LSC_TABLE:2 * LSC_TABLE], ("LSC", 3): lsc[2 * LSC_TABLE:],
        ("BPC_ABF", 1): abf,
        ("GAMMA", 0): gamma, ("GAMMA", 1): gamma, ("GAMMA", 2): gamma, ("GAMMA", 3): gamma,
    }


def generate(schema, regs, lsc, abf):
    out = bytearray(schema.size)
    out[0:8] = MAGIC
    out[8:HEADER] = struct.pack("<14I", *schema.identity())
    tab = tables(lsc, abf)
    used = set()
    for off, lab in schema.words.items():
        if lab[0] == "reg":
            v, key = reg_value(regs, lab[1], lab[2])
            used.add(key)
        elif lab[0] == "const":
            v = regs[lab[1]]
            used.add(lab[1])
        else:
            _, t, i, k = lab
            data = tab.get(TABLES[(t, i)])
            v = struct.unpack_from("<I", data, k)[0] if data else 0
        struct.pack_into("<I", out, off, v)
    ranged = regs.get("_ranged", set())
    unused = [k for k in regs if k not in used and k != "_ranged" and k not in ranged]
    if unused:
        raise ValueError("unused register source lines: %s" % unused[:8])
    return bytes(out)


def main():
    schema = Schema(sys.argv[1])
    regs = read_regs(sys.argv[2])
    lsc, abf = load_lsc(sys.argv[3]), load_abf(sys.argv[4])
    data = generate(schema, regs, lsc, abf)
    open(sys.argv[5], "wb").write(data)
    if len(sys.argv) > 7:
        open(sys.argv[6], "wb").write(lsc)
        open(sys.argv[7], "wb").write(abf)
    print(hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
