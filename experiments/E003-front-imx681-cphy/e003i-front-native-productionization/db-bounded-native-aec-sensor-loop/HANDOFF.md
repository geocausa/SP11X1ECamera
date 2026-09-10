# DB handoff — bounded native AEC sensor loop

Current intended state: **READY_UNEXECUTED** on Golden Linux.

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
9. Invoke `invoke-once.sh` exactly once. Never retry in the same candidate boot, regardless of success or failure.
10. Preserve/archive all outputs. If helper pins after STREAMON, do not kill/restart the camera path; reboot to Golden.
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
