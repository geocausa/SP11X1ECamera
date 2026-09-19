#!/usr/bin/env python3
"""Generate read-only bounded Windows flash-module/channel and timer RMW observer."""
import argparse, re
from pathlib import Path

# WinDbg/KD MASM expressions use single & and | for boolean composition here.
TARGET_REGISTERS=(0xee3e,0xee3f,0xee40,0xee41,0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e,0xee67)
SKIP_REGISTERS=(0xee3d,0xee42,0xee45,0xee47,0xee49,0xee4f,0xee66,0xee68)

def expr(reg):
    # Parenthesize EACH comparison: WinDbg MASM does not interpret the
    # unparenthesized mixture of >=, <=, &, | and == as Python would.
    return "(" + " | ".join(f"({reg} == 0x{a:04x})" for a in TARGET_REGISTERS) + ")"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pmic-base', required=True)
    ap.add_argument('--output', type=Path, required=True)
    a=ap.parse_args()
    assert re.fullmatch(r'[0-9a-fA-F]{16}', a.pmic_base)
    base=int(a.pmic_base,16)
    assert base >> 48 == 0xffff and base % 0x1000 == 0
    a.output.mkdir(parents=True, exist_ok=True)

    # At +0x23af8 the one-byte read has returned. w24 is still the target
    # register, w23 is the mask, [sp+0x18] is the read byte and [sp+0x10]
    # is the requested byte.
    pre=(f'.if ({expr("@w24")}) {{ r @$t0 = @$t0 + 1; '
         '.printf "E004GB_PRE hit=%u reg=%x mask=%x read_rc=%x\\n", @$t0, @w24, @w23, @w0; '
         'db @sp+0x18 L1; db @sp+0x10 L1; .if (@$t0 >= 0n128) { bd 0 } }; gc')

    # w24 is clobbered at +0x23b0c before the write. The helper packs the
    # original register into the low 16 bits of w27 at +0x23aac, and x21
    # points to the final one-byte write buffer by +0x23bec.
    preg='(@w27 & 0xffff)'
    post=(f'.if ({expr(preg)}) {{ r @$t1 = @$t1 + 1; '
          f'.printf "E004GB_POST hit=%u reg=%x mask=%x write_rc=%x\\n", @$t1, {preg}, @w23, @w0; '
          'db @x21 L1; .if (@$t1 >= 0n128) { bd 1 } }; gc')
    esc=lambda s:s.replace('\\','\\\\').replace('"','\\"')
    arm=(f'.echo E004GB_ARM_BEGIN\nr @$t0 = 0\nr @$t1 = 0\n'
         f'bp0 {base+0x23af8:016x} "{esc(pre)}"\n'
         f'bp1 {base+0x23bec:016x} "{esc(post)}"\n'
         'bl\n.echo E004GB_ARMED_STAY_BROKEN\n')
    (a.output/'arm.kd').write_text(arm)

    dry=['.echo E004GB_DRY_BEGIN','r @$t0 = 0','r @$t1 = 0']
    cases=[0xee3e,0xee3f,0xee40,0xee41,0xee3d,0xee42,0xee45,0xee46,0xee47,0xee49,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e,0xee4f,0xee66,0xee67,0xee68]
    for r in cases:
        yes=expr(hex(r))
        dry += [f'.if ({yes}) {{ .printf "E004GB_DRY_TARGET reg=%x\\n", 0x{r:x} }} .else {{ .printf "E004GB_DRY_SKIP reg=%x\\n", 0x{r:x} }}']
    dry += [
        'r @$t2 = 0x1234ee4a',
        '.if (((@$t2 & 0xffff) == 0xee4a)) { .printf "E004GB_DRY_POSTREG raw=%x reg=%x\\n", @$t2, (@$t2 & 0xffff) } .else { .echo E004GB_DRY_POSTREG_FAIL }',
        '.echo E004GB_DRY_END_STAY_BROKEN'
    ]
    (a.output/'validate.kd').write_text('\n'.join(dry)+'\n')
    print(f'PMIC base=0x{base:016x}; hooks=0x{base+0x23af8:016x},0x{base+0x23bec:016x}')

if __name__=='__main__': main()
