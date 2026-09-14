/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWABF_REFERENCE_H
#define SP11_SWABF_REFERENCE_H
#include <stddef.h>
#include <stdint.h>
struct sp11_swabf_tuning {
    int16_t weight[16];
    int16_t threshold;
};
extern const struct sp11_swabf_tuning sp11_swabf_windows_oracle_tuning;
int sp11_swabf_reference(uint8_t *dst, size_t dst_len,
                         const uint8_t *src, size_t src_len,
                         uint32_t width, uint32_t height,
                         const struct sp11_swabf_tuning *tuning);
#endif
