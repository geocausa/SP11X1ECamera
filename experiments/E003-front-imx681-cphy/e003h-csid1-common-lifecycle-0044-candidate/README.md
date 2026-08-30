# E003h — CSID1 common lifecycle 0044 one-shot candidate

Fresh package for static patch `0044-x1e-csid1-common-lifecycle-windows-parity.patch`.

It reuses the byte-proven Golden kernel/initrd, accepted front-only DTB, IMX681 module, PIX capsule/helper, media setup and persistent RT-CDM observer. The only camera-code change from the consumed 0043 package is qcom-camss SHA-256 `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`, which implements the exact front-mode0 Windows CSID1 common reset/config/companion/enable/stop lifecycle closed by static 0044.

- GRUB ID: `sp11-camera-e003h-csid1-0044-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-csid1-0044`
- command-line marker: `sp11_camera_e003h_csid1_0044=1`
- candidate CAMSS SHA-256: `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`

Package creation/installation **does not authorize or arm runtime**. `AUTHORIZATION.json` must be absent at this gate. The installer must leave Golden as `saved_entry` and `next_entry` empty. A hardware RUN requires a later, separate authorization checkpoint.

## v2 runtime-harness correction

The first authorized 0044 candidate boot was consumed before camera execution because the package-only `preflight.sh` was mistakenly invoked after authorization; it correctly rejected the active authorization. No camera modules were loaded, the helper was never entered, and Golden return is verified. The original authorization is preserved as `AUTHORIZATION-BOOT1-CONSUMED.json` with `BOOT1-CONSUMPTION.json` and pre-exec evidence.

`runtime-preflight.sh` is now the authorization-aware candidate-boot gate. `load-candidate.sh` calls it before any `modprobe`/`insmod`. The package-only `preflight.sh` remains intentionally authorization-free. No replacement runtime is authorized by this harness correction itself.

## Harness v3

Boot 2 was consumed before module load because the authorization-aware preflight invoked `git merge-base` without a repository cwd. Both `runtime-preflight.sh` and `run-once.sh` now use explicit `git -C <repo> merge-base --is-ancestor`; package v3 pins those hashes and both zero-hardware boot-consumption records. No active authorization remains after this correction.
