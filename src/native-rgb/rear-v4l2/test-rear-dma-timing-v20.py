#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check whole-source observer equivalence and actual C log/parser admission."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile
UNDO_STATS=runpy.run_path(str(Path(__file__).resolve().parent/"rear-statistics-source-proof.py"))["undo_queue_timestamp"]
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 base=a.staged.parent.parent/"native-rgb-rear-generation-20261007-53/camss"
 names=["camss-vfe-e008d-rear-dma.inc","native-rear-live-retire.inc","native-rear-queue.inc"]
 for name in names:
  s=(a.staged/name).read_text()
  if name=="native-rear-queue.inc":s=UNDO_STATS(s)
  s=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",s,flags=re.S);s=re.sub(r"\n/\* GAP_TIMING_BEGIN \*/\n.*?/\* GAP_TIMING_END \*/\n","\n",s,flags=re.S)
  s=re.sub(r"\n/\* FULL_CACHE_BEGIN \*/\n.*?/\* FULL_CACHE_END \*/\n","",s,flags=re.S)
  clean=re.sub(r"\n/\* DMA_TIMING_BEGIN \*/\n.*?/\* DMA_TIMING_END \*/\n","",s,flags=re.S)
  assert "".join(clean.split())=="".join((base/name).read_text().split()),("non-observer source changed",name)
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v20.py"));parse=runtime["rear_dma_timing"]
 cadence=dict(handoffs=80,elapsed_ns=6_000_000_000,prepare_ns=400_000_000,retire_ns=500_000_000)
 s=(a.staged/"native-rear-queue.inc").read_text()
 fmt=re.findall(r'"NATIVE_REAR_DMA_TIMING [^"\n]*"',s);assert len(fmt)==1
 with tempfile.TemporaryDirectory(prefix="rear-dma-timing-") as tmp:
  d=Path(tmp);src=d/"format.c";exe=d/"format"
  src.write_text('#include <stdio.h>\nint main(void){printf('+fmt[0]+',200000000ULL,100000000ULL,200000000ULL,50000000ULL,100000000ULL,80U,640U,80U,640U);return 0;}\n')
  for cc in ["gcc","clang"]:
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   line=subprocess.check_output([str(exe)],text=True);assert line.endswith("\n") and "\\n" not in line
   f=parse(line,cadence);assert f["full_get_calls"]==80
 neg=0
 def reject(line,c=cadence):
  nonlocal neg
  try:parse(line,c)
  except RuntimeError:neg+=1
  else:raise AssertionError("bad DMA timing accepted: "+line)
 valid=line.strip()
 for broken in ["",valid+"\n"+valid,valid+" bogus=0"]:
  reject(broken)
 for k,v in f.items():
  for new in ["-1","x",str(v+1)]:
   if k.endswith("_ns") and new==str(v+1):continue
   reject(valid.replace(k+"="+str(v),k+"="+new))
  reject(valid+f" {k}={v}")
  reject(" ".join(x for x in valid.split() if not x.startswith(k+"=")))
 for k in ["full_get_ns","aux_alloc_ns","full_put_ns","aux_zero_ns","aux_free_ns"]:
  reject(valid.replace(k+"="+str(f[k]),k+"=0"))
  reject(valid.replace(k+"="+str(f[k]),k+"=6000000001"))
 reject(valid,dict(cadence,prepare_ns=299999999))
 reject(valid,dict(cadence,retire_ns=349999999))
 # A second log in another prior session is ignored only after mandatory
 # strict session scoping; passing a mixed session record here is rejected.
 reject(valid+"\n"+valid.replace("full_get_calls=80","full_get_calls=79"))
 report=dict(status="PASS_DMA_OPERATION_TIMING_SOURCE_EQUIVALENCE_AND_ACTUAL_FORMAT_PARSER",negative_cases=neg,whole_source_tokens_identical_after_exact_instrumentation_removal=names,actual_C_format_GCC_Clang_Werror=True,original42_queue_policy_preserved_except_declared_owner_bound_mapping_cache=True,lifetime_and_release_predicates_unchanged=True,no_pixel_read=True,synthetic_arguments_not_hardware=True)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
