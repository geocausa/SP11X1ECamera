#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual staged rear NV12 address, FULL MMIO, round/clamp and ten-WM ledger."""
import argparse,json,os,re,subprocess,tempfile
from pathlib import Path
def function(s,name):
 i=s.index(name+"(");a=s.index("{",i);j=a+1;depth=1
 while depth:
  depth+=(s[j]=="{")-(s[j]=="}");j+=1
 return s[i:j]+"\n"
PRE=r"""
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t u64;
typedef uint64_t dma_addr_t;
#define __used __attribute__((unused))
#define __iomem
#define static_assert(expr,...) _Static_assert(expr,#expr)
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
#define BIT(x) (1U<<(x))
#define U32_MAX UINT32_MAX
#define IS_ALIGNED(x,a) (!((x)&((a)-1)))
#define CAMSS_X1E80100 99
#define VFE_BUS_WRITE_CLIENT_CFG_EN 1U
struct res {int version;};struct camss {struct res *res;void *dev;};
struct vfe_device {struct camss *camss;unsigned id;bool lite;u8 *base;};
static bool vfe_is_lite(struct vfe_device *v){return v->lite;}
static bool vfe680_x1e_dma_span_32bit(dma_addr_t d,size_t n){return d&&n&&d+n<=0x100000000ULL;}
static u32 mem[0xc000/4];static unsigned assertions,writes;
#define CHECK(x) do {assertions++;if(!(x)){fprintf(stderr,"failed line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static u32 readl(void *p){ptrdiff_t o=(u8*)p-(u8*)mem;CHECK(o>=0&&(size_t)o<sizeof(mem)&&!(o&3));return mem[o/4];}
static void writel_relaxed(u32 v,void *p){ptrdiff_t o=(u8*)p-(u8*)mem;CHECK(o>=0&&(size_t)o<sizeof(mem)&&!(o&3));CHECK(!(o>=0xe40&&o<=0xe5c));CHECK(!(o>=0xf40&&o<=0xf5c));CHECK(o!=0xc58);mem[o/4]=v;writes++;}
static void *vfe680_x1e_bus_reg(struct vfe_device *v,unsigned wm,unsigned off){return v->base+0xe00+wm*0x100+off;}
static struct res board={99};static struct camss cam={&board,&board};
static struct vfe_device vfe={&cam,1,false,(u8*)mem};
"""
MAIN=r"""
static void init(void){
 memset(mem,0,sizeof(mem));writes=0;vfe=(struct vfe_device){&cam,1,false,(u8*)mem};
}
static void valid_bus(void){
 init();struct e006p_output_path path={.bit_width=8,.enabled=true};
 for(unsigned wm=0;wm<2;wm++){
  for(unsigned word=0;word<=10;word++){
   u32 expected,base=wm?0x9e60:0x9c60,reg=word?base+0x10+(word-1)*4:base;
   CHECK(e006p_roundclamp_word(&path,wm!=0,word,&expected)==0);mem[reg/4]=expected;
  }
  native_rear_nv12_write_full_disabled(&vfe,wm);
 }
}
int main(void){
 CHECK(NATIVE_REAR_NV12_Y_BYTES==8294400U);
 CHECK(NATIVE_REAR_NV12_UV_BYTES==4147200U);
 CHECK(NATIVE_REAR_NV12_BYTES==12441600U);
 CHECK(NATIVE_REAR_NV12_ALLOCATION_BYTES==12443648U);
 CHECK(vfe680_e004nu_rear_wm_contract_valid());
 struct vfe680_e004nt_rear_surface surf={.cpu=&board,.dma=0x20000000,.size=NATIVE_REAR_NV12_ALLOCATION_BYTES};
 struct vfe680_e004nt_rear_wm_addrs addr={};
 CHECK(vfe680_e004nt_rear_surface_addrs(&vfe,&surf,&addr)==0);
 CHECK(addr.y_meta==0&&addr.c_meta==0);
 CHECK(addr.y_image==surf.dma&&addr.c_image==surf.dma+NATIVE_REAR_NV12_UV_OFFSET);
 for(unsigned i=0;i<6;i++){
  struct vfe680_e004nt_rear_surface bad=surf;
  switch(i){case 0:bad.size--;break;case 1:bad.cpu=NULL;break;case 2:bad.in_flight=true;break;
   case 3:bad.dma++;break;case 4:bad.dma=0xff800000;break;case 5:bad.dma=0;break;}
  struct vfe680_e004nt_rear_wm_addrs untouched={1,2,3,4},out=untouched;
  CHECK(vfe680_e004nt_rear_surface_addrs(&vfe,&bad,&out)!=0);CHECK(!memcmp(&out,&untouched,sizeof(out)));
 }
 init();CHECK(native_rear_nv12_cold_admit(&vfe)==0&&writes==0);
 for(unsigned i=0;i<10;i++){
  init();mem[(0xe00+vfe680_e004nu_rear_wm_contract[i].wm*0x100)/4]=1;
  CHECK(native_rear_nv12_cold_admit(&vfe)==-EBUSY&&writes==0);
 }
 for(unsigned wm=0;wm<2;wm++){
  init();mem[(0xe00+wm*0x100+0x48)/4]=1;
  CHECK(native_rear_nv12_cold_admit(&vfe)==-EOPNOTSUPP&&writes==0);
 }
 valid_bus();CHECK(writes==22);CHECK(native_rear_nv12_full_readback(&vfe)==0);
 const unsigned offsets[]={0,0x48,0x1c,0x0c,0x10,0x14,0x18,0x08,0x30,0x34,0x38,0x3c};
 for(unsigned wm=0;wm<2;wm++){
  for(unsigned i=0;i<ARRAY_SIZE(offsets);i++){
   valid_bus();mem[(0xe00+wm*0x100+offsets[i])/4]^=1;
   CHECK(native_rear_nv12_full_readback(&vfe)==-EIO);
  }
  for(unsigned word=0;word<=10;word++){
   valid_bus();unsigned base=wm?0x9e60:0x9c60,reg=word?base+0x10+(word-1)*4:base;
   mem[reg/4]^=1;CHECK(native_rear_nv12_full_readback(&vfe)==-EIO);
  }
 }
 struct e007z_rear_binding b[10]={};
 for(unsigned i=0;i<10;i++){
  const struct e007z_rear_wm_desc *d=&e007z_rear_wm_descs[i];
  b[i]=(struct e007z_rear_binding){d->wm,0x40000000+i*0x01000000,d->required_bytes,0x40000000+i*0x01000000+d->image_offset};
 }
 b[0].owned_base_iova=b[0].programmed_image_iova=addr.y_image;
 b[1].owned_base_iova=b[1].programmed_image_iova=addr.c_image;
 struct e007z_rear_frame frame={};
 CHECK(e007z_rear_bind(&frame,7,1,b)==0);
 CHECK(frame.pending==0x3ff);
 CHECK(e007z_rear_release_ledger(&frame,7,1,true,true)==-EBUSY);
 CHECK(e007z_rear_observe(&frame,8,1,1,0,addr.y_image)==-ESTALE);
 CHECK(e007z_rear_observe(&frame,7,2,1,0,addr.y_image)==-ESTALE);
 CHECK(e007z_rear_observe(&frame,7,1,0,0,addr.y_image)==-EAGAIN);
 for(unsigned i=0;i<10;i++){
  CHECK(e007z_rear_observe(&frame,7,1,BIT(e007z_rear_wm_descs[i].comp_group),b[i].wm,b[i].programmed_image_iova)==0);
  CHECK(e007z_rear_observe(&frame,7,1,BIT(e007z_rear_wm_descs[i].comp_group),b[i].wm,b[i].programmed_image_iova)==-EALREADY);
 }
 CHECK(!frame.pending);CHECK(!e007z_rear_retireable(&frame,7,1,false,true));
 CHECK(!e007z_rear_retireable(&frame,7,1,true,false));
 CHECK(e007z_rear_retireable(&frame,7,1,true,true));
 CHECK(e007z_rear_release_ledger(&frame,7,1,true,true)==0);
 for(unsigned i=0;i<2;i++){
  memset(&frame,0,sizeof(frame));CHECK(e007z_rear_bind(&frame,7,1,b)==0);
  CHECK(e007z_rear_observe(&frame,7,1,1,b[i].wm,b[i].programmed_image_iova+4)==-EIO);
  CHECK(frame.faulted&&!e007z_rear_retireable(&frame,7,1,true,true));
  struct e007z_rear_binding bad[10];memcpy(bad,b,sizeof(b));
  bad[i].owned_bytes--;memset(&frame,0,sizeof(frame));CHECK(e007z_rear_bind(&frame,7,1,bad)==-ENOSPC);
 }
 CHECK(e007z_rear_runtime_authorization()==-EOPNOTSUPP);
 printf("{\"assertions\":%u,\"FULL_compression_register_writes\":0,\"readback_faults\":46,\"cold_admission_negatives\":12,\"DMA_span_negatives\":6,\"ten_WM_exact_consumed_identity_checked\":true}\n",assertions);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",required=True,type=Path);p.add_argument("--report",required=True,type=Path);a=p.parse_args()
 assert not a.report.exists()
 s=(a.staged/"camss-vfe-680.c").read_text()
 macros="\n".join(l for l in s.splitlines() if l.startswith("#define VFE680_X1E_BUS_"))+"\n"
 layout=(a.staged/"camss-vfe-e004nt-rear-4k-buffer.inc").read_text()
 layout_prefix=layout[layout.index('#include "native-rear-nv12-layout.h"'):layout.index("/* Compile-time fit")]
 structs=layout[layout.index("struct vfe680_e004nt_rear_surface {"):layout.index("static bool __used")]
 wm=(a.staged/"camss-vfe-e004nu-rear-ten-wm.inc").read_text()
 wm_prefix=wm[wm.index("#define VFE680_E004NU_REAR_CLIENTS"):wm.index("static bool __used")]
 crop=(a.staged/"camss-e006p-crop-roundclamp.inc").read_text()
 crop_types=crop[crop.index("struct e006p_crop_info {"):crop.index("static int e006p_crop12_pack")]
 code=PRE+macros+layout_prefix+structs+wm_prefix+"static bool "+function(layout,"vfe680_e004nt_rear_4k_target")
 code+="static int "+function(layout,"vfe680_e004nt_rear_surface_addrs")
 code+="static bool "+function(wm,"vfe680_e004nu_rear_wm_contract_valid")
 code+=crop_types+"static int "+function(crop,"e006p_roundclamp_word")
 code+=(a.staged/"native-rear-nv12-bus.inc").read_text()
 code+=(a.staged/"camss-e007z-rear-retirement.inc").read_text()+MAIN
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-linear-host-") as td:
  td=Path(td);c=td/"check.c";c.write_text(code)
  for compiler in ["gcc","clang"]:
   binary=td/compiler
   args=[compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),str(c),"-o",str(binary)]
   r=subprocess.run(args,capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout)})
 report={"status":"PASS_ACTUAL_REAR_LINEAR_LAYOUT_BUS_AND_LEDGER","hardware_access":False,
  "actual_staged_surface_addresses_FULL_bus_helpers_roundclamp_and_ledger":True,
  "FULL_compression_register_writes":0,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
