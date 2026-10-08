/* SPDX-License-Identifier: GPL-2.0-only */
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>
#define REAR_TRIGGER (V4L2_CID_USER_BASE + 0x1244)
int main(int argc,char **argv){
 if(argc!=2)return 2;
 int fd=open(argv[1],O_RDWR|O_CLOEXEC);if(fd<0)return 3;
 struct v4l2_capability cap={0};
 struct v4l2_queryctrl query={.id=REAR_TRIGGER};
 if(ioctl(fd,VIDIOC_QUERYCAP,&cap)||ioctl(fd,VIDIOC_QUERYCTRL,&query)){close(fd);return 4;}
 unsigned capabilities=(cap.capabilities&V4L2_CAP_DEVICE_CAPS)?cap.device_caps:cap.capabilities;
 if(!(capabilities&V4L2_CAP_VIDEO_CAPTURE_MPLANE)||query.type!=V4L2_CTRL_TYPE_BOOLEAN||
    query.minimum!=0||query.maximum!=1||query.default_value!=0||
    (query.flags&(V4L2_CTRL_FLAG_WRITE_ONLY|V4L2_CTRL_FLAG_EXECUTE_ON_WRITE))!=
    (V4L2_CTRL_FLAG_WRITE_ONLY|V4L2_CTRL_FLAG_EXECUTE_ON_WRITE)){close(fd);return 5;}
 struct v4l2_control control={.id=REAR_TRIGGER,.value=1};struct timespec start,end;
 clock_gettime(CLOCK_MONOTONIC,&start);errno=0;
 int result=ioctl(fd,VIDIOC_S_CTRL,&control),error=result<0?errno:0;
 clock_gettime(CLOCK_MONOTONIC,&end);
 long long us=(end.tv_sec-start.tv_sec)*1000000LL+(end.tv_nsec-start.tv_nsec)/1000;
 /* Exactly one write; never retry this descriptor, module or candidate. */
 close(fd);
 printf("{\"ioctl_return\":%d,\"errno\":%d,\"elapsed_us\":%lld,\"trigger_writes\":1,\"pixel_buffers_requested\":0}\n",result,error,us);
 return result==0&&error==0?0:6;
}
