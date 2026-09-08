// SPDX-License-Identifier: GPL-2.0-only
#include "native-final-exposure.h"
#include <math.h>
#include <stddef.h>

static int adjratio_to_si(uint64_t source_exposure, float adj_ratio,
                          uint64_t *out)
{
    double product;

    if (out == NULL || !isfinite(adj_ratio) || !(adj_ratio > 0.0f))
        return -1;
    product = (double)source_exposure * (double)adj_ratio;
    /* Ordinary-path scope: match FCVTZU truncation for positive in-range d64. */
    if (!isfinite(product) || product < 0.0 || product >= 0x1p64)
        return -2;
    *out = (uint64_t)product;
    return 0;
}

int e003i_aec_default_final_exposures(
    const struct e003i_final_exposure_input *in,
    struct e003i_final_exposure_output *out)
{
    int rc;

    if (in == NULL || out == NULL)
        return -1;
    rc = e003i_aec_default_final_targets(&in->target_input, &out->targets);
    if (rc != 0)
        return -2;

    if (adjratio_to_si(in->source_exposure_s1,
                       out->targets.tail.short_adj_ratio,
                       &out->short_exposure) != 0)
        return -3;
    if (adjratio_to_si(in->source_exposure_s1,
                       out->targets.tail.long_adj_ratio,
                       &out->long_exposure) != 0)
        return -4;
    if (adjratio_to_si(in->source_exposure_s1,
                       out->targets.safe_adj_ratio,
                       &out->safe_exposure) != 0)
        return -5;
    return 0;
}
