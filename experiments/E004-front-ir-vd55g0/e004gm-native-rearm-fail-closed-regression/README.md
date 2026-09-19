# E004gm — verify Linux rearm fails closed after a failed prior OFF request

PASS (offline C source, ASan/UBSan). No flash patch installed or emitter activated.

E004gl Ghidra and original Windows ARM64 instruction execution identified a specific OEM software behavior: when Windows thinks flash was previously active and a previous OFF request reports failure, the examined flash-start function still requests current, timer and ON, and can report success. This is a software protocol gap, not evidence of the real LED state.

This stage compares that exact previously proven Windows branch against the actual Linux candidate C source, not a handwritten Linux behavior model. The isolated E004fz flash callback source already applies the uninstalled patches 0003 and 0004. The new offline regression uses E004fz's exact SHA-pinned source reconstruction, compiles the REAL patched qcom_flash_strobe C callback with AddressSanitizer/UndefinedBehaviorSanitizer, and injects a failed initial OFF request. It asserts the Linux callback returns an error, requests best-effort channel then module disarm, and makes no new current, timer, module-enable or strobe-on request. It also tests a successful normal request and a simulated bus failure in which both cleanup attempts fail and the modeled hardware can remain ON.

This establishes that the existing uninstalled Linux source deliberately avoids the observed Windows rearm-after-OFF-error software weakness. It does NOT establish safe native illumination, eliminate hardware failure, or prove an autonomous PMIC timeout/current/optical exposure limit. A failed SPMI request may leave the actual LED energized regardless of software state or rollback attempts. Ghidra findings never substitute for physical electrical/optical measurements.

Reproduce offline from repository root:

    python3 experiments/E004-front-ir-vd55g0/e004gm-native-rearm-fail-closed-regression/test_native_gate.py

This also reruns the E004gl original Windows ARM64 CPU negative test and E004fz six-fault-stage compiled-C regression. The exact isolated Linux driver source and rollback patch are pinned; no binary module, firmware, Windows PE or user image is committed. No camera boot, PMIC access, Windows/KD, IR light, PAM/login or Golden change occurred. E004fs/E004ge physical safety gates remain BLOCKED.
