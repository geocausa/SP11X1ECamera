# E003i-EJ — clean AWB calibration-factor replay

Status: **PASS 10/10 bit-exact for the proven SP11 front IMX681 two-anchor profile.**

This stage removes the captured Windows factor table as the source of calibration math. `cal_factors.py` reads the SHA-pinned shipped `sensorCalV1` tuning payload and the EI physical EEPROM window, reconstructs the two direct calibration factors plus Windows' special two-anchor midpoint, expands them into the proven 10-slot layout, and computes the reciprocal scales consumed by `CTrigleAdjV1`.

The tuning anchors are 2800 K `(RG=0x3f563583, BG=0x3ebc2efd)` and 6500 K `(RG=0x3f182603, BG=0x3f1725c4)`. The direct stored factors are `OTP/tuning`. For the middle region Windows performs float32 `(low+high)*0.5` independently on OTP and tuning, then divides those midpoint ratios. The resulting 10 pairs are bit-identical to EI's Windows oracle, including active reciprocal `(0x3f80a277,0x3f83427b)`.

The implementation is intentionally fail-closed and profile-specific. It does not claim the generic `sensorCalV1` algorithm for arbitrary cameras/counts. EK has now closed the runtime source gate: Linux reads the same physical 12-byte window from EEPROM `0x50` over CCI1 master1, byte-identical to EI. This clean calibration core is therefore backed by a native Linux physical source; integration into the normal producer path remains separate from the proof.
