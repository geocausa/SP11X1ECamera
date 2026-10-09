#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile actual timing helpers/log; prove exact queue token equivalence and admission."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile,os
UNDO_STATS=runpy.run_path(str(Path(__file__).resolve().parent/"rear-statistics-source-proof.py"))["undo_queue_timestamp"]
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 s=UNDO_STATS((a.staged/"native-rear-queue.inc").read_text());s=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",s,flags=re.S)
 clean=re.sub(r"\n/\* GAP_TIMING_BEGIN \*/\n.*?/\* GAP_TIMING_END \*/\n","\n",s,flags=re.S)
 base=a.staged.parent.parent/"native-rgb-rear-generation-20261007-56/camss/native-rear-queue.inc"
 assert "".join(clean.split())=="".join(base.read_text().split()),"timing changed queue authority or operation"
 blocks=re.findall(r"/\* GAP_TIMING_BEGIN \*/\n#ifdef __KERNEL__\n(.*?)\n#endif\n/\* GAP_TIMING_END \*/",s,re.S)
 logs=[x for x in blocks if "NATIVE_REAR_GAP_TIMING owner=" in x];assert len(logs)==1
 assert "native_rear_gap_complete(buffer->vb.vb2_buf.timestamp, buffer->vb.sequence);" in s
 assert s.index("native_rear_gap_complete(buffer->vb.vb2_buf.timestamp")<s.index("vb2_buffer_done")
 helper=(a.staged/"native-rear-gap-timing.inc").read_text()
 source=('#include <stdio.h>\n#include <stdint.h>\n#include <string.h>\n#include <assert.h>\n'
 'typedef unsigned long long u64;typedef uint32_t u32;\n'
 '#define dev_info(dev,...) printf(__VA_ARGS__)\n'+helper+
 '\nstatic void emit(void) {\n'+logs[0]+'\n}\n'+r"""
int main(void) {
 unsigned assertions=0;
 for(u32 owner=1;owner<=3;owner++) {
  memset(&native_rear_gap,0,sizeof(native_rear_gap));native_rear_gap.owner=owner;
  u64 now=1000000123ULL*owner;native_rear_gap_complete(now,0);
  for(u32 seq=1;seq<=80;seq++) {
   u64 collect=(seq==17U+owner ? 60000000ULL : 30000000ULL);
   if(seq==80)collect=100000000ULL; /* Extra raced STOP completion, excluded. */
   native_rear_gap_stage_record(&native_rear_gap.prepare,1000000ULL,seq);
   native_rear_gap_stage_record(&native_rear_gap.observe,50000ULL,seq);
   native_rear_gap_stage_record(&native_rear_gap.program,50000ULL,seq);
   native_rear_gap_stage_record(&native_rear_gap.collect,collect,seq);
   native_rear_gap_stage_record(&native_rear_gap.retire,1000000ULL,seq);
   now+=collect+2100000ULL;native_rear_gap_complete(now,seq);
   assert(native_rear_gap.completions==(seq<80 ? seq+1 : 80));assertions++;
  }
  assert(native_rear_gap.intervals==79);assertions++;
  assert(native_rear_gap.long_gaps==1);assertions++;
  assert(native_rear_gap.max_gap_sequence==17+owner);assertions++;
  assert(native_rear_gap.first_long_sequence==17+owner);assertions++;
  assert(native_rear_gap.gap_max_ns==62100000ULL);assertions++;
  assert(native_rear_gap.max_gap_collect_ns==60000000ULL);assertions++;
  assert(native_rear_gap.collect.max_ns==100000000ULL);assertions++;
  assert(native_rear_gap.collect.max_sequence==80);assertions++;
  emit();
 }
 fprintf(stderr,"ASSERTIONS=%u PREFIXES=3 INPUT_COMPLETIONS=243 OBSERVED_COMPLETIONS=240\n",assertions);
 return 0;
}
""")
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v20.py"));parse=runtime["rear_gap_timing"]
 cadence=dict(elapsed_ns=4_000_000_000,handoffs=80,prepare_ns=100_000_000,observe_ns=10_000_000,program_ns=10_000_000,collect_ns=3_000_000_000,retire_ns=100_000_000)
 probe=dict(completion_timestamp_span_ns=79*32100000+30000000,completion_gap_min_ns=32100000,completion_gap_max_ns=62100000)
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-gap-timing-") as tmp:
  d=Path(tmp);src=d/"model.c";src.write_text(source)
  for cc in ["gcc","clang"]:
   exe=d/cc
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   r=subprocess.run([str(exe)],capture_output=True,text=True,check=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   assert "ASSERTIONS=264" in r.stderr and "\\n" not in r.stdout
   lines=r.stdout.splitlines();assert len(lines)==3
   for owner,line in enumerate(lines,1):assert parse(line,cadence,probe,owner)["max_gap_sequence"]==17+owner
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=264,synthetic_input_completions=243,observed_prefix_completions=240))
 neg=0;valid=lines[1];f=parse(valid,cadence,probe,2)
 def reject(log,c=cadence,p=probe,owner=2):
  nonlocal neg
  try:parse(log,c,p,owner)
  except RuntimeError:neg+=1
  else:raise AssertionError("bad gap evidence accepted:"+log)
 for bad in ["",valid+"\n"+valid,valid+" extra=0"]:reject(bad)
 for k,v in f.items():
  for replacement in ["-1","x"]:
   reject(valid.replace(k+"="+str(v),k+"="+replacement))
  reject(valid+" "+k+"="+str(v))
  reject(" ".join(x for x in valid.split() if not x.startswith(k+"=")))
 for k,v in [("owner",1),("completions",81),("intervals",80),("span_ns",probe["completion_timestamp_span_ns"]+1),
             ("gap_max_ns",62100001),("max_gap_sequence",80),("long_gaps",0),("long_gaps",80),
             ("first_long_sequence",0),("prefix_buffers",81),("policy_changes",1),("pixel_bytes_read",1)]:
  reject(re.sub(r"\b"+k+r"=\d+",k+"="+str(v),valid))
 for stage in ["prepare","observe","program","collect","retire"]:
  reject(re.sub(r"\b"+stage+r"_max_sequence=\d+",stage+"_max_sequence=0",valid))
  reject(re.sub(r"\b"+stage+r"_max_ns=\d+",stage+"_max_ns=0",valid))
  reject(re.sub(r"\bmax_gap_"+stage+r"_ns=\d+","max_gap_"+stage+"_ns="+str(f[stage+"_max_ns"]+1),valid))
 reject(valid,owner=1);reject(valid,owner=3)
 # No-long-gap fixture must use zero first ordinal, still requires actual probe agreement.
 short=re.sub(r"\bgap_max_ns=\d+","gap_max_ns=32100000",valid)
 short=short.replace("long_gaps=1","long_gaps=0").replace("first_long_sequence=19","first_long_sequence=0")
 pshort=dict(probe,completion_gap_max_ns=32100000)
 assert parse(short,cadence,pshort,2)["long_gaps"]==0
 reject(short.replace("first_long_sequence=0","first_long_sequence=19"),p=pshort)
 report=dict(status="PASS_ACTUAL_COMPLETION_GAP_TIMING_SOURCE_MODEL_AND_FORMAT_PARSER",results=results,parser_negative_cases=neg,
             queue_tokens_identical_to44_after_exact_tag_removal=True,actual_staged_helper_and_log_compiled=True,
             timestamp_precision_matches_V4L2_timeval=True,first80_prefix_exactly_compared_to_application=True,
             extra_STOP_completions_excluded_from_prefix=True,timing_is_not_release_authority=True,hardware_access=False,pixel_bytes_read=0)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
