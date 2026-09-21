/* SPDX-License-Identifier: MIT
 * E004kd: bounded, OFFLINE optical OV13858 pgAA to 3840x2160 NV12.
 * Geometry-only 4K delivery feasibility. NOT a calibrated ISP or a live driver.
 * Does not open cameras, write files, load modules, or touch boot/IR.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

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
static unsigned char *nv12;

/* E004kd: fuse the 2x2 output tile. Each MIPI RAW10 upper-eight
 * value is loaded at most once per row/tile instead of recomputing
 * overlapping bilinear neighbourhoods for four individual pixels.
 * Preserve E004jl's exact crop, rounding, YUV matrix and 8-bit output.
 * Even crop origins are mandatory for the GRBG parity assumptions.
 */
static unsigned char clip(int v);
static int byte_offset[SRC_W];
static void plan_offsets(void) {
    for (int x=0;x<SRC_W;x++)
        byte_offset[x]=(x/4)*5+(x%4);
}
static int avg2(int a,int b) { return (a+b+1)/2; }
static int avg4(int a,int b,int c,int d) { return (a+b+c+d+2)/4; }
static void convert(void) {
    unsigned char *yp=nv12,*uv=nv12+DST_Y;
    for(int oy=0;oy<DST_H;oy+=2) {
        const int sy=CROP_Y+oy;
        const unsigned char *m=frame+(size_t)(sy-1)*SRC_STRIDE;
        const unsigned char *e=frame+(size_t)sy*SRC_STRIDE;
        const unsigned char *p=frame+(size_t)(sy+1)*SRC_STRIDE;
        const unsigned char *q=frame+(size_t)(sy+2)*SRC_STRIDE;
        unsigned char *y0=yp+(size_t)oy*DST_W;
        unsigned char *y1=y0+DST_W;
        unsigned char *uvrow=uv+(size_t)(oy/2)*DST_W;
        for(int ox=0;ox<DST_W;ox+=2) {
            const int sx=CROP_X+ox;
            const int im=byte_offset[sx-1], i0=byte_offset[sx];
            const int i1=byte_offset[sx+1], i2=byte_offset[sx+2];
            const int m0=m[i0], m1=m[i1], m2=m[i2];
            const int em=e[im], e0=e[i0], e1=e[i1], e2=e[i2];
            const int pm=p[im], p0=p[i0], p1=p[i1], p2=p[i2];
            const int qm=q[im], q0=q[i0], q1=q[i1];
            /* G at even/even, R at even/odd, B at odd/even,
             * G at odd/odd; same four bilinear RGB values as E004jl. */
            const int r00=avg2(em,e1), g00=e0, b00=avg2(m0,p0);
            const int r01=e1, g01=avg4(e0,e2,m1,p1);
            const int b01=avg4(m0,m2,p0,p2);
            const int r10=avg4(em,e1,qm,q1);
            const int g10=avg4(pm,p1,e0,q0), b10=p0;
            const int r11=avg2(e1,q1), g11=p1, b11=avg2(p0,p2);
            y0[ox]=clip((77*r00+150*g00+29*b00+128)>>8);
            y0[ox+1]=clip((77*r01+150*g01+29*b01+128)>>8);
            y1[ox]=clip((77*r10+150*g10+29*b10+128)>>8);
            y1[ox+1]=clip((77*r11+150*g11+29*b11+128)>>8);
            const int rr=(r00+r01+r10+r11+2)/4;
            const int gg=(g00+g01+g10+g11+2)/4;
            const int bb=(b00+b01+b10+b11+2)/4;
            uvrow[ox]=clip(128+((-43*rr-85*gg+128*bb+128)>>8));
            uvrow[ox+1]=clip(128+((128*rr-107*gg-21*bb+128)>>8));
        }
    }
}
static unsigned char clip(int v) { return (unsigned char)(v<0?0:v>255?255:v); }
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
    if(!in || !nv12) {
        fputs("E004JL_ALLOCATION_FAILURE\n",stderr);
        free(in);free(nv12);return 1;
    }
    plan_offsets();
    int rc=1;
    double total=0.0;
    for(long i=0;i<n;i++) {
        if(read_all(STDIN_FILENO,in,SRC_BYTES)) {
            fputs("E004JL_TRUNCATED_REAR_RAW10_INPUT\n",stderr);goto finish;
        }
        frame=in;
        double start=ms();
        convert();
        total+=ms()-start;
        if(write_all(STDOUT_FILENO,nv12,DST_BYTES)) {
            fputs("E004JL_SHORT_NV12_OUTPUT\n",stderr);goto finish;
        }
    }
    unsigned char extra;
    ssize_t x;
    do { x=read(STDIN_FILENO,&extra,1); } while(x<0 && errno==EINTR);
    if(x!=0) {
        fputs("E004JL_EXTRA_INPUT_OR_READ_ERROR\n",stderr);goto finish;
    }
    fprintf(stderr,"E004KD_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 "
        "OUTPUT=NV12_3840x2160 FRAMES=%ld BYTES_PER_FRAME=%d "
        "AVERAGE_CONVERSION_MS=%.3f CALIBRATED=NO "
        "PROVENANCE_VERIFIED_BY_CALLER=NO WINDOWS_QUALITY_PARITY=NO\n",
        n,DST_BYTES,total/n);
    rc=0;
finish:
    free(in);free(nv12);
    frame=NULL;nv12=NULL;
    return rc;
}
