#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Count source-schema destinations implemented by the typed field compiler.

The input is the earlier SOURCE-ONLY work inventory, never a private profile.
Coverage counts describe compiler capability, not removed runtime dependencies.
"""
import argparse
import json
from pathlib import Path

FIELDS = {
    "cst-coefficients": [0x6168 + 24 * i + 4 * j for i in range(3) for j in range(2)],
    "ccm-coefficients": list(range(0x5868, 0x5880, 4)),
    "round-clamp": [base for base in (0x9c60, 0x9e60)] +
                   [base + 0x10 + 4 * i for base in (0x9c60, 0x9e60) for i in range(10)],
}


def coverage(inventory):
    if inventory.get("private_profile_read") is not False or inventory.get("hardware_access") is not False:
        raise ValueError("only the source-only inventory is admitted")
    commands = inventory["register_commands"]
    counts = {name: 0 for name in FIELDS}
    for command in commands:
        start, words = command["first_register"], command["private_scalar_words"]
        if type(start) is not int or type(words) is not int or start & 3 or words <= 0:
            raise ValueError("malformed source register span")
        end = start + 4 * words
        for name, registers in FIELDS.items():
            counts[name] += sum(start <= reg < end for reg in registers)
    total = inventory["mapped_register_scalar_words"]
    if sum(command["private_scalar_words"] for command in commands) != total:
        raise ValueError("source command count differs from total")
    return {"private_profile_read": False, "hardware_access": False,
            "unique_fields": {name: len(regs) for name, regs in FIELDS.items()},
            "covered_scalar_occurrences": counts, "mapped_register_scalar_words": total,
            "unimplemented_register_occurrences": total - sum(counts.values()),
            "complete_startup_profile": False, "runtime_dependencies_removed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(coverage(json.loads(args.inventory.read_text())), indent=2) + "\n"
    if args.output:
        with args.output.open("x") as out:
            out.write(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
