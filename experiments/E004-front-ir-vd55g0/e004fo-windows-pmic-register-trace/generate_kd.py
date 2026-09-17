#!/usr/bin/env python3
"""Generate bounded KD hooks for the installed qcpmic masked-register helper."""
import argparse, re
from pathlib import Path

TARGET='((REG >= 0xee3e && REG <= 0xee41) || (REG >= 0xee4a && REG <= 0xee4d) || REG == 0xee67)'

def expr(reg): return TARGET.replace('REG', reg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pmic-base', required=True)
    ap.add_argument('--output', type=Path, required=True)
    a=ap.parse_args()
    assert re.fullmatch(r'[0-9a-fA-F]{16}', a.pmic_base)
    base=int(a.pmic_base,16)
    assert base >> 48 == 0xffff and base % 0x1000 == 0
    a.output.mkdir(parents=True, exist_ok=True)
    pre=(f'.if ({expr("@w24")}) {{ r @$t0 = @$t0 + 1; '
         '.printf "E004FO_PRE hit=%u reg=%x mask=%x read_rc=%x\\n", @$t0, @w24, @w23, @w0; '
         'db @x21 L1; db @sp+0x10 L1; .if (@$t0 >= 0n64) { bd 0 } }; gc')
    post=(f'.if ({expr("@w24")}) {{ r @$t1 = @$t1 + 1; '
          '.printf "E004FO_POST hit=%u reg=%x mask=%x write_rc=%x\\n", @$t1, @w24, @w23, @w0; '
          'db @x21 L1; .if (@$t1 >= 0n64) { bd 1 } }; gc')
    esc=lambda s:s.replace('\\','\\\\').replace('"','\\"')
    arm=(f'.echo E004FO_ARM_BEGIN\nr @$t0 = 0\nr @$t1 = 0\n'
         f'bp0 {base+0x23af8:016x} "{esc(pre)}"\n'
         f'bp1 {base+0x23bec:016x} "{esc(post)}"\n'
         'bl\n.echo E004FO_ARMED_RESUMING\ng\n')
    (a.output/'arm.kd').write_text(arm)
    dry=['.echo E004FO_DRY_BEGIN','r @$t0 = 0','r @$t1 = 0']
    cases=[0xee3e,0xee41,0xee4a,0xee4d,0xee67,0xee42,0xee68]
    for r in cases:
        yes=expr(hex(r))
        dry += [f'.if ({yes}) {{ .printf "E004FO_DRY_TARGET reg=%x\\n", 0x{r:x}; db 0x{base:016x} L1 }} .else {{ .printf "E004FO_DRY_SKIP reg=%x\\n", 0x{r:x} }}']
    dry += ['.echo E004FO_DRY_END_RESUMING','g']
    (a.output/'validate.kd').write_text('\n'.join(dry)+'\n')
    print(f'PMIC base=0x{base:016x}; hooks=0x{base+0x23af8:016x},0x{base+0x23bec:016x}')

if __name__=='__main__': main()
