#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare a full source candidate with retained front graph and sensor25."""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pin(p, value):
    if p.is_symlink() or not p.is_file() or sha(p) != value:
        raise ValueError('input pin mismatch: ' + str(p))

def main():
    if sys.flags.optimize:
        raise ValueError('Python -O is not supported')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-source', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    q = Path(__file__).resolve().parent
    r = q.parents[3]
    m = json.loads((q / 'manifest.json').read_text())
    for n, d in m['parent_source_sha256'].items():
        pin(a.parent_source / n, d)
    for n, d in m['graph_sha256'].items():
        pin(q / n, d)
    for group in ['reference_sha256', 'sensor_patch_sha256']:
        for n, d in m[group].items():
            pin(r / n, d)
    out = a.output.absolute()
    if out.exists() or any(p.is_symlink() for p in [out, *out.parents]):
        raise ValueError('output occupied or symlink')
    out = out.resolve()
    for inp in [r, a.parent_source]:
        if out == inp.resolve() or inp.resolve() in out.parents:
            raise ValueError('output nested in input')
    shutil.copytree(a.parent_source, out, copy_function=os.link, symlinks=True,
                    ignore=shutil.ignore_patterns('.git'))
    sensor = out / 'drivers/media/i2c/imx681.c'
    data = sensor.read_bytes()
    sensor.unlink()
    sensor.write_bytes(data)
    for n in m['sensor_patch_sha256']:
        subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(r / n)],
                       cwd=out, check=True)
    pin(sensor, m['final_sensor_sha256'])
    for n in m['graph_sha256']:
        dest = out / 'arch/arm64/boot/dts/qcom' / n
        if dest.exists():
            raise ValueError('new graph path occupied')
        dest.write_bytes((q / n).read_bytes())
    makefile = out / 'arch/arm64/boot/dts/qcom/Makefile'
    text = makefile.read_text()
    makefile.unlink()
    makefile.write_text(text + '\ndtb-$(CONFIG_ARCH_QCOM) += x1e80100-microsoft-denali-oled-front-camera.dtb\n')
    for n, d in m['parent_source_sha256'].items():
        pin(a.parent_source / n, d)
        if n not in ['drivers/media/i2c/imx681.c', 'arch/arm64/boot/dts/qcom/Makefile']:
            pin(out / n, d)
    print(json.dumps(dict(status='PASS_FRONT_GRAPH_SOURCE_PREPARED',
                          parent_preserved=True, full_source=True,
                          sensor_sha256=sha(sensor), installed=False,
                          hardware_qualified=False)))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        sys.exit(str(e))
