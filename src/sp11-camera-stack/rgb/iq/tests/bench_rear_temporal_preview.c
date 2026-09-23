/* No camera, raw images or external data: full 4K Y temporal CPU budget. */
#define _POSIX_C_SOURCE 200809L
#include "../rear_temporal_preview.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
enum { YP=SP11_REAR_PREVIEW_Y };
static double ms(void) {
    struct timespec t;assert(clock_gettime(CLOCK_MONOTONIC,&t)==0);
    return t.tv_sec*1000.0+t.tv_nsec/1.e6;
}
int main(void) {
    unsigned char *image=malloc(YP*3u/2u),*prior=malloc(YP);
    assert(image&&prior);
    memset(image,127,YP);memset(image+YP,128,YP/2u);
    struct sp11_rear_temporal_state s;
    struct sp11_rear_temporal_stats m;
    assert(sp11_rear_temporal_init(&s,prior,YP)==0);
    double durations[32]={0};uint64_t adjusted=0,bypassed=0;
    for(unsigned i=0;i<32;i++) {
        for(size_t p=0;p<YP;p+=64u)
            image[p]=(unsigned char)(127+((p/64u+i)%7u)-3);
        double start=ms();
        assert(sp11_rear_temporal_nv12(image,YP*3u/2u,3840,2160,1,
               i+1u,1000.0+33.333*i,1,&s,&m)==0);
        durations[i]=ms()-start;
        if(i>0)assert(m.filtered);
        adjusted+=m.pixels_changed;bypassed+=m.blocks_bypassed;
    }
    double sum=0,max=0;
    for(int k=4;k<32;k++) {
        sum+=durations[k];
        if(durations[k]>max)max=durations[k];
    }
    printf("REAR_4K_TEMPORAL_CAMERA_FREE_PER_FRAME mean_ms=%.3f "
           "worst_observed_ms=%.3f frames=28 pixels_changed=%llu "
           "blocks_bypassed=%llu no_camera=YES no_photo=YES\n",
           sum/28.,max,(unsigned long long)adjusted,
           (unsigned long long)bypassed);
    sp11_rear_temporal_reset(&s);free(image);free(prior);
}
