#!/usr/bin/env python3
import struct
from pathlib import Path
D=Path(__file__).resolve().parent
W=H=16
patterns=['const','impulsep','impulsem','hstep','vstep','checker','random']

def median5(a,b,c,d,e): return sorted((a,b,c,d,e))[2]
def check(side,x0):
    root=D/f'oracle/windows-c3e8-tile-{side}'
    n=0
    for name in patterns:
        src=list(struct.unpack('<256h',(root/f'{name}-src16.bin').read_bytes()))
        raw=list(struct.unpack('<256h',(root/f'{name}-filter16.bin').read_bytes()))
        got=raw[:H*8]
        want=[]
        def at(y,x):
            y=max(0,min(H-1,y)); x=max(0,min(W-1,x)); return src[y*W+x]
        for y in range(H):
            for x in range(x0,x0+8):
                want.append(median5(at(y,x),at(y,x-1),at(y,x+1),at(y-1,x),at(y+1,x)))
        if got!=want:
            for i,(a,b) in enumerate(zip(got,want)):
                if a!=b: raise AssertionError((side,name,i,a,b))
        n+=len(got)
    return n
n=check('left',0)+check('right',8)
print(f'E004dh C3E8 cross5 Windows oracle: PASS ({n} tile pixels)')
