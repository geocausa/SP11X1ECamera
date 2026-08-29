#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

EXPECTED_CROSS_SHA = 'b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6'
EXPECTED_PERIOD_SHA = '169cf024d87e2f9a4ec620fb15be657767d8e01dd87da0b47ebe9c11375e37c3'
EXPECTED_RTCDM_SHA = '23f9f601f0e9b8880e447d17685585bbdc1e0058a8be60fcf330172e366aa346'
EXPECTED_BUS_SHA = '92715605c99523366dd619331c6abe9bb09c7e6476bf8921ccb5b18cbaae262e'
EXPECTED_OWN_SHA = 'bc8bf64152882e8c312e0e1379b544e2ae733dc75b4e571784fac3b88b4b7dcf'
EXPECTED_START = [
    'CDM_START', 'IFE_START', 'IFE803_PACKET0', 'IFE803_PACKET1',
    'VFE1_BUS_STATIC_CONFIG', 'VFE1_BUS_ENABLE',
    'VFE1_INITIAL_DYNAMIC_ADDRESSES', 'IFE803_PACKET2',
    'IFE803_PACKET3', 'CSID_START', 'ISP_START_DONE',
]
EXPECTED_SOURCE_STAGES = [
    'CAMSS_X1E_FRONT_START_RTCDM_OPEN_INIT',
    'CAMSS_X1E_FRONT_START_RTCDM_START',
    'CAMSS_X1E_FRONT_START_IFE_RESOURCE_START',
    'CAMSS_X1E_FRONT_START_IFE803_PACKET0',
    'CAMSS_X1E_FRONT_START_IFE803_PACKET1',
    'CAMSS_X1E_FRONT_START_VFE1_BUS_PREPARE',
    'CAMSS_X1E_FRONT_START_IFE803_PACKET2',
    'CAMSS_X1E_FRONT_START_IFE803_PACKET3',
    'CAMSS_X1E_FRONT_START_CSID1_IPP_START',
    'CAMSS_X1E_FRONT_START_ISP_START_DONE',
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


def block(text, start, end):
    a = text.find(start)
    if a < 0:
        die('missing block start ' + start)
    b = text.find(end, a)
    if b < 0:
        die('missing block end ' + end)
    return text[a:b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--camss-source', type=Path, required=True)
    ap.add_argument('--vfe-source', type=Path, required=True)
    ap.add_argument('--object', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('--crossorder', type=Path, required=True)
    ap.add_argument('--period-inspection', type=Path, required=True)
    ap.add_argument('--rtcdm-inspection', type=Path, required=True)
    ap.add_argument('--bus-inspection', type=Path, required=True)
    ap.add_argument('--ownership-inspection', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    for p, h, label in (
        (a.crossorder, EXPECTED_CROSS_SHA, 'cross-order oracle'),
        (a.period_inspection, EXPECTED_PERIOD_SHA, 'period contract'),
        (a.rtcdm_inspection, EXPECTED_RTCDM_SHA, 'RT-CDM recipe'),
        (a.bus_inspection, EXPECTED_BUS_SHA, 'BUS recipe'),
        (a.ownership_inspection, EXPECTED_OWN_SHA, 'PIX ownership'),
    ):
        if sha(p) != h:
            die(label + ' identity drift')
        if not json.loads(p.read_text()).get('accepted'):
            die(label + ' not accepted')

    cross = json.loads(a.crossorder.read_text())
    period = json.loads(a.period_inspection.read_text())
    if cross.get('cross_layer_order') != EXPECTED_START:
        die('cross-layer start order drift')
    if period['dynamic_policy']['mapping'] != [0, 1, 1, 1]:
        die('two-value period mapping drift')

    src = a.camss_source.read_text()
    vfe = a.vfe_source.read_text()
    patch = a.patch.read_text()
    required = [
        '#define CAMSS_X1E_FRONT_PREP_STAGE_COUNT\t2',
        '#define CAMSS_X1E_FRONT_START_STAGE_COUNT\t10',
        '.period_packet_map = { 0, 1, 1, 1 },',
        '.hardware_execution_authorized = false,',
        '.mipi_sensor_start_included = false,',
        'CAMSS_X1E_FRONT_PREP_PIX_OWNERSHIP',
        'CAMSS_X1E_FRONT_PREP_RTCDM_CORPUS',
        'camss_x1e_front_start_recipe __used = {',
        '.validate = camss_x1e_front_start_validate,',
        'camss->res->version != CAMSS_X1E80100',
        'csid->phy.csiphy_id != 2',
        'csid->phy.phy_sel != CSID_PHY_SEL_CPHY',
        'csid->phy.lane_cnt != 1',
        '!csid->phy.en_ipp',
        'fmt->code != MEDIA_BUS_FMT_SRGGB10_1X10',
        'fmt->width != 3840 || fmt->height != 2640',
        'return camss_rtcdm1_corpus_validate_input(input);',
    ]
    for x in required:
        need(src, x, 'source contract drift')

    cbody = block(src, '.start_order = {', '\n\t},\n\t.hardware_execution_authorized')
    pos = [cbody.find(x) for x in EXPECTED_SOURCE_STAGES]
    if any(x < 0 for x in pos) or pos != sorted(pos):
        die('source stage order drift')

    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c') != 1 or patch.count('--- a/') != 1:
        die('0022 path set drift')
    forbidden_patch = [
        'camss_rtcdm1_windows_open_init(', 'camss_rtcdm1_windows_start(',
        'camss_rtcdm1_windows_fifo0_commit(', 'vfe680_x1e_bus_prepare(',
        'vfe680_x1e_bus_update(', 'vfe680_x1e_bus_stop(', 'writel(',
        'writel_relaxed(', 'enable_irq(', 'v4l2_subdev_call(', 'vfe_enable_v2(',
    ]
    for x in forbidden_patch:
        if x in patch:
            die('0022 adds hardware/runtime call: ' + x)

    m = re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}', vfe, re.S)
    if not m:
        die('vfe_enable_v2 missing')
    body = m.group(1)
    gate = body.find('return -EOPNOTSUPP;')
    lock = body.find('mutex_lock(&vfe->stream_lock)')
    if gate < 0 or lock < 0 or gate >= lock:
        die('VFE1 PIX runtime gate weakened')

    rel = run('aarch64-linux-gnu-objdump', '-r', str(a.object))
    recipe_relocs = [ln.strip() for ln in rel.splitlines()
                     if 'camss_x1e_front_start_validate' in ln]
    if len(recipe_relocs) != 1 or 'R_AARCH64_ABS64' not in recipe_relocs[0]:
        die('front-start recipe relocation drift: ' + repr(recipe_relocs))
    if 'camss_x1e_front_start_recipe' in rel:
        die('compiled relocation references front-start recipe')
    if src.count('camss_x1e_front_start_recipe') != 1:
        die('front-start recipe source reference count drift')

    dis = run('aarch64-linux-gnu-objdump', '-dr', str(a.object))
    vm = re.search(r'<camss_x1e_front_start_validate>:(.*?)(?=\n[0-9a-f]+ <|\Z)', dis, re.S)
    if not vm:
        die('validator disassembly missing')
    vbody = vm.group(1)
    need(vbody, 'camss_rtcdm1_corpus_validate_input', 'validator safe-call drift')
    for x in ('camss_rtcdm1_windows_open_init', 'camss_rtcdm1_windows_start',
              'camss_rtcdm1_windows_fifo0_commit', 'camss_rtcdm1_windows_stop',
              'vfe680_x1e_bus_', 'vfe_enable_v2', 'csid_configure_stream'):
        if x in vbody:
            die('validator reaches hardware helper ' + x)

    nm = run('aarch64-linux-gnu-nm', '-an', str(a.module))
    for x in ('camss_x1e_front_start_validate', 'camss_x1e_front_start_recipe',
              'camss_x1e_front_start_contract'):
        if x not in nm:
            die('retained module symbol missing ' + x)

    out = {
        'schema': 'sp11-e003h-linux-front-start-orchestrator-static-inspection-v1',
        'accepted': True,
        'source_sha256': sha(a.camss_source),
        'object_sha256': sha(a.object),
        'module_sha256': sha(a.module),
        'patch_sha256': sha(a.patch),
        'crossorder_oracle_sha256': EXPECTED_CROSS_SHA,
        'upstream_inspections': {
            'period_cfg_0021': EXPECTED_PERIOD_SHA,
            'rtcdm_0015': EXPECTED_RTCDM_SHA,
            'bus_0017': EXPECTED_BUS_SHA,
            'pix_ownership_0018': EXPECTED_OWN_SHA,
        },
        'target': 'X1E80100 front: CSIPHY2 C-PHY one trio -> CSID1 IPP RAW10 3840x2640 -> IFE1/VFE1',
        'period_packet_mapping': [0, 1, 1, 1],
        'prepare_order': ['PIX_OWNERSHIP', 'RTCDM_CORPUS_MATERIALIZE'],
        'prepare_order_scope': 'Linux-owned allocation/materialization only; no Windows hardware-order claim',
        'start_order_contract': EXPECTED_SOURCE_STAGES,
        'bus_crossorder': 'IFE803 packet0, packet1 -> BUS static config/enable/initial addresses -> packet2, packet3',
        'hardware_execution_authorized': False,
        'mipi_sensor_start_included': False,
        'runtime_isolation': {
            'front_recipe_source_reference_count': 1,
            'front_recipe_relocation_present': False,
            'front_recipe_helper_relocations': recipe_relocs,
            'validator_only_safe_call': 'camss_rtcdm1_corpus_validate_input',
            'hardware_helper_calls_added': False,
            'pix_stream_gate': '-EOPNOTSUPP before stream lock/IRQ/output',
        },
        'policy': 'static contract only; no module load, RT-CDM IRQ arm/FIFO0 submission, VFE1 BUS write, CSID1 start, PIX enable, MIPI/sensor transmission or frame authorized',
    }
    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: front-start order contract is target-exact, two-period-input, retained-only and hardware-unreachable')


if __name__ == '__main__':
    main()
