/* SPDX-License-Identifier: GPL-2.0-only */
/* MMAP allocation/release only. Never queues buffers or starts streaming. */
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
static int request(int fd,unsigned long op,void *arg) {
 switch(op) {
 case VIDIOC_QUERYCAP:case VIDIOC_G_FMT:case VIDIOC_REQBUFS:case VIDIOC_QUERYBUF:break;
 default:fprintf(stderr,"non-allocation ioctl refused\n");return -1;
 }
 int ret;
 do {ret=ioctl(fd,op,arg);} while(ret<0&&errno==EINTR);
 return ret;
}
static int failure(const char *s) { perror(s);return 1; }
int main(int argc,char **argv) {
 if(argc!=2||strncmp(argv[1],"/dev/video",10))return 2;
 char cmd[4096];FILE *f=fopen("/proc/cmdline","r");
 if(!f||!fgets(cmd,sizeof(cmd),f))return 2;
 fclose(f);
 if(!strstr(cmd,"sp11_camera_upstream_front_20261014_04=1") ||
    !strstr(cmd,"sp11_entry=sp11-camera-upstream-front-20261014-04"))return 2;
 unsigned mapped=0,allocated=0;unsigned long long total=0;
 for(unsigned cycle=0;cycle<3;cycle++) {
  int fd=open(argv[1],O_RDWR|O_NONBLOCK|O_CLOEXEC);
  if(fd<0)return failure("open");
  struct v4l2_capability cap={0};
  if(request(fd,VIDIOC_QUERYCAP,&cap))return failure("QUERYCAP");
  if(!(cap.device_caps&V4L2_CAP_VIDEO_CAPTURE_MPLANE))return 3;
  struct v4l2_format fmt={.type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE};
  if(request(fd,VIDIOC_G_FMT,&fmt))return failure("G_FMT");
  unsigned planes=fmt.fmt.pix_mp.num_planes;
  if(!planes||planes>3)return 3;
  for(unsigned p=0;p<planes;p++)
   if(!fmt.fmt.pix_mp.plane_fmt[p].sizeimage||fmt.fmt.pix_mp.plane_fmt[p].sizeimage>16*1024*1024)return 3;
  struct v4l2_requestbuffers r={.count=1,.type=fmt.type,.memory=V4L2_MEMORY_DMABUF};
  errno=0;
  if(request(fd,VIDIOC_REQBUFS,&r)!=-1||errno!=EINVAL)return 4;
  r=(struct v4l2_requestbuffers){.count=3,.type=fmt.type,.memory=V4L2_MEMORY_MMAP};
  if(request(fd,VIDIOC_REQBUFS,&r))return failure("REQBUFS");
  if(r.count!=3)return 4;
  allocated+=r.count;
  void *maps[3][3]={{0}};unsigned lengths[3][3]={{0}};
  for(unsigned i=0;i<r.count;i++) {
   struct v4l2_plane ps[3]={{0}};
   struct v4l2_buffer b={.index=i,.type=fmt.type,.memory=V4L2_MEMORY_MMAP,.length=planes,.m.planes=ps};
   if(request(fd,VIDIOC_QUERYBUF,&b))return failure("QUERYBUF");
   if(b.length!=planes)return 4;
   for(unsigned p=0;p<planes;p++) {
    if(!ps[p].length||ps[p].length>16*1024*1024)return 4;
    lengths[i][p]=ps[p].length;
    maps[i][p]=mmap(NULL,ps[p].length,PROT_READ,MAP_SHARED,fd,ps[p].m.mem_offset);
    if(maps[i][p]==MAP_FAILED)return failure("mmap");
    /* Do not read/write pixels, compute image hashes or save mappings. */
    mapped++;total+=ps[p].length;
   }
  }
  for(unsigned i=0;i<r.count;i++)for(unsigned p=0;p<planes;p++)
   if(munmap(maps[i][p],lengths[i][p]))return failure("munmap");
  r.count=0;
  if(request(fd,VIDIOC_REQBUFS,&r))return failure("REQBUFS release");
  if(close(fd))return failure("close");
 }
 printf("{\"status\":\"PASS_MMAP_ALLOCATE_MAP_RELEASE\",\"cycles\":3,\"buffers\":%u,\"plane_maps\":%u,\"mapped_bytes_total\":%llu,\"dmabuf_import_refusals\":3,\"streamon\":false,\"queued_buffers\":0,\"pixels_accessed\":false}\n",allocated,mapped,total);
 return 0;
}
