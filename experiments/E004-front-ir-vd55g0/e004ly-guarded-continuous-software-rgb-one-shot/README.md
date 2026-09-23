# E004ly — guarded native Linux software RGB extended managed-app trial

Fresh distinct E004ly one-shot identity on 2026-09-23. This is a
NON-DEFAULT, ROOT-PRIVATE physically bounded acceptance experiment,
NOT a permanent camera installer. It reuses the already accepted
E004la/E004kr/E004kp front RAW10→1080p NV12 and rear RAW10→4K NV12
software-conversion routes, rather than the separate 640x480
libcamera software-ISP proof. It does NOT touch Windows hardware ISP
parity, protected IR, Windows Hello or Linux OS system standby.

New unknown tested: whether the maintained direct publishers with
an explicitly opted-in 'continuous' argument can remain alive
BEYOND 2400 real source frames at native ordinary-app 1080p/4K
while retaining the previously proven uid1000 client first/reopen,
intentional client SIGKILL and recovery, the same systemd publisher
invocation, planned SIGTERM/STREAMOFF and graph neutralization
between cameras and at shutdown. Each camera first completes the
legacy bounded four-phase user-app cycle, then continues its SAME
publisher for 100 seconds without a client before a controlled stop.
Validator demands >=2600 full published source frames, no source
sequence gaps and zero leaked publisher/client FDs, and verifies
each ordinary app has 120 distinct correctly sized frames.
This is two finite roughly 2-minute sources, not multi-hour proof.
An opt-in long-lived publisher has a 4-hour hard fail deadline,
a 240-second systemd per-session watchdog and a 560-second main
one-shot timeout; no service restarts silently on failure.

Candidate-specific boot marker, distinct GRUB entry, newly rebuilt
canonical 51-file unified hardware/R4 stage, accepted hardware module
hashes and separate clean ABI-matched Ubuntu 26.04 v4l2loopback module,
and new source-pinned ARM64 direct binaries are SHA-checked and
isolated from protected Golden v19c. Root-owned one-shot service
returns automatically to saved Golden on success/failure. Before
any camera module/route write, the candidate checks boot/asset
identity, ordered GRUB writer state, root-only stage, pinned devices
and initial full graph. Front/rear have mutually exclusive physical
routes even though both named /dev/video91 and /dev/video90 virtual
endpoints remain discoverable. Only sensor runtime-PM status is read
when Linux stays fully awake; NEVER invoke system suspend/resume,
hibernate, or /sys/power/state writes.

Failure cleanup explicitly **does not guess at graph rollback or
remove camera modules if any STREAMOFF/ownership step is uncertain**.
It records failure and lets the guarded one-shot reboot into Golden.
IR sensor illumination stays OFF, IR streaming prohibited. Source
NV12 is still an uncalibrated software Bayer proxy; no pixel files
or authentication images may be exported. Hardware ISP and Windows
IQ parity are separate and deferred until Stage 1 RGB usability.

**Final result: PASS, CONSUMED, RETIRED.** See RESULT.json,
CONSUMED.json and evidence/ for bounded physical acceptance. Fresh
candidate boot 22877e95-4ad7-4e4d-8dc4-94915197c488 completed
front→neutral→rear→neutral with full native graph validation and
normal powered-on app client first/reopen/SIGKILL/recovery for both.
Front software1080p captured/published 3452 contiguous source frames
in 115.004s; rear software4K 3444 frames in 114.957s. Both sources
reported zero source-sequence gaps and intentional service stop=143
with verified STREAMOFF. Three normal uid1000 independent app opens
per camera obtained 120 distinct complete appropriately sized frames
each; intentionally killed client was recovered with the SAME
publisher invocation. Both named V4L2 endpoints were discoverable,
IR stayed off, zero camera FDs remained at route handoff and final
shutdown; peak sampled thermal 52.1C. Protected Golden returned,
and this candidate's boot/services/assets were RETIRED after return.
The prior 2400-frame source bound was passed, not an uninterrupted
all-day camera service. Both optical scenes sampled near-black, so
IMAGE QUALITY, calibration and Windows visual parity remain UNKNOWN.
The separately maintained source-only RGBSession policy has NOT
been wired into this live physical harness; no production daily
service or generic multi-client exclusivity is claimed.
E004ly one-shot identity MUST NEVER be reused.
