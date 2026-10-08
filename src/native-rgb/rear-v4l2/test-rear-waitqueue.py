#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual QBUF/start/join and registration initializer; kernel APIs modelled."""
from pathlib import Path
import argparse,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
def fn(t,name):
 i=t.index(name+"(");a=t.index("{",i);j=a+1;d=1
 while d:d+=(t[j]=="{")-(t[j]=="}");j+=1
 return t[i:j]+"\n"
PRE=r'''
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#define VFE_LINE_PIX 0
#define CAMSS_X1E80100 1
#define READ_ONCE(x) (x)
#define WRITE_ONCE(x,v) ((x)=(v))
static unsigned assertions,wakes,flushes,schedules,pending;
#define CHECK(x) do{assertions++;if(!(x)){fprintf(stderr,"INVALID_WAITQUEUE_OR_STATE:%d\n",__LINE__);exit(2);}}while(0)
struct work_struct {bool initialized;};
struct wait_queue_head {bool initialized;};
struct camss_buffer {unsigned id;};
struct camss_video {struct camss *camss;struct work_struct x1e_pix_work;struct wait_queue_head x1e_pix_buf_wait;bool x1e_pix_runner_pinned,x1e_pix_worker_started,x1e_pix_live_active,x1e_pix_runner_stopped,x1e_pix_stop_requested;int x1e_pix_worker_ret;};
struct vfe_output {int model;};
struct vfe_device {int output_lock;struct {struct camss_video video_out;struct vfe_output output;}line[1];};
struct resource {unsigned version,vfe_num;};
struct camss {struct resource *res;struct vfe_device vfe[2];};
static bool admitted=true,schedule_ok=true;
static void init_waitqueue_head(struct wait_queue_head *w){CHECK(w);w->initialized=true;}
static void wake_up_all(struct wait_queue_head *w){CHECK(w&&w->initialized);wakes++;}
static void native_rear_public_work(struct work_struct *w){(void)w;}
#define INIT_WORK(w,f) do{CHECK((f)==native_rear_public_work);(w)->initialized=true;}while(0)
static bool schedule_work(struct work_struct *w){CHECK(w&&w->initialized);schedules++;return schedule_ok;}
static void flush_work(struct work_struct *w){CHECK(w&&w->initialized);flushes++;}
static bool camss_x1e_rear_public_trial_allowed(struct camss_video *v){return admitted&&v&&v->camss;}
#define spin_lock_irqsave(l,f) do{(void)(l);(f)=0;}while(0)
#define spin_unlock_irqrestore(l,f) do{(void)(l);(void)(f);}while(0)
static void vfe_buf_add_pending(struct vfe_output *o,struct camss_buffer *b){CHECK(o&&b);pending++;}
'''
MAIN=r'''
int main(void){
 struct resource res={CAMSS_X1E80100,2};struct camss camera={.res=&res};
 struct camss_video *video=&camera.vfe[1].line[0].video_out;video->camss=&camera;
 struct camss_buffer buffers[4]={{0},{1},{2},{3}};
 /* ACTUAL_REGISTRATION_INIT */
 CHECK(!camss_x1e_pix_v4l2_queue_buffer(video,&buffers[0]));
 CHECK(!camss_x1e_pix_v4l2_queue_buffer(video,&buffers[1]));
 CHECK(pending==2&&wakes==0);
 CHECK(!camss_x1e_rear_public_start(video,2));
 CHECK(video->x1e_pix_worker_started&&video->x1e_pix_live_active&&schedules==1);
 for(unsigned i=0;i<80;i++)CHECK(!camss_x1e_pix_v4l2_queue_buffer(video,&buffers[i%4]));
 CHECK(pending==82&&wakes==80);
 camss_x1e_rear_public_join(video);CHECK(!video->x1e_pix_worker_started&&flushes==1&&wakes==81&&video->x1e_pix_stop_requested);
 CHECK(!camss_x1e_pix_v4l2_queue_buffer(video,&buffers[0]));CHECK(wakes==81);
 camss_x1e_rear_public_join(video);CHECK(flushes==1&&wakes==82);
 CHECK(camss_x1e_pix_v4l2_queue_buffer(NULL,&buffers[0])==-EINVAL);
 CHECK(camss_x1e_pix_v4l2_queue_buffer(video,NULL)==-EINVAL);
 CHECK(camss_x1e_rear_public_start(video,1)==-EINVAL);
 video->x1e_pix_runner_pinned=true;CHECK(camss_x1e_rear_public_start(video,2)==-EBUSY);video->x1e_pix_runner_pinned=false;
 video->x1e_pix_worker_started=true;CHECK(camss_x1e_rear_public_start(video,2)==-EBUSY);video->x1e_pix_worker_started=false;
 video->x1e_pix_live_active=false;schedule_ok=false;
 CHECK(camss_x1e_rear_public_start(video,2)==-EBUSY);CHECK(!video->x1e_pix_worker_started&&!video->x1e_pix_live_active);
 admitted=false;CHECK(camss_x1e_rear_public_start(video,2)==-EINVAL);
 res.version=0;CHECK(camss_x1e_pix_v4l2_queue_buffer(video,&buffers[0])==-EINVAL);res.version=1;
 res.vfe_num=1;CHECK(camss_x1e_pix_v4l2_queue_buffer(video,&buffers[0])==-EINVAL);
 printf("WAITQUEUE_PASS assertions=%u reused_QBUFs=80\n",assertions);return 0;
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 registration="int "+fn((a.staged/"camss-video.c").read_text(),"msm_video_register")
 init="init_waitqueue_head(&video->x1e_pix_buf_wait);"
 assert registration.count(init)==1 and registration.index(init)<registration.index("video_register_device(")
 worker=(a.staged/"native-rear-public-worker.inc").read_text()
 actual="int "+fn(worker,"camss_x1e_rear_public_start")+"void "+fn(worker,"camss_x1e_rear_public_join")+"int "+fn((a.staged/"camss.c").read_text(),"camss_x1e_pix_v4l2_queue_buffer")
 code=PRE+actual+MAIN.replace("/* ACTUAL_REGISTRATION_INIT */",init)
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-waitqueue-regression-") as tmp:
  d=Path(tmp);c=d/"test.c";c.write_text(code)
  for cc in ["gcc","clang"]:
   exe=d/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(c),"-o",str(exe)],check=True)
   r=subprocess.run([exe],capture_output=True,text=True);assert not r.returncode,r.stderr
   control=d/"old.c";control.write_text(code.replace(init,"/* omitted initializer reproduces candidate33 */",1))
   old=d/(cc+"-old")
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-O1",str(control),"-o",str(old)],check=True,capture_output=True)
   negative=subprocess.run([old],capture_output=True,text=True)
   assert negative.returncode==2 and "INVALID_WAITQUEUE_OR_STATE:" in negative.stderr
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,result=r.stdout.strip(),candidate33_missing_initializer_control_rejected=True))
 report=dict(status="PASS_ACTUAL_REAR_QBUF_START_JOIN_INITIALIZED_WAITQUEUE",actual_registration_initializer_order_and_queue_start_join=True,waitqueue_workqueue_lock_and_VB2_APIs_are_models=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
