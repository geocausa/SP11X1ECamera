#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, subprocess

PARENT_SHA='d05c4d50a4e2aaaff2216aa765802578c78551d97217cd3e422c9eda6a9c95e9'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'
OLD='microsoft,sp11-vd55g0-prefixprobe'
NEW='microsoft,sp11-vd55g0-config42probe'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--parent',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    if sha(a.parent)!=PARENT_SHA: raise SystemExit('E004e parent drift '+sha(a.parent))
    got=subprocess.check_output(['fdtget','-t','s',str(a.parent),NODE,'compatible'],text=True).strip()
    if got!=OLD: raise SystemExit('parent compatible drift '+got)
    shutil.copyfile(a.parent,a.out)
    subprocess.run(['fdtput','-t','s',str(a.out),NODE,'compatible',NEW],check=True)
    print('E004H_DTB_BUILD=PASS')
    print('PARENT_SHA256='+PARENT_SHA)
    print('OUTPUT_SHA256='+sha(a.out))
    print('ONLY_INTENDED_CHANGE='+NODE+':compatible='+NEW)
if __name__=='__main__': main()
