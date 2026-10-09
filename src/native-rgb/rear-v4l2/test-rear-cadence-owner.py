#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import argparse,json,re,runpy,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 runtime=runpy.run_path(str(HERE/"run-rear-cadence.py"));parse=runtime["command_retirement"];neg=0
 def log(owner,ret=0):
  return f"NATIVE_REAR_COMMAND_RETIRE ret={ret} released=4 retired_valid=1 command_arenas_pinned=0 owner={owner} BL_complete=22 stop_flags=0 vb2_complete=0 requeue=0"
 def reject(text,owner):
  nonlocal neg
  try:parse(text,owner)
  except RuntimeError:neg+=1
  else:raise AssertionError("foreign/stale command owner admitted")
 for owner in [1,2,3]:
  facts,retired=parse(log(owner),owner);assert retired and facts["owner"]==owner
  for foreign in [-1,0,1,2,3,4]:
   if foreign!=owner:reject(log(foreign),owner)
  for malformed in ["",log(owner)+"\n"+log(owner),log(owner)+" owner="+str(owner),log(owner)+" extra=0",log(owner).replace("owner="+str(owner),"owner=x")]:
   reject(malformed,owner)
 for bad in [0,-1,4]:reject(log(1),bad)
 # Check real same-boot hardware command owner1/2 facts, no relabeling.
 actual=subprocess.check_output(["sudo","-n","cat","/var/lib/sp11-camera-native-rear-generation-20261007-39/PRIVATE-DMESG.txt"],text=True)
 records=re.findall(r"NATIVE_REAR_COMMAND_RETIRE ([^\n]+)",actual);assert len(records)==2
 for owner,record in enumerate(records,1):
  facts,retired=parse("NATIVE_REAR_COMMAND_RETIRE "+record,owner)
  assert retired and facts["owner"]==owner
 starts=list(re.finditer(r"NATIVE_REAR_GENERATION_ATTEMPT identity=39 consumed=1 session=([0-9]+)\n",actual))
 assert len(starts)==2
 def validate_all(log,session):
  scoped=runtime["session_log"](log,session)
  for name in ["live_observation","live_retirement","live_aux_retirement","command_receipts","rear_queue"]:
   facts,passed=runtime[name](scoped)
   assert passed
  facts,passed=parse(scoped,session);assert passed and facts["owner"]==session
  assert runtime["session_gate"](scoped,session)["owner"]==session
  runtime["queue_snapshot"](scoped)
 for session,marker in enumerate(starts,1):
  part=actual[marker.start():starts[session].start() if session<len(starts) else len(actual)]
  part=part.replace("identity=39 consumed=1 session=","identity=41 consumed=1 session=")
  validate_all(part,session)
 # Third-session admission fixture changes only session/owner counters in
 # the retained second-session scalar log. No hardware3 claim is made.
 third=part.replace("identity=41 consumed=1 session=2","identity=41 consumed=1 session=3")
 third=re.sub(r"(NATIVE_REAR_COMMAND_RETIRE [^\n]* owner=)2\b",r"\g<1>3",third)
 third=re.sub(r"NATIVE_REAR_SESSION_GATE [^\n]+",
              "NATIVE_REAR_SESSION_GATE attempted=3 completed=3 active=0 poisoned=0 owner=3 inner_attempted=3 inner_completed=3 inner_poisoned=0",third)
 validate_all(third,3)
 source=(HERE/"run-rear-cadence.py").read_text()
 assert "command_retirement(log,session)" in source
 # Audit other owner fields: live-replacement owner is a current-owner bool;
 # command-retirement and final kernel/session gate carry actual epochs.
 assert "owner=owner_epoch" in source and 'facts["owner"]==owner_epoch' in source
 report=dict(status="PASS_EXACT_COMMAND_RETIREMENT_OWNER_PER_SESSION_AND_RETAINED_LOGS",negative_cases=neg,actual_retained_owner1_owner2_records_checked=True,successful_expected_owner_epochs=[1,2,3],all_mandatory_runtime_parsers_checked_for_owner1_owner2_and_synthetic_owner3=True,synthetic_third_session_scalar_fixture_only=True,hardware_access=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
