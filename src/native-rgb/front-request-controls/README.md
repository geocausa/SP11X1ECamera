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

# Qualified full-rate controls; all current identities spent

04 PASSED120 standard public scripted requests,consecutive4..123 frame sequence,
30.00384/30.00540fps and scripted15.00326fps,plus1/24/24 public lifecycle with
contiguous30fps metadata/start/default reset/reacquire/manager/isolated-worker exit.
Four STOPs125/6/29/29 clean,945 owner checks/no critical faults/Golden unchanged.
04 consumed and retired; ALL01/02/03/04 MUST NOT be reused. Installer currently
points spent04 intentionally, so its fresh-path guards reject reuse.

Manual controls are standard libcamera DelayedControls with measured2frames,
full normal non-priority clustered ioctl,per-SOF applied snapshots and complete
quantized request validation. Source/isolated ARM64Werror build12 qualified by
04 hardware. AE/AWB feedback still off,SensorTimestamp absent. Meter optical
domain/zero/normalization/AE targets and independent tuning/production remain.
Next work must not repeat this gate without a new change/failure. No next runtime
identity is prepared. Original prior harness failures and throughput regression
preserved in derived reports/current state.04 wrote no optical files.

# Current full-rate qualification

03 passed1/24/24 control lifecycle,manager shutdown and isolated-worker exit;
spent and retired. Pipeline11 still inserted a spare every4 application frames.
Restored threshold2 in fresh build12. NEXT04 via install-lifecycle.py and
run-throughput-once.py verifies120 standard public scripted requests with
consecutive frame sequences/full30fps and scripted15fps,no optical files,
then stricter1/24/24 contiguous30fps controls/reset/reacquire/shutdown checks.
Pipeline12 passes10 tests/2 virtual skips with Werror. Golden and one-use rules
retained. Native AE/AWB and optical/meter calibration remain unfinished.

# Latest lifecycle test

02 is consumed/retired. Three kernel streams stopped clean6/34/34,custom then
reset physical settings correct;process/49 publicmetadata qualification remains
incomplete after pipe-output timeout,original preserved. Source audit found
retained Camera reference after CameraManager::stop; corrected to reset first.
NEXT03 using install-lifecycle.py/run-lifecycle-once.py,new test binary, direct
private output files/shutdown markers,manager-stop and isolated-worker exit checks.
If needed, bounded backtrace is permitted only after3 STOPs/sensor runtime idle.
No repetition of the already qualified120-frame request capture.

# Current qualification status

request01 is CONSUMED AND RETIRED. Its actual120 public cam requests pass all
control/metadata/readback/write-SOF checks. Original qualification erroneously
required zero-origin owner logs and failed before lifecycle. Original preserved;
retrospective offline correction proves all groups1..154 contiguous, STOPclean.
See docs/NATIVE-RGB-FRONT-REQUEST-CONTROLS-01-20261007.json; no repeat capture.

NEXT fresh request02 using install-lifecycle.py/run-lifecycle-once.py tests ONLY
public lifecycle1/24/24: custom start settings, same-configuration default reset,
release/reacquire reset. Current origin-independent trace checks have6 pure tests.
Golden permanent/service120s/atomicconsume/automaticreturn/pixel privacy retained.

# Standard request control qualification

E-NATIVE-FRONT-REQUEST-CONTROLS-01 is a fresh one-use candidate. It reuses
qualified audit31 kernel modules and builds standard libcamera pipeline11.
The source implements DelayedControls with measured delay2 for all four
non-priority sensor controls, one complete clustered ioctl for each change.
Public controls: manual ExposureTime/AnalogueGain/DigitalGain and bounded
FrameDurationLimits, with AeEnable=false and manual-only mode controls.
Exposure/time conversion uses the existing sensor HBLANK/PIXEL_RATE model;
integer microseconds are rounded, not optical calibration. AE/AWB remain off.

Admission counts startup/spare/app buffers in exact VIDIOC_QBUF order. Every
controlled request must arrive before its delayed slot is pushed (three-frame
scheduling horizon); late controls fail instead of borrowing another frame.
SOF snapshots preserve applied metadata independently of the 16-entry delayed
control ring. SensorTimestamp remains absent. Upstream applyControls is void;
the pipeline checks cached V4L2 readback after each write, and qualification
independently verifies known CCI register reads and write timing.

Hypothesis: real standard cam --script requests are applied to the exact
admitted application frame and reported in public metadata, including all four
sensor fields; stopping and restarting cannot leak previous control history.
Expected:120 NV12 requests, nine explicit request lists/eight actual changes,
all applied metadata/known-register reads/CCI SOF intervals match; public API
lifecycle1/24/24 proves custom start controls then default reset and reacquire.
Golden remains permanent, candidate has a120s service bound and automatic
Golden return on success/failure/timeout. No same-ID retry is permitted.
Pixels remain in the private root-owned SP11 evidence directory. Only derived
scalar evidence goes into Git. Lights last reported ON18:26:29UTC; no new
simultaneous Windows comparison or uninstrumented scene stability claim.
Image quality, automatic exposure and production readiness remain unproven.
