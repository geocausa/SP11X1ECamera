#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());need(r['status']=='PASS_LIVE_FILESYSTEM_INSTALL_UPDATE_UNINSTALL_WITH_ZERO_ACTIVATION_SIDE_EFFECTS','status')
for f,tok in (('INSTALL1.txt','SP11_CAMERA_STACK_LIVE_INSTALL=PASS ACTIVATED=NO'),('VERIFY1.txt','SP11 CAMERA STACK LIVE VERIFY: PASS INSTALLED=YES ACTIVATED=NO'),('INSTALL2.txt','SP11_CAMERA_STACK_LIVE_INSTALL=PASS ACTIVATED=NO'),('VERIFY2.txt','SP11 CAMERA STACK LIVE VERIFY: PASS INSTALLED=YES ACTIVATED=NO'),('UNINSTALL.txt','SP11_CAMERA_STACK_LIVE_UNINSTALL=PASS ACTIVATED=NO')):
    need(tok in (D/'evidence'/f).read_text(),f)
ss=[D/'evidence'/f'ACTIVATION-{x}.txt' for x in ('BEFORE','INSTALLED','UPDATED','UNINSTALLED')]
need(len({sha(x) for x in ss})==1,'activation snapshots differ')
for p in ('install-live-unactivated.sh','verify-live-unactivated.py','uninstall-live-unactivated.sh'):
    need((R/'src/sp11-camera-stack'/p).is_file(),p)
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/usr/bin/sp11-front-imx681','/usr/bin/sp11-front-imx681-discover','/var/lib/sp11-camera-stack'):
    need(not Path(p).exists(),'managed live path remains '+p)
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
need(not any(Path('/dev').glob('media*')),'media node')
print('E004dy VERIFY: PASS (live install/update/uninstall; activation surfaces byte-exact)')
