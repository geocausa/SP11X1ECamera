// SPDX-License-Identifier: GPL-2.0-only
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-control-join.h"

static uint32_t bits(float f) { uint32_t u; memcpy(&u,&f,4); return u; }
static void candidate(const char *name, struct e003i_aec_candidate c) {
    printf(" %s=%.9g/%.9g",name,(double)c.value,(double)c.confidence);
}
int main(int argc,char **argv) {
    static const uint32_t expected_controls[3][4] = {
        {3562,3554,851,256},{3562,3554,960,556},{7116,7108,960,1111}
    };
    static const uint64_t expected_short[4] = {197553046ULL,1158944674ULL,4631188028ULL,24819566146ULL};
    struct e003i_request_loop_state state;
    if(argc!=5 || e003i_request_loop_init(&state)) return 2;
    for(unsigned i=0;i<4;i++) {
        FILE *f=fopen(argv[i+1],"rb"); long size; void *buf;
        struct e003i_raw_request_input in={0};
        struct e003i_raw_control_output controls;
        struct e003i_raw_request_output raw;
        struct e003i_request_loop_state before=state, trace=state;
        if(!f || fseek(f,0,SEEK_END) || (size=ftell(f))<=0 || fseek(f,0,SEEK_SET)) return 3;
        buf=malloc((size_t)size); if(!buf || fread(buf,1,(size_t)size,f)!=(size_t)size) return 4;
        fclose(f);
        {
            struct e003i_stats3a_view view;
            float axis[E003I_BHIST_BINS];
            uint64_t total=0; double weighted=0;
            if(e003i_stats3a_open(buf,(size_t)size,&view) ||
               e003i_bhist_build_value_axis(axis)) return 6;
            for(unsigned j=0;j<E003I_BHIST_BINS;j++) {
                uint32_t c=view.bhist_raw[j]&E003I_BHIST_RAW_MASK;
                total+=c; weighted+=(double)c*(double)axis[j];
            }
            if(total!=2073600ULL) return 7;
            printf("BHIST G=%u total=%"PRIu64" mean=%.12g\n",i+1,total,weighted/(double)total);
        }
        in.frame_id=i; in.stats3a=buf; in.stats3a_bytes=(size_t)size;
        printf("G%u lux=0x%08x %.9g\n",i+1,bits(state.lux_trigger),(double)state.lux_trigger);
        for(unsigned off=1;off<=3;off++) {
            struct e003i_request_history_entry h;
            if(e003i_request_loop_get_history_offset(&state,i,off,&h)) return 5;
            printf(" H%u request=%"PRIu64" short=%"PRIu64" long=%"PRIu64" safe=%"PRIu64" s1=%"PRIu64" pred=0x%08x\n",
                off,h.frame_id+1,h.short_exposure,h.long_exposure,h.safe_exposure,h.s1_exposure,bits(h.pred_gain));
        }
        int trc=e003i_raw_request_loop_process(&trace,&in,&raw);
        memset(&controls,0xa5,sizeof(controls));
        int rc=e003i_raw_request_to_imx681_controls(&state,&in,&controls);
        printf(" CU_RC=%d CV_RC=%d luma=0x%08x %.9g bank4=%.9g,%.9g,%.9g,%.9g\n",
            trc,rc,bits(raw.measured_luma),(double)raw.measured_luma,
            (double)raw.bank4.saturate_stats_ratio,(double)raw.bank4.sat_prev_high_pctl_luma,
            (double)raw.bank4.dark_prev_low_pctl_luma,(double)raw.bank4.short_sat_prev_high_pctl_luma);
        candidate("frame",raw.effective_target.frame); candidate("sat",raw.effective_target.sat_prev);
        candidate("dark",raw.effective_target.dark_prev); candidate("illuminance",raw.effective_target.illuminance);
        candidate("short",raw.effective_target.short_sat_prev); puts("");
        printf(" TARGET ratios=%.9g,%.9g,%.9g qwords=%"PRIu64",%"PRIu64",%"PRIu64"\n",
            (double)raw.request.target_publication.targets.short_target,(double)raw.request.target_publication.targets.long_target,
            (double)raw.request.target_publication.targets.safe_target,raw.request.target_publication.short_exposure,
            raw.request.target_publication.long_exposure,raw.request.target_publication.safe_exposure);
        printf(" CONV=%"PRIu64",%"PRIu64",%"PRIu64" basic=%.17g direction=%u pred=%.9g drc_branch=%u\n",
            raw.request.convergence.linear[0],raw.request.convergence.linear[1],raw.request.convergence.linear[2],
            raw.request.convergence.basic_safe_log,raw.request.convergence.basic_direction_ok,
            (double)raw.request.convergence.pred_gain,raw.request.convergence.drc_branch);
        if(raw.request.convergence.linear[0]!=expected_short[i]) return 8;
        if(i<3) {
            if(rc || trc) return 10+(int)i;
            const uint32_t *e=expected_controls[i];
            if(controls.controls.frame_length_lines!=e[0] || controls.controls.exposure_lines!=e[1] ||
               controls.controls.analogue_gain_code!=e[2] || controls.controls.digital_gain_code!=e[3]) return 15+(int)i;
            printf(" CONTROL FLL=%u EXP=%u AG=%u DG=%u retained=%"PRIu64"\n",
                controls.controls.frame_length_lines,controls.controls.exposure_lines,
                controls.controls.analogue_gain_code,controls.controls.digital_gain_code,
                raw.request.short_arbitration.retained_exposure);
        } else {
            unsigned char expected[sizeof(controls)]; memset(expected,0xa5,sizeof(expected));
            if(rc!=-142 || trc!=-132 || memcmp(&state,&before,sizeof(state)) ||
                memcmp(&trace,&before,sizeof(trace)) || memcmp(&controls,expected,sizeof(controls))) return 20;
            if(raw.request.convergence.linear[0]<=6133333272ULL) return 21;
            puts("G4_FAILURE_REPRODUCED=PASS STATE_AND_CONTROL_OUTPUT_UNCHANGED=PASS");
        }
        free(buf);
    }
    return 0;
}
