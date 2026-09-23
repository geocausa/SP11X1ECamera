/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include "raw-nv12-probe.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
int main(void) {
    enum { SW=128,SH=64,STRIDE=160,OW=64,OH=32 };
    unsigned char *raw=calloc(1,(size_t)STRIDE*SH);
    unsigned char *nv12=calloc(1,(size_t)OW*OH*3/2);
    assert(raw&&nv12);
    for(int y=0;y<SH;y++)
        for(int x=0;x<SW;x++)
            raw[(size_t)y*STRIDE+(x/4)*5+(x%4)]=80;
    memset(nv12,16,(size_t)OW*OH);
    struct sp11_mc_pair p;
    assert(sp11_mc_measure(raw,nv12,SW,SH,STRIDE,OW,OH,2,0,0,&p));
    assert(p.source.total==4*p.output.total);
    assert(sp11_mc_percentile(&p.source,95)==80);
    assert(sp11_mc_percentile(&p.source,99)==80);
    assert(sp11_mc_percentile(&p.output,99)==16);
    assert(p.source.above32==p.source.total && p.output.above32==0);
    sp11_mc_report("synthetic",1,&p);
    memset(raw,0,(size_t)STRIDE*SH);
    assert(sp11_mc_measure(raw,nv12,SW,SH,STRIDE,OW,OH,2,0,0,&p));
    assert(sp11_mc_percentile(&p.source,99)==0);
    assert(!sp11_mc_measure(raw,nv12,SW,SH,STRIDE,OW,OH,2,64,0,&p));
    free(raw);free(nv12);
    puts("E004MX_CAMERA_FREE_PAIRED_RAW_NV12_SCALAR_PROBE=PASS");
    return 0;
}
