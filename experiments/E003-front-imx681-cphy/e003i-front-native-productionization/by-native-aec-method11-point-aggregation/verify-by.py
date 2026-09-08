#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, math, random, struct, subprocess, sys, tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
MAX_POINTS=11
EPS_BITS=0x33d6bf95
EPS=np.frombuffer(struct.pack('<I',EPS_BITS),dtype=np.float32)[0]

assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)

def need(t,*xs):
    for x in xs:
        assert x in t,x

def f32(x): return np.float32(x)
def add(a,b): return np.float32(np.float32(a)+np.float32(b))
def sub(a,b): return np.float32(np.float32(a)-np.float32(b))
def mul(a,b): return np.float32(np.float32(a)*np.float32(b))
def div(a,b):
    with np.errstate(all='ignore'):
        return np.float32(np.float32(a)/np.float32(b))
def absv(a): return np.abs(np.float32(a),dtype=np.float32)
def bits(a): return struct.unpack('<I',struct.pack('<f',float(np.float32(a))))[0]

# Retain the exact default SafeAgg candidate reduction and BV topology fresh.
fresh('bx-windows-aec-default-safe-candidate-zero-state','verify-bx.py','BX_VERIFY=PASS')

# Arithmetic SceneAnalyzer publication duplicates one scalar into [value,value]
# before calling SetDataSceneAnalyzer.
pub=dis(0x1803efe00,0x1803efe30)
need(pub,
     '1803efe18:', 'stp\ts16, s16, [sp, #0x64]',
     '1803efe28:', 'bl\t0x1803d64f8')

# Type-0 target calculators take the direct bank read branch.  Bank-3 reads
# copy the two floats at slot +4/+8 verbatim to the calculator result.
calc=dis(0x1803f1098,0x1803f11d0)
need(calc,
     '1803f10b4:', 'ldr\tw8, [x20]',
     '1803f10b8:', 'cbz\tw8, 0x1803f11b8',
     '1803f11c8:', 'ldr\tx0, [x8, #0x10]',
     '1803f11cc:', 'bl\t0x1803d5d30')
get=dis(0x1803d5d98,0x1803d5dd0)
need(get,
     '1803d5da4:', 'mov\tx10, #0x18',
     '1803d5dac:', 'mov\tx8, #0x7d0c',
     '1803d5db4:', 'ldr\ts16, [x9, x8]',
     '1803d5db8:', 'str\ts16, [x21]',
     '1803d5dc8:', 'ldr\ts16, [x8, x0]',
     '1803d5dcc:', 'str\ts16, [x21, #0x4]')

# Method 11 instruction anchors: positive-weight boundary filter, appended
# 0/256, sorted interval scan, exact separate multiply/add accumulation,
# division, clamp, fabs metric and duplicated result.
m11=dis(0x1803f0978,0x1803f0b78)
need(m11,
     '1803f099c:', 'ldr\ts16, [x8, x27]',
     '1803f09a0:', 'fcmpe\ts16, #0.0',
     '1803f09a4:', 'b.le\t0x1803f0a08',
     '1803f0a48:', 'ldr\ts16, 0x1803f0ccc',
     '1803f0a50:', 'str\ts16, [x29, #0x10]',
     '1803f0a88:', 'bl\t0x1803f1f40',
     '1803f0abc:', 'fsub\ts16, s19, s18',
     '1803f0ae4:', 'ldr\ts21, [x10], #0x4',
     '1803f0b0c:', 'fmul\ts20, s21, s20',
     '1803f0b10:', 'fadd\ts17, s21, s17',
     '1803f0b14:', 'fadd\ts16, s20, s16',
     '1803f0b3c:', 'fdiv\ts20, s16, s17',
     '1803f0b50:', 'fmul\ts17, s12, s17',
     '1803f0b54:', 'fsub\ts0, s17, s16',
     '1803f0b58:', 'bl\t0x1800cc200',
     '1803f0b74:', 'stp\ts10, s10, [x8]')
mathwrap=dis(0x1800cc200,0x1800cc224); need(mathwrap,'1800cc214:','bl\t0x180cf53d0')
fabsfn=dis(0x180cf53d0,0x180cf53d8); need(fabsfn,'fabs\ts0, s0')

# Literal pool identities at 0x1803f0cc8: epsilon, 256, 100000, 255.
image=DLL.read_bytes(); raw_off=0x400+(0x3f0cc8-0x1000)
assert struct.unpack_from('<4I',image,raw_off)==(EPS_BITS,0x43800000,0x47c35000,0x437f0000)

# Independent point specialization of the instruction sequence above.
def reference(points):
    boundaries=[]
    for value,weight in points:
        value=f32(value); weight=f32(weight)
        if weight > f32(0.0):
            boundaries.extend((value,value))
    boundaries.extend((f32(0.0),f32(256.0)))
    boundaries=sorted(boundaries,key=float)
    best=f32(-1.0); best_metric=f32(100000.0)
    for lower,upper in zip(boundaries,boundaries[1:]):
        lower=f32(lower); upper=f32(upper)
        if absv(sub(lower,upper)) < EPS:
            continue
        sw=f32(0.0); swv=f32(0.0)
        for value,weight in points:
            value=f32(value); weight=f32(weight)
            if absv(weight) < EPS:
                continue
            if upper <= value:
                sw=add(sw,weight); swv=add(swv,mul(weight,value))
            if lower >= value:
                sw=add(sw,weight); swv=add(swv,mul(weight,value))
        avg=div(swv,sw)
        candidate=avg
        if candidate < lower: candidate=lower
        if upper < candidate: candidate=upper
        metric=absv(sub(mul(candidate,sw),swv))
        if metric < best_metric:
            best=candidate; best_metric=metric
    return f32(best)

# Compile the actual native source under strict float semantics.
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
tmp=Path(tempfile.mkdtemp(prefix='e003i-by-')); so=tmp/'by.so'
subprocess.run(cc+[str(HERE/'native-target-aggregate.c'),'-I',str(HERE),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))
class Point(ctypes.Structure): _fields_=[('value',ctypes.c_float),('weight',ctypes.c_float)]
lib.e003i_method11_point_aggregate.argtypes=[ctypes.POINTER(Point),ctypes.c_size_t,ctypes.POINTER(ctypes.c_float)]
lib.e003i_method11_point_aggregate.restype=ctypes.c_int

def native(points):
    arr=(Point*max(1,len(points)))()
    for i,(v,w) in enumerate(points): arr[i].value=float(f32(v)); arr[i].weight=float(f32(w))
    out=ctypes.c_float(123.0)
    rc=lib.e003i_method11_point_aggregate(arr,len(points),ctypes.byref(out))
    assert rc==0,rc
    return f32(out.value)

# Fail-closed API checks.
out=ctypes.c_float()
assert lib.e003i_method11_point_aggregate(None,1,ctypes.byref(out))==-1
p=(Point*12)()
assert lib.e003i_method11_point_aggregate(p,12,ctypes.byref(out))==-2
p1=(Point*1)(); p1[0].value=float('nan'); p1[0].weight=1.0
assert lib.e003i_method11_point_aggregate(p1,1,ctypes.byref(out))==-3
p1[0].value=1.0; p1[0].weight=float('inf')
assert lib.e003i_method11_point_aggregate(p1,1,ctypes.byref(out))==-3

# Edge cases exercise empty/all-zero, exact epsilon, duplicates, bounds,
# negative weights and values outside the fixed 0..256 anchors.
eps=float(EPS)
edge=[
 [], [(50.0,0.0)], [(50.0,-0.0)], [(50.0,eps/2)], [(50.0,eps)],
 [(50.0,-eps/2)], [(50.0,-eps)], [(0.0,1.0)], [(256.0,1.0)],
 [(-20.0,1.0)], [(300.0,1.0)], [(50.0,1.0),(50.0,2.0)],
 [(10.0,1.0),(250.0,1.0)], [(10.0,-1.0),(250.0,2.0)],
 [(0.0,1.0),(128.0,0.0),(256.0,1.0)],
]
for i,pts in enumerate(edge):
    a=reference(pts); b=native(pts)
    assert bits(a)==bits(b),('edge',i,pts,bits(a),bits(b),float(a),float(b))

# Known one-positive-point case where a weighted-mean shortcut rounds 1 ULP
# high while Windows' interval clamp returns the original endpoint exactly.
trap_v=f32(196.64300537109375); trap_w=f32(0.010494260117411613)
trap=reference([(trap_v,trap_w)])
mean_shortcut=div(mul(trap_v,trap_w),trap_w)
assert bits(trap)==bits(trap_v)==0x4344a49c,(bits(trap),bits(trap_v))
assert bits(mean_shortcut)==0x4344a49d,bits(mean_shortcut)
assert bits(native([(trap_v,trap_w)]))==bits(trap)

# Deterministic differential corpus. Values are bounded to normal AEC-like
# magnitudes while weights include zeros, sub-epsilon values and negatives.
rng=random.Random(0xE0031B); cases=0
special_v=[-64.0,-1.0,-0.0,0.0,1.0,50.0,128.0,255.0,256.0,300.0,400.0]
special_w=[-2.0,-1.0,-eps,-eps/2,-0.0,0.0,eps/2,eps,0.001,0.01,0.1,1.0,2.0]
for k in range(32768):
    n=rng.randrange(0,MAX_POINTS+1); pts=[]
    for j in range(n):
        if rng.random()<0.30: v=f32(rng.choice(special_v))
        else: v=f32(rng.uniform(-80.0,420.0))
        if rng.random()<0.40: w=f32(rng.choice(special_w))
        else: w=f32(rng.uniform(-2.0,3.0))
        # Frequent exact duplicate endpoints exercise duplicate-boundary skip.
        if j and rng.random()<0.12: v=pts[rng.randrange(j)][0]
        pts.append((v,w))
    a=reference(pts); b=native(pts)
    assert bits(a)==bits(b),('random',k,[(float(v),float(w)) for v,w in pts],bits(a),bits(b),float(a),float(b))
    cases+=1

print('DLL_SHA256='+DLL_SHA)
print('SCOPE=finite duplicated-point Windows target aggregation method11')
print('SCENE_ANALYZER_PUBLICATION=[value,value]')
print('EPSILON_BITS=0x%08x'%EPS_BITS)
print('FIXED_BOUNDARIES=0,256')
print('EDGE_CASES='+str(len(edge)))
print('DIFFERENTIAL_CASES='+str(cases))
print('WEIGHTED_MEAN_TRAP=method11:0x4344a49c weighted_mean:0x4344a49d')
print('NATIVE_METHOD11_MATCH=bit-exact')
print('BY_VERIFY=PASS')
