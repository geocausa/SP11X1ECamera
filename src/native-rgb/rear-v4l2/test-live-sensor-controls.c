/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <stdbool.h>
#include <linux/v4l2-controls.h>
typedef uint32_t u32;typedef uint64_t u64;
struct v4l2_ctrl {u32 id;int val;};
struct ov13858 {bool native_control_streaming;int mutex;void *dev;};
static int held=1,reads=0,logged=0,error=0,mismatch=0,backwards=0,ticks=0;
static u32 expected_reg,expected_length,expected_value;
#define lockdep_assert_held(m) do {if(!held || (m)==NULL)abort();}while(0)
#define dev_info(d,fmt,...) do {(void)(d);(void)(fmt);logged++;}while(0)
static u64 ktime_get_ns(void){ticks++;return backwards && ticks==2?50:(u64)ticks*100;}
static int ov13858_read_reg(struct ov13858 *s,u32 reg,u32 len,u32 *value){(void)s;reads++;if(reg!=expected_reg||len!=expected_length)abort();*value=expected_value+mismatch;return error;}
#include "native-rear-live-control-readback.inc"
static unsigned assertions=0,negatives=0;
#define CHECK(x) do {if(!(x))abort();assertions++;}while(0)
int main(void){
 struct ov13858 s={true,1,NULL};struct v4l2_ctrl ctrl;
 for(unsigned i=0;i<4;i++){
  ctrl.id=i<2?V4L2_CID_EXPOSURE:V4L2_CID_ANALOGUE_GAIN;ctrl.val=i==0?1600:i==1?3206:i==2?128:1024;
  expected_reg=i<2?0x3500:0x3508;expected_length=i<2?3:2;expected_value=i<2?(u32)ctrl.val<<4:(u32)ctrl.val;
  reads=logged=ticks=0;CHECK(native_rear_live_control_readback(&s,&ctrl)==0);CHECK(reads==1&&logged==1&&ticks==2);
  for(unsigned fault=0;fault<3;fault++){
   error=fault==0?-EIO:0;mismatch=fault==1;backwards=fault==2;reads=logged=ticks=0;
   CHECK(native_rear_live_control_readback(&s,&ctrl)<0);CHECK(reads==1&&logged==0);negatives++;
  }
  error=mismatch=backwards=0;
 }
 s.native_control_streaming=false;reads=0;CHECK(native_rear_live_control_readback(&s,&ctrl)==-EPROTO && reads==0);negatives++;
 s.native_control_streaming=true;ctrl.id=V4L2_CID_DIGITAL_GAIN;CHECK(native_rear_live_control_readback(&s,&ctrl)==-EOPNOTSUPP && reads==0);negatives++;
 printf("LIVE_SENSOR_MODEL_PASS assertions=%u negatives=%u\n",assertions,negatives);
 return 0;
}
