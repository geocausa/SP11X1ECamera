#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess, sys

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
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)

def need(t,*xs):
    for x in xs: assert x in t,x

# Retain narrowed consumer + downstream joins fresh.
fresh('bu-native-aec-zero-delta-preview-profile','verify-bu.py','BU_VERIFY=PASS')
fresh('bd-windows-aec-target-analyzer-si','verify-bd.py','BD_VERIFY=PASS')
fresh('bf-windows-aec-metering-convergence-join','verify-bf.py','BF_VERIFY=PASS')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
a=ids[3592]; assert a['name']=='analyzers' and a['payload_size']==52*0x8c
raw=bytes.fromhex(a['raw_hex'])
recs={}
for i in range(52):
    w=struct.unpack('<35I',raw[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def comp(aid,off): return recs[aid][off:off+8]
def calcs(ref,count):
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==count*72
    return [struct.unpack('<18I',b[i*72:(i+1)*72]) for i in range(count)]
def ops(aid):
    r=recs[aid]; n,ref=r[31],r[32]; b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*208
    return [struct.unpack('<52I',b[i*208:(i+1)*208]) for i in range(n)]
def has_bank3_output(aid,data):
    # final six words are: enabled, bank, dataID, output-mode, description-len, description-ref
    return any(o[-6]==1 and o[-5]==3 and o[-4]==data for o in ops(aid))

seq=[2,30,31,32,45,35,36,47,58,81,60,3,4,5]
# Default sequence entry is already closed by BD; require the exact tail/order here too.
assert [name(x) for x in seq[-4:]]==['ADRCCapSA','SafeAggSA','ShortAggSA','LongAggSA']

# aid, expected name, exposureType, sourceType, target dataID, final SI dataID
final=[(3,'SafeAggSA',1,3,8,9),(4,'ShortAggSA',0,3,10,11),(5,'LongAggSA',2,3,12,13)]
for aid,nm,et,st,td,si in final:
    r=recs[aid]; assert name(aid)==nm and r[5]==et and r[6]==st
    tc=comp(aid,15); assert tc[2]==11 and tc[3]==3 and tc[4]==td
    assert has_bank3_output(aid,si),(nm,si)

safe_expected=[
 (2,'FrameSA',7,6),(30,'SatPrevSA',18,16),(31,'DarkPrevSA',24,21),
 (32,'BrightenImgSA',28,27),(33,'FaceSA',37,36),(34,'TouchSA',48,47),
 (42,'DepthSA',138,137),(43,'TrackerSA',156,148),(45,'ExtremeColorSA',185,182),
 (46,'SaliencySA',189,188),(58,'IlluminanceSA',229,227)]
st=comp(3,15); sc=calcs(st[1],st[0]); assert len(sc)==11
for c,(aid,nm,value,weight) in zip(sc,safe_expected):
    assert name(aid)==nm
    assert (c[1],c[2])==(3,value),(nm,'value',c[:3])
    assert (c[10],c[11])==(3,weight),(nm,'weight',c[9:12])
    assert has_bank3_output(aid,value),(nm,value)
    assert comp(aid,23)[3:5]==(3,weight),(nm,'confidence',comp(aid,23))

# Short and Long each consume SafeAgg SI plus their dedicated preview analyzer SI.
for aid,other_aid,other_si,other_conf in [(4,35,59,58),(5,36,65,63)]:
    tc=comp(aid,15); cs=calcs(tc[1],tc[0]); assert len(cs)==2
    assert (cs[0][1],cs[0][2])==(3,9)
    assert (cs[0][10],cs[0][11])==(3,6)
    assert (cs[1][1],cs[1][2])==(3,other_si)
    assert (cs[1][10],cs[1][11])==(3,other_conf)
    assert has_bank3_output(3,9)
    assert has_bank3_output(other_aid,other_si)
    assert comp(other_aid,23)[3:5]==(3,other_conf)
    # Shared SafeAgg confidence weighting terminal is exact 0.001f.
    tref=cs[0][17]+1; e=ids[tref]; assert e['name']=='trigger2Data'
    vals=struct.unpack('<fff',bytes.fromhex(e['raw_hex']))
    assert vals[:2]==(1000.0,1000.0)
    assert struct.unpack('<I',struct.pack('<f',vals[2]))[0]==0x3a83126f

# Method switch: mode 11 is the twelfth signed table entry. Resolve directly
# from PE .text file layout (RVA 0x3f0c94, raw .text RVA 0x1000 -> file 0x400).
image=DLL.read_bytes(); table_rva=0x3f0c94; raw_off=0x400+(table_rva-0x1000)
rels=struct.unpack_from('<13i',image,raw_off)
assert rels==(-139,-116,-88,-71,-47,-23,0,23,43,68,86,116,250),rels
method11=0x1803f07a8+rels[11]*4
assert method11==0x1803f0978,hex(method11)
sel=dis(0x1803f0550,0x1803f0580)
need(sel,'1803f055c:','ldr\tw10, [x21, #0x10]','1803f0560:','cmp\tw10, #0xc','1803f0578:','br\tx8')
body=dis(0x1803f0978,0x1803f0b90)
need(body,
     '1803f099c:','ldr\ts16, [x8, x27]','1803f09a0:','fcmpe\ts16, #0.0',
     '1803f09a4:','b.le\t0x1803f0a08',
     '1803f0a48:','ldr\ts16, 0x1803f0ccc',
     '1803f0a50:','str\ts16, [x29, #0x10]',
     '1803f0a88:','bl\t0x1803f1f40',
     '1803f0abc:','fsub\ts16, s19, s18',
     '1803f0b3c:','fdiv\ts20, s16, s17',
     '1803f0b70:','add\tx8, x19, #0x138',
     '1803f0b74:','stp\ts10, s10, [x8]')
# Literal pool identities: epsilon, 256, 100000, 255.
const_rva=0x3f0cc8; const_off=0x400+(const_rva-0x1000)
assert struct.unpack_from('<4I',image,const_off)==(0x33d6bf95,0x43800000,0x47c35000,0x437f0000)

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('FINAL_AGGREGATORS=SafeAggSA:3:8->3:9;ShortAggSA:3:10->3:11;LongAggSA:3:12->3:13')
print('SAFE_CANDIDATES='+','.join(f'{nm}:{v}/{w}' for _,nm,v,w in safe_expected))
print('SHORT_CANDIDATES=SafeAggSA:9/6,ShortSatPrevSA:59/58')
print('LONG_CANDIDATES=SafeAggSA:9/6,LongDarkPrevSA:65/63')
print('METHOD11_ENTRY=0x1803f0978')
print('SHARED_SAFE_WEIGHT_LEAF=0.001f bits=0x3a83126f')
print('BV_VERIFY=PASS')
