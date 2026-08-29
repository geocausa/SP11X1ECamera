#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ORACLE_SHA = '3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4'
POST_START_SHA = 'd426c7cf4525f36c80623cab628061005c880abd5df02d17d8a76683fea4e66e'
EXPECTED = [
    (0x958, 8, 56, 472, 14, 24),
    (0x868, 42, 45, 436, 12, 20),
    (0x83c, 46, 43, 429, 12, 14),
    (0x6b8, 24, 35, 352, 8, 10),
    (0x5a4, 55, 22, 315, 2, 6),
]


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def need(s, x, label):
    if x not in s:
        die(f'{label}: {x}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--vfe-source', type=Path, required=True)
    ap.add_argument('--object', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('--oracle', type=Path, required=True)
    ap.add_argument('--post-start-oracle', type=Path, required=True)
    ap.add_argument('--build-log', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    if sha(a.oracle) != ORACLE_SHA:
        die('Epoch0 batch oracle identity drift')
    if sha(a.post_start_oracle) != POST_START_SHA:
        die('0023 oracle identity drift')
    oracle = json.loads(a.oracle.read_text())
    if not oracle.get('accepted'):
        die('Epoch0 batch oracle not accepted')
    if oracle['capture']['total_batches'] != 179 or oracle['capture']['steady_state_batches'] != 175:
        die('batch census drift')
    got = [(v['main_bytes'], v['sample_count'], v['command_count'], v['register_write_count'],
            v['dmi_count'], len(v['dynamic_register_fields'])) for v in oracle['main_bl_variants']]
    if got != EXPECTED:
        die(f'variant census drift: {got!r}')
    if oracle['supersedes_0023_wording']['registers'] != ['0x8c', '0x3b70', '0x3d78', '0x3d7c', '0x3d80', '0x3d84']:
        die('0023 correction set drift')

    src = a.source.read_text()
    patch = a.patch.read_text()
    required = [
        '#define CAMSS_X1E_FRONT_POST_START_CDM_PROGRAMMED_REGS\t6',
        'u16 cdm_programmed_regs[CAMSS_X1E_FRONT_POST_START_CDM_PROGRAMMED_REGS];',
        '.cdm_programmed_regs = {',
        '0x008c, 0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84,',
        '.direct_mmio_rewrite_authorized = false,',
        '#define CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT\t5',
        '#define CAMSS_X1E_EPOCH0_CDM_VARIANT_COUNT\t5',
        '#define CAMSS_X1E_EPOCH0_CDM_STEADY_BATCHES\t175',
        '.bl_bytes = { 0x0004, 0x0000, 0x0004, 0x0010, 0x0014 },',
        '.vfe1_change_base = 0x0000f000,',
        '.companion_change_base = 0x00057000,',
        '{ .main_bytes = 0x0958, .command_count = 56,',
        '.register_write_count = 472, .dmi_count = 14,',
        '.dynamic_register_count = 24, .observed_samples = 8 },',
        '{ .main_bytes = 0x0868, .command_count = 45,',
        '.register_write_count = 436, .dmi_count = 12,',
        '.dynamic_register_count = 20, .observed_samples = 42 },',
        '{ .main_bytes = 0x083c, .command_count = 43,',
        '.register_write_count = 429, .dmi_count = 12,',
        '.dynamic_register_count = 14, .observed_samples = 46 },',
        '{ .main_bytes = 0x06b8, .command_count = 35,',
        '.register_write_count = 352, .dmi_count = 8,',
        '.dynamic_register_count = 10, .observed_samples = 24 },',
        '{ .main_bytes = 0x05a4, .command_count = 22,',
        '.register_write_count = 315, .dmi_count = 2,',
        '.dynamic_register_count = 6, .observed_samples = 55 },',
        '.encoded_length_is_byte_count_minus_one = true,',
        '.main_dmi_addresses_per_batch = true,',
        '.main_register_values_per_frame = true,',
        '.genirq_userdata_tracks_batch_tag = true,',
        '.dmi_payload_bytes_closed = false,',
        '.fifo0_submission_authorized = false,',
        'camss_x1e_epoch0_cdm_batch_contract __used = {',
    ]
    for x in required:
        need(src, x, 'source contract drift')
    for forbidden in ('no_post_start_rewrite_regs', 'live_register_rewrite_authorized'):
        if forbidden in src:
            die('superseded 0023 wording remains in source: ' + forbidden)

    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c') != 1 or patch.count('--- a/') != 1:
        die('0024 path set drift')
    for forbidden in ('+static int ', '+static void ', '+int camss_', '+void camss_',
                      '+\twritel(', '+\treadl(', '+\tenable_irq(', 'fifo0_commit('):
        if forbidden in patch:
            die('0024 introduces executable/hardware behavior: ' + forbidden)

    # Existing VFE1 PIX fail-close must remain before stream lock/IRQ/output setup.
    vfe = a.vfe_source.read_text()
    m = re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}', vfe, re.S)
    if not m:
        die('vfe_enable_v2 missing')
    b = m.group(1)
    gate = b.find('return -EOPNOTSUPP;')
    lock = b.find('mutex_lock(&vfe->stream_lock)')
    if gate < 0 or lock < 0 or gate >= lock:
        die('VFE1 PIX fail-close drift')

    rel = run('aarch64-linux-gnu-objdump', '-r', str(a.object))
    if 'camss_x1e_epoch0_cdm_batch_contract' in rel:
        die('runtime/data relocation references 0024 contract')
    nm_obj = run('aarch64-linux-gnu-nm', '-an', str(a.object))
    nm_mod = run('aarch64-linux-gnu-nm', '-an', str(a.module))
    for sym in ('camss_x1e_epoch0_cdm_batch_contract', 'camss_x1e_front_post_start_contract'):
        if sym not in nm_obj or sym not in nm_mod:
            die('retained contract symbol missing: ' + sym)

    build = a.build_log.read_text()
    diag = [line for line in build.splitlines() if re.search(r'(^|:)\s*(warning|error):', line, re.I)]
    if diag:
        die('compiler diagnostics present: ' + repr(diag[:4]))
    vermagic = run('modinfo', '-F', 'vermagic', str(a.module)).strip()
    if not vermagic.startswith('7.1.5-sp11-render-parity-v4+'):
        die('Golden vermagic drift')

    out = {
        'schema': 'sp11-e003h-linux-vfe1-epoch0-cdm-batch-contract-inspection-v1',
        'accepted': True,
        'oracle_sha256': ORACLE_SHA,
        'post_start_0023_oracle_sha256': POST_START_SHA,
        'source_sha256': sha(a.source),
        'object_sha256': sha(a.object),
        'module_sha256': sha(a.module),
        'patch_sha256': sha(a.patch),
        'build_log_sha256': sha(a.build_log),
        'vermagic': vermagic,
        'steady_state': {
            'batches': 175,
            'bls_per_batch': 5,
            'variant_summaries': [
                {'main_bytes': x[0], 'samples': x[1], 'commands': x[2], 'register_writes': x[3],
                 'dmi_commands': x[4], 'dynamic_register_fields': x[5]} for x in EXPECTED
            ],
            'encoded_length': 'byte_count_minus_one',
            'genirq_userdata': 'observed batch tag',
        },
        'ownership_correction': {
            'cdm_programmed_registers': ['0x008c', '0x3b70', '0x3d78', '0x3d7c', '0x3d80', '0x3d84'],
            'direct_mmio_rewrite_authorized': False,
            'dmi_payload_bytes_closed': False,
        },
        'runtime_isolation': {
            'contract_relocation_present': False,
            'contract_symbols_retained': True,
            'pix_stream_gate': '-EOPNOTSUPP before stream lock/IRQ/output',
            'fifo0_submission_added': False,
        },
        'policy': 'static-only data contract; no module load, RT-CDM FIFO0 submission, CSID1/VFE1 PIX/MIPI start, IMX681 transmission or frame authorized',
    }
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print('PASS: 0024 encodes the five steady Windows Epoch0 CDM batch shapes, corrects 0023 ownership wording, and remains data-only/unreachable')


if __name__ == '__main__':
    main()
