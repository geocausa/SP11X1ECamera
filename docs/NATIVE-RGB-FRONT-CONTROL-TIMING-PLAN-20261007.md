# Native front controls: timing and feedback gate

The real front libcamera pipeline/IPA is now physically proven in both generated
execution paths. Fixed settings supply native NV12 and paired hardware statistics
at about30fps; stop/restart/reacquire and shared-buffer lifetime pass. Control
timing and optical tuning are the next engineering work, not further generic
metadata plumbing.

## Receiver event delivery now hardware-proven

Pipeline05 sourceb08bc32f/audit29/build07 delivered80 standard cam frames at
30.00469fps and84 consecutive libcamera frameStart callbacks (85 receiver IRQ
SOFs). CSID680 IPP CAMIF_SOF bit4 comes from pinned Qualcomm GPL register source
commit38d50357/SHA9240958e and matches the pinned SP11 Windows IPP bit4 test.
Existing CSID1 owning ISR emits the events; no additional register reader or
hardware mask programming is introduced. See front-sof-source.json and
NATIVE-RGB-FRONT-FRAME-SYNC-05-20261007.json.

All80 steady VIDEO source observations have SOF-count minus source0; latest SOF
observation to VIDEO IRQ20.204-20.355ms, VIDEO IRQ to completion2.877-3.248ms.
Neither relation measures first-row exposure or actual sensor-control effects.
Lifecycle05 source81f04f6e passes same CameraManager/Camera1/80/80 restart and
reacquire with actual signed threaded IPA. App event counts5/84/84 and IRQ
counts6/85/85 reset from0 per start; all161 app-frame phase observations have
SOF-count minus VIDEO source0. No SOF/phase events after final STOP; all sensors
standby after each stop. See NATIVE-RGB-FRONT-FRAME-SYNC-LIFECYCLE-05-20261007.json.
SensorTimestamp remains absent. Ordered steps1/2 pass receiver event delivery
and restart qualification; step3 is the next physical gate.

## Current source findings

| Source inspected | Observed behavior | Consequence |
|---|---|---|
| VFE17x vfe_isr_sof | no-op | Receiver CSID1 supplies the qualified event instead |
| VFE core ops | no event subscription | CSID1 standard FRAME_SYNC is used |
| audit29 camss-csid-680.c | source-qualified CAMIF_SOF bit4, existing owning ISR | Ordered actual receiver events physically verified; exposure/control latency remains unmeasured |
| pinned libcamera v4l2_device.cpp | supportsFrameStartEvent, setFrameStartEnabled, frameStart | Existing standard consumer mechanism available |
| pinned libcamera rkisp1 pipeline | sensor helper delays into DelayedControls; frameStart applies controls | Reuse standard scheduling once native timings are qualified |
| current IMX681 native control adapter | group-held four-field sensor controls; analogue law unit-tested | Arithmetic is proven, live per-frame latency is not |
| current QXS1/video timestamps | MONOTONIC buffer completion | Valid pair identity; SensorTimestamp stays absent |

All source statements are from the locally pinned/compiled trees. No inferred
IRQ bit assignment or sensor delay is accepted as measured.

## Ordered implementation

1. Establish the exact native receiver frame-start IRQ/status source from
   authoritative hardware/source evidence. Keep reads in the owning ISR; do not
   introduce a second consumer that races IRQ clear. Track stream generation,
   per-frame sequence and actual event time. An Epoch0/BUF_DONE notification must
   retain its true name; it cannot be relabeled FRAME_SYNC merely for scheduling.
2. Expose standard V4L2_EVENT_FRAME_SYNC on the qualified device, with subscription
   lifecycle, ordered sequence, restart reset and no events after stop. Verify
   frame-start identity against DMA/statistics completion over a fresh one-use
   candidate. Preserve existing ownership/queue STOP semantics. Source/build
   checks precede hardware. SensorTimestamp still needs first-row exposure and
   BOOTTIME semantics independently.
3. Apply bounded grouped sensor gain/exposure steps under controlled lighting.
   Record commanded and observed frames, I2C completion times, frame starts,
   frame/statistics identities and raw/statistic/output response. Measure analogue,
   digital, exposure and frame-length delays and any scheduling uncertainty.
   Restore the qualified defaults within the same bounded test and return Golden.
   Changes in natural lighting invalidate latency/response attribution.
4. Wire libcamera DelayedControls with the measured delays and atomic sensor
   cluster. Establish metering units/range and AE targets using controlled response
   plus matched Windows captures. Preserve ISP residual-gain scalar coupling.
   Enable bounded AE only after its input domain and application frame identity
   are established; add AWB and dynamic tables through semantic parameters.
5. Accept image quality with the same camera/scene/position/lighting on Windows
   and Linux, time-proximate dual boots, explicit timestamps/settings/output
   range. Run convergence/stability tests across illumination, then longer
   capture, restart, camera switching and fault recovery. Rear hardware ISP and
   focus remain their own required implementation path.

## Next experiment contract: grouped controls

Source review confirms IMX681 v4l2_ctrl_cluster(4, &vblank), with VBLANK as master.
One extended-control set validates the full frame-length/exposure relationship
and performs one group hold, four register writes and an unconditional hold
release, returning the CCI error. Pinned DelayedControls priorityWrite=true sends
that member through a separate setControls call. Use priorityWrite=false for all
four cluster members; keep the normal cluster validation. Measure delays for
each member rather than copying another sensor's delay or forcing equal delays.
A measured physical delay may differ even though the transaction is grouped.

Before feedback, introduce an explicit development-only bounded experiment in
standard libcamera's frameStart path. Keep automatic controls disabled and
existing default typed ISP parameters. The experiment must log command request,
receiver sequence and timestamps before/after sensor setControls, and kernel
CCI group-release completion/result. No successful-control or applied-frame
metadata may be published when a write fails. Delay inference uses observed
frame/statistic response, not the current cached control value alone.

Use the qualified baseline exposure1000, analogue code0, digital256, FLL3554.
Change one field at a time using complete four-member ControlLists; candidate
bounded steps are exposure1000/2000, analogue0/512, digital256/512 and
FLL3554/7108. Verify current driver limits and exposure containment before any
write. Hold each plateau for at least16 frames, repeat up/down three times and
restore baseline between fields and before STOP. Longer FLL requires duration
and timeout accounting. Never reuse a consumed hardware identity.

Compare AEC regions/statistics and private NV12 metrology against pre/post
baseline windows. Reject delay attribution if lighting, scene, clipping, noise or
response ambiguity prevents a repeatable transition. Frame-length response can
be assessed from receiver intervals without assuming scene brightness. Exposure
and gain response still require stable lighting and independent metering-unit
qualification. This experiment does not establish Windows optical parity.

## Constraints and current acceptance

No bespoke camera daemon, CPU image processing, AI/effects or Windows executable
release dependency. Kernel owns MMIO/DMI/buffer lifetime; standard libcamera IPA
owns control calculations. Original optical pixels, OEM artifacts and extracted
tuning remain private on SP11. Firmware redistribution rights and independent
tuning are not established. Golden default/assets remain protected; new candidate
identities are consumed once and retired after any attempt. No system suspend.

Low output Y under fixed settings is an observation, not a diagnosed brightness
defect. The user's rainy/cloudy conditions are recorded; no matched Windows
optical reference exists for these runs. Product is not complete.
