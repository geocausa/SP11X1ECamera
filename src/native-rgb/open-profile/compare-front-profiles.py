#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Lab check: what the hardware is programmed with, reference vs open profile.

Materializes both profiles like the driver, applies the same load-time
overrides the daily boot uses (native_front_ccm_q7, native_front_reg_mask,
native_front_lsc, native_front_abf) and lists every capsule difference by
register / table. Prints only addresses, counts and classes, never values of
the reference.

Usage: compare-front-profiles.py schema ref.bin open.bin camss-params.txt lsc.bin abf.bin
"""
import collections
import re
import struct
import sys
from frontprof import TABLES, Schema, le

LSC_SEL1 = (0x3B40, 0x4740, 0x7600)
LSC_SEL2 = (0x3EC0, 0x65C0, 0x7980)
ABF_AT = (0x64C0, 0x8280)


def apply_params(schema, cap, params, lsc, abf):
    p = dict(re.findall(r"(\w+)=(\S+)", params))
    if "native_front_ccm_q7" in p:
        m = [int(x) for x in p["native_front_ccm_q7"].split(",")]
        s13 = lambda v: v & 0x1FFF
        hits = 0
        for o in range(0, len(cap) - 48, 4):
            if le(cap, o) == (3 << 24) | 10 and le(cap, o + 4) == 0x5868:
                for r in range(3):
                    struct.pack_into("<I", cap, o + 8 + 8 * r, s13(m[r]) | s13(m[3 + r]) << 16)
                    struct.pack_into("<I", cap, o + 12 + 8 * r, s13(m[6 + r]))
                hits += 1
        assert hits == 3, hits
    if "native_front_reg_mask" in p:
        t = [int(x, 0) for x in p["native_front_reg_mask"].split(",")]
        t = [t[i:i + 3] for i in range(0, len(t), 3)]
        for s in schema.sections(cap):
            if s["type"] not in (1, 3):
                continue
            for o, reg in schema.walk(cap, s["off"], s["size"]):
                for r, a, b in t:
                    if r == reg:
                        struct.pack_into("<I", cap, o, (le(cap, o) & a) | b)
    if p.get("native_front_lsc") == "1":
        for a in LSC_SEL1:
            cap[a:a + 884] = lsc[:884]
        for a in LSC_SEL2:
            cap[a:a + 884] = lsc[884:1768]
    if p.get("native_front_abf") == "1":
        for a in ABF_AT:
            cap[a:a + 256] = abf
    return cap


def main():
    schema = Schema(sys.argv[1])
    ref, opn = open(sys.argv[2], "rb").read(), open(sys.argv[3], "rb").read()
    params = open(sys.argv[4]).read()
    lsc, abf = open(sys.argv[5], "rb").read(), open(sys.argv[6], "rb").read()
    a = apply_params(schema, schema.materialize(ref), params, lsc, abf)
    b = apply_params(schema, schema.materialize(opn), params, lsc, abf)
    lab = {}
    for s in schema.sections(a):
        if s["type"] in (1, 3):
            for o, reg in schema.walk(a, s["off"], s["size"]):
                lab[o] = "reg 0x%04x" % reg
        else:
            name = TABLES.get((s["type"], s["index"]), ("records", 0))
            for o in range(s["off"], s["off"] + s["size"], 4):
                lab[o] = "table %s/%d" % name if s["type"] != 4 else "records"
    diff = collections.Counter()
    for o in range(0, len(a), 4):
        if a[o:o + 4] != b[o:o + 4]:
            diff[lab.get(o, "header 0x%x" % o)] += 1
    regs = sorted(k for k in diff if k.startswith("reg"))
    print("capsule bytes", len(a), "differing words", sum(diff.values()))
    print("tables:", {k: v for k, v in diff.items() if not k.startswith("reg")})
    print("registers (%d):" % len(regs), " ".join(k[4:] for k in regs))


if __name__ == "__main__":
    main()
