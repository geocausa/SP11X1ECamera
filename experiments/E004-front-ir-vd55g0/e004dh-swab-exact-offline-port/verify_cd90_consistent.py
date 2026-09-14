#!/usr/bin/env python3
import ctypes, pathlib, struct, subprocess, tempfile
D=pathlib.Path(__file__).resolve().parent
C=D/'oracle/windows-cd90-consistent'
with tempfile.TemporaryDirectory() as td:
    so=pathlib.Path(td)/'cd90.so'
    subprocess.check_call(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(D/'scaffold/sp11-swasf-cd90.c'),'-o',str(so)])
    lib=ctypes.CDLL(str(so))
    I16=ctypes.c_int16*8; U8=ctypes.c_uint8*8; I32=ctypes.c_int32*8; Tune=ctypes.c_uint32*513
    lib.sp11_swasf_cd90.argtypes=[ctypes.POINTER(I16),ctypes.POINTER(U8),ctypes.POINTER(U8),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I32),ctypes.POINTER(U8),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(I16),ctypes.POINTER(Tune)]
    def a16(n): return I16(*struct.unpack('<8h',(C/n).read_bytes()))
    def a8(n): return U8(*(C/n).read_bytes())
    p1=a16('p1.bin'); out=U8(); p3=a8('p3.bin'); p4=a16('p4.bin'); p5=a16('p5.bin'); p6=a16('p6.bin'); p7=a16('p7.bin')
    p8=I32(*struct.unpack('<8i',(C/'p8.bin').read_bytes())); p9=a8('p9.bin'); p10=a16('p10.bin'); p11=a16('p11.bin'); p12=a16('p12.bin'); tune=Tune(*struct.unpack('<513I',(C/'p13.bin').read_bytes()))
    lib.sp11_swasf_cd90(ctypes.byref(p1),ctypes.byref(out),ctypes.byref(p3),ctypes.byref(p4),ctypes.byref(p5),ctypes.byref(p6),ctypes.byref(p7),ctypes.byref(p8),ctypes.byref(p9),ctypes.byref(p10),ctypes.byref(p11),ctypes.byref(p12),ctypes.byref(tune))
    want=(C/'p2-after.bin').read_bytes(); got=bytes(out)
    assert got==want,(got.hex(),want.hex())
print('E004dh CD90 consistent Windows invocation: PASS')
