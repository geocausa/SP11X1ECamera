#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reproduce the receiver series and apply the bounded sensor admission patch."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p,value):
    if p.is_symlink() or not p.is_file() or sha(p)!=value:
        raise ValueError('input changed or not regular: '+str(p))

def main():
    if sys.flags.optimize:raise ValueError('Python -O is not supported')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    root=Path(__file__).resolve().parents[4]
    bundle=root/'src/upstream/sensors/imx681-hwcfg-20261013'
    m=json.loads((bundle/'manifest.json').read_text())
    patch=bundle/'0001-imx681-validate-hardware-configuration.patch'
    pin(patch,m['patch_sha256'])
    prior=root/'src/upstream/receiver/cphy-x1e-20261012/manifest.json'
    pin(prior,m['receiver_manifest_sha256'])
    helper=root/'tools/prepare-upstream-cphy-receiver.py'
    pin(helper,m['receiver_prepare_sha256'])
    # The pinned receiver preparer verifies all changed/protected parent inputs
    # and rejects occupied, nested and symlink output paths before a clone.
    subprocess.run([sys.executable,str(helper),'--parent-source',str(a.parent_source),'--output',str(a.output)],check=True)
    sensor=a.output/'drivers/media/i2c/imx681.c'
    pin(sensor,m['parent_sensor_sha256'])
    tables=a.output/'drivers/media/i2c/imx681-tables.h'
    pin(tables,m['tables_sha256'])
    data=sensor.read_bytes();sensor.unlink();sensor.write_bytes(data)
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=a.output,check=True)
    pin(sensor,m['sensor_sha256']);pin(tables,m['tables_sha256'])
    r=json.loads(prior.read_text())
    for name,value in {**r['output_source_sha256'],**r['unchanged_parent_source_sha256']}.items():
        pin(a.output/name,m['sensor_sha256'] if name=='drivers/media/i2c/imx681.c' else value)
    print(json.dumps(dict(ok=True,output=str(a.output),sensor_sha256=m['sensor_sha256'],receiver_and_other_sources_unchanged=True,installed=False,hardware_qualified=False)))

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:sys.exit(str(e))
