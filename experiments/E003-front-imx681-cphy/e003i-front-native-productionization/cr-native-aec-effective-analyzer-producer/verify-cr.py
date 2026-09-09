#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, json, math, struct, subprocess, sys
import numpy as np
import pefile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA
sys.path.insert(0,str(REPO/'tools'))
import qti_parameter_bin as qti


def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,
                      stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)


def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',
                                    f'--stop-address={hex(b)}',str(DLL)],
                                   text=True,stderr=subprocess.DEVNULL)


def line_has(t,addr,*parts):
    key=f'{addr:x}:'
    ls=[x for x in t.splitlines() if key in x]
    assert len(ls)==1,(hex(addr),ls)
    for p in parts:
        assert p in ls[0],(hex(addr),p,ls[0])


def f32(x): return np.float32(x)
def bits(x): return struct.unpack('<I',struct.pack('<f',float(f32(x))))[0]
def same(a,b): return bits(a)==bits(b)
def fadd(a,b): return f32(f32(a)+f32(b))
def fsub(a,b): return f32(f32(a)-f32(b))
def fmul(a,b): return f32(f32(a)*f32(b))
def fdiv(a,b): return f32(f32(a)/f32(b))
def lerp(lo,hi,t):
    omt=fsub(f32(1.0),t)
    return fadd(fmul(lo,omt),fmul(hi,t))
def interp(x,regions):
    x=f32(x); r=[(f32(a),f32(b),f32(v)) for a,b,v in regions]
    if x <= r[0][0]: return r[0][2]
    for i,(a,b,v) in enumerate(r):
        if x <= b: return v
        if i+1<len(r) and x < r[i+1][0]:
            na,nb,nv=r[i+1]
            return lerp(v,nv,fdiv(fsub(x,b),fsub(na,b)))
    return r[-1][2]

# Keep the current composed native chain joined to CR.
fresh('ce-native-aec-final-target-producer','verify-ce.py','CE_VERIFY=PASS')
fresh('cm-native-aec-self-fed-lux-framesa','verify-cm.py','CM_VERIFY=PASS')
fresh('cj-windows-aec-source-s1-history-provenance','verify-cj.py','CJ_VERIFY=PASS')
fresh('ck-windows-aec-preview-history-delay','verify-ck.py','CK_VERIFY=PASS')
fresh('bw-windows-aec-default-stats-dependency-map','verify-bw.py','BW_VERIFY=PASS')
fresh('bz-windows-aec-final-adjratio-publication','verify-bz.py','BZ_VERIFY=PASS')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def comp(aid,off): return recs[aid][off:off+8]
def calcs(ref,count):
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==count*72
    return [struct.unpack('<18I',b[i*72:(i+1)*72]) for i in range(count)]
def ops(aid):
    r=recs[aid]; b=bytes.fromhex(ids[r[32]]['raw_hex']); assert len(b)==r[31]*208
    return [struct.unpack('<52I',b[i*208:(i+1)*208]) for i in range(r[31])]
def operand(o,k): return o[3+11*k:3+11*(k+1)]
def direct(x,bank,data,selector=None):
    ok=x[0]==1 and x[2:4]==(bank,data)
    return ok if selector is None else ok and x[10]==selector
def fixed(x,val): return x[0]==0 and bits(struct.unpack('<f',struct.pack('<I',x[1]))[0])==bits(val)
def method2(x,ob,od,ib,id_,ref): return x[0]==2 and x[4:8]==(ob,od,ib,id_) and x[9]==ref

def trig1(ref):
    e=ids[ref]; assert e['name']=='trigger1Data'; b=bytes.fromhex(e['raw_hex']); assert len(b)%16==0
    return [struct.unpack_from('<ffII',b,16*i) for i in range(len(b)//16)]
def scalar_leaf(ref):
    e=ids[ref]; assert e['name']=='trigger2Data'; b=bytes.fromhex(e['raw_hex']); assert len(b)%12==0
    return [struct.unpack_from('<fff',b,12*i) for i in range(len(b)//12)]
def pair_leaf(ref):
    e=ids[ref]; assert e['name']=='trigger2Data'; b=bytes.fromhex(e['raw_hex']); assert len(b)%16==0
    return [struct.unpack_from('<ffff',b,16*i) for i in range(len(b)//16)]

# Exact default analyzers and only four non-Frame StatsCalculator dependencies.
assert [name(x) for x in (30,31,32,45,35,36,58)] == [
    'SatPrevSA','DarkPrevSA','BrightenImgSA','ExtremeColorSA',
    'ShortSatPrevSA','LongDarkPrevSA','IlluminanceSA']
# Unit layout: method, direct bank/data, outer bank/data, inner bank/data, outer-count, tree-ref.
sat_l=calcs(comp(30,7)[1],1)[0]
dark_l=calcs(comp(31,7)[1],1)[0]
short_l=calcs(comp(35,7)[1],1)[0]
ill_conf=calcs(comp(58,23)[1],2)
assert sat_l[:9] == (0,4,7,19,0,19,0,1,3884)
assert dark_l[:9] == (1,4,8,9,8,4,8,1,3937)
assert short_l[:9] == (0,4,19,19,0,19,0,1,4424)
assert ill_conf[1][:9] == (1,4,6,9,8,4,6,1,6472)
assert {7,8,19,6} == {sat_l[2],dark_l[2],short_l[2],ill_conf[1][2]}

# Three configured active candidates are mathematically dead in DefaultSequence:
# each confidence value tree is scalar +0.0f everywhere, with unit weight 1.
for aid,tree,leaf in [(32,4013,4014),(45,6001,6002),(36,4496,4497)]:
    cc=calcs(comp(aid,23)[1],1)[0]
    assert cc[0]==1 and cc[8]==tree
    rows=scalar_leaf(leaf)
    assert rows and all(bits(v)==0 for _,_,v in rows),(name(aid),rows)

# Live component trees, exact tuning identities.
assert pair_leaf(3891)==[(0.0,160.0,0.0,220.0),(180.0,260.0,0.0,210.0),
                         (300.0,360.0,0.0,200.0),(440.0,480.0,0.0,140.0),
                         (500.0,1000.0,0.0,90.0)]
assert [bits(v) for _,_,v in scalar_leaf(3897)] == [bits(x) for x in (.5,.5,.5,.3,.1)]
assert pair_leaf(3944)==[(0.0,270.0,11.0,256.0),(300.0,360.0,9.0,256.0),
                         (380.0,460.0,9.0,256.0),(480.0,1000.0,4.0,256.0)]
assert [bits(v) for _,_,v in scalar_leaf(3950)] == [bits(x) for x in (.2,.15,.18,.2)]
assert pair_leaf(4431)==[(0.0,190.0,0.0,165.0),(240.0,290.0,0.0,175.0),
                         (340.0,1000.0,0.0,190.0)]
assert all(bits(v)==bits(1.0) for _,_,v in scalar_leaf(4437))
assert pair_leaf(6481)[0][0:2] == (f32(10.989370346069336),f32(10.989370346069336))
assert bits(pair_leaf(6481)[0][2])==0x3d0eb463 and bits(pair_leaf(6481)[0][3])==0x3d0eb463
assert [tuple(bits(v) if j==2 else f32(v) for j,v in enumerate(r)) for r in scalar_leaf(6469)] == [
    (f32(0),f32(.5),bits(2.0)),(f32(.5),f32(100),bits(0.0))]
assert [bits(v) for _,_,v in scalar_leaf(6473)] == [bits(0.0),bits(5.0)]
assert [bits(r[2]) for r in pair_leaf(6508)] == [bits(1.4),bits(1.2)]

# Arithmetic topology used by the native formulas.
sop=ops(30); dop=ops(31); shop=ops(35); iop=ops(58)
# DIV computes (A*B)/(C*D); target selector 2 is target-high.
assert sop[0][:3]==(1,1,3) and direct(operand(sop[0],0),3,15,2) and direct(operand(sop[0],1),3,4,1) and direct(operand(sop[0],2),3,14,1) and direct(operand(sop[0],3),3,5,1)
assert sop[2][:3]==(1,2,3) and method2(operand(sop[2],0),9,8,3,17,3920) and direct(operand(sop[2],1),3,5,1) and direct(operand(sop[2],2),3,4,1)
assert dop[1][:3]==(1,1,3) and direct(operand(dop[1],0),3,20,2)
assert dop[3][:3]==(1,2,3) and method2(operand(dop[3],0),9,8,3,23,3985) and direct(operand(dop[3],1),3,5,1) and direct(operand(dop[3],2),3,4,1)
assert shop[0][:3]==(1,1,3) and direct(operand(shop[0],0),3,57,2)
assert shop[3][:3]==(1,2,3) and method2(operand(shop[3],0),9,8,3,60,4469) and direct(operand(shop[3],1),3,5,1) and direct(operand(shop[3],2),3,4,1)
# Illuminance: (9:28 * factor)/(1e6*1), then FrameTarget/(illumLuma*FrameAdj),
# then final MUL with correction method2 and FrameAdj.
assert iop[0][:3]==(1,0,3) and direct(operand(iop[0],0),9,28,1) and method2(operand(iop[0],1),9,8,9,63,6480) and fixed(operand(iop[0],2),1000000.0) and fixed(operand(iop[0],3),1.0)
assert iop[1][:3]==(1,1,3) and direct(operand(iop[1],0),3,226,1) and direct(operand(iop[1],2),3,225,1) and direct(operand(iop[1],3),3,7,1)
assert iop[3][:3]==(1,2,2) and direct(operand(iop[3],0),3,228,1) and method2(operand(iop[3],1),9,8,3,228,6507) and direct(operand(iop[3],2),3,7,1)

# Runtime calculator grammar: method0 direct DB read, method1 two-coordinate interpolation.
rc=dis(0x1803f10b0,0x1803f1310)
line_has(rc,0x1803f10b4,'ldr','w8, [x20]')
line_has(rc,0x1803f10c0,'b.eq','0x1803f1134')
line_has(rc,0x1803f1158,'add','x1, x20, #0x10')
line_has(rc,0x1803f1160,'bl','0x1803d5d30')
line_has(rc,0x1803f1188,'add','x1, x20, #0x18')
line_has(rc,0x1803f1190,'bl','0x1803d5d30')
line_has(rc,0x1803f11a8,'bl','0x1803acf40')
line_has(rc,0x1803f11c4,'add','x1, x20, #0x4')
line_has(rc,0x1803f11cc,'bl','0x1803d5d30')
# Component aggregation method3 is lane-wise minimum.
image=DLL.read_bytes(); pe=pefile.PE(str(DLL),fast_load=True)
def off_va(va): return pe.get_offset_from_rva(va-pe.OPTIONAL_HEADER.ImageBase)
rels=struct.unpack_from('<13i',image,off_va(0x1803f0c94))
targets=[0x1803f07a8+r*4 for r in rels]
assert targets[3]==0x1803f068c,hex(targets[3])
mn=dis(0x1803f068c,0x1803f06e8)
line_has(mn,0x1803f06b8,'fcmpe','s18, s17')
line_has(mn,0x1803f06bc,'b.hs','0x1803f06c8')
line_has(mn,0x1803f06c0,'str','s18, [x19, #0x138]')
# Bank9 scalar geometry: slot=dataID*16 + 0xC.
b9=dis(0x1803d5f84,0x1803d5fb4)
line_has(b9,0x1803d5f90,'add','x8, x0, w8, sxtw #4')
line_has(b9,0x1803d5f98,'ldr','s16, [x8, #0xc]')
# 9:28 is selected retained-history Short converted uint64 -> f32 and published.
hp=dis(0x1803e3b90,0x1803e3bf0)
line_has(hp,0x1803e3b94,'ldr','x8, [x19, #0x28]')
line_has(hp,0x1803e3b98,'mov','x9, #0x1c')
line_has(hp,0x1803e3bb4,'ucvtf','s16, x8')
line_has(hp,0x1803e3bec,'bl','0x1803d6700')

# Same-machine Windows oracle: ordinary front path reads 9:63 as exact +0 and
# no hardware-watch write is observed from first read through Stop/Dispose.
OD=HERE/'windows-oracle'
banklog=OD/'E003I-CR63-bank9-cdb_1e5c_2026-09-09_08-15-00-316.log'
holder=OD/'E003I-CR63C-holder.log'
manifest=OD/'E003I-CR63-ORACLE-MANIFEST.txt'
assert hashlib.sha256(banklog.read_bytes()).hexdigest()=='a6bbc52f1b64d2a23070bf96dc27482c3f97b87434bc892c94fa32c452ee4fad'
assert hashlib.sha256(holder.read_bytes()).hexdigest()=='7d5a625b8b2ca8e93ab6c93a39311ba93058bc4650f9659b69a819f9eb427928'
blines=banklog.read_text(errors='replace').splitlines()
assert any(x.strip()=='CR63_BANK9_READ' for x in blines)
assert any('SLOT63=0000023e19cde43c' in x for x in blines)
# The only CR63_BANK9_WRITE occurrence is inside the breakpoint command itself.
assert sum('CR63_BANK9_WRITE' in x for x in blines)==1
idx=next(i for i,x in enumerate(blines) if x.strip()=='SLOT63_BITS')
assert '00000000' in blines[idx+1]
holder_text=holder.read_text(encoding='utf-16')
assert 'START_STATUS=Success' in holder_text and 'STOP_PASS' in holder_text
mt=manifest.read_text(errors='replace')
assert 'Observed 9:63 bits=00000000 (+0.0f)' in mt
assert 'Hardware watchpoint on SLOT63 saw no write' in mt

# Independent float32 reference model.
SAT_T=[(0,160,220),(180,260,210),(300,360,200),(440,480,140),(500,1000,90)]
SAT_C=[(0,160,.5),(180,260,.5),(300,360,.5),(440,480,.3),(500,1000,.1)]
DARK_T=[(0,270,256),(300,360,256),(380,460,256),(480,1000,256)]
DARK_C=[(0,270,.2),(300,360,.15),(380,460,.18),(480,1000,.2)]
SHORT_T=[(0,190,165),(240,290,175),(340,1000,190)]
SHORT_C=[(0,190,1),(240,290,1),(340,1000,1)]

def inner_floor(x,floor): return interp(x,[(0,floor,floor),(256,256,256)])
def sat_m2(lux,x):
    vals=[inner_floor(x,v) for v in [f32(.8),f32(.65),f32(.6),f32(.55),f32(.45)]]
    return interp(lux,[(0,160,vals[0]),(180,260,vals[1]),(300,360,vals[2]),(440,480,vals[3]),(500,1000,vals[4])])
def ident(x): return interp(x,[(0,0,0),(256,256,256)])
def dark_m2(lux,x):
    v=ident(x); return interp(lux,[(0,270,v),(300,360,v),(380,460,v),(480,1000,v)])
def short_m2(lux,x):
    v=ident(x); return interp(lux,[(0,190,v),(240,290,v),(340,1000,v)])
def model(vals):
    lux,fl,ft,shortq,sr,s7,s8,s19=vals
    lux=f32(lux); fl=f32(fl); ft=f32(ft); sr=f32(sr); s7=f32(s7); s8=f32(s8); s19=f32(s19)
    fa=fdiv(ft,fl)
    sat_t=interp(lux,SAT_T); ratio=fdiv(fmul(sat_t,fl),fmul(s7,ft)); sm=sat_m2(lux,ratio); sat=fdiv(fmul(sm,ft),fl)
    dl=interp(s8,[(0,.25,.25),(255,255,255)]); dt=interp(lux,DARK_T); ratio=fdiv(fmul(dt,fl),fmul(dl,ft)); dm=dark_m2(lux,ratio); dark=fdiv(fmul(dm,ft),fl)
    shortf=f32(int(shortq)); il=fdiv(fmul(shortf,f32(struct.unpack('<f',struct.pack('<I',0x3d0eb463))[0])),f32(1000000.0)); ir=fdiv(ft,fmul(il,fa)); cor=interp(ir,[(0,.25,1.4),(.5,1,1.2)]); illum=fmul(fmul(ir,cor),fa)
    ca=interp(fa,[(0,.5,2),(.5,100,0)]); cb=interp(sr,[(0,.5,0),(.8,1,5)]); ic=ca if ca<cb else cb
    st=interp(lux,SHORT_T); ratio=fdiv(fmul(st,fl),fmul(s19,ft)); mm=short_m2(lux,ratio); sh=fdiv(fmul(mm,ft),fl)
    return [lux,(fa,f32(struct.unpack('<f',struct.pack('<I',0x3a83126f))[0])),
            (sat,interp(lux,SAT_C)),(f32(0),f32(0)), # dark inserted below
            (f32(0),f32(0)),(illum,f32(ic)),(sh,interp(lux,SHORT_C)),(f32(0),f32(0))], dark, interp(lux,DARK_C)

class Cand(ctypes.Structure): _fields_=[('value',ctypes.c_float),('confidence',ctypes.c_float)]
class Final(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('frame',Cand),('sat_prev',Cand),('dark_prev',Cand),
              ('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),
              ('short_sat_prev',Cand),('long_dark_prev',Cand)]
class Raw(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('frame_luma',ctypes.c_float),('frame_target',ctypes.c_float),
              ('delayed_short_exposure',ctypes.c_uint64),('saturate_stats_ratio',ctypes.c_float),
              ('sat_prev_high_pctl_luma',ctypes.c_float),('dark_prev_low_pctl_luma',ctypes.c_float),
              ('short_sat_prev_high_pctl_luma',ctypes.c_float)]

lib=Path('/tmp/libe003i-cr.so')
incs=[BASE/'ce-native-aec-final-target-producer',BASE/'cc-native-aec-adrc-darkboost-tail']
cmd=['gcc','-std=c11','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
for x in incs: cmd += ['-I',str(x)]
cmd += [str(HERE/'native-effective-analyzers.c'),'-lm','-o',str(lib)]
subprocess.check_call(cmd)
so=ctypes.CDLL(str(lib)); fn=so.e003i_aec_default_effective_analyzers
fn.argtypes=[ctypes.POINTER(Raw),ctypes.POINTER(Final)]; fn.restype=ctypes.c_int

def flat_native(o):
    return [o.lux_index,(o.frame.value,o.frame.confidence),(o.sat_prev.value,o.sat_prev.confidence),
            (o.dark_prev.value,o.dark_prev.confidence),(o.brighten.value,o.brighten.confidence),
            (o.extreme_color.value,o.extreme_color.confidence),(o.illuminance.value,o.illuminance.confidence),
            (o.short_sat_prev.value,o.short_sat_prev.confidence),(o.long_dark_prev.value,o.long_dark_prev.confidence)]
def check(v):
    r=Raw(f32(v[0]),f32(v[1]),f32(v[2]),int(v[3]),f32(v[4]),f32(v[5]),f32(v[6]),f32(v[7])); o=Final(); rc=fn(ctypes.byref(r),ctypes.byref(o)); assert rc==0,(rc,v)
    ref,dark,dc=model(v); ref.insert(3,(dark,dc))
    got=flat_native(o)
    assert len(got)==len(ref)==9
    assert bits(got[0])==bits(ref[0]),('lux',v,got[0],ref[0])
    for i in range(1,9):
        for j in range(2):
            assert bits(got[i][j])==bits(ref[i][j]),(i,j,v,hex(bits(got[i][j])),hex(bits(ref[i][j])),got[i],ref[i])

lux_edges=[0,1,159.99,160,170,179.99,180,259.99,260,280,299.99,300,359.99,360,370,379.99,380,439.99,440,459.99,460,470,479.99,480,499.99,500,999.9,1000]
dark_edges=[.01,.1,.25,.2501,1,127,254.9,255]
sr_edges=[0,.49,.5,.5001,.65,.7999,.8,1,1.2]
for i,lux in enumerate(lux_edges):
    check((lux, f32(.55+(i%8)*.3), f32(30+(i%6)*5), 33333332-(i%7)*12345,
           sr_edges[i%len(sr_edges)], f32(40+(i*7)%180), dark_edges[i%len(dark_edges)], f32(50+(i*11)%190)))
rng=np.random.default_rng(0xC0DE)
for _ in range(8192):
    check((f32(rng.uniform(0,1000)),f32(rng.uniform(.5,80)),f32(rng.uniform(30,55)),
           int(rng.integers(1_000_000,33_333_333)),f32(rng.uniform(0,1.2)),
           f32(rng.uniform(.25,255)),f32(rng.uniform(.01,255)),f32(rng.uniform(.25,255))))

# Invalid-domain guard smoke tests.
o=Final(); assert fn(None,ctypes.byref(o))==-1
bad=Raw(100,0,40,33333332,.5,100,100,100); assert fn(ctypes.byref(bad),ctypes.byref(o))==-1

result={
 'dll_sha256':DLL_SHA,'tuning_sha256':TUNING_SHA,
 'effective_stats_bank4':[6,7,8,19],
 'dead_zero_confidence':['BrightenImgSA','ExtremeColorSA','LongDarkPrevSA'],
 'trigger_9_28':'selected retained-history Short uint64 converted to float32',
 'trigger_9_63_ordinary_bits':'0x00000000',
 'component_aggregation_method3':'lane-wise minimum',
 'boundary_cases':len(lux_edges),'random_cases':8192,'status':'PASS'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+"\n")
print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('EFFECTIVE_BANK4_STATS=6,7,8,19')
print('DEAD_ZERO_CONF=BrightenImgSA,ExtremeColorSA,LongDarkPrevSA')
print('TRIGGER_9_28=selected retained-history Short -> f32')
print('TRIGGER_9_63_ORDINARY=+0.0f bits=0x00000000')
print('COMPONENT_AGG_METHOD3=lane-wise-min')
print(f'NATIVE_DIFFERENTIAL=boundary:{len(lux_edges)} random:8192 bit-exact')
print('CR_VERIFY=PASS')
