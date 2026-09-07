#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
DLL = Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING = Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert hashlib.sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest() == TUNING_SHA
sys.path.insert(0, str(REPO / 'tools'))
import qti_parameter_bin as qti  # noqa: E402


def dis(start: int, stop: int) -> str:
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={start:#x}',
                                    f'--stop-address={stop:#x}',str(DLL)], text=True)

def req(text: str, *needles: str) -> None:
    for n in needles:
        assert n in text, n

# PE VA helpers.
data = DLL.read_bytes()
e = struct.unpack_from('<I', data, 0x3c)[0]; coff=e+4
nsec=struct.unpack_from('<H',data,coff+2)[0]; optsz=struct.unpack_from('<H',data,coff+16)[0]
opt=coff+20; image=struct.unpack_from('<Q',data,opt+24)[0]; sb=opt+optsz
secs=[]
for i in range(nsec):
    o=sb+i*40; vs,rva,rs,rp=struct.unpack_from('<IIII',data,o+8)
    secs.append((image+rva,max(vs,rs),rp))
def va_off(va: int) -> int:
    for s,z,r in secs:
        if s <= va < s+z: return r + va-s
    raise AssertionError(hex(va))
def cstr(va: int) -> str:
    o=va_off(va); z=data.find(b'\0',o); assert z>=0
    return data[o:z].decode('ascii','replace')

# Exact ContextManager tuning lookup -> core +0xff0.
assert cstr(0x181375E68) == 'aecxmetering'
loader = dis(0x1803CA99C, 0x1803CA9C4)
req(loader,
    '1803ca9a0:', 'add\tx1, x8, #0xe68',
    '1803ca9ac:', 'bl\t0x1806f39f8',
    '1803ca9b4:', 'add\tx8, x0, #0x120',
    '1803ca9c0:', 'str\tx8, [x22, #0xff0]')

# Core vtable slot +0x68 is the getter used by metering: it returns core+0xef8;
# the consumer's +0xf8 load is therefore exactly core+0xff0.
vbase=0x1813383B8
slot68=struct.unpack_from('<Q',data,va_off(vbase+0x68))[0]
assert slot68 == 0x1803AEBB0
getter=dis(slot68, slot68+8)
req(getter, 'add\tx0, x0, #0xef8', 'ret')

# Compact aecxmetering roots and the two antibanding blocks.
# The pinned IMX681 container carries ten mode variants.  Prove the disabled
# path across every variant so BE does not depend on reconstructing selector state.
obj=qti.parse(TUNING); entries=obj['entries']; ids={x['id']:x for x in entries}
roots=[x for x in entries if x['name']=='aecxmetering' and x['payload_size']==248]
assert len(roots)==10, [(x['id'],x['c'],x['payload_size']) for x in roots]
assert [x['id'] for x in roots] == [159,330,354,380,422,450,481,524,548,574]

def resolve_trigger_core(ref: int):
    a=ids[ref]; assert a['name']=='trigger1Data'; w=struct.unpack('<4I',bytes.fromhex(a['raw_hex']))
    b=ids[w[3]]; assert b['name']=='trigger2Data'; w2=struct.unpack('<4I',bytes.fromhex(b['raw_hex']))
    c=ids[w2[3]]; assert c['name']=='triggerData'
    z=bytes.fromhex(c['raw_hex']); assert len(z)==20
    return struct.unpack_from('<3f',z,8)

for root in roots:
    raw=bytes.fromhex(root['raw_hex'])
    u32=lambda o, raw=raw: struct.unpack_from('<I',raw,o)[0]

    # ADRC-priority compact block: disabled in every pinned IMX681 variant.
    assert u32(0x84) == 0, root['id']
    assert u32(0x88) == 0x3F266666, root['id']       # 0.65
    assert u32(0x8C) == 0 and u32(0x90) == 0, root['id']
    assert u32(0x94) == 0x4B189680, root['id']       # 1e7 sentinel/fallback
    assert tuple(u32(o) for o in range(0x98,0xB0,4)) == (9,8,9,8,9,8), root['id']
    assert u32(0xB0) == 1, root['id']
    assert ids[u32(0xB4)]['name'] == 'trigger1Data', root['id']

    # Luma-priority compact block: disabled in every pinned IMX681 variant.
    assert u32(0xB8) == 0, root['id']
    assert u32(0xBC) == 0x3F70A3D7, root['id']       # 0.94 clamp
    assert u32(0xC0) == 0x3F59999A, root['id']       # 0.85 exit
    assert u32(0xC4) == 0 and u32(0xC8) == 0, root['id']
    assert u32(0xCC) == 0x4B189680, root['id']
    assert tuple(u32(o) for o in range(0xD0,0xE8,4)) == (9,8,9,8,9,8), root['id']
    assert u32(0xE8) == 1, root['id']
    assert ids[u32(0xEC)]['name'] == 'trigger1Data', root['id']
    assert u32(0xF0) == 0 and u32(0xF4) == 0, root['id']

    # Both interpolation trees resolve to the same three-float core values.
    assert resolve_trigger_core(u32(0xB4)) == (190.0,230.0,180.0), root['id']
    assert resolve_trigger_core(u32(0xEC)) == (190.0,230.0,180.0), root['id']

# ABI layout reconstruction for the two adjacent blocks.
spec=importlib.util.spec_from_file_location('bemodel',HERE/'windows-antibanding-noop.py')
model=importlib.util.module_from_spec(spec); sys.modules[spec.name]=model; spec.loader.exec_module(model)
assert model.ADRC.compact_size==0x34 and model.ADRC.native_size==0x40
assert model.LUMA.compact_size==0x38 and model.LUMA.native_size==0x48
assert model.COMPACT_ADRC_START==0x84 and model.NATIVE_ADRC_START==0xC0
assert model.COMPACT_LUMA_START==0xB8 and model.NATIVE_LUMA_START==0x100
assert model.COMPACT_TAIL_START==0xF0 and model.NATIVE_TAIL_START==0x148
assert model.apply_pinned(11,22,33)==(11,22,33)

# Luma-priority consumer. False +0x100 gate jumps over every target write to +0x59a4.
luma=dis(0x1803E53C8,0x1803E5A04)
req(luma,
    '1803e542c:', 'ldr\tx20, [x0, #0xf8]',
    '1803e55f8:', 'add\tx17, x20, #0x104',
    '1803e56e4:', 'ldr\tw8, [x20, #0x100]',
    '1803e56e8:', 'cmp\tw8, #0x1',
    '1803e56f4:', 'b.ne\t0x1803e59a4',
    '1803e5838:', 'str\tx8, [x9]',
    '1803e58b4:', 'str\tx8, [x19, #0x48]',
    '1803e5448:', 'ldr\tw8, [x20, #0x148]',
    '1803e59cc:', 'bl\t0x1803e5a18')
# Auxiliary dynamic-adjustment gate is also zero in the compact block.
req(luma,
    '1803e5454:', 'ldr\tw8, [x20, #0x110]',
    '1803e54cc:', 'ldr\tw8, [x20, #0x114]',
    '1803e54d8:', 'ldr\ts16, [x20, #0x118]')

# ADRC-priority consumer. False +0xc0 gate jumps directly to return before target write.
adrc=dis(0x1803E5A18,0x1803E5EDC)
req(adrc,
    '1803e5a80:', 'ldr\tx19, [x0, #0xf8]',
    '1803e5b78:', 'ldr\ts16, [x19, #0xc4]',
    '1803e5c30:', 'ldr\tw8, [x19, #0xc0]',
    '1803e5c40:', 'b.ne\t0x1803e5ea8',
    '1803e5de8:', 'str\tx9, [x8]',
    '1803e5aec:', 'ldr\tw8, [x19, #0xcc]',
    '1803e5af8:', 'ldr\ts16, [x19, #0xd0]')

# RunMeteringPostprocess copies the assembled target tuple, then enters luma-priority.
post=dis(0x1803E46B0,0x1803E4AD0)
req(post,
    '1803e4a78:', 'ldp\tq17, q16, [x8]',
    '1803e4a7c:', 'stp\tq17, q16, [x23]',
    '1803e4a9c:', 'bl\t0x1803e53c8')

# Fresh upstream/downstream static joins.
def run_verify(rel, script, marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (rel, marker, cp.stdout)
run_verify('bd-windows-aec-target-analyzer-si','verify-bd.py','BD_VERIFY=PASS')
run_verify('bc-windows-aec-single-exposure-output','verify-bc.py','BC_VERIFY=PASS')

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('AECXMETERING_VARIANTS=10 size=0xf8 ids=159,330,354,380,422,450,481,524,548,574')
print('LOADER=aecxmetering -> lookup+0x120 -> core+0xff0')
print('ADRC_COMPACT=enable@0x84=0 exitFactor@0x88=0.65')
print('ADRC_NATIVE=enable@0xc0 threshold@0xc4')
print('LUMA_COMPACT=enable@0xb8=0 clamp@0xbc=0.94 exit@0xc0=0.85')
print('LUMA_NATIVE=enable@0x100 clamp@0x104 exit@0x108')
print('ABI_BLOCKS=ADRC 0x34->0x40 LUMA 0x38->0x48 tail->0x148')
print('PINNED_IMX681_ALL_METERING_VARIANTS_ANTIBANDING=IDENTITY')
print('BE_VERIFY=PASS')
