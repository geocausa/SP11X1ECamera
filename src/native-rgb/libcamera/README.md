## 2026-10-07 native receiver frame-start hardware PASS; lifecycle05 next

Fresh pipeline05 sourceb08bc32f/audit29/libcamera build07 passed80 standard cam
2560x1440 NV12 frames at30.00469fps,80 app/statistics pairs and84 actual isolated
IPA metering results. Standard CSID1 V4L2 FRAME_SYNC delivered84 consecutive
libcamera frameStart callbacks; owning ISR observed85 source-qualified bit4
SOFs at30.00535fps. All80 steady VIDEO sources had SOF-count minus source0;
latest receiver SOF observation preceded VIDEO IRQ by20.204-20.355ms and
completion followed VIDEO IRQ by2.877-3.248ms. This is interrupt phase observation,
not first-row exposure identity, sensor-control latency or SensorTimestamp proof.

425 owner checks/85 retirements,88 typed defaults,clean STOP,error0,neutral graph,
all sensors standby,critical faults0,Golden hashes unchanged. Candidate boot
 ae0cb572-f768-49c8-8cb0-0b86ba7ebba6 returned Golden54041d3b-e446-4720-844a-8c1e48300c37.
Pipeline05 consumed and retired;21 consumed identities/42 candidate-Golden boots,
23 completed sensor streams; prior5 prestream/2 poststart failures unchanged.
Evidence: docs/NATIVE-RGB-FRONT-FRAME-SYNC-05-20261007.json.

Fresh lifecycle05 is the next one-use qualification: same CameraManager/Camera
1/80/80 restart/reacquire with audit29/build07, signed threaded actual IPA, SOF
sequence reset and final-stop silence in addition to existing queue/owner/standby
checks. Its public API binary builds Werror; no stream yet. Never reuse spent IDs.
Then measure grouped sensor exposure/analogue/digital/frame-length delays before
standard DelayedControls and automatic feedback. AE/AWB, metering normalization,
rear ISP/focus, public ABI/clock policy, independent tuning and optical acceptance
remain. No matched Windows reference; fixed low Y is no proven brightness defect.
Match camera/scene/position/lighting/capture time, including rainy/cloudy changes.
Earlier NEXT statements are history. No bespoke daemon/CPU image ISP/AI/OEM runtime.

## 2026-10-07 current native front IPA: both standard paths hardware-proven

Actual libcamera build06/audit27 now passes isolated standard cam80 capture and
signed threaded same-CameraManager/Camera1,80,80 restart/reacquire. Pipeline04
source90837d1d delivered80 NV12 frames30.00485fps with84 metering results,
425 owner checks and88 typed requests. Lifecycle04 source964de842 delivered161
app frames,173 metering results across fresh streams6,7,10,880 owner checks and
185 typed defaults; longer captures30.00543/29.98823fps. No module reload.
All stops clean, sensors suspended after each stop, final graph neutral,
Golden hashes unchanged, critical faults0. Returned Golden boot
b2e5554f-6b33-4aca-8e7f-ffac7b241ecf. Pipeline04/lifecycle04 consumed and retired;
all20 candidate identities retired,22 completed sensor streams,40 candidate/
Golden boots. Pixels/original tuning remain private SP11.

The actual IPA maps eight read-only shared statistics buffers, meters exact
stream/sequence/completion-time identities and produces qualified mask0 typed
defaults. Metadata buffers wait for matching IPA results before requeue; app and
startup/spare completion also requires metering. Stop barriers precede unmapping.
Build06 Werror9 tests OK/2 VIMC skips. No bespoke daemon or CPU image ISP.

NEXT concrete blocker: native frame-start events and measured sensor-control
delays before automatic exposure/gain. Source audit shows the current VFE17x SOF
handler is a no-op and VFE core ops expose no event subscription. CSID680 Epoch0
and BUF_DONE counters are not exposure/SOF proof. Qualify an actual receiver SOF
source, standard V4L2_EVENT_FRAME_SYNC sequence/association and grouped sensor
change effects; use libcamera DelayedControls only with measured delays. See
docs/NATIVE-RGB-FRONT-CONTROL-TIMING-PLAN-20261007.md. Meter normalization, AWB and
dynamic ISP tables still require qualification. SensorTimestamp remains absent.

Fixed settings/low Y do not establish a brightness defect; matched Windows same
physical camera/scene/position/lighting and time-proximate captures required.
Rear processed ISP/focus, public ABI/clock policy, independent tuning and long-run/
switch/fault/Windows optical acceptance block product completion. Actual IPA is
no longer absent. Earlier NEXT statements are history. Evidence:
docs/NATIVE-RGB-FRONT-IPA-04-20261007.json and
docs/NATIVE-RGB-FRONT-IPA-LIFECYCLE-04-20261007.json.

## 2026-10-07 actual native front IPA physically verified

Fresh pipeline04 used90837d1d/audit27/libcamera build06. Standard cam delivered
80 hardware2560x1440 NV12 frames at30.00485fps through a real isolated libcamera
IPA. Eight shared statistics buffers produced84 ordered metering results;
all80 app frames matched stream/sequence/completion time. The IPA produced88
typed mask0 defaults. Kernel passed425 owner checks/85 retirements; cam exit0,
STOP clean, graph neutral, all sensors standby, critical faults0, Golden hashes
unchanged. Returned boot2aa4c3a8-f6c6-4d6a-b805-b8c0586b7f48. Pipeline04 consumed
and retired; all older candidate identities remain retired.

Actual IPA is now hardware-proven. Automatic AE/AWB feedback, sensor control
delays, first-row exposure timestamp and optical metering normalization remain
unqualified. Fixed settings and low Y do not establish a brightness defect;
matched Windows camera/scene/lighting/capture-time comparison remains required.
Next lifetime gate uses fresh lifecycle04 with the same actual IPA in its signed
standard threaded path:1/80/80 restart/reacquire, stop barriers/shared maps and
fresh stream identities. Then qualify sensor timing and control feedback.
Rear ISP/focus, dynamic tables, public ABI/clock policy, independent tuning and
long-run/switch/fault/Windows optical acceptance still block product completion.
See docs/NATIVE-RGB-FRONT-IPA-04-20261007.json; earlier NEXT statements are history.

# Actual native front standard libcamera IPA

Build06 integrates a real IPA module and generated standard proxy. Hardware pixel
processing stays in the Qualcomm ISP. The IPA reads shared statistics, validates
frame identity, computes the retained AEC meter and emits typed mask0 defaults.
No exposure or colour feedback is enabled. Metrology and sensor delays are next.

Nine offline tests pass with Werror; two VIMC-dependent tests skip. An actual IPA
implementation test uses real memfd mappings and covers negative admission,
ordering, nonzero metering and lifecycle reset. Fresh pipeline04 will force normal
libcamera IPA process isolation and require80 associated application frames.
No bespoke camera daemon is introduced; the worker belongs to standard libcamera.
No physical IPA claim until that candidate passes. Optical comparison requires
Windows on the same physical camera, scene and lighting, with capture times.

# Native X1E libcamera pipeline and helpers

Current physical proof: build03/audit27 delivers standard cam80 NV12/statistics
pairs2560x1440 at30.0056fps, and public API same-camera1/80/80 restart/reacquire
passes161 app frames/880 owner checks. Fixed manual only; real IPA/3A absent.
Latest build04/audit27 pipeline03 passes80 standard cam frames at29.9919fps,
with the incorrect SensorTimestamp field removed. Pairing uses completion time;
first-row exposure/CLOCK_BOOTTIME remains unqualified. Actual IPA/3A is next. Earlier helper-only descriptions below are historical.

The approved product is Linux sensor/CAMSS drivers, Qualcomm hardware ISP and
a standard libcamera pipeline/IPA. Automatic control calculations execute in
libcamera; pixel processing belongs to the hardware ISP.

This integration builds the retained front sensor-control adapter, front AEC
statistics meter and rear neutral ISP scalar producer inside real libcamera
libipa. The IMX681 helper registers the measured/reconstructed Sony analogue
gain law; it deliberately leaves unknown black level unset.

The front adapter validates every control before returning one four-control
transaction (VBLANK, exposure, analogue gain, digital gain) and residual ISP gain.
Apply the returned list through one extended-control operation. The sensor
ControlInfoMap must outlive the list. This preserves the driver's group-held
cluster. Failed validation leaves outputs unchanged.

Statistics use the retained bounded-front envelope, not a new public metadata
ABI. Both generation and sequence must match the caller's expected identity.
The rear scalar wrapper preserves the validated float/quantization arithmetic
and prevents partially published results on error.

## Reproduce

Use fresh source and build outputs outside the camera checkout:

```sh
python3 src/native-rgb/libcamera/build.py \
  --source /home/geoca/Documents/SP11-PROJECT/06-camera/reference/libcamera-v0.7.0-native-ir \
  --out /home/geoca/Documents/SP11-PROJECT/06-camera/reference/libcamera-native-rgb-NEW \
  --build-dir /home/geoca/Documents/SP11-PROJECT/02-kernel/libcamera-native-rgb-NEW \
  --jobs 4
```

The reference commit and source inputs are pinned. Clone copies committed files
only: earlier uncommitted software-ISP changes in the reference are excluded.
The retained statistics file's private fadd/fsub/fmul names receive a prefix to
avoid GNU math declarations; arithmetic is unchanged. Original retained files
remain untouched. The build enables warnings as errors, verifies staged hashes,
requires the native test to pass, and records selected tests and binary digests.
Source, setup, compile and test logs remain in the isolated outputs.

This build enables UVC/VIMC and the test-only virtual pipeline, not a CAMSS X1E
pipeline. SoftISP is disabled. Nothing is installed or opened on camera hardware.
The helper test covers gain conversion, nominal and extended exposure, complete
control publication, range rejection, neutral/asymmetric rear gains, preservation
after late errors, nonzero AEC metering, and stale/malformed statistics.

## Remaining integration

This is a compiled algorithm integration, not a completed IPA or pipeline.
Native linear NV12 capture, continuous streaming, parameters/statistics queues,
front/rear ownership and hardware-correlated delayed controls remain required.

The front driver lacks HBLANK/PIXEL_RATE and selection information. Its unused
548570000 mode field describes transport-derived throughput and must not be
published as array PIXEL_RATE. Retained Windows exposure policy uses an effective
719898240 timing model from 6752 * 3554 * 30. The public September 23 IMX681 v7
patch measures 720 MHz with the same VT PLL divisors but a different mode/platform.
Measure this SP11 mode before publishing truthful timing controls. Do not guess
full pixel-array bounds from the current crop.

Retained files keep their original licences (front GPL-2.0-only, rear MIT).
This does not relicense them as LGPL or claim upstream acceptance. No Windows
binary, tuning dump, optical frame, daemon, loopback or software pixel ISP is added.


The frame-associated metadata consumer now validates the experimental QXS1
envelope, stream ID, video sequence and pixel timestamp before reducing AEC
luma. Malformed, stale and discontinuous input leaves the caller output untouched.
It uses the exact shared kernel/probe envelope definition. This helper passed
the real ARM64 libipa build and tests, with no installation or hardware access;
see docs/NATIVE-RGB-LIBCAMERA-METADATA-BUILD-20261007.json. A complete pipeline/IPA
is still required to schedule requests and connect this consumer at runtime.


The typed front parameter encoder now forwards bounded caller-owned quantized
gains/ratios through the exact shared kernel schema, rejecting invalid masks,
sizes, sequence bounds and ranges without modifying the caller output.
See docs/NATIVE-RGB-LIBCAMERA-PARAMETERS-BUILD-20261007.json. Scheduling and the
camera pipeline remain unfinished; the private startup profile is diagnostic.

An optional --front-pipeline-trial build now stages a real CAMSS X1E pipeline
and standard cam. It matches the data-only front driver, owns four startup
buffers and pairs app images/statistics before libcamera request completion.
The first version uses fixed manual settings, no IPA/automatic controls.
Hardware pipeline02 and lifecycle03 passed the bounded scopes above. Hardware qualification lives in
src/native-rgb/front-pipeline with a fresh one-use boot.
