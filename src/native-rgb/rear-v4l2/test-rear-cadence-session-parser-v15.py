#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-rear-generation-20261007-68/restart-runtime-hosted-01.json")
def main():
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v15.py"));parse=runtime["session_gate"];negatives=0
 def reject(log,session):
  nonlocal negatives
  try:parse(log,session)
  except RuntimeError:negatives+=1
  else:raise AssertionError("invalid session admitted")
 def log(f):return "NATIVE_REAR_SESSION_GATE "+" ".join(f"{k}={v}" for k,v in f.items())
 for session in range(1,4):
  facts=dict(attempted=session,completed=session,active=0,poisoned=0,owner=session,inner_attempted=session,inner_completed=session,inner_poisoned=0)
  assert parse(log(facts),session)==facts
  for key in facts:
   changed=dict(facts);changed[key]+=1;reject(log(changed),session)
  for malformed in ["",log(facts)+"\n"+log(facts),log(facts)+" extra=0",log(facts)+" owner=1",log(facts).replace("owner="+str(session),"owner=x")]:
   reject(malformed,session)
  reject(log(facts),session+1)
 clocks={"cam_cc_ife_1_clk":594000000,"cam_cc_ife_1_clk_src":594000000,"cam_cc_csid_clk":300000000,"cam_cc_csid_clk_src":300000000,"cam_cc_csiphy1_clk":300000000}
 snapshot={name:dict(enable_count=0,prepare_count=0,rate_hz=rate) for name,rate in clocks.items()}
 validate=runtime["validate_idle_clocks"]
 validate(snapshot)
 for name in clocks:
  for key in ["enable_count","prepare_count","rate_hz"]:
   bad={k:dict(v) for k,v in snapshot.items()}
   bad[name][key]+=1
   try:validate(bad)
   except RuntimeError:negatives+=1
   else:raise AssertionError("clock leak admitted")
 snap=runtime["queue_snapshot"]
 facts=dict(retries=3,attempts_limit=256,address_reprograms=0,command_resubmissions=0,irq_disabled=0)
 def slog(f):return "NATIVE_REAR_QUEUE_SNAPSHOT "+" ".join(f"{k}={v}" for k,v in f.items())
 assert snap(slog(facts))==facts
 for key in facts:
  bad=dict(facts);bad[key]=-1 if key=="retries" else bad[key]+1
  try:snap(slog(bad))
  except RuntimeError:negatives+=1
  else:raise AssertionError("snapshot safety error admitted")
 for bad in ["",slog(facts)+"\n"+slog(facts),slog(facts)+" extra=0",slog(facts)+" retries=2",slog(facts).replace("retries=3","retries=x")]:
  try:snap(bad)
  except RuntimeError:negatives+=1
  else:raise AssertionError("malformed snapshot admitted")
 source=(HERE/"run-rear-cadence-v15.py").read_text()
 assert 'for session in range(1,4):' in source
 assert source.index('need(probe.returncode==0')<source.index('result["sessions"].append')
 assert 'log=session_log(full_log,session)' in source
 assert 'need(classify(graph)[0]=="neutral"' in source
 result=dict(status="PASS_THREE_SESSION_GATE_PARSER_FAILURE_ADMISSION",negative_cases=negatives,successful_session_parsers=3,hardware_access=False)
 assert not OUT.exists();OUT.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
