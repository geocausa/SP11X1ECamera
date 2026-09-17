#!/usr/bin/env python3
"""Generate a bounded KD observer and an idle read-only parser check."""
import argparse
from pathlib import Path
import re

def body(tag, pointer="@x1", size="@w2", code="@w0", resume=True):
    parts = [
        "r @$t0 = @$t0 + 1",
        f'.printf "{tag}_REQUEST hit=%u code=%x bytes=%u\\n", @$t0, {code}, {size}',
    ]
    reads = "; ".join(
        f".if ({size} == 0n{n}) {{ db {pointer} L{n:x} }}"
        for n in (4, 6, 16, 20)
    )
    parts += [f".if ({pointer} != 0) {{ {reads} }}",
              ".if (@$t0 >= 0n32) { bd 0 }",
              "gc" if resume else ".echo E004FN_DRY_CASE_DONE"]
    return "; ".join(parts)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="fresh verified flash module base")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"[0-9a-fA-F]{16}", args.base)
    base = int(args.base, 16)
    assert base >> 48 == 0xffff and base % 0x1000 == 0
    args.output.mkdir(parents=True, exist_ok=True)
    command = body("E004FN").replace("\\", "\\\\").replace('"', '\\"')
    arm = (".echo E004FN_ARM_BEGIN\nr @$t0 = 0\n"
           f'bp0 {base + 0x4ac0:016x} "{command}"\n'
           "bl\n.echo E004FN_ARMED_RESUMING\ng\n")
    (args.output / "arm.kd").write_text(arm)
    # Exercise the same formatter with literal inputs and a known mapped PE header.
    # No CPU registers changed, no camera opened; only debugger pseudo-register t0.
    dry = [".echo E004FN_DRY_BEGIN", "r @$t0 = 0"]
    for n in (0, 4, 6, 16, 20, 21):
        dry += [body("E004FN_DRY", f"0x{base:016x}", f"0n{n}", "0x802f0fb0", False)]
    dry += [body("E004FN_DRY", "0", "0n4", "0x802f0fb0", False),
            ".echo E004FN_DRY_END_RESUMING", "g"]
    (args.output / "validate.kd").write_text("\n".join(dry) + "\n")
    print("Generated arm.kd and validate.kd; inspect seven completed dry cases before arming.")

if __name__ == "__main__":
    main()
