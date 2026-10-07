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
Lifecycle05 next checks reset across three starts and silence after final STOP.
SensorTimestamp remains absent. Ordered implementation steps1/2 have passed the
single-stream delivery gate; restart qualification is still pending.

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
