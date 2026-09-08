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

fresh('bv-windows-aec-final-target-aggregation','verify-bv.py','BV_VERIFY=PASS')
ab=json.loads((BASE/'ab-clean-lux-reconstruction'/'RESULT.json').read_text())
assert ab['measured_luma']['status']=='PASS_LIVE_BIT_EXACT'
assert ab['measured_luma']['ab23_live_bits']==ab['measured_luma']['ab23_replay_bits']
assert ab['measured_luma']['ab26_live_bits']==ab['measured_luma']['ab26_replay_bits']

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}

# BankIDStatsCalculator data dictionary: 69 compact records x 16 bytes.
sb=bytes.fromhex(ids[3334]['raw_hex']); assert len(sb)==69*16
stats={}
for i in range(69):
    w=struct.unpack('<4I',sb[i*16:(i+1)*16])
    assert w[2]==len(ids[w[3]]['text'])+1
    stats[w[0]]=ids[w[3]]['text']
assert stats[1]=='AvgLumaBE16x16'
assert stats[2]=='FrameLumaBE16x16'
assert stats[6]=='SaturateStatsRatio'

# Metering stats calculator table: 55 compact records x 92 bytes. First word
# is calculator ID, word 13 is its primary BankIDStatsCalculator publication.
cb=bytes.fromhex(ids[7120]['raw_hex']); assert len(cb)==55*92
calculators={}
for i in range(55):
    w=struct.unpack('<23I',cb[i*92:(i+1)*92])
    calculators[w[0]]=(ids[w[2]]['text'],w[13],w)
assert len(calculators)==55

# Normal active calculator sequence from active-calculator tuning.
active=tuple(struct.unpack('<25I',bytes.fromhex(ids[2621]['raw_hex'])))
assert ids[2620]['text']=='DefaultActiveCalculatorSequence'
assert active==(11,12,15,16,23,24,45,46,52,53,47,54,55,56,57,58,60,81,83,85,61,62,63,64,65)

active_expected={
 11:(7,'SatPrevHighPCTLLuma'), 12:(8,'DarkPrevLowPCTLLuma'),
 15:(11,'BrightenImgSatPCTLLuma'), 16:(12,'BrightenImgPCTLLuma'),
 23:(19,'ShortSatPrevHighPCTLLuma'), 24:(20,'LongDarkPrevLowPCTLLuma'),
 45:(41,'ExtremeRedColorRatio'), 46:(42,'ExtremeGreenColorZone1Ratio'),
 52:(48,'ExtremeGreenColorZone2Ratio'), 53:(49,'ExtremeGreenColorZone3Ratio'),
 47:(43,'ExtremeBlueColorRatio'),
}
for cid,(data,nm) in active_expected.items():
    desc,out,_=calculators[cid]
    assert out==data,(cid,out,data)
    assert stats[out]==nm,(cid,stats[out],nm)

# Analyzer records and exact default sequence.
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w
seq=tuple(struct.unpack('<14I',bytes.fromhex(ids[2569]['raw_hex'])))
assert ids[2568]['text']=='DefaultSequence'
assert seq==(2,30,31,32,45,35,36,47,58,81,60,3,4,5)

def aname(aid): return ids[recs[aid][4]]['text']
def bank4_deps(aid):
    r=recs[aid]; out=[]
    # Luma/Target/Confidence component calculator value/weight sources.
    for off in (7,15,23):
        count,ref=r[off],r[off+1]
        b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==count*72
        for j in range(count):
            c=struct.unpack('<18I',b[j*72:(j+1)*72])
            for p in ((1,2),(10,11)):
                if c[p[0]]==4: out.append(c[p[1]])
    # Four arithmetic-operator input descriptors have bank/data at these pairs.
    n,ref=r[31],r[32]
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*208
    for j in range(n):
        op=struct.unpack('<52I',b[j*208:(j+1)*208])
        for p in (5,16,27,38):
            if op[p]==4: out.append(op[p+1])
    return tuple(dict.fromkeys(out))

# Only these default analyzers feed BV's Safe/Short/Long aggregation tree.
producer_aids=(2,30,31,32,45,35,36,58,3,4,5)
expected={
 2:(2,), 30:(7,), 31:(8,), 32:(12,11),
 45:(42,48,49,41,43), 35:(19,), 36:(20,), 58:(6,),
 3:(1,), 4:(1,), 5:(1,),
}
for aid in producer_aids:
    assert bank4_deps(aid)==expected[aid],(aid,aname(aid),bank4_deps(aid),expected[aid])

# Configured SafeAgg candidates that are not in normal DefaultSequence are
# optional modes/ROI analyzers; BW records the topology but does not yet claim
# the databank clearing semantics for their absent publications.
optional=(33,34,42,43,46)
assert tuple(aname(x) for x in optional)==('FaceSA','TouchSA','DepthSA','TrackerSA','SaliencySA')
assert all(x not in seq for x in optional)

required_stats=(1,2,6,7,8,11,12,19,20,41,42,43,48,49)
assert set(required_stats)==set(d for aid in producer_aids for d in expected[aid])

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('DEFAULT_ACTIVE_CALCULATORS='+','.join(map(str,active)))
print('FINAL_TARGET_STATS='+','.join(f'{x}:{stats[x]}' for x in required_stats))
print('DEFAULT_TARGET_ANALYZERS='+','.join(f'{x}:{aname(x)}' for x in producer_aids))
print('OPTIONAL_SAFE_CANDIDATES_ABSENT='+','.join(f'{x}:{aname(x)}' for x in optional))
print('FRAME_LUMA_DATA=bank4:2 FrameLumaBE16x16 AB_live_bit_exact=PASS')
print('BW_VERIFY=PASS')
