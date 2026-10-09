#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute actual staged gate, clean predicate and arena wrapper; hardware APIs modeled."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
PRE=r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint64_t u64;
typedef uint32_t u32;
#define __used __attribute__((unused))
#define GFP_KERNEL 0
#define E007Y_STARTUP_PACKETS 4
static unsigned assertions, stage, fail_stage, omitted;
static void check(bool x) { assertions++;if(!x)abort(); }
#define CHECK(x) check(!!(x))
struct camss {};
struct vfe_device { struct camss *camss; };
struct v4l2_subdev {};
struct camss_buffer {};
struct e008k_rear_result {
 u64 owner_epoch;
 bool packet_submitted[4], slot0_enabled, slot1_programmed, both_frames_complete;
 bool csid_quiesced,bus_stopped,rtcdm_stopped,source_stopped;
 bool ledgers_released,owner_released,dma_intentionally_pinned,dma_reclaimed;
 bool live_commands_retired;
};
struct e008l_rear_command_set {u64 packet_request_id[4];bool live_retired;};
struct e008k_rear_request {
 struct v4l2_subdev *sensor;
 struct camss_buffer *public_video[2];
 struct e008l_rear_command_set *commands;
 u64 first_request_generation,packet_request_id[4];
 unsigned long epoch_timeout_us,done_timeout_us;
};
static void *retained;
static u64 next_owner;
static int step(void) { stage++;return stage==fail_stage ? -ETIMEDOUT : 0; }
static void *kzalloc(size_t n,int g) {
 (void)g;if(step())return NULL;CHECK(!retained);retained=calloc(1,n);return retained;
}
static void kfree(void *p) {CHECK(p==retained);free(p);retained=NULL;}
static int e008l_rear_command_alloc(struct vfe_device *v,struct e008l_rear_command_set *c) {(void)v;(void)c;return step();}
static int e008k_rear_validate_route(struct camss *c,struct v4l2_subdev *s) {(void)c;(void)s;return step();}
static int e008k_rear_validate_prepared_packets(struct e008k_rear_request *r) {(void)r;return step();}
static int e008l_rear_command_mark_submitted(struct e008l_rear_command_set *c,unsigned p) {(void)c;(void)p;return step();}
static int e008l_rear_command_release(struct vfe_device *v,struct e008l_rear_command_set *c,bool exposed) {(void)v;(void)c;(void)exposed;return step();}
static bool native_rear_live_commands_retired_valid(struct e008l_rear_command_set *c,u64 owner) {return c->live_retired&&owner;}
static int e008k_rear_run_unreachable(struct vfe_device *v,struct e008k_rear_request *q,struct e008k_rear_result *r) {
 (void)v;(void)q;int ret=step();if(ret)return ret;
 r->owner_epoch=++next_owner;
 bool *bits[]={&r->packet_submitted[0],&r->packet_submitted[1],&r->packet_submitted[2],&r->packet_submitted[3],
 &r->slot0_enabled,&r->slot1_programmed,&r->both_frames_complete,&r->csid_quiesced,&r->bus_stopped,
 &r->rtcdm_stopped,&r->source_stopped,&r->ledgers_released,&r->owner_released,&r->dma_reclaimed};
 for(unsigned i=0;i<sizeof(bits)/sizeof(bits[0]);i++)*bits[i]=true;
 if(omitted)*bits[omitted-1]=false;
 return 0;
}
"""
POST=r"""
struct e008o_rear_semantic_set {};
static int e008o_rear_materialize_commands(struct e008o_rear_semantic_set *s,struct e008l_rear_command_set *c) {(void)s;(void)c;return step();}
static int e008o_rear_runtime_authorization(void) {return step();}
static void reset(void) {
 /* A fixture may free deliberately pinned mock memory only between tests. */
 free(retained);retained=NULL;
 memset(&e008n_rear_sessions,0,sizeof(e008n_rear_sessions));
 stage=fail_stage=omitted=0;next_owner=0;
}
int main(void) {
 struct camss c={};struct vfe_device v={.camss=&c};
 struct v4l2_subdev sd={};struct e008o_rear_semantic_set semantics={};
 struct e008n_rear_request req={.sensor=&sd,.semantics=&semantics,.first_request_generation=1};
 struct e008n_rear_result result;
 struct native_rear_session_gate g={};
 CHECK(native_rear_session_begin(NULL)==-EINVAL);
 CHECK(native_rear_session_begin(&g)==0);
 CHECK(native_rear_session_begin(&g)==-EBUSY&&g.attempted==1);
 CHECK(native_rear_session_finish(&g,0,true,1)==0);
 CHECK(native_rear_session_finish(&g,0,true,1)==-EINVAL);
 CHECK(native_rear_session_begin(&g)==0);
 CHECK(native_rear_session_finish(&g,0,true,1)==-EPROTO);
 CHECK(native_rear_session_begin(&g)==-EIO);
 g=(struct native_rear_session_gate){.attempted=1};
 CHECK(native_rear_session_begin(&g)==-ESTALE&&g.poisoned);
 g=(struct native_rear_session_gate){};
 CHECK(native_rear_session_begin(&g)==0);
 CHECK(native_rear_session_finish(&g,0,true,0)==-EPROTO);
 CHECK(native_rear_session_begin(&g)==-EIO);
 reset();
 for(unsigned s=1;s<=3;s++) {
  stage=0;CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)==0);
  CHECK(!retained);CHECK(result.command_arena_released);
  CHECK(native_rear_session_clean(&result));
  CHECK(e008n_rear_sessions.attempted==s&&e008n_rear_sessions.completed==s);
  CHECK(e008n_rear_sessions.last_owner==s&&!e008n_rear_sessions.poisoned);
 }
 unsigned success_stages=stage;
 CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)==-ENOSPC);
 unsigned negative=0;
 for(unsigned f=1;f<=success_stages;f++) {
  reset();fail_stage=f;
  CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)<0);
  CHECK(e008n_rear_sessions.poisoned&&!e008n_rear_sessions.active);
  unsigned old_stage=stage;
  CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)==-EIO);
  CHECK(stage==old_stage);negative++;
 }
 for(unsigned bit=1;bit<=14;bit++) {
  reset();omitted=bit;
  CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)<0);
  CHECK(e008n_rear_sessions.poisoned);
  CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)==-EIO);negative++;
 }
 reset();CHECK(e008n_rear_run_once_unreachable(&v,&req,&result)==0);
 bool *proofs[]={&result.identity_consumed,&result.command_arena_allocated,
 &result.preflight_materialized,&result.command_arena_released};
 for(unsigned i=0;i<4;i++) {
  *proofs[i]=false;CHECK(!native_rear_session_clean(&result));*proofs[i]=true;negative++;
 }
 result.transaction.dma_intentionally_pinned=true;
 CHECK(!native_rear_session_clean(&result));negative++;
 /* The outer and inner gates must agree before permitting a new session. */
 struct native_rear_session_gate outer={};
 CHECK(native_rear_session_begin(&outer)==0);
 CHECK(native_rear_session_finish(&outer,0,false,result.transaction.owner_epoch)==-EPROTO);
 CHECK(native_rear_session_begin(&outer)==-EIO);
 reset();
 printf("{\"assertions\":%u,\"negative_cases\":%u,\"wrapper_fault_stages\":%u,\"successful_sessions\":3}\n",
        assertions,negative,success_stages);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 inner=(a.staged/"camss-vfe-e008n-rear-single-use.inc").read_text()
 hook=(a.staged/"native-rear-generation-hook.inc").read_text()
 assert "atomic_cmpxchg" not in inner+hook
 assert hook.index("mutex_lock(&native_rear_generation_lock)")<hook.index("native_rear_session_begin(")<hook.index("native_rear_startup_run_once_unreachable(")<hook.index("native_rear_session_finish(")<hook.index("mutex_unlock(")
 assert "result.composed && native_rear_session_clean(&result.once)" in hook
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-session-gate-") as temp:
  temp=Path(temp);code=temp/"check.c";code.write_text(PRE+'\n'+inner+'\n'+POST)
  for compiler in ["gcc","clang"]:
   exe=temp/compiler
   subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),str(code),"-o",str(exe)],check=True,capture_output=True,text=True)
   r=subprocess.run([str(exe)],check=True,capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   results.append(dict(compiler=compiler,ASAN_UBSAN_Werror=True,**json.loads(r.stdout)))
 result=dict(status="PASS_ACTUAL_BOUNDED_SESSION_GATES_AND_CLEAN_PROOF_POISONING",actual_staged_wrapper=True,actual_clean_predicate=True,hardware_APIs_modeled=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
