// SPDX-License-Identifier: GPL-2.0-only
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-control-join.h"
static void *read_file(const char *path, size_t *bytes)
{
    FILE *f=fopen(path,"rb"); long z; void *p;
    if(!f) return NULL;
    if(fseek(f,0,SEEK_END) || (z=ftell(f))<0 || fseek(f,0,SEEK_SET)){fclose(f);return NULL;}
    p=malloc((size_t)z); if(!p){fclose(f);return NULL;}
    if(fread(p,1,(size_t)z,f)!=(size_t)z){free(p);fclose(f);return NULL;}
    fclose(f); *bytes=(size_t)z; return p;
}
int main(int argc,char **argv)
{
    struct e003i_request_loop_state state; int g;
    if(argc!=2) return 2;
    if(e003i_request_loop_init(&state)) return 3;
    for(g=1;g<=27;g++){
        char path[4096]; size_t bytes=0; void *buf;
        struct e003i_raw_request_input in; struct e003i_raw_control_output out;
        snprintf(path,sizeof(path),"%s/STATS3A-%d.bin",argv[1],g-1);
        buf=read_file(path,&bytes); if(!buf) return 10+g;
        memset(&out,0,sizeof(out)); in.frame_id=(uint64_t)(g-1); in.stats3a=buf; in.stats3a_bytes=bytes;
        if(e003i_raw_request_to_imx681_controls(&state,&in,&out)){free(buf);return 50+g;}
        printf("G=%d LUMA=%.9g LUX_IN=%.9g FRAME_TARGET=%.9g FRAME_CAND=%.9g FRAME_CONF=%.9g NEXT_LUX=%.9g CONV_SHORT=%llu CAP_SHORT=%llu T681_GAIN=%.9g T681_TIME=%llu FLL=%u VB=%u EXP=%u AGAIN=%u DGAIN=%u ISP=%.9g\n",
               g,out.raw.measured_luma,out.raw.request.lux_trigger_in,out.raw.request.frame_target,
               out.raw.request.frame_candidate.value,out.raw.request.frame_candidate.confidence,
               out.raw.request.next_lux_trigger,(unsigned long long)out.raw.request.convergence.linear[0],
               (unsigned long long)out.raw.request.capped.linear[0],out.raw.request.short_arbitration.gain,
               (unsigned long long)out.raw.request.short_arbitration.exposure_time_ns,
               out.controls.frame_length_lines,out.controls.vertical_blanking,out.controls.exposure_lines,
               out.controls.analogue_gain_code,out.controls.digital_gain_code,out.controls.isp_gain);
        free(buf);
    }
    return 0;
}
