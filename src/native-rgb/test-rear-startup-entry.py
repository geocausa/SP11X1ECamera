#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Current typed startup -> real E008N wrapper; no hardware authorization."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def checked(command,env=None):
 r=subprocess.run(command,capture_output=True,text=True,env=env)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True)
 p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 if a.report.exists():raise SystemExit("report identity exists")
 stage=a.staged.resolve()
 for name in ["native-rear-startup-entry.inc","native-rear-startup-compose.inc"]:
  if (stage/name).read_bytes()!=(HERE/name).read_bytes():raise RuntimeError("source stage drift")
 runner=(stage/"camss-vfe-e008k-rear-runner.inc").read_text()
 types=runner[runner.index("struct e008k_rear_request {"):runner.index("static int\ne008k_rear_submit_packet(")]
 validator=runner[runner.index("static int\ne008k_rear_validate_prepared_packets("):runner.index("static int\ne008k_rear_collect_done(")]
 composer=(HERE/"test-rear-startup-compose.c").read_text()
 initializer=composer[composer.index("static void initialize("):composer.index("static void check_self_pointers(")]
 text=(HERE/"test-rear-startup-entry.c").read_text()
 for marker,value in [("/* RUNNER_TYPES */",types),("/* PREPARED_VALIDATOR */",validator),("/* SYNTHETIC_INITIALIZER */",initializer)]:
  if text.count(marker)!=1:raise RuntimeError("host marker drift")
  text=text.replace(marker,value)
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-startup-entry-") as td:
  td=Path(td);source=td/"test.c";source.write_text(text)
  for compiler in ["gcc","clang"]:
   executable=shutil.which(compiler)
   if not executable:raise RuntimeError("required compiler missing")
   binary=td/compiler
   checked([executable,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
            "-fsanitize=address,undefined","-fno-omit-frame-pointer",
            "-I"+str(HERE),"-I"+str(stage),str(source),"-o",str(binary)])
   run=checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if "NATIVE_REAR_STARTUP_ENTRY_PASS" not in run.stdout:raise RuntimeError("missing test marker")
   results.append({"compiler":compiler,"Werror":True,"ASAN_UBSAN":True,"stdout":run.stdout.strip(),"stderr":run.stderr})
 report={"status":"PASS_TYPED_STARTUP_TO_REAL_SINGLE_USE_WRAPPER",
  "actual_composer_full_semantic_types_and_command_materializer":True,
  "actual_E008N_wrapper_and_prepared_validator":True,
  "route_and_unused_runner_function_host_mocks":True,"runtime_runner_calls":0,
  "host_only_consumption_resets_for_independent_cases":True,
  "no_production_consumption_reset_or_runtime_hook":True,
  "production_runtime_authorization_still_denied":True,
  "allocation_cleanup_invalid_generation_and_repeated_call_checked":True,
  "caller_inputs_synthetic":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
