#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual rear live replacement observer against actual consumed-IOVA ledger."""
import argparse,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);p.add_argument("--observer",type=Path)
 a=p.parse_args();assert not a.report.exists();observer=a.observer or a.staged/"native-rear-live-observe.inc"
 text=observer.read_text()
 assert not re.search(r"\b(?:writel(?:_relaxed)?|dma_buf_put|dma_free_coherent|vb2_buffer_done|e007z_rear_release_ledger)\s*\(",text)
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-live-observe-") as tmp:
  tmp=Path(tmp)
  shutil.copyfile(a.staged/"camss-e007z-rear-retirement.inc",tmp/"camss-e007z-rear-retirement.inc")
  shutil.copyfile(observer,tmp/"native-rear-live-observe.inc");shutil.copyfile(HERE/"test-live-observe.c",tmp/"test.c")
  for cc in ["gcc","clang"]:
   binary=tmp/cc
   r=subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(tmp),str(tmp/"test.c"),"-o",str(binary)],capture_output=True,text=True,timeout=25)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=25,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":cc,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout),"stderr":r.stderr})
 report={"status":"PASS_ACTUAL_REAR_LIVE_REPLACEMENT_READ_ONLY_OBSERVATION","results":results,"hardware_access":False,"hardware_MMIO_and_IRQ_are_models":True,"DMA_release_or_reuse_authority":False}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
