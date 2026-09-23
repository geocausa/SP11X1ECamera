# SP11 RGB cameras — software-first plan and optional hardware ISP

Decision: 2026-09-23. Current scope: front IMX681 and rear OV13858
visible-light RGB cameras. Finish and validate the Linux
software-processing RGB stack FIRST, then show the user actual results
and decide TOGETHER whether to pursue the Qualcomm hardware-ISP
path to seek Windows-like image quality. Do not silently turn hardware
ISP parity into a requirement for the first usable RGB release.
Preserve the substantial existing Qualcomm ISP/QC10C/derived IQ work
for that later decision. Protected IR/Windows Hello is separately
deferred and is NOT an RGB-only release blocker. IR illumination
remains prohibited.

## Planning snapshots — NOT objective completion metrics

As of 2026-09-23, the prior conversation estimated approximately
65–70% for a usable software-processing front1080p/rear4K RGB
solution, and 30–40% for a usable Qualcomm native hardware-ISP RGB
solution overall. These are subjective engineering estimates, not
measured work completion, schedule promises or Windows image-quality
parity percentages. Front hardware ISP has more evidence than rear;
neither backend has a measured Windows-visual-parity percentage.

Do not conflate the evidence: earlier real optical Linux 1920x1080
front and 3840x2160 rear NV12 to independent standard V4L2 apps
was through a separate RAW-to-NV12 SOFTWARE conversion route
(E004kr/E004kp/E004kw). The newer pinned libcamera software ISP
delivered only 640x480 XRGB8888/sRGB processed output, albeit
3600 frames in four front/rear/front/rear independent processes,
with all four native graphs neutral afterwards (E004lx). The
libcamera test did NOT prove high-resolution processed video,
normal-user access or permanent daily-use camera service.
Both reopened libcamera streams had a roughly 1s early-frame
pause even though subsequent steady cadence passed.

## Stage 1 — current priority: usable Linux software RGB

Acceptance for the RGB-only first usable release:
1. Integrate ONE tested software-processing path delivering genuinely
   captured, correctly formatted front 1920x1080 NV12 and rear
   3840x2160 NV12 through ordinary independent unprivileged
   application-facing camera endpoints. The earlier RAW-to-NV12
   converter may be productionized instead of requiring libcamera
   Soft ISP to reach those resolutions, PROVIDED measured image
   quality, throughput and integration are sufficient. Do not
   substitute the libcamera 640x480 preview for native resolution.
2. Implement selectable named front/rear endpoints, safe exclusive
   camera/media-route ownership, no concurrent conflicting backends,
   predictable service start/stop, true STREAMOFF/neutral shutdown,
   close/reopen and error/crash recovery, and safe rollback.
3. Verify actual 1080p/4K app-delivered frame size, useful frame rate,
   latency, CPU/thermal performance and meaningful image quality in
   controlled lit scenes (exposure, colour, orientation, noise and
   detail). Diagnose and record the observed approximately 1s
   early-frame reopen interruptions: steady-state success is NOT
   proof of seamless switching. Test sustained capture and repeated
   normal-powered-on service lifecycle.
4. Treat any initial release as RGB-only, opt-in/non-default until
   the functional and hardware safety gates pass. Do not claim
   exact Windows ISP image parity or protected Windows Hello parity
   from successfully delivering 1080p/4K software RGB frames.

All physical tests still require fresh root-private source-pinned
single-use guarded candidates, verified Golden recovery, full neutral
media-graph checks, IR OFF, and no reuse of consumed identities.
SP11 Linux OS-level suspend/standby/resume/hibernate/hybrid sleep
is NOT IMPLEMENTED RELIABLY and is excluded from camera tests;
do not label this platform limitation a camera failure. Normal
guarded reboots and ordinary sensor stop/reopen are allowed.

## Decision gate — when software RGB acceptance passes

Report the measured real front1080p/rear4K output, visual quality,
CPU/latency/FPS, reopen behaviour and remaining limitations to the
user. Ask whether to (a) retain software-only processing, (b)
prioritize Qualcomm native hardware ISP for Windows-like image
quality, or (c) validate and offer both as mutually exclusive,
user-selectable processing backends. This decision is NOT YET MADE;
do not automatically pursue a hardware-ISP build as a prerequisite
for shipping the first usable software RGB release.

## Stage 2 — optional Qualcomm hardware ISP, after user decision

If selected, validate the existing front native 2560x1440 QC10C
compressed TP10-UBWC ISP output with an exact supported memory
layout, import/decompression or separately proven native linear
output; check colourimetry and buffer synchronization. NEVER treat
QC10C compressed output as Bayer RAW10 or NV12. Integrate existing
derived native IMX681 IQ/AWB/3A work with actual live output pixels,
develop and verify the corresponding rear hardware ISP output/tuning
path, and compare measured front1080p/rear4K results against Windows
on the SAME SP11 under matched lit scenes, including exposure,
colour, white balance, detail, noise, motion, dynamic range, FPS
and latency. Earlier dark, unmatched Windows/Linux samples cannot
establish parity. Only offer optional user backend selection if BOTH
are independently production-safe with strictly exclusive routing.

Hardware-ISP path means a NATIVE LINUX implementation controlling
the same Qualcomm hardware that Windows uses, not running Windows
drivers inside Linux. RGB software usability, optional Windows ISP
visual parity and protected IR/Hello remain three DISTINCT outcomes.

Evidence:
- experiments/E004-front-ir-vd55g0/e004lx-guarded-startup-steady-rgb-reopen-one-shot/RESULT.json
- experiments/E004-front-ir-vd55g0/e004kr-direct-dual-stop-session-one-shot/
- experiments/E004-front-ir-vd55g0/e004kp-direct-rear-mmap-one-shot/
- src/front-imx681/desktop-output-contract.json
- src/front-imx681/userspace/iq/README.md
- src/sp11-camera-stack/rgb-desktop-output-contract.json
- src/sp11-camera-stack/READINESS.md
