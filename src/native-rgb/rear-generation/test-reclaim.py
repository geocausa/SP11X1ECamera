#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual post-stop reclaim admission; DMA frees and owner query are models."""
import argparse,importlib.util,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
PRE=r"""
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8;typedef uint32_t u32;typedef uint64_t u64;
#define __used __attribute__((unused))
#define static_assert(expr,...) _Static_assert(expr,#expr)
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
#define VFE_BUS_WRITE_CLIENT_CFG_EN 1U
#define READ_ONCE(x) (x)
#define E008H_REAR_SLOTS 2U
#define E008D_REAR_AUX_COUNT 8
#define E007Y_STARTUP_PACKETS 4
static unsigned assertions,releases,command_releases,negative_cases;static bool owner_valid;static u64 owner_epoch;
#define CHECK(x) do {assertions++;if(!(x)){fprintf(stderr,"failed line%d %s\n",__LINE__,#x);exit(1);}}while(0)
struct camss;
struct vfe_device {struct camss *camss;bool exact;};
struct camss {int e005y_vfe1_owner;};
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v){return v&&v->exact;}
"""
TYPES=r"""
struct full {void *cpu;size_t size;bool in_flight;};
struct aux {void *cpu;size_t size;u8 wm;};
struct e008d_rear_dma_set {struct full full;struct aux aux[8];bool allocated,prepared_disabled;};
struct e007z_rear_frame {u64 owner_epoch,request_generation;unsigned pending;bool active,faulted;};
struct e008h_rear_prime_pair {struct e008d_rear_dma_set dma[2];struct e007z_rear_frame frame[2];bool ledgers_bound,faulted,programmed[2];};
struct e008k_rear_result {bool csid_quiesced,bus_stopped,rtcdm_stopped,source_stopped,owner_released,dma_reclaimed;};
static const struct vfe680_e004nu_rear_wm_static *e008d_rear_contract_for_wm(u8 wm){
 for(unsigned i=0;i<10;i++){if(vfe680_e004nu_rear_wm_contract[i].wm==wm)return &vfe680_e004nu_rear_wm_contract[i];}
 return NULL;
}
static bool e005y_vfe1_rear_sample_begin(int *owner,bool required,u64 *epoch){CHECK(owner&&required);*epoch=owner_epoch;return owner_valid;}
static void e008d_rear_release_partial(struct vfe_device *v,struct e008d_rear_dma_set *set){
 CHECK(v&&set&&owner_valid&&owner_epoch==7);CHECK(!set->full.in_flight);releases++;memset(set,0,sizeof(*set));
}
struct packet {bool allocated;};
struct e008l_rear_command_set {bool allocated,hardware_exposed;struct packet packet[4];};
static void e008l_rear_packet_release(struct vfe_device *v,struct packet *p){CHECK(v&&p);command_releases++;p->allocated=false;}
static struct camss cam;static struct vfe_device vfe;static struct e008h_rear_prime_pair pair;static struct e008k_rear_result result;
static void init(void){
 memset(&pair,0,sizeof(pair));vfe=(struct vfe_device){&cam,true};owner_valid=true;owner_epoch=7;releases=command_releases=0;
 result=(struct e008k_rear_result){true,true,true,true,false,false};
 pair.ledgers_bound=pair.programmed[0]=pair.programmed[1]=true;
 for(unsigned s=0;s<2;s++){
  struct e008d_rear_dma_set *set=&pair.dma[s];set->allocated=set->prepared_disabled=true;
  set->full=(struct full){&cam,VFE680_E004NT_REAR_TOTAL_BYTES,true};
  pair.frame[s]=(struct e007z_rear_frame){7,s+1,0,true,false};
  for(unsigned i=0;i<8;i++){
   const struct vfe680_e004nu_rear_wm_static *c=&vfe680_e004nu_rear_wm_contract[i+2];
   set->aux[i]=(struct aux){&cam,c->frame_incr,c->wm};
  }
 }
}
"""
MAIN=r"""
int main(void){
 init();CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)==0);
 CHECK(releases==2&&!pair.dma[0].full.cpu&&!pair.dma[1].full.cpu);
 for(unsigned i=0;i<16;i++){
  init();struct camss *c=&cam;struct vfe_device *v=&vfe;struct e008h_rear_prime_pair *p=&pair;const struct e008k_rear_result *r=&result;u64 epoch=7;
  switch(i){case 0:c=NULL;break;case 1:v=NULL;break;case 2:p=NULL;break;case 3:r=NULL;break;case 4:epoch=0;break;
   case 5:vfe.camss=NULL;break;case 6:vfe.exact=false;break;case 7:result.csid_quiesced=false;break;
   case 8:result.bus_stopped=false;break;case 9:result.rtcdm_stopped=false;break;case 10:result.source_stopped=false;break;
   case 11:result.owner_released=true;break;case 12:result.dma_reclaimed=true;break;case 13:owner_valid=false;break;
   case 14:owner_epoch=8;break;case 15:pair.faulted=true;break;}
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(c,v,p,epoch,r)!=0);CHECK(releases==0);CHECK(!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
 for(unsigned s=0;s<2;s++){
  for(unsigned i=0;i<13;i++){
   init();struct e008d_rear_dma_set *set=&pair.dma[s];struct e007z_rear_frame *frame=&pair.frame[s];
   switch(i){case 0:pair.ledgers_bound=false;break;case 1:pair.programmed[s]=false;break;
    case 2:frame->active=false;break;case 3:frame->faulted=true;break;case 4:frame->owner_epoch++;break;case 5:frame->pending=1;break;
    case 6:set->allocated=false;break;case 7:set->prepared_disabled=false;break;case 8:set->full.in_flight=false;break;
    case 9:set->full.cpu=NULL;break;case 10:set->full.size--;break;case 11:frame->request_generation=0;break;
    case 12:pair.dma[s].aux[7].size--;break;}
   struct e008h_rear_prime_pair before=pair;
   CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);CHECK(releases==0);CHECK(!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
  }
  for(unsigned a=0;a<8;a++)for(unsigned field=0;field<3;field++){
   init();struct aux *aux=&pair.dma[s].aux[a];
   if(field==0)aux->cpu=NULL;else if(field==1)aux->size--;else aux->wm=99;
   struct e008h_rear_prime_pair before=pair;
   CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);CHECK(releases==0);CHECK(!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
  }
 }
 struct e008l_rear_command_set commands={.allocated=true,.hardware_exposed=true};
 init();CHECK(e008l_rear_command_release(&vfe,&commands,false)==-EBUSY);CHECK(command_releases==0&&commands.allocated);
 CHECK(e008l_rear_command_release(&vfe,&commands,true)==0);CHECK(command_releases==4&&!commands.allocated);
 printf("{\"assertions\":%u,\"admission_negatives\":%u,\"all_allocations_checked_before_any_release\":true,\"successful_DMA_set_releases\":2,\"command_release_requires_RTCDM_stop\":true}\n",assertions,negative_cases);
 return 0;
}
"""
def function(s,name):
 i=s.index(name+"(");a=s.index("{",i);j=a+1;depth=1
 while depth:
  depth+=(s[j]=="{")-(s[j]=="}");j+=1
 return s[i:j]+"\n"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",required=True,type=Path);p.add_argument("--report",required=True,type=Path);a=p.parse_args();assert not a.report.exists()
 layout=(a.staged/"camss-vfe-e004nt-rear-4k-buffer.inc").read_text()
 macros=layout[layout.index('#include "native-rear-nv12-layout.h"'):layout.index("/* Compile-time fit")]
 wm=(a.staged/"camss-vfe-e004nu-rear-ten-wm.inc").read_text()
 wm_prefix=wm[wm.index("#define VFE680_E004NU_REAR_CLIENTS"):wm.index("static bool __used")]
 code=PRE+macros+wm_prefix+TYPES
 code+="static bool "+function((a.staged/"camss-vfe-e008h-rear-prime.inc").read_text(),"e008h_rear_both_complete")
 code+="static int "+function((a.staged/"camss-vfe-e008k-rear-runner.inc").read_text(),"e011i_rear_reclaim_after_stop")
 code+="static int "+function((a.staged/"camss-vfe-e008l-rear-command-dma.inc").read_text(),"e008l_rear_command_release")+MAIN
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-reclaim-host-") as td:
  td=Path(td);c=td/"check.c";c.write_text(code)
  for compiler in ["gcc","clang"]:
   binary=td/compiler
   r=subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),str(c),"-o",str(binary)],capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout)})
 report={"status":"PASS_ACTUAL_ALL_OR_NONE_REAR_POST_STOP_RECLAIM_ADMISSION","actual_staged_reclaim_complete_ledger_and_command_release_admission":True,
         "owner_query_DMA_set_and_command_packet_frees_are_models":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
