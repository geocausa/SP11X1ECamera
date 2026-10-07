#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Whole real rear semantic/DMI/allocator/materializer test. No hardware."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def checked(command,env=None):
 p=subprocess.run(command,capture_output=True,text=True,env=env)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True)
 p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 if a.report.exists():raise SystemExit("report already exists")
 stage=a.staged.resolve()
 for name in ["native-rear-startup-compose.inc","native-rear-startup-iq.inc","native-rear-startup-statistics.inc"]:
  if (stage/name).read_bytes()!=(HERE/name).read_bytes():raise RuntimeError("source/stage drift")
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-full-startup-") as directory:
  tmp=Path(directory)
  for compiler in ["gcc","clang"]:
   executable=shutil.which(compiler)
   if not executable:raise RuntimeError("required compiler missing")
   binary=tmp/compiler
   checked([executable,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
            "-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(stage),
            str(HERE/"test-rear-startup-compose.c"),"-o",str(binary)])
   r=checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                                    UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"))
   if "NATIVE_REAR_COMPLETE_STARTUP_PASS" not in r.stdout:raise RuntimeError("missing result")
   results.append({"compiler":compiler,"Werror":True,"ASAN_UBSAN":True,
                   "stdout":r.stdout.strip(),"stderr":r.stderr})
 report={"status":"PASS_COMPLETE_REAR_STARTUP_COMPOSITION_AND_MATERIALIZATION",
         "actual_full_kernel_semantic_types_providers_layout_allocator_materializer":True,
         "host_allocation_and_DMA_addresses_simulated":True,
         "caller_tuning_statistics_and_adaptive_inputs_synthetic":True,
         "independent_IPA_producers_or_photometric_quality_proven":False,
         "transactional_composition_and_late_materialization_failure":True,
         "self_pointer_relocation_after_heap_workspace_release_checked":True,
         "hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
