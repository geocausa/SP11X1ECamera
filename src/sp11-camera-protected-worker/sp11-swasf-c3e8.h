/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWASF_C3E8_H
#define SP11_SWASF_C3E8_H
#include <stdint.h>
void sp11_swasf_c3e8_tile(const int16_t *src, int stride,
                          int x0, int x1, int y0, int y1,
                          int width, int height,
                          int32_t *out_hp, uint8_t *out_lp, int16_t *out_cross5);
#endif
