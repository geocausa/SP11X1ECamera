#!/usr/bin/env python3
import hashlib,importlib.util,math,struct,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'; assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA
spec=importlib.util.spec_from_file_location('drcs',HERE/'windows-drc-stretch.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def dis(a,b):return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
 for s in ss: assert s in t,s
# Caller proves GetExposureInfo(0/1), DRC block log ordering and aggregator->sensor order.
c=dis(0x1803b6734,0x1803b67e8)
req(c,'1803b6740:','bl\t0x1803d18a0','1803b6750:','bl\t0x1803d18a0',
 '1803b678c:','ldp\td17, d16, [x22, #0xf0]','1803b6794:','ldr\tx7, [x22, #0xe8]',
 '1803b67d4:','bl\t0x1803d2150','1803b67e4:','bl\t0x1803d13f0')
# GetExposureInfo destination law +e8+8*type.
g=dis(0x1803d20d0,0x1803d2138)
req(g,'1803d2104:','add\tx8, x19, #0x1d','1803d2108:','str\td8, [x21, x8, lsl #3]')
# Aggregator ratios, policy field, unconditional Long seed.
a=dis(0x1803d2150,0x1803d2610)
req(a,'1803d217c:','ldr\td16, [x19, #0xe8]','1803d2180:','ldr\td8, [x19, #0xb0]',
 '1803d218c:','bl\t0x180cf5a60','1803d2190:','ldr\td16, [x19, #0xa0]','1803d21a4:','bl\t0x180cf5a60',
 '1803d21b4:','ldr\tw25, [x8, #0x30]','1803d21ac:','ldr\td16, [x19, #0xf0]','1803d21c4:','str\td16, [x19, #0xa8]')
# Full DRC copy blocks and cascade short transform.
req(a,'1803d227c:','ldr\td16, [x19, #0xe8]','1803d2280:','str\td16, [x19, #0xa0]',
 '1803d2284:','ldr\td16, [x19, #0xf0]','1803d2288:','str\td16, [x19, #0xa8]',
 '1803d228c:','ldr\td16, [x19, #0xf8]','1803d2290:','str\td16, [x19, #0xb0]',
 '1803d23a8:','bl\t0x180f5cd58','1803d23b0:','ldr\ts16, [x8, #0xb34]',
 '1803d23f0:','fsub\td16, d17, d18','1803d23f4:','str\td16, [x19, #0xa0]')
# Branch diagnostics prove policy semantics.
for s in ['DRC > Stretch, Keep DRC and set PG to unity','drcRatio < predGain, Keep DRC and set PG: %f',
          'Cascade pred and DRC together','Consider only stretch predictive gain','Use DRC output','Use normal/predictive output']:
 assert s.encode() in DLL.read_bytes(),s
# Numeric branch coverage.
L=m.Lanes
# normal: short<safe gives stretch>1; drc short above/equal safe gives drc<=1.
n=L(98,101,100,1,2,3,4); d=L(101,105,100,11,12,13,14)
r=m.aggregate(n,d,1.5,0); assert r.branch=='normal-predictive' and r.lanes.short==98 and r.lanes.safe==100 and r.lanes.long==105
# unity stretch + DRC>1 => full DRC.
n=L(100,101,100,1,2,3,4); d=L(98,105,100,11,12,13,14)
r=m.aggregate(n,d,1.2,2); assert r.branch=='use-drc' and r.lanes==d and r.pred_gain==1.0
# both >1, policy0 DRC >= stretch => full DRC.
n=L(98,101,100,1,2,3,4); d=L(97,105,100,11,12,13,14)
r=m.aggregate(n,d,1.4,0); assert r.branch=='drc-greater-than-stretch' and r.lanes==d
# both >1, DRC below stretch and under pred consumes PG instead of replacing lanes.
n=L(96,101,100,1,2,3,4); d=L(99,105,100,11,12,13,14)
r=m.aggregate(n,d,2.0,0); assert r.branch=='drc-below-pred-adjust-pg' and r.lanes.short==96 and r.lanes.long==105 and r.pred_gain<2.0
# policy1 cascades stretch separation onto DRC short and copies DRC rest.
r=m.aggregate(n,d,1.7,1); assert r.branch=='cascade-pred-and-drc' and r.lanes.safe==d.safe and r.lanes.long==d.long and r.lanes.short<d.short and r.pred_gain==m.f32(1.7)
# policy2 retains stretch Short/Safe and DRC Long.
r=m.aggregate(n,d,1.7,2); assert r.branch=='stretch-predictive-only' and r.lanes.short==n.short and r.lanes.safe==n.safe and r.lanes.long==d.long
print('DLL_SHA256='+SHA)
print('GET_EXPOSURE_INFO=0x1803d18a0 output=e8+8*type')
print('DRC_BLOCK=Short@e8 Long@f0 Safe@f8 s1-s4@100..118')
print('NORMAL_BLOCK=Short@a0 Long@a8 Safe@b0 s1-s4@b8..d0')
print('AGGREGATOR=0x1803d2150 policy=config+0x30')
print('RATIOS=Stretch:1.03^(Safe-Short) DRC:1.03^(Safe-DRCShort)')
print('BA_VERIFY=PASS')
