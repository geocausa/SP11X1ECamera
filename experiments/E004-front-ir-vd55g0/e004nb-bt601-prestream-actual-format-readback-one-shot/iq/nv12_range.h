/* SPDX-License-Identifier: MIT
 * Camera-free integer mapping of provisional full-range 8-bit RGB luma and
 * chroma into nominal 8-bit studio/video-range NV12, opt-in ONLY.
 * This corrects an output-range convention, NOT sensor exposure, Bayer
 * colourimetry, calibrated black reference, dynamic tone mapping or IQ.
 */
#ifndef SP11_RGB_NV12_RANGE_H
#define SP11_RGB_NV12_RANGE_H
#include <stdint.h>
static inline uint8_t sp11_rgb_y_to_video(uint8_t full)
{
    return (uint8_t)(16u + ((unsigned)full*219u + 127u)/255u);
}
static inline uint8_t sp11_rgb_uv_to_video(uint8_t full)
{
    const int delta=(int)full-128;
    const int mapped=delta>=0 ? (delta*224+127)/255 :
                                      -((-delta*224+127)/255);
    return (uint8_t)(128+mapped);
}
#endif
