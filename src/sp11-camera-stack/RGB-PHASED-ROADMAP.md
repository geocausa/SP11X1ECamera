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

## E004md actual low-light gain response (2026-09-23)

E004ma selector, E004mb morning dark-scene probe and E004mc same-frame
RAW/NV12 source diagnosis are completed, archived and retired. A newer
unique E004md guarded trial measured physical front source RAW8-upper
p99 21→36 and uid1000 NV12 app Y p99 20→34 after supported gain edits.
The rear source p99 rose 17→21 and app p99 16→20 after supported
gain and bounded exposure edits. Both sensors had exact baseline
control readback restoration and controlled publisher stop143. This
confirms real gain-response data, NOT visibly recognizable images,
calibrated RAW black level/colour, normal dynamic 3A, or Windows parity.
The enclosing E004md runner FAILED due to a stale predecessor-status
string check AFTER inner tests; final independent candidate graph/FD
checks did not run. Automatic Golden recovery verified and all E004md
assets retired. Never retry that identity. Before any fresh guarded
physical trial, run tools/camera-validator-contract.py on its fresh
runner/paired validator and prevent stale cross-experiment literals;
prioritize offline gain/exposure policy and controlled-lit RGB scene
visibility with source-format/black-level checks. Keep IR off and
never initiate OS system sleep. Evidence: E004md RESULT.json.

The camera-free standalone full-precision RAW10 primitive at
`rgb/iq/raw10_unpack.h` preserves both previously discarded low bits
and validates the native front/rear packing and rear stride padding.
It is unit-tested but not integrated into the live publishers. In a
FRESH guarded lit-scene candidate, test real black-level/channel
statistics before any auto-exposure or tone-curve claim; neither
this offline primitive nor E004md gain-response numbers establish
recognizable images.

The maintained direct publishers now contain a default-disabled
`SP11_CAMERA_ALLOW_RAW_PROFILE` diagnostic for sparse same-frame full
10-bit R/G0/G1/B source statistics. Both front/rear fake-device lifecycle
suites and synthetic native full-frame packing tests pass. This has NOT
been physically accepted; only an entirely fresh one-shot boot can
measure real sensor data. A raw code histogram alone cannot prove
recognizable scene detail or optical black-level calibration.

## Software RGB service integration in progress (2026-09-23)

Maintained source:
\`src/sp11-camera-stack/rgb/service/session.py\` defines a
single-owner front/rear session state machine. It requires an
injected real backend to prove a fresh authorized camera boot and
exclusive lease, complete neutral/selected native graph before/after
each camera, actual publisher STREAMOFF and process exit, no remaining
source/client FDs and IR-off readback. Unsafe/uncertain operations
poison it: no speculative rollback or further link writes. Fifteen
camera-free simulated-device lifecycle/failure tests pass. **This is
source-only, not a functional installed camera service.** The real
kernel-backed adapter and guarded physical multi-app acceptance
remain necessary.

Both maintained RAW→NV12 direct publishers now support an explicit
\`SP11_CAMERA_ALLOW_CONTINUOUS=1\` compile-time opt-in coupled to the
separate one-shot boot token. Normal/default builds DENY the
\`continuous\` argument. The experimental mode has a four-hour hard
deadline and returns STOPPED=143 only after intentional termination
and verified STREAMOFF. Nine fake-device scenarios per camera pass,
including intentional signal-stop after four published buffers;
**continuous capture has NOT yet been live-tested on SP11**.
Do not claim a persistent daily camera service until the new mode
and controller/backend are separately accepted on real front1080p
and rear4K hardware, through ordinary application readers.

## Stage 1 real-software-publisher service integration in progress

E004ly separately demonstrated physical 1080p-front and 4K-rear
software RAW→NV12 capture/publication for about 115s each, with
same-invocation uid1000 app first/reopen/SIGKILL/recovery, verified
STREAMOFF and full native media graph neutral between/after.
The one-shot was CONSUMED and RETIRED and Golden returned safely.
Actual sampled frames were nearly black; no calibrated image quality.

The next maintained backend implementation lives in
src/sp11-camera-stack/rgb/service/{session.py,media_backend.py,
rgb_device_backend.py,candidate_owner.py,candidate_driver.py}.
35 camera-free injected-failure tests pass. This joins the exclusive
RGBSession with the exact Media Controller route policy, pinned
root-only candidate owner, live source-format configuration and
verified publisher stop contract. Fresh distinct E004lz physically
validated this maintained controller against both actual cameras at
front1080p/rear4K, uid1000 first/reopen/kill/recovery app sessions,
stop143/STREAMOFF and full graph neutrality. E004lz was consumed,
retired and Golden returned. This proves bounded real hardware
integration, NOT a default or genuinely opt-in enduring normal-use
service; controlled-lit image quality and general-client/long-run
reliability still require acceptance. Do not count an opt-in one-shot
as a daily service.

Next acceptance candidate E004ma exercises root-private
selector.py/rgbctl.py opt-in front/rear/off/quit commands as a
separate process from the three normal uid1000 app opens and one
killed/recovered app per camera. It retains both discoverable named
front1080p/rear4K endpoints, but only one real source is active.
A source-only selector is not a production normal-user camera
interface until actual guarded optical test and duration/IQ/user
permissions are independently accepted. Direct root-only
selection is a temporary administrative interface, not automatic
app-driven routing or Windows camera UX equivalence.

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

### 2026-09-23 E004mf visible-light measurement (consumed)

Normal front1080 and rear4K UID1000 application sessions, RAW10 full-bit per-channel scalar and same-frame RAW8/NV12 profile passed. Morning baseline/gain Y p99 front27/59, rear17/25; rear baseline RAW10 green p99 ~70 is clustered near ~16–18 upper8, front green p99 ~119. E004mf Golden returned and assets retired. No image pixels retained, so recognizable scene, calibrated black, colour or Windows IQ parity remain unproven; next attempts must use a new unique guarded identity and never activate IR or Linux OS sleep.
