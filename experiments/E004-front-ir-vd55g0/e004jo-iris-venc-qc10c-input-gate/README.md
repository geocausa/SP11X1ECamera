# E004jo — same-machine Iris encoder input and QC10C front-camera gate

2026-09-20. Parent `aa29aa9`. **Read-only Golden source audit**. No camera/frame capture, codec load, media format IOCTL, boot, installation, Windows intervention or IR illumination. This extends E004jj's decoder-direction check to the other possible shortcut: using a hardware encoder on front-camera QC10C and decoding the resulting video into ordinary linear NV12.

## Source-locked evidence from the current SP11 Golden Linux kernel

The installed kernel's `/lib/modules/$(uname -r)/source` resolves to the Golden v33-derived kernel source tree. Its Iris encoder `drivers/media/platform/qcom/iris/iris_venc.c` has SHA-256 `4b50d72b2bdc0804ab2a5a5367fd0fa8a23840aaad575c3e117664e6d54a1b03`. Exact original `iris_venc_formats_out` input table lists **only NV12 and QC08C** for `V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE`. It does **not** include captured front QC10C/TP10 UBWC or linear P010. `iris_venc_formats_cap` contains H264 and HEVC as encoded outputs. The driver's `find_format()` maps encoder `VIDEO_OUTPUT_MPLANE` to this input table and rejects unknown formats; do not confuse the compressed codec output with a compressed-pixel input.

Five source-identity/direction/read-only tests passed on the *actual installed source link*. There was **no runtime V4L2 encoder `VIDIOC_ENUM_FMT` probe or QC10C hardware submission**. These tests establish that the **currently installed Golden Iris encoder source does not expose QC10C as supported input**, not that no other hardware path or future driver could convert it.

Separate upstream July 2026 Iris discussion still lists NV12/QC08C as encoder raw inputs:
https://lists.openwall.net/linux-kernel/2026/07/07/2805
A Qualcomm July 2026 QC10C format-selection fix concerns the **decoder capture/output** direction, not a direct camera-QC10C hardware encoder input:
https://lists.openwall.net/linux-kernel/2026/07/10/157

## Practical front-camera implication

A proposed `captured QC10C → Iris hardware VENC → encoded H264/HEVC → Iris VDEC NV12` workaround is **not admitted by this machine's installed Iris VENC input format list**. Nor can one reinterpret QC10C as the advertised 8-bit compressed QC08C or inject it as an H264/HEVC bitstream (separate E004jj). This is an important fail-closed check; blindly feeding compressed camera memory into the wrong interface would not demonstrate decoded RGB video.

The existing separately proven IMX681 27 physical QC10C buffers, 1080p **Windows** front NV12 frame-handle baseline and blocked **Linux** native front NV12 image are unchanged. Keep pursuing exact X1E80100 ISP linear Y/C output and proper UBWC mode reset authority, or a *separately version-matched, validated* TP10 UBWC decompressor/GPU import whose metadata, 10-bit pixels and reference-image fidelity can be independently checked. Do not use a synthetic front demo or a guessed encoder format to claim Windows parity.

Replay without activating any hardware:

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jo-iris-venc-qc10c-input-gate \
  -p test_iris_venc_input.py -v
```
