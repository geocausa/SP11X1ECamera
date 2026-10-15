#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate the open SP11 rear (ov13858) ISP start-up input from published sources.

Inputs (repository):
  source  front-ae/tuning/ov13858-rear-startup.json: request ids, mode geometry,
          statistics windows, AF window, start 3A state (digital gain, white balance)
  lsc     front-ae/tuning/ov13858-rear-lsc-v1.txt (our flat-field mesh, 13x17 Q10)
Generated here:
  CST12   full-range BT.601 RGB->YCbCr (JFIF, chroma x 255/256), Q10, columns G,B,R
  BPC/ABF the open BPC_ABF register values measured on the front IFE (sweep ae-44..74)
  GTM     zeros (the GTM tone mapper is switched off in camss 50)
Usage: gen-rear-open-input.py source.json lsc.txt out.bin   (prints the SHA-256)
"""
import hashlib
import json
import struct
import sys
from rearprof import Input, pack_scalars


def bt601_jfif_q10():
    """Rows Y, Cb, Cr; columns G, B, R; Q10. Chroma rows sum to 0 so greys stay neutral."""
    kr, kb = 0.299, 0.114
    kg = 1 - kr - kb
    s = 255 / 256
    y = [kg, kb, kr]
    cb = [-kg / (2 * (1 - kb)) * s, 0.5 * s, -kr / (2 * (1 - kb)) * s]
    cr = [-kg / (2 * (1 - kr)) * s, -kb / (2 * (1 - kr)) * s, 0.5 * s]
    q = [[round(v * 1024) for v in r] for r in (y, cb, cr)]
    for r, big in ((q[1], 1), (q[2], 2)):
        r[big] = -(sum(r) - r[big])
    return q


def lsc_tables(path):
    grids, cur = {}, None
    for ln in open(path):
        ln = ln.split("#", 1)[0].strip()
        if not ln:
            continue
        if ln.endswith(":"):
            cur = grids.setdefault(ln[:-1], [])
        else:
            cur.extend(int(x) for x in ln.split())
    r, g, b = grids["red"], grids["green"], grids["blue"]
    if not len(r) == len(g) == len(b) == 221 or max(r + g + b) >= 1 << 13:
        raise ValueError("LSC text: expected 13x17 Q10 grids below 8192")
    return (struct.pack("<221I", *[r[i] | g[i] << 14 for i in range(221)]),
            struct.pack("<221I", *[b[i] | g[i] << 14 for i in range(221)]))


def fill(obj, d):
    for k, v in d.items():
        cur = getattr(obj, k)
        if isinstance(v, dict):
            fill(cur, v)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            for i, x in enumerate(v):
                fill(cur[i], x)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                cur[i] = x
        else:
            setattr(obj, k, v)


def generate(src, lsc_path):
    inp = Input()
    ids = src["request_ids"]
    for i, v in enumerate(ids):
        inp.request_id[i] = v
    start = src["start_3a"]
    sc = bytearray()
    sc[:] = pack_scalars(ids, start["demux_q10"], start["wb_r_q10"], start["wb_b_q10"])
    C.memmove(inp.scalars, bytes(sc), 208)
    fill(inp.geometry, src["geometry"])
    m = bt601_jfif_q10()
    lsc1, lsc2 = lsc_tables(lsc_path)
    for p in range(4):
        fill(inp.stats[p], src["stats"][p])
        iq = inp.iq[p]
        fill(iq, src["iq"][p])
        c = iq.cst
        c.enabled = True
        c.c00 = c.c10 = c.c20 = 0
        c.c01 = c.c11 = c.c21 = 4095
        (c.m00, c.m01, c.m02), (c.m10, c.m11, c.m12), (c.m20, c.m21, c.m22) = m
        c.o0, c.o1, c.o2 = 0, 2048, 2048
        c.s0 = c.s1 = c.s2 = 0
        b = iq.bpcabf  # open BPC_ABF: 0x49b8/0x49bc/0x49d8/0x49dc = 0, 0x49d0/0x49d4/0x49e0 saturated
        for ch in range(2):
            b.signed10[ch] = b.unsigned9[ch] = b.nibble4[ch] = 0
            for i in range(4):
                b.byte_group0[ch][i] = 255
                b.byte_group1[ch][i] = 0
                b.nibble_group[ch][i] = 15
        a = inp.adaptive[p]
        fill(a, src["adaptive"][p])
        C.memmove(a.lsc1, lsc1, 884)
        C.memmove(a.lsc2, lsc2, 884)
        C.memset(a.gtm, 0, 2048)
    return bytes(inp)


import ctypes as C  # noqa: E402


def main():
    data = generate(json.load(open(sys.argv[1])), sys.argv[2])
    open(sys.argv[3], "wb").write(data)
    print(hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
