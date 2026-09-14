#!/usr/bin/env python3
import ctypes, pathlib, struct, subprocess, tempfile
D=pathlib.Path(__file__).resolve().parent
R=D/'oracle/windows-cd90-random-vectors'
b=(R/'vectors.bin').read_bytes()
magic,n,rec,seed=struct.unpack_from('<4I',b,0)
assert magic==0x30394443 and n==4096 and rec==184 and seed==0x8380cd90
assert len(b)==16+n*rec,(len(b),16+n*rec)
tune=struct.unpack('<513I',(R/'tune.bin').read_bytes())
with tempfile.TemporaryDirectory() as td:
    so=pathlib.Path(td)/'cd90.so'
    subprocess.check_call(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(D/'scaffold/sp11-swasf-cd90.c'),'-o',str(so)])
    lib=ctypes.CDLL(str(so)); I16=ctypes.c_int16*8; U8=ctypes.c_uint8*8; I32=ctypes.c_int32*8; Tune=ctypes.c_uint32*513
    lib.sp11_swasf_cd90.argtypes=[ctypes.POINTER(I16),ctypes.POINTER(U8),ctypes.POINTER(U8),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I32),ctypes.POINTER(U8),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(Tune)]
    T=Tune(*tune); off=16
    for it in range(n):
        start=off
        p1=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p3=U8(*b[off:off+8]); off+=8
        p4=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p5=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p6=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p7=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p8=I32(*struct.unpack_from('<8i',b,off)); off+=32
        p9=U8(*b[off:off+8]); off+=8
        p10=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p11=I16(*struct.unpack_from('<8h',b,off)); off+=16
        p12=I16(*struct.unpack_from('<8h',b,off)); off+=16
        want=b[off:off+8]; off+=8
        assert off-start==rec
        out=U8();lib.sp11_swasf_cd90(ctypes.byref(p1),ctypes.byref(out),ctypes.byref(p3),ctypes.byref(p4),ctypes.byref(p5),ctypes.byref(p6),ctypes.byref(p7),ctypes.byref(p8),ctypes.byref(p9),ctypes.byref(p10),ctypes.byref(p11),ctypes.byref(p12),ctypes.byref(T))
        got=bytes(out)
        if got!=want:
            dif=[(i,got[i],want[i]) for i in range(8) if got[i]!=want[i]]
            raise AssertionError((it,dif,got.hex(),want.hex()))
print(f'E004dh CD90 Windows random vectors: PASS ({n} cases / {n*8} lanes)')
