/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWASF_C230_H
#define SP11_SWASF_C230_H
#include <stdint.h>

void sp11_swasf_c230(const int16_t rows[7][8], const int16_t tail[2],
                     int32_t out4[2], uint8_t out2[2]);

#endif
