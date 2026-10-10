#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate our own BPC_ABF noise LUT from a measured noise model.

The IFE BPC_ABF filter takes 64 entries, one per intensity bin over the full
scale, each an inverse noise level: bits 0-8 the value (0..511), bits 9 and up
the decrement to the next entry (last entry 0). For a sensor noise model
var = a*x + b (x in full-scale units), the inverse noise level per bin i is
  v_i = S / sqrt(i + c),  c = 64 * b / (a * full_scale)
where S sets the filter strength. Values are clipped to 1..511 and made
non-increasing.
Usage: gen-abf-lut.py --a A --b B --full F --strength S out.bin
"""
import argparse, json, math, struct


def lut(a, b, full, s):
    c = 64.0 * b / (a * full)
    v = [max(1, min(511, round(s / math.sqrt(i + c)))) for i in range(64)]
    for i in range(1, 64):
        v[i] = min(v[i], v[i - 1])
    words = [v[i] | ((v[i] - v[i + 1]) << 9 if i < 63 else 0) for i in range(64)]
    return c, v, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=float, required=True)
    ap.add_argument("--b", type=float, required=True)
    ap.add_argument("--full", type=float, required=True)
    ap.add_argument("--strength", type=float, required=True)
    ap.add_argument("out")
    o = ap.parse_args()
    c, v, words = lut(o.a, o.b, o.full, o.strength)
    with open(o.out, "wb") as f:
        f.write(struct.pack("<64I", *words))
    print(json.dumps({"c_bins": round(c, 3), "strength": o.strength, "values": v}))


if __name__ == "__main__":
    main()
