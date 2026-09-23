/* SPDX-License-Identifier: MIT
 * E004kq: bounded front RAW10 mmap -> unchanged software NV12 -> V4L2 write.
 * No graph/sensor/boot/module changes. Default build refuses all live capture.
 */
#define _GNU_SOURCE
/* Isolated E004nc studio-range publisher refuses a missing opt-in flag. */
#if !defined(SP11_RGB_NV12_VIDEO_RANGE) || !SP11_RGB_NV12_VIDEO_RANGE
#error E004NC_REFUSE_UNCORRECTED_NV12_OUTPUT_RANGE
#endif
#define main pipe_converter_main
#include "front-convert.c"
#undef main
#if !defined(SP11_RGB_FRONT_PREVIEW_TONE) || !SP11_RGB_FRONT_PREVIEW_TONE
#error E004NC_REFUSE_UNGATED_FRONT_1080_GAIN_TONE
#endif
#include "iq/front_preview_tone.h"
/* Unique sealed source-defined token; never pass through GCC shell quoting. */
#define SP11_CAMERA_BOOT_TOKEN "sp11_camera_e004nc_rgb_session=1"
#include <fcntl.h>
#include <sys/stat.h>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <signal.h>
#include <limits.h>
#include <stdbool.h>
#if !defined(SP11_RGB_NV12_BT601_TAG) || !SP11_RGB_NV12_BT601_TAG
#error E004NC_EXACT_BT601_OUTPUT_METADATA_EXPLICIT_OPTIN_REQUIRED
#endif
#include "iq/nv12_colorimetry.h"
#include "raw-nv12-probe.h"
#if defined(SP11_CAMERA_ALLOW_RAW_PROFILE) && SP11_CAMERA_ALLOW_RAW_PROFILE
#include "iq/raw10_profile.h"
/* Isolated opt-in new-candidate in-memory sensor diagnostics; no frames or
 * spatial pixel positions are exported and normal builds compile it out. */
static int profile_source_raw10(const uint8_t *pixels,long frame_number) {
    struct sp11_raw10_profile statistics;
    if (sp11_raw10_profile_frame(pixels,SRC_BYTES,SRC_STRIDE,SRC_W,SRC_H,
                SP11_RGB_RGGB,16u,&statistics)) return -1;
    static const char *names[4]={"R","G0","G1","B"};
    fprintf(stderr,"SP11_RGB_RAW10_PROFILE camera=front frame=%ld blocks=%zu",
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
        p->pixelformat==V4L2_PIX_FMT_SRGGB10P && p->num_planes==1 &&
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
        if(stopping || wall_ms()>=deadline) { errno=ETIMEDOUT; return -1; }
        struct pollfd p={.fd=fd,.events=events};
        int rc=poll(&p,1,250);
        if(rc<0 && errno==EINTR) continue;
        if(rc<0 || (p.revents&(POLLERR|POLLHUP|POLLNVAL))) return -1;
        if(rc>0 && (p.revents&events)) return 0;
    }
}
int front_publisher_main(int argc,char **argv) {
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
    double begin=wall_ms(),deadline=begin+(continuous?14400000.0:210000.0);
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
    dst=open("/dev/video91",O_RDWR|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
    if(dst<0 || fstat(dst,&st) || !S_ISCHR(st.st_mode)) goto cleanup;
    memset(&cap,0,sizeof(cap));
    if(xioctl(dst,VIDIOC_QUERYCAP,&cap) || strcmp((char*)cap.driver,"v4l2 loopback") ||
       strcmp((char*)cap.card,"SP11-Front-Preview")) goto cleanup;
    caps=(cap.capabilities&V4L2_CAP_DEVICE_CAPS)?cap.device_caps:cap.capabilities;
    if(!(caps&V4L2_CAP_VIDEO_OUTPUT) || !(caps&V4L2_CAP_READWRITE)) goto cleanup;
    struct v4l2_format output={.type=V4L2_BUF_TYPE_VIDEO_OUTPUT};
    output.fmt.pix.width=DST_W;output.fmt.pix.height=DST_H;
    output.fmt.pix.pixelformat=V4L2_PIX_FMT_NV12;output.fmt.pix.field=V4L2_FIELD_NONE;
    output.fmt.pix.bytesperline=DST_W;output.fmt.pix.sizeimage=DST_BYTES;
    sp11_rgb_nv12_request_bt601(&output.fmt.pix);
    fprintf(stderr,"E004NC_COLOR_DIAG camera=%s stage=request "
        "width=%u height=%u fourcc=%u bytesperline=%u sizeimage=%u "
        "colorspace=%u ycbcr_enc=%u quantization=%u xfer_func=%u\n",
        "front",(unsigned)output.fmt.pix.width,
        (unsigned)output.fmt.pix.height,(unsigned)output.fmt.pix.pixelformat,
        (unsigned)output.fmt.pix.bytesperline,(unsigned)output.fmt.pix.sizeimage,
        (unsigned)output.fmt.pix.colorspace,(unsigned)output.fmt.pix.ycbcr_enc,
        (unsigned)output.fmt.pix.quantization,(unsigned)output.fmt.pix.xfer_func);
    int set_fmt_rc=xioctl(dst,VIDIOC_S_FMT,&output);
    int set_fmt_errno=set_fmt_rc?errno:0;
    fprintf(stderr,"E004NC_COLOR_DIAG camera=%s stage=S_FMT_return "
        "rc=%d errno=%d width=%u height=%u fourcc=%u bytesperline=%u "
        "sizeimage=%u colorspace=%u ycbcr_enc=%u quantization=%u xfer_func=%u\n",
        "front",set_fmt_rc,set_fmt_errno,(unsigned)output.fmt.pix.width,
        (unsigned)output.fmt.pix.height,(unsigned)output.fmt.pix.pixelformat,
        (unsigned)output.fmt.pix.bytesperline,(unsigned)output.fmt.pix.sizeimage,
        (unsigned)output.fmt.pix.colorspace,(unsigned)output.fmt.pix.ycbcr_enc,
        (unsigned)output.fmt.pix.quantization,(unsigned)output.fmt.pix.xfer_func);
    struct v4l2_format independently_get_fmt={.type=V4L2_BUF_TYPE_VIDEO_OUTPUT};
    int get_fmt_rc=set_fmt_rc?-1:xioctl(dst,VIDIOC_G_FMT,&independently_get_fmt);
    int get_fmt_errno=get_fmt_rc?(set_fmt_rc?set_fmt_errno:errno):0;
    fprintf(stderr,"E004NC_COLOR_DIAG camera=%s stage=G_FMT_return "
        "rc=%d errno=%d width=%u height=%u fourcc=%u bytesperline=%u "
        "sizeimage=%u colorspace=%u ycbcr_enc=%u quantization=%u xfer_func=%u\n",
        "front",get_fmt_rc,get_fmt_errno,(unsigned)independently_get_fmt.fmt.pix.width,
        (unsigned)independently_get_fmt.fmt.pix.height,
        (unsigned)independently_get_fmt.fmt.pix.pixelformat,
        (unsigned)independently_get_fmt.fmt.pix.bytesperline,
        (unsigned)independently_get_fmt.fmt.pix.sizeimage,
        (unsigned)independently_get_fmt.fmt.pix.colorspace,
        (unsigned)independently_get_fmt.fmt.pix.ycbcr_enc,
        (unsigned)independently_get_fmt.fmt.pix.quantization,
        (unsigned)independently_get_fmt.fmt.pix.xfer_func);
    if(set_fmt_rc || get_fmt_rc ||
       !sp11_rgb_nv12_confirm_effective_bt601(&independently_get_fmt.fmt.pix)) {
        fputs("E004NC_V4L2_BT601_PRESTREAM_REQUEST_OR_INDEPENDENT_G_FMT_COLOUR_TAG_MISMATCH\n",stderr);
        goto cleanup;
    }
    if(set_fmt_rc ||
       output.fmt.pix.width!=DST_W || output.fmt.pix.height!=DST_H ||
       output.fmt.pix.pixelformat!=V4L2_PIX_FMT_NV12 ||
       output.fmt.pix.bytesperline!=DST_W || output.fmt.pix.sizeimage!=DST_BYTES) goto cleanup;
    if(!sp11_rgb_nv12_confirm_effective_bt601(&output.fmt.pix)) {
        fputs("E004NC_V4L2_BT601_NATIVE_LOOPBACK_S_FMT_COLOUR_TAG_MISMATCH\n",stderr);
        goto cleanup;
    }
    fprintf(stderr,"E004NC_REAL_V4L2_OUTPUT_COLORIMETRY camera=%s "
        "width=%d height=%d colorspace=%d ycbcr_enc=%d "
        "quantization=%d xfer_func=%d effective_bt601=YES\n",
        "front",DST_W,DST_H,output.fmt.pix.colorspace,
        output.fmt.pix.ycbcr_enc,output.fmt.pix.quantization,
        output.fmt.pix.xfer_func);
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
    nv12=malloc(DST_BYTES);if(!nv12) goto cleanup;for(int x=0;x<SRC_W;x++)mipi_high_index[x]=(x/4)*5+x%4;
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
        raw=maps[b.index];
#if defined(SP11_CAMERA_ALLOW_RAW_PROFILE) && SP11_CAMERA_ALLOW_RAW_PROFILE
        /* Probe the SAME bounded native mmap frame before its RAW8→NV12
         * conversion and before original owner requeues its buffer. */
        if (captured==1 || captured==30 || captured==90 || captured==180 ||
            captured==600 || captured==630) {
            if (profile_source_raw10(raw,captured)) goto cleanup;
        }
#endif
        double t=wall_ms();convert();
        /* Source and converted output are paired on this exact queued frame.
         * Never persist either plane or a tile/pixel hash. Source remains
         * owned until the original guarded QBUF below completes. */
        if(captured==1 || captured==30 || captured==90 || captured==180 ||
           (captured>180 && captured<=3600 && captured%30==0)) {
            struct sp11_mc_pair pair;
            if(!sp11_mc_measure(raw,nv12,SRC_W,SRC_H,SRC_STRIDE,
                                DST_W,DST_H,2,0,0,&pair)) goto cleanup;
            sp11_mc_report("front",captured,&pair);
        }
        /* CRITICAL: source/converted untoned same-frame RAW10/NV12
         * reference above is captured BEFORE this new opt-in FRONT
         * DISPLAY-ONLY Y mapping. No native sensor controls or UV change.
         * Normal maintained front publisher never compiles this helper.
         * Full 1080p output is consumed by an independent uid1000 app;
         * never mistake a brightness lift for recovered scene detail.
         */
        struct sp11_front_preview_tone_result ft={0};
        if(sp11_front_optin_tone_nv12(nv12,DST_BYTES,DST_W,DST_H,&ft))
            goto cleanup;
        if(captured==1 || captured==30 || captured==90 || captured==180 ||
           captured==600 || captured==601 || captured==610 ||
           captured==630 || captured==631 || captured==640 ||
           captured==650 || captured==690) {
            fprintf(stderr,"E004NC_FRONT_PREVIEW_TONE frame=%ld seq=%u "
                "applied=%d p01=%u p50=%u p99=%u "
                "output_p01=%u output_p50=%u output_p99=%u "
                "uv_unchanged=%d optical_detail_calibrated=NO "
                "source_RAW10_unchanged=YES\n",
                captured,b.sequence,ft.applied,ft.input_p01,
                ft.input_p50,ft.input_p99,
                ft.output_p01_estimate,ft.output_p50_estimate,
                ft.output_p99_estimate,ft.unchanged_chroma);
        }
        conversion+=wall_ms()-t;
        /* Release the physical buffer as soon as conversion ends. */
        if(xioctl(src,VIDIOC_QBUF,&b)) goto cleanup;
        t=wall_ms();
        if(ready(dst,POLLOUT,deadline)) goto cleanup;
        ssize_t n;
        do { n=write(dst,nv12,DST_BYTES); } while(n<0 && errno==EINTR && !stopping);
        if(n!=DST_BYTES) goto cleanup;
        publication+=wall_ms()-t;completed++;
    }
    if(!continuous && completed==requested && !stopping) rc=0;
cleanup:;
    bool stop_ok=!streaming;
    if(streaming) { stop_ok=xioctl(src,VIDIOC_STREAMOFF,&type)==0; if(!stop_ok) rc=1; }
    if(stopping && stop_ok) rc=143;
    for(unsigned i=0;i<count;i++) if(maps[i]) munmap(maps[i],lengths[i]);
    if(src>=0) close(src);
    if(dst>=0) close(dst);
    free(nv12);nv12=NULL;raw=NULL;
    fprintf(stderr,"E004KQ_LIFECYCLE captured=%ld published=%ld termination_requested=%d streamoff_completed=%d\n",captured,completed,(int)stopping,(int)stop_ok);
    fprintf(stderr,"{\"status\":\"%s\",\"frames\":%ld,\"requested\":%ld,\"continuous\":%s,"
        "\"source_sequence_first_last\":[%u,%u],\"source_sequence_gaps\":%lu,"
        "\"source_span_s\":%.6f,\"conversion_mean_ms\":%.3f,"
        "\"publication_mean_ms\":%.3f,\"elapsed_ms\":%.3f,"
        "\"raw_pipe_copy\":false,\"pixel_files_written\":false}\n",
        rc?(rc==143?"STOPPED":"FAIL"):"PASS",completed,continuous?0:requested,
        continuous?"true":"false",first_seq,last_seq,gaps,last_ts-first_ts,
        completed?conversion/completed:0,completed?publication/completed:0,wall_ms()-begin);
    return rc;
}

#ifndef E004KQ_NO_MAIN
int main(int argc,char **argv) { return front_publisher_main(argc,argv); }
#endif
