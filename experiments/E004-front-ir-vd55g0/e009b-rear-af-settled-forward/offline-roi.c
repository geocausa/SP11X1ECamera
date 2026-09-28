/* SPDX-License-Identifier: MIT */
/* Host-only, source-composed settled AF ROI candidate. No runtime call site. */
#include <stdio.h>
#define main e008t_existing_host_check
#include "../e008t-rear-packet-aware-bf-semantic-composer/compile-check.c"
#undef main
#include "../e008x-rear-af-bf-roi-map/af-bf-roi-map.h"
#include "../e008z-rear-af-default-rectangle/af-default-rectangle.h"

int main(void)
{
    const struct e008z_af_default_inputs in = {
        .camif_width = 4064, .camif_height = 2286,
        .width_fraction = 0.25f, .height_fraction = 0.25f,
        .mode_scale = 1.0f, .zoom = 1.0f,
        .pd_width_scale = 1.0f, .pd_height_scale = 1.0f,
        .alternate_mode = 0, .pd_scale_enabled = 0, .sparse_pd = 0,
    };
    struct e008z_af_rect af;
    struct e008x_rect baf;
    struct e008x_roi mapped[25];
    struct e008o_rear_bootstrap s;
    u8 payload[E007E_BF_ROI_BYTES];
    unsigned int packet, i;

    if (e008z_af_default_rect(&in, &af))
        return 10;
    /* af_util_adjust_roi even halfwords, BAF SetROICoordinates
     * vertical count five plus its source constant eleven. The
     * accepted crop passes the BAF clamp without modifying this rect.
     */
    baf.x = af.x & ~1U;
    baf.y = af.y & ~1U;
    baf.width = af.width & ~1U;
    baf.height = (af.height & ~1U) + 5U + 11U;
    if (baf.x < 76 || baf.y < 64 || baf.x + baf.width > 4064 - 12 ||
        baf.y + baf.height > 2286)
        return 11;
    if (e008x_normal_roi_map(baf, mapped))
        return 12;
    memset(&s, 0, sizeof(s));
    s.initialized = true;
    if (e008t_rear_seed_bootstrap_bf(&s, 4064, 2286))
        return 13;
    for (packet = 0; packet < 4; packet++) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[packet].dmi);
        if (!d || d->roi_count != 25)
            return 20;
        if (packet) {
            for (i = 0; i < 25; i++) {
                d->roi[i].left = mapped[i].left;
                d->roi[i].top = mapped[i].top;
                d->roi[i].width = mapped[i].width;
                d->roi[i].height = mapped[i].height;
            }
        }
        if (e007e_bfstats25_dmi(d, 1, payload, sizeof(payload)))
            return 30;
        if (fwrite(payload, 1, sizeof(payload), stdout) != sizeof(payload))
            return 40;
    }
    return 0;
}
