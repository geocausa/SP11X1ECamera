#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, struct, subprocess, sys

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

fresh('bn-windows-aec-convbase-default-controls','verify-bn.py','BN_VERIFY=PASS')
fresh('ay-windows-aec-basic-safe-convergence','verify-ay.py','AY_VERIFY=PASS')
fresh('ba-windows-aec-drc-stretch-aggregator','verify-ba.py','BA_VERIFY=PASS')

# One sensor-wide aecxconvergence module in the pinned IMX681 tuning.
roots=[e for e in entries if e['name']=='aecxconvergence']
assert len(roots)==1
r=roots[0]; assert r['id']==131 and r['payload_size']==56
w=words(r)
assert w==(10,0,0,2,2426,3,0x3f000000,0,0,2,2427,0,1,2428)
assert by[2426]['name']=='revision' and by[2426]['text']=='A'

# Context manager performs a direct global lookup of literal aecxconvergence and
# keeps lookup-result +0x120. This is not one of the request-local ConvBase banks.
cm=dis(0x1803ca53c,0x1803ca564)
req(cm,
 '1803ca53c:', 'adrp\tx8, 0x181375000',
 '1803ca540:', 'add\tx1, x8, #0xcb0',
 '1803ca54c:', 'bl\t0x1806f39f8',
 '1803ca554:', 'add\tx8, x0, #0x120',
 '1803ca560:', 'str\tx8, [x22, #0xf10]')
assert b'aecxconvergence\x00' in DLL.read_bytes()

# Generated aecxconvergence deserializer. Runtime payload base is object +0x120
# (x23). It consumes compact root words sequentially:
#   words0..2 -> runtime +8/+c/+10
#   words3..4 -> child/revision object at runtime +0x20
#   word5     -> runtime +0x28
#   word6     -> runtime +0x2c
#   word7     -> runtime +0x30
# The latter two are the exact controls consumed by AEC convergence.
p=dis(0x1802139a0,0x180213c74)
req(p,
 '1802139a4:', 'add\tx9, x19, #0x120',
 '180213a24:', 'add\tx13, x23, #0x8',
 '180213a30:', 'add\tx11, x23, #0xc',
 '180213a3c:', 'add\tx8, x23, #0x10',
 '180213af8:', 'add\tx1, x23, #0x20',
 '180213b20:', 'ldr\tw11, [x8]',
 '180213b60:', 'ldr\tw8, [x12]',
 '180213bb4:', 'bl\t0x1800db3a0',
 '180213bf8:', 'str\tw11, [x23, #0x28]',
 '180213c10:', 'add\tx11, x23, #0x2c',
 '180213c28:', 'ldr\tw10, [x10]',
 '180213c2c:', 'str\tw10, [x11]',
 '180213c6c:', 'str\tw11, [x23, #0x30]')

# Compact sequence proves exact values after the child pair (2,2426).
assert w[:5]==(10,0,0,2,2426)
runtime_28=w[5]
minimum_step_bits=w[6]
drc_policy=w[7]
assert runtime_28==3                         # distinct control; not DRC policy
assert minimum_step_bits==0x3f000000
minimum_step=struct.unpack('<f',struct.pack('<I',minimum_step_bits))[0]
assert minimum_step==0.5
assert drc_policy==0

# Consumers independently establish field semantics.
ay=dis(0x1803ceac4,0x1803ceae0)
req(ay,'1803ceac4:','ldr\tx8, [x19, #0x138]','1803ceacc:','ldr\ts9, [x8, #0x2c]')
bb=dis(0x1803d1f34,0x1803d1f6c)
req(bb,'1803d1f38:','ldr\tx8, [x21, #0x138]','1803d1f40:','ldr\ts8, [x8, #0x2c]')
ba=dis(0x1803d21a8,0x1803d21c8)
req(ba,'1803d21a8:','ldr\tx8, [x19, #0x138]','1803d21b4:','ldr\tw25, [x8, #0x30]')

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('AECXCONVERGENCE_MODULES=1 global direct lookup')
print('DESERIALIZER_COMPACT_WORD5_TO_RUNTIME_0x28=3')
print('MINIMUM_STEP_BITS=0x3f000000 value=0.5')
print('DRC_POLICY=0')
print('POLICY_SEMANTICS=BA policy0 overlap arbitration')
print('BO_VERIFY=PASS')
