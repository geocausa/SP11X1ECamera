#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual fixed RUP/AUP MMIO helper; locks/route and MMIO are host models."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
PRE=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;typedef uint64_t u64;
#define READ_ONCE(x) (x)
#define E005Y_VFE1_OWNER_REAR 2
#define CSID_IPP_CTRL 0
#define CSID_IPP_CFG0 4
#define CSID_IPP_CFG1 8
#define CSID_REG_UPDATE_CMD 0x18
#define CSID_E004NS_REAR_IPP_CFG0 0x802b2000U
#define CSID_E004NS_REAR_IPP_CFG1 0x7241U
static unsigned assertions,writes,barriers,locks;
#define CHECK(x) do{assertions++;if(!(x))abort();}while(0)
struct e005y_vfe1_owner {int lock;unsigned active_owner;u64 active_epoch;bool unsafe_stop_pinned;};
struct csid_device {struct camss *camss;unsigned irq;u64 e008i_rear_owner_epoch;u32 e008i_rear_done_overflow,e008i_rear_latch_errors;unsigned char *base;};
struct camss {struct csid_device csid[2];struct e005y_vfe1_owner e005y_vfe1_owner;};
static struct camss camera;static u32 regs[64];static bool mode=true;
static bool csid_e004ns_rear_ipp_mode0(struct csid_device *c){return mode&&c==&camera.csid[1];}
#define spin_lock_irqsave(l,f) do{CHECK(!locks);locks++;(void)(l);(f)=0;}while(0)
#define spin_unlock_irqrestore(l,f) do{CHECK(locks==1);locks--;(void)(l);(void)(f);}while(0)
static u32 readl(const void *p){return *(const u32*)p;}
#define wmb() do{CHECK(locks==1);barriers++;}while(0)
static void writel(u32 value,void *p){CHECK(locks==1&&barriers==1&&p==(void*)((unsigned char*)regs+0x18)&&value==0x01f501f5U);writes++;*(u32*)p=value;}
'''
MAIN=r'''
static void reset(void){
 memset(&camera,0,sizeof(camera));memset(regs,0,sizeof(regs));writes=barriers=locks=0;mode=true;
 camera.csid[1]=(struct csid_device){.camss=&camera,.irq=9,.e008i_rear_owner_epoch=7,.base=(unsigned char*)regs};
 camera.e005y_vfe1_owner=(struct e005y_vfe1_owner){.active_owner=2,.active_epoch=7};
 regs[0]=CSID_E004NS_REAR_IPP_CFG0;regs[0]=1;regs[1]=CSID_E004NS_REAR_IPP_CFG0;regs[2]=CSID_E004NS_REAR_IPP_CFG1;
}
int main(void){
 for(unsigned i=0;i<80;i++){reset();CHECK(!csid680_native_rear_output_update(&camera.csid[1],7));CHECK(writes==1&&barriers==1&&!locks);}
 for(unsigned i=0;i<15;i++){
  reset();struct csid_device *c=&camera.csid[1];u64 owner=7;
  switch(i){
   case 0:c=NULL;break;case 1:c->camss=NULL;break;case 2:owner=0;break;case 3:c->irq=0;break;
   case 4:c=&camera.csid[0];c->camss=&camera;c->irq=9;break;case 5:mode=false;break;
   case 6:c->e008i_rear_owner_epoch=8;break;case 7:c->e008i_rear_done_overflow=1;break;
   case 8:c->e008i_rear_latch_errors=1;break;case 9:camera.e005y_vfe1_owner.active_owner=1;break;
   case 10:camera.e005y_vfe1_owner.active_epoch=8;break;case 11:camera.e005y_vfe1_owner.unsafe_stop_pinned=true;break;
   case 12:regs[0]=0;break;case 13:regs[1]^=1;break;case 14:regs[2]^=1;break;
  }
  u32 before[64];memcpy(before,regs,sizeof(regs));
  CHECK(csid680_native_rear_output_update(c,owner)<0);CHECK(!writes&&!barriers&&!locks);CHECK(!memcmp(before,regs,sizeof(regs)));
 }
 printf("OUTPUT_UPDATE_PASS assertions=%u guarded_commits=80 negative_cases=15\n",assertions);return 0;
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 actual=(a.staged/"native-rear-output-update.inc").read_text()
 startup=(a.staged/"camss-e007y-rear-startup.inc").read_text()
 authority=int(re.search(r"#define E007Y_REAR_RUP_AUP_VALUE (0x[0-9a-fA-F]+)",startup)[1],16)
 value=int(re.search(r"writel\((0x[0-9a-fA-F]+)U, csid->base \+ CSID_REG_UPDATE_CMD",actual)[1],16)
 assert value==authority==0x01f501f5
 driver=(a.staged/"camss-csid-680.c").read_text()
 assert int(re.search(r"#define CSID_REG_UPDATE_CMD\s+(0x[0-9a-fA-F]+)",driver)[1],16)==0x18
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-output-update-") as tmp:
  d=Path(tmp);c=d/"check.c";c.write_text(PRE+actual+MAIN)
  for cc in ["gcc","clang"]:
   exe=d/cc;subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(c),"-o",str(exe)],check=True)
   r=subprocess.run([exe],capture_output=True,text=True);assert not r.returncode,r.stderr
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,result=r.stdout.strip()))
 report=dict(status="PASS_ACTUAL_SOURCE_LOCKED_REAR_RUP_AUP_OWNER_GUARDS",actual_staged_MMIO_helper=True,MMIO_route_and_lock_APIs_are_models=True,fixed_value_matches_qualified_startup_wrapper=True,offset_matches_GPL_driver_definition=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
