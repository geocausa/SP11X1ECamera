#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare only a sensor source package; no kernel tree, installation or capture."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p,value):
    if p.is_symlink() or not p.is_file() or sha(p)!=value:raise ValueError('input changed or not regular: '+str(p))
def main():
    if sys.flags.optimize:raise ValueError('Python -O is not supported')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-source',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();q=Path(__file__).resolve().parent;m=json.loads((q/'manifest.json').read_text())
    source=a.parent_source/'drivers/media/i2c';patch=q/'0001-imx681-align-frame-length.patch'
    pin(source/'imx681.c',m['parent_sensor_sha256']);pin(source/'imx681-tables.h',m['tables_sha256']);pin(patch,m['patch_sha256'])
    out=a.output.absolute()
    if any(p.is_symlink() for p in [out,*out.parents]):raise ValueError('symlink output path')
    out=out.resolve()
    if out.exists() or out.is_symlink():raise ValueError('output already exists')
    for inp in [a.parent_source,q]:
        if out==inp.resolve() or inp.resolve() in out.parents:raise ValueError('output nested in input')
    out.mkdir(parents=True,exist_ok=False);dest=out/'drivers/media/i2c';dest.mkdir(parents=True)
    for n in ['imx681.c','imx681-tables.h']:(dest/n).write_bytes((source/n).read_bytes())
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=out,check=True)
    pin(dest/'imx681.c',m['sensor_sha256']);pin(dest/'imx681-tables.h',m['tables_sha256'])
    print(json.dumps(dict(ok=True,sensor_sha256=m['sensor_sha256'],sensor_package_only=True,installed=False,hardware_qualified=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError) as e:sys.exit(str(e))
