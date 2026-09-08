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
    key=f'{addr:x}:'; ls=[x for x in t.splitlines() if key in x]
    assert len(ls)==1,(hex(addr),ls)
    for p in parts: assert p in ls[0],(hex(addr),p,ls[0])

# Require the committed CB ancestry that closes the common interpolation semantics.
cp=subprocess.run(['git','merge-base','--is-ancestor','80c872b','HEAD'],cwd=REPO)
assert cp.returncode==0,'CB ancestry missing'
cb_result=(BASE/'cb-windows-aec-adrc-darkboost-tail'/'VERIFY-RESULT.txt').read_text()
assert 'CB_VERIFY=PASS' in cb_result

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def comp(aid,off): return recs[aid][off:off+8]
def calcs(aid):
    tc=comp(aid,15); b=bytes.fromhex(ids[tc[1]]['raw_hex']); assert len(b)==tc[0]*72
    return [struct.unpack('<18I',b[i*72:(i+1)*72]) for i in range(tc[0])]
def trig1(ref):
    e=ids[ref]; assert e['name']=='trigger1Data'; b=bytes.fromhex(e['raw_hex']); assert len(b)==16
    a,z,n,r=struct.unpack('<ffII',b); return a,z,n,r
def trig2_scalar(ref):
    e=ids[ref]; assert e['name']=='trigger2Data'; b=bytes.fromhex(e['raw_hex']); assert len(b)==12
    return struct.unpack('<fff',b)

short=calcs(4); long=calcs(5)
assert len(short)==len(long)==2
# Runtime 0x60 calculator record consists of two 0x30 halves. Compact 9-word
# halves preserve method/direct DB/trigger descriptors/reference.
for c,leaf in [(short[0],3724),(long[0],3797)]:
    wh=c[9:18]
    assert wh[0]==1                 # method 1: trigger interpolation
    assert wh[1:3]==(3,6)          # serialized direct descriptor retained but not read by method 1
    assert wh[3:7]==(9,8,9,8)      # Lux/Lux trigger descriptors
    assert wh[7]==1 and wh[8]==leaf
    a,z,n,r=trig1(leaf); assert (a,z,n)==(1000.0,1000.0,1)
    v=trig2_scalar(r); assert v[:2]==(1000.0,1000.0)
    assert struct.unpack('<I',struct.pack('<f',v[2]))[0]==0x3a83126f

# Dedicated Short/Long candidates keep method 0 direct confidence weights.
assert short[1][9:12]==(0,3,58)
assert long[1][9:12]==(0,3,63)

# Weight calculator runtime switch. x22 is the current 0x60 calculator record.
w=dis(0x1803f11e0,0x1803f1310)
line_has(w,0x1803f11e4,'mov','x8, #0x60')
line_has(w,0x1803f11ec,'ldr','[x22, #0x30]')
line_has(w,0x1803f11f0,'cbz','0x1803f12ec')
line_has(w,0x1803f11f4,'cmp','w8, #0x1')
line_has(w,0x1803f11f8,'b.eq','0x1803f126c')
# Method 1 reads only the two trigger descriptors +0x40/+0x48, then invokes
# the common interpolator. There is no generic read of direct descriptor +0x34.
line_has(w,0x1803f126c,'ldr','[x22, #0x40]')
line_has(w,0x1803f1290,'add','x1, x22, #0x40')
line_has(w,0x1803f1298,'bl','0x1803d5d30')
line_has(w,0x1803f129c,'ldr','[x22, #0x48]')
line_has(w,0x1803f12c0,'add','x1, x22, #0x48')
line_has(w,0x1803f12c8,'bl','0x1803d5d30')
line_has(w,0x1803f12e0,'bl','0x1803acf40')
line_has(w,0x1803f12e4,'ldr','s16, [x0]')
line_has(w,0x1803f1308,'str','s16')
# Method 0, in contrast, directly reads descriptor +0x34 through the bank manager.
line_has(w,0x1803f12f8,'add','x1, x22, #0x34')
line_has(w,0x1803f1300,'bl','0x1803d5d30')

# Because both trigger dimensions each have one configured region/leaf, CB's
# recursive clamp semantics make the method-1 result exactly the sole leaf for
# every finite Lux coordinate: 0.001f.
print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('SHORT_SAFE_WEIGHT_METHOD=1 trigger-only')
print('LONG_SAFE_WEIGHT_METHOD=1 trigger-only')
print('SERIALIZED_3_6_DESCRIPTOR=retained-but-not-read-on-method1')
print('SAFE_SHARED_TRIGGER_COORDS=9:8,9:8 Lux/Lux')
print('SAFE_SHARED_EFFECTIVE_WEIGHT=0.001f bits=0x3a83126f')
print('SHORT_DEDICATED_WEIGHT=direct 3:58')
print('LONG_DEDICATED_WEIGHT=direct 3:63')
print('CD_VERIFY=PASS')
