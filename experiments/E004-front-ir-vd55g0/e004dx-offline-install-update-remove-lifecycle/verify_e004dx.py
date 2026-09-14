#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());need(r['status']=='PASS_DISPOSABLE_ROOT_INSTALL_UPDATE_TAMPER_REJECT_UNINSTALL_LIFECYCLE','status')
for f,tok in (
 ('INSTALL1.txt','SP11_CAMERA_STACK_ROOT_INSTALL=PASS ACTIVATED=NO'),('VERIFY1.txt','SP11 CAMERA STACK INSTALLED ROOT VERIFY: PASS ACTIVATED=NO'),('INSTALL2.txt','SP11_CAMERA_STACK_ROOT_INSTALL=PASS ACTIVATED=NO'),('VERIFY2.txt','SP11 CAMERA STACK INSTALLED ROOT VERIFY: PASS ACTIVATED=NO'),('UNINSTALL.txt','SP11_CAMERA_STACK_ROOT_UNINSTALL=PASS')):
    need(tok in (D/'evidence'/f).read_text(),f)
need('computed checksum did NOT match' in (D/'evidence/TAMPER-REJECT.err').read_text(),'tamper negative')
need('live root install is intentionally forbidden' in (D/'evidence/LIVE-INSTALL-REFUSAL.err').read_text(),'live install refusal')
need('live root uninstall is intentionally forbidden' in (D/'evidence/LIVE-UNINSTALL-REFUSAL.err').read_text(),'live uninstall refusal')
for p in ('install-staged-root.sh','verify-installed-root.py','uninstall-root.sh'):
    need((R/'src/sp11-camera-stack'/p).is_file(),p)
dw=json.loads((R/'experiments/E004-front-ir-vd55g0/e004dw-canonical-full-stack-package/RESULT.json').read_text());need(dw['status']=='PASS_OFFLINE_FULL_STACK_PACKAGE_STAGED_NOT_ACTIVATED','E004dw')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004dx VERIFY: PASS (disposable-root lifecycle bounded; live root untouched)')
