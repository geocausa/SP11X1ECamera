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
suites and synthetic native full-frame packing tests pass. It was physically exercised in the fresh guarded E004mf/E004mg
one-shots; a raw histogram still cannot prove recognizable detail
or an optical black-level calibration.

## E004mg private local RGB optical proof — image usability still open

A new source-pinned E004mg physical one-shot captured real front1080p
and rear4K RGB PNGs **only on SP11** (`~/Pictures/SP11-Camera-Private-E004mg/`).
Numerical analysis of the locally downsampled images found front
luminance p99=9 (99.74% below20) and rear p99=0 (all below20):
physical frame delivery is proven but visually usable imagery is NOT.
Independent same-boot NV12 app Y p99 was 27/17 at baseline and 60/25
after bounded reversible visible RGB sensor gain. Native RAW10 full10
source and same-frame paired RAW8/NV12 checks passed. The RGB PNG and
NV12 studio-range Y values have different scales and can clip near
video black; no converter-only root cause or true optical black level
is established. Both photos are private and not committed/exported.
E004mg consumed/retired, Golden recovered. Prioritize source black
reference and supported exposure control, then opt-in offline-verified
tone mapping and a fresh guarded controlled-light recognizability gate.
A source-only optional NV12 nominal video-range output mapping has since
passed SP11 synthetic GStreamer dark-value round-trip and exhaustive
integer/opt-in publisher fake-device tests; without the flag, front/rear
converter ELFs remain byte-identical to their E004mg-era equivalents.
It has NOT been physically tested and does not compensate for the dark
rear native RAW sensor or establish colour/black/exposure calibration.

## E004mh physical opt-in video-range and private baseline/gain image gate

A completely fresh/consumed E004mh boot physically ran both source-locked
studio-range-enabled front1080/rear4K software publishers, ordinary UID1000
applications, same-frame RAW10/NV12 diagnostics, and bounded native sensor
gain/exposure with exact restore. Four original RGB PNGs remain ONLY ON
SP11 at `~/Pictures/SP11-Camera-Private-E004mh/` (0700/0600). All
normal STREAMOFF/native graph neutral/Golden return checks passed and
candidate assets were retired, IR off, no Linux OS system sleep.

Downsampled RGB PNG luma p99 front baseline/gain 22/51 and rear 15/20;
independent NV12 app Y p99 front 37/62 and rear 31/37. Real front
source RAW-upper8 p99 26→56.3333 and rear17→27. The baseline rear
RAW10 green is still tightly clustered around code64–70; that is NOT
a verified optical black offset, and amplified signal may include noise.
Earlier E004mg non-studio-range preview p99 front9/rear0 was captured
under separate uncontrolled morning light. Thus the synthetic range
fix is independently verified and physical studio-range images are no
longer numerically zero, but a matched scene luminance ratio and
recognizable visual detail remain UNPROVEN, especially at the rear.
Normal publisher release/default still excludes studio range opt-in;
no colour/AE/black-level calibration or Windows ISP parity is claimed.

Next, obtain a controlled visible-light target/black reference and
validate optical source/exposure plus a bounded noise-preserving tonal
processing proposal offline BEFORE a fresh camera one-shot; never reuse
E004mh. Do not substitute another delivery-only PASS for the usability
gate or activate protected IR/OS system sleep.

## E004wn fresh Windows oracle: current rear corner is rendered bright

The rear camera may physically face a darker, relatively featureless corner
(as reported by the user), so comparing front vs rear physical signal is NOT
an equivalent scene exposure test. To check that explanation, a new
single-use E004wn Windows-only numeric oracle sampled exact SP11 front1080
and rear4K colour WinRT NV12 at 11:16 BST, about 18min after E004mh
Linux. Windows rear mean Y=148.24–148.55, P01=119–120, P99=169,
with **zero** sampled Y below32, and 8x8 tile means std ~11.2. Windows
front mean Y~123.27–123.70. Both ExposureControl.Auto=true, nominal
ticks5000 (not a native sensor-register exposure readback). This
Windows rear capture is NOT similarly near-black to the recent Linux
rear app baseline Y P99=31/adjusted37 or Linux RGB PNG P99=15/20.

A dark/featureless corner alone is therefore insufficient as a factual
explanation for *both* platforms' current rendered output, but it remains
possible that lighting/direction changed or Windows automatic exposure
compensates for the corner. The capture times, raw/native sensor exposure
units, image processing and data summary statistics were NOT matched.
Do NOT diagnose sensor failure or calculate a cross-OS brightness ratio.
Use a deliberately fixed bright and dark physical target, confirm field
of view and illuminance in both boots, collect comparable native NV12
Y histograms plus Linux RAW10 channel and exposure/gain metadata, and
then test bounded automatic-exposure/tonal processing in a fresh guarded
Linux one-shot. E004wn task was retired and SP11 returned to protected
Golden; never reuse E004wn, E004mh or other consumed identity. IR OFF,
no Linux OS system sleep.

## E004mp bounded rear extra analogue gain: signal rises, usability still open

New E004mp one-shot ran source-locked front1080/rear4K RGB, UID1000 apps,
full10 RAW10 channel histograms, same-frame RAW-upper8/NV12 telemetry
and exact native control restoration. Only the **rear analogue gain target**
changed versus E004mh (256→512); rear trial exposure3200 and digital
gain2048 were unchanged, frame timing/FPS unchanged and IR OFF.
The rear source green0 RAW10 P01/P99 baseline64/70→gain73/140;
p99−p01 6→67, while ordinary-app NV12 Y p99 31→48 and private
RGB preview downsampled Y p99 15→30. The gain-dependent shift of P01
means full10 code64 is not a calibrated optical black value. More
spatial contrast MAY mean optical scene detail and/or fixed pattern noise.
Local-only 12x16-tile image brightness correlation rear baseline/gain
r0.806 and E004mh-vs-E004mp gain r0.977 suggests a repeatable pattern,
but cannot identify it as usable scenery or prove SNR/scene recognition.

All four original PNGs remain ONLY on SP11 at
`~/Pictures/SP11-Camera-Private-E004mp/` (directory0700/photos0600),
no pixel data/image hashes committed or sent. Candidate consumed and
retired after automatic protected Golden boot
`b3692bba-238a-4885-8f3b-9332c8284b51`, native neutral and clean
overlap guard. The rear native exposure current mode max is3206 lines,
and trial3200 is almost full-frame; longer exposure needs explicit
separate VBLANK/FPS verification rather than a silent control tweak.
Next controlled fixed-lit target/actual black/noise and per-gain
RAW10 scene checks must precede robust automatic exposure or tone
mapping. Windows E004wn rendered a much brighter rear at another time,
but scenes/time and statistics were not matched. Default/Golden camera
still not enabled, IR OFF, no Linux OS-level sleep.

## Camera-free fixed-frame envelope and temporal source preparation (after E004mp)

A read-only E004mp evidence validator now checks exact native V4L2
bounds, previous control readbacks/restoration and ordered full10
Bayer channel quantiles. Under the accepted current frame timings,
front exposure3546 leaves 4 lines vs active max3550 and rear3200
leaves 6 vs max3206. It explicitly REFUSES to promote an uncalibrated
p01 to sensor black or approve further native writes/AE/tone mapping
without a dark reference and a lit target. An independent camera-free
front/rear RAW10 two-frame temporal/spatial aggregate primitive has
passed synthetic constant/fixed-pattern/temporal-jitter tests but is
NOT integrated into live publishers and has captured NO NEW frames.
Stable spatial correlation can arise from sensor FPN as well as a
scene; temporal changes can reflect illumination flicker or motion.

Admission for the *next* physical one-shot is an actual distinguishable,
visibly lit target IN BOTH physical fields of view, a separate dark
reference, bounded timestamps/exact controls and private on-SP11 image
verification. Do not run another uncontrolled dark-corner gain trial
or silently change FPS/IR/Golden/Linux OS-level sleep. See
`src/sp11-camera-stack/rgb/iq/FIXED-TARGET-ACCEPTANCE.md`.

## E004wp fresh Windows oracle: rear receives ample rendered luminance

At 11:58 BST a **new** one-shot SP11 Windows Color VideoRecord NV12
oracle sampled eight 4K rear frames: Y mean149.15–150.41, P01 118–119,
P99 169–171, zero samples below64; 8x8 tile-mean Y std11.46–12.06
and horizontal64px/vertical32px mean absolute Y changes~3.3. The
front1080 mean Y124.87–125.19. WinRT RGB ExposureControl.Auto=true
for both; nominal ticks5000 is not verified equivalent to native
Linux sensor-register exposure. This independently reinforces fresh
E004wn Windows rear mean Y~148 at 11:16 BST, so Windows can render
the current corner *brightly*, with nonzero spatial contrast. It
cannot alone establish recognizable objects or sensor RAW scene SNR.
A 960x540 rear luma-derived grayscale PNG remains strictly LOCAL on
SP11 Windows user-private Documents E004wp folder (Geoca/SYSTEM/
Administrators ACL), NEVER exported/hash committed; user can inspect
it locally to confirm scene geometry. No Windows vs Linux same-time,
identical exposure/light/metrics experiment was achieved.

E004wp unique Windows identity was consumed, single-use task retired,
auto-return to protected Golden Linux verified at boot
`fe4bcab8-a209-4466-819e-0ce7fbeabc03`. No camera processes,
IR/illumination or Linux system sleep. Next meaningful Linux ISP/AE
quality test still requires a fixed visible scene and dark reference;
not another uncontrolled rear corner gain run.

## E004ms first real opt-in rear brightness near current Windows range

After E004mr failed pre-stream and was retired, a distinct new E004ms
source-pinned one-shot added durable root-private selector tracing and
successfully delivered actual front1080p/rear4K RAW-to-NV12 video to
ordinary UID1000 apps. Exact native RGB controls were restored,
source RAW10 paired/full10 and service/graph shutdown evidence passed,
IR OFF, no Linux OS system sleep. A **rear-only, opt-in** studio-range
Y preview LUT bypasses flat baseline and engages only when the bounded
rear exposure3200/analogue512/digital2048 produces sufficient sampled
luminance spread. The real rear ordinary app baseline meanY30.22–30.23,
p01=30, p99=31, tile std0.22; trial with live LUT meanY145.46–145.67,
p01=125, p99=167, tile std9.8–9.87. Root-private rear RGB PNG
aggregate meanY144.399/p99=165, no endpoint-clipped Y pixels; front
was NOT tone-adjusted. E004wp Windows current rear auto-exposed native
NV12 had meanY149.15–150.41/p99=169–171/tile std11.46–12.06.
Therefore Windows-like rear *rendered brightness* is physically possible
through Linux software; these different-time scenes and different
exposure controls do NOT prove color, recognizable detail, true SNR,
calibrated black, white balance, full Windows ISP parity, dynamic AE or
safe routine day-to-day camera integration. Y-only tone does not
recover genuinely absent source signal and can amplify sensor FPN.

E004ms fresh one-shot consumed and fully retired after automatic
protected Golden return boot
`5e400c52-4c3f-4c69-ab7e-19065f514527`; Golden normal output
remains unchanged and candidate tone default-OFF. Four original PNGs
remain user-private **only on SP11** at
`~/Pictures/SP11-Camera-Private-E004ms/` folder0700/photos0600;
no pixels, photos or image hashes exported. Future work: controlled
lit/dark optical RAW10 sensor-noise and color measurements, bounded
adaptive native exposure/gain within fixed-mode max3206 lines rear,
day/night/tone clipping/flicker safeguards, and a separate fresh guarded
end-to-end opt-in normal-service test before productionization. No
manual user-side reboot or photo inspection is required for the tests
and diagnosis accomplished here.

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

### 2026-09-23 E004kt Windows morning reference (consumed)

Fresh Windows WinRT NV12 CPU luminance scalar eight samples/camera gave mean Y front123.17–123.58 and rear151.48–151.90 with Auto=true nominal5000 ticks; no pixel exports/IR or control writes. Linux E004mf earlier morning baseline app p99 front27/rear17 (gain59/25) is NOT the same luminance statistic, time or controlled scene, so only a qualitative brightness discrepancy. The prior Windows E004ks reference was much darker under different lighting; do not infer a calibrated cause. Investigate source black level, Linux exposure controls and bounded tone mapping next. Windows returned Golden, inert future scheduled task retired, no default changes.
