#!/usr/bin/env python3
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
EXPECTED = {
    'common_oracle': '43a265f0cd63fa9e01406e8b5ff0b62c756dc2bc2f8c3a24df74a4f832b76996',
    'start_oracle': '01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda',
    'patch': 'a96339ab84094cfa0d103d73e6c04294dce5f211738fcbbe2bd370b9c5bb3340',
    'build_log': '99ea98ba59b015b1111053654d8535b965723f88be827cb568ce2fa04fabbd8b',
    'checkpatch_log': 'e6e2a7f1ef5193106f623889a6f3c6b7cb88bd15ec031f537e419af79f7a6e07',
    'module': '98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc',
    'csid680': '59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0',
    'header': 'e581e9a43a74a577aa535a7e33af4f5cd7e8c7af455d3c3fccd083dac2766f44',
    'camss': '5eccf7c32a754ef97d19bafecb6a98cada393af57526d02835c9ff2176f90695',
}
VERMAGIC = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def exact_hash(path, key):
    got = sha(path)
    if got != EXPECTED[key]:
        die(f'{key} hash drift: {got}')
    return got


def one(text, needle, label):
    n = text.count(needle)
    if n != 1:
        die(f'{label}: expected one occurrence, got {n}')
    return text.index(needle)


def ordered(text, needles, label):
    pos = []
    cursor = 0
    for needle in needles:
        at = text.find(needle, cursor)
        if at < 0:
            die(f'{label}: missing {needle!r}')
        pos.append(at)
        cursor = at + len(needle)
    return pos


def func_slice(text, start, end):
    a = text.index(start)
    b = text.index(end, a + len(start))
    return text[a:b]


def main():
    common_path = HERE / 'windows-csid1-common-reset-oracle.json'
    start_path = HERE / 'windows-csid1-ipp-start-oracle.json'
    patch_path = HERE / '0044-x1e-csid1-common-lifecycle-windows-parity.patch'
    build_path = HERE / 'CAMSS-CSID1-COMMON-LIFECYCLE-0044-BUILD.log'
    check_path = HERE / 'CAMSS-CSID1-COMMON-LIFECYCLE-0044-CHECKPATCH.log'
    module_path = SRC / 'drivers/media/platform/qcom/camss/qcom-camss.ko'
    csid_path = SRC / 'drivers/media/platform/qcom/camss/camss-csid-680.c'
    hdr_path = SRC / 'drivers/media/platform/qcom/camss/camss-csid.h'
    camss_path = SRC / 'drivers/media/platform/qcom/camss/camss.c'
    pm_path = SRC / 'drivers/media/v4l2-core/v4l2-mc.c'

    exact_hash(common_path, 'common_oracle')
    exact_hash(start_path, 'start_oracle')
    exact_hash(patch_path, 'patch')
    exact_hash(build_path, 'build_log')
    exact_hash(check_path, 'checkpatch_log')
    exact_hash(module_path, 'module')
    exact_hash(csid_path, 'csid680')
    exact_hash(hdr_path, 'header')
    exact_hash(camss_path, 'camss')

    common = json.loads(common_path.read_text())
    start = json.loads(start_path.read_text())
    if common.get('schema') != 'sp11-e003h-windows-csid1-common-reset-v1' or not common.get('accepted'):
        die('common reset oracle not accepted')
    if common.get('runtime_authorized') is not False:
        die('common reset oracle unexpectedly authorizes runtime')
    if start.get('schema') != 'sp11-e003h-windows-csid1-ipp-start-v1' or not start.get('accepted'):
        die('CSID start oracle not accepted')
    if start.get('runtime_authorized') is not False:
        die('CSID start oracle unexpectedly authorizes runtime')

    csid = csid_path.read_text()
    hdr = hdr_path.read_text()
    camss = camss_path.read_text()
    pm = pm_path.read_text()
    patch = patch_path.read_text()

    # Front predicate remains same-machine/mode specific.
    pred = func_slice(csid, 'static bool __csid_sp11_front_ipp_mode0', 'static void __csid_ctrl_ipp')
    for needle in [
        'csid->camss->res->version == CAMSS_X1E80100', 'csid->id == 1',
        'csid->phy.csiphy_id == 2', 'csid->phy.phy_sel == CSID_PHY_SEL_CPHY',
        'csid->phy.lane_cnt == 1', 'MEDIA_BUS_FMT_SRGGB10_1X10',
        'fmt->width == 3840 && fmt->height == 2640',
    ]:
        if needle not in pred:
            die('front predicate drift: ' + needle)

    # Full builder is post-reset DEVICE_CONFIG state, not a late runner prepare.
    full = func_slice(csid, 'static int __csid_sp11_front_ipp_full_config', 'static void __csid_configure_top')
    ordered(full, [
        '__csid_configure_rx(csid, &csid->phy, 0);',
        'writel(SP11_CSID_RX_IRQ_MASK_MODE0, csid->base + CSID_CSI2_RX_IRQ_MASK);',
        'writel(SP11_CSID_BUF_DONE_IRQ_MASK_MODE0,',
        'writel(0, csid->base + CSID_IPP_FRM_DROP_PATTERN);',
        'writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_FRM_DROP_PERIOD);',
        'writel(SP11_IPP_IRQ_SUBSAMPLE_PATTERN_MODE0,',
        'writel(0, csid->base + CSID_IPP_IRQ_SUBSAMPLE_PERIOD);',
        'writel(0, csid->base + CSID_IPP_PIX_DROP_PATTERN);',
        'writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_PIX_DROP_PERIOD);',
        'writel(0, csid->base + CSID_IPP_LINE_DROP_PATTERN);',
        'writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_LINE_DROP_PERIOD);',
        'writel(SP11_IPP_EPOCH_IRQ_MODE0, csid->base + CSID_IPP_EPOCH_IRQ_CFG);',
        'writel(SP11_IPP_EPOCH_SUBSAMPLE_MODE0,',
        'csid->base + CSID_IPP_EPOCH0_SUBSAMPLE_PATTERN);',
        'writel(SP11_IPP_EPOCH_SUBSAMPLE_MODE0,',
        'csid->base + CSID_IPP_EPOCH1_SUBSAMPLE_PATTERN);',
        'writel(SP11_IPP_HCROP_MODE0, csid->base + CSID_IPP_HCROP);',
        'writel(SP11_IPP_VCROP_MODE0, csid->base + CSID_IPP_VCROP);',
        'val = format->decode_format << IPP_CFG0_DECODE_FORMAT;',
        'val |= format->data_type << IPP_CFG0_DATA_TYPE;',
        'val |= IPP_CFG0_ENABLE;',
        'writel(val, csid->base + CSID_IPP_CFG0);',
        'writel(SP11_IPP_CFG1_MODE0, csid->base + CSID_IPP_CFG1);',
        'writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO0);',
        'writel(SP11_CSID_IPP_IRQ_MASK_PREP_MODE0,',
    ], 'full builder order')
    for forbidden in ['CSID_IPP_SP11_PARITY_ZERO1', 'CSID_IPP_FORMAT_MEASURE_CFG0',
                      'CSID_IPP_FORMAT_MEASURE_CFG1', 'BIN_PD', '0x328', '0x32c']:
        if forbidden in full:
            die('full builder contains non-owner write/identifier: ' + forbidden)

    # RX helper establishes builder's first two direct register writes.
    rx = func_slice(csid, 'static void __csid_configure_rx', 'static void __csid_ctrl_rdi')
    ordered(rx, ['writel(val, csid->base + CSID_CSI2_RX_CFG0);',
                 'writel(val, csid->base + CSID_CSI2_RX_CFG1);'], 'RX config order')

    # Windows common reset: route -> TOP=1 -> RESET_CFG=0x11 -> SW reset -> 50 ms -> builder.
    reset = func_slice(csid, 'static int csid_reset(struct csid_device *csid)',
                       'int csid680_x1e_front_ipp_stop')
    front_return = ordered(reset, [
        'if (front_mode0) {', '__csid_configure_top(csid);',
        'writel(SP11_CSID_TOP_IRQ_MASK_MODE0,',
        'val = CSID_RESET_CFG_MODE_IMMEDIATE |',
        'CSID_RESET_CFG_LOCATION_COMPLETE;',
        'writel(val, csid->base + CSID_RESET_CFG);',
        'writel(CSID_RESET_CMD_SW_RESET, csid->base + CSID_RESET_CMD);',
        'msecs_to_jiffies(SP11_CSID_RESET_TIMEOUT_MS)',
        'return __csid_sp11_front_ipp_full_config(csid);',
        'writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);',
        'val = CSID_RESET_CMD_HW_RESET | CSID_RESET_CMD_SW_RESET;',
        'writel(~0u, csid->base + CSID_BUF_DONE_IRQ_MASK);',
        'writel(~0u, csid->base + CSID_TOP_IRQ_MASK);',
    ], 'front reset before generic fallback')
    if '#define SP11_CSID_RESET_TIMEOUT_MS\t\t\t\t50' not in csid:
        die('front reset timeout is not exact 50 ms')
    # Ensure there is no front-path IRQ_CMD write before the front return.
    if 'CSID_IRQ_CMD' in reset[:front_return[8]]:
        die('front reset contains pre-reset IRQ_CMD write')

    # Captured CSID companion packets: packet0 extras, every packet crop.
    companion = func_slice(csid, 'int csid680_x1e_front_ipp_companion',
                            'int csid680_x1e_front_ipp_enable')
    if companion.count('if (!packet) {') != 2:
        die('companion packet0 conditional count drift')
    ordered(companion, [
        'if (!packet) {',
        'writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO1);',
        'writel(SP11_IPP_IRQ_SUBSAMPLE_PATTERN_MODE0,',
        'writel(0, csid->base + CSID_IPP_IRQ_SUBSAMPLE_PERIOD);',
        'writel(SP11_IPP_HCROP_MODE0, csid->base + CSID_IPP_HCROP);',
        'writel(SP11_IPP_VCROP_MODE0, csid->base + CSID_IPP_VCROP);',
        'if (!packet) {',
        'writel(SP11_IPP_FORMAT_MEASURE_CFG0_MODE0,',
        'writel(SP11_IPP_FORMAT_MEASURE_CFG1_MODE0,',
    ], 'companion ownership/order')

    # 0x804 path-enable stays CTRL -> final IPP mask -> TOP mask.
    enable = func_slice(csid, 'int csid680_x1e_front_ipp_enable', 'static void csid_configure_stream')
    ordered(enable, ['__csid_ctrl_ipp(csid, true);',
                     'writel(SP11_CSID_IPP_IRQ_MASK_MODE0,',
                     'writel(SP11_CSID_TOP_IRQ_MASK_MODE0,'], 'IPP enable order')

    # Private 0x805 stop uses exact HW-reset-only callback and no V4L2 stream bookkeeping.
    stop = func_slice(csid, 'int csid680_x1e_front_ipp_stop', 'static void csid_rup_complete')
    ordered(stop, ['writel(SP11_CSID_TOP_IRQ_MASK_MODE0,',
                   'val = CSID_RESET_CFG_MODE_IMMEDIATE | CSID_RESET_CFG_LOCATION_COMPLETE;',
                   'writel(val, csid->base + CSID_RESET_CFG);',
                   'writel(CSID_RESET_CMD_HW_RESET, csid->base + CSID_RESET_CMD);',
                   'msecs_to_jiffies(SP11_CSID_RESET_TIMEOUT_MS)'], 'private stop order')
    if 'CSID_RESET_CMD_SW_RESET' in stop or 'CSID_IRQ_CMD' in stop:
        die('private stop contains unproven reset/IRQ command')

    # ISR acknowledgement remains present after status clears.
    isr = func_slice(csid, 'static irqreturn_t csid_isr', 'static void csid_subdev_reg_update')
    if isr.count('writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);') != 1:
        die('ISR IRQ_CMD acknowledgement drift')
    ordered(isr, ['writel(val_top, csid->base + CSID_TOP_IRQ_CLEAR);',
                  'writel(val, csid->base + CSID_CSI2_RX_IRQ_CLEAR);',
                  'writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);',
                  'writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);'], 'ISR clear/ack order')

    # No late prepare API remains; runner interleaves IFE packet then its CSID companion.
    if 'csid680_x1e_front_ipp_prepare' in csid + hdr + camss:
        die('late 0043 prepare API still present')
    if 'camss_x1e_pix_runner_stream(&csid->subdev' in camss:
        die('runner still uses public CSID s_stream bookkeeping')
    runner = func_slice(camss, 'static int camss_x1e_pix_runner_once',
                        'static ssize_t e003h_pix_run_once_store')
    ordered(runner, [
        'ret = v4l2_pipeline_pm_get(video_entity);', 'pipeline_powered = true;',
        'csid_configured = true;',
        'camss_x1e_pix_submit_startup(camss, &materialized->startup, 0);',
        'csid680_x1e_front_ipp_companion(csid, 0);',
        'camss_x1e_pix_submit_prime(camss, &materialized->prime, 0);',
        'camss_x1e_pix_submit_startup(camss, &materialized->startup, 1);',
        'csid680_x1e_front_ipp_companion(csid, 1);',
        'vfe680_x1e_pix_runtime_bus_prepare(vfe, pix);',
        'camss_x1e_pix_submit_prime(camss, &materialized->prime, 1);',
        'camss_x1e_pix_submit_startup(camss, &materialized->startup, 2);',
        'csid680_x1e_front_ipp_companion(csid, 2);',
        'camss_x1e_pix_submit_startup(camss, &materialized->startup, 3);',
        'csid680_x1e_front_ipp_companion(csid, 3);',
        'csid680_x1e_front_ipp_enable(csid);',
        'camss_x1e_pix_runner_stream(&csiphy->subdev, true);',
        'camss_x1e_pix_runner_stream(req->sensor, true);',
    ], 'runner Windows order')
    if runner.count('csid680_x1e_front_ipp_stop(csid);') != 2:
        die('normal/failure private CSID stop coverage drift')

    # A successful pipeline PM get means all enabled subdevices powered successfully;
    # the helper unwinds prior entities on any s_power failure.
    for needle in ['ret = v4l2_subdev_call(subdev, core, s_power, 1);',
                   'ret = pipeline_pm_power_one(entity, change);',
                   'pipeline_pm_power_one(first, -change);']:
        if needle not in pm:
            die('pipeline PM ownership proof drift: ' + needle)

    # Old unowned final-state replay has been removed from implementation.
    for forbidden in ['CSID_IPP_BIN_PD_DETECT_CFG1', 'CSID_IPP_BIN_PD_DETECT_CFG2',
                      'SP11_IPP_BIN_PD_DETECT_MODE0']:
        if forbidden in csid:
            die('unowned +0x328/+0x32c replay still present: ' + forbidden)

    # Build/checkpatch identities and module ABI.
    build = build_path.read_text()
    check = check_path.read_text()
    if 'BUILD_RC=0' not in build or EXPECTED['module'] not in build or VERMAGIC not in build:
        die('build log does not pin final module/vermagic')
    if 'total: 0 errors, 0 warnings, 0 checks' not in check or 'CHECKPATCH_RC=0' not in check:
        die('strict checkpatch gate not clean')
    modinfo = subprocess.check_output(['modinfo', str(module_path)], text=True)
    vermagic = next((x.split(':', 1)[1].strip() for x in modinfo.splitlines()
                     if x.startswith('vermagic:')), None)
    if vermagic != VERMAGIC:
        die('module vermagic drift: ' + repr(vermagic))

    # Patch must reverse and re-apply to byte-identical current source.
    touched = [csid_path, hdr_path, camss_path]
    with tempfile.TemporaryDirectory(prefix='e003h-0044-roundtrip-') as td:
        tmp = Path(td)
        for src_path in touched:
            rel = src_path.relative_to(SRC)
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
        subprocess.check_call(['git', '-C', str(tmp), 'init', '-q'])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--check', '--reverse', str(patch_path)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--reverse', str(patch_path)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', '--check', str(patch_path)])
        subprocess.check_call(['git', '-C', str(tmp), 'apply', str(patch_path)])
        for src_path in touched:
            rel = src_path.relative_to(SRC)
            if sha(tmp / rel) != sha(src_path):
                die('patch roundtrip mismatch: ' + str(rel))

    out = {
        'status': 'PASS',
        'schema': 'sp11-e003h-linux-csid1-common-lifecycle-0044-inspection-v1',
        'windows_oracles': {
            'common_reset_sha256': EXPECTED['common_oracle'],
            'ipp_start_sha256': EXPECTED['start_oracle'],
            'accepted': True,
        },
        'patch': {
            'sha256': EXPECTED['patch'],
            'strict_checkpatch': '0 errors, 0 warnings, 0 checks',
            'reverse_forward_roundtrip_byte_identical': True,
        },
        'source': {
            'camss_csid_680_sha256': EXPECTED['csid680'],
            'camss_csid_h_sha256': EXPECTED['header'],
            'camss_c_sha256': EXPECTED['camss'],
        },
        'module': {'sha256': EXPECTED['module'], 'vermagic': vermagic},
        'proved_delta': {
            'front_mode0_only': True,
            'device_config_order': 'wrapper 0x101 -> TOP mask 1 -> RESET_CFG 0x11 -> SW reset 2 -> wait 50 ms -> exact full builder',
            'front_pre_reset_irq_cmd_write': False,
            'front_generic_post_reset_mask_staging': False,
            'unowned_0x328_0x32c_replay_removed': True,
            'initial_packet_order': 'IFE packetN -> exact CSID companionN for N=0..3',
            'path_enable_order': 'IPP_CTRL=1 -> IPP mask 0x3cbc601c -> TOP mask 1',
            'private_stop_order': 'TOP mask 1 -> RESET_CFG 0x11 -> HW reset 1 -> wait 50 ms',
            'public_csid_s_stream_rollback_removed': True,
            'isr_irq_cmd_ack_retained': True,
            'pipeline_pm_success_pins_csid_configuration_success': True,
        },
        'runtime_authorized': False,
        'next_gate': 'Refresh provenance and durable state, then build/inspect a distinct one-shot package before any runtime authorization.',
    }
    out_path = HERE / 'csid1-common-lifecycle-linux-inspection.json'
    out_path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
