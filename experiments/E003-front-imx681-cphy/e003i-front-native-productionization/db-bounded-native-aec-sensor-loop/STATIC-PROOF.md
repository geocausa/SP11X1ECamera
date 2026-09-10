# DB static/offline proof

## Parent closures

DB requires corrected parent `c094198`.

- AQ/CH: active ordinary-preview T681 range is gain `1..92`, time `37,516..66,666,664 ns`, policy `0`.
- CQ: the corrected CH output domain converts bit-exactly to IMX681 FLL/VBLANK/exposure/analogue/digital controls.
- CV: generation-tagged STATS3A composes atomically through native AEC to CQ controls; Windows ownership is `request = generation + 3`; sensor pipeline delay is 2 and CamX history realign is 0.
- DA: combining Windows request ownership and CY's measured Linux write→effect delay requires release after completed `G+1`, first effect `G+3`.
- CW: the Linux four-control request is an atomic V4L2 cluster and is published under IMX681 group hold.

## Exact runtime ordering

The paired-stats thread is the sole owner of native AEC state and the DB schedule. The video thread publishes validated DQBUF completion using a C11 release-store; the stats thread reads it with acquire semantics.

For target generation 2..4 the stats thread calls `release_control_at_video_boundary()` **before** reading/processing the current target's STATS3A. The release routine:

1. waits until `video_completed_generation == target`;
2. fails without a write if the counter has already advanced past target;
3. releases the previously queued source `target-1` from the pure scheduler;
4. rechecks the exact completion generation;
5. issues the single four-control ioctl call site;
6. rechecks the completion generation after the ioctl and fails the remaining schedule if the next DQBUF arrived during the write.

Thus G1 is queued from stats G1, released at DQBUF G2, and expected at G4; similarly G2→G5 and G3→G6. G4..G6 are computed for observation/history but are never released in this bounded gate.

## Failure behavior

The pure scheduler separately models `queue` and `release`. Verification covers out-of-order queue, invalid control geometry, release without a queued source, duplicate release, explicit failure latching, post-failure queue rejection, and the corrected long-exposure sensor geometry. Any failure prevents later releases.

## Scope

DB applies sensor controls only. CQ's residual ISP gain is retained in the native output but is not written by DB. Full unrestricted/native image-pipeline AEC parity remains outside this checkpoint.

## Bootstrap transport correction after first candidate

The first candidate did not enter streaming. Preparation exposed that `v4l2-ctl` was issuing piecemeal `VIDIOC_S_CTRL` for the cold tuple. This is incompatible with the four-control CW cluster contract even though the tuple itself is valid (`3554 <= even(3562-4)=3558`). The failed state was VBLANK 1402 / exposure 3546 / analogue 0 / digital 256, helper unconsumed, STREAMON not attempted.

The corrected DB bootstrap uses one `VIDIOC_S_EXT_CTRLS` with count 4 and control order VBLANK, EXPOSURE, ANALOGUE_GAIN, DIGITAL_GAIN, then requires exact `VIDIOC_G_EXT_CTRLS` readback. The runtime boundary write path already used the same extended-control mechanism, so no scheduler or sensor-driver arithmetic changed.

## Request-4 warm-up rebase after second candidate

Attempt2's `-142` maps exactly to CV(-10) + CU(-100) + CP Short-T681(-32), with CH returning `-2` because G3 Short convergence was over the ordinary table. DG/DH independently prove Windows policy-0 post-convergence T681 rejects that same forced target, so no clamp is permitted.

The missing state is the W `G -> request G+3` warm-up. DC shows real Windows requests1..3 each converge all seven lanes to 33,312,452; CH maps that coordinate back to the same retained exposure exactly. DI pins PredGain `0x3f800000` for requests1..3. AB22 pins the cold request4 entry Lux `0x4365acdd`. DJ installs exactly those values behind a +3 internal history coordinate while leaving CU's public local frame identity unchanged. Its verifier replays the byte-pinned attempt2 G1..G3 STATS3A corpus and eliminates the G3 `-142` with no sensor/device access.

## Attempt3 G4 boundary and DK failure persistence

Attempt3 completed all three allowed sensor transactions before native AEC G4 returned `-142`. The return-code chain is exact: CH Short T681 `-2` → DJ request loop `-32` → CU raw loop `-132` → CV control join `-142`. Thus the failure is upstream Short exposure arbitration, not the sensor ioctl path. No fourth sensor write is authorized by the scheduler.

The old full-run persistence loop was unreachable after this failure, so the validated G4 TLBG/STATS3A buffers were lost from RAM at reboot. DK adds a failure-only persistence function. In the AEC-error branch, `e003i_db_schedule_fail()` executes first; only then are the already generation/source/slot-validated current buffers written through `save_file()`, which fsyncs before close. If either evidence write fails, the error is logged while the original AEC failure and failed schedule remain authoritative. The normal success save loop and the single sensor-apply call site are unchanged.
