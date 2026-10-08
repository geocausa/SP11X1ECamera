#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual staged command retirement/free/tombstone; MMIO/IRQ are explicit models."""
import argparse,json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def function(t,name):
 i=t.index(name+"(");a=t.index("{",i);j=a+1;depth=1
 while depth:depth+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 with tempfile.TemporaryDirectory(prefix="rear-command-retire-") as temp:
  d=Path(temp);y=(a.staged/"camss-e007y-rear-startup.inc").read_text()
  (d/"e007y-layout.h").write_text(y[:y.index("static int\ne007y_rear_slot(")]+y[y.index("static void e007y_rear_clear_output("):y.index("static int\ne007y_rear_materialize(")])
  k=(a.staged/"camss-vfe-e008k-rear-runner.inc").read_text()
  (d/"e008k-prepared-validator.h").write_text(k[k.index("struct e008k_rear_request {"):k.index('#include "native-rear-live-observe.inc"')]+k[k.index("static int\ne008k_rear_validate_prepared_packets("):k.index("static int\ne008k_rear_collect_done(")])
  (d/"native-rear-command-receipt.h").write_text((a.staged/"native-rear-command-receipt.h").read_text().replace("#include <linux/types.h>",""))
  lease=(a.staged/"native-rear-video-lease.inc").read_text();dma=(a.staged/"camss-vfe-e008d-rear-dma.inc").read_text()
  types="""#define E008H_REAR_SLOTS 2
#define E007Z_REAR_WMS 10
#define E008D_REAR_AUX_COUNT 8
#define NATIVE_REAR_NV12_BYTES 12441600U
#define NATIVE_REAR_NV12_UV_OFFSET 8294400U
#define VFE680_E004NT_REAR_TOTAL_BYTES NATIVE_REAR_NV12_BYTES
struct csid_device {int model;};
struct vfe680_e004nt_rear_surface {void *cpu;dma_addr_t dma;size_t size;bool in_flight;};
struct native_rear_video_dma {u32 y_iova,uv_iova;u64 mapped_bytes;};
struct e007z_rear_frame {bool active,faulted,pending;u64 owner_epoch,request_generation;struct {u32 owned_base_iova,owned_bytes;}slot[10];};
struct native_rear_live_observation {int model;};
"""
  start=lease.index("struct native_rear_video_lease {");types+=lease[start:lease.index("};",start)+2]+"\n"
  start=dma.index("struct e008d_rear_aux_buffer {");types+=dma[start:dma.index("struct e008d_rear_addresses",start)]
  start=dma.index("static const u8 e008d_rear_aux_wms");types+=dma[start:dma.index("static const struct",start)]
  types+="struct e008h_rear_prime_pair {struct e008d_rear_dma_set dma[2];struct e007z_rear_frame frame[2];};\n"
  for source,name in [(lease,"native_rear_video_lease_valid"),(dma,"native_rear_dma_full_valid"),((a.staged/"native-rear-live-retire.inc").read_text(),"native_rear_live_full_retired_valid"),((a.staged/"native-rear-live-aux-retire.inc").read_text(),"native_rear_live_aux_retired_valid"),((a.staged/"camss-e007z-rear-retirement.inc").read_text(),"e007z_rear_spans_overlap")]:
   types+="static bool "+function(source,name)
  t=(HERE.parent/"test-rear-prepared-commands.c").read_text()
  t=t.replace("typedef uint64_t u64;","typedef unsigned long long u64;")
  t=t.replace("#define U64_MAX UINT64_MAX","#define U64_MAX UINT64_MAX\n#define U32_MAX UINT32_MAX\n#define READ_ONCE(x) (x)\nstatic bool native_rear_diagnostic_active;")
  t=t.replace("int main(void){",(HERE/"test-command-receipts-tail.c").read_text()+"\n"+types+"\n"+(HERE/"test-command-retire-tail.c").read_text()+"\nint main(void){")
  t=t.replace(" scalar_binding_test();"," receipt_tests(&v);\n command_retire_tests(&v);\n scalar_binding_test();")
  (d/"test.c").write_text(t)
  results=[]
  for cc in ("gcc","clang"):
   binary=d/cc;cmd=[cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(d),"-I"+str(a.staged),str(d/"test.c"),"-o",str(binary)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   m=re.search(r"COMMAND_RETIRE_PASS assertions=(\d+) negatives=(\d+) CPU_aliases=(\d+) aux_aliases=(\d+) DMA_aliases=(\d+)",r.stdout);assert m
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=int(m[1]),negative_cases=int(m[2]),command_CPU_aliases=int(m[3]),auxiliary_CPU_aliases=int(m[4]),command_output_DMA_aliases=int(m[5]),stdout=r.stdout.strip()))
 report=dict(status="PASS_ACTUAL_LIVE_COMMAND_RETIREMENT_AND_POST_STOP_ZERO_STATE_RELEASE",results=results,actual_staged_allocator_layout_receipts_alias_guard_live_retire_and_cleanup=True,MMIO_IRQ_semantic_provider_and_output_contracts_are_models=True,hardware_access=False,live_command_reuse=False,VB2_completion=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
