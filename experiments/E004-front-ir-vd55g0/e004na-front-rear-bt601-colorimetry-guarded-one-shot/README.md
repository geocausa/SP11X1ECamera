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


## Pre-arm source asset omission discovered and guarded repair

Initial unarmed 98ad08b staging ran camera-free software tests,
registered an experimental boot/service but did NOT arm the boot,
reboot SP11 or access a real camera. Independent mandatory pre-arm
asset check found that install-unarmed.sh had accidentally failed
to copy the brand-new root validator validate_bt601_live.py, though
its source was committed and the immutable original run-once.sh
correctly invokes that file. Arming would have produced a false
physical FAIL after stream; no such trial has occurred.

The installer and arm preconditions were corrected BEFORE arming,
and repair-unarmed-validator-asset.sh was separately source-pinned
with an exact OLD expected HEAD, verified active Golden/no camera,
no arm/consumption, every old stage SHA, same front/rear ELF and
runner, then ONLY installed the missing validator, regenerated the
complete root/private-boot/user-service SHA manifest and advanced
EXPECTED-HEAD to the new committed source. This is a unique
UNARMED staging fix, NOT a reused candidate boot or a retroactive
physical pass. No native camera controls or device modules were
touched in the pre-arm repair; full physical end-to-end acceptance
remains to be checked after a deliberately armed one-shot.


## 2026-09-23 E004na actual physical outcome: FAIL before sensor streaming

The distinct source-locked 0a8882f candidate boot
25434aee-c0fb-40ba-8128-62ffb6984227 was attempted ONCE.
Its original first FRONT publisher called VIDIOC_S_FMT on the
temporary v4l2loopback output, then failed the strict new
BT.601 exact-metadata readback. Original stderr:
E004NA_V4L2_BT601_NATIVE_LOOPBACK_S_FMT_COLOUR_TAG_MISMATCH;
captured=0 published=0, so neither front nor rear produced
a real native source frame, the ordinary UID1000 front app
received zero, the selector failed closed and the true live
front/rear GStreamer negotiated colour caps were NEVER observed.
The original pixel/fps/neutral release gates were not completed.
The new physical metadata trial is a FAIL, not a successful fix.

Crucially, the new opt-in implementation logged only a generic
mismatch before exiting, not actual returned integer colours:
the specific field(s) not echoed, and why, remain UNKNOWN.
The earlier source-only inspection of v4l2loopback v0.15.3
showed valid explicit colorspace accepted at a code location;
it did not prove transfer function, quantization, YCBCR encoding
or the actual IOCTL echo. Do NOT claim V4L2 driver inability,
colour accuracy, successful live colour fix or altered camera
FPS from this failed pre-stream experiment. Front/rear original
optical photos did not exist for E004na; previous SP11-local
private originals remain untouched.

SP11 successfully rebooted itself into protected normal Golden
Linux boot c6312e00-f579-4ba2-a276-365fc311ce1f with no
matching GPU hangcheck/GMU/Adreno ring, panic or thermal event
in the failed candidate kernel journal; no physical user
intervention. The already-consumed unique E004na root, boot,
GRUB and systemd assets were fully RETIRED under Golden, no
camera devices/modules/processes remain, IR and normal camera
settings unaffected. It must NEVER be rearmed. Future analysis
should first inspect the exact loopback V4L2 API and source
in camera-free mode and create a candidate that LOGS the actual
S_FMT returned colour fields BEFORE the rejection, rather than
merely assuming a valid colorspace implies all metadata echoes.
Only a fresh single-use source-locked boot could test that in
real hardware, without relaxing strict accepted FPS or daily
default camera protection.

This failure does not invalidate the previous distinct E004my
original fully passed real front1080/rear4K speed/brightness/
native-neutral and automatic Golden return result.
See RESULT.json, evidence/front-SERVICE-STDERR.txt,
evidence/FRONT-FIRST-APP.jsonl,
evidence/FAILURE-INTERPRETATION.txt,
evidence/CANDIDATE-KERNEL-ERROR-SCALARS.json and RETIREMENT.txt.
