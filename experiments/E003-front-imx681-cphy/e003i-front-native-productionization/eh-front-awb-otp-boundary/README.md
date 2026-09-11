# E003i-EH — front AWB OTP boundary

Status: **PASS static boundary; physical 12-byte same-device EEPROM sample still required.**

This stage closes the source contract behind the runtime AWB calibration scales proven in EF/EG. The installed IMX681 module names its EEPROM `gt24p128f_imx681` at descriptor slave `0xA0` (Linux 7-bit `0x50`). Generic `EEPROMData::FormatWBData` is enabled with integer format 1, method 1, two light records, float32 qValue 1023, and third-channel inversion.

The only physical bytes needed for AWB are one contiguous 12-byte window `0x941..0x94c`: three little-endian u16 fields for the 2850 K light at `0x941/0x943/0x945`, followed by three for 5000 K at `0x947/0x949/0x94b`. Windows divides each integer by 1023. `FillIlluminantCalibrationFactor` forwards the first two formatted values as `ratioRG` and `ratioBG`; the third field is not part of the illuminant-factor input used by `ComputeCalFactors`.

The byte order is not inferred from host convention: the pinned ARM64 `FormatDataTypeInteger` format-1 path starts at the last byte of the masked field and folds bytes with `new | old<<8`, which gives ordinary little-endian u16 for mask `0xffff`.

Next gate: recover/read those 12 physical bytes on the same SP11, then replay `ComputeCalFactors` and prove they produce the EG runtime calibration scales `RG=0x3f80a277`, `BG=0x3f83427b` for the active slot. Do not hard-code those solved scales into production.
