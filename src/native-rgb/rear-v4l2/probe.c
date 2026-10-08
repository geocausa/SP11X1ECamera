/* SPDX-License-Identifier: GPL-2.0-only */
/* One standard V4L2 capture. No mmap, read, pixel file or image hash. */
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <poll.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
static int call(int fd,unsigned long cmd,void *arg){
 int ret;do{ret=ioctl(fd,cmd,arg);}while(ret<0&&errno==EINTR);return ret;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 int fd=open(argv[1],O_RDWR|O_NONBLOCK|O_CLOEXEC),err=0;
 unsigned completed=0;bool streaming=false,stopped=false,released=false;
 const char *phase="open";
 if(fd<0){err=errno;goto report;}
 struct v4l2_format fmt={.type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE};
 fmt.fmt.pix_mp.width=3840;fmt.fmt.pix_mp.height=2160;
 fmt.fmt.pix_mp.pixelformat=V4L2_PIX_FMT_NV12;fmt.fmt.pix_mp.num_planes=1;
 phase="S_FMT";
 if(call(fd,VIDIOC_S_FMT,&fmt)<0){err=errno;goto cleanup;}
 if(fmt.fmt.pix_mp.width!=3840||fmt.fmt.pix_mp.height!=2160||
    fmt.fmt.pix_mp.pixelformat!=V4L2_PIX_FMT_NV12||fmt.fmt.pix_mp.num_planes!=1||
    fmt.fmt.pix_mp.plane_fmt[0].bytesperline!=3840||
    fmt.fmt.pix_mp.plane_fmt[0].sizeimage!=12441600){err=EPROTO;goto cleanup;}
 struct v4l2_requestbuffers req={.count=4,.type=fmt.type,.memory=V4L2_MEMORY_MMAP};
 phase="REQBUFS";
 if(call(fd,VIDIOC_REQBUFS,&req)<0){err=errno;goto cleanup;}
 if(req.count<4){err=ENOBUFS;goto cleanup;}
 for(unsigned i=0;i<4;i++){
  struct v4l2_plane planes[1]={{0}};
  struct v4l2_buffer b={.type=fmt.type,.memory=V4L2_MEMORY_MMAP,.index=i,.length=1,.m.planes=planes};
  phase="QUERYBUF_QBUF";
  if(call(fd,VIDIOC_QUERYBUF,&b)<0||planes[0].length<12441600||
     call(fd,VIDIOC_QBUF,&b)<0){err=errno?errno:EPROTO;goto cleanup;}
 }
 enum v4l2_buf_type type=fmt.type;phase="STREAMON";
 if(call(fd,VIDIOC_STREAMON,&type)<0){err=errno;goto cleanup;}
 streaming=true;
 while(completed<2){
  struct pollfd p={.fd=fd,.events=POLLIN};phase="poll_DQBUF";
  int ret;do{ret=poll(&p,1,5000);}while(ret<0&&errno==EINTR);
  if(ret<=0){err=ret==0?ETIMEDOUT:errno;goto cleanup;}
  struct v4l2_plane planes[1]={{0}};
  struct v4l2_buffer b={.type=fmt.type,.memory=V4L2_MEMORY_MMAP,.length=1,.m.planes=planes};
  if(call(fd,VIDIOC_DQBUF,&b)<0){err=errno;goto cleanup;}
  if(b.flags&V4L2_BUF_FLAG_ERROR||b.sequence!=completed||
     b.length!=1||planes[0].bytesused!=12441600){err=EPROTO;goto cleanup;}
  completed++;
 }
 phase="STREAMOFF";
 if(call(fd,VIDIOC_STREAMOFF,&type)<0){err=errno;goto cleanup;}
 streaming=false;stopped=true;
 req.count=0;phase="REQBUFS_zero";
 if(call(fd,VIDIOC_REQBUFS,&req)<0){err=errno;goto cleanup;}
 released=true;phase="complete";
cleanup:
 if(streaming){enum v4l2_buf_type t=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;call(fd,VIDIOC_STREAMOFF,&t);}
 close(fd);
report:
 printf("{\"phase\":\"%s\",\"errno\":%d,\"completed_frames\":%u,\"width\":3840,\"height\":2160,\"stride\":3840,\"bytesused\":12441600,\"STREAMOFF\":%s,\"REQBUFS_zero\":%s,\"pixel_bytes_read\":0}\n",phase,err,completed,stopped?"true":"false",released?"true":"false");
 return err?1:0;
}
