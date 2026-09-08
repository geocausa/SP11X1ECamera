#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, math, random, struct, subprocess, tempfile
import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_PROT_ALL, UC_HOOK_CODE
from unicorn.arm64_const import *

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
BU=BASE/'bu-native-aec-zero-delta-preview-profile'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
CE_RESULT=(BASE/'ce-native-aec-final-target-producer'/'VERIFY-RESULT.txt').read_text().splitlines()
DLL_SHA=[x.split('=',1)[1] for x in CE_RESULT if x.startswith('DLL_SHA256=')][0]
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def fbits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]
def fval(u): return struct.unpack('<f',struct.pack('<I',u&0xffffffff))[0]
def old_coord(q):
    x=f32(q)
    if not x>0: return f32(0)
    scale=fval(0x429bcc0c)
    return f32(math.log10(x)*scale)
def exact_math_coord(q):
    x=f32(q)
    if not x>0: return f32(0)
    scale=fval(0x429bcc0c)
    lg=f32(math.log10(x))
    return f32(lg*scale)

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)
def need(t,*xs):
    for x in xs: assert x in t,x

# Require preceding public-state proof and the current native ancestry.
cp=subprocess.run(['git','merge-base','--is-ancestor','3ff2346','HEAD'],cwd=REPO)
assert cp.returncode==0,'CF ancestry missing'
assert 'BU_VERIFY=PASS' in (BU/'VERIFY-RESULT.txt').read_text()

# Exact static input conversion: qword -> float32 -> Windows log10f -> f32 scale -> double.
c=dis(0x1803b47ac,0x1803b485c)
need(c,
 '1803b47b4:', 'ldr\tx8, [x23, #0x10]',
 '1803b47b8:', 'ucvtf\ts0, x8',
 '1803b47bc:', 'bl\t0x180f5cd58',
 '1803b47c4:', 'ldr\ts8, [x8, #0xb34]',
 '1803b47c8:', 'fmul\ts16, s0, s8',
 '1803b47cc:', 'fcvt\td16, s16',
 '1803b47d0:', 'str\td16, [x22, #0x20]',
 '1803b47d8:', 'ucvtf\ts0, x8',
 '1803b47dc:', 'bl\t0x180f5cd58',
 '1803b47e0:', 'fmul\ts16, s0, s8',
 '1803b47e8:', 'str\td16, [x22, #0xa0]',
 '1803b47f4:', 'ldr\tx8, [x23, #0x18]',
 '1803b47f8:', 'ucvtf\ts0, x8',
 '1803b47fc:', 'bl\t0x180f5cd58',
 '1803b4800:', 'fmul\ts16, s0, s8',
 '1803b4808:', 'str\td16, [x22, #0x28]',
 '1803b4824:', 'ldr\tx8, [x23, #0x20]',
 '1803b4830:', 'ucvtf\ts0, x8',
 '1803b4834:', 'bl\t0x180f5cd58',
 '1803b4838:', 'fmul\ts16, s0, s8',
 '1803b4840:', 'str\td16, [x22, #0x30]')

# Scale initialization is log10f(1.03f) followed by a separate f32 reciprocal.
init=dis(0x1800021d0,0x180002218)
need(init,
 '1800021dc:', 'ldr\ts0, 0x1800021f8',
 '1800021e0:', 'bl\t0x180f5cd58',
 '180002204:', 'ldr\ts16, [x8, #0xb38]',
 '180002208:', 'fmov\ts17, #1.00000000',
 '18000220c:', 'fdiv\ts16, s17, s16',
 '180002214:', 'str\ts16, [x8, #0xb34]')

# Build CG and historical BU independently.
td=Path(tempfile.mkdtemp(prefix='e003i-cg-')); cgso=td/'cg.so'; buso=td/'bu.so'
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(cgso)],check=True)
subprocess.run(cc+[str(BU/'native-convergence.c'),'-I',str(BU),'-lm','-o',str(buso)],check=True)
cg=ctypes.CDLL(str(cgso)); bu=ctypes.CDLL(str(buso))
cg.e003i_convergence_log103_u64.argtypes=[ctypes.c_uint64]; cg.e003i_convergence_log103_u64.restype=ctypes.c_float

# Map pinned Windows helper so the native scalar is compared against executable oracle code.
pe=pefile.PE(str(DLL)); base=pe.OPTIONAL_HEADER.ImageBase; size=pe.OPTIONAL_HEADER.SizeOfImage
uc=Uc(UC_ARCH_ARM64,UC_MODE_ARM); page=0x1000
uc.mem_map(base,(size+page-1)&~(page-1),UC_PROT_ALL)
uc.mem_write(base,pe.get_memory_mapped_image(max_virtual_address=size))
stack=0x7000000000; uc.mem_map(stack,0x20000,UC_PROT_ALL); uc.reg_write(UC_ARM64_REG_SP,stack+0x1ff00)
sentinel=0x7001000000; uc.mem_map(sentinel,page,UC_PROT_ALL); uc.mem_write(sentinel,b'\x1f\x20\x03\xd5')
def call_log10f(bits):
    uc.reg_write(UC_ARM64_REG_S0,bits); uc.reg_write(UC_ARM64_REG_X30,sentinel)
    uc.reg_write(UC_ARM64_REG_FPCR,0); uc.reg_write(UC_ARM64_REG_FPSR,0)
    hit=[]
    def hook(u,a,s,d):
        if a==sentinel: hit.append(1); u.emu_stop()
    h=uc.hook_add(UC_HOOK_CODE,hook)
    try: uc.emu_start(0x180f5cd58,sentinel+4,count=1000000)
    finally: uc.hook_del(h)
    assert hit
    return uc.reg_read(UC_ARM64_REG_S0)&0xffffffff
def arm_u64_to_f32_bits(q):
    uc.reg_write(UC_ARM64_REG_X8,int(q)); uc.reg_write(UC_ARM64_REG_FPCR,0); uc.reg_write(UC_ARM64_REG_FPSR,0)
    uc.emu_start(0x1803b47b8,0x1803b47bc,count=1)
    return uc.reg_read(UC_ARM64_REG_S0)&0xffffffff
def windows_coord_bits(q):
    xb=arm_u64_to_f32_bits(q)
    lb=call_log10f(xb)
    # ARM f32 multiply is exactly representable via double product then one f32 rounding.
    return fbits(fval(lb)*fval(0x429bcc0c))

# Recover scale bits directly from executable helper arithmetic.
one03=call_log10f(0x3f83d70a)
assert one03==0x3c52532c,hex(one03)
# f32 reciprocal of the helper result.
recip=fbits(f32(1.0)/fval(one03)); assert recip==0x429bcc0c,hex(recip)

rng=random.Random(0xC70031)
qs=[1,2,3,10,100,1000,37516,10_000_000,2**24-1,2**24+1,2**32-1,2**32+1,
    1093437165,548071942,728799742,1652803121,311393444,1122074225,
    2**53-1,2**53,2**53+1,2**53+3,2**63-1]
qs += [rng.randrange(1,2**63) for _ in range(8192)]
scalar_cases=0; old_traps=[]
for q in qs:
    w=windows_coord_bits(q)
    n=fbits(cg.e003i_convergence_log103_u64(q))
    assert n==w,(q,hex(w),hex(n))
    # Python independent arithmetic agrees for values below 2^53 where int->double is exact.
    if q < 2**53:
        assert n==fbits(exact_math_coord(q)),(q,hex(n),hex(fbits(exact_math_coord(q))))
    if q < 2_000_000_000 and fbits(old_coord(q)) != w and len(old_traps)<8:
        old_traps.append((q,w,fbits(old_coord(q))))
    scalar_cases+=1
assert old_traps, 'need an observable old-order trap'

# ctypes convergence shapes.
class H1(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H2(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H3(ctypes.Structure): _fields_=[('safe_exposure',ctypes.c_uint64)]
class CGIn(ctypes.Structure): _fields_=[('target_exposure',ctypes.c_uint64*3),('history1',H1),('history2',H2),('delayed_history',H3)]
class BUIn(ctypes.Structure): _fields_=[('target_log',ctypes.c_double*3),('history1',H1),('history2',H2),('delayed_history',H3)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*7),('final_log',ctypes.c_double*7),('linear',ctypes.c_uint64*7),
              ('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),
              ('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]
cg.e003i_converge_front_preview_unlocked_qword_history.argtypes=[ctypes.POINTER(CGIn),ctypes.POINTER(Out)]
cg.e003i_converge_front_preview_unlocked_qword_history.restype=ctypes.c_int
bu.e003i_converge_front_preview_unlocked_zero_delta_history.argtypes=[ctypes.POINTER(BUIn),ctypes.POINTER(Out)]
bu.e003i_converge_front_preview_unlocked_zero_delta_history.restype=ctypes.c_int

o=Out(); assert cg.e003i_converge_front_preview_unlocked_qword_history(None,ctypes.byref(o))==-1
z=CGIn(); z.target_exposure[:]=(1,1,0); assert cg.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(z),ctypes.byref(o))==-2

# Structural regression check: for request states whose old/new coordinate bits
# coincide (and drc_gain=1, DisableStretch), CG must be byte-identical to BU.
def obytes(o): return ctypes.string_at(ctypes.byref(o),ctypes.sizeof(o))
def same_coord(q): return fbits(old_coord(q))==fbits(exact_math_coord(q))
compat=0; attempts=0
while compat < 2048 and attempts < 200000:
    attempts+=1
    vals=[rng.randrange(1000,80_000_000) for _ in range(10)]
    if not all(same_coord(v) for v in vals): continue
    ti=vals[:3]; h1=vals[3:6]; h2=vals[6:9]; hd=vals[9]
    a=CGIn(); b=BUIn(); a.target_exposure[:]=ti; b.target_log[:]=[float(exact_math_coord(v)) for v in ti]
    for x,n,v in [(a.history1,'short_exposure',h1[0]),(a.history1,'long_exposure',h1[1]),(a.history1,'safe_exposure',h1[2]),
                  (b.history1,'short_exposure',h1[0]),(b.history1,'long_exposure',h1[1]),(b.history1,'safe_exposure',h1[2]),
                  (a.history2,'short_exposure',h2[0]),(a.history2,'long_exposure',h2[1]),(a.history2,'safe_exposure',h2[2]),
                  (b.history2,'short_exposure',h2[0]),(b.history2,'long_exposure',h2[1]),(b.history2,'safe_exposure',h2[2])]: setattr(x,n,v)
    a.history1.drc_gain=b.history1.drc_gain=1.0; a.history2.drc_gain=b.history2.drc_gain=1.0
    a.delayed_history.safe_exposure=b.delayed_history.safe_exposure=hd
    oa=Out(); ob=Out(); ra=cg.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(a),ctypes.byref(oa)); rb=bu.e003i_converge_front_preview_unlocked_zero_delta_history(ctypes.byref(b),ctypes.byref(ob))
    assert ra==rb,(ra,rb)
    if ra==0: assert obytes(oa)==obytes(ob),compat
    compat+=1
assert compat==2048,(compat,attempts)

# Confirm the corrected ordering is actually observably different from BU's old
# combined-double expression on known scalar traps.
known=1093437165
assert windows_coord_bits(known)==0x443006f5
assert fbits(old_coord(known))==0x443006f6
assert fbits(cg.e003i_convergence_log103_u64(known))==0x443006f5

print('DLL_SHA256='+DLL_SHA)
print('WINDOWS_INPUT_ORDER=UCVTF.f32 -> log10f.f32 -> FMUL.f32(scale) -> FCVT.d64')
print('RECIP_LOG10F_1P03_BITS=0x429bcc0c')
print('SCALAR_ORACLE_CASES='+str(scalar_cases))
print('OLD_ORDER_TRAP=qword1093437165 windows=0x443006f5 old=0x443006f6')
print('BU_COMPATIBLE_REQUEST_CASES='+str(compat))
print('PUBLIC_TARGET_INPUT=Short,Long,Safe qwords')
print('NATIVE_QWORD_COORDINATE_MATCH=bit-exact')
print('CG_VERIFY=PASS')
