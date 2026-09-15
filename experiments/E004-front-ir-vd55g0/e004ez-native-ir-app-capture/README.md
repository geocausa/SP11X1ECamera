# E004ez: stock libcamera packed monochrome capture

Unchanged E004ex sensor/CAMSS modules, DT and firmware. One fresh one-shot boot,
one stream through the installed Ubuntu cam application, no V4L2 fallback stream.
Discover/inventory the camera, cache the known 1000-line exposure and unity gains,
then request exactly 644x604 R10_CSI2P with strict formats and 16 completed requests.

Use the video role because libcamera 0.7.0 classifies packed monochrome R10_CSI2P
as ColourEncodingYUV; the samples are still the sensor's unconverted 10-bit data.
This is the exact format advertised in E004ey. No Bayer format substitution,
virtual device, root application, custom camera service or library patch.

The application owns buffer allocation, request queueing, start and stop. The
harness performs no streaming ioctl. Require 16 consecutive completed sequences,
full byte counts, requested/applied controls, clean kernel, stop and autosuspend.
Save stock application debug logs and metadata. Bound capture to 20 seconds and
return to Golden on success or failure. Retire the identity; never retry it.
No scene-quality or processed-video claim follows from this transport gate.

## Result

PASS: stock cam captured all 16 consecutive full frames (7,885,824 bytes)
through libcamera, with no fallback capture client. Applied 1000-line exposure
and unity gains matched, kernel health passed, stop and autosuspend completed.
Golden restored and identity retired. Crop/helper/processing warnings remain;
this proves bounded unconverted application capture, not processed video or
scene image quality.
