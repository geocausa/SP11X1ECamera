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
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

# Generic container parser + BM's clean-room bank decoder.
spec=importlib.util.spec_from_file_location('qti_parameter_bin',ROOT/'tools'/'qti_parameter_bin.py')
qti=importlib.util.module_from_spec(spec);sys.modules[spec.name]=qti;spec.loader.exec_module(qti)
spec=importlib.util.spec_from_file_location('bm_selection',HERE/'tuning-selection.py')
bm=importlib.util.module_from_spec(spec);sys.modules[spec.name]=bm;spec.loader.exec_module(bm)
o=qti.parse(TUNING); entries=o['entries']; by={e['id']:e for e in entries}

def raw(e): return bytes.fromhex(e['raw_hex'])
def words(e):
    b=raw(e); assert len(b)%4==0
    return struct.unpack('<'+'I'*(len(b)//4),b)
def f32_bits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)
def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*needles):
    for s in needles: assert s in t,s

# Fresh consumer proofs: AZ defines materialized ConvStretch semantics; BL consumes
# request-local resolved controls without inventing selection.
fresh('az-windows-aec-convstretch-aggregation','verify-az.py','AZ_VERIFY=PASS')
fresh('bl-native-aec-convergence-kernel','verify-bl.py','BL_VERIFY=PASS')

# RunConvProcesss queries request-local bank rings with query dataID=0 and caches
# the returned ConvBase/ConvStretch pointers in +0x2f0/+0x2f8.
r=dis(0x1803b5b68,0x1803b5bdc)
req(r,
 '1803b5b70:', 'str\twzr, [sp, #0x98]',
 '1803b5b88:', 'mov\tx8, #0xdef0', '1803b5b90:', 'bl\t0x1803d4968',
 '1803b5ba8:', 'str\tx8, [x22, #0x2f0]',
 '1803b5bb4:', 'mov\tx8, #0xdf50', '1803b5bbc:', 'bl\t0x1803d4968',
 '1803b5bd4:', 'str\tx8, [x22, #0x2f8]')

# Bank automatic priority evaluator: build a context bitmask, context-0-only mask
# is unconditional, otherwise required bits must all be active; strictly higher
# signed priority replaces the current selection and records dataID.
p=dis(0x1803d4530,0x1803d4620)
req(p,
 '1803d4558:', 'ldur\tw4, [x9, #-0x8]',
 '1803d45e4:', 'cmp\tx5, #0x1', '1803d45ec:', 'ldr\tx15, [x19, #0x38]',
 '1803d45f0:', 'bics\tx15, x5, x15',
 '1803d45f8:', 'ldr\tw15, [x9, #0x8]', '1803d45fc:', 'cmp\tw12, w15',
 '1803d4604:', 'ldr\tw11, [x9, #0xc]', '1803d460c:', 'str\tw11, [sp, #0x30]')

# GetData query 0 returns the already selected cached record (+0x48/+0x58) on
# the ordinary automatic path; RunConvProcesss passes zero above.
g=dis(0x1803d4968,0x1803d4a78)
req(g,
 '1803d4980:', 'ldr\tw11, [x19]', '1803d498c:', 'cbnz\tw11, 0x1803d4a00',
 '1803d49e0:', 'ldur\tq16, [x8, #0x48]', '1803d49e8:', 'ldr\tx8, [x8, #0x58]')

# Exactly one ConvStretch module exists in the pinned IMX681 tuning.
stretch_roots=[e for e in entries if e['name']=='aecxdbconvstretch']
assert len(stretch_roots)==1
stretch=bm.decode(entries,stretch_roots[0])
assert stretch['bank_type']==12
assert set(stretch['data'])=={1,2}
assert stretch['data'][1]['description']=='DarkBrightStretch'
assert stretch['data'][2]['description']=='DisableStretch'
expected_rules=[((0,),0,2),((2,),1,2),((10,),2,2),((23,),2,2),((11,),2,2)]
assert [(x.contexts,x.priority,x.data_id) for x in stretch['rules']]==expected_rules
# Every possible combination of the module's contexts still selects dataID 2,
# including the empty set because context 0 is the unconditional fallback.
ctx=[2,10,23,11]
for mask in range(1<<len(ctx)):
    active=[ctx[i] for i in range(len(ctx)) if mask&(1<<i)]
    assert bm.select(stretch['rules'],active)==2,(mask,active)

# Decode the selected DisableStretch record exactly.
sw=stretch['data'][2]['words']
assert sw[:3]==(2,15,3022) and by[3022]['text']=='DisableStretch'
assert sw[4:6]==(1,3023)
cw=words(by[3023])
# stretchType=0; trigger descriptors (9,8),(9,8),(9,6); one trigger1 node.
assert cw==(0,9,8,9,8,9,6,1,3024)
assert words(by[3024])==(0,0x447a0000,1,3025)       # 0..1000
assert words(by[3025])==(0,0x447a0000,1,3026)       # 0..1000
leaf=words(by[3026]); assert leaf[:2]==(0,0x447a0000)
assert leaf[2:]==(0x3f800000,)*4                    # weight/factor/comp/tempWeight = 1

# Under AZ semantics, stretchType 0 turns factor 1 into offset log_1.03(1)=0.
# tempWeight=1 makes the history filter exactly select that zero offset, so the
# selected tuning is an identity transform for arbitrary BasicSafe and prior delta.
spec=importlib.util.spec_from_file_location('bm_az',BASE/'az-windows-aec-convstretch-aggregation'/'windows-convstretch.py')
az=importlib.util.module_from_spec(spec);sys.modules[spec.name]=az;spec.loader.exec_module(az)
mat=az.materialize_record(0,1.0,1.0,1.0,1.0)
assert f32_bits(mat.offset)==0 and mat.negative==0
for basic in (-500.0,-1.0,0.0,1.0,500.0):
    for prev in (-100.0,-1.0,0.0,1.0,100.0):
        z=az.apply_aggregated_stretch(basic,prev,mat,.5)
        assert z.short_stretch==0.0 and z.safe_stretch==0.0
        assert z.short_log==basic and z.safe_log==basic and z.long_log==basic
        assert f32_bits(z.pred_gain)==0x3f800000

# Ten ConvBase mode variants exist. Their automatic context-0 fallback always
# selects dataID 1 FastConv. The surrounding record headers are NOT invariant,
# so BM intentionally proves only the three-float interpolated core.
base_roots=[e for e in entries if e['name']=='aecxdbconvbase']
assert len(base_roots)==10
headers=[]
for root in base_roots:
    d=bm.decode(entries,root)
    assert d['bank_type']==11
    assert d['rules'][0].contexts==(0,) and d['rules'][0].priority==0 and d['rules'][0].data_id==1
    assert d['data'][1]['description']=='FastConv'
    rec=d['data'][1]['words']; headers.append(rec[3:7])
    # Data record's final descriptor points to the 3-level interpolation tree.
    leaves=bm.leaves(entries,rec[-1],rec[-2],3)
    assert leaves
    for x in leaves:
        assert x['core_bits']==(0x3f4ccccd,0x3ea8f5c3,0x3e19999a),x
# Work's observed distinction is preserved as a guard: mode-root 143 differs
# from the other nine in control header fields around the same FastConv core.
assert len(set(headers))==2
assert headers[0]!=(headers[1]) and len(set(headers[1:]))==1

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('CONVSTRETCH_MODULES=1')
print('CONVSTRETCH_ALL_CONTEXTS_DATAID=2 DisableStretch')
print('DISABLE_STRETCH=identity (factor=1,tempWeight=1 -> offset=0)')
print('CONVBASE_MODULES=10')
print('CONVBASE_CONTEXT0_DATAID=1 FastConv all variants')
print('FASTCONV_CORE_BITS=0x3f4ccccd,0x3ea8f5c3,0x3e19999a (0.8,0.33,0.15) all variants')
print('CONTROL_HEADER_VARIANTS=2 (capping/tolerance semantics deliberately deferred)')
print('BM_VERIFY=PASS')
