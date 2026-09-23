# E004na: new opt-in V4L2 front1080/rear4K BT.601 tag physical candidate

NEW single-use unique source/ELF-locked candidate: never rearm
consumed E004my/E004mx/etc. Earlier original E004my successfully
proved actual front1080 gain-only Y preview/UID1000 app FPS,
rear4K NEON/UID1000 app FPS, exact native RGB sensor controls
restored, front->rear->off->quit, full 119-edge final neutral,
automatic protected Golden return and no GPU/thermal fault.
E004na retains all of that and only adds a metadata request
and exact V4L2 readback for front/rear native NV12 output:
SMPTE170M/YCBCR601/limited studio-range/XFER709. Pixel encoder
is unchanged from E004my (provisional BT.601-like YUV).

SP11 camera-free ACTUAL GStreamer synthetic HD/UHD decoder
selected BT.709 on unspecified NV12 caps but explicit BT.601
decoded matching existing software matrix. New UID1000
front/rear scene_probe must independently record actual
v4l2src negotiated colorimetry=bt601 and final I420 consumer
colorimetry=bt601; exact V4L2 VIDIOC_S_FMT echo required,
all strict native >=29fps whole-run and FOUR high-gain 30frame
windows required. If any caps/colorimetry/FPS/native sensor
restore or final-neutral check fails, original one-shot is FAIL
and NEVER rearm this identity; a read-only posthoc simulation
does not convert failed original physical acceptance into PASS.

Output metadata match cannot establish native sensor true
colorimetric primaries, calibrated white balance, Bayer/demosaic
fidelity, object detail, noise or full Windows ISP parity.
Normal maintained Golden camera and front/rear tone/temporal/
IR remain default OFF/unchanged, no OS sleep or native VBLANK/FPS
changes, original four optical RGB PNGs ONLY on same SP11
owner geoca private 0700/0600, never export photos/optical
pixels/RAW/image hashes/thumbnails to chat/Git/other hosts.
