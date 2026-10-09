#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual staged formatter, only declared epoch-wait change, malformed measurement rejection."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 s=(a.staged/"native-rear-queue.inc").read_text();s=re.sub(r"\n/\* STARTUP_SPARE_BEGIN \*/\n.*?/\* STARTUP_SPARE_END \*/\n","\n",s,flags=re.S)
 s=re.sub(r"\n/\* GAP_TIMING_BEGIN \*/\n.*?/\* GAP_TIMING_END \*/\n","\n",s,flags=re.S)
 s=re.sub(r"\n/\* FULL_CACHE_BEGIN \*/\n.*?/\* FULL_CACHE_END \*/\n","",s,flags=re.S)
 s=re.sub(r"\n/\* DMA_TIMING_BEGIN \*/\n.*?/\* DMA_TIMING_END \*/\n","",s,flags=re.S)
 baseline=(HERE/"native-rear-queue-stable-v2.inc").read_text()
 epoch_wait=("  epoch = csid680_e008i_rear_epoch0_seq(csid);\n"
 "  ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch, req->epoch_timeout_us);\n"
 "  if (ret) {\n"
 "   e008d_rear_release_partial(vfe, &next->dma[1]);\n"
 "   break;\n"
 "  }\n")
 assert baseline.count(epoch_wait)==1
 baseline=baseline.replace(epoch_wait,"",1).replace("  u32 epoch;\n","",1)
 # Remove only the exact observer's additions, then compare the full source.
 clean=re.sub(r"^.*(?:u64 profile_started|u64 profile_drain|u64 profile_epoch|u32 profile_first_epoch).*\n","",s,flags=re.M)
 clean=re.sub(r"^\s*tick = ktime_get_ns\(\);\n","",clean,flags=re.M)
 clean=re.sub(r"^\s*profile_\w+ \+= ktime_get_ns\(\) - tick;\n","",clean,flags=re.M)
 clean=re.sub(r'\n dev_info\(vfe->camss->dev,\n  "NATIVE_REAR_CADENCE .*?profile_retire\);\n',"",clean,flags=re.S)
 assert "".join(clean.split())=="".join(baseline.split()),"measurement changed an existing queue branch or operation"
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v12.py"));parse=runtime["rear_cadence"];neg=0
 fmt=re.findall(r'"NATIVE_REAR_CADENCE [^"\n]*"',s);assert len(fmt)==1
 with tempfile.TemporaryDirectory(prefix="rear-cadence-format-") as tmp:
  d=Path(tmp);src=d/"format.c";exe=d/"format"
  src.write_text('#include <stdio.h>\nint main(void){printf('+fmt[0]+',6000000000ULL,160U,80U,100ULL,200ULL,100000000ULL,300ULL,0ULL,400ULL,3100000000ULL,90000000ULL);return 0;}\n')
  for cc in ["gcc","clang"]:
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(src),"-o",str(exe)],check=True,capture_output=True,text=True)
   line=subprocess.check_output([str(exe)],text=True)
   assert line.endswith("\n") and "\\n" not in line
   f=parse(line,{"handoffs":80});assert f["epoch_delta"]==160 and f["collect_ns"]==3100000000
 def reject(line):
  nonlocal neg
  try:parse(line,{"handoffs":80})
  except RuntimeError:neg+=1
  else:raise AssertionError("bad timing accepted: "+line)
 valid=line.strip()
 reject("");reject(valid+valid);reject(valid+" bogus=0")
 for k,value in f.items():
  reject(valid.replace(k+"="+str(value),k+"=-1"))
  reject(valid.replace(k+"="+str(value),k+"=x"))
  reject(valid+f" {k}={value}")
 for k in ["drain_ns","pending_ns","prepare_ns","observe_ns","epoch_wait_ns","program_ns","collect_ns","retire_ns"]:
  reject(valid.replace(k+"="+str(f[k]),k+"=6000000001"))
 reject(valid.replace("elapsed_ns=6000000000","elapsed_ns=0"))
 reject(valid.replace("epoch_delta=160","epoch_delta=78"))
 reject(valid.replace("handoffs=80","handoffs=79"))
 reject(valid.replace("policy_changes=1","policy_changes=0"))
 reject(valid.replace("epoch_wait_ns=0","epoch_wait_ns=1"))
 reject(valid.replace("pixel_bytes_read=0","pixel_bytes_read=1"))
 reject(valid.replace("prepare_ns=100000000","prepare_ns=3000000000"))
 probe=dict(callback_intervals=79,timestamp_kind="driver_completion_not_sensor_SOF",callback_span_seconds=5.0,callback_interval_rate_fps=15.8,start_to_first_callback_seconds=0.5,last_callback_to_release_seconds=0.1,stop_release_seconds=0.08,completion_timestamp_span_ns=5_000_000_000,completion_gap_min_ns=60_000_000,completion_gap_max_ns=70_000_000,elapsed_seconds=5.6)
 runtime["validate_probe_cadence"](probe)
 for k in list(probe):
  broken=probe.copy();broken[k]=None
  try:runtime["validate_probe_cadence"](broken)
  except (RuntimeError,TypeError):neg+=1
  else:raise AssertionError("bad app timing accepted: "+k)
 report=dict(status="PASS_ACTUAL_CADENCE_FORMAT_PARSER_AND_ONLY_DECLARED_EPOCH_WAIT_CHANGE",negative_cases=neg,actual_staged_C_formatter_GCC_Clang_Werror=True,only_declared_per_handoff_epoch_wait_removed=True,other_queue_source_tokens_identical_to_qualified_baseline=True,hardware_access=False,pixel_bytes_read=0,fixture_arguments_are_synthetic=True)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
