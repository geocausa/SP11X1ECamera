# E004nc fresh real front/rear BT601 V4L2 DEFAULT normalized + UID1000 GStreamer caps trial

E004na and E004nb source-locked one-shots are consumed and fully
retired. E004nb independently measured S_FMT and G_FMT successful
1920x1080 NV12 colorspace=1(SMPTE170M), ycbcr_enc=0,
quantization=0,xfer_func=0. The Linux videodev2 UAPI explicitly
maps DEFAULT=0 trailing fields for this NV12 YCbCr colorspace to
601/limited/709. The old literal raw field equality was too strict
and failed before sensor streaming. NEW e004nc has an opt-in
fail-closed check for the EFFECTIVE UAPI defaults, requires the
V4L2 colorspace itself be explicitly SMPTE170M, the correct NV12
format, and rejects explicit 709/incorrect quantization/transfer.
No widening of original format dimensions, 29fps whole/per gain
window source, sensor exact control restore or safety gates.

This uniquely new candidate retains the previous front/rear
numeric request/S_FMT/G_FMT scalar logging for independent readback.
The actual independently unprivileged UID1000 v4l2src NV12 AND
ordinary I420 consumer must BOTH negotiate real colorimetry bt601
in front1080p and rear4K at baseline and gain. Neither a UAPI
normalization test nor synthetic GST proves that: if any observed
caps differ, full physical runner MUST FAIL, never relabel.
Also independently require front gain Y preview, rear NEON, real
RAW10 source/frame pairs, front->rear->off->quit selector, final
119-edge native neutral graph, automatic Golden return and no GPU
fault. The normal maintained Golden camera remains default OFF/IR
unchanged; all private images ONLY SP11 and NEVER send pictures,
RAW frames, pixel arrays, thumbs or photo hashes to chat/Git/other
hosts. This is a colour-space matrix-consistency trial, NOT a
calibrated white balance/colour chart/Windows ISP parity approval.
