/* SPDX-License-Identifier: MIT */
/* Host-only E008t packet materialization for the E008u private audit. */
#include <stdio.h>
#define main e008t_existing_host_check
#include "../e008t-rear-packet-aware-bf-semantic-composer/compile-check.c"
#undef main

int main(void)
{
    struct e008o_rear_bootstrap s;
    unsigned int i;
    u8 payload[E007E_BF_ROI_BYTES];

    memset(&s, 0, sizeof(s));
    s.initialized = true;
    /* The accepted rear ISP crop is 4064x2286, not the raw sensor extent. */
    if (e008t_rear_seed_bootstrap_bf(&s, 4064, 2286))
        return 10;
    for (i = 0; i < 4; ++i) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[i].dmi);
        if (e007e_bfstats25_dmi(d, 1, payload, sizeof(payload)))
            return 20 + i;
        if (fwrite(payload, 1, sizeof(payload), stdout) != sizeof(payload))
            return 30 + i;
    }
    return 0;
}
