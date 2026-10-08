#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual clean runner orchestration; lifecycle/IRQ/reclaim are explicit mocks."""
import argparse,importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",required=True,type=Path);p.add_argument("--report",required=True,type=Path);a=p.parse_args()
 assert not a.report.exists()
 spec=importlib.util.spec_from_file_location("faults",HERE.parent/"test-rear-runner-faults.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 text=m.harness(a.staged)
 text=m.once(text,"static int native_rear_vfe_configure(struct vfe_device *v) {CHECK(v);attempted|=2;return step();}",
  "static int native_rear_vfe_configure(struct vfe_device *v) {CHECK(v);attempted|=2;int r=step();if(r)return r;r=step();return r?r:step();}")
 text="#define READ_ONCE(x) (x)\n#define native_rear_diagnostic_active host_authorized\n#define native_rear_diagnostic_reclaim host_authorized\n#define dev_info(...) ((void)0)\nstatic unsigned reclaim_calls,csid_stop_calls,bus_stop_calls;\n"+text
 text=m.once(text,"halted|=4;return step();","halted|=4;csid_stop_calls++;return step();")
 text=m.once(text,"halted|=2;return step();","halted|=2;bus_stop_calls++;return step();")
 text=m.once(text,"attempted=halted=0;memset(faultable,0,sizeof(faultable));","attempted=halted=0;reclaim_calls=csid_stop_calls=bus_stop_calls=0;memset(faultable,0,sizeof(faultable));")
 text=m.once(text," CHECK(!r->owner_released&&!r->dma_reclaimed);\n return step();",
  " CHECK(!r->owner_released&&!r->dma_reclaimed);\n reclaim_calls++;return step();")
 text=m.once(text,"  CHECK(!pm_refs);CHECK((halted&attempted)==attempted);",
  "  CHECK(!pm_refs);CHECK((halted&attempted)==attempted);\n  CHECK(reclaim_calls==1&&csid_stop_calls==1&&bus_stop_calls==1);\n  CHECK(result.ledgers_released&&!result.dma_intentionally_pinned);")
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-clean-lifecycle-") as td:
  td=Path(td);c=td/"check.c";c.write_text(text)
  for compiler in ["gcc","clang"]:
   binary=td/compiler
   m.checked([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),str(c),"-o",str(binary)])
   run=m.checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(run.stdout),"stderr":run.stderr})
 report={"status":"PASS_CANDIDATE_CLEAN_STOP_RELEASE_AND_FAILURE_STOP_MODELS",
  "actual_staged_runner_orchestration":True,"successful_reclaim_mock_call_checked":True,
  "successful_stop_helpers_called_once_checked":True,
  "post_stop_reclaim_and_lifecycle_IRQ_helpers_are_host_models":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
