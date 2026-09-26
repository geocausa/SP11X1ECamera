#!/usr/bin/env python3
from __future__ import annotations
import json, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTH=HERE/'AUTHORITY-SAFE.json'

def pack_curve(curve):
    if len(curve)!=257:
        raise ValueError('Gamma151 requires 257 semantic samples')
    out=[]
    for i in range(256):
        x=max(0,min(4095,int(curve[i])))
        y=max(0,min(4095 if i<255 else 4096,int(curve[i+1])))
        d=max(-2048,min(2047,y-x))
        out.append(x | ((d & 0xfff)<<12))
    return struct.pack('<256I',*out)

def load_and_pack(path:Path=AUTH):
    j=json.load(open(path))
    return pack_curve(j['curve']['samples'])

if __name__=='__main__':
    p=load_and_pack()
    print('E007T_GAMMA151_PACK_PASS bytes=%d'%len(p))
