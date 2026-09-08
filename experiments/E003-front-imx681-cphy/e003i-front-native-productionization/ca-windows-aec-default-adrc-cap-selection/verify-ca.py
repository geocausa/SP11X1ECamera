#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct, subprocess, sys

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

def fbits(x): return struct.unpack('<I',struct.pack('<f',x))[0]

# BZ fresh-runs BY -> BX, preserving method11 identity and the default
# SceneAnalyzer zero-state proof used here.
fresh('bz-windows-aec-final-adjratio-publication','verify-bz.py','BZ_VERIFY=PASS')
bx=(BASE/'bx-windows-aec-default-safe-candidate-zero-state'/'VERIFY-RESULT.txt').read_text()
assert 'DEFAULT_SAFE_ZERO=FaceSA,TouchSA,DepthSA,TrackerSA,SaliencySA' in bx

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def ops(aid):
    r=recs[aid]; n,ref=r[31],r[32]; b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*208
    return [struct.unpack('<52I',b[i*208:(i+1)*208]) for i in range(n)]

assert name(60)=='ADRCCapSA'
seq=struct.unpack('<14I',bytes.fromhex(ids[2569]['raw_hex']))
assert seq[-4:]==(60,3,4,5) and 33 not in seq
op=ops(60)[0]
assert op[0:3]==(1,0,13),op[:3]  # enabled; tuning count; CondSmaller
A=op[3:14]; B=op[14:25]; C=op[25:36]; D=op[36:47]; OUT=op[47:52]
assert A[0]==1 and A[2:4]==(3,36),A           # FaceSA confidence
assert B[0]==0 and B[1]==0x38d1b717,B         # 0.0001f
assert C[0]==2 and C[8:11]==(1,6745,1),C
assert D[0]==2 and D[8:11]==(1,6747,1),D
assert OUT==(9,54,0,15,6749),OUT
assert ids[6749]['text']=='ADRCLuxFaceCap'
assert struct.unpack('<f',struct.pack('<I',B[1]))[0] > 0.0

# C/D terminal tables are pinned but their full two-trigger semantic mapping is
# deliberately left for the next checkpoint.
c1=struct.unpack('<4I',bytes.fromhex(ids[6745]['raw_hex'])); assert c1==(0,0x447a0000,3,6746)
c2=struct.unpack('<12f',bytes.fromhex(ids[6746]['raw_hex']))
assert tuple(fbits(x) for x in c2)==(
    0x00000000,0x43520000,0x3fcccccd,0x3fcccccd,
    0x43820000,0x43960000,0x3fc00000,0x3fc00000,
    0x43a00000,0x447a0000,0x3fb33333,0x3fb33333)
assert ids[6747]['name']=='trigger1Data' and ids[6748]['name']=='trigger2Data'

# RunOneArithMeticOperator resolves operands in A,B,C,D order to s11,s12,s13,s14.
pre=dis(0x1803c8e58,0x1803c8f54)
need(pre,
     '1803c8e6c:', 'add\tx1, x20, #0x10',
     '1803c8e88:', 'add\tx1, x20, #0x48',
     '1803c8ea4:', 'add\tx1, x20, #0x80',
     '1803c8ec0:', 'add\tx1, x20, #0xb8',
     '1803c8f40:', 'ldp\ts11, s12, [sp, #0x68]',
     '1803c8f48:', 'ldr\ts13, [sp, #0x70]',
     '1803c8f50:', 'ldr\ts14, [sp, #0x60]')
# Enum 13 CondSmaller: if A<B choose C, else D.
cond=dis(0x1803c9b58,0x1803c9b6c)
need(cond,
     '1803c9b5c:', 'fcmpe\ts11, s12',
     '1803c9b60:', 'fcsel\ts10, s13, s14, lo')

# BX established FaceSA confidence data3:36 remains +0 in uninterrupted
# DefaultSequence. Therefore A=0 < fixed B=0.0001 and C is selected.
print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('ADRC_CAP_OUTPUT=Triggers:9:54 ADRCLuxFaceCap')
print('DEFAULT_FACE_CONFIDENCE=SceneAnalyzer:3:36=+0')
print('COND_SMALLER=A<B?C:D')
print('DEFAULT_SELECTION=0.0<0.0001 -> C')
print('SELECTED_C_TERMINALS=0..210:1.6;260..300:1.5;320..1000:1.4')
print('METHOD2_TRIGGER_MAPPING=deferred')
print('CA_VERIFY=PASS')
