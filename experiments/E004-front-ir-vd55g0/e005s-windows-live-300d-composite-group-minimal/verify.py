#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
def req(v,m):
    if not v: raise AssertionError('E005S_FAIL_CLOSED '+m)
p=json.loads((HERE/'PLAN.json').read_text())
req(p['breakpoint_count']==3,'bp count')
req(p['load_e005n'] is False,'no E005n')
req(OEM.is_file() and hashlib.sha256(OEM.read_bytes()).hexdigest()==SHA,'OEM SHA')
dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')
for pat in (
 r'140016de8:.*ldr\s+w2, \[x21, #0x8c0\]',
 r'14001fc98:.*mov\s+x23, x0',
 r'14001fce8:.*mov\s+w9, #0x300d',
):
 req(re.search(pat,dis) is not None,pat)
print('PASS_E005S_PREFLIGHT_MINIMAL_3BP_300D_GROUP_FIFO_MATCHER_WM16_GOLDEN_ROLLBACK')
