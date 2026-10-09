#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile actual first80/full400 scalar aggregates; preserve existing request flow."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile,os
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 baseline=a.staged.parent.parent/"native-rgb-rear-generation-20261007-58/camss"
 for name in ["native-rear-queue.inc","native-rear-gap-timing.inc","native-rear-full-cache.inc"]:
  s=(a.staged/name).read_text();s=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",s,flags=re.S)
  assert "".join(s.split())=="".join((baseline/name).read_text().split()),("undeclared kernel change",name)
 lib=HERE.parent/"rear-libcamera";s=(lib/"capture-soak.cpp").read_text();base=(lib/"capture-cadence.cpp").read_text()
 clean=s.replace('#include "rear-completion-cadence.h"\n',"").replace("  cadence_.observe(buffer->metadata().timestamp, completed_);\n","").replace(" RearCompletionCadence cadence_;\n","")
 clean="\n".join(l for l in clean.splitlines() if not any(x in l for x in ['<< ",\\\"prefix_','<< ",\\\"long_gap_','<< ",\\\"first_long_gap_sequence','<< ",\\\"completion_gap_max_sequence']))
 clean=clean.replace(">= 400",">= 80").replace("== 400","== 80").replace('"400 complete','"80 complete').replace("seconds(20)","seconds(15)")
 assert "".join(clean.split())=="".join(base.split()),"longer probe changed request, buffer, metadata or release flow"
 assert s.index('request->metadata().get(controls::SensorTimestamp)')<s.index('cadence_.observe(')
 r=runpy.run_path(str(HERE/"run-rear-cadence-v11.py"));validate=r["validate_longer_probe"]
 model=r"""
#include <iostream>
#include <cassert>
#include "rear-completion-cadence.h"
int main() {
 unsigned assertions=0;
 for(unsigned scenario=0;scenario<3;scenario++) {
  RearCompletionCadence c;uint64_t ts=1000000000;
  for(unsigned sequence=0;sequence<400;sequence++) {
   if(sequence)ts+=(sequence==(scenario==1 ? 1U : 240U) && scenario ? 62000000ULL : 33000000ULL);
   c.observe(ts,sequence);
   assert(c.count==sequence+1);assertions++;
  }
  assert(c.prefixLast-c.first==79ULL*33000000ULL+(scenario==1 ? 29000000ULL : 0ULL));assertions++;
  assert(c.prefixMax==(scenario==1 ? 62000000ULL : 33000000ULL));assertions++;
  assert(c.longGaps==(scenario ? 1U : 0U));assertions++;
  assert(c.lateLongGaps==(scenario==2 ? 1U : 0U));assertions++;
  assert(c.firstLongSequence==(scenario==1 ? 1U : scenario==2 ? 240U : 0U));assertions++;
  assert(c.maximumSequence==(scenario==1 ? 1U : scenario==2 ? 240U : 1U));assertions++;
  std::cout<<"{\"completed_frames\":400,\"prefix_buffers\":80,\"long_gap_threshold_ns\":50000000"
   <<",\"completion_timestamp_span_ns\":"<<c.previous-c.first
   <<",\"completion_gap_min_ns\":33000000,\"completion_gap_max_ns\":"<<c.maximum
   <<",\"prefix_completion_timestamp_span_ns\":"<<c.prefixLast-c.first
   <<",\"prefix_completion_gap_min_ns\":"<<c.prefixMin
   <<",\"prefix_completion_gap_max_ns\":"<<c.prefixMax
   <<",\"long_gap_count\":"<<c.longGaps<<",\"long_gap_count_after_first80\":"<<c.lateLongGaps
   <<",\"first_long_gap_sequence\":"<<c.firstLongSequence
   <<",\"completion_gap_max_sequence\":"<<c.maximumSequence<<"}\n";
 }
 std::cerr<<"ASSERTIONS="<<assertions<<" INPUT_COMPLETIONS=1200\n";
}
"""
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-soak-timing-") as tmp:
  d=Path(tmp);src=d/"model.cpp";src.write_text(model)
  for cc in ["g++","clang++"]:
   exe=d/cc
   subprocess.run([cc,"-std=c++17","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(lib),str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   run=subprocess.run([str(exe)],check=True,capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   assert "ASSERTIONS=1218" in run.stderr
   facts=[json.loads(l) for l in run.stdout.splitlines()];assert len(facts)==3
   for f in facts:validate(f)
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=1218,synthetic_completions=1200,scenarios=["no_long_gaps","prefix_long_gap","late_long_gap"]))
 neg=0
 def reject(f):
  nonlocal neg
  try:validate(f)
  except RuntimeError:neg+=1
  else:raise AssertionError("bad longer probe accepted")
 for f in facts:
  for k in f:
   bad=dict(f);bad[k]=None;reject(bad)
 for k,v in [("completed_frames",399),("prefix_buffers",400),("long_gap_threshold_ns",0),("long_gap_count",400),
             ("long_gap_count_after_first80",321),("first_long_gap_sequence",0),("first_long_gap_sequence",400),
             ("completion_gap_max_sequence",0),("completion_gap_max_sequence",80),
             ("prefix_completion_gap_max_ns",63000000)]:
  bad=dict(facts[1]);bad[k]=v;reject(bad)
 for k in ["long_gap_count","first_long_gap_sequence"]:
  bad=dict(facts[0]);bad[k]=1;reject(bad)
 bad=dict(facts[2]);bad["first_long_gap_sequence"]=1;reject(bad)
 # Existing80 timing validator fixtures remain admitted; main explicitly requires400.
 source=(HERE/"run-rear-cadence-v11.py").read_text()
 assert 'validate_probe_cadence(result["probe"],400)' in source and 'validate_longer_probe(result["probe"])' in source
 assert 'get("completed_frames")==400' in source
 report=dict(status="PASS_ACTUAL_LONGER_PROBE_TIMING_MODEL_SOURCE_SCOPE_AND_PARSER",results=results,parser_negative_cases=neg,
             original_request_buffer_metadata_release_tokens_unchanged=True,only_frame_target_timeout_and_scalar_timing_added=True,
             prefix80_kernel_observer_unchanged=True,late_gap_count_and_max_ordinal_checked=True,qualification_requests_per_session=400,
             hardware_access=False,pixel_bytes_read=0)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
