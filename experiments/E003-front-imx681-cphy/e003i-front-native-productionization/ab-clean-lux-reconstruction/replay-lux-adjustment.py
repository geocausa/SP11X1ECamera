#!/usr/bin/env python3
import math, struct

def f32(x):
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]

def from_bits(bits):
    return struct.unpack('<f', struct.pack('<I', bits))[0]

def bits(x):
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]

def algorithm001(measured_bits, target_bits, baseline_bits, k_bits, previous_bits=0, alpha_bits=0):
    measured = from_bits(measured_bits)
    target = from_bits(target_bits)
    baseline = from_bits(baseline_bits)
    k = from_bits(k_bits)
    previous = from_bits(previous_bits)
    alpha = from_bits(alpha_bits)
    tiny = from_bits(0x33d6bf95)  # constant loaded by the Windows routine
    ratio = f32(max(target, tiny) / max(measured, tiny))
    if ratio > 0.0:
        delta = f32(math.log10(float(ratio)) * float(k))
    else:
        delta = f32(0.0)
    candidate = f32(max(f32(baseline + delta), 0.0))
    if abs(previous) >= 0.5:
        candidate = f32(f32(f32(1.0 - alpha) * candidate) + f32(alpha * previous))
    return candidate

CASES = [
    dict(name='ab2-iter1', measured=0x40f19357, target=0x42480000,
         baseline=0x4365acdd, k=0x429bcc0c, previous=0x00000000, alpha=0x00000000,
         expected=0x4392d14d),
    dict(name='ab2-iter2', measured=0x40f19d1a, target=0x42480000,
         baseline=0x4365acdd, k=0x429bcc0c, previous=0x4392d14d, alpha=0x00000000,
         expected=0x4392d09e),
]

if __name__ == '__main__':
    ok = True
    for c in CASES:
        out = algorithm001(c['measured'], c['target'], c['baseline'], c['k'], c['previous'], c['alpha'])
        out_bits = bits(out)
        passed = out_bits == c['expected']
        ok &= passed
        print(f"{c['name']}: measured={from_bits(c['measured']):.9g} target={from_bits(c['target']):.9g} "
              f"baseline={from_bits(c['baseline']):.9g} K={from_bits(c['k']):.9g} "
              f"out={out:.9g} bits=0x{out_bits:08x} expected=0x{c['expected']:08x} pass={passed}")
    raise SystemExit(0 if ok else 1)
