#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=BASE.parents[2]
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

spec=importlib.util.spec_from_file_location('qti_parameter_bin',ROOT/'tools'/'qti_parameter_bin.py')
qti=importlib.util.module_from_spec(spec);sys.modules[spec.name]=qti;spec.loader.exec_module(qti)
spec=importlib.util.spec_from_file_location('bm_selection',BASE/'bm-windows-aec-tuning-selection'/'tuning-selection.py')
bm=importlib.util.module_from_spec(spec);sys.modules[spec.name]=bm;spec.loader.exec_module(bm)
o=qti.parse(TUNING); entries=o['entries']; by={e['id']:e for e in entries}

def raw(e): return bytes.fromhex(e['raw_hex'])
def words(e):
    b=raw(e); assert len(b)%4==0
    return struct.unpack('<'+'I'*(len(b)//4),b)
def dis(a,b): return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
    for s in ss: assert s in t,s

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

fresh('bm-windows-aec-tuning-selection','verify-bm.py','BM_VERIFY=PASS')
fresh('ay-windows-aec-basic-safe-convergence','verify-ay.py','AY_VERIFY=PASS')

# Parameter-bin section 2 is the 20-byte mode-tree index. The generic parser
# exposes its offset/size even though it intentionally parses only symbols/payload.
s2=o['sections'][2]
assert s2['offset']==6446303 and s2['size']==18700
b=TUNING.read_bytes()[s2['offset']:s2['offset']+s2['size']]
assert len(b)==18700 and len(b)%20==0
mode=[struct.unpack_from('<5I',b,i) for i in range(0,len(b),20)]
assert len(mode)==935
for i,r in enumerate(mode): assert r[0]==i

# Every tuning-mode group is 17 records. Slot 6 is the AEC domain for the roots
# below. Decode each group-root key as high16=subMode, low16=modeType.
def key(idx):
    r=mode[idx]
    return (r[1]&0xffff, r[1]>>16, r[3])
def path_from_slot(slot):
    root=slot-(slot%17)
    out=[]
    seen=set()
    while root and root not in seen:
        seen.add(root); mt,sm,parent=key(root); out.append((mt,sm))
        root=parent
    return tuple(reversed(out))

roots=[e for e in entries if e['name']=='aecxdbconvbase']
assert [e['id'] for e in roots]==[143,325,349,375,417,445,476,519,543,569]
assert [e['c'] for e in roots]==[6,176,193,210,244,261,278,312,329,346]
assert path_from_slot(6)==()
paths={r['id']:path_from_slot(r['c']) for r in roots[1:]}
expected={
 325:((1,1),(2,0),(3,5)), 349:((1,1),(2,0),(3,6)), 375:((1,1),(2,0),(3,4)),
 417:((1,1),(2,1),(3,5)), 445:((1,1),(2,1),(3,6)), 476:((1,1),(2,1),(3,4)),
 519:((1,1),(2,2),(3,5)), 543:((1,1),(2,2),(3,6)), 569:((1,1),(2,2),(3,4)),
}
assert paths==expected
assert all((1,1) in p for p in paths.values())

# FillTuningModeData lays out standard selector pairs. It stores modeType Sensor=1
# at +fcc, the current sensor mode at +fd0, then modeType Usecase=2 at +fd4 and
# Feature1=3 at +fdc. Later verbose logging loads +fd0 as the argument labelled
# "Sensor mode".
f=dis(0x1802b343c,0x1802b35a0)
req(f,
 '1802b34b0:', 'mov\tw8, #0x1', '1802b34b4:', 'str\tw8, [x9, #0xfcc]',
 '1802b34dc:', 'strh\tw8, [x9, #0xfd0]',
 '1802b34e4:', 'mov\tw8, #0x2', '1802b34e8:', 'str\tw8, [x9, #0xfd4]',
 '1802b351c:', 'add\tx9, x8, #0xfdc', '1802b3528:', 'str\tx8, [x9]')
log=dis(0x1802b3950,0x1802b39a8)
req(log,
 '1802b3990:', 'ldrh\tw6, [x8, #0xfd0]',
 '1802b399c:', 'adrp\tx8, 0x18137d000', '1802b39a0:', 'add\tx2, x8, #0x9c0')
assert b'FillTuningModeData: Node: %s, Sensor mode: %d, Usecase:' in DLL.read_bytes()

# Existing same-machine Windows KD checkpoint: stock Windows Camera selected
# IMX681 firmware resolution/sensor mode index 2, 3840x2160@30.
mode2_json=ROOT/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static/0054-static-inspection.json'
j=json.loads(mode2_json.read_text())
assert j['accepted'] is True and j['selected_resolution_index']==2 and j['geometry']=='3840x2160@30'
# The non-default ConvBase paths all require Sensor subMode 1. Sensor mode 2 cannot
# match any of them, so the unqualified/default root 143 is the selected module.
assert j['selected_resolution_index']!=1
selected=by[143]; assert selected['c']==6
sel=bm.decode(entries,selected)
assert sel['rules'][0].contexts==(0,) and sel['rules'][0].data_id==1
rec=sel['data'][1]['words']
assert sel['data'][1]['description']=='FastConv'
assert rec==(1,9,2822,1,2,2,9,3,9,13,9,6,5,2823)

# Compact -> native expanded record geometry. Compact description is {len,ref};
# expansion turns the ref into an aligned native pointer, adding four bytes before
# compact word4. Runtime BasicSafe then reads +0x14 and +0x18 as tolerance and
# capping type, and its trigger descriptors at +0x1c/+0x24/+0x2c align exactly
# with compact words6..11. This mechanically identifies compact word4/word5.
a=dis(0x1803ce700,0x1803ce950)
req(a,
 '1803ce710:', 'add\tx1, x22, #0x1c',
 '1803ce728:', 'add\tx1, x22, #0x24',
 '1803ce738:', 'add\tx1, x22, #0x2c',
 '1803ce8d4:', 'ldr\tw8, [x22, #0x18]',
 '1803ce93c:', 'ldr\tw8, [x22, #0x14]')
# Compact trigger descriptors are (9,3),(9,13),(9,6), confirming the +4 expansion shift.
assert rec[6:12]==(9,3,9,13,9,6)
tolerance=rec[4]; capping_type=rec[5]
assert tolerance==2 and capping_type==2

# All other mode overlays carry the distinct pair 1/0, corroborating Work's trace.
others=[]
for root in roots[1:]:
    d=bm.decode(entries,root); r=d['data'][1]['words']; others.append((r[4],r[5]))
assert set(others)=={(1,0)}

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('MODE_INDEX_RECORDS=935 (55x17)')
print('DEFAULT_CONVBASE_ROOT=143 mode-slot=6 unqualified')
print('NONDEFAULT_CONVBASE=9 all require Sensor subMode=1')
print('WINDOWS_FRONT_SENSOR_MODE=2 from KD checkpoint')
print('SELECTED_CONVBASE=default root143 FastConv')
print('FASTCONV_TOLERANCE=2')
print('FASTCONV_CAPPING_TYPE=2')
print('OTHER_OVERLAYS=tolerance1/cappingType0 (not selected by mode2 preview)')
print('AY_ADJACENT_BYTE_CAPPING_CLAIM=SUPERSEDED')
print('BN_VERIFY=PASS')
