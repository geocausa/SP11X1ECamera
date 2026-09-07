#!/usr/bin/env python3
"""Replay one front AWB_BG request through the clean CCT model.

Lux is always explicit. Temporal publication requires explicit previous XY bits;
use --fresh-only to stop at the fresh AGW target.
"""
import argparse, json, struct
from pathlib import Path
import cct_model as m

def frombits(v):
    return struct.unpack('<f', struct.pack('<I', int(v, 0)))[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('raw', type=Path, help='Titan680 AWB_BG raw buffer (3072 * 0x50 bytes)')
    ap.add_argument('--lux', required=True, type=float, help='request-local AEC/AWB lux index')
    ap.add_argument('--fresh-only', action='store_true', help='stop before temporal publication blend')
    ap.add_argument('--prev-x-bits', help='previous final X float32 bits, e.g. 0x3f1129ca')
    ap.add_argument('--prev-y-bits', help='previous final Y float32 bits, e.g. 0x3f00e486')
    a=ap.parse_args()
    g=m.agw(a.raw, a.lux)
    out={
        'raw': str(a.raw), 'lux': a.lux, 'p01': g['p01'], 'valid': g['valid'],
        'sum_weight': float(g['sumW']),
        'fresh_xy_bits': [f'0x{m.bits(g["x"]):08x}', f'0x{m.bits(g["y"]):08x}'],
        'fresh_xy': [float(g['x']), float(g['y'])], 'fresh_cct': float(g['cct'])
    }
    if not a.fresh_only:
        if a.prev_x_bits is None or a.prev_y_bits is None:
            ap.error('temporal publication requires --prev-x-bits and --prev-y-bits, or use --fresh-only')
        px,py=frombits(a.prev_x_bits),frombits(a.prev_y_bits)
        x,y,c=m.temporal(g['x'],g['y'],px,py)
        out.update({
            'previous_xy_bits':[f'0x{m.bits(px):08x}',f'0x{m.bits(py):08x}'],
            'final_xy_bits':[f'0x{m.bits(x):08x}',f'0x{m.bits(y):08x}'],
            'final_xy':[float(x),float(y)], 'final_cct':float(c),
            'published_cct':int(c)
        })
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__=='__main__':
    main()
