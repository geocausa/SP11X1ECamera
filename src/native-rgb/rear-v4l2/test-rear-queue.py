#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual rolling queue and consumed-IOVA ledger; hardware and DMA APIs modelled."""
from pathlib import Path
import argparse,json,os,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent
def fn(t,name):
 i=t.index(name+"(");a=t.index("{",i);j=a+1;depth=1
 while depth:depth+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 t=(HERE/"test-rear-queue-model.c").read_text()
 ledger=(a.staged/"camss-e007z-rear-retirement.inc").read_text()
 ledger=ledger[:ledger.index("static int __used e007z_rear_runtime_authorization")]
 t=t.replace("/* ACTUAL_LEDGER */",ledger+"\n#endif\n")
 dma=(a.staged/"camss-vfe-e008d-rear-dma.inc").read_text();lease=(a.staged/"native-rear-video-lease.inc").read_text()
 types=lease[lease.index("struct native_rear_video_lease {"):lease.index("};",lease.index("struct native_rear_video_lease {"))+2]+"\n"
 types+=dma[dma.index("struct e008d_rear_aux_buffer {"):dma.index("static const struct vfe680_e004nu_rear_wm_static *")]
 h=(a.staged/"camss-vfe-e008h-rear-prime.inc").read_text()
 types+=h[h.index("static const u8 e008h_rear_program_wms"):h.index("static int\ne008h_rear_addr_index")]
 k=(a.staged/"camss-vfe-e008k-rear-runner.inc").read_text()
 types+=k[k.index("struct e008k_rear_request {"):k.index('#include "native-rear-live-observe.inc"')]
 t=t.replace("/* ACTUAL_TYPES */",types)
 code="static bool "+fn(lease,"native_rear_video_lease_valid")+"static bool "+fn(dma,"native_rear_dma_full_valid")
 for name,kind in [("e008h_rear_addr_index","int"),("e008h_rear_build_binding","int"),("e008h_rear_validate_pair_disjoint","int"),("e008h_rear_check_slot_addresses","int"),("e008h_rear_write_slot_addresses","int"),("e008h_rear_fault_ledgers","void"),("e008h_rear_observe_consumed","int"),("e008h_rear_both_complete","bool")]:
  code+="static "+kind+" "+fn(h,name)
 t=t.replace("/* ACTUAL_PRIME_HELPERS */",code)
 t=t.replace("/* ACTUAL_AUX_FREE */","static void "+fn(dma,"e008d_rear_aux_release"))
 t=t.replace("/* ACTUAL_RETIRE */",'#include "native-rear-live-retire.inc"\n#include "native-rear-live-aux-retire.inc"')
 if (a.staged/"native-rear-output-update.inc").exists():
  t=t.replace("/* ACTUAL_QUEUE */","static int csid680_native_rear_output_update(struct csid_device *c,u64 owner){CHECK(c&&owner==7);return step();}\n/* ACTUAL_QUEUE */")
 t=t.replace("/* ACTUAL_QUEUE */",'#include "native-rear-queue.inc"')
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-rolling-queue-") as temp:
  d=Path(temp);(d/"test.c").write_text(t)
  for cc in ("gcc","clang"):
   binary=d/cc;cmd=[cc,"-std=gnu11","-Wall","-Wextra","-Werror","-Wno-unused-function","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(a.staged),str(d/"test.c"),"-o",str(binary)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   m=re.search(r"REAR_QUEUE_PASS assertions=(\d+) live_frames=(\d+) negative_cases=(\d+)",r.stdout);assert m
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=int(m[1]),live_frames=int(m[2]),negative_cases=int(m[3])))
 report=dict(status="PASS_ACTUAL_REAR_ROLLING_QUEUE_LEDGER_RETIREMENT_AND_BUFFER_REUSE",actual_staged_queue_ledger_address_writes_and_output_retirement=True,hardware_and_DMA_BUF_allocation_APIs_are_models=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
