// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_INTERNAL_CAP_H
#define E003I_NATIVE_INTERNAL_CAP_H
#include <stdint.h>
#define E003I_CAP_LANES 7
#define E003I_PREVIEW_CAP_MIN UINT64_C(37516)
#define E003I_PREVIEW_CAP_MAX UINT64_C(6133333088)
/* Order is Short, Long, Safe, S1, S2, S3, S4. */
struct e003i_cap_input {
    uint64_t linear[7], minimum[7], maximum[7];
    uint64_t history1_short;
    float pred_gain, compact_98, snap_steps;
    uint32_t rescale_disabled, history1_valid;
};
struct e003i_cap_output {
    uint64_t linear[7];
    float pred_gain;
    uint32_t rescaled, history_snapped;
};
/* Parameterized arithmetic from the pinned Windows internal cap, atomic on error. */
int e003i_internal_cap(const struct e003i_cap_input *, struct e003i_cap_output *);
/* DM observed preview domain. Rejects an eligible conditional prelude because
 * its bank9:data10 value has not yet been observed in this reduced runtime. */
int e003i_internal_cap_preview_observed(const uint64_t linear[7], float pred_gain,
                                      struct e003i_cap_output *);
#endif
