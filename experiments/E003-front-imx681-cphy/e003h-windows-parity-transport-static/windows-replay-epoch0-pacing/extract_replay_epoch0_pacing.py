#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path
RAW_SHA='db0d038625843d77428633fcd229a0818a8dc9aafa0af06bc63c06cc6b949b35'
RAW_BYTES=2008

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--raw',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 b=a.raw.read_bytes()
 if len(b)!=RAW_BYTES or sha(b)!=RAW_SHA: die('raw pacing log identity drift')
 lines=b.decode('utf-16').splitlines(); ev=[x for x in lines if x.startswith('EV ')]
 expected=[
  'EV SENSOR_ON','EV EPOCH0 n=0',
  *[f'EV BUS_ADDR n={i:x}' for i in range(0,9)],
  'EV REPLAY lenenc=903','EV CONSUME req=0000000000000002 sub=0','EV VIDEO',
  'EV EPOCH0 n=1',
  *[f'EV BUS_ADDR n={i:x}' for i in range(9,18)],
  'EV REPLAY lenenc=4e7','EV CONSUME req=0000000000000003 sub=0',
  *[f'EV EPOCH0 n={i:x}' for i in range(2,8)],
 ]
 if ev!=expected: die('event sequence drift: '+repr(ev))
 out={
  'schema':'sp11-e003h-replay-epoch0-pacing-v1','accepted':True,
  'source':{'bytes':len(b),'sha256':sha(b),'encoding':'UTF-16LE KD log'},
  'proven_prefix':[
   'IMX681 sensor-on','Epoch0 #0','complete nine-client BUS address update',
   'priming replay2 (0x904 bytes)','selector-2 consume requestId=2 subRequest=0',
   'VIDEO completion','Epoch0 #1','complete nine-client BUS address update',
   'priming replay3 (0x4e8 bytes)','selector-2 consume requestId=3 subRequest=0'],
  'address_bundles':[
   {'epoch0':0,'writer_hits':9,'indices':'0x0..0x8'},
   {'epoch0':1,'writer_hits':9,'indices':'0x9..0x11'}],
  'replays':[
   {'epoch0':0,'encoded_length':'0x903','bytes':'0x904','request_id':2,'subrequest':0},
   {'epoch0':1,'encoded_length':'0x4e7','bytes':'0x4e8','request_id':3,'subrequest':0}],
  'first_video_relation':'replay2/request2 completes before first observed VIDEO; next Epoch0 follows that VIDEO',
  'later_epoch0_observation':'Epoch0 #2..#7 occurred in the bounded debugger window without another captured BUS writer or selector-2 consume; this absence is not used to infer steady-state production timing because breakpoint overhead and the 3-second holder bound are intrusive.',
  'linux_consequence':'For the first bounded QC10C frame, do not submit replay2/replay3 immediately after sensor-on. Wait Epoch0 #0, update the complete BUS address bundle, submit replay2/request2, then wait VIDEO and stop. Replay3 belongs to the next Epoch0 and is not required before returning/stopping the first VIDEO buffer.',
  'runtime_authorized':False,
 }
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output:a.output.write_text(txt)
 else: print(txt,end='')
 print('PASS: first QC10C pacing is sensor-on -> Epoch0 -> BUS update -> replay2/request2 -> VIDEO; replay3 waits for next Epoch0')
if __name__=='__main__': main()
