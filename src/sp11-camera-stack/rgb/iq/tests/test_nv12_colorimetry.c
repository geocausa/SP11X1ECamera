/* Camera-free synthetic v4l2 metadata check: no ioctl. */
#include "../nv12_colorimetry.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
 struct v4l2_pix_format f;memset(&f,0,sizeof(f));
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.width=3840;f.height=2160;f.pixelformat=V4L2_PIX_FMT_NV12;
 f.bytesperline=3840;f.sizeimage=3840*2160*3/2;
 sp11_rgb_nv12_request_bt601(&f);
 assert(sp11_rgb_nv12_confirm_bt601(&f));
 assert(sp11_rgb_nv12_confirm_effective_bt601(&f));
 assert(f.width==3840 && f.height==2160 && f.pixelformat==V4L2_PIX_FMT_NV12);
 /* Real E004nb V4L2 S_FMT and independent G_FMT returned exactly
  * (SMPTE170M,DEFAULT,DEFAULT,DEFAULT): effective 601/limited/709. */
 f.ycbcr_enc=V4L2_YCBCR_ENC_DEFAULT;
 f.quantization=V4L2_QUANTIZATION_DEFAULT;
 f.xfer_func=V4L2_XFER_FUNC_DEFAULT;
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 assert(sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.colorspace=V4L2_COLORSPACE_REC709;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.colorspace=V4L2_COLORSPACE_DEFAULT;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.colorspace=V4L2_COLORSPACE_SMPTE170M;
 f.ycbcr_enc=V4L2_YCBCR_ENC_709;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.ycbcr_enc=V4L2_YCBCR_ENC_DEFAULT;
 f.quantization=V4L2_QUANTIZATION_FULL_RANGE;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.quantization=V4L2_QUANTIZATION_DEFAULT;
 f.xfer_func=V4L2_XFER_FUNC_SRGB;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.xfer_func=V4L2_XFER_FUNC_DEFAULT;
 assert(sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.pixelformat=V4L2_PIX_FMT_YUYV;
 assert(!sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.pixelformat=V4L2_PIX_FMT_NV12;
 assert(sp11_rgb_nv12_confirm_effective_bt601(&f));
 f.colorspace=V4L2_COLORSPACE_REC709;
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 f.colorspace=V4L2_COLORSPACE_SMPTE170M;
 f.ycbcr_enc=V4L2_YCBCR_ENC_709;
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 f.ycbcr_enc=V4L2_YCBCR_ENC_601;
 f.quantization=V4L2_QUANTIZATION_FULL_RANGE;
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 f.quantization=V4L2_QUANTIZATION_LIM_RANGE;
 f.xfer_func=V4L2_XFER_FUNC_SRGB;
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 puts("RGB_PROVISIONAL_BT601_VIDEO_RANGE_V4L2_METADATA_CAMERA_FREE=PASS");
 puts("SP11_NV12_REAL_V4L2_DEFAULT_0_COMPONENTS_MAP_601_LIMITED_709_NEGATIVE_REC709_AND_UNSPECIFIED_REFUSED=PASS");
 return 0;
}
