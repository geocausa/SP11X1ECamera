# E004nb: fresh opt-in BT601 pre-stream real V4L2 S_FMT / G_FMT numeric readback

The distinct prior consumed E004na boot FAILED before sensor STREAMON:
front virtual NV12 output format returned a non-identical colour
metadata tuple but only a generic mismatch was logged. It captured
ZERO frames, was retired after automatic protected Golden return.
Root cause and which fields the V4L2 loopback driver returns were
UNKNOWN. Never rearm E004na or prior consumed identities.

E004nb is a NEW separately source-locked guarded single-use candidate.
Its sole material change is a metadata-only pre-stream scalar readback
of the exact requested S_FMT, returned S_FMT, and independent G_FMT
values for front/rear; no photo/pixel/tile/thumb/hash exported. The
strict existing failure gate remains unchanged: do NOT automatically
accept an unknown or 709-tagged consumer stream as correct BT601.
On mismatch the publisher exits before native sensor streaming,
original guarded runner records FAIL and single-use identity is
consumed; preserve numeric evidence and automatically return Golden.
If all fields really echo, require full original front1080/rear4K
ordinary UID1000 app/color caps/29fps each gain window/final neutral
GPU/Golden checks. Any captured private photos stay ONLY SP11
geoca0700/photos0600; none expected if same pre-stream failure.
Normal Golden camera/IR/nonnative DSP configuration unchanged.

## 2026-09-23 actual E004nb outcome: numeric pre-stream colour fields measured

Single-use candidate boot0c425045-b8a0-4b6d-99ec-289521f5f419
confirmed the FIRST FRONT temporary V4L2 output 1920x1080 NV12
S_FMT REQUEST colorspace=1 (SMPTE170M), ycbcr_enc=1 (601),
quantization=2 (limited), xfer_func=1 (709). Both ACTUAL S_FMT
RETURN and a SEPARATE VIDIOC_G_FMT RETURN success rc=0 retained
colorspace=1 but returned ycbcr_enc=0, quantization=0,
xfer_func=0. All dimensions/fourcc/stride/sizeimage unchanged.
The original literal four-field equality rejected BEFORE sensor
STREAMON, zero physical front/rear source or ordinary app frames,
zero optical photos. It is a genuine original runner FAIL, not a
performance or sensor defect. The checked-in Linux videodev2.h API
explicitly defines 0 as DEFAULT for all three; for an NV12
YCbCr stream with SMPTE170M, its default maps independently to
601 encoding, limited range and 709 transfer. This is a clear
representation mismatch in the test, NOT yet verification that
ordinary real GStreamer v4l2src/consumer negotiated BT601.

The candidate kernel showed no new GPU hang/panic/thermal event.
The host automatically returned to protected Golden Linux boot
3361fa4f-2171-4938-ab4c-68e368df9b6b; E004nb consumed
NEVER REARM, all experimental assets retired and Golden camera/IR
defaults unchanged. Next source-only tests must accept the V4L2
standard effective DEFAULT semantics only when explicit
SMPTE170M/NV12 geometry and all mapped components agree, never
blindly accept missing/Rec709 tags or relax strict actual normal
UID1000 app BT601 caps and 29fps/frame-gap/neutral quality gates.
Evidence: RESULT.json and evidence/front-SERVICE-STDERR.txt.
