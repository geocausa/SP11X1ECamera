/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWASF_CD90_H
#define SP11_SWASF_CD90_H
#include <stdint.h>
void sp11_swasf_cd90(const int16_t p1[8], uint8_t out[8], const uint8_t p3[8],
                     const int16_t p4[8], const int16_t p5[8], const int16_t p6[8],
                     const int16_t p7[8], const int32_t p8[8], const uint8_t p9[8],
                     const int16_t p10[8], const int16_t p11[8], const int16_t p12[8],
                     const uint32_t tune[513]);
#endif
