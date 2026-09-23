/* SP11 synthetic ONLY, no camera/file/photo: differential exact-pixel
 * oracle for default scalar 2x2 versus opt-in AArch64 NEON.
 * Test 12.44 MB entire NV12 output + 8.29 MB history + all stats,
 * across stationary noise, two different moving contrast edges,
 * low contrast motion, scene cut, dropped sequence and tone-off reset.
 */
#define SP11_REAR_TEMPORAL_ENABLE_NEON 0
#define sp11_rear_temporal_state scalar_state
#define sp11_rear_temporal_stats scalar_stats
#define sp11_rear_temporal_init scalar_init
#define sp11_rear_temporal_reset scalar_reset
#define sp11_rear_temporal_nv12 scalar_filter
#include "../rear_temporal_preview.h"
#undef SP11_REAR_TEMPORAL_ENABLE_NEON
#undef sp11_rear_temporal_state
#undef sp11_rear_temporal_stats
#undef sp11_rear_temporal_init
#undef sp11_rear_temporal_reset
#undef sp11_rear_temporal_nv12
#undef SP11_REAR_TEMPORAL_PREVIEW_H
#define SP11_REAR_TEMPORAL_ENABLE_NEON 1
#define sp11_rear_temporal_state neon_state
#define sp11_rear_temporal_stats neon_stats
#define sp11_rear_temporal_init neon_init
#define sp11_rear_temporal_reset neon_reset
#define sp11_rear_temporal_nv12 neon_filter
#include "../rear_temporal_preview.h"
#undef sp11_rear_temporal_state
#undef sp11_rear_temporal_stats
#undef sp11_rear_temporal_init
#undef sp11_rear_temporal_reset
#undef sp11_rear_temporal_nv12
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { WIDTH=SP11_REAR_PREVIEW_W,HEIGHT=SP11_REAR_PREVIEW_H,
       Y_BYTES=SP11_REAR_PREVIEW_Y };
#define NV12_BYTES (Y_BYTES*3u/2u)
static uint8_t *a,*b,*hist_a,*hist_b;
static struct scalar_state sa;
static struct neon_state sn;
static struct scalar_stats ma;
static struct neon_stats mn;
static void fill(int frame) {
    const uint32_t SEED=0x19a12c57u;
    for(size_t i=0;i<Y_BYTES;i++) {
        const int x=(int)(i%WIDTH),y=(int)(i/WIDTH);
        uint32_t v=(uint32_t)i*1664525u+SEED;
        v^=v>>15u;
        unsigned luma=(unsigned)(122u+((v>>27u)%11u));
        /* Standstill and moving scene, plus low-contrast blurred
         * movement to verify identical limitations in both paths. */
        if(frame==1||frame==2||frame==3) {
            luma=123u+(unsigned)((v+frame)%6u);
            if(frame>=2 && x>=608+frame*4 && x<752+frame*4 &&
               y>=302 && y<480)luma=187u;
        } else if(frame==4) {
            luma=178u+(unsigned)((v>>29u)%3u);
        } else if(frame==5||frame==6) {
            luma=126u+(unsigned)((v+frame)%6u);
            if(x>=400+frame*2 && x<590+frame*2 &&
               y>=610 && y<840)luma=133u;
        }
        a[i]=(uint8_t)luma;
    }
    for(size_t i=Y_BYTES;i<NV12_BYTES;i++)a[i]=(uint8_t)(119u+i%17u);
    memcpy(b,a,NV12_BYTES);
}
static void run(int frame,uint32_t seq,double timestamp,
                unsigned profile,int tone) {
    fill(frame);
    assert(scalar_filter(a,NV12_BYTES,WIDTH,HEIGHT,tone,
                         seq,timestamp,profile,&sa,&ma)==0);
    assert(neon_filter(b,NV12_BYTES,WIDTH,HEIGHT,tone,
                       seq,timestamp,profile,&sn,&mn)==0);
    assert(memcmp(a,b,NV12_BYTES)==0);
    assert(memcmp(hist_a,hist_b,Y_BYTES)==0);
    assert(memcmp(&ma,&mn,sizeof(ma))==0);
    assert(sa.valid==sn.valid &&
           sa.last_sequence==sn.last_sequence &&
           sa.last_ms==sn.last_ms &&
           sa.last_median==sn.last_median &&
           sa.last_profile==sn.last_profile);
}
int main(void) {
#if !defined(__aarch64__)
#error This test requires real AArch64 NEON comparison not scalar fallback.
#endif
    a=malloc(NV12_BYTES);b=malloc(NV12_BYTES);
    hist_a=malloc(Y_BYTES);hist_b=malloc(Y_BYTES);
    assert(a&&b&&hist_a&&hist_b);
    assert(!scalar_init(&sa,hist_a,Y_BYTES) &&
           !neon_init(&sn,hist_b,Y_BYTES));
    run(0,1,1000.,1,0);
    run(1,2,1033.3,1,1);
    run(2,3,1066.6,1,1);
    run(3,4,1099.9,1,1);
    run(4,5,1133.2,1,1);
    run(5,6,1166.5,2,1);
    run(6,8,1199.8,2,1);
    run(7,9,1233.1,2,0);
    scalar_reset(&sa);neon_reset(&sn);
    assert(memcmp(hist_a,hist_b,Y_BYTES)==0);
    free(a);free(b);free(hist_a);free(hist_b);
    puts("SYNTHETIC_ONLY_REAR_FULL_4K_NV12_NEON_SCALAR_BIT_EXACT=PASS "
         "ALL_PIXELS_UV_STATE_COUNTERS_STATIC_MOVING_EDGE_SCENE_CUT_FRAME_GAP");
    return 0;
}
