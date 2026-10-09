#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Qualify final aggregate against immutable real46 scalar results and failures."""
from pathlib import Path
import argparse,ast,copy,json,runpy,subprocess
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v18.py"));validate=runtime["validate_trial_totals"]
 actual=json.loads(subprocess.check_output(["sudo","-n","cat","/var/lib/sp11-camera-native-rear-generation-20261007-46/RESULT.json"],text=True))
 assert actual["status"]=="FAIL_REAR_GENERATION_DIAGNOSTIC" and actual["error"]=="240 real requests required"
 assert validate(actual)==1200
 assert [s["probe"]["completed_frames"] for s in actual["sessions"]]==[400,400,400]
 # Execute just the actual failed old aggregate expression, with no main/hardware.
 old=ast.parse((HERE/"run-rear-cadence-v6.py").read_text())
 calls=[n for n in ast.walk(old) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="need" and len(n.args)==2 and isinstance(n.args[1],ast.Constant) and n.args[1].value=="240 real requests required"]
 assert len(calls)==1
 try:eval(compile(ast.Expression(calls[0]),"<actual-old46-aggregate>","eval"),{"result":actual,"need":runtime["need"]})
 except RuntimeError:pass
 else:raise AssertionError("old actual aggregate did not reject retained1200")
 neg=0
 def reject(result):
  nonlocal neg
  try:validate(result)
  except RuntimeError:neg+=1
  else:raise AssertionError("partial, mixed or miscounted total admitted")
 for v in [0,240,1199,1201,True,None,1200.0]:
  bad=copy.deepcopy(actual);bad["completed_application_requests"]=v;reject(bad)
 for sessions in [[],actual["sessions"][:2],actual["sessions"]+actual["sessions"][:1],None,{}]:
  bad=copy.deepcopy(actual);bad["sessions"]=sessions;reject(bad)
 for index in range(3):
  for v in [0,80,399,401,None,400.0,True]:
   bad=copy.deepcopy(actual);bad["sessions"][index]["probe"]["completed_frames"]=v;reject(bad)
  for k,v in [("continuous_capture_proven",False),("probe",None),("session_gate",None)]:
   bad=copy.deepcopy(actual);bad["sessions"][index][k]=v;reject(bad)
  for k,v in [("completed",0),("owner",index+2),("active",1),("poisoned",1)]:
   bad=copy.deepcopy(actual);bad["sessions"][index]["session_gate"][k]=v;reject(bad)
  bad=copy.deepcopy(actual);bad["sessions"][index]=None;reject(bad)
 source=(HERE/"run-rear-cadence-v18.py").read_text()
 assert 'need(result["completed_application_requests"]==240' not in source
 assert source.count("validate_trial_totals(result)")==2 # Definition and one main call.
 main=source[source.index("def main():"):]
 assert main.index("validate_trial_totals(result)")<main.index('result["status"]="PASS_REAR_THREE_SAME_BOOT_LIBCAMERA_SESSIONS_AND_CLEAN_RELEASE"')
 assert 'get("completed_frames")==400' in main and 'validate_probe_cadence(result["probe"],400)' in main
 assert '400<=int(facts.get("epochs","0"))' in main
 report=dict(status="PASS_EXACT_THREE400_AGGREGATE_REAL_RETAINED46_AND_FAILURE_CASES",
             real_retained46_scalar_requests=1200,actual_old46_aggregate_rejects1200=True,
             immutable_raw_failure_preserved=True,actual_new_final_aggregate_accepts_three400=True,
             parser_negative_cases=neg,partial_mixed_miscounted_and_wrong_owner_trials_rejected=True,
             final_aggregate_validated_before_PASS=True,hardware_access=False,pixel_bytes_read=0)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
