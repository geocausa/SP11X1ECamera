/* SPDX-License-Identifier: MIT
 * E004jl: bounded, OFFLINE optical OV13858 pgAA to 3840x2160 NV12.
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

static int sample8(int y, int x) {
    return frame[(size_t)y*SRC_STRIDE+(size_t)(x/4)*5+(size_t)(x%4)];
}
static int avg2(int a,int b) { return (a+b+1)/2; }
static int avg4(int a,int b,int c,int d) { return (a+b+c+d+2)/4; }
static void rgb(int y,int x,int *r,int *g,int *b) {
    const int v=sample8(y,x);
    if (!(y&1) && (x&1)) { /* red */
        *r=v;
        *g=avg4(sample8(y,x-1),sample8(y,x+1),
                sample8(y-1,x),sample8(y+1,x));
        *b=avg4(sample8(y-1,x-1),sample8(y-1,x+1),
                sample8(y+1,x-1),sample8(y+1,x+1));
    } else if ((y&1) && !(x&1)) { /* blue */
        *b=v;
        *g=avg4(sample8(y,x-1),sample8(y,x+1),
                sample8(y-1,x),sample8(y+1,x));
        *r=avg4(sample8(y-1,x-1),sample8(y-1,x+1),
                sample8(y+1,x-1),sample8(y+1,x+1));
    } else if (!(y&1)) { /* green on red row */
        *g=v;
        *r=avg2(sample8(y,x-1),sample8(y,x+1));
        *b=avg2(sample8(y-1,x),sample8(y+1,x));
    } else { /* green on blue row */
        *g=v;
        *r=avg2(sample8(y-1,x),sample8(y+1,x));
        *b=avg2(sample8(y,x-1),sample8(y,x+1));
    }
}
static unsigned char clip(int v) { return (unsigned char)(v<0?0:v>255?255:v); }
static void convert(void) {
    unsigned char *yp=nv12,*uv=nv12+DST_Y;
    for(int oy=0;oy<DST_H;oy+=2) {
        for(int ox=0;ox<DST_W;ox+=2) {
            int sr=0,sg=0,sb=0;
            for(int dy=0;dy<2;dy++) {
                for(int dx=0;dx<2;dx++) {
                    int r,g,b;
                    rgb(CROP_Y+oy+dy,CROP_X+ox+dx,&r,&g,&b);
                    yp[(size_t)(oy+dy)*DST_W+(size_t)ox+dx]=
                        clip((77*r+150*g+29*b+128)>>8);
                    sr+=r;sg+=g;sb+=b;
                }
            }
            int r=(sr+2)/4,g=(sg+2)/4,b=(sb+2)/4;
            size_t uvpos=(size_t)(oy/2)*DST_W+ox;
            uv[uvpos]=clip(128+((-43*r-85*g+128*b+128)>>8));
            uv[uvpos+1]=clip(128+((128*r-107*g-21*b+128)>>8));
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
        fputs("E004JL_USAGE: --frames 1..8\n",stderr);return 2;
    }
    char *end=NULL;
    errno=0;
    long n=strtol(argv[2],&end,10);
    if(errno || end==argv[2] || *end || n<1 || n>8) {
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
    fprintf(stderr,"E004JL_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 "
        "OUTPUT=NV12_3840x2160 FRAMES=%ld BYTES_PER_FRAME=%d "
        "AVERAGE_CONVERSION_MS=%.3f CALIBRATED=NO "
        "LIVE_4K_CAPTURE=NO WINDOWS_QUALITY_PARITY=NO\n",
        n,DST_BYTES,total/n);
    rc=0;
finish:
    free(in);free(nv12);
    frame=NULL;nv12=NULL;
    return rc;
}
