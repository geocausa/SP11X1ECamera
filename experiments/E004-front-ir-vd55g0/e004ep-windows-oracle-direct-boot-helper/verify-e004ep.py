#!/usr/bin/env python3
from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent; R=D.parents[2]; S=R/'tools/sp11-camera-windows-oracle-oneshot.sh'
def need(v,m):
    if not v: raise AssertionError(m)
s=S.read_text()
for token in ('--check-only','--reboot','Windows Direct Oracle Temp','\\EFI\\Microsoft\\Boot\\bootmgfw.efi','efibootmgr -n','BOOTORDER_AFTER','saved_entry=sp11-audio-fullio-v19c','camera-overlap-guard.sh'):
    need(token in s,token)
subprocess.run(['bash','-n',str(S)],check=True)
out=subprocess.check_output([str(S),'--check-only'],text=True,cwd=R)
need('SP11_WINDOWS_ORACLE_ONESHOT=PASS CHECK_ONLY=YES MUTATED=NO' in out,'live check')
print(out.strip())
print('E004ep VERIFY: PASS (direct Windows BootNext helper, persistent boot order untouched)')
