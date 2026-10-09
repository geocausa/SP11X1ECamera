#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual cache/lease helpers, unchanged guard source, exact log/identity admission."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile,os
UNDO_STATS=runpy.run_path(str(Path(__file__).resolve().parent/"rear-statistics-source-proof.py"))["undo_queue_timestamp"]
HERE=Path(__file__).resolve().parent
def fn(t,name):
 i=t.index(name+"(");a=t.index("{",i);j=a+1;depth=1
 while depth:depth+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 base=a.staged.parent.parent/"native-rgb-rear-generation-20261007-55/camss"
 names=["native-rear-video-lease.inc","native-rear-live-retire.inc","camss-vfe-e008d-rear-dma.inc","native-rear-queue.inc","native-rear-reclaim.inc","native-rear-session-clean.inc"]
 for name in names:
  s=(a.staged/name).read_text()
  if name=="native-rear-queue.inc":s=UNDO_STATS(s)
  s=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",s,flags=re.S);s=re.sub(r"\n/\* GAP_TIMING_BEGIN \*/\n.*?/\* GAP_TIMING_END \*/\n","\n",s,flags=re.S);clean=re.sub(r"\n/\* FULL_CACHE_BEGIN \*/\n.*?/\* FULL_CACHE_END \*/\n","",s,flags=re.S)
  assert "".join(clean.split())=="".join((base/name).read_text().split()),("undeclared source change",name)
 retire=(a.staged/"native-rear-live-retire.inc").read_text()
 start=retire.index("native_rear_live_retire_full(")
 assert retire.index("native_rear_live_replacement_read(",start)<retire.index("native_rear_full_cache_retire(",start)<retire.index("dma_buf_unmap_attachment_unlocked",start)
 queue=(a.staged/"native-rear-queue.inc").read_text()
 assert queue.index("native_rear_full_cache_begin(")<queue.index("for (;;) {",queue.index("native_rear_queue_run("))
 lease=(a.staged/"native-rear-video-lease.inc").read_text()
 types=lease[lease.index("struct native_rear_video_lease {"):lease.index("};",lease.index("struct native_rear_video_lease {"))+2]
 helpers=""
 for name in ["native_rear_video_lease_valid","native_rear_video_lease_expose","native_rear_video_lease_stop","native_rear_video_lease_put"]:
  helpers+="static "+("bool " if name.endswith("_valid") else "int ")+fn(lease,name)
 model=(HERE/"test-rear-full-cache-model.c").read_text().replace("/* ACTUAL_LEASE_TYPES */",types).replace("/* ACTUAL_LEASE_HELPERS */",helpers)
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v18.py"))
 assert runtime["IDENTITY"]=="E-NATIVE-REAR-GENERATION-58"
 assert str(runtime["D"]).endswith("generation-20261007-58") and runtime["MARKER"].endswith("_58=1")
 assert 'result={"identity":IDENTITY' in (HERE/"run-rear-cadence-v18.py").read_text()
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-full-cache-") as tmp:
  d=Path(tmp);src=d/"model.c";src.write_text(model)
  for cc in ["gcc","clang"]:
   exe=d/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-Wno-unused-function","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(a.staged),str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   r=subprocess.run([exe],capture_output=True,text=True,check=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   m=re.search(r"FULL_CACHE_PASS assertions=(\d+) negatives=(\d+) frames=240",r.stdout);assert m,r.stdout
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=int(m[1]),negative_cases=int(m[2]),model_handoffs=240))
  # Compile the actual cache C format strings, then pass their emitted output
  # through the real runtime's strict owner/counter/flush parser.
  s=(a.staged/"native-rear-full-cache.inc").read_text()
  formats=[re.findall(r'"NATIVE_REAR_FULL_CACHE [^"\n]*"',s)[0],re.findall(r'"NATIVE_REAR_FULL_CACHE_FLUSH [^"\n]*"',s)[0]]
  src.write_text('#include <stdio.h>\nint main(void){printf('+formats[0]+',2ULL,1U,77U,3U,80U,0U,3U);printf('+formats[1]+',2ULL,3U,1U);return 0;}\n')
  for cc in ["gcc","clang"]:
   exe=d/(cc+"-format");subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   log=subprocess.check_output([exe],text=True);f=runtime["rear_full_cache"](log,{"handoffs":80},2);assert f["queue"]["hits"]==77
 neg=0
 def reject(log,owner=2):
  nonlocal neg
  try:runtime["rear_full_cache"](log,{"handoffs":80},owner)
  except RuntimeError:neg+=1
  else:raise AssertionError("bad cache evidence admitted")
 for line in log.splitlines():
  reject(log.replace(line,""));reject(log+"\n"+line)
  for token in line.split()[1:]:
   k,v=token.split("=");reject(log.replace(line,line.replace(token,k+"=-1")))
   reject(log.replace(line,line+" "+token))
   reject(log.replace(line," ".join(x for x in line.split() if x!=token)))
 for bad in ["hits=76","misses=4","stored=79","evicted=1","retained=4","capacity=3","physical_unmaps_deferred=0","pixel_bytes_read=1","all_stops=7","idle=0","released=2"]:
  key=bad.split("=")[0];changed=re.sub(r"\b"+key+r"=\d+",bad,log);reject(changed)
 reject(log,1);reject(log,3)
 report=dict(status="PASS_ACTUAL_FULL_CACHE_OWNER_GENERATION_ALIAS_FOUR_STOP_FLUSH_AND_FORMAT_PARSER",results=results,parser_negative_cases=neg,original_retirement_and_stop_guards_source_tokens_unchanged=True,cache_hook_after_original_last_hardware_snapshot=True,exact_identity_descriptor_checked=True,hardware_DMA_APIs_are_models=True,physical_hardware_access=False,pixel_bytes_read=0)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":
 try:main()
 except subprocess.CalledProcessError as e:
  print(e.stdout or "",e.stderr or "");raise
