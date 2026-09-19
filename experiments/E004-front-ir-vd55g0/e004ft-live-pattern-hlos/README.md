# E004ft — first bounded live Linux IR capture-to-HLOS worker test

Status: **PASS — FRESH LIVE ONE-SHOT CONSUMED, RETIRED TO GOLDEN (2026-09-19)**. E004ft captured and processed 16 current-session generated-pattern frames with ordinary Linux userspace; it is not eligible for another run. E004fe remains separately consumed.

## Hypothesis and one variable

E004fe already proved a 16-frame 644×604 RGB888 generated grayscale pattern captured with an isolated libcamera 0.7.0 build and a native VD55G0 sensor driver with all GPIO outputs disabled. E004ft reuses those **hash-pinned, immutable** sensor/CAMSS modules, IR-only DTB, firmware artifact, userspace camera app, IPA and fixed exposure/gain test-pattern configuration. Its **only new runtime variable** is passing frames captured during this one live session through the newly built unprotected Linux RGB888→NV12 bridge and 16-frame Windows-derived pixel processor.

This tests live generated-pattern capture → ordinary Linux userspace processing, **not an optical image, emitter, face identification, spoof detection or login**. No CPZ/SecurePD buffers are accessed, no firmware verification is modified, and no IR emitter is armed.

## Build, preflight and one-shot controls

- `python3 prepare_hlos.py` compiles the bridge and worker on Golden and records exact source/binary SHA-256s in `evidence/HLOS-BINARIES.json`. Both binaries live only in this candidate's ignored `build/` directory. The E004fe camera artifacts remain in its original build directory and are reverified rather than copied or modified.
- Before any mutation, run the camera overlap guard with `--require-clean-tracked --require-golden --require-no-camera-process`. Verify empty GRUB next entry, Golden saved default, camera idle, and source/artifact/binary checksums. **Checkpoint and push this candidate before installing or arming.**
- `candidate.py install` creates only a **separate** `/boot/sp11-7.1.5-camera-e004ft-native-ir` candidate, its one-shot GRUB entry, and the exact E004fe-derived required sensor firmware at its previously empty path. It does not overwrite Golden or install a protected IR worker.
- `candidate.py arm` verifies the installed artifacts, clean tracked tree and remote HEAD match, then arms one-shot GRUB. Reboot once. The disposable camera boot retains a 120-second independent Golden-return timer, registered before camera artifact verification or module load. An interrupted chat is not permission for a same-boot retry.
- In the one-shot boot, invoke `candidate.py capture` **once**, with independent SP7/PiMaster recovery available. The script confirms the one-shot boot marker, no pre-existing camera nodes/modules, intact binary hashes and no emitter capability; captures exactly 16 generated-pattern frames with the original strict format/sequence/media/PM checks; runs them through both HLOS executables; records hashes/counts only; deletes raw captured frames on normal and error exit; and requests the Golden return.
- After SP11 reconnects, verify Golden saved default, empty next entry, BootOrder and absence of camera nodes/modules/processes. Archive the bounded numeric/log evidence, run `candidate.py retire` to remove only the exact candidate files, and checkpoint the result. **Never retry E004ft in the same boot or reuse it after consumption.**

## Gates

A successful outcome requires a verified fresh 16-frame libcamera capture, no test-pattern/firmware/CAMSS drift, 16 processed NV12 frames with correct length and neutral chroma, camera stop, no kernel faults, and sensor runtime suspension. A failed capture or worker check is a failed experiment, not an instruction to change camera or emitter settings during that boot.

## Actual result — accepted and retired

A single fresh E004ft one-shot boot captured 16 consecutive live VD55G0 **sensor-generated horizontal grayscale pattern** frames with GPIO outputs disabled. It then passed those *same session's* 16 × 644×604 RGB888 frames to the independently built Linux RGB888→NV12 bridge and ordinary Linux HLOS parity processor. All 16 resulting processed NV12 frames matched the established pinned offline generated-pattern output digest `ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df`. The capture digest was `33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3`. These are deterministic test-pattern values, **not optical face images**. One camera stream/capture, 16/16 numbered frames, camera stop, sensor runtime suspension, and kernel-health gates passed. No protected worker, login/PAM changes or IR illumination were used.

The one-shot's scheduled reboot returned SP11 to protected Golden FullIO v19c (`df3233f3-c19e-491a-ab98-928893f39603`). BootOrder `0005,0004,0000,0001,0002,0006`, saved Golden default, empty `next_entry`, no camera nodes/modules/processes, and removal of the disposable boot entry, boot files and sensor firmware were verified. The raw generated-pattern payload was deleted. `verify_result.py` checks the hash-pinned capture/kernel text logs, lifecycle markers and bounded result, then emits `evidence/RESULT.json`. These non-image capture/kernel logs and lifecycle markers are checkpointed; expanded media inventories remain local and are identified by the project evidence state.

The E004fs emitter safety gate remains **BLOCKED**. Native illumination, biometric enrollment and PAM changes were not attempted. The next live question is **ordinary unilluminated optical capture** in a separate fresh one-shot identity; E004ft cannot be reused. Current HLOS output establishes pixel processing of camera-generated frames, not optical quality, face identification, liveness or working login.
