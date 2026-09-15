// SPDX-License-Identifier: GPL-2.0-only
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-aec-loop.h"
#define STATS_BYTES 331840u
static uint32_t fbits(float f){uint32_t u;memcpy(&u,&f,4);return u;}
int main(int argc,char **argv)
{
    struct e003i_request_loop_state st;
    struct e003i_raw_request_input in;
    struct e003i_raw_request_output out;
    unsigned char *buf;
    FILE *f;
    size_t n;
    int rc;
    if(argc!=2){fprintf(stderr,"usage: %s STATS3A-G1\n",argv[0]);return 2;}
    buf=malloc(STATS_BYTES); if(!buf)return 3;
    f=fopen(argv[1],"rb"); if(!f)return 4;
    n=fread(buf,1,STATS_BYTES,f); if(n!=STATS_BYTES||fgetc(f)!=EOF){fclose(f);return 5;} fclose(f);
    rc=e003i_request_loop_init(&st); if(rc)return 10;
    memset(&in,0,sizeof(in)); in.frame_id=0; in.stats3a=buf; in.stats3a_bytes=STATS_BYTES;
    rc=e003i_raw_request_loop_process(&st,&in,&out); free(buf); if(rc){fprintf(stderr,"process rc=%d\n",rc);return 20;}
    printf("G1_LUMA=%.9g\n",out.measured_luma);
    printf("G1_FRAME_ADJ_BITS=0x%08x\n",fbits(out.request.frame_candidate.low));
    printf("G1_SAFE_BITS=0x%08x\n",fbits(out.request.target_publication.targets.safe_target));
    printf("G1_SHORT_TARGET_BITS=0x%08x\n",fbits(out.request.target_publication.targets.short_target));
    printf("G1_PUBLISHED_SHORT=%" PRIu64 "\n",out.request.target_publication.short_exposure);
    printf("G1_CONV_SHORT=%" PRIu64 "\n",out.request.convergence.linear[0]);
    printf("G1_CAP_SHORT=%" PRIu64 "\n",out.request.capped.linear[0]);
    printf("G1_RETAINED_SHORT=%" PRIu64 "\n",out.request.short_arbitration.retained_exposure);
    printf("G1_SAT_RANGE=[%.9g,%.9g] conf=%.9g\n",out.effective_target.sat_prev.low,out.effective_target.sat_prev.high,out.effective_target.sat_prev.confidence);
    printf("G1_DARK_RANGE=[%.9g,%.9g] conf=%.9g\n",out.effective_target.dark_prev.low,out.effective_target.dark_prev.high,out.effective_target.dark_prev.confidence);
    if(fbits(out.request.target_publication.targets.safe_target)!=fbits(out.request.frame_candidate.low)) return 31;
    if(out.request.convergence.linear[0]!=UINT64_C(84034875)) return 32;
    if(out.request.capped.linear[0]!=UINT64_C(84034875)) return 33;
    if(out.request.short_arbitration.retained_exposure!=UINT64_C(84034869)) return 34;
    puts("E004EH_G1_INTERVAL_REPLAY=PASS");
    return 0;
}
