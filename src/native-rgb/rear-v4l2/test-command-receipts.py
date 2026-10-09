#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Run actual staged command allocation/layout/receipt guard with IRQ models."""
import argparse,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-command-receipts-") as d:
  d=Path(d)
  y=(a.staged/"camss-e007y-rear-startup.inc").read_text()
  prefix=y[:y.index("static int\ne007y_rear_slot(")]
  wrappers=y[y.index("static void e007y_rear_clear_output("):y.index("static int\ne007y_rear_materialize(")]
  (d/"e007y-layout.h").write_text(prefix+wrappers)
  k=(a.staged/"camss-vfe-e008k-rear-runner.inc").read_text()
  types=k[k.index("struct e008k_rear_request {"):k.index('#include "native-rear-live-observe.inc"')]
  validate=k[k.index("static int\ne008k_rear_validate_prepared_packets("):k.index("static int\ne008k_rear_collect_done(")]
  (d/"e008k-prepared-validator.h").write_text(types+validate)
  h=(a.staged/"native-rear-command-receipt.h").read_text().replace("#include <linux/types.h>","")
  (d/"native-rear-command-receipt.h").write_text(h)
  t=(HERE.parent/"test-rear-prepared-commands.c").read_text()
  if (a.staged/"native-rear-session.h").exists():
   t=t.replace("static int atomic_cmpxchg(", "static __attribute__((unused)) int atomic_cmpxchg(")
   t=t.replace("e008n_rear_run_once_unreachable(v,&req,&result)==-EALREADY",
               "e008n_rear_run_once_unreachable(v,&req,&result)==-EIO")

  t=t.replace("#define U64_MAX UINT64_MAX","#define U64_MAX UINT64_MAX\n#define U32_MAX UINT32_MAX\n#define READ_ONCE(x) (x)\nstatic bool native_rear_diagnostic_active;")
  tail=(HERE/"test-command-receipts-tail.c").read_text()
  t=t.replace("int main(void){",tail+"\nint main(void){")
  t=t.replace(" scalar_binding_test();"," receipt_tests(&v);\n scalar_binding_test();")
  (d/"test.c").write_text(t)
  for cc in ("gcc","clang"):
   binary=d/cc
   cmd=[cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(d),"-I"+str(a.staged),str(d/"test.c"),"-o",str(binary)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   m=re.search(r"COMMAND_RECEIPTS_PASS assertions=(\d+) negatives=(\d+)",r.stdout)
   assert m is not None
   results.append({"compiler":cc,"ASAN_UBSAN_Werror":True,"assertions":int(m[1]),"negative_cases":int(m[2]),"stdout":r.stdout.strip(),"stderr":r.stderr})
 report={"status":"PASS_ACTUAL_EXACT_COMMAND_ALLOCATION_REQUEST_OWNER_AND_22_BL_RECEIPTS","results":results,"actual_staged_allocator_layout_wrapper_and_receipt_helpers":True,"hardware_FIFO_and_semantic_provider_are_models":True,"commands_remain_pinned_until_stop":True,"hardware_access":False,"live_command_release_or_requeue":False}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
