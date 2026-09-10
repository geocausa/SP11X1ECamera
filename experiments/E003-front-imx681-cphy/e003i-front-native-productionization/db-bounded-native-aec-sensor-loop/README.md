# E003i DB — bounded native AEC sensor loop

Status: **READY_UNEXECUTED**.

DB is the first bounded Linux integration of the self-contained native AEC request path with the live-proven IMX681 clustered/group-held sensor-control transport. It is deliberately not an unrestricted continuous-AEC claim.

## What DB does

The candidate captures six ordinary front-preview generations. Each exact generation-tagged STATS3A snapshot is processed through CU→CV. Native AEC therefore computes G1..G6, but only the first three sensor tuples are eligible for live release.

The timing law is evidence-backed:

- Windows: stats generation G owns logical request G+3.
- CY: a Linux group-held write after completed generation N first changes optical statistics at N+2.
- Therefore DB releases G1 after completed G2 for optical G4, G2 after G3 for G5, and G3 after G4 for G6.

DB does not wait until G2's AEC computation to release G1. The paired-stats worker queues G1 first, then on the next iteration waits for the exact G2 DQBUF completion and releases G1 immediately **before** processing G2. The same ordering is used for G2/G3 and G3/G4. If the DQBUF generation has already advanced past the required boundary, the run fails closed rather than issuing a late write. It also verifies that the next DQBUF did not arrive during the control ioctl.

## Cold bootstrap

DA's exact cold bootstrap is installed before STREAMON as one four-control cluster:

- FLL 3562 / VBLANK 1402
- exposure 3554 lines
- analogue gain code 0
- digital gain code 0x0100
- residual ISP gain 1.0

CW republishes the cached cluster during stream setup under IMX681 group hold.

## Range correction

DB depends on `c094198` (`camera: correct T681 preview exposure range`). The active Windows T681 controller is now byte-pinned to gain 1..92, time 37,516..66,666,664 ns, policy 0. The older 33.333 ms / 184x interpretation is retired.

## Safety boundary

Only three runtime calls can reach the four-control `VIDIOC_S_EXT_CTRLS` site. AEC failure, ownership mismatch, invalid control geometry, schedule failure, missed DQBUF window, or ioctl failure latches the schedule failed and prevents later releases. The one-shot helper has a consumed marker and same-boot retry is forbidden.

The IQ producer remains a separate state machine for the already-proven R5/R6 image-IQ capsules. CQ also computes residual ISP gain for AEC, but **DB does not apply that ISP gain**. This checkpoint therefore claims only a bounded sensor-side native-AEC loop.

## Offline acceptance

`verify.py` proves the corrected parent range, DA timing/bootstrap, CV composition, CW atomic control parent, exact release-before-current-AEC ordering, one sensor-write call site, four-control cluster, schedule failure corpus, and warning-free canonical integrated helper build.

`prearm-check.sh` additionally reruns the inherited AI live-safety gate, rebuilds CW with `W=1`, requires CW module SHA-256 `72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1`, checks vermagic, and reruns DB verification.

No DB STREAMON or sensor write has occurred at this checkpoint.
