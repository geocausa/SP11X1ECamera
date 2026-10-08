#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual candidate NoC helper against shared-parent CCF failure models."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
PRE=r"""
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
struct clk {int id;};
struct camss_clock {struct clk *clk; const char *name;};
struct vfe_device {void *base;struct camss_clock *clock;int nclocks;bool target;};
static struct clk rt={1},nrt={2},other={3};
static struct camss_clock clocks[4];
static struct vfe_device v;
static unsigned assertions,gets,rounds,sets;
static unsigned long shared_rate;
static int bad_round_id,set_error;
static long bad_round_value;
static bool mismatch_before,mismatch_after,silent_set;
#define CHECK(x) do {assertions++;if(!(x)){fprintf(stderr,"failed %d\n",__LINE__);exit(1);}}while(0)
#define IS_ERR_OR_NULL(p) (!(p)||(intptr_t)(p)<0)
#define dev_info(...) ((void)0)
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *a){return a&&a->target;}
static unsigned long clk_get_rate(struct clk *c){gets++;return shared_rate+((c->id==2&&((mismatch_before&&!sets)||(mismatch_after&&sets)))?1:0);}
static long clk_round_rate(struct clk *c,unsigned long rate){rounds++;CHECK(rate==240000000UL);return c->id==bad_round_id?bad_round_value:240000000L;}
static int clk_set_rate(struct clk *c,unsigned long rate){sets++;CHECK(c==&rt&&rate==240000000UL);if(set_error)return set_error;if(!silent_set)shared_rate=rate;return 0;}
static void init(void){
 clocks[0]=(struct camss_clock){&rt,"camnoc_rt_axi"};
 clocks[1]=(struct camss_clock){&nrt,"camnoc_nrt_axi"};
 clocks[2]=(struct camss_clock){&other,"cpas_ahb"};
 clocks[3]=(struct camss_clock){&other,"other"};
 v=(struct vfe_device){&v,clocks,3,true};
 gets=rounds=sets=0;shared_rate=19200000UL;
 bad_round_id=0;bad_round_value=0;set_error=0;
 mismatch_before=mismatch_after=silent_set=false;
}
"""
MAIN=r"""
int main(void){
 init();CHECK(native_rear_generation_noc_floor(&v)==0);
 CHECK(shared_rate==240000000UL&&sets==1&&rounds==2&&gets==4);
 for(unsigned long rate=240000000UL;rate<=400000000UL;rate+=(rate==240000000UL?60000000UL:100000000UL)){
  init();shared_rate=rate;CHECK(native_rear_generation_noc_floor(&v)==0);CHECK(shared_rate==rate&&sets==0&&rounds==0);
 }
 for(unsigned n=0;n<11;n++){
  init();struct vfe_device *a=&v;
  switch(n){case 0:a=NULL;break;case 1:v.target=false;break;case 2:v.base=NULL;break;
   case 3:v.clock=NULL;break;case 4:v.nclocks=0;break;case 5:clocks[0].name=NULL;break;
   case 6:clocks[0].clk=NULL;break;case 7:clocks[1].clk=(void*)-1;break;
   case 8:clocks[0].name="missing_rt";break;case 9:clocks[1].name="missing_nrt";break;
   case 10:v.nclocks=4;clocks[3].name="camnoc_rt_axi";break;}
  CHECK(native_rear_generation_noc_floor(a)==-EINVAL);CHECK(sets==0);
 }
 init();mismatch_before=true;CHECK(native_rear_generation_noc_floor(&v)==-EPROTO);CHECK(sets==0&&rounds==0);
 for(int id=1;id<=2;id++){
  init();bad_round_id=id;bad_round_value=-EINVAL;CHECK(native_rear_generation_noc_floor(&v)==-EINVAL);CHECK(sets==0);
  init();bad_round_id=id;bad_round_value=300000000L;CHECK(native_rear_generation_noc_floor(&v)==-EPROTO);CHECK(sets==0);
 }
 init();set_error=-EIO;CHECK(native_rear_generation_noc_floor(&v)==-EIO);CHECK(sets==1&&shared_rate==19200000UL);
 init();silent_set=true;CHECK(native_rear_generation_noc_floor(&v)==-EIO);CHECK(sets==1);
 init();mismatch_after=true;CHECK(native_rear_generation_noc_floor(&v)==-EIO);CHECK(sets==1);
 printf("{\"assertions\":%u,\"admission_negatives\":12,\"CCF_fault_cases\":7,\"shared_parent_one_set\":true,\"higher_rate_preserved\":true}\n",assertions);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-noc-ccf-") as tmp:
  tmp=Path(tmp);c=tmp/"check.c";c.write_text(PRE+a.source.read_text()+MAIN)
  for compiler in ["gcc","clang"]:
   binary=tmp/compiler
   r=subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer",str(c),"-o",str(binary)],capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout)})
 report={"status":"PASS_ACTUAL_CANDIDATE_NOC_FLOOR_SHARED_PARENT_CCF_FAILURE_MODELS","hardware_access":False,"no_direct_clock_or_image_CSR_writes":True,"models_are_not_hardware_proof":True,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
