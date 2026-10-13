#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reject invalid preparation inputs before cloning or modifying sources."""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-source', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    q = Path(__file__).resolve().parent
    r = q.parents[3]
    m = json.loads((q / 'manifest.json').read_text())
    if a.output.exists() or any(p.is_symlink() for p in [a.output, *a.output.absolute().parents]):
        raise ValueError('test output occupied/symlink')
    a.output.mkdir(parents=True)
    cases = []
    def reject(label, helper, parent, out, optimize=False):
        args = [sys.executable] + (['-O'] if optimize else []) + [str(helper), '--parent-source', str(parent), '--output', str(out)]
        p = subprocess.run(args, text=True, capture_output=True)
        (a.output / (label + '.log')).write_text(p.stdout + p.stderr)
        if p.returncode == 0:
            raise ValueError('accepted invalid input: ' + label)
        cases.append(dict(label=label, exit_code=p.returncode, reason=p.stderr.strip()))
    existing = a.output / 'occupied'
    existing.mkdir()
    reject('occupied', q / 'prepare.py', a.parent_source, existing)
    reject('nested-source', q / 'prepare.py', a.parent_source, a.parent_source / 'front-graph-rejected-output')
    reject('nested-repo', q / 'prepare.py', a.parent_source, q / 'front-graph-rejected-output')
    link = a.output / 'linked-output'
    link.symlink_to(a.output / 'absent-target')
    reject('symlink-output', q / 'prepare.py', a.parent_source, link)
    reject('python-optimize', q / 'prepare.py', a.parent_source, a.output / 'no-optimize-output', True)
    def parent_fixture(label):
        dest = a.output / label
        for n in m['parent_source_sha256']:
            p = dest / n
            p.parent.mkdir(parents=True, exist_ok=True)
            os.link(a.parent_source / n, p)
        return dest
    parent = parent_fixture('changed-parent')
    sensor = parent / 'drivers/media/i2c/imx681.c'
    sensor.unlink()
    sensor.write_text('invalid sensor source\n')
    reject('changed-source', q / 'prepare.py', parent, a.output / 'no-source-output')
    parent = parent_fixture('symlink-parent')
    sensor = parent / 'drivers/media/i2c/imx681.c'
    sensor.unlink()
    sensor.symlink_to(a.parent_source / 'drivers/media/i2c/imx681.c')
    reject('symlink-source', q / 'prepare.py', parent, a.output / 'no-symlink-source-output')
    fixture = a.output / 'fixture-repo'
    bundle = fixture / q.relative_to(r)
    shutil.copytree(q, bundle, ignore=shutil.ignore_patterns('__pycache__'))
    dtsi = bundle / 'x1e80100-denali-front-camera.dtsi'
    original = dtsi.read_bytes()
    dtsi.write_bytes(original + b'/* pin mutation */\n')
    reject('changed-graph', bundle / 'prepare.py', a.parent_source, a.output / 'no-graph-output')
    dtsi.write_bytes(original)
    for group in ['reference_sha256', 'sensor_patch_sha256']:
        for n in m[group]:
            p = fixture / n
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(r / n, p)
    patch = fixture / next(iter(m['sensor_patch_sha256']))
    patch.write_bytes(patch.read_bytes() + b'/* pin mutation */\n')
    reject('changed-patch', bundle / 'prepare.py', a.parent_source, a.output / 'no-patch-output')
    for n, digest in m['parent_source_sha256'].items():
        if hashlib.sha256((a.parent_source / n).read_bytes()).hexdigest() != digest:
            raise ValueError('real parent changed: ' + n)
    result = dict(status='PASS_PREPARATION_INPUT_REJECTIONS', cases=cases, original_parent_preserved=True)
    (a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
