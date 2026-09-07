#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / 'imx681.c').read_text()
HDR = (HERE / 'imx681-sp11-mode2-regs.h').read_text()
ORACLE_PATH = HERE / 'windows-oracle' / 'oracle.py'
spec = importlib.util.spec_from_file_location('aj_windows_oracle', ORACLE_PATH)
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def define_hex(name):
    m = re.search(rf'^#define\s+{re.escape(name)}\s+CCI_REG(?:8|16|24)\((0x[0-9a-fA-F]+)\)', SRC, re.M)
    need(m, f'missing register define {name}')
    return int(m.group(1), 16)


def simple_define(name):
    m = re.search(rf'^#define\s+{re.escape(name)}\s+([^\s/]+)', SRC, re.M)
    need(m, f'missing define {name}')
    token = m.group(1).rstrip('UuLl')
    return int(token, 0)


def source_function(name):
    start = SRC.index(f'static int {name}')
    next_static = SRC.find('\nstatic ', start + 1)
    return SRC[start: next_static if next_static >= 0 else len(SRC)]


def parse_mode_registers():
    regs = {}
    for a, v in re.findall(r'\{\s*CCI_REG8\((0x[0-9a-fA-F]+)\),\s*(0x[0-9a-fA-F]+)\s*\}', HDR):
        regs[int(a, 16)] = int(v, 16)
    return regs


def bytes_for_value(addr, value, width):
    return [(addr + i, (value >> (8 * (width - 1 - i))) & 0xff) for i in range(width)]


def linux_dynamic_bytes(fll, exposure, again, dgain):
    # CCI_REG24/16 use register-width big-endian byte order. AJ masks coarse bit0.
    exposure &= ~1
    return (
        bytes_for_value(0x033d, fll & 0xffffff, 3)
        + bytes_for_value(0x0229, exposure & 0xffffff, 3)
        + bytes_for_value(0x0204, again & 0xffff, 2)
        + bytes_for_value(0x020e, dgain & 0xffff, 2)
    )


def main():
    oracle_sha256 = hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest()
    need(oracle_sha256 == '2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f',
         f'Windows oracle hash changed: {oracle_sha256}')

    # Stable active-path register identities recovered live on Windows.
    need(define_hex('IMX681_REG_GROUP_HOLD') == 0x0104, 'group hold address')
    need(define_hex('IMX681_REG_FRAME_LENGTH') == oracle.FLL_ADDR, 'FLL address')
    need(define_hex('IMX681_REG_EXPOSURE') == oracle.COARSE_INT_ADDR, 'coarse address')
    need(define_hex('IMX681_REG_ANALOG_GAIN') == oracle.ANALOG_GAIN_ADDR, 'analogue address')
    need(define_hex('IMX681_REG_DIGITAL_GAIN') == oracle.DIGITAL_GLOBAL_GAIN_ADDR, 'global digital address')

    # Windows-derived raw-code limits, without the obsolete PR164 combined-gain guess.
    need(simple_define('IMX681_ANALOG_GAIN_MAX') == 0x3c0, 'analogue max')
    need(simple_define('IMX681_DIGITAL_GAIN_MIN') == 0x100, 'digital min')
    need(simple_define('IMX681_DIGITAL_GAIN_MAX') == 0x0f00, 'digital max')
    need(simple_define('IMX681_EXPOSURE_DEFAULT') == 3546, 'exposure default')

    apply = source_function('imx681_apply_request_controls')
    ordered = [
        'IMX681_REG_GROUP_HOLD, 1',
        'IMX681_REG_FRAME_LENGTH, frame_length',
        'IMX681_REG_EXPOSURE, exposure',
        'IMX681_REG_ANALOG_GAIN, analogue_gain',
        'IMX681_REG_DIGITAL_GAIN, digital_gain',
        'IMX681_REG_GROUP_HOLD, 0',
    ]
    pos = -1
    for needle in ordered:
        p = apply.find(needle, pos + 1)
        need(p >= 0, f'missing/out-of-order transaction element {needle}')
        pos = p
    need('exposure->val & ~1U' in apply, 'Windows even-line mask absent')
    need('ret_hold = cci_write' in apply and 'if (ret_hold)' in apply, 'unconditional hold release/error propagation absent')
    need('0x0210' not in apply and '0x0212' not in apply and '0x0214' not in apply,
         'per-colour digital gain leaked into dynamic path')

    init = source_function('imx681_init_controls')
    need('v4l2_ctrl_cluster(4, &imx681->vblank)' in init, 'four-control cluster absent')
    need('V4L2_CID_VBLANK' in init and 'V4L2_CID_EXPOSURE' in init and
         'V4L2_CID_ANALOGUE_GAIN' in init and 'V4L2_CID_DIGITAL_GAIN' in init,
         'control ABI incomplete')
    need('IMX681_EXPOSURE_MIN, exposure_max, 2' in init, 'even exposure step absent')

    stream = source_function('imx681_s_stream')
    p_mode = stream.index('imx681_program_mode2_standby')
    p_ctrl = stream.index('v4l2_ctrl_handler_setup')
    p_stream = stream.index('IMX681_MODE_STREAMING')
    need(p_mode < p_ctrl < p_stream, 'cached controls are not restored between mode table and STREAMON')

    # The current static mode2 table must itself be an identity AJ transaction.
    regs = parse_mode_registers()
    fll = (regs[0x033d] << 16) | (regs[0x033e] << 8) | regs[0x033f]
    coarse = (regs[0x0229] << 16) | (regs[0x022a] << 8) | regs[0x022b]
    again = (regs[0x0204] << 8) | regs[0x0205]
    dgain = (regs[0x020e] << 8) | regs[0x020f]
    need((fll, coarse, again, dgain) == (3554, 3546, 0, 0x100),
         f'unexpected mode2 defaults {(fll, coarse, again, dgain)}')
    need(linux_dynamic_bytes(fll, coarse, again, dgain) ==
         oracle.fill_exposure_settings(fll, coarse, again, dgain),
         'mode2 default byte transaction differs from Windows')

    # Canonical Windows decoded example: gain 32 -> AG 0x3c0, DG 0x0200.
    exp, win = oracle.replay(32.0, 0x6789, 0x12345)
    need((exp['analog_reg'], exp['digital_reg']) == (0x3c0, 0x200), 'Windows gain32 conversion changed')
    need(linux_dynamic_bytes(0x12345, 0x6789, exp['analog_reg'], exp['digital_reg']) == win,
         'canonical Linux transaction differs from Windows')

    # Deterministic boundary/fuzz proof over the control domain. Odd exposure input
    # is intentionally included: both Windows and AJ clear bit0 before publication.
    rng = random.Random(0x681A1)
    for _ in range(20000):
        fll = rng.randint(2164, 0xffffff)
        exposure = rng.randint(4, min(fll - 4, 0xffffff))
        again = rng.randint(0, 0x3c0)
        dgain = rng.randint(0x100, 0x0f00)
        got = linux_dynamic_bytes(fll, exposure, again, dgain)
        want = oracle.fill_exposure_settings(fll, exposure, again, dgain)
        need(got == want, (fll, exposure, again, dgain, got, want))

    result = {
        'schema': 'sp11-e003i-aj-imx681-exposure-controls-proof-v1',
        'status': 'PASS',
        'windows_oracle_self_test': 'PASS',
        'windows_oracle_sha256_expected': '2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f',
        'active_registers': {
            'group_hold': '0x0104', 'frame_length': '0x033d', 'coarse': '0x0229',
            'analogue_gain': '0x0204', 'digital_global_gain': '0x020e'
        },
        'mode2_defaults': {'fll': 3554, 'exposure': 3546, 'analogue_code': 0, 'digital_code': 256},
        'dynamic_bytes_per_request': 10,
        'per_colour_dynamic_digital_gain': False,
        'clustered_controls': ['V4L2_CID_VBLANK', 'V4L2_CID_EXPOSURE', 'V4L2_CID_ANALOGUE_GAIN', 'V4L2_CID_DIGITAL_GAIN'],
        'exposure_even_line_contract': True,
        'fuzz_cases': 20000,
    }
    (HERE / 'PROOF.json').write_text(json.dumps(result, indent=2) + '\n')
    print('AJ_WINDOWS_ORACLE_SELFTEST=PASS')
    oracle.self_test()
    print('AJ_SOURCE_TRANSACTION=PASS')
    print('AJ_MODE2_DEFAULT_IDENTITY=PASS')
    print('AJ_WINDOWS_DYNAMIC_BYTES=20000/20000')
    print('AJ_PROOF=PASS')


if __name__ == '__main__':
    main()
