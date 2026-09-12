#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, subprocess

PARENT_SHA='e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'
OLD='microsoft,sp11-vd55g0-config42probe'
NEW='microsoft,sp11-vd55g0'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if sha(a.parent)!=PARENT_SHA:
        raise SystemExit('E004h parent drift '+sha(a.parent))
    got=subprocess.check_output(['fdtget','-t','s',str(a.parent),NODE,'compatible'],text=True).strip()
    if got!=OLD:
        raise SystemExit('parent compatible drift '+got)
    shutil.copyfile(a.parent,a.out)
    subprocess.run(['fdtput','-t','s',str(a.out),NODE,'compatible',NEW],check=True)
    print('E004L_DTB_BUILD=PASS')
    print('PARENT_SHA256='+PARENT_SHA)
    print('OUTPUT_SHA256='+sha(a.out))
    print('ONLY_INTENDED_CHANGE='+NODE+':compatible='+NEW)

if __name__=='__main__':
    main()
