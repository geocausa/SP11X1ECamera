// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_STATS3A_H
#define E003I_NATIVE_STATS3A_H

#include <stddef.h>
#include <stdint.h>

#define E003I_STATS3A_HEADER_BYTES 64u
#define E003I_STATS3A_AEC_BYTES 0x14000u
#define E003I_STATS3A_BHIST_BYTES 0x1000u
#define E003I_STATS3A_AWB_BYTES 0x3c000u
#define E003I_STATS3A_RAW_BYTES 0x51000u
#define E003I_STATS3A_BYTES \
    (E003I_STATS3A_HEADER_BYTES + E003I_STATS3A_RAW_BYTES)
#define E003I_STATS3A_MAGIC UINT32_C(0x54534133)

struct e003i_stats3a_view {
    uint64_t generation;
    uint32_t source_seq;
    uint32_t slot;
    const uint8_t *aec_raw;
    const uint32_t *bhist_raw;
    const uint8_t *awb_raw;
};

/* Validate the generation-tagged producer envelope and expose its raw planes. */
int e003i_stats3a_open(const void *data, size_t bytes,
                       struct e003i_stats3a_view *out);

/* Exact normal-front FrameLumaBE16x16 -> Equally Weighted FrameSA replay. */
int e003i_aecbe_frame_luma(
    const uint8_t aec_raw[E003I_STATS3A_AEC_BYTES], float *out_luma);

#endif
