#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

EXPECTED_ORACLE_SHA = '01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda'
EXPECTED_PATCH_SHA = '0f21697369369be11d0692268f71ea2af3768346c9a63e5eb2d03f67c57e3414'
EXPECTED_MODULE_SHA = 'c67ce602f88be5db2ffecd816879081d74f996f7884e8661bea252d924f7098e'
EXPECTED_VERMAGIC = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(text, needle, label):
    count = text.count(needle)
    if count != 1:
        die(f'{label}: expected exactly one occurrence, got {count}')
    return text.index(needle)


def ordered(text, needles, label):
    positions = [one(text, n, f'{label}/{n[:48]}') for n in needles]
    if positions != sorted(positions):
        die(label + ': source ordering drift')
    return positions


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path,
                    default=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src'))
    ap.add_argument('--oracle', type=Path, default=here / 'windows-csid1-ipp-start-oracle.json')
    ap.add_argument('--patch', type=Path, default=here / '0042-x1e-csid1-ipp-start-windows-parity.patch')
    ap.add_argument('--module', type=Path,
                    default=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko'))
    ap.add_argument('--checkpatch-log', type=Path,
                    default=here / 'CAMSS-CSID1-IPP-START-PARITY-CHECKPATCH.log')
    ap.add_argument('--build-log', type=Path,
                    default=here / 'CAMSS-CSID1-IPP-START-PARITY-BUILD.log')
    ap.add_argument('-o', '--output', type=Path, default=here / 'csid1-ipp-start-linux-inspection.json')
    a = ap.parse_args()

    if sha(a.oracle) != EXPECTED_ORACLE_SHA:
        die('Windows CSID1 start oracle hash drift')
    oracle = json.loads(a.oracle.read_text())
    if not oracle.get('accepted') or oracle.get('schema') != 'sp11-e003h-windows-csid1-ipp-start-v1':
        die('Windows CSID1 start oracle not accepted')
    if oracle.get('runtime_authorized') is not False:
        die('oracle must not authorize runtime')

    if sha(a.patch) != EXPECTED_PATCH_SHA:
        die('0042 patch hash drift')
    patch = a.patch.read_text()
    added = [line[1:] for line in patch.splitlines()
             if line.startswith('+') and not line.startswith('+++')]
    if any('writel' in line and 'CSID_REG_UPDATE_CMD' in line for line in added):
        die('0042 synthesizes an unproven CSID REG_UPDATE_CMD write')

    csid_path = a.source / 'drivers/media/platform/qcom/camss/camss-csid-680.c'
    hdr_path = a.source / 'drivers/media/platform/qcom/camss/camss-csid.h'
    camss_path = a.source / 'drivers/media/platform/qcom/camss/camss.c'
    csid = csid_path.read_text()
    hdr = hdr_path.read_text()
    camss = camss_path.read_text()

    expected_defines = {
        '#define CSID_IPP_SP11_PARITY_ZERO0\t\t\t\t0x324': 0x324,
        '#define CSID_IPP_SP11_PARITY_ZERO1\t\t\t\t0x330': 0x330,
        '#define SP11_CSID_TOP_IRQ_MASK_MODE0\t\t\t\t0x00000001': 0x1,
        '#define SP11_CSID_BUF_DONE_IRQ_MASK_MODE0\t\t\t0x0001ffff': 0x1ffff,
        '#define SP11_CSID_RX_IRQ_MASK_MODE0\t\t\t\t0x019fb800': 0x019fb800,
        '#define SP11_CSID_IPP_IRQ_MASK_MODE0\t\t\t\t0x3cbc601c': 0x3cbc601c,
    }
    for line in expected_defines:
        one(csid, line, 'define')

    ordered(csid, [
        'writel(SP11_CSID_RX_IRQ_MASK_MODE0, csid->base + CSID_CSI2_RX_IRQ_MASK);',
        'writel(SP11_CSID_BUF_DONE_IRQ_MASK_MODE0,\n\t       csid->base + CSID_BUF_DONE_IRQ_MASK);',
        'writel(val, csid->base + CSID_IPP_CFG0);\n\twritel(SP11_IPP_CFG1_MODE0',
        'writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO0);',
        'writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO1);',
        'writel(SP11_IPP_EPOCH_IRQ_MODE0, csid->base + CSID_IPP_EPOCH_IRQ_CFG);',
    ], 'initial CSID1 config order')

    ordered(csid, [
        '__csid_ctrl_ipp(csid, enable);',
        'writel(SP11_CSID_IPP_IRQ_MASK_MODE0,\n\t\t\t       csid->base + CSID_IPP_IRQ_MASK);',
        'writel(SP11_CSID_TOP_IRQ_MASK_MODE0,\n\t\t\t       csid->base + CSID_TOP_IRQ_MASK);',
    ], 'CSID 0x804-equivalent path-enable order')

    if 'if (enable && __csid_sp11_front_ipp_mode0(csid)) {' not in csid:
        die('start mask writes lost front-mode0 gate')
    one(hdr,
        'void csid680_x1e_front_runtime_dump(struct csid_device *csid, const char *reason);',
        'telemetry prototype')
    one(csid, 'void csid680_x1e_front_runtime_dump(', 'telemetry implementation')

    epoch = '''\tret = vfe680_x1e_pix_runtime_poll_epoch0(vfe,\n\t\t\t\t\t\t CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);\n\tif (ret) {\n\t\tcsid680_x1e_front_runtime_dump(csid, "epoch0-timeout");\n\t\tgoto out_unwind;\n\t}\n'''
    one(camss, epoch, 'timeout-only telemetry hook')
    if camss.count('csid680_x1e_front_runtime_dump(') != 1:
        die('telemetry hook must remain timeout-only')

    if sha(a.module) != EXPECTED_MODULE_SHA:
        die('built qcom-camss.ko hash drift')
    modinfo = subprocess.check_output(['modinfo', str(a.module)], text=True)
    vermagic = next((line.split(':', 1)[1].strip() for line in modinfo.splitlines()
                     if line.startswith('vermagic:')), None)
    if vermagic != EXPECTED_VERMAGIC:
        die('module vermagic drift: ' + repr(vermagic))

    check = a.checkpatch_log.read_text()
    if 'total: 0 errors, 0 warnings' not in check or 'CHECKPATCH_RC=0' not in check:
        die('checkpatch log is not clean')
    build = a.build_log.read_text()
    if 'BUILD_RC=0' not in build or EXPECTED_MODULE_SHA not in build or EXPECTED_VERMAGIC not in build:
        die('build log identity drift')

    # Prove the canonical patch exactly describes the current source delta:
    # reverse it in a throwaway tree, check forward application, re-apply it,
    # and require byte-identical recovery of all touched source files.
    touched = [csid_path, hdr_path, camss_path]
    with tempfile.TemporaryDirectory(prefix='e003h-0042-roundtrip-') as td:
        tmp = Path(td)
        for src_path in touched:
            rel = src_path.relative_to(a.source)
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
        subprocess.check_call(['git', '-C', str(tmp), 'init', '-q'])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--check', '--reverse', str(a.patch)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--reverse', str(a.patch)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--check', str(a.patch)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', str(a.patch)])
        for src_path in touched:
            rel = src_path.relative_to(a.source)
            if sha(tmp / rel) != sha(src_path):
                die(f'0042 patch round-trip mismatch: {rel}')

    out = {
        'status': 'PASS',
        'schema': 'sp11-e003h-linux-csid1-ipp-start-inspection-v1',
        'windows_oracle': {'sha256': sha(a.oracle), 'accepted': True},
        'patch': {
            'sha256': sha(a.patch),
            'checkpatch': '0 errors, 0 warnings',
            'reverse_forward_roundtrip_byte_identical': True,
        },
        'source': {
            'camss_csid_680_sha256': sha(csid_path),
            'camss_csid_h_sha256': sha(hdr_path),
            'camss_c_sha256': sha(camss_path),
        },
        'proved_linux_delta': {
            'front_mode0_only': True,
            'initial_masks': {
                'buf_done': '0x0001ffff',
                'rx': '0x019fb800',
            },
            'proven_zero_writes': ['CSID1 +0x324 = 0', 'CSID1 +0x330 = 0'],
            'start_order': ['IPP_CTRL=1', 'IPP_IRQ_MASK=0x3cbc601c', 'TOP_IRQ_MASK=0x00000001'],
            'synthetic_reg_update_cmd_added': False,
            'epoch0_timeout_snapshot_before_teardown': True,
        },
        'module': {'sha256': sha(a.module), 'vermagic': vermagic},
        'runtime_authorized': False,
        'next_gate': 'Update durable state and inspect the exact candidate package before any one-shot runtime authorization.',
    }
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
