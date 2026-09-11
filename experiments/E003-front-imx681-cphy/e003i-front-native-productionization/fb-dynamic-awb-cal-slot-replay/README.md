# E003i-FB — dynamic AWB calibration-slot replay

Status: **PASS offline — EG 8/8 and FA 9/9 bit-exact.**

FA exposed a real gap in EL: EL correctly replayed the historical EG sequence but kept EJ's slot-0/high reciprocal calibration fixed. The longer FA run crosses Windows' calibration-selector boundary after R4, so R5–R12 use EJ's midpoint reciprocal factor instead.

FB preserves EL and EJ as historical closed stages. It reconstructs the missing Windows CAWBCtrlV1-to-CSFStatDistV1 selector from the pinned DeviceMFT control flow plus the SHA-pinned refPtV1/SFDistWVV1 tuning profile. For this SP11 front normal-preview profile, Windows always installs the special F-bound search line; its optional SFDist displacement remains outside the active adjustment envelope, so the static F-bound is used.

The resulting selector is deterministic on both independent same-machine Windows oracles:

- EG R4–R11: slot 3 throughout (EJ high region), 8/8 GainAdj + publication bit-exact.
- FA R4: slot 3 (high).
- FA R5–R12: slot 5 (EJ midpoint region), 9/9 GainAdj + publication bit-exact.

FB performs no camera I/O and adds no Windows stream. It is profile-specific and fail-closed on tuning payload drift.
