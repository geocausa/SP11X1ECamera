## 2026-10-10 front lit-chart run: request cancellation blocker; all retired

SP11 front now user-aimed at SP7. Independently written fixed grey/RGB chart
ran throughout Linux front-meter02 and fresh Windows-front03 captures with SP7
brightness unchanged26percent. No lux measurement or real-illuminant AWB claim.

Front02 FAILED after158/160 output requests: requests96/128 (the analogue gain
changes) were cancelled, three exposure groups reached sensor readbacks, then
standard cam waited until40s timeout. Kernel queue stopped1190 completions with
error0, critical signatures0, automatic Golden returned. Identity consumed,
retired, service/timer disabled and watchdog static/untriggered; firmware restored
absent. Never retry02. Timing-horizon admission is the source-derived suspected
cause; add explicit rejection diagnostics and preserve valid pending requests
until a safe delayed-control slot, keeping the two-frame association guard.

Partial original pixels remain SP11: baseline Y3.30/raw green751.3; longer exposure
Y3.65/green827.0; gain response unqualified because those requests cancelled.
Windows-front03 PASS: eight unique native2560x1440 NV12 samples, three private
snapshots, normal automatic controls, clean stop and task unregistered. Y26.32..
26.36. Same-SP11 original-byte comparison reproduces metrics, but coarse scene
correlation only0.24 baseline/0.64 longer exposure, below0.95 gate. No matched
photometry, tone/color calibration or Windows image-quality parity follows.

Golden783cc2d6-4267-4193-ad35-2c6b184de931 restored; next_entry empty, camera idle.
Windows partition unmounted after strictly read-only comparison. All960 older
control-response02/03/04 NV12 originals byte-for-byte verified in private lossless
archives, five loose representatives retained per run. Recovered3.79GB; current
free about3.8GB after new capture. Future full-series analysis must restore old
archives to a fresh private directory. No pixels, spatial arrays or image hashes
exported; no OS power policy changes. No new AE enabled.

NEXT fix native front valid-control cancellation, then qualify sensor/input,
statistics black/gain and ISP brightness using the lit reference. Continue native
kernel/libcamera/IPA with independent tuning and upstreamable sources; loopback
remains optional. Rear66 qualifications retained. Evidence:
docs/FRONT-METER02-FAILED-20261010.json,
docs/WINDOWS-FRONT03-LINUX-METER02-PARTIAL-20261010.json,
docs/FRONT-EVIDENCE-STORAGE-20261010.json.
Earlier entries are historical; totals still require reconciliation after59.

## 2026-10-10 native direction: rear AE qualified; front quality blocker isolated

Native Linux sensor/CAMSS/ISP kernel + libcamera pipeline/IPA remains the goal,
front and rear RGB with Windows quality/function parity and redistributable
upstream patches/tuning. Optional loopback bridge is preserved, not the milestone.

Rear66 passes400 real4K NV12 requests/400 compact QXA2 statistics joins, five
acknowledged AE proposals and six actual sensor-register receipts. Raw target
converges, callback29.9705fps, no>50ms gaps, all four STOPs/DMA/cache/owner/arena
release pass, hazards0. Measured63 chart tone/CST retained. Engineering12000
target and same-exposure metadata still uncalibrated; no general Windows parity.
66 consumed/retired/unarmed; never retry. Evidence REAR-COMPACT-AEC66-HARDWARE.

Front-meter01 replaces the active IPA historical vendor float/checkerboard with
independently written raw Gr/Gb sum/count mean.1980 samples/channel,1024 regions.
G++/Clang++239 assertions/117 negatives each;10 libcamera tests pass including
actual mapped-buffer IPA/control/helper;two general test-device checks SKIP.
Hardware160 real2560x1440 NV12 frames at29.9971fps, all5 clustered known-register
readbacks and160 applied metadata match,165 completions stop cleanly, neutral
graph, sensors suspended, hazards0. Output Y3.13 baseline/4.57 analogue16x;
raw green714.2->628.2 with gain. Do not infer monotonic optical gain or enable
blind AE on this meter. Raw scale/black/target and current front scene unknown.

Fresh Windows-front02 selected exact2560x1440 nativeNV1230/1, eight distinct
timestamps/three private snapshots, normal automatic controls unchanged, clean
stop, task unregistered. Y10.943..11.136, also dim. Private original-byte metrics
reproduce saved scalar results; coarse scene correlation negative/about-0.21.
Cross-boot scene/lighting/control equivalence is unproven. The older bright
Windows reference is not tonight's reference. No covered-lens/night/driver
brightness diagnosis or parity pass follows from these captures.

All three identities consumed/retired/do-not-retry. Golden restored
5bc9215f-59f0-4157-aa61-5f945aab931f, protected hashes/default unchanged,
next_entry empty, camera units disabled/inactive and no loaded camera driver.
Windows partition unmounted after strictly read-only comparison. All160 front
originals remain byte-for-byte recoverable in same-SP11 root-only lossless archive,
with five representative originals retained; about1.20GB free. No pixels/spatial
arrays/image-derived hashes exported. No OS sleep/power-policy changes.

NEXT front raw/statistics black-level and gain-domain interpretation with credible
controlled illumination/optical response before automatic exposure; rear target/
clipping/AWB and fresh Windows quality calibration; independently replace private
profile dependencies and experimental ABI. Full stack/upstream release incomplete.
Evidence: docs/FRONT-METER01-HARDWARE-20261010.json,
docs/WINDOWS-FRONT02-LINUX-METER01-20261010.json and
docs/NATIVE-UPSTREAM-NEXT-20261010.md. Historical totals only verified through59.
Earlier entries are historical.

# Native front normal-AEC metering

The active native IPA uses an independently written sum/count reduction over
all 1024 regions. Four channel sample means are retained by the pure decoder;
the current scalar callback is the equal Gr/Gb mean. The declared fixed mode
requires1980 samples/channel,34-bit sums,zero reserved sum bits and81920bytes.
Failures leave output unchanged. No Bayer array or pixels leave SP11.

This replaces the active path's historical OEM float scaling/checkerboard and
colour weighting. The older bounded-envelope helper remains historical and its
tests keep their previous meaning. No black level, full scale, optical target,
automatic controls or Windows quality parity is inferred.

Fresh front-meter01 will bracket exposure1000/3546/restored and analogue1x/
16x/restored via standard public libcamera requests, record private NV12 and
whole-frame scalar response, verify all sensor register readbacks, owner/SOF/
metadata and neutral shutdown. Kernel audit31 is unchanged. Private profile
dependency remains; this work is not an upstream-ready claim.
