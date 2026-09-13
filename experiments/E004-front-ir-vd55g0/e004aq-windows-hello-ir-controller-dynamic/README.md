# E004aq — Windows Hello IR source-controller SecureISP dynamic oracle

## Result

PASS as the bounded Windows dynamic oracle.

This experiment reproduces the Windows Hello IR controller sequence recovered in E004ap and proves that the explicit SecureMode request enters the Qualcomm kernel SecureISP path on the installed SP11 Windows stack.

Linux SecureISP runtime remains **NOT AUTHORIZED**.

## Clean Windows run

The clean run used the Surface IR FaceAuth profile and the IR `MediaFrameSource.Controller`.

Observed:

- FaceAuthMode GET returned a valid 40-byte extended-property buffer, Flags 1, Capability 3.
- FaceAuthMode SET to Flags 2 returned Success and a following GET confirmed Flags 2.
- SecureMode GET returned a valid 40-byte buffer, Flags 1, Capability 3.
- SecureMode SET to Flags 2 returned Success and a following GET confirmed Flags 2.
- `MediaFrameReader.StartAsync` returned Success.
- 12 real IR frames were acquired at the expected 644x604 / 60 fps FaceAuth format.
- SecureMode remained Flags 2 during streaming.
- teardown returned both SecureMode and FaceAuthMode to Flags 1.

This closes the uncertainty left by profile-only experiments: selecting the FaceAuth profile is not sufficient, while the source-controller property sequence is sufficient to enter the protected Windows path.

## DeviceMFT negative result

A process-bound trace was armed on the live `QcDeviceMFT8380.dll` instance in FrameServer.

The exact E004aq property transaction produced zero accepted DeviceMFT breakpoint hits.

That is a useful ownership result: the Windows Hello source-controller control request is not being serviced through the Qualcomm DeviceMFT SecureMode broker traced in E004ao. The active transition is lower in the AVStream/kernel path.

## Kernel path proof

KD recovered the live driver objects and current driver starts rather than relying on stale module-list names:

- `QCCamAvs`: DriverStart `0xfffff80384620000`, size `0xad000`
- `CameraSecureISP`: DriverStart `0xfffff80384810000`, size `0x36000`

The E004z/E004ai RVAs were then armed against those live bases.

The dynamic trace recorded real execution of:

- QCCamAvs packet routing
- SecureISP operation dispatch
- SecureISP task dispatch
- SecureISP lane dispatch
- SecureISP `ConfigSecureCamera`

The instrumented rerun captured both sides of the secure transition:

- an enable-side `ConfigSecureCamera` hit with the recovered secure-state argument nonzero (`x2=1`)
- a teardown-side `ConfigSecureCamera` hit with that argument zero (`x2=0`)

The surrounding SecureISP operation-dispatch sequence was captured in the same bounded run.

The dedicated QCCamAvs SecureMode-setter breakpoint was not observed, so E004aq does **not** claim a setter hit. Acceptance rests on the successful source-controller GET/SET/GET transaction plus the downstream live SecureISP transition.

## Instrumentation note

The clean run is the frame-validity authority: it captured 12 real IR frames while SecureMode was confirmed enabled.

A later heavily instrumented rerun reached the same FaceAuthMode/SecureMode enable sequence and the SecureISP kernel transition, but acquired zero frames before its five-second deadline. The script's `finally` cleanup still completed and returned both controls to Flags 1. This rerun is used only as kernel-transition evidence, not as the frame-success authority.

## Golden return

The Windows oracle was entered through the one-shot Windows boot entry. After collection, SP11 rebooted directly back to the protected Linux Golden configuration.

Post-return verification:

- kernel `7.1.5-sp11-render-parity-v4+`
- `sp11_entry=7.1.5-sp11-fullio-v19c`
- saved GRUB entry `sp11-audio-fullio-v19c`
- empty `next_entry`
- BootCurrent `0005`
- BootOrder unchanged
- no `/dev/media*` or `/dev/video*`
- no camera modules loaded

## Evidence

- `evidence/E004AQ-WINDOWS-SUCCESS.txt` — clean 12-frame Windows authority
- `evidence/E004AQ-WINDOWS-KERNEL-TRACED-RERUN.txt` — instrumentation-heavy rerun and cleanup
- `evidence/E004AQ-DEVICEMFT-LOAD-HOLD.txt` — live FrameServer/QcDeviceMFT load hold
- `evidence/E004AQ_DEVICEMFT_TRACE.log` — process-bound DeviceMFT trace; zero actual E004AQ hits
- `evidence/E004AQ_KERNEL_SUMMARY.txt` — live driver bases, raw-trace hashes, actual hit counts, secure enable/disable transitions
- `PREBOOT-LINUX.txt`
- `POSTRETURN-GOLDEN.txt`

The full raw kernel trace is retained on SP7 under the E004AQ KDNET evidence directory and is identified by SHA256 in `E004AQ_KERNEL_SUMMARY.txt`.

## Next gate

E004aq satisfies the Windows dynamic oracle for the protected IR path. It does **not** itself authorize running or implementing SecureISP on Linux. The next checkpoint should translate the proven Windows ownership/sequence into a Linux implementation plan while keeping SecureISP runtime disabled until separately authorized.
