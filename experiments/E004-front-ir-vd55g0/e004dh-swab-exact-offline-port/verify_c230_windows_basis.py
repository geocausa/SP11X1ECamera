#!/usr/bin/env python3
import ctypes, re, subprocess, tempfile
from pathlib import Path

D=Path(__file__).resolve().parent
SRC=D/'scaffold/sp11-swasf-c230.c'
HDR=D/'scaffold/sp11-swasf-c230.h'
RX=re.compile(r'^(?:R=(\d+) C=(\d+)|T=(\d+)) O4=([^ ]+) O2=(\d+),(\d+)$')

def i32_from_shorts(a,b):
    u=(a & 0xffff)|((b & 0xffff)<<16)
    return u-(1<<32) if u & 0x80000000 else u

def load_lib():
    td=tempfile.TemporaryDirectory()
    so=Path(td.name)/'libc230.so'
    subprocess.check_call(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(SRC),'-o',str(so)])
    lib=ctypes.CDLL(str(so))
    Rows=(ctypes.c_int16*8)*7
    Tail=ctypes.c_int16*2
    O4=ctypes.c_int32*2
    O2=ctypes.c_uint8*2
    lib.sp11_swasf_c230.argtypes=[ctypes.POINTER(Rows),ctypes.POINTER(Tail),ctypes.POINTER(O4),ctypes.POINTER(O2)]
    return td,lib,Rows,Tail,O4,O2

def check_file(path, base, delta_expected):
    td,lib,Rows,Tail,O4,O2=load_lib()
    try:
        delta=None; checked=0
        for raw in path.read_text(errors='replace').splitlines():
            line=raw.strip()
            if line.startswith('DELTA='):
                delta=int(line.split('=',1)[1]);
                if abs(delta)!=delta_expected: raise AssertionError((path,delta))
                continue
            m=RX.match(line)
            if not m: continue
            rows=Rows(); tail=Tail(base,base)
            for r in range(7):
                for c in range(8): rows[r][c]=base
            if m.group(1) is not None:
                r=int(m.group(1)); c=int(m.group(2)); rows[r][c]=base+delta
            else:
                t=int(m.group(3)); tail[t]=base+delta
            shorts=[int(x) for x in m.group(4).split(',')]
            want4=(i32_from_shorts(shorts[0],shorts[1]),i32_from_shorts(shorts[2],shorts[3]))
            want2=(int(m.group(5)),int(m.group(6)))
            o4=O4(); o2=O2(); lib.sp11_swasf_c230(ctypes.byref(rows),ctypes.byref(tail),ctypes.byref(o4),ctypes.byref(o2))
            got4=(o4[0],o4[1]); got2=(o2[0],o2[1])
            if got4!=want4 or got2!=want2:
                raise AssertionError((path.name,line,got4,want4,got2,want2))
            checked+=1
        assert checked==116, (path,checked)
        return checked
    finally:
        td.cleanup()

n1=check_file(D/'oracle/windows-c230-basis/RESULT.txt',512,256)
n2=check_file(D/'oracle/windows-c230-basis4096/RESULT.txt',0,4096)
print(f'E004dh C230 Windows basis differential: PASS ({n1+n2} direct oracle cases)')
