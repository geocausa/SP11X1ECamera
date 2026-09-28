/* SPDX-License-Identifier: MIT */
/* Host-only four-packet ROI candidate; zoom is an explicit caller input. */
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#define main e008t_existing_host_check
#include "../e008t-rear-packet-aware-bf-semantic-composer/compile-check.c"
#undef main
#include "../e009c-rear-af-request-roi-handoff/af-request-roi-handoff.h"

static int parse_zoom(const char *arg, float *out)
{
    char *end;
    errno = 0;
    *out = strtof(arg, &end);
    return errno || end == arg || *end || !(*out > 0.0f) || !(*out < 16.0f);
}

int main(int argc, char **argv)
{
    struct e008o_rear_bootstrap s;
    struct e008z_af_default_inputs in = {
        .camif_width = 4064, .camif_height = 2286,
        .width_fraction = 0.25f, .height_fraction = 0.25f,
        .mode_scale = 1.0f, .pd_width_scale = 1.0f,
        .pd_height_scale = 1.0f,
    };
    struct e008z_af_rect af;
    float first_zoom, settled_zoom;
    u8 payload[E007E_BF_ROI_BYTES];
    unsigned int packet;

    if (argc != 3 || parse_zoom(argv[1], &first_zoom) ||
        parse_zoom(argv[2], &settled_zoom))
        return 10;
    memset(&s, 0, sizeof(s));
    s.initialized = true;
    if (e008t_rear_seed_bootstrap_bf(&s, 4064, 2286))
        return 11;
    for (packet = 0; packet < 4; packet++) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[packet].dmi);
        if (!d || d->roi_count != 25)
            return 20;
        if (packet) {
            in.zoom = packet == 1 ? first_zoom : settled_zoom;
            if (e008z_af_default_rect(&in, &af) ||
                e009c_rear_apply_af_rect(&s, packet, 4064, 2286, &af))
                return 21;
        }
        if (e007e_bfstats25_dmi(d, 1, payload, sizeof(payload)))
            return 30;
        if (fwrite(payload, 1, sizeof(payload), stdout) != sizeof(payload))
            return 40;
    }
    return 0;
}
