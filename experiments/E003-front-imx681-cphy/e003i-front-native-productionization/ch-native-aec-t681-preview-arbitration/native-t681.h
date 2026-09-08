// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_T681_H
#define E003I_NATIVE_T681_H
#include <stdint.h>

struct e003i_t681_result {
    float gain;
    uint64_t exposure_time_ns;
    float correction;
    uint64_t retained_exposure;
    uint32_t upper_knee;
};

/*
 * Ordinary front-preview T681 arbitration for a positive in-table target.
 * Applies the pinned preview range fit (time maximum 33,333,332 ns) and
 * returns the exact retained exposure qword persisted by runEndOfFrame.
 */
int e003i_t681_preview_arbitrate(uint64_t target_exposure,
                                struct e003i_t681_result *out);

#endif
