#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute actual candidate pair-stop function with ordered fault injection."""
from pathlib import Path
import argparse,tempfile,subprocess,json,os
def main():
 p=argparse.ArgumentParser();p.add_argument('--staged',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 text=(a.staged/'camss-vfe-e008k-rear-runner.inc').read_text()
 start=text.index('static int\ne008k_rear_pair_stop_release(');end=text.index('\nstatic void\ne008k_rear_emergency_pin',start)
 actual=text[start:end]
 assert actual.index('if (!e008h_rear_both_complete')<actual.index('e008k_rear_subdev_stream(&csiphy->subdev, false)')<actual.index('e008k_rear_subdev_stream(sensor, false)')<actual.index('csid680_e008a_rear_quiesce(')<actual.index('vfe680_e008a_rear_bus_stop(')<actual.index('e008k_rear_rtcdm_stop_close(')<actual.index('e011i_rear_reclaim_after_stop(')
 source=r'''
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
typedef uint64_t u64;
#define E008H_REAR_SLOTS 2
#define READ_ONCE(x) (x)
#define dev_info(...) ((void)0)
#define E005Y_VFE1_OWNER_REAR 7
static bool native_rear_diagnostic_active=true,native_rear_diagnostic_reclaim=true;
static unsigned checks,steps,failed_at,reclaims,pm_puts,owner_puts,phy_stops,sensor_stops;
static unsigned order[32],order_n;
static bool permit=true;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
static int step(unsigned kind){order[order_n++]=kind;steps++;return steps==failed_at?-EIO:0;}
struct v4l2_subdev{unsigned kind;};
struct csiphy_device{struct v4l2_subdev subdev;};
struct csid_device{int dummy;};
struct vfe_device{int dummy;};
struct camss{int e005y_vfe1_owner;};
struct media_entity{int dummy;};
struct frame{bool active,faulted;unsigned pending;u64 owner_epoch,request_generation;};
struct e008h_rear_prime_pair{bool ledgers_bound,faulted,programmed[2];struct frame frame[2];};
struct e008k_rear_result{bool source_stopped,csid_quiesced,bus_stopped,rtcdm_stopped,dma_intentionally_pinned,dma_reclaimed,ledgers_released,owner_released;};
static bool e008h_rear_both_complete(struct e008h_rear_prime_pair*p,u64 owner){CHECK(p&&owner==9);return permit;}
static int e008k_rear_subdev_stream(struct v4l2_subdev*s,bool on){CHECK(s&&!on);if(s->kind==1)phy_stops++;else sensor_stops++;return step(s->kind);}
static int csid680_e008a_rear_quiesce(struct csid_device*c,bool exact){CHECK(c&&exact&&phy_stops==1&&sensor_stops==1);return step(3);}
static int vfe680_e008a_rear_bus_stop(struct vfe_device*v,bool exact){CHECK(v&&exact);return step(4);}
static bool e007z_rear_retireable(struct frame*f,u64 o,u64 g,bool bus,bool irq){CHECK(f&&o==9&&g&&bus&&irq);return !step(5);}
static void e008k_rear_rtcdm_stop_close(struct camss*c){CHECK(c);order[order_n++]=6;}
static bool e008k_rear_rtcdm_stopped(struct camss*c){CHECK(c);return !step(7);}
static int e011i_rear_reclaim_after_stop(struct camss*c,struct vfe_device*v,struct e008h_rear_prime_pair*p,u64 o,struct e008k_rear_result*r){CHECK(c&&v&&p&&o==9&&r->source_stopped&&r->csid_quiesced&&r->bus_stopped&&r->rtcdm_stopped);reclaims++;return step(8);}
static int e007z_rear_release_ledger(struct frame*f,u64 o,u64 g,bool bus,bool irq){CHECK(f&&o==9&&g&&bus&&irq);return step(9);}
static void e008k_rear_pipeline_pm_put(struct media_entity*e){CHECK(e);pm_puts++;order[order_n++]=10;}
static int e005y_vfe1_owner_release(int*own,int kind,u64 o,bool clean){CHECK(own&&kind==7&&o==9&&clean);owner_puts++;return step(11);}
'''
 tail=r'''
int main(void){
 struct camss c={0};struct vfe_device v={0};struct csid_device cid={0};struct csiphy_device phy={{1}};struct v4l2_subdev sensor={2};struct media_entity video={0};
 struct e008h_rear_prime_pair pair={.ledgers_bound=true,.programmed={true,true},.frame={{.active=true,.owner_epoch=9,.request_generation=401},{.active=true,.owner_epoch=9,.request_generation=402}}};
 unsigned failure_cases=0;
 for(unsigned test=0;test<14;test++){
  steps=order_n=reclaims=pm_puts=owner_puts=phy_stops=sensor_stops=0;failed_at=test>0&&test<=11?test:0;permit=test!=12;native_rear_diagnostic_reclaim=test!=13;
  bool power=true,rtcdm=true,ps=true,ss=true;struct e008k_rear_result r={0};
  int ret=e008k_rear_pair_stop_release(&c,&v,&cid,&phy,&sensor,&pair,&video,9,&power,&rtcdm,&ps,&ss,&r);
  if(test==0){CHECK(!ret&&r.source_stopped&&r.csid_quiesced&&r.bus_stopped&&r.rtcdm_stopped&&r.dma_reclaimed&&r.ledgers_released&&r.owner_released&&!power&&!rtcdm&&!ps&&!ss);CHECK(reclaims==1&&pm_puts==1&&owner_puts==1);unsigned want[]={1,2,3,4,5,5,6,7,8,9,9,10,11};CHECK(order_n==13&&!memcmp(want,order,sizeof(want)));}
  else if(test==12){CHECK(ret==-EBUSY&&steps==0&&reclaims==0&&power&&rtcdm&&ps&&ss);failure_cases++;}
  else if(test==13){CHECK(ret==-EINPROGRESS&&r.dma_intentionally_pinned&&r.source_stopped&&r.csid_quiesced&&r.bus_stopped&&r.rtcdm_stopped&&!r.dma_reclaimed&&reclaims==0&&pm_puts==0&&owner_puts==0&&power);failure_cases++;}
  else {CHECK(ret<0&&!r.owner_released);if(test<=7){CHECK(reclaims==0&&!r.dma_reclaimed&&pm_puts==0&&owner_puts==0&&power);}CHECK(phy_stops==1&&sensor_stops==1);failure_cases++;}
 }
 printf("{\"assertions\":%u,\"fault_and_denial_cases\":%u,\"all_four_stops_before_reclaim\":true,\"source_stop_before_CSID\":true}\n",checks,failure_cases);
}
'''
 results=[]
 with tempfile.TemporaryDirectory(prefix='rear59-source-stop-') as td:
  td=Path(td);c=td/'check.c';c.write_text(source+actual+tail)
  for cc in ['gcc','clang']:
   exe=td/cc
   subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(c),'-o',str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output([exe],text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,**json.loads(out)))
 report=dict(status='PASS_ACTUAL_EARLY_SOURCE_STOP_ORDER_AND_FAILURE_PINNING',actual_pair_stop_function_executed=True,hardware_stop_helpers_mocked=True,DMA_release_requires_all_four_proofs=True,completion_guard_unchanged=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
