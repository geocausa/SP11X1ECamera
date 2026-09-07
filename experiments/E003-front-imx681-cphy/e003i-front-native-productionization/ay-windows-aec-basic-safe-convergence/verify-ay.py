#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, math, struct, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

spec=importlib.util.spec_from_file_location('basic_safe', HERE/'windows-basic-safe.py')
mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
I=mod.BasicSafeInputs; run=mod.compute_basic_safe; f32=mod.f32

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(txt,*ss):
    for s in ss: assert s in txt,s

# Exact core anchors: delayed selector, history 1/2, ConvBase, three core values.
c=dis(0x1803ce400,0x1803cecb8)
req(c,
 '1803ce43c:', 'ldr\tx22, [x19, #0x2f0]',
 '1803ce460:', 'ldrb\tw1, [x0, #0x8ec]', '1803ce468:', 'bl\t0x1803d3938',
 '1803ce550:', 'mov\tw1, #0x1', '1803ce55c:', 'bl\t0x1803d3938',
 '1803ce6bc:', 'mov\tw1, #0x2', '1803ce6c8:', 'bl\t0x1803d3938',
 '1803ce8bc:', 'ldr\tx8, [x19, #0x308]',
 '1803ce8c8:', 'ldr\ts16, [x8, #0x8]', '1803ce8d0:', 'ldp\ts16, s17, [x8]',
 '1803ce8d4:', 'ldr\tw8, [x22, #0x18]')

# target - previous history; history motion; base-speed candidate.
req(c,
 '1803ce5f4:', 'ldr\td16, [x20]', '1803ce5f8:', 'fsub\td14, d16, d17',
 '1803ce708:', 'fsub\td8, d9, d16', '1803ce70c:', 'fmul\td16, d8, d14',
 '1803ce9f0:', 'fmul\td8, d16, d14')

# Capping type 0, type 1, and fallback / pipeline-delay byte.
req(c,
 '1803ce9e4:', 'ldr\tw8, [x22, #0x18]', '1803ce9f4:', 'cbz\tw8, 0x1803cea4c',
 '1803ce9f8:', 'cmp\tw8, #0x1', '1803cea28:', 'fdiv\td13, d13, d16',
 '1803cea44:', 'fmul\td13, d16, d18', '1803cea4c:', 'fmul\td13, d18, d13')

# fabs(candidate), fabs(cap), smaller magnitude selection.
req(c,
 '1803cea50:', 'fmov\td0, d8', '1803cea54:', 'bl\t0x18007afc0',
 '1803cea5c:', 'fmov\td0, d13', '1803cea60:', 'bl\t0x18007afc0',
 '1803cea6c:', 'fcsel\td11, d13, d8, gt')

# Tolerance/snap, minimum-step guard, direction gate, seven-lane broadcast.
req(c,
 '1803ce93c:', 'ldr\tw8, [x22, #0x14]', '1803ce94c:', 'ldr\tw8, [x19, #0x2b4]',
 '1803cea74:', 'fcvt\ts16, d11', '1803cea7c:', 'fabs\ts16, s16',
 '1803cea88:', 'ldr\tw8, [x22, #0x14]', '1803ceac0:', 'fsub\td11, d16, d15',
 '1803ceac8:', 'ldr\ts9, [x8, #0x2c]',
 '1803ceb50:', 'fcsel\td8, d12, d11, eq', '1803ceb60:', 'fadd\td16, d8, d15',
 '1803cebfc:', 'stp\td16, d16, [x19, #0xa0]',
 '1803cec00:', 'stp\td16, d16, [x19, #0xb0]',
 '1803cec04:', 'stp\td16, d16, [x19, #0xc0]', '1803cec0c:', 'str\td16, [x19, #0xd0]')

# The two inline guard literals are exact.
b=DLL.read_bytes()
# For this pinned PE, .text RVA 0x1000 maps to raw 0x400; VA->raw = RVA-0xc00.
def text_raw(va): return (va-0x180000000)-0xc00
assert struct.unpack_from('<I',b,text_raw(0x1803cecc0))[0] == 0x33D6BF95
assert struct.unpack_from('<I',b,text_raw(0x1803cecc4))[0] == 0x3F800001
assert f32(struct.unpack('<f',struct.pack('<I',0x33D6BF95))[0]) == mod.FLOAT_EPS_GUARD
assert f32(struct.unpack('<f',struct.pack('<I',0x3F800001))[0]) == mod.TOL_ONE_GUARD

# Shared log coordinate remains the AR/AQ literal.
assert struct.unpack('<f',struct.pack('<I',0x3F83D70A))[0] == mod.ONE03_F32 == f32(1.03)

# Front tuning: exact unique serialized ConvBase core tuples, all capping type 0.
t=TUNING.read_bytes()
profiles={
 'FastConv': (0x377171, .8,.33,.15,0),
 'TouchReduce0p8': (0x377375, .64,.33,.15,0),
 'FastConvFastDRC': (0x377573, .8,.33,.63,0),
 'CropWindowSlow': (0x377655, .1,.33,.1,0),
}
for name,(off,a,cap,drc,mode) in profiles.items():
    pat=struct.pack('<fffI',a,cap,drc,mode)
    assert t[off:off+16] == pat, name
    assert t.count(pat)==1, name

# Arithmetic branch coverage. Values are in the already-proven log1.03 coordinate.
r=run(I(10,0,-1,2, .2,4, .8,.33,.15,0, 2,0, False,False))
assert r.direction_ok and math.isclose(r.candidate_step,8.0,rel_tol=0,abs_tol=2e-6)
assert math.isclose(r.capping_step,float(f32(.33))*8.0,rel_tol=0,abs_tol=1e-12)
assert r.selected_step==r.capping_step and r.lanes==(r.output_log,)*7

r=run(I(-10,0,1,-2, .2,4, .8,.33,.15,1, 2,0, False,False))
assert r.direction_ok and math.isclose(r.capping_step,-float(f32(.33)),abs_tol=1e-12)
assert r.selected_step==r.capping_step

r=run(I(10,0,-1,-2, .2,4, .8,.33,.15,2, 2,0, False,False))
assert r.direction_ok and r.capping_step==3.0 and r.selected_step==3.0

# Explicit intolerance skip: within tol + gate + exact zero previous delta.
r=run(I(.5,0,-1,0, 0.0,4, .8,.33,.15,0, 1,0, True,False))
assert r.skipped_for_intolerance and r.output_log==0.0 and r.applied_step==0.0

# Residual-to-target snap (gate disabled so the earlier skip is not taken).
r=run(I(.5,0,-1,0, .2,4, .8,.33,.15,1, 1,0, False,False))
assert r.snapped_to_target and math.isclose(r.selected_step,.5,abs_tol=1e-12)

# Runtime minimum-step clamp.
r=run(I(10,0,-1,0, .0,4, .001,100,.15,0, 2,.1, False,False))
assert r.minimum_step_clamped and math.isclose(r.selected_step,float(f32(.1)),abs_tol=1e-12)

# Direction reversal: previous temporal motion opposes current target, so apply zero.
r=run(I(10,0,1,0, .0,4, .8,.33,.15,0, 2,0, False,False))
assert not r.direction_ok and r.applied_step==0.0 and r.output_log==0.0

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('FUNCTION=CAECXConvergence::ComputeBasicSafeConvergence@0x1803ce400')
print('LOG_BASE_F32=1.03 bits=0x3f83d70a')
print('FLOAT_EPS_GUARD_BITS=0x33d6bf95')
print('TOL_ONE_GUARD_BITS=0x3f800001')
print('CAP_MODES=0:baseCapping*delayedDelta,1:signedBaseCapping,other:delayedDelta/pipelineDelay')
print('DIRECTION_GATE=temporalMotion*targetDelta>=0')
print('OUTPUT_LANES=7 broadcast +0xa0..+0xd0')
print('FRONT_CONVBASE_PROFILES=4 exact unique tuples checked')
print('AY_VERIFY=PASS')
