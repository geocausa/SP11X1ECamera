#include <errno.h>
#include <fcntl.h>
#include <linux/media-bus-format.h>
#include <linux/v4l2-subdev.h>
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
static long long get64(int fd, __u32 id, const char *name) {
    struct v4l2_ext_control c; if(get_ext(fd,id,&c)<0){perror(name);return -1;} return c.value64;
}
int main(int argc,char **argv){
    const char *dev=argc>1?argv[1]:"/dev/v4l-subdev25";
    int fd=open(dev,O_RDONLY|O_CLOEXEC); if(fd<0){perror("open");return 1;}
    struct v4l2_ext_control lc; if(get_ext(fd,V4L2_CID_LINK_FREQ,&lc)<0){perror("GET LINK_FREQ");return 2;}
    struct v4l2_querymenu qm; memset(&qm,0,sizeof(qm)); qm.id=V4L2_CID_LINK_FREQ; qm.index=(__u32)lc.value;
    if(ioctl(fd,VIDIOC_QUERYMENU,&qm)<0){perror("QUERYMENU LINK_FREQ");return 3;}
    long long pix=get64(fd,V4L2_CID_PIXEL_RATE,"PIXEL_RATE");
    long long hb=get64(fd,V4L2_CID_HBLANK,"HBLANK");
    long long vb=get64(fd,V4L2_CID_VBLANK,"VBLANK");
    printf("LINK_FREQ index=%d value=%lld\n",lc.value,(long long)qm.value);
    printf("PIXEL_RATE=%lld HBLANK=%lld VBLANK=%lld\n",pix,hb,vb);
    unsigned n=0;
    for(unsigned i=0;i<8;i++){
      struct v4l2_subdev_frame_size_enum f; memset(&f,0,sizeof(f));
      f.index=i; f.pad=0; f.code=MEDIA_BUS_FMT_SGRBG10_1X10; f.which=V4L2_SUBDEV_FORMAT_ACTIVE;
      if(ioctl(fd,VIDIOC_SUBDEV_ENUM_FRAME_SIZE,&f)<0){ if(errno==EINVAL) break; perror("ENUM_FRAME_SIZE"); return 4; }
      printf("FRAME_SIZE[%u]=%ux%u..%ux%u\n",i,f.min_width,f.min_height,f.max_width,f.max_height); n++;
    }
    close(fd);
    if((long long)qm.value!=592800000LL || pix!=432732960LL || hb!=412 || vb!=408 || n!=1) return 10;
    return 0;
}
