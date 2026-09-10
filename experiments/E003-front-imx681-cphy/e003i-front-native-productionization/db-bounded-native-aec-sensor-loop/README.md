# E003i DB — bounded native AEC sensor loop

> Current disposition (2026-09-10): attempt4 failed closed at G4 after three writes; failure evidence archived, Golden restored, candidate retired. DL proves an omitted internal Windows CapExposure stage. The earlier readiness/protocol text below is historical and does not authorize a repeat of this consumed candidate. See ../dl-native-aec-g4-failure-replay/HANDOFF.md.

Status: **ATTEMPT3 FAIL-CLOSED AT G4 AFTER ALL THREE ALLOWED WRITES; DK DIAGNOSTIC HARDENING OFFLINE**.

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

At the original unexecuted DB checkpoint no STREAMON had occurred. Attempt2 later performed one bounded STREAMON and two fail-closed sensor writes. Attempt3 ran DJ live and completed all three allowed sensor writes, then failed closed at G4; DK has not run live.

## 2026-09-10 first candidate preparation failure and retry fix

The first DB candidate boot reached preparation only. No STREAMON, DQBUF, native AEC helper execution, or DB sensor write occurred. `v4l2-ctl --set-ctrl=...` attempted the four clustered bootstrap values through piecemeal `VIDIOC_S_CTRL`; VBLANK advanced to 1402 but exposure remained 3546 and the exposure set returned `ERANGE`. The helper-consumed marker was absent. The boot was archived, no same-boot retry was made, SP11 returned to Golden, and the disposable candidate was removed.

CW's Linux 7.1.5 core proof already establishes the required transaction law: an extended-control set copies all caller values for a master cluster before one `try_ctrl`/`s_ctrl` callback. DB therefore now bootstraps with `bootstrap-controls.c`, one four-member `VIDIOC_S_EXT_CTRLS` containing VBLANK=1402, exposure=3554, analogue=0, digital=256, followed by an extended-control readback. The streaming helper and scheduler are unchanged. `prepare.sh` no longer contains any `--set-ctrl=` path.

## 2026-09-10 second candidate G3 fail-closed and DJ correction

The corrected bootstrap allowed the second DB candidate to STREAMON once and capture all six frames. G1/request4 and G2/request5 completed and exactly two scheduled sensor writes succeeded. G3 then failed native AEC with `-142`; DB latched failure, issued no third sensor write, stopped the stream, performed no same-boot retry, returned to Golden, and the disposable candidate was removed. `LIVE-FAILURE.txt` and the external attempt2 archive preserve the hashes.

DG and DH proved the `-142` endpoint is not a Linux T681 defect: Windows ordinary post-convergence policy 0 also rejects the same over-range G3 Short target. The root cause is earlier temporal state. W maps stats G1 to Windows request4, but CP initialized local G1 as request1, replacing Windows real requests1..3 with one synthetic start record. DC pins requests1..3 compact/retained exposure to 33,312,452 in every lane; DI pins their PredGain to exact `1.0f`; AB22 pins request4 entry Lux to `0x4365acdd`.

DJ preserves CU's local `G1 == frame_id 0` API and rebases only internal history by +3. It seeds those three real warm-up records and the request4 entry Lux. Replaying the exact archived failing G1/G2/G3 STATS3A bytes through the complete CU→CV chain passes all three, with CH unchanged. Attempt3 then validated that correction live by completing the G1/request4, G2/request5 and G3/request6 sensor writes.

## 2026-09-10 third candidate G4 fail-closed and DK evidence hardening

Attempt3 passed preparation and STREAMON once. All three bounded writes completed behind exact DQBUF gates: G1@G2→R4/G4, G2@G3→R5/G5, and G3@G4→R6/G6. The third control tuple was FLL6807 / exposure6798 / analogue960 / digital1072. G4 then returned `RC=-142`; exact error composition identifies this as Short-lane CH/T681 range failure. Because the bounded schedule had already released its third and final permitted write, no fourth write was possible or attempted. The IQ producer passed. Kernel camera-fatal markers remained absent, Golden return passed, and the disposable candidate was removed.

The old helper saved paired raw snapshots only after all six AEC generations succeeded. Consequently the already identity-validated G4 pair remained in RAM and was lost at reboot. DK fixes only that evidence gap: after an AEC error, it first permanently fails the schedule, then fsync-saves the current validated TLBG/STATS3A pair as `*-FAIL-GN.bin`. Successful generations still perform no per-generation disk writes, so the live control timing path is unchanged. No AEC/T681/sensor arithmetic is modified.

One orchestration error is preserved explicitly: attempt3 was launched through a finite 180-second command call. The helper intentionally pins after post-STREAMON failure, so the command layer eventually SIGTERM'd that pinned process. There was no retry; afterward no helper process or video opener remained and no camera-fatal kernel marker appeared. Future pin-capable invocations must use a persistent PiMaster job and be terminated only by the planned whole-machine reboot.

## Fourth candidate disposition / DL

The persistent attempt4 reproduced G4 -142 after all three permitted writes. DK saved the exact G4 pair. The helper was left pinned until normal whole-machine Golden reboot; no kill or retry occurred. DL reproduces the same control tuples and error offline. Windows internal PopulateOutput calls CapExposure before publishing; native CG/DJ omit this stage. Recover exact request-local bounds and branch inputs before correcting native math or staging another runtime. Golden return passed and the candidate entry/bundle were retired.
