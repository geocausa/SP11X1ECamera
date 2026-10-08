#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Test the actual staged rear event queue including SPSC threaded publication."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-event-queue-") as tmp:
  tmp=Path(tmp)
  for n in ["native-rear-event-queue.inc","camss-e008i-rear-observer.h"]:shutil.copyfile(a.staged/n,tmp/n)
  shutil.copyfile(HERE/"test-events.c",tmp/"test.c")
  for cc in ["gcc","clang"]:
   binary=tmp/cc
   r=subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-pthread","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(tmp),tmp/"test.c","-o",binary],capture_output=True,text=True,timeout=25)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],capture_output=True,text=True,timeout=25,
    env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":cc,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout),"stderr":r.stderr})
 report={"status":"PASS_ACTUAL_REAR_SPSC_EVENT_QUEUE_WRAP_OVERFLOW_AND_THREADED_PUBLICATION",
  "results":results,"actual_staged_observer_body_tested":True,"hardware_MMIO_IRQ_route_are_models":True,
  "hardware_access":False,"continuous_image_delivery_or_live_DMA_retirement_proven":False}
 a.report.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report))
if __name__=="__main__":main()
