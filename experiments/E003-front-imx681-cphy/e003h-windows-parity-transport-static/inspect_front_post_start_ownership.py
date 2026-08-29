#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

EXPECTED_ORACLE_SHA = 'd426c7cf4525f36c80623cab628061005c880abd5df02d17d8a76683fea4e66e'
EXPECTED_START_INSPECTION_SHA = 'dc4a86ae51cfc608074194d89874268d03cd52569591694b4e32c71dd3ec700a'
EXPECTED_PIX_OWNERSHIP_SHA = 'bc8bf64152882e8c312e0e1379b544e2ae733dc75b4e571784fac3b88b4b7dcf'
EXPECTED_BUS_INSPECTION_SHA = '92715605c99523366dd619331c6abe9bb09c7e6476bf8921ccb5b18cbaae262e'
EXPECTED_RTCDM_INSPECTION_SHA = '23f9f601f0e9b8880e447d17685585bbdc1e0058a8be60fcf330172e366aa346'
EXPECTED_STAGES = [
    'CAMSS_X1E_FRONT_POST_START_EPOCH0',
    'CAMSS_X1E_FRONT_POST_START_VFE1_BUS_UPDATE',
    'CAMSS_X1E_FRONT_POST_START_RTCDM_BATCH_CONSUME',
    'CAMSS_X1E_FRONT_POST_START_COMPLETION_RETIRE',
]


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def need(text, fragment, label):
    if fragment not in text:
        die(label + ': ' + fragment)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--camss-source', type=Path, required=True)
    ap.add_argument('--vfe-source', type=Path, required=True)
    ap.add_argument('--object', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('--oracle', type=Path, required=True)
    ap.add_argument('--start-inspection', type=Path, required=True)
    ap.add_argument('--pix-ownership', type=Path, required=True)
    ap.add_argument('--bus-inspection', type=Path, required=True)
    ap.add_argument('--rtcdm-inspection', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    expected_files = [
        (a.oracle, EXPECTED_ORACLE_SHA, 'post-start oracle'),
        (a.start_inspection, EXPECTED_START_INSPECTION_SHA, '0022 start inspection'),
        (a.pix_ownership, EXPECTED_PIX_OWNERSHIP_SHA, '0018 PIX ownership'),
        (a.bus_inspection, EXPECTED_BUS_INSPECTION_SHA, '0017 BUS inspection'),
        (a.rtcdm_inspection, EXPECTED_RTCDM_INSPECTION_SHA, '0015 RT-CDM inspection'),
    ]
    for p, h, label in expected_files:
        if sha(p) != h:
            die(label + ' identity drift')
        if not json.loads(p.read_text()).get('accepted'):
            die(label + ' not accepted')

    oracle = json.loads(a.oracle.read_text())
    sessions = oracle['runtime_timeline']['sessions']
    if len(sessions) != 2 or any(x['observed_initial_prime_depth_bundles'] != 2 for x in sessions):
        die('two-session/two-prime-bundle runtime proof drift')
    if any(x['first_post_start_bundle']['last_seq'] >= x['first_completion_cycle']['first_seq'] for x in sessions):
        die('first post-start bundle no longer precedes first completion')
    if any(x['post_completion_refill_bundle']['first_seq'] <= x['first_completion_cycle']['last_seq'] for x in sessions):
        die('refill no longer follows first completion cycle')
    if oracle['completion_policy']['cross_group_order_required'] is not False:
        die('post-start oracle incorrectly requires completion cross-group order')

    pix = json.loads(a.pix_ownership.read_text())
    if pix.get('slots') != 2 or pix.get('cross_group_order_required') is not False:
        die('0018 two-slot/independent-group ownership drift')
    if pix.get('linux_logical_completion_mask') != '0x1f':
        die('0018 completion mask drift')

    src = a.camss_source.read_text()
    vfe = a.vfe_source.read_text()
    patch = a.patch.read_text()

    required = [
        '#define CAMSS_X1E_FRONT_POST_START_STAGE_COUNT\t4',
        '#define CAMSS_X1E_FRONT_POST_START_BUNDLE_CLIENTS\t9',
        '#define CAMSS_X1E_FRONT_POST_START_COMPLETION_GROUPS\t5',
        '#define CAMSS_X1E_FRONT_POST_START_INITIAL_PRIME_BUNDLES\t2',
        '#define CAMSS_X1E_FRONT_POST_START_NO_REWRITE_REGS\t6',
        '#define CAMSS_X1E_FRONT_POST_START_LIVE_MUTABLE_REGS\t4',
        'camss_x1e_front_post_start_contract __used = {',
        '.address_bundle_clients = CAMSS_X1E_FRONT_POST_START_BUNDLE_CLIENTS,',
        '.observed_initial_prime_bundles = CAMSS_X1E_FRONT_POST_START_INITIAL_PRIME_BUNDLES,',
        '.completion_group_count = CAMSS_X1E_FRONT_POST_START_COMPLETION_GROUPS,',
        '0x008c, 0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84,',
        '0x3d78, 0x3d7c, 0x3d80, 0x3d84,',
        '.second_bundle_before_first_completion = true,',
        '.refill_after_first_completion_cycle = true,',
        '.completion_cross_group_order_required = false,',
        '.slot_reuse_requires_all_groups = true,',
        '.bus_iova_update_software_owned = true,',
        '.rtcdm_batch_consume_software_owned = true,',
        '.completion_retirement_software_owned = true,',
        '.live_register_rewrite_authorized = false,',
        '.hardware_execution_authorized = false,',
    ]
    for x in required:
        need(src, x, 'source contract drift')

    order_block = src[src.find('.stage_order = {'):src.find('\n\t},\n\t.address_bundle_clients', src.find('.stage_order = {'))]
    positions = [order_block.find(x) for x in EXPECTED_STAGES]
    if any(x < 0 for x in positions) or positions != sorted(positions):
        die('post-start stage order drift')

    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c') != 1 or patch.count('--- a/') != 1:
        die('0023 path set drift')

    added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
    # 0023 is data-only. It must not add any callable helper or hardware primitive.
    if re.search(r'(?m)^\s*static\s+(?:int|void|bool|u32|irqreturn_t)\s+\w+\s*\(', added):
        die('0023 adds executable helper')
    forbidden = [
        'writel(', 'writel_relaxed(', 'readl(', 'enable_irq(', 'disable_irq(',
        'dma_alloc_', 'dma_free_', 'mutex_lock(', 'v4l2_subdev_call(',
        'camss_rtcdm1_windows_', 'camss_rtcdm1_corpus_materialize(',
        'vfe680_x1e_bus_', 'vfe_enable_v2(', 'csid_configure_stream(',
    ]
    for x in forbidden:
        if x in added:
            die('0023 adds runtime/hardware primitive: ' + x)

    if src.count('camss_x1e_front_post_start_contract __used') != 1:
        die('post-start contract definition count drift')

    rel = run('aarch64-linux-gnu-objdump', '-r', str(a.object))
    if 'camss_x1e_front_post_start_contract' in rel:
        die('compiled relocation references post-start contract')

    nm_obj = run('aarch64-linux-gnu-nm', '-an', str(a.object))
    nm_mod = run('aarch64-linux-gnu-nm', '-an', str(a.module))
    for nm, label in ((nm_obj, 'object'), (nm_mod, 'module')):
        lines = [ln for ln in nm.splitlines() if ln.endswith(' camss_x1e_front_post_start_contract')]
        if len(lines) != 1 or ' r ' not in (' ' + lines[0] + ' '):
            die(label + ' retained read-only post-start symbol drift: ' + repr(lines))
    # There must be no executable symbol sharing the post-start prefix.
    for ln in nm_obj.splitlines():
        if 'camss_x1e_front_post_start_' in ln and ' r ' not in (' ' + ln + ' '):
            die('unexpected executable/non-read-only post-start symbol: ' + ln)

    # Existing hard runtime gate remains earlier than stream lock/IRQ/output setup.
    m = re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}', vfe, re.S)
    if not m:
        die('vfe_enable_v2 missing')
    body = m.group(1)
    gate = body.find('return -EOPNOTSUPP;')
    lock = body.find('mutex_lock(&vfe->stream_lock)')
    if gate < 0 or lock < 0 or gate >= lock:
        die('VFE1 PIX runtime gate weakened')

    out = {
        'schema': 'sp11-e003h-linux-front-post-start-ownership-static-inspection-v1',
        'accepted': True,
        'source_sha256': sha(a.camss_source),
        'object_sha256': sha(a.object),
        'module_sha256': sha(a.module),
        'patch_sha256': sha(a.patch),
        'post_start_oracle_sha256': EXPECTED_ORACLE_SHA,
        'upstream_inspections': {
            'front_start_0022': EXPECTED_START_INSPECTION_SHA,
            'pix_ownership_0018': EXPECTED_PIX_OWNERSHIP_SHA,
            'bus_0017': EXPECTED_BUS_INSPECTION_SHA,
            'rtcdm_0015': EXPECTED_RTCDM_INSPECTION_SHA,
        },
        'observed_initial_prime_bundles': 2,
        'address_bundle_clients': 9,
        'completion_groups': 5,
        'stage_order': ['EPOCH0', 'VFE1_BUS_UPDATE', 'RTCDM_BATCH_CONSUME', 'COMPLETION_RETIRE'],
        'cross_group_completion_order_required': False,
        'slot_reuse_requires_all_groups': True,
        'software_owned_post_start': ['BUS_IOVA_UPDATE', 'RTCDM_BATCH_CONSUME', 'COMPLETION_RETIREMENT'],
        'no_post_start_rewrite_regs': ['0x008c', '0x3b70', '0x3d78', '0x3d7c', '0x3d80', '0x3d84'],
        'hardware_live_mutable_observation_only': ['0x3d78', '0x3d7c', '0x3d80', '0x3d84'],
        'data_only_contract': True,
        'runtime_isolation': {
            'callable_helper_added': False,
            'compiled_relocation_to_contract': False,
            'hardware_primitive_added': False,
            'pix_stream_gate': '-EOPNOTSUPP before stream lock/IRQ/output',
            'hardware_execution_authorized': False,
        },
        'policy': 'post-start ownership/scheduling data only; no module load, RT-CDM IRQ arm/FIFO0 submission, VFE1 BUS write, CSID1/PIX/MIPI start, IMX681 transmission or frame authorized',
    }
    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: post-start contract is two-prime-bundle, Epoch0-scheduled, independent-completion, data-only and runtime-unreachable')


if __name__ == '__main__':
    main()
