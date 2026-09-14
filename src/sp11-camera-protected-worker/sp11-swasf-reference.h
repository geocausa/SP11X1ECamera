/* SPDX-License-Identifier: MIT */
#ifndef SP11_SWASF_REFERENCE_H
#define SP11_SWASF_REFERENCE_H
#include <stddef.h>
#include <stdint.h>

#define SP11_SWASF_TUNING_WORDS 513u
#define SP11_SWASF_WINDOWS_ACTIVITY_SCALE 253

extern const uint32_t sp11_swasf_windows_oracle_tuning[SP11_SWASF_TUNING_WORDS];

/*
 * Full scalar transcription of the shipping Windows SWASF luma transform.
 * raw16 and smooth16 are caller-owned width*height scratch planes.
 */
int sp11_swasf_reference(uint8_t *dst, size_t dst_len,
                         const uint8_t *src, size_t src_len,
                         uint32_t width, uint32_t height,
                         int16_t *raw16, size_t raw_count,
                         int16_t *smooth16, size_t smooth_count,
                         const uint32_t tune[SP11_SWASF_TUNING_WORDS],
                         int16_t activity_scale);

#endif
