#!/usr/bin/env python3
import argparse
import struct

# Live-proven SP11 IMX681 custom callback RVAs in QcDeviceMFT8380.dll.
CALCULATE_EXPOSURE_RVA = 0x870EE0
FILL_EXPOSURE_SETTINGS_RVA = 0x871000
GET_SENSOR_MODE_INDEX_RVA = 0x8712F0

# Live-proven mode0 register bases read from the active custom sensor-info object.
FLL_ADDR = 0x033D
COARSE_INT_ADDR = 0x0229
SHORT_COARSE_INT_ADDR = 0x0224  # present in sensor-info, not emitted by the active single-exposure callback
ANALOG_GAIN_ADDR = 0x0204
DIGITAL_GLOBAL_GAIN_ADDR = 0x020E

ANALOG_SCALE = 1024.0
ANALOG_REG_MAX = 0x3C0
ANALOG_REG_SPECIAL_CAP = 0x380
DIGITAL_SCALE = 256.0
DIGITAL_INV_SCALE = 1.0 / 256.0
DIGITAL_REAL_MAX = 15.0


def f32(x):
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def f32bits(x):
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]


def calculate_exposure(real_gain, line_count, special_0x380_cap=False):
    """Replay QcDeviceMFT8380+0x870ee0 for the active IMX681 path."""
    g = f32(real_gain)

    # ARM64 path converts requested float to double for analog-register conversion.
    target = float(g)
    if target < 1.0:
        target = 1.0
    elif target > 16.0:
        target = 16.0

    analog_reg = int(ANALOG_SCALE - ANALOG_SCALE / target)  # FCVTZU, all values non-negative

    # Input flag at CalculateExposure input +0x18. For the flagged path the sensor caps AG at 0x380.
    if special_0x380_cap and analog_reg > ANALOG_REG_SPECIAL_CAP:
        analog_reg = ANALOG_REG_SPECIAL_CAP
    if analog_reg > ANALOG_REG_MAX:
        analog_reg = ANALOG_REG_MAX

    # UC VTF -> double math -> FCVT single.
    analog_gain = f32(ANALOG_SCALE / (ANALOG_SCALE - float(analog_reg)))

    # Remaining digital gain is calculated in single precision only when requested gain > 16.
    if g <= f32(16.0):
        digital_target = f32(1.0)
    else:
        digital_target = f32(g / analog_gain)
    if digital_target > f32(DIGITAL_REAL_MAX):
        digital_target = f32(DIGITAL_REAL_MAX)

    digital_reg = int(f32(digital_target * f32(DIGITAL_SCALE)))  # FMUL s + FCVTZU
    digital_gain = f32(f32(float(digital_reg)) * f32(DIGITAL_INV_SCALE))
    isp_gain = f32(g / f32(analog_gain * digital_gain))

    return {
        'requested_gain': g,
        'requested_gain_bits': f32bits(g),
        'analog_reg': analog_reg,
        'analog_gain': analog_gain,
        'analog_gain_bits': f32bits(analog_gain),
        'digital_reg': digital_reg,
        'digital_gain': digital_gain,
        'digital_gain_bits': f32bits(digital_gain),
        'isp_gain': isp_gain,
        'isp_gain_bits': f32bits(isp_gain),
        'line_count': int(line_count) & 0xFFFFFFFF,
        'special_0x380_cap': bool(special_0x380_cap),
    }


def fill_exposure_settings(frame_length_lines, line_count, analog_reg, digital_reg):
    """Replay the 10 generated dynamic register writes in QcDeviceMFT8380+0x871000.

    The real callback copies any configured pre-register list first and post-register list last.
    This function returns the exact 10 dynamic IMX681 writes between those lists.
    """
    fll = int(frame_length_lines) & 0xFFFFFFFF
    coarse = (int(line_count) & 0xFFFFFFFF) & 0xFFFFFFFE  # callback clears bit 0 in-place
    ag = int(analog_reg) & 0xFFFFFFFF
    dg = int(digital_reg) & 0xFFFFFFFF

    writes = [
        (FLL_ADDR + 0, (fll >> 16) & 0xFF),
        (FLL_ADDR + 1, (fll >> 8) & 0xFF),
        (FLL_ADDR + 2, fll & 0xFF),
        (COARSE_INT_ADDR + 0, (coarse >> 16) & 0xFF),
        (COARSE_INT_ADDR + 1, (coarse >> 8) & 0xFF),
        (COARSE_INT_ADDR + 2, coarse & 0xFF),
        (ANALOG_GAIN_ADDR + 0, (ag >> 8) & 0xFF),
        (ANALOG_GAIN_ADDR + 1, ag & 0xFF),
        (DIGITAL_GLOBAL_GAIN_ADDR + 0, (dg >> 8) & 0xFF),
        (DIGITAL_GLOBAL_GAIN_ADDR + 1, dg & 0xFF),
    ]
    return writes


def replay(real_gain, line_count, frame_length_lines, special_0x380_cap=False):
    exp = calculate_exposure(real_gain, line_count, special_0x380_cap)
    return exp, fill_exposure_settings(frame_length_lines, exp['line_count'], exp['analog_reg'], exp['digital_reg'])


def self_test():
    # Exact algebraic/boundary fixtures from the decoded callback.
    fixtures = [
        (1.0, False, 0x000, 0x100, 1.0, 1.0, 1.0),
        (16.0, False, 0x3C0, 0x100, 16.0, 1.0, 1.0),
        (32.0, False, 0x3C0, 0x200, 16.0, 2.0, 1.0),
        (300.0, False, 0x3C0, 0xF00, 16.0, 15.0, 1.25),
        (16.0, True, 0x380, 0x100, 8.0, 1.0, 2.0),
    ]
    for gain, cap, agreg, dgreg, again, dgain, ispg in fixtures:
        got = calculate_exposure(gain, 0x6789, cap)
        assert got['analog_reg'] == agreg, (gain, 'analog_reg', got)
        assert got['digital_reg'] == dgreg, (gain, 'digital_reg', got)
        assert f32bits(got['analog_gain']) == f32bits(again), (gain, 'analog_gain', got)
        assert f32bits(got['digital_gain']) == f32bits(dgain), (gain, 'digital_gain', got)
        assert f32bits(got['isp_gain']) == f32bits(ispg), (gain, 'isp_gain', got)

    w = fill_exposure_settings(0x012345, 0x006789, 0x03C0, 0x0100)
    expected = [
        (0x033D, 0x01), (0x033E, 0x23), (0x033F, 0x45),
        (0x0229, 0x00), (0x022A, 0x67), (0x022B, 0x88),
        (0x0204, 0x03), (0x0205, 0xC0),
        (0x020E, 0x01), (0x020F, 0x00),
    ]
    assert w == expected, (w, expected)
    print('IMX681_AJ_SELFTEST=PASS')
    print('CUSTOM_CALLBACKS=%#x,%#x,%#x' % (CALCULATE_EXPOSURE_RVA, FILL_EXPOSURE_SETTINGS_RVA, GET_SENSOR_MODE_INDEX_RVA))
    print('MODE0_BASES=FLL:%#06x COARSE:%#06x SHORT:%#06x AG:%#06x DG:%#06x' % (
        FLL_ADDR, COARSE_INT_ADDR, SHORT_COARSE_INT_ADDR, ANALOG_GAIN_ADDR, DIGITAL_GLOBAL_GAIN_ADDR))


def main():
    ap = argparse.ArgumentParser(description='SP11 Windows IMX681 custom exposure/register replay')
    ap.add_argument('--gain', type=float, default=32.0)
    ap.add_argument('--line-count', type=lambda x: int(x, 0), default=0x6789)
    ap.add_argument('--fll', type=lambda x: int(x, 0), default=0x12345)
    ap.add_argument('--special-0x380-cap', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    exp, writes = replay(args.gain, args.line_count, args.fll, args.special_0x380_cap)
    for k, v in exp.items():
        if isinstance(v, float):
            print(f'{k}={v:.9g}')
        else:
            print(f'{k}={v}')
    print('dynamic_writes:')
    for addr, value in writes:
        print(f'  0x{addr:04x} = 0x{value:02x}')


if __name__ == '__main__':
    main()
