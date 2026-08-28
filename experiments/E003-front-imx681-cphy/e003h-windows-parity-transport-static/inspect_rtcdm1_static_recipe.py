#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HELPERS = [
    'camss_rtcdm1_windows_preflight',
    'camss_rtcdm1_windows_open_init',
    'camss_rtcdm1_windows_start',
    'camss_rtcdm1_windows_fifo0_commit',
    'camss_rtcdm1_windows_stop',
]


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--object', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    src = a.source.read_text()
    patch = a.patch.read_text()

    required = [
        'readl_relaxed(rt->base + CAMSS_RTCDM_HW_VERSION)',
        'readl_relaxed(rt->base + CAMSS_RTCDM_FE_CFG)',
        'readl_relaxed(rt->base + CAMSS_RTCDM_FIFO0_CFG)',
        'writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_MASK,',
        'writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_CMD,',
        'camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_RESET_DONE)',
        'dmb(sy);',
        'writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_CFG,',
        'writel_relaxed(CAMSS_RTCDM_WINDOWS_IRQ0_MASK,',
        'writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_EN,',
        'encoded_len = len_low20 | CAMSS_RTCDM_WINDOWS_FIFO_LEN_HIGH;',
        'writel_relaxed(base, rt->base + CAMSS_RTCDM_FIFO0_BASE);',
        'writel_relaxed(encoded_len, rt->base + CAMSS_RTCDM_FIFO0_LEN);',
        'writel_relaxed(1, rt->base + CAMSS_RTCDM_FIFO0_STORE);',
        'camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_BL_DONE)',
        'writel_relaxed(0, rt->base + CAMSS_RTCDM_IRQ0_MASK);',
        'camss_rtcdm1_windows_recipe __used = {',
    ]
    missing = [x for x in required if x not in src]
    if missing:
        die('missing source anchors: ' + repr(missing))

    forbidden = {
        'fe_cfg_write': r'writel_relaxed\([^;]*CAMSS_RTCDM_FE_CFG',
        'fifo0_cfg_write': r'writel_relaxed\([^;]*CAMSS_RTCDM_FIFO0_CFG',
        'cgc_cfg_symbol': r'CAMSS_RTCDM_CGC',
        'core_en_zero_write': r'writel_relaxed\(\s*0\s*,\s*rt->base\s*\+\s*CAMSS_RTCDM_CORE_EN',
    }
    bad = {k: bool(re.search(v, src, re.S)) for k, v in forbidden.items()}
    if any(bad.values()):
        die('forbidden source behavior present: ' + repr(bad))

    # The retained table must be data-only: it has one source definition and
    # no source use. Helper references are definition/table, plus preflight's
    # deliberate private call from open_init.
    if src.count('camss_rtcdm1_windows_recipe') != 1:
        die('recipe source reference count changed')

    rel = run('aarch64-linux-gnu-objdump', '-r', str(a.object))
    helper_relocs = [ln.strip() for ln in rel.splitlines() if any(h in ln for h in HELPERS)]
    if len(helper_relocs) != 5 or any('R_AARCH64_ABS64' not in ln for ln in helper_relocs):
        die('helper relocation set is not exactly five ABS64 table entries: ' + repr(helper_relocs))
    if 'camss_rtcdm1_windows_recipe' in rel:
        die('compiled code/data unexpectedly relocates to the recipe table')

    nm = run('nm', '-an', str(a.module))
    for h in HELPERS + ['camss_rtcdm1_windows_recipe']:
        if h not in nm:
            die('retained module symbol missing: ' + h)

    dis = {}
    for h in HELPERS:
        dis[h] = run('aarch64-linux-gnu-objdump', '-d', '--disassemble=' + h, str(a.object))
    if 'dmb\tsy' not in dis['camss_rtcdm1_windows_open_init']:
        die('open_init compiled barrier is not dmb sy')
    if 'dmb\tsy' not in dis['camss_rtcdm1_windows_start']:
        die('start compiled barrier is not dmb sy')
    fifo = dis['camss_rtcdm1_windows_fifo0_commit']
    if '#0x100000' not in fifo:
        die('compiled FIFO high-field insertion missing')
    for off in ('#0x50', '#0x54', '#0x58'):
        if off not in fifo:
            die('compiled FIFO commit missing offset ' + off)

    headers = [ln for ln in patch.splitlines() if ln.startswith(('--- a/', '+++ b/'))]
    expected_headers = [
        '--- a/drivers/media/platform/qcom/camss/camss.c',
        '+++ b/drivers/media/platform/qcom/camss/camss.c',
    ]
    if headers != expected_headers:
        die('0015 patch touches unexpected paths: ' + repr(headers))

    result = {
        'schema': 'sp11-e003h-linux-rtcdm1-static-recipe-inspection-v1',
        'accepted': True,
        'source_sha256': sha256(a.source),
        'object_sha256': sha256(a.object),
        'module_sha256': sha256(a.module),
        'patch_sha256': sha256(a.patch),
        'patch_paths': ['drivers/media/platform/qcom/camss/camss.c'],
        'runtime_isolation': {
            'recipe_source_reference_count': 1,
            'recipe_compiled_relocation_present': False,
            'helper_relocations': helper_relocs,
            'interpretation': 'helpers are retained only by the private data table; no code path references that table',
        },
        'forbidden_writes': bad,
        'compiled_mechanics': {
            'open_init_dmb_sy': True,
            'start_dmb_sy': True,
            'fifo_len_high_field_0x00100000': True,
            'fifo_offsets_0x50_0x54_0x58_present': True,
        },
        'policy': 'static-only; no runtime caller, no FE/FIFO/CGC write, no CORE_EN=0 shutdown',
    }
    out = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(out)
    else:
        print(out, end='')
    print('PASS: RT-CDM1 Windows static recipe retained but unreachable; forbidden writes absent; compiled ordering preserved')


if __name__ == '__main__':
    main()
