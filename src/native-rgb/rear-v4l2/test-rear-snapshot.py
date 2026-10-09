#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual bounded retry functions; event/owner/address/release APIs explicitly modeled."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
PRE=r"""
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
typedef uint32_t u32;
typedef uint64_t u64;
#define U32_MAX UINT32_MAX
static unsigned assertions, negatives;
#define CHECK(x) do{assertions++;if(!(x))abort();}while(0)
struct vfe_device {};struct csid_device {};struct e008h_rear_prime_pair {};
struct e008k_rear_result {u64 owner_epoch;u32 queue_snapshot_retries;bool live_full_retired,live_aux_retired;};
struct native_rear_live_observation {};
static unsigned drain_calls,observe_calls,full_calls,aux_calls,sleeps,full_freed,aux_freed;
static unsigned observe_races,full_races,aux_races;
static unsigned fail_kind;static int fail_errno;
static int native_rear_queue_drain(struct csid_device *c,struct e008h_rear_prime_pair *p,u64 owner,u32 *cursor) {
 CHECK(c&&p&&owner==7&&cursor);drain_calls++;
 if(fail_kind==1)return fail_errno;
 *cursor=drain_calls;return 0;
}
static int native_rear_live_replacement_read(struct vfe_device *v,struct csid_device *c,struct e008h_rear_prime_pair *p,struct e008k_rear_result *r,u32 cursor,struct native_rear_live_observation *o) {
 CHECK(v&&c&&p&&r&&o&&cursor==drain_calls);observe_calls++;
 if(fail_kind==2)return fail_errno;
 if(observe_races){observe_races--;return -EAGAIN;}return 0;
}
static int native_rear_live_retire_full(struct vfe_device *v,struct csid_device *c,struct e008h_rear_prime_pair *p,struct e008k_rear_result *r,u32 cursor) {
 CHECK(v&&c&&p&&r&&cursor==drain_calls&&!r->live_full_retired&&!full_freed);full_calls++;
 if(fail_kind==3)return fail_errno;
 if(full_races){full_races--;return -EAGAIN;}
 full_freed++;r->live_full_retired=true;return 0;
}
static int native_rear_live_retire_aux(struct vfe_device *v,struct csid_device *c,struct e008h_rear_prime_pair *p,struct e008k_rear_result *r,u32 cursor) {
 CHECK(v&&c&&p&&r&&cursor==drain_calls&&r->live_full_retired&&!r->live_aux_retired&&!aux_freed);aux_calls++;
 if(fail_kind==4)return fail_errno;
 if(aux_races){aux_races--;return -EAGAIN;}
 aux_freed+=8;r->live_aux_retired=true;return 0;
}
static void usleep_range(unsigned low,unsigned high){CHECK(low==250&&high==500);sleeps++;}
"""
POST=r"""
static struct e008k_rear_result reset(void) {
 drain_calls=observe_calls=full_calls=aux_calls=sleeps=full_freed=aux_freed=0;
 observe_races=full_races=aux_races=fail_kind=0;fail_errno=0;
 return (struct e008k_rear_result){.owner_epoch=7};
}
int main(void) {
 struct vfe_device v={};struct csid_device c={};struct e008h_rear_prime_pair p={};u32 cursor=0;
 struct e008k_rear_result r=reset();
 observe_races=3;
 CHECK(native_rear_queue_observe_stable(&v,&c,&p,&r,&cursor)==0);
 CHECK(observe_calls==4&&drain_calls==4&&sleeps==3&&r.queue_snapshot_retries==3);
 CHECK(full_freed==0&&aux_freed==0);
 r=reset();full_races=3;aux_races=5;
 CHECK(native_rear_queue_retire_stable(&v,&c,&p,&r,&cursor)==0);
 CHECK(full_calls==4&&aux_calls==6&&sleeps==8&&drain_calls==9);
 CHECK(full_freed==1&&aux_freed==8&&r.live_full_retired&&r.live_aux_retired);
 CHECK(r.queue_snapshot_retries==8);
 int errors[]={-EIO,-ESTALE,-EOVERFLOW,-ESHUTDOWN,-EPROTO,-EINVAL,-EBUSY};
 for(unsigned e=0;e<sizeof(errors)/sizeof(errors[0]);e++)
  for(unsigned kind=1;kind<=4;kind++) {
   r=reset();fail_kind=kind;fail_errno=errors[e];
   int ret=kind<=2 ? native_rear_queue_observe_stable(&v,&c,&p,&r,&cursor):
                    native_rear_queue_retire_stable(&v,&c,&p,&r,&cursor);
   CHECK(ret==errors[e]&&sleeps==0&&r.queue_snapshot_retries==0);
   CHECK(drain_calls==1&&aux_freed==0);
   CHECK(full_freed==(kind==4?1U:0U));
   negatives++;
  }
 for(unsigned kind=2;kind<=4;kind++) {
  r=reset();fail_kind=kind;fail_errno=-EAGAIN;
  int ret=kind==2 ? native_rear_queue_observe_stable(&v,&c,&p,&r,&cursor):
                   native_rear_queue_retire_stable(&v,&c,&p,&r,&cursor);
  CHECK(ret==-ETIMEDOUT&&sleeps==256&&drain_calls==256&&r.queue_snapshot_retries==256);
  CHECK(aux_freed==0&&full_freed==(kind==4?1U:0U));
  if(kind==4)CHECK(full_calls==1&&r.live_full_retired&&!r.live_aux_retired);
  negatives++;
 }
 r=reset();observe_races=1;r.queue_snapshot_retries=U32_MAX;
 CHECK(native_rear_queue_observe_stable(&v,&c,&p,&r,&cursor)==-EOVERFLOW&&sleeps==0);
 negatives++;
 r=reset();aux_races=1;r.queue_snapshot_retries=U32_MAX;
 CHECK(native_rear_queue_retire_stable(&v,&c,&p,&r,&cursor)==-EOVERFLOW&&sleeps==0&&full_freed==1&&aux_freed==0);
 negatives++;
 r=reset();r.live_full_retired=r.live_aux_retired=true;
 CHECK(native_rear_queue_retire_stable(&v,&c,&p,&r,&cursor)==0&&full_calls==0&&aux_calls==0);
 printf("{\"assertions\":%u,\"negative_cases\":%u,\"attempt_limit\":256,\"partial_FULL_release_never_repeated\":true}\n",assertions,negatives);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 source=(a.staged/"native-rear-queue.inc").read_text()
 start=source.index("#define NATIVE_REAR_SNAPSHOT_ATTEMPTS")
 end=source.index("/* All retained FULL mapping tails",start)
 code=source[start:end]
 assert "native_rear_queue_observe_stable(vfe, csid, pair, result, cursor)" in source
 assert "native_rear_queue_retire_stable(vfe, csid, pair, result, cursor)" in source
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-snapshot-retry-") as temp:
  temp=Path(temp);c=temp/"check.c";c.write_text(PRE+code+POST)
  for cc in ["gcc","clang"]:
   exe=temp/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer",str(c),"-o",str(exe)],check=True,capture_output=True,text=True)
   r=subprocess.run([str(exe)],check=True,capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,**json.loads(r.stdout)))
 report=dict(status="PASS_ACTUAL_BOUNDED_SNAPSHOT_RETRY_AND_PARTIAL_RETIREMENT_HOLD",actual_staged_retry_functions=True,hardware_events_owner_address_and_release_APIs_are_models=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
