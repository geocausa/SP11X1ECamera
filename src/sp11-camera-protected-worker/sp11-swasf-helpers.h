/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWASF_HELPERS_H
#define SP11_SWASF_HELPERS_H
#include <stdint.h>
void sp11_swasf_local_extrema_5x5(const int16_t rows[5][8], int16_t pos[4], int16_t neg[4]);
uint8_t sp11_swasf_c078_activity(const int16_t rows[5][8], int16_t center, int16_t scale);
#endif
