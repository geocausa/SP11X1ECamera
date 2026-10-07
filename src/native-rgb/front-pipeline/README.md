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
