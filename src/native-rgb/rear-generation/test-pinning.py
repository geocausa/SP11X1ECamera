#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fault-test candidate orchestration, including forced post-stop pinning."""
import argparse,importlib.util,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True)
 p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 if a.report.exists():raise SystemExit("report identity exists")
 spec=importlib.util.spec_from_file_location("rear_generation_faults",HERE.parent/"test-rear-runner-faults.py")
 faults=importlib.util.module_from_spec(spec);spec.loader.exec_module(faults)
 text=faults.harness(a.staged)
 # Config contains the independently tested NoC preparation then register prefix.
 text=faults.once(text,
  "static int native_rear_vfe_configure(struct vfe_device *v) {CHECK(v);attempted|=2;return step();}",
  "static int native_rear_vfe_configure(struct vfe_device *v) {CHECK(v);attempted|=2;int r=step();return r?r:step();}")

 if (a.staged/"native-rear-nv12-bus.inc").exists():
  text=faults.once(text,"int r=step();return r?r:step();}","int r=step();if(r)return r;r=step();return r?r:step();}")

 text="#define READ_ONCE(x) (x)\n#define native_rear_diagnostic_active host_authorized\n#define dev_info(...) ((void)0)\nstatic unsigned reclaim_calls,csid_stop_calls,bus_stop_calls;\n"+text
 text=faults.once(text,"halted|=4;return step();","halted|=4;csid_stop_calls++;return step();")
 text=faults.once(text,"halted|=2;return step();","halted|=2;bus_stop_calls++;return step();")
 text=faults.once(text,"attempted=halted=0;memset(faultable,0,sizeof(faultable));",
  "attempted=halted=0;csid_stop_calls=bus_stop_calls=0;memset(faultable,0,sizeof(faultable));")
 before=" CHECK(!r->owner_released&&!r->dma_reclaimed);\n return step();"
 after=" CHECK(!r->owner_released&&!r->dma_reclaimed);\n reclaim_calls++;return step();"
 text=faults.once(text,before,after)
 text=faults.once(text,"CHECK(run_case(0,0,true)==0);","CHECK(run_case(0,0,true)==-EINPROGRESS);")
 needle=" int ret=e008k_rear_run_unreachable(&c.vfe[1],&req,&result);"
 extra=needle+"""
 CHECK(reclaim_calls==0);
 if(ret==-EINPROGRESS){
  CHECK(result.both_frames_complete&&result.csid_quiesced&&result.bus_stopped);
  CHECK(result.rtcdm_stopped&&result.source_stopped&&result.dma_intentionally_pinned);
  CHECK(!result.dma_reclaimed&&!result.owner_released&&!result.ledgers_released);
  CHECK(pm_refs==1&&unsafe_release>0);\n CHECK(csid_stop_calls==1&&bus_stop_calls==1);
 }
"""
 text=faults.once(text,needle,extra)
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-generation-fault-") as td:
  td=Path(td);source=td/"check.c";source.write_text(text)
  for compiler in ["gcc","clang"]:
   binary=td/compiler
   faults.checked([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
    "-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),str(source),"-o",str(binary)])
   run=faults.checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(run.stdout),"stderr":run.stderr})
 report={"status":"PASS_CANDIDATE_FAILURE_PATHS_AND_COMPLETE_POST_STOP_PINNING",
  "actual_candidate_orchestration_and_stop_pin_branch":True,
  "lifecycle_IRQ_helpers_and_DMA_allocations_host_models":True,
  "all_modeled_partial_start_stop_attempts_checked":True,
  "complete_frames_do_not_authorize_output_reclaim":True,
  "reclaim_function_calls":0,"default_authorization_denial_checked":True,
  "successful_stop_helpers_called_once_checked":True,"physical_completion_not_proven":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
