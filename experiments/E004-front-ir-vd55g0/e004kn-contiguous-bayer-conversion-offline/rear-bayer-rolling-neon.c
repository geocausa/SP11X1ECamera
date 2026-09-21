/* SPDX-License-Identifier: MIT
 * E004kn: contiguous upper-eight-bit layout, single-worker bounded 1MiB IPC, OFFLINE optical OV13858 pgAA to 3840x2160 NV12.
 * Geometry-only 4K delivery feasibility. NOT a calibrated ISP or a live driver.
 * Does not open cameras, write files, load modules, or touch boot/IR.
 */
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <arm_neon.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

enum {
    SRC_W=4076, SRC_H=2806, SRC_STRIDE=5104,
    DST_W=3840, DST_H=2160, SRC_BYTES=SRC_STRIDE*SRC_H,
    DST_Y=DST_W*DST_H, DST_BYTES=DST_Y*3/2,
    CROP_X=118, CROP_Y=322
};
/* Both offsets are even to preserve the sensor's GRBG parity. The target
 * lies strictly inside the source, including one-pixel interpolation halo.
 * pgAA: four MIPI RAW10 pixels packed in five bytes. First four bytes
 * contain each pixel's upper eight bits; fifth contains four 2-bit LSBs.
 * This experimental 8-bit transform intentionally discards 2 LSBs. */
static const unsigned char *frame;
static unsigned char *unpacked;
static unsigned char *nv12;

/* E004kd: fuse the 2x2 output tile. Each MIPI RAW10 upper-eight
 * value is loaded at most once per row/tile instead of recomputing
 * overlapping bilinear neighbourhoods for four individual pixels.
 * Preserve E004jl's exact crop, rounding, YUV matrix and 8-bit output.
 * Even crop origins are mandatory for the GRBG parity assumptions.
 */
/* Unpack upper eight bits only, identical to the accepted RAW10 proxy.
 * Contiguous neighbours remove indirect loads from the bilinear loop.
 * No change to crop, matrix, interpolation, rounding or frame bounds. */
static void unpack_row(int y) {
    {
        const unsigned char * restrict src=frame+(size_t)y*SRC_STRIDE;
        unsigned char * restrict dst=unpacked+(size_t)(y%4)*SRC_W;
        for (int x=0;x<SRC_W;x+=4) {
            int i=(x/4)*5;
            dst[x]=src[i]; dst[x+1]=src[i+1];
            dst[x+2]=src[i+2]; dst[x+3]=src[i+3];
        }
    }
}
static uint16x8_t u8(const unsigned char *p, int odd) {
    return vmovl_u8(vld2_u8(p).val[odd]);
}
static uint16x8_t a2(uint16x8_t a,uint16x8_t b) {
    return vrhaddq_u16(a,b);
}
static uint16x8_t a4(uint16x8_t a,uint16x8_t b,uint16x8_t c,uint16x8_t d) {
    return vshrq_n_u16(vaddq_u16(vaddq_u16(a,b),vaddq_u16(vaddq_u16(c,d),vdupq_n_u16(2))),2);
}
static uint8x8_t y8(uint16x8_t r,uint16x8_t g,uint16x8_t b) {
    uint16x8_t y=vmlaq_n_u16(vmlaq_n_u16(vmulq_n_u16(r,77),g,150),b,29);
    return vshrn_n_u16(vaddq_u16(y,vdupq_n_u16(128)),8);
}
static int16x4_t c4(int16x4_t r,int16x4_t g,int16x4_t b,int16_t cr,int16_t cg,int16_t cb) {
    int32x4_t c=vmlal_n_s16(vmlal_n_s16(vmull_n_s16(r,cr),g,cg),b,cb);
    c=vaddq_s32(vshrq_n_s32(vaddq_s32(c,vdupq_n_s32(128)),8),vdupq_n_s32(128));
    return vqmovn_s32(c);
}
static uint8x8_t c8(uint16x8_t rr,uint16x8_t gg,uint16x8_t bb,int16_t cr,int16_t cg,int16_t cb) {
    int16x8_t r=vreinterpretq_s16_u16(rr),g=vreinterpretq_s16_u16(gg),b=vreinterpretq_s16_u16(bb);
    return vqmovun_s16(vcombine_s16(
        c4(vget_low_s16(r),vget_low_s16(g),vget_low_s16(b),cr,cg,cb),
        c4(vget_high_s16(r),vget_high_s16(g),vget_high_s16(b),cr,cg,cb)));
}
static void convert(void) {
    unpack_row(CROP_Y-1); unpack_row(CROP_Y);
    for(int oy=0;oy<DST_H;oy+=2) {
        int sy=CROP_Y+oy;
        unpack_row(sy+1); unpack_row(sy+2);
        const unsigned char *m=unpacked+(size_t)((sy-1)%4)*SRC_W;
        const unsigned char *e=unpacked+(size_t)(sy%4)*SRC_W;
        const unsigned char *p=unpacked+(size_t)((sy+1)%4)*SRC_W;
        const unsigned char *q=unpacked+(size_t)((sy+2)%4)*SRC_W;
        unsigned char *y0=nv12+(size_t)oy*DST_W,*y1=y0+DST_W;
        unsigned char *uv=nv12+DST_Y+(size_t)(oy/2)*DST_W;
        for(int ox=0;ox<DST_W;ox+=16) {
            int x=CROP_X+ox;
            uint16x8_t m0=u8(m+x,0),m1=u8(m+x,1),m2=u8(m+x+2,0);
            uint16x8_t em=u8(e+x-1,0),e0=u8(e+x,0),e1=u8(e+x,1),e2=u8(e+x+2,0);
            uint16x8_t pm=u8(p+x-1,0),p0=u8(p+x,0),p1=u8(p+x,1),p2=u8(p+x+2,0);
            uint16x8_t qm=u8(q+x-1,0),q0=u8(q+x,0),q1=u8(q+x,1);
            uint16x8_t r00=a2(em,e1),g00=e0,b00=a2(m0,p0);
            uint16x8_t r01=e1,g01=a4(e0,e2,m1,p1),b01=a4(m0,m2,p0,p2);
            uint16x8_t r10=a4(em,e1,qm,q1),g10=a4(pm,p1,e0,q0),b10=p0;
            uint16x8_t r11=a2(e1,q1),g11=p1,b11=a2(p0,p2);
            uint8x8x2_t yy0={{y8(r00,g00,b00),y8(r01,g01,b01)}};
            uint8x8x2_t yy1={{y8(r10,g10,b10),y8(r11,g11,b11)}};
            vst2_u8(y0+ox,yy0);vst2_u8(y1+ox,yy1);
            uint16x8_t rr=a4(r00,r01,r10,r11),gg=a4(g00,g01,g10,g11),bb=a4(b00,b01,b10,b11);
            uint8x8x2_t cc={{c8(rr,gg,bb,-43,-85,128),c8(rr,gg,bb,128,-107,-21)}};
            vst2_u8(uv+ox,cc);
        }
    }
}
static int read_all(int fd,unsigned char *p,size_t n) {
    while(n) {
        ssize_t v=read(fd,p,n);
        if(v<0 && errno==EINTR) continue;
        if(v<=0) return -1;
        p+=(size_t)v;n-=(size_t)v;
    }
    return 0;
}
static int write_all(int fd,const unsigned char *p,size_t n) {
    while(n) {
        ssize_t v=write(fd,p,n);
        if(v<0 && errno==EINTR) continue;
        if(v<=0) return -1;
        p+=(size_t)v;n-=(size_t)v;
    }
    return 0;
}
static double ms(void) {
    struct timespec ts;
    if(clock_gettime(CLOCK_MONOTONIC,&ts)) return -1.0;
    return 1000.0*ts.tv_sec+ts.tv_nsec/1000000.0;
}
int main(int argc,char **argv) {
    if(argc!=3 || strcmp(argv[1],"--frames")) {
        fputs("E004KD_USAGE: --frames 1..240\n",stderr);return 2;
    }
    char *end=NULL;
    errno=0;
    long n=strtol(argv[2],&end,10);
    if(errno || end==argv[2] || *end || n<1 || n>240) {
        fputs("E004JL_INVALID_FRAME_BOUND\n",stderr);return 2;
    }
    if(isatty(STDIN_FILENO) || isatty(STDOUT_FILENO)) {
        fputs("E004JL_REFUSE_TERMINAL_PIXEL_IO\n",stderr);return 2;
    }
    if(CROP_X<1 || CROP_Y<1 || CROP_X+DST_W>=SRC_W ||
       CROP_Y+DST_H>=SRC_H || (CROP_X&1) || (CROP_Y&1) ||
       (DST_W&1) || (DST_H&1)) {
        fputs("E004JL_UNSAFE_CROP\n",stderr);return 1;
    }
    unsigned char *in=malloc(SRC_BYTES);
    nv12=malloc(DST_BYTES);
    unpacked=malloc((size_t)SRC_W*4);
    if(!in || !nv12 || !unpacked) {
        fputs("E004JL_ALLOCATION_FAILURE\n",stderr);
        free(in);free(nv12);free(unpacked);return 1;
    }
    /* At most 1 MiB per anonymous pipe, less than one source/output frame.
     * This adjusts IPC batching only; the single-frame pixel algorithm is unchanged.
     * Refused pipe growth is reported and the existing bounded pipe remains usable.
     */
    int pipe_bytes[2]={-1,-1};
    for (int fd=0;fd<2;fd++) {
        struct stat st;
        if (!fstat(fd,&st) && S_ISFIFO(st.st_mode)) {
            (void)fcntl(fd,F_SETPIPE_SZ,1048576);
            pipe_bytes[fd]=fcntl(fd,F_GETPIPE_SZ);
        }
    }
    int rc=1;
    double total=0.0, input_ms=0.0, output_ms=0.0;
    double begin=ms();
    for(long i=0;i<n;i++) {
        double input_begin=ms();
        if(read_all(STDIN_FILENO,in,SRC_BYTES)) {
            fputs("E004JL_TRUNCATED_REAR_RAW10_INPUT\n",stderr);goto finish;
        }
        input_ms+=ms()-input_begin;
        frame=in;
        double start=ms();
        convert();
        total+=ms()-start;
        double output_begin=ms();
        if(write_all(STDOUT_FILENO,nv12,DST_BYTES)) {
            fputs("E004JL_SHORT_NV12_OUTPUT\n",stderr);goto finish;
        }
        output_ms+=ms()-output_begin;
    }
    double elapsed=ms()-begin;
    unsigned char extra;
    ssize_t x;
    do { x=read(STDIN_FILENO,&extra,1); } while(x<0 && errno==EINTR);
    if(x!=0) {
        fputs("E004JL_EXTRA_INPUT_OR_READ_ERROR\n",stderr);goto finish;
    }
    fprintf(stderr,"E004KN_ROLLING_NEON_4K=PASS SOURCE=pgAA_4076x2806 "
        "OUTPUT=NV12_3840x2160 FRAMES=%ld BYTES_PER_FRAME=%d "
        "AVERAGE_CONVERSION_MS=%.3f AVERAGE_INPUT_WAIT_MS=%.3f AVERAGE_OUTPUT_WAIT_MS=%.3f ELAPSED_MS=%.3f WORKER_LIMIT=1 INPUT_PIPE_BYTES=%d OUTPUT_PIPE_BYTES=%d CALIBRATED=NO "
        "PROVENANCE_VERIFIED_BY_CALLER=NO WINDOWS_QUALITY_PARITY=NO\n",
        n,DST_BYTES,total/n,input_ms/n,output_ms/n,elapsed,pipe_bytes[0],pipe_bytes[1]);
    rc=0;
finish:
    free(in);free(nv12);free(unpacked);
    frame=NULL;nv12=NULL;
    return rc;
}
