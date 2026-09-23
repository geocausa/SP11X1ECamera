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
/* V4L2 API permits the optional enc/range/xfer fields to be zero,
 * meaning DEFAULT derived from the non-default colorspace. E004nb
 * actually read back (SMPTE170M,0,0,0) in BOTH independent ioctls.
 * Do not interpret 0 as undefined, do not accept default colorspace,
 * Rec709 primaries, non-NV12, full quantization or arbitrary fields.
 * A future real user app MUST independently negotiate bt601 on both
 * V4L2 input and rendered consumer, not merely pass this helper.
 */
static inline int sp11_rgb_nv12_confirm_effective_bt601(
            const struct v4l2_pix_format *p)
{
    if (!p || p->pixelformat!=V4L2_PIX_FMT_NV12 ||
        p->colorspace!=V4L2_COLORSPACE_SMPTE170M)
        return 0;
    const unsigned enc=p->ycbcr_enc?p->ycbcr_enc:
           V4L2_MAP_YCBCR_ENC_DEFAULT(p->colorspace);
    const unsigned quant=p->quantization?p->quantization:
           V4L2_MAP_QUANTIZATION_DEFAULT(0,p->colorspace,enc);
    const unsigned transfer=p->xfer_func?p->xfer_func:
           V4L2_MAP_XFER_FUNC_DEFAULT(p->colorspace);
    return enc==V4L2_YCBCR_ENC_601 &&
           quant==V4L2_QUANTIZATION_LIM_RANGE &&
           transfer==V4L2_XFER_FUNC_709;
}
#endif
