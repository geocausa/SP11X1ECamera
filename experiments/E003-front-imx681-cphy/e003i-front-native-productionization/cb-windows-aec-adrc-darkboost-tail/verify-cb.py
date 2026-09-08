#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess, sys
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
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)

def line_has(t,addr,*parts):
    key=f'{addr:x}:'
    ls=[x for x in t.splitlines() if key in x]
    assert len(ls)==1,(hex(addr),ls)
    for p in parts:
        assert p in ls[0],(hex(addr),p,ls[0])

def f32(x): return np.float32(x)
def fbits(x): return struct.unpack('<I',struct.pack('<f',float(f32(x))))[0]
def same(a,b): return fbits(a)==fbits(b)
def lerp_win(lo,hi,t):
    # Mirrors CAECX TwoFloats/OneFloat blend order: lo*(1-t) + hi*t.
    t=f32(t); omt=f32(f32(1.0)-t)
    p0=f32(f32(lo)*omt); p1=f32(f32(hi)*t)
    return f32(p0+p1)
def interp_regions(x,regions):
    """Windows-shaped scalar interval interpolation.
    regions = [(start,end,value), ...], sorted, with plateaus in-region and
    linear blending only across gaps. Endpoint clamp outside the table.
    """
    x=f32(x)
    rs=[(f32(a),f32(b),f32(v)) for a,b,v in regions]
    if x <= rs[0][0]: return rs[0][2]
    for i,(a,b,v) in enumerate(rs):
        if x <= b: return v
        if i+1 < len(rs):
            na,nb,nv=rs[i+1]
            if x < na:
                t=f32(f32(x-b)/f32(na-b))
                return lerp_win(v,nv,t)
    return rs[-1][2]

# Preserve the now-closed final arithmetic grammar and default branch choice.
fresh('ca-windows-aec-default-adrc-cap-selection','verify-ca.py','CA_VERIFY=PASS')
# BG independently ties trigger bank (9,8) to the controller LuxIndex path.
fresh('bg-windows-aec-framesa-target-lux','verify-bg.py','BG_VERIFY=PASS')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def ops(aid):
    r=recs[aid]; b=bytes.fromhex(ids[r[32]]['raw_hex']); assert len(b)==r[31]*208
    return [struct.unpack('<52I',b[i*208:(i+1)*208]) for i in range(r[31])]
def operand(o,k): return o[3+11*k:3+11*(k+1)]
def out(o): return o[47:52]
def desc(o): return ids[o[51]]['text']
def fixed(x,v): return x[0]==0 and x[1]==fbits(v)
def db(x,bank,data): return x[0]==1 and x[2:4]==(bank,data)
def method2(x,pbank,pdata,sbank,sdata,ref):
    # Runtime method-2 resolves compact bank2/data2 and bank3/data3 as the two triggers.
    return x[0]==2 and x[4:8]==(pbank,pdata,sbank,sdata) and x[9]==ref

def trig1(ref):
    e=ids[ref]; assert e['name']=='trigger1Data'
    b=bytes.fromhex(e['raw_hex']); assert len(b)%16==0
    rows=[]
    for i in range(len(b)//16):
        a,bb=struct.unpack_from('<ff',b,i*16); n,r=struct.unpack_from('<II',b,i*16+8)
        rows.append((a,bb,n,r))
    return rows
def trig2_scalar(ref):
    e=ids[ref]; assert e['name']=='trigger2Data'
    b=bytes.fromhex(e['raw_hex']); assert len(b)%16==0
    return [struct.unpack_from('<ffff',b,i*16) for i in range(len(b)//16)]

# -------------------------------------------------------------------------
# Trigger-control enum: exact Windows name switch.  BG independently proves
# bank9:data8 is Lux.  For bank9:data14, CB records the enum-name evidence but
# does not require a writer-level identity: the selected outer table has one
# region, so the scoped arithmetic is invariant to that coordinate.
# -------------------------------------------------------------------------
pe=pefile.PE(str(DLL),fast_load=True); image=DLL.read_bytes(); image_base=pe.OPTIONAL_HEADER.ImageBase
def off_va(va): return pe.get_offset_from_rva(va-image_base)
def cstr(va):
    o=off_va(va); e=image.index(b'\0',o); return image[o:e].decode('ascii')
# The signed-byte jump table is indexed by controlID-1 and based at 0x1803ae5f8.
tab=struct.unpack_from('<20b',image,off_va(0x1803ae5f8))
base=0x1803ae5f8
targets=[base+x*4 for x in tab]
assert targets[7]==0x1803ae474 and targets[13]==0x1803ae4bc,(hex(targets[7]),hex(targets[13]))
name_sw=dis(0x1803ae3f0,0x1803ae520)
line_has(name_sw,0x1803ae400,'sub','w8, w21, #0x1')
line_has(name_sw,0x1803ae410,'adr','0x1803ae5f8')
line_has(name_sw,0x1803ae474,'adrp','0x1813b8000')
line_has(name_sw,0x1803ae478,'add','0xc50')
line_has(name_sw,0x1803ae4bc,'adrp','0x1813b8000')
line_has(name_sw,0x1803ae4c0,'add','0xf10')
assert cstr(0x1813b8c50)=='TriggerCtrlLux'
assert cstr(0x1813b8f10)=='TriggerCtrlGyro'

# GetDataTriggers directly indexes dataID*16 and returns slot +8.
gdt=dis(0x1803ae610,0x1803ae658)
line_has(gdt,0x1803ae628,'cmp','w19, #0x3e7')
line_has(gdt,0x1803ae63c,'add','x8, x0, w19, sxtw #4')
line_has(gdt,0x1803ae640,'add','x0, x8, #0x8')

# Method-2 resolves two DB descriptors at runtime operand +0x10/+0x18 and
# evaluates the nested trigger program through the common interpolator.
m2=dis(0x1803ca020,0x1803ca0f4)
line_has(m2,0x1803ca05c,'ldp','[x19, #0x10]')
line_has(m2,0x1803ca080,'add','x1, x19, #0x10')
line_has(m2,0x1803ca084,'bl','0x1803d5d30')
line_has(m2,0x1803ca088,'ldp','[x19, #0x18]')
line_has(m2,0x1803ca0a8,'add','x1, x19, #0x18')
line_has(m2,0x1803ca0ac,'bl','0x1803d5d30')
line_has(m2,0x1803ca0c8,'bl','0x1803acf40')
# The interpolation object preserves coordinate order.  The method-2 helper
# stores current s0/s1 at +0x58/+0x5c, seeds recursion level 0 with current s0,
# and recursive level+1 reloads current coordinates from +(level+0x16)*4.
# Therefore descriptor +0x10 is the outer coordinate and +0x18 the inner one.
ord0=dis(0x1803acf58,0x1803ad024)
line_has(ord0,0x1803acf5c,'fmov','s9, s0')
line_has(ord0,0x1803acf64,'fmov','s11, s1')
line_has(ord0,0x1803acffc,'stp','s9, s11, [x19, #0x58]')
line_has(ord0,0x1803ad018,'ldr','s1, [x19, #0x64]')
line_has(ord0,0x1803ad020,'bl','0x1803ad048')
ord1=dis(0x1803ad194,0x1803ad1bc)
line_has(ord1,0x1803ad194,'add','w1, w20, #0x1')
line_has(ord1,0x1803ad1a4,'add','x9, x8, #0x19')
line_has(ord1,0x1803ad1a8,'add','x8, x8, #0x16')
line_has(ord1,0x1803ad1ac,'ldr','s1, [x19, x9, lsl #2]')
line_has(ord1,0x1803ad1b0,'ldr','s0, [x19, x8, lsl #2]')
line_has(ord1,0x1803ad1b8,'bl','0x1803ad048')
# Recursive interval interpolation computes t and 1-t before the virtual blend.
ip=dis(0x1803ad38c,0x1803ad3c8)
line_has(ip,0x1803ad39c,'fsub','s17, s8, s18')
line_has(ip,0x1803ad3a4,'fsub','s16, s16, s18')
line_has(ip,0x1803ad3a8,'fdiv','s16, s17, s16')
line_has(ip,0x1803ad3ac,'fmov','s17, #1.00000000')
line_has(ip,0x1803ad3b0,'fsub','s0, s17, s16')
# Concrete TwoFloats blend fixes instruction order.
tw=dis(0x1803adac0,0x1803adb20)
line_has(tw,0x1803adaf4,'fsub','s21, s16, s0')
line_has(tw,0x1803adafc,'fmul','s17, s16, s21')
line_has(tw,0x1803adb04,'fmul','s16, s16, s0')
line_has(tw,0x1803adb08,'fadd','s18, s17, s16')

# Enum 5 is MIN(A*B,C*D), exact executor body.
mn=dis(0x1803c9448,0x1803c9468)
line_has(mn,0x1803c9448,'fmul','s15, s12, s11')
line_has(mn,0x1803c9450,'fmul','s9, s14, s13')
line_has(mn,0x1803c9458,'fcmp','s15, s9')
line_has(mn,0x1803c9460,'fcsel','s10, s15, s9, lo')

# -------------------------------------------------------------------------
# Default ADRC cap: CA selects method-2 operand C.  Outer control is Gyro and
# has one 0..1000 region; inner control is Lux and carries the actual curve.
# -------------------------------------------------------------------------
adrc=ops(60)[0]; C=operand(adrc,2)
assert desc(adrc)=='ADRCLuxFaceCap' and method2(C,9,14,9,8,6745)
assert trig1(6745)==[(0.0,1000.0,3,6746)]
cap_rows=trig2_scalar(6746)
assert cap_rows==[(0.0,210.0,np.float32(1.6),np.float32(1.6)),
                  (260.0,300.0,1.5,1.5),
                  (320.0,1000.0,np.float32(1.4),np.float32(1.4))]
cap_regions=[(a,b,v0) for a,b,v0,v1 in cap_rows if same(v0,v1)]

def cap_lux(lux): return interp_regions(lux,cap_regions)
# Wide deterministic sample confirms the nested program collapses to Lux only
# for all finite ordinary Gyro values inside the sole configured outer region.
for lux in [0,1,209.5,210,211,235,259.9,260,299.9,300,310,319.9,320,500,1000]:
    v=cap_lux(lux)
    assert f32(1.399) < v < f32(1.601)

# -------------------------------------------------------------------------
# Short tail.
# -------------------------------------------------------------------------
sop=ops(4); ar_short=sop[0]; gain=sop[1]
assert desc(ar_short)=='AdjRatioShort' and ar_short[:3]==(1,1,3)
assert db(operand(ar_short,0),3,9) and fixed(operand(ar_short,1),1.0)
assert db(operand(ar_short,2),3,10) and fixed(operand(ar_short,3),1.0)
assert out(ar_short)[:2]==(3,66)
assert desc(gain)=='ADRCGain' and gain[:3]==(1,1,5)
A=operand(gain,0); C=operand(gain,2)
assert method2(A,9,8,3,66,3747)
assert db(C,9,54) and fixed(operand(gain,1),1.0) and fixed(operand(gain,3),1.0)
assert trig1(3747)==[(0.0,1000.0,2,3748)]
short_inner=trig2_scalar(3748)
assert short_inner==[(0.0,1.0,1.0,1.0),(1000.0,1000.0,1000.0,1000.0)]
short_regions=[(a,b,v0) for a,b,v0,v1 in short_inner]
# Do NOT algebraically collapse this ramp to clamp(x,1,1000): Windows's
# f32 interpolation order can differ by 1 ULP (the explicit trap below).
def short_ramp(x): return interp_regions(x,short_regions)
assert fbits(short_ramp(f32(123.5)))==0x42f70001
assert fbits(f32(123.5))==0x42f70000
for x in [0,0.5,1,1.25,2,10,123.5,999,1000,1200]:
    got=short_ramp(x)
    assert f32(1.0) <= got <= f32(1000.0)
# cap <=1.6, so the 1000 endpoint is irrelevant after MIN with cap, but the
# Windows interpolation itself remains authoritative in the 1..cap interval.
assert max(float(cap_lux(x)) for x in np.linspace(0,1000,1001,dtype=np.float32)) <= float(f32(1.6))

# -------------------------------------------------------------------------
# Long tail.
# -------------------------------------------------------------------------
lop=ops(5); rem=lop[0]; ar_long=lop[1]; dark=lop[2]
assert desc(rem)=='DRCGainRemainder' and rem[:3]==(1,0,3)
assert fixed(operand(rem,0),8.0) and fixed(operand(rem,1),1.0)
assert db(operand(rem,2),3,67) and fixed(operand(rem,3),1.0)
assert out(rem)[:2]==(3,157)
assert desc(ar_long)=='AdjRatioLong' and ar_long[:3]==(1,1,3)
assert db(operand(ar_long,0),3,12) and fixed(operand(ar_long,1),1.0)
assert db(operand(ar_long,2),3,9) and fixed(operand(ar_long,3),1.0)
assert out(ar_long)[:2]==(3,68)
assert desc(dark)=='DarkBoostGain' and dark[:3]==(1,1,5)
A=operand(dark,0); C=operand(dark,2)
assert method2(A,9,8,3,68,3829)
assert method2(C,9,8,3,157,3835)
assert fixed(operand(dark,1),1.0) and fixed(operand(dark,3),1.0)
assert trig1(3829)==[(0.0,260.0,2,3830),(300.0,320.0,2,3831),(360.0,1000.0,2,3832)]
assert trig2_scalar(3830)==[(0.0,1.0,1.0,1.0),(2.0,1000.0,2.0,2.0)]
assert trig2_scalar(3831)==trig2_scalar(3830)
assert trig2_scalar(3832)==[(0.0,1.0,1.0,1.0),(2.0,1000.0,1.0,1.0)]
assert trig1(3835)==[(0.0,1000.0,2,3836)]
assert trig2_scalar(3836)==[(0.0,1.0,1.0,1.0),(64.0,64.0,64.0,64.0)]

def clamp12(x): return interp_regions(x,[(0,1,1),(2,1000,2)])
def long_A(lux,ratio):
    g=clamp12(ratio)
    # Outer regions 0..260 and 300..320 produce identical g; 360..1000 produces 1.
    return interp_regions(lux,[(0,260,g),(300,320,g),(360,1000,1)])
def long_C(remv): return interp_regions(remv,[(0,1,1),(64,64,64)])

# Do not collapse the 260..300 outer gap even though its child programs are
# numerically identical: Windows still executes lerp(g,g,t), which can move 1 ULP.
trap_lux=f32(260.9975); trap_ratio=f32(1.1)
trap_g=clamp12(trap_ratio); trap_out=long_A(trap_lux,trap_ratio)
assert fbits(trap_g)==0x3f8ccccd
assert fbits(trap_out)==0x3f8ccccc
rng=np.random.default_rng(0xCB)
for lux in list(np.linspace(0,1000,513,dtype=np.float32))+list(rng.uniform(0,1000,4096).astype(np.float32)):
    for ratio in (f32(0.5),f32(1),f32(1.1),f32(1.5),f32(2),f32(4)):
        v=long_A(lux,ratio)
        assert f32(0.999) < v < f32(2.001),(lux,ratio,v)

# Branch dominance under default cap.  ADRCGain is at least 1 and at most cap<=1.6.
# Thus remainder=8/ADRCGain is safely >4.9 while Long A is <=2, so MIN always selects A.
min_remainder=f32(f32(8.0)/f32(1.6))
assert float(min_remainder)>4.9 and same(min_remainder,f32(5.0))
assert max(float(long_A(l,r)) for l in (0,320,340,360,1000) for r in (0,1,1.5,2,10)) <= 2.0
assert float(long_C(min_remainder)) > 4.9

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('TRIGGER_CONTROL_ENUM_8=Lux')
print('TRIGGER_CONTROL_ENUM_14=Gyro')
print('BANK9_DATA14_SCOPE=outer-coordinate-semantic-not-required')
print('DEFAULT_ADRC_CAP=Lux:<=210=1.6;210..260=linear1.6->1.5;260..300=1.5;300..320=linear1.5->1.4;>=320=1.4')
print('SHORT_ADJRATIO=3:66=3:9/3:10')
print('SHORT_ADRCGAIN=3:67=min(WindowsRamp1to1000(3:66),ADRCCap(Lux))')
print('SHORT_RAMP_1ULP_TRAP=input123.5:windows=0x42f70001 direct=0x42f70000')
print('LONG_DRCGAIN_REMAINDER=3:157=8/3:67')
print('LONG_ADJRATIO=3:68=3:12/3:9')
print('LONG_DARKBOOST_REMAINDER_BRANCH=dominated:min_remainder=5.0>max_primary=2.0')
print('LONG_DARKBOOST=3:69=WindowsMethod2(Lux,3:68;tables3829..3832);remainder branch dominated')
print('LONG_EQUAL_ENDPOINT_1ULP_TRAP=lux260.9975 ratio1.1:windows=0x3f8ccccc child=0x3f8ccccd')
print('CB_VERIFY=PASS')
