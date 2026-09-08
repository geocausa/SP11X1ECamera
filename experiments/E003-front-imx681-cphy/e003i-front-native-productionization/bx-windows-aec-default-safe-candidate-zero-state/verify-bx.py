#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct, subprocess, sys, collections

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

fresh('bw-windows-aec-default-stats-dependency-map','verify-bw.py','BW_VERIFY=PASS')
fresh('bv-windows-aec-final-target-aggregation','verify-bv.py','BV_VERIFY=PASS')

# CAECX bank-manager construction zeroes exactly 1000 SceneAnalyzer slots x
# 24 bytes at object+0x7d08.
ctor=dis(0x1803a9294,0x1803a92e0)
need(ctor,
     '1803a92c0:', 'mov\tx8, #0x7d08',
     '1803a92c4:', 'add\tx0, x19, x8',
     '1803a92cc:', 'mov\tx2, #0x5dc0',
     '1803a92d0:', 'mov\tw1, #0x0')
assert 0x5dc0 == 1000*24

# SceneAnalyzer slot accessor: object + 0x7d08 + dataID*24.
slot=dis(0x1803c4c88,0x1803c4cd8)
need(slot,
     '1803c4ca0:', 'cmp\tw19, #0x3e7',
     '1803c4cb4:', 'mov\tx8, #0x18',
     '1803c4cb8:', 'smaddl\tx9, w19, w8, x0',
     '1803c4cbc:', 'mov\tx8, #0x7d08',
     '1803c4cc0:', 'add\tx0, x9, x8')

# SetDataSceneAnalyzer writes one complete 24-byte record to the same slot.
setter=dis(0x1803d64f8,0x1803d6574)
need(setter,
     '1803d6538:', 'cmp\tw10, #0x3e7',
     '1803d6540:', 'mov\tx9, #0x18',
     '1803d6548:', 'smaddl\tx9, w10, w9, x8',
     '1803d654c:', 'mov\tx8, #0x7d08',
     '1803d6554:', 'str\tq16, [x9]',
     '1803d655c:', 'str\tx8, [x9, #0x10]')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
seq=tuple(struct.unpack('<14I',bytes.fromhex(ids[2569]['raw_hex'])))
assert seq==(2,30,31,32,45,35,36,47,58,81,60,3,4,5)

# Build a whole-tuning writer census for SceneAnalyzer-bank outputs from both
# component publications and arithmetic-operator publications.
writers=collections.defaultdict(list)
for aid,r in recs.items():
    nm=name(aid)
    for off,label in ((7,'Luma'),(15,'Target'),(23,'Confidence')):
        c=r[off:off+8]
        if c[3]==3 and c[4] != 0xffffffff:
            writers[c[4]].append((aid,nm,label))
    n,ref=r[31],r[32]
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*208
    for oi in range(n):
        op=struct.unpack('<52I',b[oi*208:(oi+1)*208])
        if op[46]==1 and op[47]==3:
            writers[op[48]].append((aid,nm,f'op{oi}'))

optional=[
    (33,'FaceSA',37,36),
    (34,'TouchSA',48,47),
    (42,'DepthSA',138,137),
    (43,'TrackerSA',156,148),
    (46,'SaliencySA',189,188),
]
for aid,nm,value,conf in optional:
    assert name(aid)==nm and aid not in seq
    assert {x[0] for x in writers[value]}=={aid},(nm,value,writers[value])
    assert {x[0] for x in writers[conf]}=={aid},(nm,conf,writers[conf])

# BV's SafeAgg candidate order; default-active subset is exactly six analyzers.
r=recs[3]; tc=r[15:23]; assert tc[0]==11 and tc[2]==11
b=bytes.fromhex(ids[tc[1]]['raw_hex']); cs=[struct.unpack('<18I',b[i*72:(i+1)*72]) for i in range(11)]
configured=[(2,7,6),(30,18,16),(31,24,21),(32,28,27),(33,37,36),(34,48,47),(42,138,137),(43,156,148),(45,185,182),(46,189,188),(58,229,227)]
for c,(_,v,w) in zip(cs,configured):
    assert (c[1],c[2],c[10],c[11])==(3,v,3,w)
active=[x for x in configured if x[0] in seq]
assert active==[(2,7,6),(30,18,16),(31,24,21),(32,28,27),(45,185,182),(58,229,227)]

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('SCENE_BANK_LAYOUT=base+0x7d08 + dataID*24 slots=1000')
print('SCENE_BANK_INIT_ZERO_BYTES=0x5dc0')
print('DEFAULT_SAFE_ACTIVE=FrameSA,SatPrevSA,DarkPrevSA,BrightenImgSA,ExtremeColorSA,IlluminanceSA')
print('DEFAULT_SAFE_ZERO=FaceSA,TouchSA,DepthSA,TrackerSA,SaliencySA')
print('ZERO_PROOF=constructor-zero + unique-writer + analyzer-absent-from-uninterrupted-DefaultSequence')
print('BX_VERIFY=PASS')
