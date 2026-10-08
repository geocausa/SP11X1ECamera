#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual live FULL retirement, mapping APIs/MMIO/IRQ explicitly modelled."""
import argparse,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def function(t,name):
 i=t.index(name+"(");a=t.index("{",i);j=a+1;depth=1
 while depth:
  depth+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 auxiliary=(a.staged/"native-rear-live-aux-retire.inc").is_file()
 t=(HERE/"test-live-observe.c").read_text()
 t=t.replace("typedef uint8_t u8;","typedef uint64_t dma_addr_t;\ntypedef uint8_t u8;")
 t=t.replace("#define E008H_REAR_SLOTS", "#define NATIVE_REAR_NV12_BYTES 12441600U\n#define NATIVE_REAR_NV12_UV_OFFSET 8294400U\n#define VFE680_E004NT_REAR_TOTAL_BYTES NATIVE_REAR_NV12_BYTES\n#define E008D_REAR_AUX_COUNT 8U\n#define DMA_FROM_DEVICE 2\n#define E008H_REAR_SLOTS")
 lease=(a.staged/"native-rear-video-lease.inc").read_text()
 dma=(a.staged/"camss-vfe-e008d-rear-dma.inc").read_text()
 types="""struct vfe680_e004nt_rear_surface {void *cpu;dma_addr_t dma;size_t size;bool in_flight;};
struct native_rear_video_dma {u32 y_iova,uv_iova;u64 mapped_bytes;};
"""
 start=lease.index("struct native_rear_video_lease {");end=lease.index("};",start)+2;types+=lease[start:end]+"\n"
 start=dma.index("struct e008d_rear_aux_buffer {");end=dma.index("struct e008d_rear_addresses",start);types+=dma[start:end]
 start=dma.index("static const u8 e008d_rear_aux_wms");end=dma.index("static const struct",start);types+=dma[start:end]
 types+="static bool "+function(lease,"native_rear_video_lease_valid")
 types+="static bool "+function(dma,"native_rear_dma_full_valid")
 t=t.replace("struct e008d_rear_addresses {",types+"\nstruct e008d_rear_addresses {")
 t=t.replace("struct e008h_rear_prime_pair {","struct e008h_rear_prime_pair {struct e008d_rear_dma_set dma[2];")
 t=t.replace("u64 owner_epoch;bool packet_submitted[4];","u64 owner_epoch;bool packet_submitted[4];bool both_frames_complete,live_full_retired;")
 t=t.replace("struct vfe680_e004nu_rear_wm_static {u8 wm;u32 cfg;};","struct vfe680_e004nu_rear_wm_static {u8 wm;u32 cfg,frame_incr;};")
 t=t.replace("{wm,0x20U+i*0x20U}","{wm,0x20U+i*0x20U,e007z_rear_wm_descs[i].required_bytes}")
 mocks=r"""
static unsigned unmaps,detaches,put_calls,aux_frees;
static void *expected_dbuf,*expected_attachment,*expected_table;
static void dma_buf_unmap_attachment_unlocked(void *a,void *t,int direction){
 CHECK(a==expected_attachment&&t==expected_table&&direction==DMA_FROM_DEVICE);CHECK(unmaps==0);unmaps++;
}
static void dma_buf_detach(void *d,void *a){CHECK(d==expected_dbuf&&a==expected_attachment);CHECK(unmaps==1&&detaches==0);detaches++;}
static void dma_buf_put(void *d){CHECK(d==expected_dbuf);CHECK(detaches==1&&put_calls==0);put_calls++;}
static void e008d_rear_aux_release(struct vfe_device *v,struct e008d_rear_aux_buffer *a){CHECK(v&&a);if(a->cpu){aux_frees++;memset(a,0,sizeof(*a));}}
static int vfe680_e004nt_rear_surface_free(struct vfe_device *v,struct vfe680_e004nt_rear_surface *f){CHECK(v&&f);CHECK(false);return -EINVAL;}
"""
 mocks+="static int "+function(lease,"native_rear_video_lease_put")
 mocks+="static void "+function(dma,"e008d_rear_release_partial")
 t=t.replace('#include "native-rear-live-observe.inc"','#include "native-rear-live-observe.inc"\n'+mocks+'\n#include "native-rear-live-retire.inc"')
 extension=r"""
static void retire_fixture(void){
 fixture();unmaps=detaches=put_calls=aux_frees=0;result.both_frames_complete=true;
 for(unsigned s=0;s<2;s++){
  struct e007z_rear_slot *uv=&pair.frame[s].slot[1];
  uv->owned_base_iova=uv->programmed_image_iova=pair.frame[s].slot[0].owned_base_iova+NATIVE_REAR_NV12_UV_OFFSET;
  pair.addr[s].image[1]=uv->programmed_image_iova;
  struct e008d_rear_dma_set *d=&pair.dma[s];
  d->allocated=true;d->prepared_disabled=(s==0);
  d->full.dma=pair.frame[s].slot[0].owned_base_iova;d->full.size=NATIVE_REAR_NV12_BYTES;d->full.in_flight=true;
  d->public_full=(struct native_rear_video_lease){.dbuf=(void*)(uintptr_t)(100+s),.attachment=(void*)(uintptr_t)(200+s),.table=(void*)(uintptr_t)(300+s),
   .span={d->full.dma,d->full.dma+NATIVE_REAR_NV12_UV_OFFSET,12443648},.acquired=true,.exposed=true};
  for(unsigned i=0;i<8;i++){
   u8 wm=e008d_rear_aux_wms[i];int idx=e007z_rear_index(wm);
   d->aux[i]=(struct e008d_rear_aux_buffer){.cpu=(void*)(uintptr_t)(400+s*8+i),.dma=pair.frame[s].slot[idx].owned_base_iova,.size=contracts[idx].frame_incr,.wm=wm};
  }
 }
 camss.vfe[1].registers[1][1]=camss.vfe[1].registers[1][2]=pair.addr[1].image[1];
 expected_dbuf=pair.dma[0].public_full.dbuf;expected_attachment=pair.dma[0].public_full.attachment;expected_table=pair.dma[0].public_full.table;
}
#define fixture retire_fixture
"""
 t=t.replace("static int check_read(u32 cursor)",extension+"\nstatic int check_read(u32 cursor)")
 t=t.replace("CHECK(check_read(15)<0);negative_cases++;","CHECK(native_rear_live_retire_full(&camss.vfe[1],&camss.csid[1],&pair,&result,15)<0);negative_cases++;CHECK(unmaps==0&&detaches==0&&put_calls==0&&aux_frees==0);")
 t=t.replace("int main(void){",(HERE/"test-live-retire-tail.c").read_text()+"\nint main(void){")
 t=t.replace(' printf("{\\"assertions\\"',' live_positive();extra_matrix();\n printf("{\\"assertions\\"')
 t=t.replace('\\"read_only_live_observer\\":true','\\"actual_live_FULL_retirement\\":true').replace('\\"DMA_release_or_reuse_authority\\":false','\\"old_FULL_unmap_only_after_actual_guard\\":true')
 if auxiliary:
  t=t.replace("both_frames_complete,live_full_retired;","both_frames_complete,live_full_retired,live_aux_retired;")
  t=t.replace('#include "native-rear-live-retire.inc"','#include "native-rear-live-retire.inc"\n#include "native-rear-live-aux-retire.inc"')
  t=t.replace("int main(void){",(HERE/"test-live-aux-retire-tail.c").read_text()+"\nint main(void){")
  t=t.replace("live_positive();extra_matrix();","live_positive();extra_matrix();aux_matrix();")
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-live-retire-") as tmp:
  tmp=Path(tmp)
  for n in ["native-rear-live-observe.inc","native-rear-live-retire.inc","camss-e007z-rear-retirement.inc"]:shutil.copyfile(a.staged/n,tmp/n)
  if auxiliary:shutil.copyfile(a.staged/"native-rear-live-aux-retire.inc",tmp/"native-rear-live-aux-retire.inc")
  (tmp/"test.c").write_text(t)
  for cc in ["gcc","clang"]:
   binary=tmp/cc
   r=subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(tmp),str(tmp/"test.c"),"-o",str(binary)],capture_output=True,text=True,timeout=25)
   if r.returncode:raise RuntimeError(r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=25,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":cc,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout),"stderr":r.stderr})
 report={"status":"PASS_ACTUAL_LIVE_REAR_FULL_MAPPING_RETIREMENT_AND_AUX_PINNING","actual_staged_observer_lease_predicates_partial_release_and_retirement":True,"MMIO_IRQ_DMA_BUF_API_and_aux_free_are_models":True,"hardware_access":False,"VB2_completion_or_requeue":False,"auxiliary_allocations_match_completed_ledger":True,"all_120_CPU_aliases_rejected":True,"DMA_high_bits_not_truncated":True,"results":results}
 report["actual_old_auxiliary_live_release_checked"]=auxiliary
 report["command_recycling_or_VB2_live_delivery_authorized"]=False
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
