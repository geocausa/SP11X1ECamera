#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Inventory front private-value destinations from public source topology only.

Reads the existing source schema, never the private profile. Reports register
locations/counts and copy-region dimensions, with no register/table values.
These are replacement-work units, not permission to reuse a vendor table.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

BLOCKS = [(0x3b60,0x3d00,"demux"),(0x3d00,0x3f00,"pdpc"),
          (0x3f00,0x4300,"binning"),(0x4300,0x4500,"lsc"),
          (0x4500,0x4700,"white-balance"),(0x4700,0x4900,"gic"),
          (0x4900,0x4b00,"bpc-abf"),(0x4b00,0x4d00,"black-level"),
          (0x5400,0x5600,"unknown-5400"),(0x5600,0x5800,"unknown-5600"),
          (0x5800,0x5a00,"ccm"),(0x5a00,0x5f00,"tone-mapper"),
          (0x5f00,0x6100,"gamma"),(0x6100,0x6300,"cst"),
          (0x9800,0xa400,"output-scalers-crop"),(0xb000,0xbf00,"statistics")]


def inventory(schema):
    text = Path(schema).read_text()
    fixed_text = text.split("native_front_profile_fixed[]",1)[1].split("native_front_profile_copies[]",1)[0]
    copies_text = text.split("native_front_profile_copies[]",1)[1]
    fixed = {int(a,16): int(b,16) for a,b in re.findall(r"\{\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+)\s*\}",fixed_text)}
    copies = [(int(a,16),int(b,16),int(n,16)) for a,b,n in
              re.findall(r"\{\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+)\s*\}",copies_text)]
    scalars = int(re.search(r"NATIVE_FRONT_PROFILE_SCALAR_WORDS (\d+)U", text).group(1))
    tables = int(re.search(r"NATIVE_FRONT_PROFILE_TABLE_BYTES (\d+)U", text).group(1))
    if sum(n for d,s,n in copies) != 4 * scalars + tables:
        raise ValueError("copy regions do not account for the declared scalar/table data")
    by_copy = {d: (s,n) for d,s,n in copies}
    commands, assigned = [], set()
    summary = Counter()
    for at,header in sorted(fixed.items()):
        n = header & 65535
        if at < 1024 or header >> 24 != 3 or header & 0x00ff0000 or not 0 < n < 512:
            continue
        reg = fixed.get(at+4)
        if reg is None or reg & 3 or reg >= 0x10000 or by_copy.get(at+8, (0,0))[1] != 4*n:
            continue
        counts = Counter()
        for i in range(n):
            r = reg + 4*i
            block = next((name for lo,hi,name in BLOCKS if lo <= r < hi), "other-functional-or-unknown")
            counts[block] += 1
            summary[block] += 1
        assigned.add(at+8)
        commands.append({"command_offset": at, "first_register": reg, "private_scalar_words": n,
                         "replacement_groups": dict(counts)})
    unmapped = [{"capsule_offset": d, "bytes": n} for d,s,n in copies if d not in assigned]
    return {"private_profile_read": False, "hardware_access": False,
            "mapped_register_scalar_words": sum(summary.values()),
            "declared_private_scalar_words": scalars,
            "non_register_scalar_words": scalars - sum(summary.values()),
            "declared_private_table_bytes": tables,
            "private_copy_bytes": sum(n for d,s,n in copies),
            "replacement_groups": dict(sorted(summary.items())), "register_commands": commands,
            "non_register_regions_requiring_separate_classification": unmapped,
            "complete_replacement": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.dumps(inventory(args.schema), indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as f:
            f.write(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
