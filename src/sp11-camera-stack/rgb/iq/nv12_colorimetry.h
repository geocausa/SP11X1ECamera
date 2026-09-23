/* SPDX-License-Identifier: MIT
 * Candidate ONLY: metadata matches current provisional BT.601-style
 * 8-bit RGB -> YUV video-range coefficients, NOT sensor colour accuracy.
 * Existing normal camera output remains unmodified unless explicitly opted in.
 */
#ifndef SP11_RGB_NV12_COLORIMETRY_H
#define SP11_RGB_NV12_COLORIMETRY_H
#include <time.h>
#include <linux/videodev2.h>
static inline void sp11_rgb_nv12_request_bt601(struct v4l2_pix_format *p) {
    p->colorspace=V4L2_COLORSPACE_SMPTE170M;
    p->ycbcr_enc=V4L2_YCBCR_ENC_601;
    p->quantization=V4L2_QUANTIZATION_LIM_RANGE;
    p->xfer_func=V4L2_XFER_FUNC_709;
}
static inline int sp11_rgb_nv12_confirm_bt601(const struct v4l2_pix_format *p) {
    return p->colorspace==V4L2_COLORSPACE_SMPTE170M &&
           p->ycbcr_enc==V4L2_YCBCR_ENC_601 &&
           p->quantization==V4L2_QUANTIZATION_LIM_RANGE &&
           p->xfer_func==V4L2_XFER_FUNC_709;
}
#endif
