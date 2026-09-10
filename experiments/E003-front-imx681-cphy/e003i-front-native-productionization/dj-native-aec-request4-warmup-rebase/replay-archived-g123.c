// SPDX-License-Identifier: GPL-2.0-only
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-control-join.h"
#include "native-stats3a.h"

static uint32_t fbits(float f)
{
    uint32_t u;
    memcpy(&u, &f, sizeof(u));
    return u;
}

static void *load_file(const char *path, size_t *bytes)
{
    FILE *f = fopen(path, "rb");
    long size;
    void *buf;

    if (f == NULL || fseek(f, 0, SEEK_END) != 0)
        return NULL;
    size = ftell(f);
    if (size <= 0 || fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }
    buf = malloc((size_t)size);
    if (buf == NULL) {
        fclose(f);
        return NULL;
    }
    if (fread(buf, 1, (size_t)size, f) != (size_t)size) {
        free(buf);
        fclose(f);
        return NULL;
    }
    fclose(f);
    *bytes = (size_t)size;
    return buf;
}

static int expect_hist(const struct e003i_request_loop_state *state,
                       uint64_t local_frame, unsigned offset,
                       uint64_t history_frame, uint64_t exposure,
                       uint32_t pred_bits)
{
    struct e003i_request_history_entry e;

    if (e003i_request_loop_get_history_offset(state, local_frame, offset, &e) != 0)
        return -1;
    if (e.frame_id != history_frame || e.short_exposure != exposure ||
        e.long_exposure != exposure || e.safe_exposure != exposure ||
        e.s1_exposure != exposure || fbits(e.pred_gain) != pred_bits)
        return -2;
    return 0;
}

int main(int argc, char **argv)
{
    static const uint64_t target[3] = {2922393002ULL, 2683504659ULL, 2678810946ULL};
    static const uint64_t conv[3] = {160604061ULL, 745178717ULL, 2407243907ULL};
    static const uint64_t retained[3] = {160604073ULL, 745178701ULL, 2407244072ULL};
    static const uint32_t fll[3] = {3562, 3562, 3839};
    static const uint32_t exposure[3] = {3554, 3554, 3830};
    static const uint32_t again[3] = {811, 960, 960};
    static const uint32_t dgain[3] = {256, 357, 1072};
    struct e003i_request_loop_state state;
    unsigned i;

    if (argc != 4)
        return 2;
    if (e003i_request_loop_init(&state) != 0)
        return 3;
    if (state.next_frame_id != 0 || fbits(state.lux_trigger) != 0x4365acddU)
        return 4;
    for (i = 0; i < 3; ++i) {
        const struct e003i_request_history_entry *e = &state.history[i];
        if (!e->valid || e->frame_id != i || e->short_exposure != 33312452ULL ||
            e->long_exposure != 33312452ULL || e->safe_exposure != 33312452ULL ||
            e->s1_exposure != 33312452ULL || fbits(e->pred_gain) != 0x3f800000U)
            return 5;
    }
    if (expect_hist(&state, 0, 1, 2, 33312452ULL, 0x3f800000U) ||
        expect_hist(&state, 0, 2, 1, 33312452ULL, 0x3f800000U) ||
        expect_hist(&state, 0, 3, 0, 33312452ULL, 0x3f800000U))
        return 6;

    puts("DJ_INITIAL=localG1_request4 lux=0x4365acdd h1=req3 h2=req2 h3=req1 exposure33312452 pred1");
    for (i = 0; i < 3; ++i) {
        size_t bytes = 0;
        void *buf = load_file(argv[i + 1], &bytes);
        struct e003i_raw_request_input in;
        struct e003i_raw_control_output out;
        int rc;

        if (buf == NULL)
            return 10 + (int)i;
        memset(&in, 0, sizeof(in));
        memset(&out, 0, sizeof(out));
        in.frame_id = i;
        in.stats3a = buf;
        in.stats3a_bytes = bytes;
        rc = e003i_raw_request_to_imx681_controls(&state, &in, &out);
        free(buf);
        if (rc != 0)
            return 20 + (int)i;
        if (out.stats_owned_request_frame != (uint64_t)i + 4ULL ||
            out.raw.request.target_publication.short_exposure != target[i] ||
            out.raw.request.convergence.linear[0] != conv[i] ||
            out.raw.request.short_arbitration.retained_exposure != retained[i])
            return 30 + (int)i;
        if (out.controls.frame_length_lines != fll[i] ||
            out.controls.exposure_lines != exposure[i] ||
            out.controls.analogue_gain_code != again[i] ||
            out.controls.digital_gain_code != dgain[i])
            return 40 + (int)i;
        if (fbits(out.raw.request.convergence.pred_gain) != 0x3f800000U ||
            state.next_frame_id != (uint64_t)i + 1ULL)
            return 50 + (int)i;
        printf("DJ_G%u=PASS request=%" PRIu64 " targetS=%" PRIu64
               " convS=%" PRIu64 " retainedS=%" PRIu64
               " FLL=%u EXP=%u AG=%u DG=%u\n",
               i + 1, out.stats_owned_request_frame, target[i], conv[i], retained[i],
               fll[i], exposure[i], again[i], dgain[i]);
    }
    {
        struct e003i_request_history_entry e;
        if (e003i_request_loop_get_history_offset(&state, 3, 1, &e) != 0 ||
            e.frame_id != 5 || e.short_exposure != retained[2] ||
            fbits(e.pred_gain) != 0x3f800000U)
            return 60;
    }
    puts("DJ_PRIOR_DB_G3_MINUS142=ELIMINATED_OFFLINE");
    puts("DJ_VERIFY=PASS");
    return 0;
}
