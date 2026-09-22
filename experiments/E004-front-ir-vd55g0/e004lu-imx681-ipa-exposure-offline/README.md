# E004lu — bounded IMX681 fixed-frame software-IPA exposure (OFFLINE)

2026-09-23. Parent E004lt consumed physical processed-viewfinder experiment
passed six XRGB8888 frames for each real SP11 camera with full neutral
before/between/after. However SIX V4L2 SET_CONTROLS operations on IMX681
returned ERANGE, zero on OV13858; no per-control index was emitted by
libcamera and this is a reasoned source-level hypothesis, not an observed
control ID or proven physical fix.

SOURCE AUDIT: accepted native IMX681 3840x2160 mode has 3554 frame lines,
default 3546 exposure lines, margin 4, even two-line exposure step.
Its V4L2 EXPOSURE advertises hardware maximum 16777210, but its current
cluster try_ctrl rejects exposure > (2160 + VBLANK - 4) & ~1; default
VBLANK makes that maximum 3550. Pinned libcamera 0.7.0 Soft IPA AGC
configured exposureMax straight from the hardware maximum and therefore
was capable of requesting out-of-frame and odd exposures. In dark scenes,
a ten-percent increase from the default 3546 exceeds the actual 3550
frame cap. This is consistent with the repeated front ERANGE log, but
cannot exclude another control without a fresh observed per-control trace.

Maintained pure C++ header:
src/sp11-camera-stack/libcamera/sp11-imx681-fixed-frame-agc.h
SHA-256 af58a47d4a2101d97841c2933040bc94d8c5d2a31c46ada346d47e9501b2f997.
The header admits ONLY independently accepted IMX681 output height2160,
minFrameLength3554, exposure min4 and a hardware maximum >=3550;
unknown sensor modes fail closed. It caps Soft IPA exposureMax to 3550
without changing hardware VBLANK, sensor register programming, CSI
clock or frame rate, and quantizes the proposed AGC exposure to even
steps before both sensor control emission and retained AGC state.
OV13858 and all non-IMX681 paths are unchanged. This sacrifices very
long low-light exposure while the fixed 30fps frame period is preserved;
future variable FPS needs a separately validated frame-length handshake.

Apply to exact pinned clean libcamera 0.7.0 commit
b7854fd07d42168f099b5ce30d1702e0e0875bf5 AFTER E004lh, E004lm,
E004lo and the independent IMX681 gain-helper patch. Install this
maintained header into src/ipa/simple/ before building the patch
0001-imx681-fixed-frame-soft-ipa-agc.patch (SHA-256 d2c386ac760949147c6d169255759f735859adbd97b284e063ab8c77319a99f7).
The patch was regenerated and byte-for-byte reapplied against a FRESH
git-archive clean pinned soft_simple.cpp (not the dirty working
reference checkout). Its only code mutation is the IMX681 fixed-frame
Soft IPA exposure contract. The root-free scratch source/build was
never installed or granted camera access.

OFFLINE TESTS: standalone ARM64 g++ C++17 -Wall -Wextra -Werror -pedantic
ASan+UBSan strict unit: PASS, including 4000 exposure requests, odd
step, default3546, capped3550, and fail-closed unapproved frame modes.
Entire pinned guarded libcamera source build 359-target initial plan,
completed [245/245] resume after a missing historical E004lo lease
header was copied from its tracked experiment; 77 suite tests:45 OK,
1 expected failure,31 skipped,0 unexpected failures including IMX681
gain helper. 11 Python routing-policy tests PASS. Patch application
and cmp of reconstructed clean pinned file PASS.

The fix is NOT yet physically admitted. Next fresh unused one-shot
candidate must build libcamera from a separate root-sealed /var/lib
source path so the compiled IPA config cannot resolve to geoca-writable
scratch. Require both real cameras, exact XRGB8888, no front V4L2 ERANGE
in a longer short bounded session, distinct frame sequence/timestamps,
independent full neutral graph before/between/after and automatic Golden
return; any fault consumes the fresh identity. Never reuse E004lt.
This is not a Windows QC10C/ISP parity or production multiclient proof.
