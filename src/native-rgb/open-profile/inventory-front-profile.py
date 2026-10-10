#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Inventory the private front startup profile by register block (values stay private).

Rebuilds the command capsule exactly as the kernel does (schema fixed words +
profile copy regions), walks the CDM command stream (encoding per Qualcomm's
GPL cam_cdm_util: 0x3 REG_CONT, 0x4 REG_RANDOM, 0x1/0xa/0xb DMI), and prints
per block: register range, count, and how many words come from the private
profile versus the kernel schema. No values are printed.
Usage: inventory-front-profile.py <schema.h> <profile.bin> [--json out.json]
"""
import json, re, sys
from pathlib import Path


def parse_schema(path):
    t = Path(path).read_text()
    cap = int(re.search(r"NATIVE_FRONT_PROFILE_CAPSULE_BYTES (\d+)U", t).group(1))
    fixed_s = t[t.index("native_front_profile_fixed[]"):t.index("native_front_profile_copies[]")]
    copy_s = t[t.index("native_front_profile_copies[]"):]
    fixed = [(int(a, 16), int(b, 16)) for a, b in re.findall(r"\{ (0x[0-9a-f]+), (0x[0-9a-f]+) \}", fixed_s)]
    copies = [(int(a, 16), int(b, 16), int(c, 16)) for a, b, c in
              re.findall(r"\{ (0x[0-9a-f]+), (0x[0-9a-f]+), (0x[0-9a-f]+) \}", copy_s)]
    return cap, fixed, copies


def main():
    cap, fixed, copies = parse_schema(sys.argv[1])
    prof = Path(sys.argv[2]).read_bytes()
    buf = bytearray(cap)
    src = ["zero"] * (cap // 4)
    for d, v in fixed:
        buf[d:d + 4] = v.to_bytes(4, "little"); src[d // 4] = "schema"
    for d, s, n in copies:
        buf[d:d + n] = prof[s:s + n]
        for i in range(d // 4, (d + n) // 4):
            src[i] = "profile"
    w = lambda o: int.from_bytes(buf[o:o + 4], "little")
    blocks = []
    o = 0x400
    end = max(d for d, v in fixed) + 4  # last schema word (command headers)
    while o < end:
        h = w(o); op = h >> 24; n = h & 0xffff
        if op == 0x3 and 0 < n < 512:
            reg = w(o + 4) & 0xffffff
            body = src[(o + 8) // 4:(o + 8) // 4 + n]
            blocks.append(dict(at=o, op="REG_CONT", reg=reg, count=n,
                               profile=body.count("profile"), schema=body.count("schema"), zero=body.count("zero")))
            o += 8 + 4 * n
        elif op == 0x4 and 0 < n < 512:
            regs = [w(o + 4 + 8 * i) & 0xffffff for i in range(n)]
            vals = [src[(o + 8 + 8 * i) // 4] for i in range(n)]
            blocks.append(dict(at=o, op="REG_RANDOM", reg=min(regs), reg_max=max(regs), count=n,
                               profile=vals.count("profile"), schema=vals.count("schema"), zero=vals.count("zero")))
            o += 4 + 8 * n
        elif op in (0x1, 0xa, 0xb):
            length = (h & 0xffff) + 1
            dmi = w(o + 8)
            blocks.append(dict(at=o, op="DMI", reg=dmi & 0xffffff, sel=dmi >> 24, bytes=length,
                               addr_src=src[(o + 4) // 4]))
            o += 12
        else:
            o += 4
    tables = [dict(capsule=d, bytes=n) for d, s, n in copies if n >= 0x100]
    summary = dict(capsule_bytes=cap, blocks=len(blocks),
                   reg_words_profile=sum(b.get("profile", 0) for b in blocks),
                   reg_words_schema=sum(b.get("schema", 0) for b in blocks),
                   dmi_blocks=sum(b["op"] == "DMI" for b in blocks), table_regions=tables)
    for b in blocks:
        if b["op"] == "DMI":
            print(f"{b['at']:#06x} DMI      reg={b['reg']:#07x} sel={b['sel']:#04x} bytes={b['bytes']}")
        else:
            r = f"{b['reg']:#07x}" + (f"-{b['reg_max']:#07x}" if 'reg_max' in b else f"-{b['reg'] + 4 * (b['count'] - 1):#07x}")
            print(f"{b['at']:#06x} {b['op']:<8} {r} n={b['count']:<3} profile={b['profile']} schema={b['schema']} zero={b['zero']}")
    print(json.dumps(summary))
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(dict(summary=summary, blocks=blocks), indent=1))


if __name__ == "__main__":
    main()
