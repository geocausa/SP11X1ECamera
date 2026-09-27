/* SPDX-License-Identifier: MIT */
/* Host-only, narrow BFStats25 normal ROI width validation slice. */
#include <stdio.h>
#define main e008t_existing_host_check
#include "../e008t-rear-packet-aware-bf-semantic-composer/compile-check.c"
#undef main

int main(void)
{
    struct e008o_rear_bootstrap s;
    unsigned int packet, roi;
    u8 payload[E007E_BF_ROI_BYTES];

    memset(&s, 0, sizeof(s));
    s.initialized = true;
    if (e008t_rear_seed_bootstrap_bf(&s, 4064, 2286))
        return 10;
    for (packet = 0; packet < 4; packet++) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[packet].dmi);

        if (!d || d->roi_count != E007E_BF_ROI_COUNT)
            return 20;
        if (packet) {
            for (roi = 0; roi < d->roi_count; roi++) {
                struct e007e_bf_roi *r = &d->roi[roi];

                /* BFStats25::ValidateAndAdjustROIBoundary, valid
                 * non-clipping width branch: an even width is reduced
                 * by one to satisfy the odd hardware dimension rule.
                 * This slice deliberately leaves other fields open.
                 */
                if (!r->width || r->width < 5 || r->width >= 4064)
                    return 30;
                if (!(r->width & 1))
                    r->width--;
            }
        }
        if (e007e_bfstats25_dmi(d, 1, payload, sizeof(payload)))
            return 40;
        if (fwrite(payload, 1, sizeof(payload), stdout) != sizeof(payload))
            return 50;
    }
    return 0;
}
