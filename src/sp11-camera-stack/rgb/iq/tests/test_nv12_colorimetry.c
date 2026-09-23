/* Camera-free synthetic v4l2 metadata check: no ioctl. */
#include "../nv12_colorimetry.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
 struct v4l2_pix_format f;memset(&f,0,sizeof(f));
 assert(!sp11_rgb_nv12_confirm_bt601(&f));
 f.width=3840;f.height=2160;f.pixelformat=V4L2_PIX_FMT_NV12;
 f.bytesperline=3840;f.sizeimage=3840*2160*3/2;
 sp11_rgb_nv12_request_bt601(&f);
 assert(sp11_rgb_nv12_confirm_bt601(&f));
 assert(f.width==3840 && f.height==2160 && f.pixelformat==V4L2_PIX_FMT_NV12);
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
 return 0;
}
