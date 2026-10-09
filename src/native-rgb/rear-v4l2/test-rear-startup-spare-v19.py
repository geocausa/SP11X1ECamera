#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual startup helper failure/ownership model, declared source diff, strict parser."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile,os
UNDO_STATS=runpy.run_path(str(Path(__file__).resolve().parent/"rear-statistics-source-proof.py"))["undo_queue_timestamp"]
UNDO_STOP=runpy.run_path(str(Path(__file__).resolve().parent/"rear-stop-admission-source-proof.py"))["undo_stop_diagnostic"]
UNDO_ORDER=runpy.run_path(str(Path(__file__).resolve().parent/"rear-source-stop-order-proof.py"))["undo_source_stop_order"]
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 base=a.staged.parent.parent/"native-rgb-rear-generation-20261007-60/camss"
 for name in ["camss-vfe-e008h-rear-prime.inc","native-rear-queue.inc","camss-vfe-e008k-rear-runner.inc"]:
  t=(a.staged/name).read_text()
  if name=="native-rear-queue.inc":t=UNDO_STATS(t)
  if name=="camss-vfe-e008k-rear-runner.inc":t=UNDO_ORDER(UNDO_STOP(t))
  clean=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",t,flags=re.S)
  assert "".join(clean.split())=="".join((base/name).read_text().split()),("undeclared source delta",name)
 runner=(a.staged/"camss-vfe-e008k-rear-runner.inc").read_text()
 assert runner.index("native_rear_startup_spare_prepare(")<runner.index("e008k_rear_pipeline_pm_get(video_entity)")<runner.index("hardware_touched = true")
 assert runner.index("native_rear_startup_spare_release(vfe, pair, true)")>runner.index("e008k_rear_pair_stop_release(")
 pin=runner[runner.index("out_pin:"):runner.index("out_clean_power:")]
 assert "native_rear_startup_spare_release(" not in pin and "native_rear_faulted_pair = pair" in pin
 queue=(a.staged/"native-rear-queue.inc").read_text()
 assert queue.index("native_rear_startup_spare_take(")<queue.index("e007z_rear_bind(&next->frame[1]")
 assert queue.index("native_rear_queue_prepare(vfe, pair, next, buffer")<queue.index("*pair = *next;")<queue.index("native_rear_video_lease_expose(&pair->dma[1]")
 helper=(a.staged/"native-rear-startup-spare.inc").read_text()
 assert "vfe_buf_get_pending" not in helper and "vb2_buffer_done" not in helper
 source=(HERE/"test-rear-startup-spare-model.c").read_text().replace("/* ACTUAL_HELPER */",
  'static u64 ktime_get_ns(void) { static u64 t=1000000;t+=1000000;return t;}\n'+helper)
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v19.py"));parse=runtime["rear_startup_prefetch"]
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-startup-spare-") as tmp:
  d=Path(tmp);src=d/"model.c";src.write_text(source)
  for cc in ["gcc","clang"]:
   exe=d/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output([exe],text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   match=re.search(r"STARTUP_MODEL_PASS assertions=(\d+) failure_stages=10 stale_take_cases=12",out);assert match,out
   results.append(dict(compiler=cc,assertions=int(match[1]),ASAN_UBSAN_Werror=True,allocation_and_API_failure_stages=10,stale_take_cases=12))
  formats=[re.findall(r'"NATIVE_REAR_PREFETCH [^"\n]*"',queue)[0],re.findall(r'"NATIVE_REAR_PREFETCH_RELEASE [^"\n]*"',helper)[0]]
  src.write_text('#include <stdio.h>\nint main(void){printf('+formats[0]+',2ULL,3ULL,5000000ULL,1U,0U);printf('+formats[1]+',2ULL,1U,0U,15U);return 0;}\n')
  for cc in ["gcc","clang"]:
   exe=d/(cc+"-format");subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   log=subprocess.check_output([exe],text=True);parsed=parse(log,2);assert parsed["prepare"]["taken"]==1
 neg=0
 def reject(s,owner=2):
  nonlocal neg
  try:parse(s,owner)
  except RuntimeError:neg+=1
  else:raise AssertionError("invalid startup evidence admitted")
 for line in log.splitlines():
  reject(log.replace(line,""));reject(log+"\n"+line)
  for token in line.split()[1:]:
   key,value=token.split("=")
   reject(log.replace(line,line.replace(token,key+"=-1")))
   reject(log.replace(line,line+" "+token))
   reject(log.replace(line," ".join(x for x in line.split() if x!=token)))
 for bad in ["owner=3","generation=2","prepare_ns=0","prepare_ns=2000000000","taken=0","pending_allocated=1","before_power=0","fifo_preserved=0","original_proofs=0","pixel_bytes_read=1","unused_freed=1","all_stops=7","wrapper_idle=0"]:
  key=bad.split("=")[0];reject(re.sub(r"\b"+key+r"=\d+",bad,log))
 reject(log,1);reject(log,3);reject(log,0)
 # Prefetch removes exactly one rolling allocation/cache lookup, but original
 # logical retirement remains every handoff. Strict unmodified defaults reject it.
 cadence=dict(handoffs=400,elapsed_ns=14000000000,prepare_ns=800000000,retire_ns=700000000)
 dma="NATIVE_REAR_DMA_TIMING full_get_ns=10000000 aux_alloc_ns=700000000 full_put_ns=200000 aux_zero_ns=35000000 aux_free_ns=570000000 full_get_calls=399 aux_alloc_calls=3192 full_put_calls=400 aux_free_calls=3200 scope=1 pixel_bytes_read=0\n"
 cache="NATIVE_REAR_FULL_CACHE owner=2 active=1 hits=397 misses=2 stored=400 evicted=0 retained=3 capacity=4 physical_unmaps_deferred=1 pixel_bytes_read=0\nNATIVE_REAR_FULL_CACHE_FLUSH owner=2 released=3 all_stops=15 idle=1 pixel_bytes_read=0\n"
 runtime["rear_dma_timing"](dma,cadence,prefetched=1);runtime["rear_full_cache"](cache,cadence,2,prefetched=1)
 for fn,args in [(runtime["rear_dma_timing"],(dma,cadence)),(runtime["rear_full_cache"],(cache,cadence,2))]:
  try:fn(*args)
  except RuntimeError:neg+=1
  else:raise AssertionError("unaccounted early allocation admitted")
 main_src=(HERE/"run-rear-cadence-v19.py").read_text().split("def main():",1)[1]
 assert main_src.index('rear_startup_prefetch(log,session)')<main_src.index('rear_dma_timing(log,result["cadence"],prefetched=1)')
 assert 'rear_full_cache(log,queue_facts,session,prefetched=1)' in main_src
 report=dict(status="PASS_ACTUAL_STARTUP_SPARE_OWNERSHIP_FAILURE_MODELS_AND_PARSER",results=results,parser_negative_cases=neg,
  original_proof_and_queue_tokens_preserved_after_declared_overlay=True,whole_alias_and_command_checks_called_for_both_initial_sets=True,
  preallocation_before_pipeline_power=True,original_FIFO_preserved=True,exact_owner_and_next_generation_checked=True,
  uncertain_descriptor_retained_with_faulted_pair=True,hardware_DMA_APIs_are_models=True,pixel_bytes_read=0,physical_hardware_access=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":
 try:main()
 except subprocess.CalledProcessError as e:
  print(e.stdout or "",e.stderr or "");raise
