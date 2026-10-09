#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
typedef uint32_t u32;
#define V4L2_CID_EXPOSURE 0
#define V4L2_CID_ANALOGUE_GAIN 1
#define V4L2_CID_DIGITAL_GAIN 2
#define V4L2_CID_TEST_PATTERN 3
struct v4l2_ctrl {int val;};
struct handler {struct v4l2_ctrl ctrl[4];int missing;};
struct ov13858 {struct {struct handler *ctrl_handler;} sd;void *dev;};
static u32 regs[6];
static unsigned addresses[6]={0x3500,0x3508,0x5100,0x5102,0x5104,0x4503};
static unsigned sizes[6]={3,2,2,2,2,1};
static int fail_read, reads, assertions, negatives;
static struct v4l2_ctrl *v4l2_ctrl_find(struct handler *h,int id){return h->missing==id?NULL:&h->ctrl[id];}
static int ov13858_read_reg(struct ov13858 *s,unsigned address,unsigned size,u32 *v){
 (void)s;int i=reads++;if(i>=6 || address!=addresses[i] || size!=sizes[i])abort();
 if(i==fail_read)return -EIO;
 *v=regs[i];return 0;
}
#define dev_info(dev,fmt,...) do {(void)(dev);printf(fmt,__VA_ARGS__);}while(0)
#include "native-rear-sensor-controls.inc"
static void check(bool ok){assertions++;if(!ok)abort();}
static void reset(struct handler *h,int pattern){
 h->missing=-1;h->ctrl[0].val=1600;h->ctrl[1].val=128;h->ctrl[2].val=1024;h->ctrl[3].val=pattern;
 regs[0]=25600;regs[1]=128;regs[2]=regs[3]=regs[4]=1024;regs[5]=pattern?0x80U|(pattern-1):0U;
 reads=0;fail_read=-1;
}
int main(void){
 struct handler h;struct ov13858 s={.sd={&h},.dev=NULL};
 for(int p=0;p<=4;p++){reset(&h,p);check(native_rear_sensor_controls_readback(&s)==0);check(reads==6);}
 reset(&h,0);regs[5]=3;check(native_rear_sensor_controls_readback(&s)==0); /* Disabled retains selection bits */
 for(int i=0;i<6;i++){reset(&h,1);fail_read=i;check(native_rear_sensor_controls_readback(&s)==-EIO);check(reads==i+1);negatives++;}
 for(int i=0;i<4;i++){reset(&h,0);h.missing=i;check(native_rear_sensor_controls_readback(&s)==-EPROTO);check(reads==0);negatives++;}
 for(int i=0;i<6;i++){reset(&h,1);regs[i]^=1;check(native_rear_sensor_controls_readback(&s)==-EPROTO);negatives++;}
 reset(&h,0);regs[5]=128;check(native_rear_sensor_controls_readback(&s)==-EPROTO);negatives++;
 for(int lines=4;lines<=3206;lines+=1601){reset(&h,0);h.ctrl[0].val=lines;regs[0]=(u32)lines<<4;check(native_rear_sensor_controls_readback(&s)==0);}
 printf("SENSOR_READBACK_MODEL_PASS assertions=%d negatives=%d\n",assertions,negatives);
 return 0;
}
