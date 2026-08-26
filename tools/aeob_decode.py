#!/usr/bin/env python3
"""Decode Qualcomm Windows AeoB ACPI resource blobs to readable package text.

Format behavior derived from WOA-Project/AeoBUtils (MIT, copyright 2022 WOA Project),
then independently implemented in Python for this project.
"""
from __future__ import annotations
import argparse, io, struct
from pathlib import Path

SIG=b'AeoB'
INT, STR, BUF, PKG, PKG_EX = range(5)

def u16(b): return struct.unpack('<H', b.read(2))[0]
def u32(b): return struct.unpack('<I', b.read(4))[0]
def u64(b): return struct.unpack('<Q', b.read(8))[0]

def parse_arg(br: io.BytesIO, depth=0):
    typ=u16(br); n=u16(br); pad=' '*(depth*4)
    if typ==INT:
        if n==2: v=u16(br); width=4
        elif n==4: v=u32(br); width=8
        elif n==8: v=u64(br); width=16
        else: raise ValueError(f'unknown integer length {n} at 0x{br.tell()-4:x}')
        out=f'{pad}0x{v:0{width}X},\n'
    elif typ==STR:
        raw=br.read(n)
        if not raw.endswith(b'\0'): raise ValueError('unterminated string')
        out=f'{pad}"{raw[:-1].decode("ascii")}",\n'
    elif typ==BUF:
        raw=br.read(n)
        vals=', '.join(f'0x{x:02X}' for x in raw)
        out=f'{pad}Buffer (0x{n:04X}) {{ {vals} }},\n'
    elif typ==PKG:
        end=br.tell()+n
        chunks=[]
        while br.tell()<end: chunks.append(parse_arg(br, depth+1))
        if br.tell()!=end: raise ValueError('package overflow')
        out=f'{pad}Package ()\n{pad}{{\n'+''.join(chunks)+f'{pad}}},\n'
    elif typ==PKG_EX:
        raise ValueError('PACKAGE_EX not implemented')
    else: raise ValueError(f'unknown type {typ}')
    if n<4: br.read(4-n)
    return out

def decode(path):
    br=io.BytesIO(Path(path).read_bytes())
    if br.read(4)!=SIG: raise ValueError('invalid AeoB signature')
    length=u32(br); count=u32(br)
    if length!=len(br.getbuffer()): raise ValueError(f'length mismatch header={length} actual={len(br.getbuffer())}')
    out=''.join(parse_arg(br,0) for _ in range(count))
    if br.tell()!=length: raise ValueError(f'trailing bytes: pos={br.tell()} length={length}')
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('-o','--output'); a=ap.parse_args()
    text=decode(a.input)
    if a.output: Path(a.output).write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
