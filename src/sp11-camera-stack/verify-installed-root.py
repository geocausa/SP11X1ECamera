#!/usr/bin/env python3
from pathlib import Path
import argparse,subprocess
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();r=a.root.resolve()
def need(v,m):
    if not v:raise AssertionError(m)
need(str(r)!='/','refuse live root')
s=r/'var/lib/sp11-camera-stack';m=s/'installed-camera-stack-manifest.sha256';need(m.is_file(),'installed manifest')
cp=subprocess.run(['sha256sum','-c',str(m)],cwd=r,text=True,capture_output=True);need(cp.returncode==0,cp.stdout+cp.stderr)
need((s/'installed-front-package-manifest.sha256').is_file(),'front manifest state');need((s/'INSTALL-STATE.txt').is_file(),'state')
need('activated=NO' in (s/'INSTALL-STATE.txt').read_text(),'activation state')
# Offline root installer is not allowed to create boot/system activation surfaces.
for p in ('boot','etc/modprobe.d','etc/modules-load.d','etc/systemd/system','lib/modules'):
    need(not (r/p).exists(),f'activation surface created: {p}')
print('SP11 CAMERA STACK INSTALLED ROOT VERIFY: PASS ACTIVATED=NO')
