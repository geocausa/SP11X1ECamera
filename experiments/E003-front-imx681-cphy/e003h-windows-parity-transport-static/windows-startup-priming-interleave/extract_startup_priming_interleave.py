#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA='cae67c10421246f86a469d95c73cdfa3684c1004827847fe922ab59c2d9273ed'
RAW_BYTES=9624
BUS_SHA='b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6'
PM_SHA='849687aaa5206c25484b9a6e015aba320d7d01610d5292a33df54605f20ae599'
PRIME_SHA='4d49864c26d0bf311b92f65d7020a7942421b9a216fc6068bae45bf47c8c1ef2'

def sha(b): return hashlib.sha256(b).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def file_sha(p): return sha(Path(p).read_bytes())

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--raw',type=Path,required=True); ap.add_argument('--bus',type=Path,required=True); ap.add_argument('--priming-mipi',type=Path,required=True); ap.add_argument('--priming',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 raw=a.raw.read_bytes()
 if len(raw)!=RAW_BYTES or sha(raw)!=RAW_SHA: die('raw identity drift')
 for p,h,n in ((a.bus,BUS_SHA,'bus'),(a.priming_mipi,PM_SHA,'priming/mipi'),(a.priming,PRIME_SHA,'priming replay')):
  if file_sha(p)!=h: die(n+' oracle identity drift')
 bus=json.loads(a.bus.read_text()); pm=json.loads(a.priming_mipi.read_text()); prime=json.loads(a.priming.read_text())
 if not bus.get('accepted') or not pm.get('accepted') or not prime.get('accepted'): die('upstream oracle not accepted')
 text=raw.decode('utf-16')
 marks=[x.strip() for x in text.splitlines() if x.startswith('EV ')]
 if 'EV CYCLE2_ARMED' not in marks: die('cycle2 delimiter missing')
 first=marks[:marks.index('EV CYCLE2_ARMED')]
 expected=[
  'EV IFEPROC n=0 req=0 used=e94','EV REPLAY lenenc=e93','EV IFEPROC n=1 req=1 used=e34',
  *[f'EV BUS_CONFIG n={i:x}' for i in range(9)],
  *[f'EV BUS_ENABLE n={i:x}' for i in range(8)],
  *[f'EV BUS_ADDR n={i:x}' for i in range(9)],
  'EV REPLAY lenenc=e33','EV IFEPROC n=2 req=2 used=904','EV IFEPROC n=3 req=3 used=4e8',
  'EV CSID_START_CALL','EV ISP_START_DONE','EV REPLAY lenenc=903','EV REPLAY lenenc=4e7',
  'EV IFEPROC n=4 req=4 used=958','EV REPLAY lenenc=957','EV IFEPROC n=5 req=5 used=958','EV REPLAY lenenc=957',
  'EV IFEPROC n=6 req=6 used=958','EV REPLAY lenenc=957','EV IFEPROC n=7 req=7 used=958','EV REPLAY lenenc=957',
 ]
 if first!=expected: die('first startup sequence drift: '+repr(first))
 if bus['pre_start_events'][:2]!=['EV IFE803 p=0','EV IFE803 p=1']: die('bus upstream prefix drift')
 if pm['closure']['replay01_relation']!='replay0 -> replay1 -> CSID1 start' or not pm['closure']['replay23_vs_mipi_sensor_start_closed']: die('priming/mipi upstream order drift')
 if prime['replay']['period_packet_mapping']!='packet0=value0; packets1,2,3=value1': die('priming period map drift')
 full=[
  'startup packet0 process','priming replay0 consume','startup packet1 process',
  'VFE1 BUS static config','VFE1 BUS enable','VFE1 initial nine-client addresses','priming replay1 consume',
  'startup packet2 process','startup packet3 process','CSID1 start','ISP_START_DONE',
  'MIPI/CSIPHY start enter','MIPI/CSIPHY start done','IMX681 stream-on','priming replay2 consume','priming replay3 consume','first steady 0x958 request/consume'
 ]
 out={
  'schema':'sp11-e003h-startup-priming-interleave-v1','accepted':True,
  'raw':{'bytes':len(raw),'sha256':sha(raw),'canonical_cycle':'first boot-start window before CYCLE2_ARMED','later_markers_ignored':len(marks)-len(first)-1},
  'upstream_oracles':{'bus_crossorder_sha256':BUS_SHA,'priming_mipi_sha256':PM_SHA,'priming_replay_sha256':PRIME_SHA},
  'first_cycle_events':first,
  'exact_pre_csid_order':['startup packet0','priming replay0','startup packet1','BUS config','BUS enable','initial BUS addresses','priming replay1','startup packet2','startup packet3','CSID1 start'],
  'combined_total_order':full,
  'closures':{
   'replay0_after_packet0_before_packet1':True,
   'replay1_after_initial_bus_addresses_before_packet2':True,
   'replay01_before_csid1_start':True,
   'replay23_after_sensor_on':True,
   'startup_priming_bus_csid_interleave_closed':True,
  },
  'linux_consequence':'The bounded PIX runner may now use the exact startup/priming interleave: startup0 -> priming0 -> startup1 -> BUS prepare -> priming1 -> startup2 -> startup3 -> CSID1 start -> ISP done -> CSIPHY2 -> sensor-on -> priming2 -> priming3 -> steady. Keep the runner unarmed until compiled/inspected.',
  'runtime_authorized':False,
 }
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: startup0 -> priming0 -> startup1 -> BUS -> priming1 -> startup2/3 -> CSID1; priming2/3 remain after sensor-on')
if __name__=='__main__': main()
