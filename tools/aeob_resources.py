#!/usr/bin/env python3
"""Decode an AeoB blob to structured JSON, focused on DEVICE/DSTATE resources."""
from __future__ import annotations
import argparse, io, json, struct
from pathlib import Path
SIG=b'AeoB'; INT=0; STR=1; BUF=2; PKG=3; PKG_EX=4

def u16(b): return struct.unpack('<H',b.read(2))[0]
def u32(b): return struct.unpack('<I',b.read(4))[0]
def u64(b): return struct.unpack('<Q',b.read(8))[0]

def arg(br):
    typ=u16(br); n=u16(br)
    if typ==INT:
        if n==2: v=u16(br)
        elif n==4: v=u32(br)
        elif n==8: v=u64(br)
        else: raise ValueError(f'bad integer size {n}')
    elif typ==STR:
        raw=br.read(n); v=raw[:-1].decode('ascii') if raw.endswith(b'\0') else raw.decode('ascii')
    elif typ==BUF: v={'buffer_hex':br.read(n).hex()}
    elif typ==PKG:
        end=br.tell()+n; v=[]
        while br.tell()<end: v.append(arg(br))
        if br.tell()!=end: raise ValueError('package overflow')
    elif typ==PKG_EX: raise ValueError('PACKAGE_EX unsupported')
    else: raise ValueError(f'unknown type {typ}')
    if n<4: br.read(4-n)
    return v

def parse(path):
    raw=Path(path).read_bytes(); br=io.BytesIO(raw)
    if br.read(4)!=SIG: raise ValueError('not AeoB')
    length=u32(br); count=u32(br)
    if length!=len(raw): raise ValueError(f'length mismatch {length}!={len(raw)}')
    vals=[arg(br) for _ in range(count)]
    if br.tell()!=length: raise ValueError(f'trailing data at {br.tell()} of {length}')
    return vals

def device_summary(vals):
    root=vals[0] if len(vals)==1 and isinstance(vals[0],list) else vals
    if not root or root[0] != 'DEVICE': raise ValueError('root is not DEVICE')
    out={'device_id':root[1], 'acpi_path':root[2], 'dstates':{}}
    for x in root[3:]:
        if isinstance(x,list) and len(x)>=2 and x[0]=='DSTATE':
            st=str(x[1]); resources=[]
            for r in x[2:]:
                if isinstance(r,list) and r:
                    kind=r[0]
                    if len(r)==2 and isinstance(r[1],list): args=r[1]
                    else: args=r[1:]
                    resources.append({'kind':kind,'args':args})
            out['dstates'][st]=resources
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--full',action='store_true'); a=ap.parse_args()
    vals=parse(a.file)
    print(json.dumps(vals if a.full else device_summary(vals),indent=2))
if __name__=='__main__': main()
