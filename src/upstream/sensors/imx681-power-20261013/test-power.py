#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile actual sensor function bodies against bounded API fault models."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def function(s, name):
    import re
    match = re.search(r'^static (?:inline )?(?:int|bool|void|struct imx681 \*)\s*' + name + r'\(', s, re.M)
    if not match:
        raise ValueError('missing function: ' + name)
    end = s.index('\n}', match.start()) + 3
    return s[match.start():end] + '\n'


def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    if sys.flags.optimize:
        raise ValueError('Python -O is not supported')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--parent-source', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    q = Path(__file__).resolve().parent
    m = json.loads((q / 'manifest.json').read_text())
    p = a.source / 'drivers/media/i2c/imx681.c'
    old = a.parent_source / 'drivers/media/i2c/imx681.c'
    for f, digest in [(p, m['sensor_sha256']), (old, m['parent_sensor_sha256']),
                      (a.source / 'drivers/media/i2c/imx681-tables.h', m['tables_sha256'])]:
        if f.is_symlink() or not f.is_file() or sha(f) != digest:
            raise ValueError('input pin mismatch: ' + str(f))
    if a.output.exists() or any(p.is_symlink() for p in [a.output, *a.output.absolute().parents]):
        raise ValueError('output occupied or symlink')
    for inp in [q, a.source, a.parent_source]:
        if inp.resolve() == a.output.resolve() or inp.resolve() in a.output.resolve().parents:
            raise ValueError('output nested in input')
    a.output.mkdir(parents=True)
    s, parent = p.read_text(), old.read_text()
    plain_guard = '\tif (!imx681_power_ready(sensor))\n\t\treturn -EIO;\n\n'
    control_guard = '\tif (!imx681_power_ready(sensor)) {\n\t\tpm_runtime_put_autosuspend(sensor->dev);\n\t\treturn -EIO;\n\t}\n\n'
    start_guard = '\tif (!imx681_power_ready(sensor)) {\n\t\tret = -EIO;\n\t\tgoto err_rpm_put;\n\t}\n\n'
    for name, guard in [('imx681_identify', plain_guard), ('imx681_stop_streaming', plain_guard),
                        ('imx681_s_ctrl', control_guard), ('imx681_start_streaming', start_guard)]:
        body = function(s, name)
        if body.count(guard) != 1 or body.replace(guard, '') != function(parent, name):
            raise ValueError('register payload or PM behavior changed beyond power guard: ' + name)
    for name in ['imx681_validate_endpoint', 'imx681_check_hwcfg', 'imx681_init_controls',
                 'imx681_fill_fmt', 'imx681_init_state', 'imx681_s_stream']:
        if function(s, name) != function(parent, name):
            raise ValueError('unrelated function changed: ' + name)
    constants = '\n'.join(x for x in s.splitlines() if x.startswith('#define IMX681_')) + '\n'
    for line in parent.splitlines():
        if line.startswith('#define IMX681_') and 'XCLR' not in line and line not in constants.splitlines():
            raise ValueError('unrelated constant changed: ' + line)
    enum = s[s.index('enum imx681_supply {'):s.index('\n};', s.index('enum imx681_supply {')) + 4]
    supply = s[s.index('static const char * const imx681_supply_name[]'):s.index('\n};', s.index('static const char * const imx681_supply_name[]')) + 4]
    struct = s[s.index('struct imx681 {'):s.index('\n};', s.index('struct imx681 {')) + 4]
    names = ['to_imx681', 'imx681_power_ready', 'imx681_power_off', 'imx681_power_on',
             'imx681_identify', 'imx681_s_ctrl', 'imx681_start_streaming', 'imx681_stop_streaming', 'imx681_remove']
    bodies = '\n'.join(function(s, n) for n in names)
    cleanup = s[s.index('err_power_off:'):s.index('static void imx681_remove')]
    cleanup = cleanup[cleanup.index('\n') + 1:cleanup.index('\n}')]
    wrapper = 'static int probe_error_cleanup(struct device *dev, int ret)\n{\n\tint cleanup_ret;\n' + cleanup + '\n}\n'
    fixture = (q / 'power-stub.c').read_text() + '\n' + constants + enum + supply + struct + bodies + wrapper + (q / 'power-harness.c').read_text()
    results = []
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:abort_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    flags = ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    def run_case(cc, label, content, expected):
        c = a.output / (cc + '-' + label + '.c')
        exe = c.with_suffix('')
        c.write_text(content)
        cp = subprocess.run([cc, *flags, str(c), '-o', str(exe)], text=True, capture_output=True)
        (a.output / (cc + '-' + label + '-compile.log')).write_text(cp.stdout + cp.stderr)
        if cp.returncode:
            raise ValueError('fixture compile failed: ' + str(c))
        rp = subprocess.run([str(exe)], text=True, capture_output=True, env=env, preexec_fn=no_core)
        (a.output / (cc + '-' + label + '-run.log')).write_text(rp.stdout + rp.stderr)
        if expected != (rp.returncode == 0):
            raise ValueError('unexpected fixture result: ' + label)
        results.append(dict(compiler=cc, label=label, exit_code=rp.returncode, expected_success=expected, stdout=rp.stdout.strip()))
    for cc in ['gcc', 'clang']:
        run_case(cc, 'actual', fixture, True)
    mutants = {
        'short-reset-delay': fixture.replace('#define IMX681_RESET_DELAY_MIN_US\t10000', '#define IMX681_RESET_DELAY_MIN_US\t6200'),
        'ignore-analog-release-error': fixture.replace('return ret;\n\t\t}\n\t\tsensor->avdd_on = false;', 'ret = 0;\n\t\t}\n\t\tsensor->avdd_on = false;', 1),
        'missing-identify-guard': fixture.replace(plain_guard, '', 1),
        'missing-control-guard': fixture.replace(control_guard, '', 1),
        'missing-start-guard': fixture.replace(start_guard, '', 1),
        'missing-stop-guard': fixture[:fixture.index('static int imx681_stop_streaming')] + fixture[fixture.index('static int imx681_stop_streaming'):].replace(plain_guard, '', 1),
    }
    for label, content in mutants.items():
        if content == fixture:
            raise ValueError('inactive negative control: ' + label)
        run_case('gcc', label, content, False)
    result = dict(status='PASS_ACTUAL_BODY_POWER_PORT', source_sha256=sha(p), results=results,
                  negative_controls=len(mutants), transport_modeled=True, hardware_qualified=False,
                  retained_hardware_sequence_reused=True, register_payloads_unchanged_except_guards=True)
    (a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        sys.exit(str(e))
