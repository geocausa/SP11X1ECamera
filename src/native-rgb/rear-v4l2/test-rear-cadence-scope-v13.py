#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import argparse,json,re,runpy,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
RETAINED=Path("/var/lib/sp11-camera-native-rear-generation-20261007-38/PRIVATE-DMESG.txt")
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v13.py"));scope=runtime["session_log"];negatives=0
 def marker(s):return f"NATIVE_REAR_GENERATION_ATTEMPT identity=53 consumed=1 session={s}\n"
 def reject(log,s):
  nonlocal negatives
  try:scope(log,s)
  except RuntimeError:negatives+=1
  else:raise AssertionError("missing/duplicate/foreign session admitted")
 for s in [1,2,3]:
  own=marker(s)+"NATIVE_REAR_SESSION_GATE body\n"
  assert scope("arbitrary changed old history\n"+own,s)==own
  assert scope(own,s)==own
  for bad in ["",marker(s+1),own+own,own+marker(s+1),own+"NATIVE_REAR_GENERATION_ATTEMPT malformed\n",own.replace("consumed=1","consumed=0"),own.replace("identity=53","identity=38"),own.replace("session="+str(s),"session=x"),own.replace("session="+str(s),"session="+str(s)+" extra=0")]:
   reject(bad,s)
 for s in [0,4,-1]:reject(marker(s),s)
 # Use actual retained scalar logs locally; change only qualification labels.
 # This is offline admission, not a fresh hardware test or fabricated capture.
 actual=subprocess.check_output(["sudo","-n","cat",str(RETAINED)],text=True)
 old=list(re.finditer(r"NATIVE_REAR_GENERATION_ATTEMPT identity=38 consumed=1",actual));assert len(old)==2
 changed=actual
 for s,m in reversed(list(enumerate(old,1))):
  changed=changed[:m.start()]+marker(s).rstrip("\n")+changed[m.end():]
 for s in [1,2]:
  begin=changed.index(marker(s))
  end=changed.index(marker(s+1)) if s==1 else len(changed)
  part=changed[begin:end]
  assert scope(part,s)==part
  gate=runtime["session_gate"](scope(part,s),s);assert gate["completed"]==s
  queue,ok=runtime["rear_queue"](part);assert ok
 # Simulate exactly the lost old prefix that broke rear38.
 rotated="rotated old prefix\n"+changed[changed.index(marker(2)):]
 scoped=scope(rotated,2)
 assert runtime["session_gate"](scoped,2)["owner"]==2
 assert runtime["queue_snapshot"](scoped)["retries"]==0
 report=dict(status="PASS_STRICT_CURRENT_SESSION_LOG_SCOPE_WITH_RING_HISTORY_ROTATION",negative_cases=negatives,actual_retained_scalar_sessions_checked=2,synthetic_session_labels_and_history_rotation=True,no_current_marker_loss_accepted=True,hardware_access=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
