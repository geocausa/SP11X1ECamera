#!/usr/bin/env python3
from pathlib import Path
import subprocess
REPO=Path(__file__).resolve().parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
s=Path('/var/lib/sp11-camera-stack');need((s/'installed-camera-stack-manifest.sha256').is_file(),'state manifest')
cp=subprocess.run(['sudo','-n','sh','-c','cd / && sha256sum -c /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256'],text=True,capture_output=True);need(cp.returncode==0,cp.stdout+cp.stderr)
need('activated=NO' in (s/'INSTALL-STATE.txt').read_text(),'activation state')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/usr/bin/sp11-front-imx681','/usr/bin/sp11-front-imx681-discover'):need(Path(p).exists(),p)
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
need(not any(Path('/dev').glob('media*')),'media node')
print('SP11 CAMERA STACK LIVE VERIFY: PASS INSTALLED=YES ACTIVATED=NO')
