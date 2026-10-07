## 2026-10-07 native receiver frame-start and restart hardware PASS

Kernel audit29/libcamera build07 physically pass both actual standard IPA paths.
Pipeline05 sourceb08bc32f:80 standard cam2560x1440 NV12 frames30.00469fps,
84 isolated IPA metering results,84 consecutive libcamera frameStart callbacks,
85 receiver IRQ SOFs,425 owner checks,88 typed defaults. Lifecycle05 source81f04f6e:
same CameraManager/Camera1/80/80 restart/reacquire passes161 app frames and173
signed threaded IPA results; app SOF counts5/84/84,IRQ counts6/85/85 reset from0
each start; final STOP has no later SOF/phase events. Stream IDs6/7/10,880 owner
checks,185 typed defaults; longer runs30.00582/30.00572fps. No module reload.

All241 app frames across these four streams matched hardware statistics/IPA.
All241 steady observations had SOF-count minus VIDEO source0. Receiver SOF IRQ
observation to VIDEO IRQ20.204-20.355ms in pipeline05; IRQ to completion2.877-
3.248ms. These observations are not first-row exposure identity or sensor-control
latency. SensorTimestamp remains absent; automatic AE/AWB remains disabled.

All STOPs clean,error0,all sensors standby after each stop,final graph neutral,
critical kernel faults0,Golden hashes unchanged. Both05 IDs consumed and retired;
all22 candidate IDs retired,26 completed sensor streams,44 candidate/Golden boots;
prior5 prestream/2 poststart failures unchanged. Latest Golden boot
33010f45-c44b-4faa-923a-953e90113de3. No candidate boot/unit/writer/FW remains.
Private original tuning, logs and optical pixels stay on SP11.
Evidence: docs/NATIVE-RGB-FRONT-FRAME-SYNC-05-20261007.json and
 docs/NATIVE-RGB-FRONT-FRAME-SYNC-LIFECYCLE-05-20261007.json.

NEXT: bounded grouped sensor exposure/analogue/digital/frame-length response and
measured per-field delays with CCI completion + receiver/frame/statistics times,
stable-light screening and repeated up/down steps. Use standard DelayedControls
only with those measurements. IMX681 already has a four-control atomic V4L2
cluster with VBLANK master; do not copy another sensor's priorityWrite=true,
which splits VBLANK into a separate ioctl. See current timing plan.
Metering normalization, AE/AWB/dynamic tables,rear ISP/focus,public ABI/clock
policy,independent tuning and soak/switch/fault/Windows optical acceptance remain.
No matched Windows reference; fixed low Y is no proven brightness defect.
Match physical camera/scene/position/lighting/time, including weather changes.
Earlier NEXT statements are history. No bespoke daemon/CPU image ISP/AI/OEM runtime.

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

## 2026-10-07 native receiver frame-sync built; fresh pipeline05 next

Source-qualified CSID680 IPP CAMIF_SOF is bit4 (status0xac, clear0xb4);
Qualcomm GPL register source, commit38d50357, SHA9240958e, matches the pinned
SP11 Windows IPP handler bit4 test. Epoch0 bit21 remains a different event.
Source evidence: src/native-rgb/front-sof-source.json. Kernel audit29 compiles
W=1/-Werror: explicit native_front_sof_trial depends on data-only profile mode;
CSID1 accepts standard FRAME_SYNC, existing owning ISR emits ordered events,
IRQ barriers reset/start and disarm/stop. No hardware mask/DMA programming change.
Read-only phase observations relate SOF count to VIDEO interrupt count.

libcamera build07 passes Werror9 tests/2 VIMC skips; subscribes to receiver
frameStart before capture, checks continuity, unsubscribes after hardware stop.
No control scheduling or SensorTimestamp publication. Fresh pipeline05 is the
next one-use candidate, requiring80 standard cam NV12/statistics/IPA pairs and
actual SOF delivery/phase observations, STOP/neutral/standby/Golden protection.
Audit28 was an offline SOF-only build; audit29 adds phase observations. Neither
created a sensor stream or consumed hardware identity. Hardware timing remains
unproven until pipeline05. Sensor delays/metrology/AE/AWB and rear ISP remain next.
Matched Windows scene/lighting/capture-time condition still applies to quality;
low Y alone is not a brightness defect. Earlier NEXT statements are history.

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

# Fresh pipeline04: actual standard libcamera IPA qualification

This fresh one-use identity uses audit27 and libcamera build06. It loads the real
native IPA through libcamera's generated proxy, forces standard process isolation,
and maps eight read-only shared statistics buffers. Each metadata buffer stays
held until the matching stream/sequence/timestamp IPA result returns. Application
requests and internal startup/spare buffers retire only after video, metadata and
metering agree. The IPA produces the previously qualified mask0 typed defaults.

The test requires80 standard cam NV12 application frames, ordered IPA metering
including four hidden startup frames, exact completion-time association, actual
isolated proxy loading, contiguous kernel typed admission and owners, clean stop,
neutral graph, sensor standby and unchanged Golden. It does not enable AE/AWB or
claim exposure timestamps, metering normalization, optical quality, or brightness
defects. Comparison requires matched Windows scene and lighting conditions.

Build06 passes Werror:9 tests OK,2 VIMC-dependent skips. The added test exercises
the actual IPA implementation with real shared memfd mappings, atomic map
admission, typed request order, nonzero AEC metering, stale/duplicate/malformed
rejection, and restart reset. Build05 failed offline on a staging newline escape;
no candidate boot or sensor stream occurred. Do not reuse completed identities.

# Standard libcamera front pipeline qualification

Fresh pipeline02 uses the physically verified audit24 kernel, data-only firmware
and the corrected build03 real pipeline compiled into pinned libcameraff740913. The standard cam app
must capture80 hardware2560x1440 NV12 frames. No custom capture probe, daemon,
userspace command packet, software pixel ISP or Windows executable is used.

The pipeline matches only the front typed-control/data-only driver graph. It
opens descriptors on acquire and closes them on release, configures the exact
sensor/CSIPHY2/CSID1/VFE1PIX route, supplies bounded typed defaults and owns four
startup buffers internally. App buffers then use normal libcamera/V4L2 DMA-BUF
export/import. Statistics use an internally owned standard metadata queue; every
app request requires matching stream, hardware sequence and pixel timestamp
before completion. Queues stop before buffers are freed; release restores the
neutral graph. The standard cam writes private NV12 files only on SP11.

This initial pipeline advertises no automatic or per-request image controls.
It uses the qualified fixed-manual exposure/IQ to prove actual application,
buffer and request/statistics integration. Full IPA/3A, dynamic semantic tables,
rear processed capture, public ABI/clock policy, reopen/soak/switch and Windows
optical quality remain required. Build success alone does not prove hardware.

The fresh candidate requires80 application frames,80 paired request markers,
four hidden startup frames, exact Y/UV extents, metadata timestamps, at least84
kernel retirements and matching consumed owners, semantic FIFO continuity,
explicit clean stop, neutral graph, sensor standby and protected Golden return.
The identity is one-use; consume and retire after any attempt, never rearm it.

Pipeline01 is consumed and retired: it delivered79 application frames before
the final output waited for a further queued buffer. Zero kernel faults occurred;
Golden was restored. Pipeline02 reuses only fully paired and retired internal
startup buffers as spare outputs when queued depth falls below two. This lets
finite application captures drain the last request without exposing spare frames.
The corrected build passes Werror and8 selected tests with2 VIMC skips; pipeline02 hardware qualification passed80 app frames at30.0056fps,425
owner checks across85 retirements and clean stop/release. Both identities retired. Timeout output is retained privately on SP11.

Fresh pipeline03/audit27/libcamera build04 removes the unqualified SensorTimestamp
control. Kernel/video/statistics completion times still pair every app request,
but they are not claimed as first-row sensor exposure time or CLOCK_BOOTTIME.
Qualification requires80 standard cam frames and absence of that control.

Pipeline03 physically passed80 hardware frames at29.9919fps,425 owner checks/
85 retirements and88 typed requests. Unqualified SensorTimestamp absent; all
statistics pairs valid and STOP/release clean. All3 pipeline identities retired.
