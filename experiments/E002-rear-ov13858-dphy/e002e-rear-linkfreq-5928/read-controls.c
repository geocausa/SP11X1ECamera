#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

static int get_ext(int fd, __u32 id, struct v4l2_ext_control *c) {
    struct v4l2_ext_controls cs;
    memset(&cs,0,sizeof(cs)); memset(c,0,sizeof(*c));
    cs.which=V4L2_CTRL_WHICH_CUR_VAL; cs.count=1; cs.controls=c; c->id=id;
    return ioctl(fd,VIDIOC_G_EXT_CTRLS,&cs);
}
int main(int argc,char **argv){
    const char *dev=argc>1?argv[1]:"/dev/v4l-subdev25";
    int fd=open(dev,O_RDONLY|O_CLOEXEC); if(fd<0){perror("open");return 1;}
    struct v4l2_query_ext_ctrl q; memset(&q,0,sizeof(q)); q.id=V4L2_CID_LINK_FREQ;
    if(ioctl(fd,VIDIOC_QUERY_EXT_CTRL,&q)<0){perror("QUERY LINK_FREQ");return 2;}
    struct v4l2_ext_control lc; if(get_ext(fd,V4L2_CID_LINK_FREQ,&lc)<0){perror("GET LINK_FREQ");return 3;}
    struct v4l2_querymenu qm; memset(&qm,0,sizeof(qm)); qm.id=V4L2_CID_LINK_FREQ; qm.index=(__u32)lc.value;
    if(ioctl(fd,VIDIOC_QUERYMENU,&qm)<0){perror("QUERYMENU LINK_FREQ");return 4;}
    printf("LINK_FREQ index=%d value=%lld type=%u flags=0x%x\n",lc.value,(long long)qm.value,q.type,q.flags);
    memset(&q,0,sizeof(q)); q.id=V4L2_CID_PIXEL_RATE;
    if(ioctl(fd,VIDIOC_QUERY_EXT_CTRL,&q)<0){perror("QUERY PIXEL_RATE");return 5;}
    struct v4l2_ext_control pc; if(get_ext(fd,V4L2_CID_PIXEL_RATE,&pc)<0){perror("GET PIXEL_RATE");return 6;}
    printf("PIXEL_RATE value=%lld type=%u flags=0x%x min=%lld max=%lld\n",(long long)pc.value64,q.type,q.flags,(long long)q.minimum,(long long)q.maximum);
    close(fd);
    return (qm.value==592800000LL && pc.value64==474240000LL)?0:7;
}
