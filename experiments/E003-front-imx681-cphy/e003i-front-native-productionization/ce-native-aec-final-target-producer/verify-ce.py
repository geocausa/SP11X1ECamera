#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, math, random, struct, subprocess, tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
BY=BASE/'by-native-aec-method11-point-aggregation'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

# Required semantic/native ancestry: BX reduction, BY method11, BZ Safe identity,
# CC native tail and CD effective Short/Long weights.
for commit in ['7bb370f','11ededf','5258e86','e6d9e55','64572b7']:
    assert subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=REPO).returncode==0,commit
for p,marker in [
    (BY/'VERIFY-RESULT.txt','BY_VERIFY=PASS'),
    (CC/'VERIFY-RESULT.txt','CC_VERIFY=PASS'),
    (BASE/'cd-windows-aec-final-aggregator-effective-weights'/'VERIFY-RESULT.txt','CD_VERIFY=PASS')]:
    assert marker in p.read_text(),(p,marker)


def f32(x): return np.float32(x)
def bits(x): return struct.unpack('<I',struct.pack('<f',float(f32(x))))[0]
def add(a,b): return f32(f32(a)+f32(b))
def sub(a,b): return f32(f32(a)-f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b):
    with np.errstate(all='ignore'):
        return f32(f32(a)/f32(b))
def absv(a): return np.abs(f32(a),dtype=np.float32)
EPS=np.frombuffer(struct.pack('<I',0x33d6bf95),dtype=np.float32)[0]
SHARED=np.frombuffer(struct.pack('<I',0x3a83126f),dtype=np.float32)[0]

# Independent point specialization of Windows method 11 (BY instruction order).
def method11(points):
    pts=[(f32(v),f32(w)) for v,w in points]
    boundaries=[]
    for v,w in pts:
        if w > f32(0): boundaries.extend((v,v))
    boundaries.extend((f32(0),f32(256)))
    boundaries=sorted(boundaries,key=float)
    best=f32(-1); best_metric=f32(100000)
    for lower,upper in zip(boundaries,boundaries[1:]):
        if absv(sub(lower,upper)) < EPS: continue
        sw=f32(0); swv=f32(0)
        for v,w in pts:
            if absv(w) < EPS: continue
            if upper <= v:
                sw=add(sw,w); swv=add(swv,mul(w,v))
            if lower >= v:
                sw=add(sw,w); swv=add(swv,mul(w,v))
        avg=div(swv,sw); c=avg
        if c < lower: c=lower
        if upper < c: c=upper
        metric=absv(sub(mul(c,sw),swv))
        if metric < best_metric:
            best=c; best_metric=metric
    return f32(best)

# Independent CC arithmetic tail model.
def lerp(lo,hi,t):
    t=f32(t); omt=sub(1,t)
    return add(mul(lo,omt),mul(hi,t))
def cap(lux):
    lux=f32(lux); v16=np.frombuffer(struct.pack('<I',0x3fcccccd),dtype=np.float32)[0]; v14=np.frombuffer(struct.pack('<I',0x3fb33333),dtype=np.float32)[0]
    if lux <= f32(210): return f32(v16)
    if lux < f32(260): return lerp(v16,1.5,div(sub(lux,210),50))
    if lux <= f32(300): return f32(1.5)
    if lux < f32(320): return lerp(1.5,v14,div(sub(lux,300),20))
    return f32(v14)
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
def long_rem(r):
    r=f32(r)
    if r <= f32(1): return f32(1)
    if r < f32(64): return lerp(1,64,div(sub(r,1),63))
    return f32(64)
def tail(lux,safe,st,lt):
    c=cap(lux); ars=div(safe,st); ag=short_ramp(ars)
    if c < ag: ag=c
    short=div(safe,ag); rem=div(8,ag); arl=div(lt,safe)
    p=long_primary(lux,arl); rr=long_rem(rem); db=p if p < rr else rr
    return (c,ars,ag,short,rem,arl,db,mul(safe,db))

def reference(lux,cands):
    safe=method11(cands[:6])
    st=method11([(safe,SHARED),cands[6]])
    lt=method11([(safe,SHARED),cands[7]])
    assert safe > 0 and st > 0 and lt > 0
    return (safe,safe,st,lt)+tail(lux,safe,st,lt)

# Compile the three native production primitives as one test DSO.
tmp=Path(tempfile.mkdtemp(prefix='e003i-ce-')); so=tmp/'ce.so'
cmd=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off',
     str(HERE/'native-final-target.c'),str(BY/'native-target-aggregate.c'),str(CC/'native-aec-tail.c'),
     '-I',str(HERE),'-I',str(BY),'-I',str(CC),'-lm','-o',str(so)]
subprocess.run(cmd,check=True)
lib=ctypes.CDLL(str(so))
class Cand(ctypes.Structure): _fields_=[('value',ctypes.c_float),('confidence',ctypes.c_float)]
class In(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('frame',Cand),('sat_prev',Cand),('dark_prev',Cand),
              ('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),
              ('short_sat_prev',Cand),('long_dark_prev',Cand)]
class Tail(ctypes.Structure):
    _fields_=[('adrc_lux_cap',ctypes.c_float),('adj_ratio_short',ctypes.c_float),
              ('adrc_gain',ctypes.c_float),('short_adj_ratio',ctypes.c_float),
              ('drc_gain_remainder',ctypes.c_float),('adj_ratio_long',ctypes.c_float),
              ('dark_boost_gain',ctypes.c_float),('long_adj_ratio',ctypes.c_float)]
class Out(ctypes.Structure):
    _fields_=[('safe_target',ctypes.c_float),('safe_adj_ratio',ctypes.c_float),
              ('short_target',ctypes.c_float),('long_target',ctypes.c_float),('tail',Tail)]
lib.e003i_aec_default_final_targets.argtypes=[ctypes.POINTER(In),ctypes.POINTER(Out)]
lib.e003i_aec_default_final_targets.restype=ctypes.c_int
names=['safe_target','safe_adj_ratio','short_target','long_target']+[x for x,_ in Tail._fields_]

def native(lux,cands):
    i=In(); i.lux_index=float(f32(lux))
    fields=['frame','sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev']
    for n,(v,w) in zip(fields,cands): setattr(i,n,Cand(float(f32(v)),float(f32(w))))
    o=Out(); rc=lib.e003i_aec_default_final_targets(ctypes.byref(i),ctypes.byref(o)); assert rc==0,rc
    vals=[o.safe_target,o.safe_adj_ratio,o.short_target,o.long_target]
    vals += [getattr(o.tail,n) for n,_ in Tail._fields_]
    return tuple(f32(x) for x in vals)
def same(a,b,tag):
    aa=[bits(x) for x in a]; bb=[bits(x) for x in b]
    assert aa==bb,(tag,aa,bb,[float(x) for x in a],[float(x) for x in b])

# API failure behavior.
o=Out(); good=In(); good.lux_index=0
assert lib.e003i_aec_default_final_targets(None,ctypes.byref(o))==-1
assert lib.e003i_aec_default_final_targets(ctypes.byref(good),None)==-1
good.lux_index=float('nan'); assert lib.e003i_aec_default_final_targets(ctypes.byref(good),ctypes.byref(o))==-2

# BY's weighted-mean trap survives through the composed producer when all
# other Safe confidences and the dedicated confidences are zero.
trap_v=f32(196.64300537109375); trap_w=f32(0.010494260117411613)
trap_c=[(trap_v,trap_w)]+[(50,0)]*5+[(100,0),(120,0)]
a=reference(0,trap_c); b=native(0,trap_c); same(a,b,'method11-trap')
assert bits(a[0])==0x4344a49c and bits(a[1])==0x4344a49c

# Deterministic edge matrix over Lux transition points and confidence zeros.
edge=0
for lux in [-100,0,210,235,260,300,310,320,340,360,1000,1200]:
    for scale in [0.25,1.0,4.0,32.0,128.0,255.0]:
        c=[
            (f32(scale),f32(1.0)),
            (f32(scale*0.8+1),f32(0.0)),
            (f32(scale*0.6+2),f32(0.2)),
            (f32(scale*0.9+3),f32(0.7)),
            (f32(min(255,scale*1.1+4)),f32(0.01)),
            (f32(min(255,scale*0.7+5)),f32(1.3)),
            (f32(min(255,scale*0.5+6)),f32(0.0)),
            (f32(min(255,scale*1.2+7)),f32(0.5)),
        ]
        same(reference(lux,c),native(lux,c),('edge',lux,scale)); edge+=1

# Broad ordinary finite corpus. Safe has at least one positive confidence;
# dedicated weights may be zero because the CD-proven shared 0.001 remains.
rng=random.Random(0xE0031D); cases=0
for k in range(8192):
    lux=f32(rng.uniform(-200,1400)); c=[]
    for j in range(8):
        v=f32(rng.uniform(0.05,255.5))
        if j==0: w=f32(rng.uniform(0.0005,2.0))
        else: w=f32(0.0 if rng.random()<0.18 else rng.uniform(0.0005,2.0))
        c.append((v,w))
    same(reference(lux,c),native(lux,c),('random',k,float(lux))); cases+=1

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('SAFE_ACTIVE_ORDER=Frame,SatPrev,DarkPrev,Brighten,ExtremeColor,Illuminance')
print('SHORT_POINTS=SafeAdjRatio@0.001,ShortSatPrev@confidence')
print('LONG_POINTS=SafeAdjRatio@0.001,LongDarkPrev@confidence')
print('SAFE_ADJRATIO_IDENTITY=3:9=3:8')
print('METHOD11_WEIGHTED_MEAN_TRAP=preserved:0x4344a49c')
print('EDGE_CASES='+str(edge))
print('DIFFERENTIAL_CASES='+str(cases))
print('NATIVE_FINAL_TARGET_PRODUCER_MATCH=bit-exact')
print('CE_VERIFY=PASS')
