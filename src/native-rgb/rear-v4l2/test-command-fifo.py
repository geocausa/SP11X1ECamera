#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile unchanged staged FIFO wait/commit and receipt bridge with API models."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def function(t,n):
 i=t.index(n+"(");a=t.index("{",i);j=a+1;depth=1
 while depth:
  depth+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 t=(a.staged/"camss.c").read_text();bridge=(a.staged/"camss-e008k-rear-rtcdm-bridge.inc").read_text()
 functions=""
 for name in ("camss_rtcdm1_windows_wait","camss_rtcdm1_windows_fifo0_commit_receipt","camss_rtcdm1_windows_fifo0_commit"):
  functions+="static int "+function(t,name)
 for name in ("e008k_rear_rtcdm_submit_bl_receipt","e008k_rear_rtcdm_receipt_current"):
  functions+="int "+function(bridge,name)
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-command-fifo-") as d:
  d=Path(d);(d/"actual-fifo-functions.h").write_text(functions)
  (d/"native-rear-command-receipt.h").write_text((a.staged/"native-rear-command-receipt.h").read_text().replace("#include <linux/types.h>",""))
  for cc in ("gcc","clang"):
   binary=d/cc
   r=subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(d),str(HERE/"test-command-fifo.c"),"-o",str(binary)],capture_output=True,text=True,timeout=30)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":cc,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout),"stderr":r.stderr})
 report={"status":"PASS_ACTUAL_SERIALIZED_FIFO_RECEIPT_CAPTURE_AND_CURRENT_CHECK","results":results,"actual_staged_wait_commit_and_bridge":True,"IRQ_MMIO_completion_and_timeouts_are_models":True,"hardware_access":False,"hardware_BL_DONE_contract_independently_reproven":False}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
