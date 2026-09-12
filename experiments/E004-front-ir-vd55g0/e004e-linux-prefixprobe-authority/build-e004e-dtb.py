#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, subprocess

PARENT_SHA='2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'
OLD='microsoft,sp11-vd55g0-idprobe'
NEW='microsoft,sp11-vd55g0-prefixprobe'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if sha(a.parent)!=PARENT_SHA:
        raise SystemExit('E004b parent identity drift '+sha(a.parent))
    got=subprocess.check_output(['fdtget','-t','s',str(a.parent),NODE,'compatible'],text=True).strip()
    if got!=OLD:
        raise SystemExit('unexpected parent compatible '+got)
    shutil.copyfile(a.parent,a.out)
    subprocess.run(['fdtput','-t','s',str(a.out),NODE,'compatible',NEW],check=True)
    got2=subprocess.check_output(['fdtget','-t','s',str(a.out),NODE,'compatible'],text=True).strip()
    if got2!=NEW:
        raise SystemExit('compatible update failed')
    print('E004E_DTB_BUILD=PASS')
    print('PARENT_SHA256='+PARENT_SHA)
    print('OUTPUT_SHA256='+sha(a.out))
    print('ONLY_INTENDED_CHANGE='+NODE+':compatible='+NEW)

if __name__=='__main__':
    main()
