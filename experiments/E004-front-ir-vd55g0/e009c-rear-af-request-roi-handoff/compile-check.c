/* SPDX-License-Identifier: MIT */
/* Host-only type/phase/byte check; never linked into qcom-camss. */
#include <stdio.h>
#define main e008t_existing_host_check
#include "../e008t-rear-packet-aware-bf-semantic-composer/compile-check.c"
#undef main
#include "af-request-roi-handoff.h"

int main(void)
{
    struct e008o_rear_bootstrap s;
    struct e008z_af_default_inputs in = {
        .camif_width = 4064, .camif_height = 2286,
        .width_fraction = 0.25f, .height_fraction = 0.25f,
        .mode_scale = 1.0f, .zoom = 1.0f,
        .pd_width_scale = 1.0f, .pd_height_scale = 1.0f,
    };
    struct e008z_af_rect af, invalid;
    u8 payload[E007E_BF_ROI_BYTES], before[E007E_BF_ROI_BYTES];
    unsigned int packet;
    memset(&s, 0, sizeof(s));
    s.initialized = true;
    if (e008t_rear_seed_bootstrap_bf(&s, 4064, 2286) ||
        e008z_af_default_rect(&in, &af))
        return 10;
    if (e007e_bfstats25_dmi(e008t_rear_bf_dmi(&s.packet[0].dmi),
                            1, before, sizeof(before)))
        return 11;
    if (e009c_rear_apply_af_rect(&s, 0, 4064, 2286, &af) == 0 ||
        e007e_bfstats25_dmi(e008t_rear_bf_dmi(&s.packet[0].dmi),
                            1, payload, sizeof(payload)) ||
        memcmp(before, payload, sizeof(payload)))
        return 12;
    for (packet = 1; packet < 4; packet++) {
        if (e009c_rear_apply_af_rect(&s, packet, 4064, 2286, &af) ||
            e007e_bfstats25_dmi(e008t_rear_bf_dmi(&s.packet[packet].dmi),
                                1, payload, sizeof(payload)))
            return 20 + packet;
        if (fwrite(payload, 1, sizeof(payload), stdout) != sizeof(payload))
            return 30 + packet;
    }
    invalid = af;
    invalid.x = 0;
    if (e009c_rear_apply_af_rect(&s, 1, 4064, 2286, &invalid) == 0 ||
        e007e_bfstats25_dmi(e008t_rear_bf_dmi(&s.packet[1].dmi),
                            1, before, sizeof(before)) ||
        memcmp(before, payload, sizeof(payload)))
        return 40;
    s.packet[1].consumed = true;
    if (e009c_rear_apply_af_rect(&s, 1, 4064, 2286, &af) == 0)
        return 41;
    return 0;
}
