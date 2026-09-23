/* SPDX-License-Identifier: MIT
 * E004kq: bounded rear RAW10 mmap -> unchanged software NV12 -> V4L2 write.
 * No graph/sensor/boot/module changes. Default build refuses all live capture.
 */
#define main pipe_converter_main
#include "rear-convert.c"
#undef main
/* Unique sealed source-defined token; never pass through GCC shell quoting. */
#define SP11_CAMERA_BOOT_TOKEN "sp11_camera_e004mf_rgb_session=1"
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <signal.h>
#include <limits.h>
#include <stdbool.h>
#include "raw-nv12-probe.h"
#if defined(SP11_CAMERA_ALLOW_RAW_PROFILE) && SP11_CAMERA_ALLOW_RAW_PROFILE
#include "iq/raw10_profile.h"
/* Isolated opt-in new-candidate in-memory sensor diagnostics; no frames or
 * spatial pixel positions are exported and normal builds compile it out. */
static int profile_source_raw10(const uint8_t *pixels,long frame_number) {
    struct sp11_raw10_profile statistics;
    if (sp11_raw10_profile_frame(pixels,SRC_BYTES,SRC_STRIDE,SRC_W,SRC_H,
                SP11_RGB_GRBG,16u,&statistics)) return -1;
    static const char *names[4]={"R","G0","G1","B"};
    fprintf(stderr,"SP11_RGB_RAW10_PROFILE camera=rear frame=%ld blocks=%zu",
            frame_number,statistics.sampled_bayer_blocks);
    for (unsigned k=0;k<4;k++) {
        const struct sp11_raw10_channel *v=&statistics.channel[k];
        fprintf(stderr," %s_p01=%u %s_p50=%u %s_p95=%u %s_p99=%u"
                       " %s_min=%u %s_max=%u %s_lsb0=%llu %s_lsb1=%llu"
                       " %s_lsb2=%llu %s_lsb3=%llu",
                names[k],(unsigned)v->p01,names[k],(unsigned)v->p50,
                names[k],(unsigned)v->p95,names[k],(unsigned)v->p99,
                names[k],(unsigned)v->lowest,names[k],(unsigned)v->highest,
                names[k],(unsigned long long)v->low_two_bits[0],
                names[k],(unsigned long long)v->low_two_bits[1],
                names[k],(unsigned long long)v->low_two_bits[2],
                names[k],(unsigned long long)v->low_two_bits[3]);
    }
    fputc('\n',stderr);
    return 0;
}
#endif
static volatile sig_atomic_t stopping;
static void stop_requested(int sig) { (void)sig; stopping=1; }
static int xioctl(int fd,unsigned long op,void *arg) {
    int rc;
    do { rc=ioctl(fd,op,arg); } while(rc<0 && errno==EINTR && !stopping);
    return rc;
}
#ifndef SP11_CAMERA_BOOT_TOKEN
#define SP11_CAMERA_BOOT_TOKEN ""
#endif
static bool token_allowed(const char *cmd) {
    const char *token=SP11_CAMERA_BOOT_TOKEN;
    size_t n=strlen(token);
    if(!n) return false;
    const char *p=cmd;
    while((p=strstr(p,token))) {
        if((p==cmd || p[-1]==' ' || p[-1]=='\n') &&
           (p[n]==0 || p[n]==' ' || p[n]=='\n')) return true;
        p+=n;
    }
    return false;
}
static bool source_format_ok(const struct v4l2_format *f) {
    const struct v4l2_pix_format_mplane *p=&f->fmt.pix_mp;
    return f->type==V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE &&
        p->width==SRC_W && p->height==SRC_H &&
        p->pixelformat==V4L2_PIX_FMT_SGRBG10P && p->num_planes==1 &&
        p->plane_fmt[0].bytesperline==SRC_STRIDE &&
        p->plane_fmt[0].sizeimage==SRC_BYTES;
}
static bool payload_ok(const struct v4l2_buffer *b,const struct v4l2_plane *p,
                       unsigned count,const size_t *lengths) {
    return b->index<count && b->length==1 && !(b->flags&V4L2_BUF_FLAG_ERROR) &&
        p->data_offset==0 && p->bytesused==SRC_BYTES &&
        p->length==lengths[b->index] && p->bytesused<=lengths[b->index];
}
static int ready(int fd,short events,double deadline) {
    for(;;) {
        if(stopping || ms()>=deadline) { errno=ETIMEDOUT; return -1; }
        struct pollfd p={.fd=fd,.events=events};
        int rc=poll(&p,1,250);
        if(rc<0 && errno==EINTR) continue;
        if(rc<0 || (p.revents&(POLLERR|POLLHUP|POLLNVAL))) return -1;
        if(rc>0 && (p.revents&events)) return 0;
    }
}
int rear_publisher_main(int argc,char **argv) {
    if(argc!=4 || strcmp(argv[1],"--source") || strncmp(argv[2],"/dev/video",10)) {
        fputs("usage: --source /dev/videoN FRAME_COUNT_1_TO_2400|continuous\n",stderr);return 2;
    }
    const char *suffix=argv[2]+10;
    if(!*suffix || strspn(suffix,"0123456789")!=strlen(suffix) ||
       !strcmp(argv[2],"/dev/video90") || !strcmp(argv[2],"/dev/video91")) return 2;
    /* Long-lived mode is disabled in normal builds and opt-in only for
     * a new source-pinned guarded candidate with a distinct boot token.
     * A four-hour hard deadline remains FAIL (never silently restart).
     */
    const bool continuous=strcmp(argv[3],"continuous")==0;
#if !defined(SP11_CAMERA_ALLOW_CONTINUOUS) || !SP11_CAMERA_ALLOW_CONTINUOUS
    if(continuous) return 2;
#endif
    long requested=LONG_MAX;
    if(!continuous) {
        char *end;errno=0;requested=strtol(argv[3],&end,10);
        if(errno || end==argv[3] || *end || requested<1 || requested>2400) return 2;
    }
    char cmd[8192]={0};FILE *cf=fopen("/proc/cmdline","r");
    if(!cf) return 1;
    bool read_ok=fgets(cmd,sizeof(cmd),cf)!=NULL;fclose(cf);
    if(geteuid()!=0 || !read_ok || !token_allowed(cmd)) {
        fputs("E004KQ_REFUSE_OUTSIDE_FRESH_E004KR_CANDIDATE\n",stderr);return 1;
    }
    struct sigaction sa={0};sa.sa_handler=stop_requested;
    sigemptyset(&sa.sa_mask);sigaction(SIGTERM,&sa,NULL);sigaction(SIGINT,&sa,NULL);
    int src=-1,dst=-1,rc=1; bool streaming=false;
    void *maps[4]={0};size_t lengths[4]={0};unsigned count=0;
    long completed=0,captured=0;uint32_t first_seq=0,last_seq=0;unsigned long gaps=0;
    double first_ts=0,last_ts=0,conversion=0,publication=0;
    double begin=ms(),deadline=begin+(continuous?14400000.0:210000.0);
    enum v4l2_buf_type type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    src=open(argv[2],O_RDWR|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
    if(src<0) goto cleanup;
    struct stat st;
    if(fstat(src,&st) || !S_ISCHR(st.st_mode)) goto cleanup;
    struct v4l2_capability cap={0};
    if(xioctl(src,VIDIOC_QUERYCAP,&cap) || strcmp((char*)cap.driver,"qcom-camss")) goto cleanup;
    uint32_t caps=(cap.capabilities&V4L2_CAP_DEVICE_CAPS)?cap.device_caps:cap.capabilities;
    if((caps&(V4L2_CAP_VIDEO_CAPTURE_MPLANE|V4L2_CAP_STREAMING)) !=
             (V4L2_CAP_VIDEO_CAPTURE_MPLANE|V4L2_CAP_STREAMING)) goto cleanup;
    struct v4l2_format fmt={.type=type};
    if(xioctl(src,VIDIOC_G_FMT,&fmt) || !source_format_ok(&fmt)) goto cleanup;
    dst=open("/dev/video90",O_RDWR|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
    if(dst<0 || fstat(dst,&st) || !S_ISCHR(st.st_mode)) goto cleanup;
    memset(&cap,0,sizeof(cap));
    if(xioctl(dst,VIDIOC_QUERYCAP,&cap) || strcmp((char*)cap.driver,"v4l2 loopback") ||
       strcmp((char*)cap.card,"SP11-Rear-Preview")) goto cleanup;
    caps=(cap.capabilities&V4L2_CAP_DEVICE_CAPS)?cap.device_caps:cap.capabilities;
    if(!(caps&V4L2_CAP_VIDEO_OUTPUT) || !(caps&V4L2_CAP_READWRITE)) goto cleanup;
    struct v4l2_format output={.type=V4L2_BUF_TYPE_VIDEO_OUTPUT};
    output.fmt.pix.width=DST_W;output.fmt.pix.height=DST_H;
    output.fmt.pix.pixelformat=V4L2_PIX_FMT_NV12;output.fmt.pix.field=V4L2_FIELD_NONE;
    output.fmt.pix.bytesperline=DST_W;output.fmt.pix.sizeimage=DST_BYTES;
    if(xioctl(dst,VIDIOC_S_FMT,&output) ||
       output.fmt.pix.width!=DST_W || output.fmt.pix.height!=DST_H ||
       output.fmt.pix.pixelformat!=V4L2_PIX_FMT_NV12 ||
       output.fmt.pix.bytesperline!=DST_W || output.fmt.pix.sizeimage!=DST_BYTES) goto cleanup;
    struct v4l2_requestbuffers req={.count=4,.type=type,.memory=V4L2_MEMORY_MMAP};
    if(xioctl(src,VIDIOC_REQBUFS,&req) || req.count<2 || req.count>4) goto cleanup;
    count=req.count;
    for(unsigned i=0;i<count;i++) {
        struct v4l2_plane plane={0};
        struct v4l2_buffer b={.type=type,.memory=V4L2_MEMORY_MMAP,.index=i,.length=1,.m.planes=&plane};
        if(xioctl(src,VIDIOC_QUERYBUF,&b) || b.length!=1 || plane.length<SRC_BYTES) goto cleanup;
        lengths[i]=plane.length;
        maps[i]=mmap(NULL,plane.length,PROT_READ|PROT_WRITE,MAP_SHARED,src,plane.m.mem_offset);
        if(maps[i]==MAP_FAILED) { maps[i]=NULL; goto cleanup; }
        if(xioctl(src,VIDIOC_QBUF,&b)) goto cleanup;
    }
    nv12=malloc(DST_BYTES);if(!nv12) goto cleanup;plan_offsets();
    if(xioctl(src,VIDIOC_STREAMON,&type)) goto cleanup;
    streaming=true;
    while(completed<requested && !stopping) {
        if(ready(src,POLLIN,deadline)) goto cleanup;
        struct v4l2_plane plane={0};
        struct v4l2_buffer b={.type=type,.memory=V4L2_MEMORY_MMAP,.length=1,.m.planes=&plane};
        if(xioctl(src,VIDIOC_DQBUF,&b)) {
            if(errno==EAGAIN) continue;
            goto cleanup;
        }
        if(!payload_ok(&b,&plane,count,lengths)) goto cleanup;
        double stamp=b.timestamp.tv_sec+b.timestamp.tv_usec/1000000.0;
        if(completed && (b.sequence<=last_seq || stamp<=last_ts)) goto cleanup;
        if(!completed) { first_seq=b.sequence; first_ts=stamp; }
        else gaps+=b.sequence-last_seq-1;
        last_seq=b.sequence;last_ts=stamp;captured++;
        frame=maps[b.index];
#if defined(SP11_CAMERA_ALLOW_RAW_PROFILE) && SP11_CAMERA_ALLOW_RAW_PROFILE
        /* Probe the SAME bounded native mmap frame before its RAW8→NV12
         * conversion and before original owner requeues its buffer. */
        if (captured==1 || captured==30 || captured==90 || captured==180 ||
            captured==600 || captured==630) {
            if (profile_source_raw10(frame,captured)) goto cleanup;
        }
#endif
        double t=ms();convert();conversion+=ms()-t;
        /* READ ONLY same-frame RAW10 high-byte and NV12 luma histogram.
         * The unchanged source release/QBUF remains AFTER this brief
         * scalar-only measurement; no pixel data leaves this process. */
        if(captured==1 || captured==30 || captured==90 || captured==180 ||
           (captured>180 && captured<=3600 && captured%30==0)) {
            struct sp11_mc_pair pair;
            if(!sp11_mc_measure(frame,nv12,SRC_W,SRC_H,SRC_STRIDE,
                                DST_W,DST_H,1,CROP_X,CROP_Y,&pair)) goto cleanup;
            sp11_mc_report("rear",captured,&pair);
        }
        /* Release the physical buffer as soon as conversion ends. */
        if(xioctl(src,VIDIOC_QBUF,&b)) goto cleanup;
        t=ms();
        if(ready(dst,POLLOUT,deadline)) goto cleanup;
        ssize_t n;
        do { n=write(dst,nv12,DST_BYTES); } while(n<0 && errno==EINTR && !stopping);
        if(n!=DST_BYTES) goto cleanup;
        publication+=ms()-t;completed++;
    }
    if(!continuous && completed==requested && !stopping) rc=0;
cleanup:;
    bool stop_ok=!streaming;
    if(streaming) { stop_ok=xioctl(src,VIDIOC_STREAMOFF,&type)==0; if(!stop_ok) rc=1; }
    if(stopping && stop_ok) rc=143;
    for(unsigned i=0;i<count;i++) if(maps[i]) munmap(maps[i],lengths[i]);
    if(src>=0) close(src);
    if(dst>=0) close(dst);
    free(nv12);nv12=NULL;frame=NULL;
    fprintf(stderr,"E004KQ_LIFECYCLE captured=%ld published=%ld termination_requested=%d streamoff_completed=%d\n",captured,completed,(int)stopping,(int)stop_ok);
    fprintf(stderr,"{\"status\":\"%s\",\"frames\":%ld,\"requested\":%ld,\"continuous\":%s,"
        "\"source_sequence_first_last\":[%u,%u],\"source_sequence_gaps\":%lu,"
        "\"source_span_s\":%.6f,\"conversion_mean_ms\":%.3f,"
        "\"publication_mean_ms\":%.3f,\"elapsed_ms\":%.3f,"
        "\"raw_pipe_copy\":false,\"pixel_files_written\":false}\n",
        rc?(rc==143?"STOPPED":"FAIL"):"PASS",completed,continuous?0:requested,
        continuous?"true":"false",first_seq,last_seq,gaps,last_ts-first_ts,
        completed?conversion/completed:0,completed?publication/completed:0,ms()-begin);
    return rc;
}

#ifndef E004KQ_NO_MAIN
int main(int argc,char **argv) { return rear_publisher_main(argc,argv); }
#endif
