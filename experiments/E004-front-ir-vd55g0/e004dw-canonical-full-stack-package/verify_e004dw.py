#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());need(r['status']=='PASS_OFFLINE_FULL_STACK_PACKAGE_STAGED_NOT_ACTIVATED','status')
need(sha(D/'evidence/FRONT-PACKAGE-MANIFEST.sha256')=='caad78ac3b622b8fc2082131a32079900c55ca248dd025cf7186913366424b65','front manifest')
need(sha(D/'evidence/CAMERA-STACK-MANIFEST.sha256')=='d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373','stack manifest')
subprocess.run(['python3',str(R/'src/sp11-camera-stack/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
hw=json.loads((R/'experiments/E004-front-ir-vd55g0/e004dv-canonical-unified-camera-hardware-product/RESULT.json').read_text());need(hw['status']=='PASS_CANONICAL_UNIFIED_THREE_CAMERA_HARDWARE_AUTHORITY_EXACT','E004dv')
st=(D/'evidence/STAGE.txt').read_text();need('SP11_CAMERA_STACK_STAGE=PASS ACTIVATED=NO' in st,'stage marker')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004dw VERIFY: PASS (full stack staged offline, not installed/activated)')
