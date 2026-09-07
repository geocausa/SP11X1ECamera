#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def need(t,*xs):
    for x in xs: assert x in t,x

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m

m=load(HERE/'windows-aec-request-state.py','bh_state')

# History payload construction: x21 = control +0x10a8, payload size 0x1b0.
# Seven saved lanes start at +0x10b8 = payload+0x10 and are 0x28 apart.
eof=dis(0x1803bd2e8,0x1803bd620)
need(eof,
 '1803bd2ec:', 'mov\tx9, #0x10b8', '1803bd2f4:', 'add\tx9, x5, #0x8',
 '1803bd304:', 'ldp\tq17, q16, [x9]', '1803bd310:', 'str\tx9, [x10, #0x20]',
 '1803bd3ec:', 'mov\tx9, #0x10a8', '1803bd3f0:', 'add\tx21, x19, x9',
 '1803bd5cc:', 'mov\tw2, #0x1b0', '1803bd5d0:', 'mov\tx1, x21',
 '1803bd5f0:', 'mov\tx0, #0x1c0', '1803bd614:', 'add\tx0, x0, #0x10')
assert 0x10b8-0x10a8==0x10
assert 0x10e0-0x10b8==0x28

# History getter returns node+0x10: the 432-byte payload base whose first qword
# is the saved frame ID. Algorithm001 then selects payload + 0x28*lane + 0x20.
# Because lanes begin at payload+0x10, that is lane-relative +0x10.
hist=dis(0x1803d3b24,0x1803d3b80)
need(hist,'1803d3b40:','ldr\tx11, [x8, #0x10]','1803d3b48:','add\tx0, x8, #0x10')
a1=dis(0x1803fb8f8,0x1803fba38)
need(a1,
 '1803fb8fc:', 'ldrb\tw1, [x0, #0x8ec]', '1803fb904:', 'bl\t0x1803d3938',
 '1803fb9c8:', 'mov\tx23, #0x28', '1803fba2c:', 'smaddl\tx8, w20, w23, x22',
 '1803fba30:', 'ldr\ts10, [x8, #0x20]')
assert 0x20-0x10==0x10

# Algorithm001 steady-state publisher constructs packed trigger key (9,8) and
# calls the generic setter.  This supersedes BG's deliberately conservative
# steady-state-writer scope.
pub=dis(0x1803fba58,0x1803fbad8)
need(pub,
 '1803fba60:', 'mov\tx22, #0x9', '1803fba64:', 'movk\tx22, #0x8, lsl #32',
 '1803fbac8:', 'ldr\tx0, [x8, #0x10]', '1803fbacc:', 'bl\t0x1803d6208')
setter=dis(0x1803d6208,0x1803d6800)
need(setter,'1803d6700:')

# Fresh prerequisite proofs.
fresh('bg-windows-aec-framesa-target-lux','verify-bg.py','BG_VERIFY=PASS')
fresh('bd-windows-aec-target-analyzer-si','verify-bd.py','BD_VERIFY=PASS')
fresh('bf-windows-aec-metering-convergence-join','verify-bf.py','BF_VERIFY=PASS')

# FrameSA curve / interpolation checks.
curve_cases={0.0:55.0,140.0:55.0,150.0:52.5,160.0:50.0,270.0:50.0,
             285.0:48.0,300.0:46.0,365.0:43.0,370.0:40.0,440.0:40.0,
             480.0:35.0,500.0:30.0,1200.0:30.0}
for x,y in curve_cases.items(): assert m.framesa_target_low(x)==m.f32(y),(x,m.framesa_target_low(x),y)

# Recheck AB's bit-exact Algorithm001 arithmetic, but call the formerly named
# "baseline" only the mechanically correct F-3 history reference here.
ab=json.loads((BASE/'ab-clean-lux-reconstruction'/'RESULT.json').read_text())['lux_algorithm001']
for row in ab['ab8_cases']:
    measured=int(row['measured_bits'],16)
    href=int(row['baseline_bits'],16)
    expected=int(row['live_output_bits'],16)
    got=m.bits(m.algorithm001_lux(m.from_bits(measured),m.from_bits(href),0.0,0.0))
    assert got==expected,(row['raw'],hex(got),hex(expected))

# Stateful ordering test: target consumes entry Lux; Algorithm001 updates the
# internal trigger only afterwards; its result is externally visible at F+2.
s=m.AECRequestState(150.0,algorithm001_alpha=0.0)
for f,h in [(7,229.6752471923828),(8,229.6752471923828),(9,229.6752471923828),
            (10,276.67523193359375),(11,323.6752624511719)]: s.commit_history_reference(f,h)
s.commit_exposure_history(9,[101,102,103,104,105,106,107])
r10=s.process_request(10,m.from_bits(0x3f1e9ed8),1_000_000)
assert r10.lux_trigger_in==m.f32(150.0) and r10.target_low==m.f32(52.5)
assert r10.history_reference_frame==7 and r10.external_lux_publication is None
assert r10.previous_exposure_frame==9 and r10.previous_exposure_lanes==(101,102,103,104,105,106,107)
first_next=r10.next_lux_trigger
r11=s.process_request(11,m.from_bits(0x3f1fc97f),1_000_000)
assert r11.lux_trigger_in==first_next
assert r11.external_lux_publication is None
r12=s.process_request(12,m.from_bits(0x3f1fbfcb),1_000_000)
assert m.bits(r12.external_lux_publication)==m.bits(first_next)

# Fail closed if the F-3 reference is missing.
try:
    m.AECRequestState(50.0).process_request(100,1.0,1000)
    raise AssertionError('missing F-3 reference did not fail closed')
except KeyError:
    pass

print('DLL_SHA256='+DLL_SHA)
print('HISTORY_PAYLOAD=0x1b0 bytes in node+0x10; lane0=payload+0x10 stride=0x28')
print('ALGORITHM001_HISTORY_READ=payload+0x20+0x28*i == lane+0x10')
print('AB_DYNAMIC_HISTORY_FIELD_LABEL_CORRECTION=old lane+0x20 Lux label superseded')
print('STEADY_STATE_LUX_WRITER=Algorithm001 -> trigger(9,8) via generic setter')
print('REQUEST_ORDER=entry Lux -> FrameSA target/SI -> Algorithm001 F-3 ref -> next Lux')
print('EXTERNAL_LUX_PUBLICATION_DELAY=+2 requests')
print('CONVERGENCE_HISTORY_SEAM=separate F-1 seven-lane exposure commit')
print('BH_VERIFY=PASS')
