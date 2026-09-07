#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, math, pefile, random, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_PROT_ALL, UC_HOOK_CODE
from unicorn.arm64_const import *

HERE=Path(__file__).resolve().parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def fval(b): return struct.unpack('<f',struct.pack('<I',b & 0xffffffff))[0]
def dbits(x): return struct.unpack('<Q',struct.pack('<d',float(x)))[0]
def dval(b): return struct.unpack('<d',struct.pack('<Q',b & 0xffffffffffffffff))[0]

# Build the clean-room implementation exactly as intended for SP11 Linux.
td=tempfile.TemporaryDirectory(prefix='e003i-bj-')
so=Path(td.name)/'libnative-log103.so'
subprocess.run(['gcc','-shared','-fPIC','-O2','-fno-fast-math',str(HERE/'native-log103.c'),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))
lib.e003i_log103_coordinate_bits.argtypes=[ctypes.c_uint64]
lib.e003i_log103_coordinate_bits.restype=ctypes.c_uint32

# Map the pinned ARM64 PE at its preferred address and execute only the two
# self-contained math helpers / tiny arithmetic fragments used by RunControl.
pe=pefile.PE(str(DLL))
base=pe.OPTIONAL_HEADER.ImageBase
size=pe.OPTIONAL_HEADER.SizeOfImage
uc=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
page=0x1000
uc.mem_map(base,(size+page-1)&~(page-1),UC_PROT_ALL)
uc.mem_write(base,pe.get_memory_mapped_image(max_virtual_address=size))
stack=0x7000000000
uc.mem_map(stack,0x20000,UC_PROT_ALL)
uc.reg_write(UC_ARM64_REG_SP,stack+0x1ff00)
sentinel=0x7001000000
uc.mem_map(sentinel,page,UC_PROT_ALL)
uc.mem_write(sentinel,b'\x1f\x20\x03\xd5')

def call(start,reg,val):
    uc.reg_write(reg,val)
    uc.reg_write(UC_ARM64_REG_X30,sentinel)
    uc.reg_write(UC_ARM64_REG_FPCR,0)
    uc.reg_write(UC_ARM64_REG_FPSR,0)
    hit=[]
    def hook(u,a,s,d):
        if a==sentinel:
            hit.append(True); u.emu_stop()
    h=uc.hook_add(UC_HOOK_CODE,hook)
    try:
        uc.emu_start(start,sentinel+4,count=1000000)
    finally:
        uc.hook_del(h)
    assert hit
    return uc.reg_read(reg)

# Recover exact shared scale as Windows initializes it:
# log10f(1.03f), then ARM float32 1.0f / result.
one03_bits=0x3f83d70a
log10f_one03_bits=call(0x180f5cd58,UC_ARM64_REG_S0,one03_bits) & 0xffffffff
assert log10f_one03_bits==0x3c52532c,hex(log10f_one03_bits)
uc.reg_write(UC_ARM64_REG_S0,log10f_one03_bits)
uc.reg_write(UC_ARM64_REG_FPCR,0); uc.reg_write(UC_ARM64_REG_FPSR,0)
uc.emu_start(0x1800016e4,0x1800016ec,count=2)
recip_bits=uc.reg_read(UC_ARM64_REG_S16)&0xffffffff
assert recip_bits==0x429bcc0c,hex(recip_bits)
uc.mem_write(0x181795a10,struct.pack('<I',recip_bits))

# Sanity-name the helper family: exact Windows helper returns log10(2).
assert (call(0x180f5cd58,UC_ARM64_REG_S0,fbits(2.0)) & 0xffffffff)==fbits(math.log10(2.0))
assert abs(dval(call(0x180cc2e98,UC_ARM64_REG_D0,dbits(2.0)))-math.log10(2.0))<1e-15

def windows_coordinate(exposure):
    exposure=int(exposure)
    if exposure==0:
        return 0
    # ucvtf s16,x8; fdiv s16,s16,s8; branch; fcvt d0,s16
    uc.reg_write(UC_ARM64_REG_X8,exposure)
    uc.reg_write(UC_ARM64_REG_S8,fbits(37516.0))
    uc.reg_write(UC_ARM64_REG_FPCR,0); uc.reg_write(UC_ARM64_REG_FPSR,0)
    uc.emu_start(0x18038a1b8,0x18038a1d4,count=20)
    ratio_d=uc.reg_read(UC_ARM64_REG_D0)&0xffffffffffffffff
    # exact double log10 helper
    log_d=call(0x180cc2e98,UC_ARM64_REG_D0,ratio_d)
    # ldr exact reciprocal; widen; multiply; narrow
    uc.reg_write(UC_ARM64_REG_D0,log_d)
    uc.reg_write(UC_ARM64_REG_X21,0x181795000)
    uc.reg_write(UC_ARM64_REG_FPCR,0); uc.reg_write(UC_ARM64_REG_FPSR,0)
    uc.emu_start(0x18038a1d8,0x18038a1e8,count=4)
    return uc.reg_read(UC_ARM64_REG_S16)&0xffffffff

# Deterministic corpus covering zero, dense low values, the active base,
# 1.03-step boundaries, known live/table values, large uint64 values, and
# 20k seeded random uint64 values.
vals={0,1,2,3,10,100,999,1000,37515,37516,37517,33312451,241379204,
      2**32-1,2**40,2**48,2**53-1,2**63-1,2**64-1}
vals.update(range(0,10000,3))
vals.update(range(37516-5000,37516+5001,7))
for k in range(-300,1000):
    x=37516.0*(1.03**k)
    if 0 <= x <= 2**64-1:
        n=int(x)
        for d in (-2,-1,0,1,2):
            if 0 <= n+d <= 2**64-1:
                vals.add(n+d)
rng=random.Random(0xE0031B1)
for _ in range(20000):
    vals.add(rng.getrandbits(64))

mismatch=[]
for exposure in sorted(vals):
    w=windows_coordinate(exposure)
    c=int(lib.e003i_log103_coordinate_bits(exposure))
    if w!=c:
        mismatch.append((exposure,w,c))
        if len(mismatch)>=20:
            break
assert not mismatch,mismatch

# Prior live AB2 coordinate/exposure pair.
assert windows_coordinate(33312451)==0x4365acdd
assert int(lib.e003i_log103_coordinate_bits(33312451))==0x4365acdd

cc=subprocess.check_output(['gcc','-dumpmachine'],text=True).strip()
print('DLL_SHA256='+DLL_SHA)
print('WINDOWS_LOG_HELPER_FAMILY=log10')
print(f'LOG10F_1P03_BITS=0x{log10f_one03_bits:08x}')
print(f'RECIP_LOG10F_1P03_BITS=0x{recip_bits:08x}')
print('T681_BASE=37516')
print('AB2_COORD=0x4365acdd PASS')
print(f'CLEANROOM_DIFFERENTIAL={len(vals)}/{len(vals)} bit-exact')
print('TARGET='+cc)
print('BJ_VERIFY=PASS')
