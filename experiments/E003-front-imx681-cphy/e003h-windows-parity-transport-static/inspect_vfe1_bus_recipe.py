#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HELPERS = [
    'vfe680_x1e_bus_prepare',
    'vfe680_x1e_bus_update',
    'vfe680_x1e_bus_stop',
]
ORDER = [0, 1, 2, 3, 11, 18, 12, 14, 13]


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_body(src, name):
    start = src.find(name + '(')
    if start < 0:
        die('missing function ' + name)
    brace = src.find('{', start)
    if brace < 0:
        die('missing function brace ' + name)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                return src[brace:i + 1]
    die('unterminated function ' + name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--vfe-source', type=Path, required=True)
    ap.add_argument('--object', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('--oracle', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    src = a.source.read_text()
    vfe_src = a.vfe_source.read_text()
    patch = a.patch.read_text()
    oracle = json.loads(a.oracle.read_text())
    if not oracle.get('accepted'):
        die('dynamic address oracle is not accepted')
    if oracle.get('lifecycle') != ('BUS static config -> BUS enable -> initial dynamic IOVA set -> '
                                    'ISP_START_DONE -> repeated per-frame dynamic IOVA sets -> BUS disable'):
        die('oracle lifecycle drift')

    required = [
        '#define VFE680_X1E_BUS_IMAGE_ADDR\t\t0x04',
        '#define VFE680_X1E_BUS_META_ADDR\t\t0x40',
        'dma_addr_t qc10c;',
        'dma_addr_t ds4;',
        'dma_addr_t ds16;',
        'dma_addr_t aec_be;',
        'dma_addr_t rs;',
        'dma_addr_t bhist;',
        'dma_addr_t awb_bg;',
        'dma_addr_t tl_bg;',
        'VFE680_X1E_QC10C_Y_DATA_OFF',
        'VFE680_X1E_QC10C_C_META_OFF',
        'VFE680_X1E_QC10C_C_DATA_OFF',
        'cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN',
        'vfe680_x1e_windows_bus_recipe __used = {',
    ]
    missing = [x for x in required if x not in src]
    if missing:
        die('missing source anchors: ' + repr(missing))

    m = re.search(r'static const u8 vfe680_x1e_windows_bus_client_order\[\] = \{(.*?)\};', src, re.S)
    if not m:
        die('missing BUS client order array')
    got_order = [int(x) for x in re.findall(r'\b\d+\b', m.group(1))]
    if got_order != ORDER:
        die('BUS client order drift: ' + repr(got_order))

    prepare = function_body(src, 'vfe680_x1e_bus_prepare')
    p_config = prepare.find('vfe680_x1e_bus_config_client')
    p_enable = prepare.find('vfe680_x1e_bus_set_enabled(vfe, true)')
    p_addr = prepare.find('vfe680_x1e_bus_write_addresses')
    if min(p_config, p_enable, p_addr) < 0 or not p_config < p_enable < p_addr:
        die('prepare MMIO sequence is not config -> enable -> initial addresses')
    update = function_body(src, 'vfe680_x1e_bus_update')
    if 'vfe680_x1e_bus_write_addresses' not in update or 'vfe680_x1e_bus_config_client' in update or 'set_enabled' in update:
        die('per-frame update is not address-only')
    stop = function_body(src, 'vfe680_x1e_bus_stop')
    if 'vfe680_x1e_bus_set_enabled(vfe, false)' not in stop:
        die('stop does not disable Windows BUS resource order')

    target = function_body(src, 'vfe680_x1e_bus_target')
    for frag in ('CAMSS_X1E80100', 'vfe->id == 1', '!vfe_is_lite(vfe)'):
        if frag not in target:
            die('target gate drift: ' + frag)

    # Captured Windows addresses and allocator slots are evidence, never Linux constants.
    captured = set()
    for key in ('first_pre_start_set', 'first_post_start_set'):
        for rec in oracle[key]:
            captured.add(rec['image'].lower())
            captured.add(rec['meta'].lower())
    bad_iovas = sorted(x for x in captured if x in src.lower())
    if bad_iovas:
        die('captured Windows IOVA frozen into Linux source: ' + repr(bad_iovas))
    if '0x76c000' in src.lower():
        die('Windows QC10C allocator slot stride frozen into Linux source')

    # Existing fail-close remains before any VFE output setup.
    gate = re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}', vfe_src, re.S)
    if not gate:
        die('vfe_enable_v2 missing')
    g = gate.group(1)
    if 'line->id == VFE_LINE_PIX' not in g or 'return -EOPNOTSUPP;' not in g:
        die('VFE1 PIX fail-close missing')
    if g.find('return -EOPNOTSUPP;') > g.find('mutex_lock(&vfe->stream_lock)'):
        die('VFE1 PIX fail-close moved after stream lock')

    # Patch scope is one VFE680 source file only.
    paths = re.findall(r'^--- a/(.+)$', patch, re.M)
    if paths != ['drivers/media/platform/qcom/camss/camss-vfe-680.c']:
        die('0017 patch path set drift: ' + repr(paths))
    if src.count('vfe680_x1e_windows_bus_recipe') != 1:
        die('private recipe source reference count changed')
    ops = re.search(r'const struct vfe_hw_ops vfe_ops_680 = \{(.*?)\n\};', src, re.S)
    if not ops or 'x1e_bus_' in ops.group(1) or 'windows_bus_recipe' in ops.group(1):
        die('runtime vfe_ops_680 references private BUS recipe')

    rel = run('aarch64-linux-gnu-objdump', '-r', str(a.object))
    helper_relocs = [ln.strip() for ln in rel.splitlines() if any(h in ln for h in HELPERS)]
    if len(helper_relocs) != 3 or any('R_AARCH64_ABS64' not in ln for ln in helper_relocs):
        die('helper relocations are not exactly three private-table ABS64 entries: ' + repr(helper_relocs))
    if 'vfe680_x1e_windows_bus_recipe' in rel:
        die('compiled code/data unexpectedly relocates to recipe table')

    nm_obj = run('aarch64-linux-gnu-nm', '-an', str(a.object))
    nm_mod = run('aarch64-linux-gnu-nm', '-an', str(a.module))
    for sym in HELPERS + ['vfe680_x1e_windows_bus_recipe']:
        if sym not in nm_obj or sym not in nm_mod:
            die('retained symbol missing: ' + sym)

    result = {
        'schema': 'sp11-e003h-linux-vfe1-bus-unreachable-recipe-inspection-v1',
        'accepted': True,
        'source_sha256': sha(a.source),
        'object_sha256': sha(a.object),
        'module_sha256': sha(a.module),
        'patch_sha256': sha(a.patch),
        'oracle_sha256': sha(a.oracle),
        'patch_paths': paths,
        'client_order': ORDER,
        'initial_mmio_order': ['static_config', 'enable', 'dynamic_addresses'],
        'dynamic_registers': {'image_addr': '0x04', 'meta_addr': '0x40'},
        'qc10c_offsets': {'y_meta': 0, 'y_data': 0x6000, 'c_meta': 0x4f2000, 'c_data': 0x4f5000},
        'runtime_isolation': {
            'recipe_source_reference_count': 1,
            'recipe_compiled_relocation_present': False,
            'helper_relocations': helper_relocs,
            'vfe_ops_reference_present': False,
            'pix_stream_gate': '-EOPNOTSUPP before stream lock/IRQ/output',
        },
        'windows_iovas_frozen': False,
        'windows_slot_stride_frozen': False,
        'policy': 'build/static only; Linux DMA IOVAs are caller-provided; no module load, RT-CDM submission, PIX enable or sensor transmission authorized',
    }
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: VFE1 BUS recipe is oracle-ordered, Linux-IOVA-driven, retained-only and blocked from runtime')


if __name__ == '__main__':
    main()
