#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Real private child processes, scalar fixtures; no camera devices or pixels."""
from pathlib import Path
import json,os,runpy,sys,time
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent
from capture_bounded import capture_bounded,proc_stopped
m=runpy.run_path(str(Q/'run-once.py'));O=Path(sys.argv[1]);O.mkdir(parents=True,exist_ok=False)
emitter=O/'scalar-emitter.py'
emitter.write_text("import sys,time\nfor i in range(int(sys.argv[1])):\n print(f'cap dqbuf: {i%3} seq: {i} bytesused: 12672000 ts: {time.monotonic():.6f} field: None (ts-monotonic)',flush=True)\n time.sleep(0.01)\n")
cases=0;pids=[]
def observe(pid):
 assert proc_stopped(pid);pids.append(pid)
 return dict(result=1,active=0,wm_cfg=0,paused=True)
def gone(pid):
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError('child remains')
r=capture_bounded([sys.executable,str(emitter),'90'],O/'baseline.txt',frames=90,timeout=4)
assert m['check_raw_capture']((O/'baseline.txt').read_text(),90)['frames']==90;gone(r['pid']);cases+=1
r=capture_bounded([sys.executable,str(emitter),'120'],O/'hold.txt',frames=120,hold_ms=300,trigger=20,observe=observe,timeout=4)
v=m['check_raw_capture']((O/'hold.txt').read_text(),120)
assert r['actual_stopped_seconds']>=0.3 and v['maximum_completion_gap_seconds']>=0.25;gone(r['pid']);cases+=1
def fail_observer(pid):
 assert proc_stopped(pid);pids.append(pid);raise RuntimeError('deliberate observer refusal')
try:capture_bounded([sys.executable,str(emitter),'300'],O/'refusal.txt',frames=300,hold_ms=300,trigger=20,observe=fail_observer,timeout=4)
except RuntimeError as e:assert 'deliberate observer refusal' in str(e)
else:raise AssertionError('observer refusal admitted')
gone(pids[-1]);cases+=1
try:capture_bounded([sys.executable,'-c',"import time; print('starting',flush=True);time.sleep(10)"],O/'timeout.txt',frames=90,hold_ms=300,trigger=20,observe=observe,timeout=0.3)
except TimeoutError:pass
else:raise AssertionError('freeze admission timeout admitted')
cases+=1
try:capture_bounded([sys.executable,'-c','raise SystemExit(2)'],O/'exit.txt',frames=90,timeout=3)
except RuntimeError as e:assert 'capture process exit: 2' in str(e)
else:raise AssertionError('process exit admitted')
cases+=1
scalar=(O/'baseline.txt').read_text()
negative=[scalar.replace('12672000','1',1),scalar.replace('seq: 40','seq: 400'),'\n'.join(scalar.splitlines()[:-1]),scalar.replace('field: None','field: None error',1)]
for text in negative:
 try:m['check_raw_capture'](text,90)
 except RuntimeError:cases+=1
 else:raise AssertionError('bad scalar capture accepted')
r=dict(status='PASS_BOUNDED_CAPTURE_PROCESS_AND_SCALAR_GATES',cases=cases,
       real_stop_resume_checked=True,observer_refusal_and_timeout_cleanup_checked=True,
       hardware_access=False,pixels=False)
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
