#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, json, math, random, struct, subprocess, sys, tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CB=BASE/'cb-windows-aec-adrc-darkboost-tail'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'


def fresh(path, script, marker):
    cp=subprocess.run([sys.executable,str(path/script)],cwd=path,text=True,
                      stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{script} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(script,marker,cp.stdout)

fresh(CB,'verify-cb.py','CB_VERIFY=PASS')
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

src=(HERE/'native-aec-tail.c').read_text(); hdr=(HERE/'native-aec-tail.h').read_text()
for needle in [
    'e003i_aec_default_tail', 'lerp_win', 'short_gain_ramp',
    'long_primary_child', 'long_primary', 'long_remainder_branch',
    'return lerp_win(g, g,', '-ffp-contract=off']:
    if needle == '-ffp-contract=off':
        continue
    assert needle in src or needle in hdr,needle
assert 'primary < remainder_branch ? primary : remainder_branch' in src


def f32(x): return np.float32(x)
def bits(x): return struct.unpack('<I',struct.pack('<f',float(f32(x))))[0]
def add(a,b): return f32(f32(a)+f32(b))
def sub(a,b): return f32(f32(a)-f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b):
    with np.errstate(all='ignore'):
        return f32(f32(a)/f32(b))

def lerp(low,high,t):
    t=f32(t)
    omt=sub(f32(1.0),t)
    return add(mul(low,omt),mul(high,t))

def cap(lux):
    lux=f32(lux); v16=f32(np.frombuffer(struct.pack('<I',0x3fcccccd),dtype=np.float32)[0]); v15=f32(1.5); v14=f32(np.frombuffer(struct.pack('<I',0x3fb33333),dtype=np.float32)[0])
    if lux <= f32(210): return v16
    if lux < f32(260): return lerp(v16,v15,div(sub(lux,210),50))
    if lux <= f32(300): return v15
    if lux < f32(320): return lerp(v15,v14,div(sub(lux,300),20))
    return v14

def short_ramp(r):
    r=f32(r)
    if r <= f32(1): return f32(1)
    if r < f32(1000): return lerp(1,1000,div(sub(r,1),999))
    return f32(1000)

def long_child(r):
    r=f32(r)
    if r <= f32(1): return f32(1)
    if r < f32(2): return lerp(1,2,sub(r,1))
    return f32(2)

def long_primary(lux,r):
    lux=f32(lux); g=long_child(r)
    if lux <= f32(260): return g
    if lux < f32(300): return lerp(g,g,div(sub(lux,260),40))
    if lux <= f32(320): return g
    if lux < f32(360): return lerp(g,1,div(sub(lux,320),40))
    return f32(1)

def long_rem(rem):
    rem=f32(rem)
    if rem <= f32(1): return f32(1)
    if rem < f32(64): return lerp(1,64,div(sub(rem,1),63))
    return f32(64)

def reference(lux,safe,st,lt):
    lux,safe,st,lt=map(f32,(lux,safe,st,lt))
    c=cap(lux)
    ars=div(safe,st)
    ag=short_ramp(ars)
    if c < ag: ag=c
    short=div(safe,ag)
    rem=div(8,ag)
    arl=div(lt,safe)
    p=long_primary(lux,arl)
    rr=long_rem(rem)
    db=p if p < rr else rr
    longv=mul(safe,db)
    return (c,ars,ag,short,rem,arl,db,longv)

# Compile the exact native source with contraction disabled.
tmp=Path(tempfile.mkdtemp(prefix='e003i-cc-')); so=tmp/'cc.so'
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',
    '-fno-fast-math','-ffp-contract=off']
subprocess.run(cc+[str(HERE/'native-aec-tail.c'),'-I',str(HERE),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))
class In(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('safe_adj_ratio',ctypes.c_float),
              ('short_target',ctypes.c_float),('long_target',ctypes.c_float)]
class Out(ctypes.Structure):
    _fields_=[('adrc_lux_cap',ctypes.c_float),('adj_ratio_short',ctypes.c_float),
              ('adrc_gain',ctypes.c_float),('short_adj_ratio',ctypes.c_float),
              ('drc_gain_remainder',ctypes.c_float),('adj_ratio_long',ctypes.c_float),
              ('dark_boost_gain',ctypes.c_float),('long_adj_ratio',ctypes.c_float)]
lib.e003i_aec_default_tail.argtypes=[ctypes.POINTER(In),ctypes.POINTER(Out)]
lib.e003i_aec_default_tail.restype=ctypes.c_int

def native(vals):
    i=In(*[float(f32(x)) for x in vals]); o=Out()
    rc=lib.e003i_aec_default_tail(ctypes.byref(i),ctypes.byref(o)); assert rc==0,rc
    return tuple(f32(getattr(o,n)) for n,_ in Out._fields_)

def same_tuple(a,b,tag):
    aa=[bits(x) for x in a]; bb=[bits(x) for x in b]
    assert aa==bb,(tag,aa,bb,[float(x) for x in a],[float(x) for x in b])

# Fail-closed API.
o=Out(); i=In(1,1,1,1)
assert lib.e003i_aec_default_tail(None,ctypes.byref(o))==-1
assert lib.e003i_aec_default_tail(ctypes.byref(i),None)==-1
for vals in [(math.nan,1,1,1),(1,math.inf,1,1),(1,1,0,1),(1,-1,1,1),(1,1,1,0)]:
    x=In(*vals); rc=lib.e003i_aec_default_tail(ctypes.byref(x),ctypes.byref(o)); assert rc in (-2,-3),(vals,rc)

# Edge corpus covers all Lux plateaus/gaps and ratio branch boundaries.
luxes=[-100,0,209.999,210,210.001,235,259.999,260,299.999,300,310,319.999,320,340,359.999,360,1000,1200]
safes=[0.25,1.0,1.4880515336990356,1.6,8.0,64.0,255.0]
shorts=[0.25,0.5,1.0,2.0,16.0,255.0]
longs=[0.25,1.0,1.1,2.0,16.0,255.0]
edge=0
for lux in luxes:
    for safe in safes:
        for st in shorts:
            for lt in longs:
                same_tuple(reference(lux,safe,st,lt),native((lux,safe,st,lt)),('edge',lux,safe,st,lt))
                edge+=1

# A public-output 1-ULP trap for the Short ramp while the Lux cap stays above it.
trap_ratio=f32(1.4880515336990356)
trap=reference(0.0,trap_ratio,1.0,trap_ratio)
assert bits(trap_ratio)==0x3fbe7879
assert bits(trap[2])==0x3fbe787a,(hex(bits(trap[2])),float(trap[2]))
assert bits(native((0.0,trap_ratio,1.0,trap_ratio))[2])==0x3fbe787a

# CB's equal-child Long outer-gap trap remains visible at DarkBoostGain.
trap2=reference(f32(260.9975),1.0,1.0,f32(1.1))
assert bits(trap2[5])==0x3f8ccccd
assert bits(trap2[6])==0x3f8ccccc,(hex(bits(trap2[6])),float(trap2[6]))
assert bits(native((f32(260.9975),1.0,1.0,f32(1.1)))[6])==0x3f8ccccc

# Deterministic broad finite-positive differential corpus.
rng=random.Random(0xE0031C); cases=0; remainder_wins=0
for k in range(16384):
    lux=f32(rng.uniform(-200.0,1400.0))
    safe=f32(10.0**rng.uniform(-1.0,2.4))
    st=f32(10.0**rng.uniform(-1.0,2.4))
    lt=f32(10.0**rng.uniform(-1.0,2.4))
    a=reference(lux,safe,st,lt); b=native((lux,safe,st,lt))
    same_tuple(a,b,('random',k,float(lux),float(safe),float(st),float(lt)))
    if bits(a[6])==bits(long_rem(a[4])) and bits(long_primary(lux,a[5]))!=bits(a[6]):
        remainder_wins+=1
    cases+=1

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('SCOPE=finite-positive ordinary/default AEC arithmetic tail')
print('EDGE_CASES='+str(edge))
print('DIFFERENTIAL_CASES='+str(cases))
print('SHORT_RAMP_1ULP_TRAP=input0x3fbe7879 output0x3fbe787a')
print('LONG_EQUAL_CHILD_1ULP_TRAP=darkboost0x3f8ccccc child0x3f8ccccd')
print('FULL_LONG_MIN_BRANCH=implemented')
print('RANDOM_REMAINDER_BRANCH_WINS='+str(remainder_wins))
print('NATIVE_AEC_TAIL_MATCH=bit-exact')
print('CC_VERIFY=PASS')
