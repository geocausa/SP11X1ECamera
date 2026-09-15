// SPDX-License-Identifier: GPL-2.0-only
#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-aec-loop.h"

#define STATS_BYTES 331840u

static int load_file(const char *p, unsigned char *buf, size_t n)
{
    FILE *f = fopen(p, "rb"); size_t got;
    if (!f) return -errno;
    got = fread(buf, 1, n, f);
    if (got != n || fgetc(f) != EOF) { fclose(f); return -EIO; }
    if (fclose(f)) return -errno;
    return 0;
}

static void cand(const char *name, const struct e003i_aec_candidate *c)
{
    printf(" %s=%.9g/%a conf=%.9g/%a", name, c->value, c->value, c->confidence, c->confidence);
}

int main(int argc, char **argv)
{
    struct e003i_request_loop_state st;
    unsigned char *buf;
    unsigned g;
    if (argc != 2) { fprintf(stderr, "usage: %s FRONT1_DIR\n", argv[0]); return 2; }
    buf = malloc(STATS_BYTES); if (!buf) return 3;
    if (e003i_request_loop_init(&st)) { fprintf(stderr, "init failed\n"); return 4; }

    printf("E004EG_OFFLINE_AEC_REPLAY_BEGIN\n");
    for (g = 1; g <= 27; ++g) {
        char path[4096];
        struct e003i_raw_request_input in;
        struct e003i_raw_request_output out;
        struct e003i_request_history_entry h1, h2, h3;
        int rc;
        snprintf(path, sizeof(path), "%s/STATS3A-%u.bin", argv[1], g - 1u);
        rc = load_file(path, buf, STATS_BYTES); if (rc) { fprintf(stderr, "load G%u rc=%d\n", g, rc); return 10; }
        rc = e003i_request_loop_get_history_offset(&st, g - 1u, 1, &h1); if (rc) return 11;
        rc = e003i_request_loop_get_history_offset(&st, g - 1u, 2, &h2); if (rc) return 12;
        rc = e003i_request_loop_get_history_offset(&st, g - 1u, 3, &h3); if (rc) return 13;
        memset(&in, 0, sizeof(in)); in.frame_id = g - 1u; in.stats3a = buf; in.stats3a_bytes = STATS_BYTES;
        rc = e003i_raw_request_loop_process(&st, &in, &out);
        if (rc) { fprintf(stderr, "process G%u rc=%d\n", g, rc); return 20; }

        printf("G=%u H1=%" PRIu64 " H2=%" PRIu64 " H3=%" PRIu64,
               g, h1.short_exposure, h2.short_exposure, h3.short_exposure);
        printf(" LUMA=%.9g/%a LUX_IN=%.9g/%a FRAME_TARGET=%.9g/%a FRAME_ADJ=%.9g/%a",
               out.measured_luma, out.measured_luma,
               out.request.lux_trigger_in, out.request.lux_trigger_in,
               out.request.frame_target, out.request.frame_target,
               out.request.frame_candidate.value, out.request.frame_candidate.value);
        printf(" B4_SAT=%.9g B4_HI=%.9g B4_LO=%.9g B4_SHI=%.9g",
               out.bank4.saturate_stats_ratio, out.bank4.sat_prev_high_pctl_luma,
               out.bank4.dark_prev_low_pctl_luma, out.bank4.short_sat_prev_high_pctl_luma);
        cand("EFF_FRAME", &out.effective_target.frame);
        cand("EFF_SAT", &out.effective_target.sat_prev);
        cand("EFF_DARK", &out.effective_target.dark_prev);
        cand("EFF_ILLUM", &out.effective_target.illuminance);
        cand("EFF_SHORTSAT", &out.effective_target.short_sat_prev);
        printf(" TARGET_SAFE=%.9g TARGET_SHORT=%.9g TARGET_LONG=%.9g",
               out.request.target_publication.targets.safe_target,
               out.request.target_publication.targets.short_target,
               out.request.target_publication.targets.long_target);
        printf(" PUB_SHORT=%" PRIu64 " PUB_LONG=%" PRIu64 " PUB_SAFE=%" PRIu64,
               out.request.target_publication.short_exposure,
               out.request.target_publication.long_exposure,
               out.request.target_publication.safe_exposure);
        printf(" CONV=%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64,
               out.request.convergence.linear[0], out.request.convergence.linear[1], out.request.convergence.linear[2],
               out.request.convergence.linear[3], out.request.convergence.linear[4], out.request.convergence.linear[5],
               out.request.convergence.linear[6]);
        printf(" PRED=%.9g STRETCH=%.9g/%.9g RATIO=%.9g DRC=%.9g",
               out.request.convergence.pred_gain, out.request.convergence.short_stretch,
               out.request.convergence.safe_stretch, out.request.convergence.stretch_ratio,
               out.request.convergence.drc_ratio);
        printf(" CAP=%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64,
               out.request.capped.linear[0], out.request.capped.linear[1], out.request.capped.linear[2],
               out.request.capped.linear[3], out.request.capped.linear[4], out.request.capped.linear[5], out.request.capped.linear[6]);
        printf(" CAP_FLAGS=rescaled:%u,snap:%u CAP_PRED=%.9g",
               out.request.capped.rescaled, out.request.capped.history_snapped, out.request.capped.pred_gain);
        printf(" T681_SHORT=ret:%" PRIu64 ",time:%" PRIu64 ",gain:%.9g,corr:%.9g,knee:%u",
               out.request.short_arbitration.retained_exposure,
               out.request.short_arbitration.exposure_time_ns,
               out.request.short_arbitration.gain,
               out.request.short_arbitration.correction,
               out.request.short_arbitration.upper_knee);
        printf(" NEXT_LUX=%.9g/%a HREF=%.9g/%a\n",
               out.request.next_lux_trigger, out.request.next_lux_trigger,
               out.request.history_reference_log103, out.request.history_reference_log103);
    }
    printf("E004EG_OFFLINE_AEC_REPLAY_END\n");
    free(buf); return 0;
}
