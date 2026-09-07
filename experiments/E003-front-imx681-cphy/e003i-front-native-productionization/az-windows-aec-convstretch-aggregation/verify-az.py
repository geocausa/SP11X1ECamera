#!/usr/bin/env python3
import hashlib, importlib.util, math, struct, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll'); TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'; TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA
spec=importlib.util.spec_from_file_location('convstretch',HERE/'windows-convstretch.py'); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
R=m.StretchRecord

def dis(a,b): return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
 for s in ss: assert s in t,s

# Request-local ConvStretch lookup -> convergence +0x2f8.
r=dis(0x1803b5b78,0x1803b5c48)
req(r,'1803b5bb4:', 'mov\tx8, #0xdf50', '1803b5bbc:', 'bl\t0x1803d4968', '1803b5bd4:', 'str\tx8, [x22, #0x2f8]')

# ComputeTargetStretchOutput record layout / batch head.
c=dis(0x1803cecc8,0x1803cf900)
req(c,'1803ced04:', 'ldr\tw25, [x8, #0x14]', '1803ced10:', 'str\txzr, [x19, #0x128]',
 '1803ced58:', 'mov\tx9, #0x30', '1803ced60:', 'ldr\tx8, [x8, #0x20]',
 '1803ced68:', 'add\tx1, x25, #0x4', '1803ced70:', 'add\tx1, x25, #0xc', '1803ced80:', 'add\tx1, x25, #0x14',
 '1803cedac:', 'ldr\tw21, [x25, #0x18]')
# Interpolated runtime record: weight/finalOffset/comp/tempWeight/sign.
req(c,'1803cf484:', 'ldr\ts16, [x23]', '1803cf494:', 'str\ts16, [x9, x8]',
 '1803cf498:', 'ldr\ts0, [x23, #0x4]', '1803cf514:', 'str\ts16, [x8, #0x4]',
 '1803cf540:', 'fcmpe\ts16, #0.0', '1803cf548:', 'str\tw8, [x9, #0x10]',
 '1803cf590:', 'ldr\ts16, [x23, #0x8]', '1803cf5a0:', 'str\ts16, [x8, #0x8]',
 '1803cf5bc:', 'ldr\ts16, [x23, #0xc]', '1803cf5cc:', 'str\ts16, [x8, #0xc]')

# AggregateStretchOutput fields and valid modes.
a=dis(0x1803cfa00,0x1803d0298)
req(a,'1803cfa38:', 'ldr\tw21, [x8, #0x28]', '1803cfa3c:', 'ldr\tw24, [x8, #0x14]',
 '1803cfb58:', 'ldr\tw26, [x8, #0x10]', '1803cfbd4:', 'cmp\tw21, #0x5')
# Mode0 weighted accumulation then normalization.
req(a,'1803cfd78:', 'ldp\ts20, s16, [x8]', '1803cfd7c:', 'fmul\ts17, s16, s20',
 '1803cfd84:', 'fadd\ts8, s20, s8', '1803cfdf0:', 'fdiv\ts16, s16, s8')
# Modes 1/2 vs 3/4 comparator field: +4 offset vs +0 weight; full 0x14 swap.
req(a,'1803cfe28:', 'sub\tw8, w21, #0x3', '1803cfe88:', 'add\tx12, x12, #0x4',
 '1803cfec8:', 'ldr\tq16, [x11]', '1803cfed4:', 'ldr\tq17, [x12]', '1803cfee4:', 'str\tw11, [x12, #0x10]')
# No-selection fallback and selected 16-byte copy.
req(a,'1803d0194:', 'ldp\ts17, s16, [x8]', '1803d01a0:', 'stp\ts17, s16, [x20, #0x8]',
 '1803d01ac:', 'str\twzr, [x20, #0x4]', '1803d01b0:', 'fmov\ts16, #1.00000000', '1803d01b4:', 'stp\ts16, s17, [x20, #0x8]')

# Caller post-filter and exact lane writes. Logger ABI gives Short=a0, Safe=b0, Long=a8.
req(c,'1803cf6d4:', 'bl\t0x1803d3938', '1803cf6e0:', 'ldr\ts17, [x0, #0x17c]',
 '1803cf6f0:', 'fsub\ts16, s9, s8', '1803cf700:', 'fadd\ts11, s17, s16',
 '1803cf75c:', 'bl\t0x1800014d0', '1803cf780:', 'bl\t0x180cf5a60',
 '1803cf83c:', 'fadd\td16, d12, d16', '1803cf840:', 'str\td16, [x19, #0xa0]',
 '1803cf844:', 'ldr\td16, [x19, #0xb0]', '1803cf848:', 'fadd\td16, d17, d16', '1803cf84c:', 'str\td16, [x19, #0xb0]',
 '1803cf850:', 'stp\ts9, s11, [x19, #0xd8]')

# Inline constants: 1e-7 and 1.03f.
b=DLL.read_bytes(); raw=lambda va:(va-0x180000000)-0xc00
assert struct.unpack_from('<I',b,raw(0x1803cf9f8))[0]==0x33d6bf95
assert struct.unpack_from('<I',b,raw(0x1803cf9fc))[0]==0x3f83d70a

# Front tuning explicitly contains both dynamic profile descriptions; do not collapse to one default.
t=TUNING.read_bytes(); assert t.count(b'DarkBrightStretch')==1; assert t.count(b'DisableStretch')==1

# Core materialization: type0 factor->log1.03, nonzero type is direct offset.
x=m.materialize_record(0,1.0,m.ONE03,0.5,0.25); assert abs(x.offset-1.0)<2e-5 and x.negative==0
x=m.materialize_record(1,1.0,-2.0,0.5,0.25); assert x.offset==-2.0 and x.negative==1

# Mode0 weighted blend, including direction filtering.
ring=[R(1,-2,.5,.2,1),R(3,4,1,.6,0),R(),R()]
o=m.aggregate_stretch_output(ring,2,0,0,False); assert abs(o.offset-2.5)<1e-6 and abs(o.comp-.875)<1e-6 and abs(o.temp_weight-.5)<1e-6
o=m.aggregate_stretch_output(ring,2,0,1,True); assert o.offset==-2.0 and abs(o.comp-.5)<1e-6

# Mode1 = offset-sorted closest-to-zero in target direction for well-formed mixed-sign batch.
ring=[R(1,-5,.2,.2,1),R(2,3,.4,.4,0),R(3,-1,.6,.6,1),R(4,7,.8,.8,0)]
o=m.aggregate_stretch_output(ring,4,1,0,False); assert o.offset==3.0
o=m.aggregate_stretch_output(ring,4,1,0,True); assert o.offset==-1.0
# Mode2 = offset-sorted extreme in target direction.
o=m.aggregate_stretch_output(ring,4,2,0,False); assert o.offset==7.0
o=m.aggregate_stretch_output(ring,4,2,0,True); assert o.offset==-5.0
# Mode3/4 sort by weight and select low/high-weight endpoint; direction_mode can reject endpoint.
ring=[R(4,-2,.1,.1,1),R(1,3,.2,.2,0),R(7,5,.3,.3,0),R(2,-4,.4,.4,1)]
assert m.aggregate_stretch_output(ring,4,3,0,False).weight==1.0
assert m.aggregate_stretch_output(ring,4,4,0,False).weight==7.0
fallback=m.aggregate_stretch_output(ring,4,3,1,True); assert fallback.offset==0.0 and fallback.comp==1.0 and fallback.temp_weight==.5

# Post-aggregate filter/quantization and corrected lane map.
a=R(0,-4,.5,1.0,1)
z=m.apply_aggregated_stretch(100.0,0.0,a,.5)
assert z.short_stretch==-4.0 and z.short_log==96.0 and z.long_log==100.0
assert z.pred_gain>1.0 and z.safe_log>z.short_log
# Positive stretch has unity PG and changes Short/Safe equally, leaving Long untouched.
a=R(0,3,1.0,1.0,0); z=m.apply_aggregated_stretch(100.0,0.0,a,.5)
assert z.short_log==103.0 and abs(z.safe_log-103.0)<2e-5 and z.long_log==100.0 and z.pred_gain==1.0

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('COMPUTE_TARGET_STRETCH=0x1803cecc8')
print('AGGREGATE_STRETCH=0x1803cfa00')
print('RUNTIME_RECORD=stride0x14 weight@0 finalOff@4 comp@8 tempWeight@c negative@10')
print('AGG_MODES=0 weighted;1/2 offset-sort directional selection;3/4 weight-sort endpoints')
print('LANES=Short@a0 Safe@b0 Long@a8 PredGain@d8 ShortStretch@dc')
print('FRONT_PROFILES=DarkBrightStretch+DisableStretch both present')
print('AZ_VERIFY=PASS')
