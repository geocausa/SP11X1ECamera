#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, subprocess

PARENT_SHA='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b'
REMOVALS=[
 '/soc@0/isp@acb7000/ports/port@1',
 '/soc@0/isp@acb7000/ports/port@2',
 '/soc@0/cci@ac15000/i2c-bus@1/camera@10',
 '/soc@0/cci@ac16000/i2c-bus@1/camera@10',
]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if sha(a.parent)!=PARENT_SHA:
        raise SystemExit('E004l parent drift '+sha(a.parent))
    shutil.copyfile(a.parent,a.out)
    for node in REMOVALS:
        subprocess.run(['fdtput','-r',str(a.out),node],check=True)
    print('E004O_DTB_BUILD=PASS')
    print('PARENT_SHA256='+PARENT_SHA)
    print('OUTPUT_SHA256='+sha(a.out))
    for node in REMOVALS:
        print('REMOVED='+node)

if __name__=='__main__':
    main()
