/* SPDX-License-Identifier: MIT
 * E004iu: OFFLINE SP11 OV13858 SGRBG10P ("pgAA") rear preview to NV12.
 *
 * This is a fast nearest-tile RGB proxy, NOT calibrated demosaic,
 * production IQ, sensor access, V4L2 producer, or a live webcam.
 * Fixed width/stride and a private offline input/output file contract.
 * No camera, media, DRM, IR, PMIC, GRUB or hardware APIs are used.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

enum { IN_W=4076, IN_H=2806, IN_STRIDE=5104,
       OUT_W=1920, OUT_H=1080, IN_SIZE=IN_H*IN_STRIDE,
       OUT_SIZE=OUT_W*OUT_H*3/2, OUT_Y=OUT_W*OUT_H };
static unsigned char *input, *output;
static int src_row[OUT_H], src_off[OUT_W];

static int clamp8(int value) {
    return value < 0 ? 0 : value > 255 ? 255 : value;
}
static void pixel(int yy, int xx, int *red, int *green, int *blue) {
    const size_t index=(size_t)src_row[yy]*IN_STRIDE+(size_t)src_off[xx];
    const int g0=input[index], r=input[index+1];
    const int b=input[index+IN_STRIDE], g1=input[index+IN_STRIDE+1];
    *red=r;
    *green=(g0+g1+1)>>1;
    *blue=b;
}
static int plan(void) {
    const double tile_w=IN_W/2.0, tile_h=IN_H/2.0;
    const double crop_h=tile_w*(double)OUT_H/(double)OUT_W;
    for (int y=0;y<OUT_H;y++) {
        int tile=(int)floor((tile_h-crop_h)/2.0+
               ((double)y+0.5)*crop_h/(double)OUT_H);
        if (tile<0 || tile>=IN_H/2) return -1;
        src_row[y]=tile*2;
    }
    for (int x=0;x<OUT_W;x++) {
        int tile=(int)floor(((double)x+0.5)*tile_w/(double)OUT_W);
        if (tile<0 || tile>=IN_W/2) return -1;
        src_off[x]=(tile/2)*5+(tile%2)*2;
        if (src_off[x]+1 >= IN_W*5/4) return -1;
    }
    return 0;
}
static void convert_frame(void) {
    unsigned char *yplane=output, *uvplane=output+OUT_Y;
    for (int y=0;y<OUT_H;y+=2) {
        for (int x=0;x<OUT_W;x+=2) {
            int sum_r=0,sum_g=0,sum_b=0;
            for (int dy=0;dy<2;dy++) {
                for (int dx=0;dx<2;dx++) {
                    int red,green,blue;
                    pixel(y+dy,x+dx,&red,&green,&blue);
                    /* Full-range, integer BT.601-like approximation. */
                    int luma=(77*red+150*green+29*blue+128)>>8;
                    yplane[(size_t)(y+dy)*OUT_W+x+dx]=(unsigned char)clamp8(luma);
                    sum_r+=red;sum_g+=green;sum_b+=blue;
                }
            }
            /* Average the four source RGB pixels before chroma matrix. */
            int r=(sum_r+2)>>2, g=(sum_g+2)>>2, b=(sum_b+2)>>2;
            int u=128+((-43*r-85*g+128*b+128)>>8);
            int v=128+((128*r-107*g-21*b+128)>>8);
            const size_t uv=(size_t)(y/2)*OUT_W+x;
            uvplane[uv]=(unsigned char)clamp8(u);
            uvplane[uv+1]=(unsigned char)clamp8(v);
        }
    }
}
static double monotonic_ms(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC,&t)) return -1;
    return (double)t.tv_sec*1000.0+(double)t.tv_nsec/1000000.0;
}
static int read_exact(int fd, unsigned char *dst, size_t len) {
    while (len) {
        ssize_t n=read(fd,dst,len);
        if (n<0 && errno==EINTR) continue;
        if (n<=0) return -1;
        dst+=(size_t)n;len-=(size_t)n;
    }
    return 0;
}
static int write_entire(int fd, const unsigned char *src, size_t len) {
    while (len) {
        ssize_t n=write(fd,src,len);
        if (n<0 && errno==EINTR) continue;
        if (n<=0) return -1;
        src+=(size_t)n;len-=(size_t)n;
    }
    return 0;
}
static int open_private_input(const char *path, int frames) {
    struct stat st;
    if (lstat(path,&st) || !S_ISREG(st.st_mode) || st.st_size!=(off_t)IN_SIZE*frames) return -1;
    int fd=open(path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW|O_NONBLOCK);
    if (fd<0) return -1;
    if (fstat(fd,&st) || !S_ISREG(st.st_mode) || st.st_size!=(off_t)IN_SIZE*frames) {
        close(fd);return -1;
    }
    return fd;
}
int main(int argc, char **argv) {
    int rc=1,fd=-1,outfd=-1,frames=1;
    bool created=false;
    const char *path=NULL,*dest=NULL;
    if ((argc!=5 && argc!=7) || strcmp(argv[1],"--input") || strcmp(argv[3],"--output")) {
        fputs("Usage: rear_fast --input FILE --output NEW_PRIVATE_FILE [--frames 1..27]\n",stderr);
        return 2;
    }
    if (argc==7) {
        char *end=NULL;
        long n;
        if (strcmp(argv[5],"--frames")) return 2;
        errno=0;n=strtol(argv[6],&end,10);
        if (errno || end==argv[6] || *end || n<1 || n>27) {
            fputs("E004IU_FRAME_COUNT_MUST_BE_1_TO_27\n",stderr);return 2;
        }
        frames=(int)n;
    }
    path=argv[2];dest=argv[4];
    fd=open_private_input(path,frames);
    if (fd<0) { fputs("E004IU_INPUT_INVALID_OR_NOT_FULL_REAR_FRAME\n",stderr);return 2; }
    input=malloc(IN_SIZE);output=malloc(OUT_SIZE);
    if (!input || !output || plan()) {
        fputs("E004IU_FRAME_MEMORY_OR_READ_FAILURE\n",stderr);goto cleanup;
    }
    /* Only an ordinary, new file inside an existing private /tmp dir.
     * Python front-end is responsible for parent ownership and confinement;
     * this offline executable additionally refuses links and replacement.
     */
    outfd=open(dest,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
    if (outfd<0) { fputs("E004IU_OUTPUT_ALREADY_EXISTS_OR_UNAVAILABLE\n",stderr);goto cleanup; }
    created=true;
    double started=monotonic_ms(),conversion_ms=0.0;
    for (int i=0;i<frames;i++) {
        if (read_exact(fd,input,IN_SIZE)) {
            fputs("E004IU_INPUT_READ_FAILURE\n",stderr);goto cleanup;
        }
        double t0=monotonic_ms();
        convert_frame();
        conversion_ms+=monotonic_ms()-t0;
        if (write_entire(outfd,output,OUT_SIZE)) {
            fputs("E004IU_OUTPUT_WRITE_FAILURE\n",stderr);goto cleanup;
        }
    }
    unsigned char extra;
    if (read(fd,&extra,1)!=0 || fsync(outfd)) {
        fputs("E004IU_INPUT_EXTRA_BYTES_OR_OUTPUT_SYNC_FAILURE\n",stderr);goto cleanup;
    }
    double total_ms=monotonic_ms()-started;
    if (close(outfd)) { outfd=-1;goto cleanup; }
    outfd=-1;
    printf("E004IU_OFFLINE_REAR_NV12_BYTES=%d FRAMES=%d CONVERSION_MS=%.4f "
           "AVG_CONVERSION_MS=%.4f BATCH_IO_AND_CONVERSION_MS=%.4f "
           "SOURCE=pgAA_4076x2806 OUTPUT=NV12_1920x1080 "
           "COLOUR_CALIBRATED=NO LIVE_CAMERA=NO\n",
           OUT_SIZE*frames,frames,conversion_ms,conversion_ms/frames,total_ms);
    rc=0;
cleanup:
    if (fd>=0) close(fd);
    if (outfd>=0) close(outfd);
    if (rc && created) unlink(dest);
    free(input);free(output);
    return rc;
}
