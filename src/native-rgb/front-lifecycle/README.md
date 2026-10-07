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

# Fresh lifecycle04: actual signed threaded IPA lifetime qualification

Uses audit27/libcamera build06. The same public CameraManager and Camera capture
1 frame, restart for80 with the same configuration/app buffers, then release/
reacquire/reconfigure for80. This exercises actual IPA map/start/stop/unmap and
queued callbacks across kernel stream/profile resets in the signed threaded path.
Pipeline04 already proves the isolated path; this gate covers the normal trusted
opensource module path and repeated mapping lifetime. No automatic feedback.

Every app frame requires an actual IPA metering result with matching completion
time and a new stream identity per start. SensorTimestamp must be absent, since
buffer return time is not exposure time. All sensors suspend after each stop;
final release leaves neutral graph. Identity is fresh and one-use; keep pixels
private. Product quality and matched Windows lighting acceptance remain separate.

# Front public libcamera lifecycle qualification

Fresh native-lifecycle-20261007-03 uses corrected audit27 and qualified libcamera build03.
A small qualification application uses the public libcamera API; it is not a
product capture runtime. The same CameraManager and Camera object capture one
frame, restart with80 frames using the same configuration and application DMA
buffers, then release, reacquire, reconfigure and capture80 frames. No module
reload intervenes. Each finite capture must finish exactly, stop cleanly, carry
fresh stream identity and pair each hardware output with statistics. The kernel
must retire every owner group, reset its semantic FIFO and load a fresh profile
each start. No pixel data is processed or exported by this lifecycle test.

Protected Golden/default assets stay unchanged; the one-use service returns
Golden regardless of result. Consume and retire this identity after one attempt.
IPA/automatic3A, rear ISP and optical quality remain separate requirements.

Lifecycle01 passed the one-frame round then rejected the second start before
STREAMON: cached profile remained after its producer FIFO closed. Successful
STREAMOFF now retires stream-owned profile/FIFO after worker exit. Unsafe/pinned
paths keep their early returns. Lifecycle01 consumed/retired; never rearm.

Lifecycle02 verified profile/FIFO reinitialization but reached the legacy static
one-start-per-module NV12 guard. Profile mode now admits only inactive, unpinned
workers and retains the exact disabled-WM/linear-MODE cold-state readback gates.
The earlier diagnostic modes retain their one-start guard. Lifecycle02 consumed
and retired; never rearm.

Lifecycle03 physically passed161 app frames,880 owner checks/176 retirements,
185 typed requests and3 firmware loads; all three stops clean and all sensors
suspended after each. Original Golden hashes unchanged. All three lifecycle
identities consumed/retired. Pair timestamps are completion-time association;
SensorTimestamp first-row exposure/CLOCK_BOOTTIME semantics are not qualified.
