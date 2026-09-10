# DB handoff — bounded native AEC sensor loop

Current state: **Attempt4 reproduced G4 -142, preserved the failure pair, and returned to Golden. DL reproduces the failure offline and proves the native loop omits Windows internal CapExposure.**

## Preconditions

- branch `experiment/e003-front-imx681-cphy`
- corrected range parent `c094198` is an ancestor
- Golden saved entry `sp11-audio-fullio-v19c`
- `next_entry` empty
- camera modules absent
- no prior `runtime-output/`
- `verify.py` and `prearm-check.sh` both PASS

## Live protocol

1. Commit/push this unexecuted package before any boot mutation.
2. Run `install-candidate.sh`; confirm it leaves `next_entry` empty.
3. Recheck Golden identity, boot assets, and no camera modules.
4. Run `arm-once.sh`; confirm only `sp11-camera-e003i-db-native-aec-one-shot` is in `next_entry` and saved Golden is unchanged.
5. Reboot once.
6. On candidate reconnect, identify it by `sp11_camera_e003i_db_native_aec=1` in `/proc/cmdline`; the kernel version intentionally matches Golden.
7. Run `load.sh` (which re-runs runtime preflight), then `prepare.sh`.
8. Before STREAMON inspect `CAPTURE-PREFLIGHT.txt`, `CONTROLS-AFTER.txt`, media identity, module load dmesg, and kernel health. Required bootstrap: FLL3562/VB1402/EXP3554/AGAIN0/DGAIN256.
9. Invoke `invoke-once.sh` exactly once using a **persistent PiMaster job**. Never use a finite command timeout for this pin-capable helper, and never retry in the same candidate boot.
10. Preserve/archive all outputs. If helper pins after STREAMON, inspect it from a separate command, do not stop/kill/restart it, and reboot the whole machine to Golden.
11. Reboot normally to saved Golden after the single run.
12. Run `golden-return-check.sh` and require candidate tag absent, saved Golden intact, next empty, camera modules absent.
13. Promote `RESULT.json` only after both live verification and Golden return are proven. Commit capture hashes/metadata, not multi-megabyte raw payloads.
14. Remove the disposable DB GRUB entry and `/boot` bundle after the post-live evidence is durable, then run `update-grub` and recheck Golden + Windows entries. Do not leave experiment boot clutter behind.

## Live acceptance

A PASS requires six exact AEC generations, exact G→G+3 ownership, three and only three writes, releases G1@G2/G2@G3/G3@G4, exact DQBUF window before and after each ioctl, matching CW hardware transactions, six paired TLBG/STATS3A identities, IQ producer PASS, STREAMOFF PASS, clean kernel health, and subsequent Golden return PASS.

## Scope warning

DB is sensor-side only. CQ computes residual ISP gain, but DB does not apply it. Do not call DB full/continuous AEC parity. G4-G6 controls are compute/observe only and are not released to the sensor in this gate.

## First candidate disposition / retry gate

First DB candidate on 2026-09-10 failed during cold-bootstrap preparation only: piecemeal `VIDIOC_S_CTRL` rejected exposure 3554 after VBLANK moved to 1402. No stream or native AEC helper ran, and no same-boot retry was performed. `PREPARE-FAILURE.txt` preserves the compact evidence. Golden return passed and the first disposable boot entry/directory were removed.

Retry code uses `bootstrap-controls.c` + `build-bootstrap.sh` and one four-field `VIDIOC_S_EXT_CTRLS`, with exact readback. Before another candidate boot, require a clean-tree full `prearm-check.sh` after committing this correction. On the retry candidate, do not bypass `prepare.sh`, and do not run twice in one boot.

## Second candidate disposition / DJ retry gate

Attempt2 reached STREAMON once, captured six frames, released G1@G2 and G2@G3, then failed closed at native AEC G3 with `RC=-142`. No G3 sensor tuple was written and no same-boot retry occurred. Golden return passed and the disposable candidate is absent.

Windows DG/DH confirms the policy-0 T681 rejection is correct. DJ fixes the upstream startup-coordinate mismatch: local G1 remains frame0 externally but maps to Windows request4/internal history frame3; requests1..3 are preseeded as real history with all exposure lanes 33,312,452 and PredGain 1.0, and request4 starts with Lux `0x4365acdd`. Exact archived attempt2 G1..G3 stats now pass offline through CU→CV. Before another candidate, commit/push DJ + DB integration explicitly, require a clean tree, then require full `prearm-check.sh` PASS.

## Third candidate disposition / DK diagnostic gate

Attempt3 proved DJ live through all three permitted sensor writes, then failed native AEC at G4 with `RC=-142`. Error composition is Short-lane T681 out-of-range. No fourth write occurred, the IQ producer passed, camera-fatal kernel markers were absent, Golden return passed, and the disposable boot entry/bundle are removed.

The exact G4 stats pair was lost because the old helper persisted raw pairs only after six-generation success. DK changes only failure evidence: schedule fail is latched before the already validated failing pair is fsync-saved as `TLBG-FAIL-GN.bin` and `STATS3A-FAIL-GN.bin`. Do not change AEC math until an exact G4 failure pair is captured and replayed offline. Before that diagnostic retry, commit/push DK + attempt3 evidence, require a clean-tree root prearm, and use a persistent job for the one-shot invocation.

## Fourth candidate disposition / DL

The persistent attempt4 reproduced G4 -142 after all three permitted writes. DK saved the exact G4 pair. The helper was left pinned until normal whole-machine Golden reboot; no kill or retry occurred. DL reproduces the same control tuples and error offline. Windows internal PopulateOutput calls CapExposure before publishing; native CG/DJ omit this stage. Recover exact request-local bounds and branch inputs before correcting native math or staging another runtime. Golden return passed and the candidate entry/bundle were retired.
