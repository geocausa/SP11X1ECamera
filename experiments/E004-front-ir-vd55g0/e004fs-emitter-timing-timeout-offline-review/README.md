# E004fs — IR emitter timing/current/timeout authority review (offline only)

Status: **OFFLINE REVIEW IN PROGRESS / EMITTER ACTIVATION BLOCKED**. E004fr's bounded Windows trace is verified and archived in commit `feec525`; no E004fs hardware experiment has been performed.

## Current evidence and limits

- E004fp recorded seven successful Windows PMIC read/modify/write pairs during one 12-frame normal IR preview. Windows programmed paired LED1 sources 1/4, each low-three-bit trigger code `0x05`, and cleared `0xee67` bit 0. No PMIC timer-register write to `0xee3e..0xee41` occurred **within that session**; this does not establish that no timeout mechanism exists.
- E004fr captured another 12-frame Windows preview and 114 contiguous sensor register-write calls. The `0x044e/0x044f` 16-bit coarse exposure rose from 32 to 1955 lines; `0x0458/0x0459` frame length changed from 1955 to 2000 lines. The standard Windows exposure API's constant 0.5 ms readback was **not** a reliable description of those driver writes. Sixteen programming groups are not asserted to align 1:1 with twelve acquired frames. No `0x0467..0x046e` strobe-control write appeared in this bounded capture.
- The pinned Windows sensor package programs GPIO1 to STROBE mode with zero strobe-edge shifts at first start, and the ST register documentation describes a sensor integration-time strobe envelope. The observed register writes do not directly measure the GPIO output, emitted pulse width, IR current or irradiance.

## Review tasks before any native emitter attempt

1. Identify and pin the exact validated sensor line-time and frame-clock authority; distinguish initial/static settings from subsequent driver writes. Derive a conservative pulse-time ceiling in physical units **only when those clock data are verified**.
2. Reconcile the already-observed Windows LED1 routing, selected trigger edge/polarity, and common enable/disable ordering with the Linux device-tree/PMIC GPIO and a verifiable off-state. Distinguish a sensor-strobe-controlled current path from a software-driven flash.
3. Investigate PMIC LED current configuration and timer/timeout register semantics using the exact available hardware documentation and installed Windows driver, including which device/host authority actually terminates illumination on stream stop, process crash, missed frame, and suspend. Absence of a timer write in one capture is not proof of a safe native policy.
4. Specify conservative independent timeouts, software and hardware fail-safe off paths, activation/deactivation ordering, and a bounded test identity with forced Golden return; require reliable evidence for every bound. If a hardware-backed shutdown cannot be justified, do **not** run an illuminated Linux experiment.
5. Keep the existing HLOS ordinary Linux IR pixel processor independent from the protected Qualcomm SecurePD worker. Offline format/algorithm proof is not face detection, liveness or login authentication.


## Current offline disposition (2026-09-19)

Re-ran the existing E004fl static trigger/initial-timing verifier and E004fi conditional PMIC-routing verifier on Golden Ubuntu; both completed successfully. Their own results explicitly leave runtime timer use, physical wiring and pulse limits unproven. E004fr now bounds the Windows *software-requested* coarse exposure to 32–1955 lines in one preview, but does not measure line time, electrical strobe edges, PMIC current, or independent emitter shutoff on loss of camera stream. The E004fl 137.6 MHz clock is a **Linux-side** observation and must not silently be assumed to apply to the observed Windows session; the 700 mA Windows request is not a measured safe optical power or sustained-duty specification. In particular, do not treat the nominal 1270 ms PMIC timer-helper default as proven active in the type-0 Windows path. **Gate outcome: blocked pending independently verifiable pulse-duration/current limits and fail-safe off/timeout authority.** No emitter payload was built or installed, no one-shot camera boot was armed, and no IR light was activated in E004fs.

## Reproducible E004fs line-count reconciliation

Run `python3 assess_gate.py` and `python3 test_assess_gate.py` in this directory. The first pins the raw E004fr Windows KD/capture archive hashes, checks E004fp and E004fr bounded result contracts and reproduces all sixteen paired coarse-exposure/frame-length register values in `evidence/RESULT.json`. The second checks the valid evidence is **still blocked** and that six tampered/mismatched evidence cases are rejected. Both are offline and have no camera/PMIC interface.

**Concrete bound from the observed register pairs:** the largest coarse value is 1,955 lines and its paired frame length is 2,000 lines: 97.75% as a *dimensionless line-count ratio*. There are **zero** observed groups with exposure equal to frame length. The 1,866/1,955 group is approximately 95.45%. The sixteen programming groups cannot be matched frame-for-frame with the twelve acquired images. Line-count ratios are **not measured optical duty cycle or IR emission time**: Windows line clock during this run, actual GPIO pulse edges and electrical LED behaviour remain unknown. Linux's separately observed 137.6 MHz clock is not a measurement of this Windows run. The Windows preview reports 60 fps but the acquired frame timestamps are not authoritative pulse timestamps.

**Gate conclusion:** the ratio is a warning that sensor integration can occupy nearly the entire programmed frame, not permission to run a long illumination pulse. The 700 mA Windows request is nominal, not a physically validated SP11 optical exposure limit. No independent hard cutoff on a stuck-high strobe or stalled host is verified, and one PMIC trace's missing timer writes cannot establish timer state. Until timing, current/irradiance limits and fault-independent shutdown are proven, the native emitter remains OFF even though the ordinary IR pixel worker operates offline.

Do not reboot, enable LED/flash/strobe output, change protected firmware, enroll a face, install PAM modules or alter Golden during this **offline-only** review. E004fp, E004fq and E004fr have all been consumed. Any future hardware experiment must use a fresh identity and pass a new read-only preflight.
