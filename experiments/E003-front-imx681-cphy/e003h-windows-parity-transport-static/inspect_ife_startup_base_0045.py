#!/usr/bin/env python3
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
HERE = REPO / 'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
KSRC = Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
CAMSS = KSRC / 'drivers/media/platform/qcom/camss/camss.c'
CSID = KSRC / 'drivers/media/platform/qcom/camss/camss-csid-680.c'
CSID_H = KSRC / 'drivers/media/platform/qcom/camss/camss-csid.h'
MODULE = KSRC / 'drivers/media/platform/qcom/camss/qcom-camss.ko'
PATCH = HERE / '0045-x1e-ife-startup-change-base-wrapper.patch'
ORACLE = HERE / 'windows-ife-startup-base-wrapper-oracle.json'
BUILD = HERE / 'CAMSS-IFE-STARTUP-BASE-0045-BUILD.log'
CHECKPATCH = HERE / 'CAMSS-IFE-STARTUP-BASE-0045-CHECKPATCH.log'

EXPECTED = {
    'pre_source': '5eccf7c32a754ef97d19bafecb6a98cada393af57526d02835c9ff2176f90695',
    'source': '2b7930869bfe2a263a4242393536188f3f97249d3d76806bf19b4f955da291b0',
    'patch': '9fd8ddd43013441a2bedc2a603f9373a42559da17cc113ab8bbe959f38d7be4e',
    'oracle': '93b793d4bb13bc9d0abc09b667502466681f1a3e81d39bc837700d50ada96d03',
    'module': 'cfdd66c9d2c56533993f5f73831d77b3f5018c1d552183da634971378aa06923',
    'csid': '59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0',
    'csid_h': 'e581e9a43a74a577aa535a7e33af4f5cd7e8c7af455d3c3fccd083dac2766f44',
    'prime_function': '1f705da1cd30b2ce2f4663fa2e6554d02e052fde0747af82333c23e57d78ad06',
}


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)


for p in (CAMSS, CSID, CSID_H, MODULE, PATCH, ORACLE, BUILD, CHECKPATCH):
    req(p.is_file(), f'missing {p}')
req(sha(CAMSS) == EXPECTED['source'], 'camss source hash drift')
req(sha(PATCH) == EXPECTED['patch'], '0045 patch hash drift')
req(sha(ORACLE) == EXPECTED['oracle'], 'startup wrapper oracle hash drift')
req(sha(MODULE) == EXPECTED['module'], 'qcom-camss.ko hash drift')
req(sha(CSID) == EXPECTED['csid'], 'CSID source changed in 0045')
req(sha(CSID_H) == EXPECTED['csid_h'], 'CSID header changed in 0045')
req('BUILD_RC=0' in BUILD.read_text(errors='replace'), 'build did not pass')
cp = CHECKPATCH.read_text(errors='replace')
req('0 errors, 0 warnings, 0 checks' in cp and 'ready for submission' in cp,
    'checkpatch did not pass cleanly')

src = CAMSS.read_text()
req('#define CAMSS_X1E_PIX_STARTUP_CHANGE_BASE\t0x0800f000' in src,
    'startup CHANGE_BASE word absent')
req('CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE' in src, 'startup wrapper arena absent')
req(src.count('put_unaligned_le32(CAMSS_X1E_PIX_STARTUP_CHANGE_BASE,') == 1,
    'startup wrapper word writer drift')
req('out->bl_len[packet] = sizeof(u32);' in src, 'startup wrapper length not four bytes')
req(src.count('&materialized->startup_wrapper') == 4,
    'runner does not pass wrapper for exactly four startup packets')

m = re.search(r'static int camss_x1e_pix_submit_startup\(.*?\n}\n\nstatic int camss_x1e_pix_submit_prime', src, re.S)
req(m is not None, 'startup submit function not found')
submit = m.group(0)
wrapper_commit = submit.find('wrapper->bl_dma[packet]')
main_commit = submit.find('corpus->packet_dma[packet]')
req(wrapper_commit >= 0 and main_commit > wrapper_commit,
    'startup submit order is not wrapper then main')
req('SP11_CSID_BUF_DONE_IRQ_MASK' not in submit and 'CSID_BUF_DONE_IRQ_MASK' not in submit,
    '0045 added a late CSID mask repair')

pm = re.search(r'static int camss_x1e_pix_prime_materialize\(.*?\n}\n\nstatic void camss_x1e_pix_capsule_materialized_release', src, re.S)
req(pm is not None, 'priming materializer not found')
prime_sha = hashlib.sha256(pm.group(0).encode()).hexdigest()
req(prime_sha == EXPECTED['prime_function'], 'priming materializer changed in 0045')

# Prove patch roundtrip from the exact current source without trusting source-tree git flags.
with tempfile.TemporaryDirectory(prefix='e003h0045-') as td:
    root = Path(td)
    dst = root / 'drivers/media/platform/qcom/camss/camss.c'
    dst.parent.mkdir(parents=True)
    shutil.copy2(CAMSS, dst)
    patch_bytes = PATCH.read_bytes()
    r = subprocess.run(['patch', '-R', '-p1'], cwd=root, input=patch_bytes,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    req(r.returncode == 0, 'reverse patch failed')
    req(sha(dst) == EXPECTED['pre_source'], 'reverse patch did not recover exact 0044 camss.c')
    r = subprocess.run(['patch', '-p1'], cwd=root, input=patch_bytes,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    req(r.returncode == 0, 'forward patch failed')
    req(sha(dst) == EXPECTED['source'], 'forward patch did not recover exact 0045 camss.c')

modinfo = subprocess.check_output(['modinfo', str(MODULE)], text=True)
vermagic = next(line.split(':', 1)[1].strip() for line in modinfo.splitlines()
                if line.startswith('vermagic:'))
req(vermagic == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64',
    'module vermagic drift')

oracle = json.loads(ORACLE.read_text())
req(oracle['accepted'] is True, 'Windows startup wrapper oracle not accepted')
req(oracle['wrapper_command']['byte_identity_to_captured_windows_bl0'] is True,
    'exact wrapper word lacks independent Windows byte identity')
req(oracle['linux_consequence']['runtime_authorized'] is False,
    'oracle unexpectedly authorizes runtime')

out = {
    'schema': 'sp11-e003h-linux-0045-startup-base-wrapper-inspection-v1',
    'accepted': True,
    'patch_sha256': sha(PATCH),
    'pre_0045_camss_source_sha256': EXPECTED['pre_source'],
    'camss_source_sha256': sha(CAMSS),
    'csid680_source_sha256': sha(CSID),
    'csid_header_sha256': sha(CSID_H),
    'module_sha256': sha(MODULE),
    'module_vermagic': vermagic,
    'prime_materializer_sha256': prime_sha,
    'startup_wrapper': {
        'word': '0x0800f000',
        'entries': 4,
        'bytes_per_entry': 4,
        'linux_owned_coherent_dma': True,
        'submit_order': 'wrapper -> unchanged startup main',
    },
    'unchanged': {
        'csid_implementation': True,
        'csid_header': True,
        'selector2_priming_materializer': True,
        'steady_epoch0_materializer': 'not modified by patch 0045',
        'captured_startup_main_bytes': 'not modified; wrapper is a separate BL',
    },
    'late_csid_mask_repair_added': False,
    'patch_roundtrip_byte_identical': True,
    'runtime_authorized': False,
}
path = HERE / 'linux-0045-startup-base-wrapper-inspection.json'
path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
print(json.dumps(out, indent=2, sort_keys=True))
print('INSPECTION_SHA256=' + sha(path))
