#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Mutate a DTB to exercise graph protection, without hardware access."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    m = runpy.run_path(str(Path(__file__).with_name('prepare.py')))
    m['need'](not a.out.exists(), 'retain existing controls')
    golden = m['GOLDEN'] / 'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb'
    m['validate'](golden, a.candidate)
    a.out.mkdir()
    rsc, cell = m['RSC'], m['cell']
    mutations = [
        ('wrong-parent', rsc + '/regulators-10', 'vdd-l6-l7-supply', cell(0x191)),
        ('unsupported-voltage', rsc + '/regulators-10/ldo7', 'regulator-min-microvolt', cell(2900000)),
        ('initial-mode', rsc + '/regulators-11/ldo3', 'regulator-initial-mode', cell(1)),
        ('existing-property', rsc + '/regulators-0/bob2', 'regulator-max-microvolt', cell(2992000)),
        ('extra-actuator', rsc + '/regulators-10/ldo16', None, None),
        ('missing-constraint', rsc + '/regulators-11/ldo3', 'regulator-max-microvolt', None),
    ]
    results = []
    for name, node, prop, value in mutations:
        dest = a.out / (name + '.dtb')
        shutil.copyfile(a.candidate, dest)
        if prop is None:
            cmd = ['fdtput', '-p', '-c', str(dest), node]
        elif value is None:
            cmd = ['fdtput', '-d', str(dest), node, prop]
        else:
            cmd = ['fdtput', '-t', 'bx', str(dest), node, prop, *[f'{x:x}' for x in value]]
        subprocess.run(cmd, check=True)
        try:
            m['validate'](golden, dest)
        except ValueError as exc:
            results.append({'name': name, 'rejected': True, 'reason': str(exc)})
        else:
            raise RuntimeError('mutation admitted: ' + name)
    output = {'status': 'PASS_PROVIDER_DELTA_REJECTION_CONTROLS', 'controls': results, 'candidate_revalidated': m['validate'](golden, a.candidate)}
    (a.out / 'RESULT.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))

if __name__ == '__main__':
    main()
