/* SPDX-License-Identifier: MIT
 * CAMERA-FREE: synthetic bounded uniform Bayer RAW10 pattern for ALL
 * possible 2x2 mosaic orders. Invoke the REAL current rear converter
 * and inspect only a single SYNTHETIC RGB reconstruction as scalars.
 * NO V4L2 open, firmware, private optical data, files, RAW exports,
 * image pixels or source captures from actual users/cameras.
 */
#define SP11_RGB_NV12_VIDEO_RANGE 1
#define SP11_RGB_REAR_BGGR_OPTIN 1
#define main sp11_offline_converter_unused_main
#include "rear-convert.c"
#undef main
#include <assert.h>
enum {GRBG=0, BGGR=1, GBRG=2, RGGB=3};
static int raw_from_pattern(int phase,int y,int x,int r,int g,int b) {
    /* 2x2 sites in row-major order. */
    static const int mapping[4][4]={
        {1,0,2,1}, /* GRBG:  G,R / B,G, source metadata currently declares */
        {2,1,1,0}, /* BGGR:  B,G / G,R */
        {1,2,0,1}, /* GBRG:  G,B / R,G */
        {0,1,1,2}, /* RGGB:  R,G / G,B */
    };
    const int color[3]={r,g,b};
    return color[mapping[phase][((y&1)<<1)|(x&1)]];
}
static void fill_synthetic_mipi_raw10(int phase,int r,int g,int b) {
    /* No real image: repeated constant pixel mosaics; fifth RAW10
       byte low bits are intentionally zero. Source 5104-byte stride. */
    for (int y=0;y<SRC_H;y++) {
        uint8_t *row=(uint8_t*)frame+(size_t)y*SRC_STRIDE;
        for(int x=0;x<SRC_W;x+=4) {
            int byte=(x/4)*5;
            for(int i=0;i<4;i++)
                row[byte+i]=(uint8_t)raw_from_pattern(phase,y,x+i,r,g,b);
            row[byte+4]=0;
        }
    }
}
static int clip_byte(int v){return v<0?0:v>255?255:v;}
static void center_decoded(int result[3]) {
    const int x=96,y=96;
    const int yy=nv12[(size_t)y*DST_W+x];
    const int uv_base=(int)DST_Y+(y/2)*DST_W+(x&~1);
    const int u=nv12[uv_base],v=nv12[uv_base+1];
    const int c=yy-16,d=u-128,e=v-128;
    result[0]=clip_byte((298*c+409*e+128)>>8);
    result[1]=clip_byte((298*c-100*d-208*e+128)>>8);
    result[2]=clip_byte((298*c+516*d+128)>>8);
}
static int close_triplet(const int a[3],const int b[3],int tol) {
    for(int i=0;i<3;i++)if(abs(a[i]-b[i])>tol)return 0;
    return 1;
}
int main(void) {
    /* Match exact maintained 4K conversion source implementation. */
    unsigned char *source=malloc(SRC_BYTES);
    unsigned char *out=malloc(DST_BYTES);
    assert(source&&out);
    frame=source;nv12=out;plan_offsets();
    const int cyan[3]={2,200,245};
    int expected[3]={0,0,0},wrong[3]={0,0,0};
    for(int phase=GRBG;phase<=RGGB;phase++) {
        fill_synthetic_mipi_raw10(phase,cyan[0],cyan[1],cyan[2]);
        convert();
        int actual[3];
        center_decoded(actual);
        if(phase==BGGR) {
            /* Proposed BGGR opt-in must reconstruct known synthetic
             * cyan, not just randomly rebalance user-camera photo. */
            assert(close_triplet(actual,cyan,8));
            memcpy(expected,actual,sizeof expected);
        }
        if(phase==GRBG) {
            assert(!close_triplet(actual,cyan,20));
            memcpy(wrong,actual,sizeof wrong);
        }
        printf("SYNTHETIC_ONLY_CYAN_SOURCE_HYPOTHESIS phase=%s renderer_RGB=%d,%d,%d\n",
            (const char*[]){"GRBG","BGGR","GBRG","RGGB"}[phase],
            actual[0],actual[1],actual[2]);
    }
    /* Red and blue ONLY synthetic proper GRBG need no white balance. */
    for(int color=0;color<3;color++) {
        const int source_rgb[3][3]={{210,3,4},{3,210,4},{3,4,210}};
        fill_synthetic_mipi_raw10(BGGR,source_rgb[color][0],
            source_rgb[color][1],source_rgb[color][2]);
        convert();
        int v[3];center_decoded(v);
        assert(close_triplet(v,source_rgb[color],8));
        printf("SYNTHETIC_ONLY_CORRECT_BGGR_PRIMARY_%s_ROUNDTRIP_RGB=%d,%d,%d\n",
             (const char*[]){"RED","GREEN","BLUE"}[color],v[0],v[1],v[2]);
    }
    assert(expected[1]>expected[0]+100 && expected[2]>expected[0]+100);
    assert(!close_triplet(wrong,cyan,20));
    free(source);free(out);
    puts("E004NH_OPTIN_BGGR_REAR_REAL_4K_BAYER_CONVERTER_SYNTHETIC_CYAN_PRIMARY_AND_MISMATCHED_GRBG_NEGATIVE=PASS_NO_CAMERAS_NO_OPTICAL_EXPORT");
    return 0;
}
