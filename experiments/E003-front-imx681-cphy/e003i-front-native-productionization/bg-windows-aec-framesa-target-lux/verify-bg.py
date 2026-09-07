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

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def need(t,*xs):
    for x in xs: assert x in t,x

def run_verify(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
# FrameSA is analyzer ID 2 in the 52x0x8c compact analyzer array.
a=ids[3592]; assert a['name']=='analyzers' and a['payload_size']==52*0x8c
raw=bytes.fromhex(a['raw_hex']); rec=None
for i in range(52):
    w=struct.unpack('<35I',raw[i*0x8c:(i+1)*0x8c])
    if w[0]==2: rec=w; break
assert rec is not None
assert ids[rec[4]]['text']=='FrameSA'
# Three component blocks: calculator count/ref/aggregation/.../description length/ref.
assert rec[7:15]==(1,3595,0,3,4,0,13,3600)
assert ids[3600]['text']=='FrameSA_Luma'
assert rec[15:23]==(1,3601,0,3,5,0,15,3606)
assert ids[3606]['text']=='FrameSA_Target'
assert rec[23:31]==(1,3607,0,3,6,0,19,3612)
assert ids[3612]['text']=='FrameSA_Confidence'

# FrameSA_Target calculator descriptor uses trigger type/dataID (9,8) on both
# its TwoFloats value program and OneFloat weight program.
calc=struct.unpack('<18I',bytes.fromhex(ids[3601]['raw_hex']))
assert calc==(1,19,0,9,8,9,8,1,3602, 1,19,0,9,8,9,8,1,3604)
assert ids[3602]['name']=='trigger1Data' and ids[3602]['payload_size']==16
assert ids[3603]['name']=='trigger2Data' and ids[3603]['payload_size']==96
assert ids[3604]['name']=='trigger1Data' and ids[3604]['payload_size']==16
assert ids[3605]['name']=='trigger2Data' and ids[3605]['payload_size']==12

curve=list(struct.iter_unpack('<ffff',bytes.fromhex(ids[3603]['raw_hex'])))
expected=[(0.0,140.0,55.0,55.0),(160.0,270.0,50.0,50.0),(300.0,360.0,46.0,46.0),
          (370.0,410.0,40.0,40.0),(420.0,460.0,40.0,40.0),(500.0,1000.0,30.0,30.0)]
assert curve==expected,curve
weight=struct.unpack('<fff',bytes.fromhex(ids[3605]['raw_hex']))
assert weight==(1000.0,1000.0,1.0)
# Confidence is distinct and carries the 0.001 leaf.
conf=struct.unpack('<fff',bytes.fromhex(ids[3609]['raw_hex']))
assert conf[0:2]==(0.0,1000.0) and struct.unpack('<I',struct.pack('<f',conf[2]))[0]==0x3a83126f

# TwoFloats runtime interpolator independently proves pairwise linear interpolation.
two=dis(0x1803adac0,0x1803adb38)
need(two,'1803adaf4:','fsub\ts21, s16, s0','1803adaf8:','ldp\ts16, s20, [x20]',
     '1803adb00:','ldp\ts16, s19, [x19]','1803adb08:','fadd\ts18, s17, s16',
     '1803adb14:','fadd\ts16, s17, s16','1803adb18:','stp\ts18, s16')

# RunAnalyzer commits the target pair at object +0x18/+0x1c; SI uses targetLow +0x18.
run=dis(0x1803f13d0,0x1803f16c0)
need(run,'1803f13d4:','add\tx0, x19, #0x178','1803f13e0:','bl\t0x1803f0518',
     '1803f15c4:','str\tx8, [x19, #0x18]','1803f16a4:','ldr\ts16, [x19, #0x18]',
     '1803f16a8:','fdiv\ts16, s16, s17')

# Startup exposure path seeds trigger DB key (type/bank 9, dataID 8) from its Lux field.
seed=dis(0x180378cec,0x18037904c)
need(seed,'180378cec:','ldr\ts17, [x8, #0x71c]','180378cfc:','str\ts17, [x19, #0x7c]',
     '180378f74:','ldr\ts17, [x19, #0x7c]','180378f84:','mov\tw8, #0x8',
     '180378f8c:','str\tw8, [sp, #0x88]','180378f90:','mov\tw8, #0x9',
     '180378f94:','str\tw8, [sp, #0xa0]','180378fa4:','str\ts17, [sp, #0x8c]',
     '180378fb0:','ldr\tx8, [x0, #0x70]')

# Normal runConvergence reads the same packed key (9 | 8<<32) through trigger DB slot +0x58.
conv=dis(0x180375004,0x1803750d0)
need(conv,'18037501c:','mov\tx9, #0x9','180375020:','movk\tx9, #0x8, lsl #32',
     '180375028:','stp\tx9, xzr, [sp, #0x68]','180375030:','ldr\tx8, [x0, #0x58]')
# Two snapshot/control consumers independently read the identical key and consume returned float +4.
for a0,b0,tag in [(0x180381240,0x1803812e8,'180381244:'),(0x1803815d4,0x18038168c,'1803815d8:')]:
    t=dis(a0,b0); need(t,tag,'mov\tx9, #0x9','movk\tx9, #0x8, lsl #32','ldr\tx8, [x0, #0x58]','ldr\ts8, [x8, #0x4]')

# Reuse AB's live bit-exact evidence: dynamic Algorithm001 Lux with known publication latency.
ab=json.loads((BASE/'ab-clean-lux-reconstruction'/'RESULT.json').read_text())['lux_algorithm001']
assert ab['status']=='PASS_LIVE_REQUEST_LOCAL_BIT_EXACT'
assert ab['producer']=='CAnalyzerAlgorithm001::RunAlgorithm'
assert ab['target_bits']=='0x42480000' and ab['target']==50.0
assert ab['history_baseline_dynamic'] is True
assert ab['publication_law']=='Algorithm result appears at the second subsequent publication'
assert ab['ab7_all_match_second_subsequent_publication'] is True

# Retain the already-closed downstream target-SI and metering/convergence joins.
run_verify('bd-windows-aec-target-analyzer-si','verify-bd.py','BD_VERIFY=PASS')
run_verify('bf-windows-aec-metering-convergence-join','verify-bf.py','BF_VERIFY=PASS')

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('FRAMESA_TARGET_COMPONENT=calculators:3601 description:FrameSA_Target')
print('TARGET_TRIGGER_KEY=type9/dataID8')
print('TARGET_CURVE=0-140:55;160-270:50;300-360:46;370-410:40;420-460:40;500-1000:30')
print('TARGET_INTERPOLATION=CAECXTwoFloatsXML linear pair interpolation')
print('CONFIDENCE_0P001_IS_NOT_TARGET=PASS')
print('STARTUP_LUX_SEED=controller+0x1671c -> local+0x7c -> trigger(9,8)')
print('NORMAL_RUNCONVERGENCE_TRIGGER_READ=(9,8) via vtable+0x58')
print('AB_DYNAMIC_LUX_PUBLICATION=second subsequent publication')
print('STEADY_STATE_DIRECT_WRITER=NOT_CLAIMED_BY_BG')
print('BG_VERIFY=PASS')
