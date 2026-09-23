/* SPDX-License-Identifier: MIT
 * E004ke: PROPOSED IMX681 RDI RAW10 Bayer -> 1920x1080 NV12 proxy.
 * Does not decode the ISP QC10C stream or claim Windows colour parity.
 * A correct RAW10 RDI capture from this front sensor remains unproven.
 * Only stdin/stdout, no camera, boot, files or hardware registers.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdint.h>
#include "iq/nv12_range.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

enum {
    SRC_W=3840,SRC_H=2160,SRC_STRIDE=4800,
    SRC_BYTES=SRC_STRIDE*SRC_H,DST_W=1920,DST_H=1080,
    DST_Y=DST_W*DST_H,DST_BYTES=DST_Y*3/2
};
static unsigned char *raw,*nv12;
static int mipi_high_index[SRC_W];
static unsigned char clip(int x) { return (unsigned char)(x<0?0:x>255?255:x); }
/* Default release keeps its previous numeric output bit-for-bit;
 * only an isolated fresh guarded trial may explicitly request studio-range
 * encoding. No auto exposure or sensor/IR control is introduced here. */
static unsigned char sp11_rgb_output_y(int full) {
#if defined(SP11_RGB_NV12_VIDEO_RANGE) && SP11_RGB_NV12_VIDEO_RANGE
    return sp11_rgb_y_to_video(clip(full));
#else
    return clip(full);
#endif
}
static unsigned char sp11_rgb_output_uv(int full) {
#if defined(SP11_RGB_NV12_VIDEO_RANGE) && SP11_RGB_NV12_VIDEO_RANGE
    return sp11_rgb_uv_to_video(clip(full));
#else
    return clip(full);
#endif
}
static int read_exact(int fd,unsigned char *p,size_t n) {
    while(n) {
        ssize_t k=read(fd,p,n);
        if(k<0 && errno==EINTR) continue;
        if(k<=0) return -1;
        p+=(size_t)k;n-=(size_t)k;
    }
    return 0;
}
static int write_exact(int fd,const unsigned char *p,size_t n) {
    while(n) {
        ssize_t k=write(fd,p,n);
        if(k<0 && errno==EINTR) continue;
        if(k<=0) return -1;
        p+=(size_t)k;n-=(size_t)k;
    }
    return 0;
}
static double wall_ms(void) {
    struct timespec now;
    if(clock_gettime(CLOCK_MONOTONIC,&now)) return -1.;
    return (double)now.tv_sec*1000.+(double)now.tv_nsec/1e6;
}
/* RGGB Bayer 2x2 -> one RGB pixel, retains the right/front mosaic phase.
 * Averages the pair of green sites and discards two least-significant
 * RAW10 bits intentionally; full 10-bit/HDR/ISP processing NOT preserved.
 * Four of these 2x2 tiles -> one chroma pair in output NV12.
 */
static void convert(void) {
    unsigned char *y=nv12,*uv=nv12+DST_Y;
    for(int py=0;py<SRC_H;py+=2) {
        const unsigned char *top=raw+(size_t)py*SRC_STRIDE;
        const unsigned char *bottom=top+SRC_STRIDE;
        const int oy=py/2;
        const size_t yrow=(size_t)oy*DST_W;
        const size_t uvrow=(size_t)(oy/2)*DST_W;
        for(int px=0;px<SRC_W;px+=2) {
            const int ox=px/2;
            const int red=top[mipi_high_index[px]];
            const int green=(top[mipi_high_index[px+1]]+
                bottom[mipi_high_index[px]]+1)/2;
            const int blue=bottom[mipi_high_index[px+1]];
            y[yrow+ox]=sp11_rgb_output_y((77*red+150*green+29*blue+128)>>8);
            /* One fully populated UV pair after a 2x2 output tile. */
            if((oy&1)==0 && (ox&1)==0) {
                int reds=0,greens=0,blues=0;
                for(int dy=0;dy<2;dy++) {
                    const unsigned char *a=raw+(size_t)(py+2*dy)*SRC_STRIDE;
                    const unsigned char *b=a+SRC_STRIDE;
                    for(int dx=0;dx<2;dx++) {
                        const int x=px+2*dx;
                        reds+=a[mipi_high_index[x]];
                        greens+=(a[mipi_high_index[x+1]]+
                                 b[mipi_high_index[x]]+1)/2;
                        blues+=b[mipi_high_index[x+1]];
                    }
                }
                const int r=(reds+2)/4,g=(greens+2)/4,b=(blues+2)/4;
                uv[uvrow+ox]=sp11_rgb_output_uv(128+((-43*r-85*g+128*b+128)>>8));
                uv[uvrow+ox+1]=sp11_rgb_output_uv(128+((128*r-107*g-21*b+128)>>8));
            }
        }
    }
}
int main(int argc,char **argv) {
    if(argc!=3 || strcmp(argv[1],"--frames")) {
        fputs("E004KH_FRONT_RAW_USAGE --frames 1..2400\n",stderr);return 2;
    }
    char *end=NULL;errno=0;
    long n=strtol(argv[2],&end,10);
    if(errno || end==argv[2] || *end || n<1 || n>2400) {
        fputs("E004KH_FRONT_RAW_FRAME_BOUND_INVALID\n",stderr);return 2;
    }
    if(isatty(STDIN_FILENO)||isatty(STDOUT_FILENO)) {
        fputs("E004KH_REFUSE_TERMINAL_PIXEL_IO\n",stderr);return 2;
    }
    raw=malloc(SRC_BYTES);nv12=malloc(DST_BYTES);
    if(!raw||!nv12) {
        fputs("E004KH_ALLOCATE_FAIL\n",stderr);free(raw);free(nv12);return 1;
    }
    for(int x=0;x<SRC_W;x++)mipi_high_index[x]=(x/4)*5+x%4;
    double ms=0;int rc=1;
    for(long i=0;i<n;i++) {
        if(read_exact(STDIN_FILENO,raw,SRC_BYTES)) {
            fputs("E004KH_TRUNCATED_FRONT_RDI_RAW10_INPUT\n",stderr);goto done;
        }
        double a=wall_ms();
        convert();
        ms+=wall_ms()-a;
        if(write_exact(STDOUT_FILENO,nv12,DST_BYTES)) {
            fputs("E004KH_SHORT_NV12_OUTPUT\n",stderr);goto done;
        }
    }
    unsigned char extra;
    ssize_t k;
    do{k=read(STDIN_FILENO,&extra,1);}while(k<0&&errno==EINTR);
    if(k!=0){
        fputs("E004KH_EXTRA_RAW_INPUT_OR_READ_ERROR\n",stderr);goto done;
    }
    fprintf(stderr,"E004KH_FRONT_RDI_BAYER_TO_NV12=PASS "
        "SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 "
        "FRAMES=%ld SRC_BYTES_PER_FRAME=%d DEST_BYTES_PER_FRAME=%d "
        "AVERAGE_CONVERSION_ONLY_MS=%.3f REAL_SENSOR_PROVEN_BY_CALLER=NO "
        "QC10C_DECODED=NO OEM_ISP_PARITY=NO PIXELS_SAVED=NO\n",
        n,SRC_BYTES,DST_BYTES,ms/n);
    rc=0;
done:
    free(raw);free(nv12);raw=NULL;nv12=NULL;
    return rc;
}
