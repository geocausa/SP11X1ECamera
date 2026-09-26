#!/usr/bin/env python3
from __future__ import annotations
import json, struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
AUTH=HERE/'AUTHORITY-SAFE.json'

def pack_points(points):
    if len(points)!=65: raise ValueError('BPCABF411 requires 65 points')
    words=[]
    for i in range(64):
        a=max(0,min(511,int(points[i])))
        b=max(0,min(511,int(points[i+1])))
        words.append(a | (min(511,abs(b-a))<<9))
    return struct.pack('<64I',*words)

def load_and_pack(path:Path=AUTH):
    j=json.load(open(path))
    return pack_points(j['common_setting']['transformed_points'])

if __name__=='__main__':
    p=load_and_pack();print('E007U_BPCABF_PACK_PASS bytes=%d'%len(p))
