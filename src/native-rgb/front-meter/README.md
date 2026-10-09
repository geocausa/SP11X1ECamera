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
