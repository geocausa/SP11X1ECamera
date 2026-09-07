#!/usr/bin/env python3
import hashlib, importlib.util, math, struct, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA
spec=importlib.util.spec_from_file_location('gei',HERE/'windows-get-exposure-info.py'); m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
H=m.HistoryLane; I=m.GetExposureInfoInputs

def dis(a,b):return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
 for s in ss: assert s in t,s

# Entry helper mode 4 = target Safe(+30) - target lane(+20/+28).
h=dis(0x1803d2fe0,0x1803d3050)
req(h,'1803d3024:','cmp\tw22, #0x4','1803d3030:','ldr\td17, [x19, #0x30]',
 '1803d3034:','add\tx8, x8, #0x4','1803d3038:','ldr\td16, [x19, x8, lsl #3]','1803d303c:','fsub\td8, d17, d16')

g=dis(0x1803d18a0,0x1803d2138)
# Input drcSpeed, helper mode4 and history(1).
req(g,'1803d18d4:','fmov\ts14, s0','1803d18dc:','mov\tw1, #0x4','1803d18e4:','bl\t0x1803d2fe0',
 '1803d1910:','mov\tw1, #0x1','1803d1918:','bl\t0x1803d3938')
# history safe +0x78; selected lane (type+1)*0x28; type0 DRC gain +0x178 adjustment.
req(g,'1803d1984:','ldr\tx8, [x19, #0x78]','1803d19a0:','mov\tx9, #0x28','1803d19ac:','ldr\tx8, [x8, x19]',
 '1803d19bc:','ldr\ts0, [x19, #0x178]','1803d19c8:','ccmp\tw20, #0x0','1803d19e8:','fsub\td9, d9, d16')
# targetRelative - historyRelative and exact 1e-7 double equality guard.
req(g,'1803d1a98:','fsub\td8, d11, d9','1803d1aa0:','bl\t0x18007afc0','1803d1aa4:','ldr\td16, 0x1803d2140')
# history1/history2 lane motion and target-motion sign test.
req(g,'1803d1ac4:','mov\tw1, #0x1','1803d1ad4:','mov\tw1, #0x2','1803d1b8c:','fsub\td13, d15, d12',
 '1803d1c48:','ldr\td16, [x21, x8, lsl #3]','1803d1c4c:','fsub\td16, d16, d17','1803d1d24:','fmul\td16, d13, d16')
# tolerance/state[type] force-carry check; state array base is 0x2ac = 0xab*4.
req(g,'1803d1e78:','ldr\tx8, [x21, #0x2f0]','1803d1e80:','ldr\tw8, [x8, #0x14]',
 '1803d1e94:','add\tx9, x8, #0xab','1803d1e98:','ldr\tw9, [x21, x9, lsl #2]')
# Generic carry = DRC Safe(+f8) - previous relative separation.
req(g,'1803d1ea4:','ldr\td12, [x21, #0xf8]','1803d1eac:','fsub\td8, d12, d9')
# drcSpeed relative smoothing and signed runtime minimum-step clamp.
req(g,'1803d1f34:','fcvt\td16, s14','1803d1f3c:','fmul\td14, d16, d8','1803d1f40:','ldr\ts8, [x8, #0x2c]',
 '1803d1f58:','fneg\ts16, s8','1803d1f64:','fcvt\td14, s16','1803d1f68:','fadd\td16, d14, d9','1803d1f74:','fsub\td8, d12, d16')
# target residual snap guarded by 0x3f800001.
req(g,'1803d1f7c:','fsub\td0, d8, d16','1803d1f80:','bl\t0x18007afc0','1803d1f9c:','ldr\ts16, 0x1803d2148','1803d1fac:','ldr\td8, [x21, x8, lsl #3]')
# Final history-direction gate, target bound, Safe-distance cap and output law.
req(g,'1803d207c:','fsub\td16, d8, d19','1803d2084:','fsub\td17, d18, d19','1803d2088:','fmul\td16, d16, d17',
 '1803d2090:','fcsel\td16, d8, d19, ge','1803d20a0:','fcsel\td8, d16, d18, lo','1803d20ac:','fcsel\td8, d16, d18, gt',
 '1803d20b0:','fmov\td0, d11','1803d20bc:','fmov\td0, d9','1803d20c8:','fcsel\td16, d0, d10, gt',
 '1803d20d0:','ldr\td16, [x21, #0xf8]','1803d20f8:','fadd\td8, d16, d17','1803d2100:','fsub\td8, d17, d16',
 '1803d2104:','add\tx8, x19, #0x1d','1803d2108:','str\td8, [x21, x8, lsl #3]')

# Inline constants exact.
b=DLL.read_bytes(); raw=lambda va:(va-0x180000000)-0xc00
assert struct.unpack_from('<Q',b,raw(0x1803d2140))[0]==0x3e7ad7f2a0000000
assert struct.unpack_from('<d',b,raw(0x1803d2140))[0]==m.RELATIVE_EQUAL_EPS_D
assert struct.unpack_from('<I',b,raw(0x1803d2148))[0]==0x3f800001
# Constructor shows state[0..2]=0, state[3]=1 as a contiguous word array.
c=dis(0x1803cd570,0x1803cd680)
req(c,'1803cd5f4:','str\txzr, [x19, #0x2b0]','1803cd5f8:','str\twzr, [x19, #0x2ac]','1803cd66c:','str\tw8, [x19, #0x2b8]')

# Numeric tests in log coordinates while histories are supplied as exact powers of 1.03.
def lin(logv): return int(round(m.ONE03**logv))
# Use large enough exponents for integer quantization; compute expected relations from model's own decoded history logs.
h2=H(lin(100),lin(95),1.0); h1=H(lin(102),lin(96),1.0)
base=I(0, target_lane_log=99,target_safe_log=106,drc_safe_log=107,history1=h1,history2=h2,drc_speed_f32=.5,minimum_step_f32=.25,tolerance_steps=1,state_flag=0)
r=m.compute(base)
assert r.direction_same and r.smoothing_applied
assert abs(r.relative_error)>m.RELATIVE_EQUAL_EPS_D
assert r.candidate_after_target_bound <= 99.0 + 1e-12  # target overshoot bound occurs first
assert abs(107-r.output_log) <= r.safe_distance_limit + 1e-9  # final DRC-Safe cap occurs last
# Direction reversal blocks smoothing and final motion opposite target.
h2=H(lin(100),lin(97),1.0); h1=H(lin(102),lin(96),1.0)
r=m.compute(I(0,99,106,107,h1,h2,.8,.25,1,0))
assert not r.direction_same and not r.smoothing_applied
# state==1 inside tolerance forces carry path.
h2=H(lin(100),lin(95),1.0); h1=H(lin(102),lin(96),1.0); h1log=h1.adjusted_lane_log(0)
r=m.compute(I(0,h1log+.5,106,107,h1,h2,.8,.25,1,1))
assert not r.smoothing_applied
# min-step clamp is exercised with tiny drcSpeed and aligned direction.
r=m.compute(I(0,100,106,107,h1,h2,.001,.5,0,0))
assert r.smoothing_applied and r.minimum_step_clamped
# Type0 DRC gain adjusts the history Short lane; type1 ignores it.
h=H(lin(102),lin(96),2.0)
assert h.adjusted_lane_log(0) > h.adjusted_lane_log(1)
# Type1 output path is accepted and independently produces a finite Long value.
r=m.compute(I(1,101,106,107,H(lin(102),lin(99),2.0),H(lin(100),lin(98),2.0),.3,.25,1,0))
assert math.isfinite(r.output_log)

print('DLL_SHA256='+SHA)
print('FUNCTION=CAECXConvergence::GetExposureInfo@0x1803d18a0')
print('NORMAL_TYPES=0->DRC Short(+e8),1->DRC Long(+f0)')
print('TARGET_RELATIVE=targetSafe-targetLane')
print('HISTORY_RELATIVE=historySafe-adjustedHistoryLane')
print('TYPE0_HISTORY_ADJUST=+log1.03(historyDRCGain) when gain>1')
print('SMOOTH=historyRelative + drcSpeed*(targetRelative-historyRelative), minimum-step-clamped')
print('FINAL_GUARDS=history direction,target overshoot,DRC-Safe max-relative-distance')
print('RELATIVE_EQUAL_EPS_D=0x3e7ad7f2a0000000')
print('BB_VERIFY=PASS')
