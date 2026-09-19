# E004fu — bounded unilluminated optical capture into Linux IR worker

Status: OFFLINE PREPARED; NOT INSTALLED, ARMED OR CONSUMED. Fresh one-shot identity: the completed E004ft experiment must not be reused.

## One variable and scope

E004ft established live 16-frame *sensor-generated* pattern capture and ordinary Linux RGB888-to-NV12 bridge/IR pixel processing. E004fu reuses the byte-pinned E004fe camera binaries, IR-only GPIO-output-disabled DT, 16-frame libcamera capture, and independently built ordinary Linux bridge and worker. The only changed sensor setting is test_pattern=0 (Disabled) to capture actual unilluminated ambient optical samples. Exposure=1000 lines, analogue gain code=16 and digital unity remain as in E004ft. No emitter, flash, strobe, protected worker, firmware trust changes, PAM or enrollment. E004fs emitter safety gate remains BLOCKED.

The camera may produce virtually black frames without illumination. A transport/processing PASS does not demonstrate useful face images or authentication.

## Privacy and containment

One disposable GRUB candidate, Golden FullIO v19c saved default and untouched EFI BootOrder. The capture script arms an independent 120-second reboot timer before touching camera modules, and consumes the identity before capturing exactly 16 frames. Temporary optical RGB888 files reside only in a user-private (0700) runtime directory and are deleted on normal or error completion. The script retains only per-frame aggregate grayscale min/max/mean/p99 and fraction above 32, plus non-image kernel/capture lifecycle evidence. Do not save image hashes, face templates, raw frames or processed NV12 to GitHub. If the watchdog reboots SP11 before cleanup, remove orphaned raw images after returning to Golden before archiving. Do not claim successful cleanup until the file is actually absent.

Capture must verify test_pattern=0 via V4L2 and the sensor's Disabled readback in kernel logs, consecutive 16 buffers of 1169344 bytes, grayscale pixel format/zero padding, exact bridge/worker output sizes, kernel health, clean stop and sensor runtime suspension. A near-black but correctly captured image is reported as low-signal, not face recognition success.

## Procedure

Run overlap guard, offline camera/worker manifest verification and optical statistics tests, commit and push this prepared stage before installation or boot mutation. Check SP7 independent recovery access. Install the new candidate, verify hashes/Golden/BootOrder, arm exactly one boot, reboot, and run candidate.py capture ONCE. Return to Golden, confirm clean boot/camera state, clear any orphaned raw files, hash-verify and retire the candidate. Archive only aggregate numeric results and safe logs; commit and push the result. A failed test consumes E004fu and may not be retried during the same boot.

Independent hardware pulse/current/irradiance/timeout authority is still required before Linux illumination. No optical-quality or face-authentication claim follows from this experiment.
