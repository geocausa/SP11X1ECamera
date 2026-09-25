#!/usr/bin/env python3
from pathlib import Path
import hashlib,re,subprocess,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
def req(v,m):
    if not v: raise AssertionError('E005W_FAIL_CLOSED '+m)
p=json.loads((HERE/'PLAN.json').read_text())
req(hashlib.sha256(OEM.read_bytes()).hexdigest()==SHA,'OEM SHA')
dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')
for a in (
 r'14001dc54:.*ldr\s+x8, \[x19, #0x150\].*?14001dc58:.*ldr\s+w8, \[x8, #0x28\].*?14001dc5c:.*str\s+w8, \[x20, #0xc\]',
 r'14001c2e4:.*ldr\s+x8, \[x19, #0x150\].*?14001c2e8:.*ldr\s+w8, \[x8, #0x28\].*?14001c2ec:.*str\s+w8, \[x20, #0xc\]',
 r'14001f190:.*mov\s+w15, #0xf',
 r'140022464:.*ldr\s+w8, \[x20, #0x349c\].*?14002246c:.*cmp\s+w24, w8.*?140022474:.*cset\s+w9, hs.*?140022478:.*str\s+w9, \[x8, #0x678\]',
 r'14002247c:.*mov\s+x9, #0xc00.*?140022480:.*mov\s+x8, #0x1200.*?140022484:.*csel\s+x8, x9, x8, lo.*?14002248c:.*str\s+x8, \[x20, #0x150\]'
):
    req(re.search(a,dis,re.S),'anchor '+a)
req(p['sp7_external_kd_only'] is True and p['local_sp11_kd_forbidden'] is True,'KD topology')
req(len(p['breakpoints'])==3,'probe count')
req(p['camera']['min_valid_frame_handles']==10,'acceptance gate')
req(p['load_e005n'] is False,'E005n remains unloaded')
req(p['native_rear_hardware_isp_runtime_authorized'] is False,'rear denied')
print('PASS_E005W_MINIMAL_IFE_MODE_DISCRIMINATOR_PREFLIGHT')
