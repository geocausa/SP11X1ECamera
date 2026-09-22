/* Camera-free fake-device lifecycle tests. Linker wrapping prevents device access. */
#define E004KQ_NO_MAIN
#include "front-direct-publisher.c"
#include <assert.h>
#include <stdarg.h>
static int scenario,started,stopped,writes,closed,mapped,unmapped,seq;
FILE *__wrap_fopen(const char *name,const char *mode) {
    (void)mode;assert(!strcmp(name,"/proc/cmdline"));
    static char cmd[]="test sp11_camera_e004kw_rgb_session=1";
    return fmemopen(cmd,strlen(cmd),"r");
}
uid_t __wrap_geteuid(void) { return 0; }
int __wrap_open(const char *name,int flags,...) {
    (void)flags;
    if(!strcmp(name,"/dev/video0")) return 1001;
    assert(!strcmp(name,"/dev/video91"));return 1002;
}
int __wrap_fstat(int fd,struct stat *st) {
    assert(fd==1001 || fd==1002);memset(st,0,sizeof(*st));st->st_mode=S_IFCHR;return 0;
}
int __wrap_close(int fd) { assert(fd==1001 || fd==1002);closed++;return 0; }
void *__wrap_mmap(void *addr,size_t length,int prot,int flags,int fd,off_t off) {
    (void)addr;(void)prot;(void)flags;(void)off;assert(fd==1001);mapped++;return calloc(1,length);
}
int __wrap_munmap(void *addr,size_t length) { (void)length;unmapped++;free(addr);return 0; }
int __wrap_poll(struct pollfd *p,nfds_t n,int timeout) {
    (void)timeout;assert(n==1);
    p->revents=scenario==5?POLLERR:p->events;
    if(scenario==6) stop_requested(SIGTERM);
    return 1;
}
ssize_t __wrap_write(int fd,const void *buf,size_t n) {
    assert(fd==1002 && buf && n==DST_BYTES);writes++;
    return scenario==4?(ssize_t)n-1:(ssize_t)n;
}
int __wrap_ioctl(int fd,unsigned long op,...) {
    va_list args;va_start(args,op);void *v=va_arg(args,void*);va_end(args);
    if(op==VIDIOC_QUERYCAP) {
        struct v4l2_capability *c=v;
        strcpy((char*)c->driver,fd==1001?"qcom-camss":"v4l2 loopback");
        strcpy((char*)c->card,"SP11-Front-Preview");
        c->capabilities=fd==1001?(V4L2_CAP_VIDEO_CAPTURE_MPLANE|V4L2_CAP_STREAMING):(V4L2_CAP_VIDEO_OUTPUT|V4L2_CAP_READWRITE);
    } else if(op==VIDIOC_G_FMT) {
        struct v4l2_pix_format_mplane *p=&((struct v4l2_format*)v)->fmt.pix_mp;
        p->width=SRC_W;p->height=SRC_H;p->num_planes=1;p->pixelformat=V4L2_PIX_FMT_SRGGB10P;
        p->plane_fmt[0].bytesperline=SRC_STRIDE;p->plane_fmt[0].sizeimage=SRC_BYTES;
        if(scenario==1)p->pixelformat=V4L2_PIX_FMT_NV12;
    } else if(op==VIDIOC_REQBUFS) {
        assert(((struct v4l2_requestbuffers*)v)->count==4);
    } else if(op==VIDIOC_QUERYBUF) {
        struct v4l2_buffer *b=v;b->m.planes[0].length=SRC_BYTES;
    } else if(op==VIDIOC_STREAMON) started++;
    else if(op==VIDIOC_STREAMOFF) { stopped++; if(scenario==7) { errno=EIO; return -1; } }
    else if(op==VIDIOC_DQBUF) {
        struct v4l2_buffer *b=v;b->index=(unsigned)seq%4;b->sequence=(unsigned)seq++;
        b->timestamp.tv_sec=1;b->timestamp.tv_usec=seq*33333;
        b->m.planes[0].length=SRC_BYTES;b->m.planes[0].bytesused=SRC_BYTES;
        if(scenario==2)b->m.planes[0].bytesused--;
        if(scenario==3)b->flags|=V4L2_BUF_FLAG_ERROR;
    } else assert(op==VIDIOC_QBUF || op==VIDIOC_S_FMT);
    return 0;
}
int main(void) {
    assert(token_allowed("sp11_camera_e004kw_rgb_session=1"));
    assert(!token_allowed("xsp11_camera_e004kw_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004kw_rgb_session=10"));
    assert(!token_allowed("sp11_camera_e004km_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004kp_rgb_session=1"));
    for(scenario=0;scenario<8;scenario++) {
        started=stopped=writes=closed=mapped=unmapped=seq=0;stopping=0;
        char *argv[]={"test","--source","/dev/video0","4",NULL};
        int rc=front_publisher_main(4,argv);
        assert((scenario==0)==(rc==0));
        assert(started==stopped && mapped==unmapped);
        assert(closed==(scenario==1?1:2));
        if(scenario==0)assert(writes==4 && started==1);
        if(scenario==1)assert(!started && !writes && !mapped);
    }
    puts("E004KQ_FAKE_DEVICE_TESTS=PASS CASES=8 TOKEN_NEGATIVES=4");
    return 0;
}
