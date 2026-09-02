# E003h 0073 — exact IMX681 EEPROM → LSC411 calibration boundary

Status: **accepted static/offline**. The deterministic proof passes twice byte-identically. No camera runtime or Linux request6 submission is part of this work.

The exact Surface sensor-module blob and exact `QcDeviceMFT8380.dll` close the static EEPROM side of LSC411 substantially further than the previous adaptive-state boundary.

## Static Surface EEPROM descriptor

The front IMX681 sensor module contains an `EEPROMDriverData` object whose generated Parameter Parser representation resolves to the LSC runtime fields consumed by `CamX::EEPROMData::FormatLSCData`. The LSC formatter is enabled (`runtime +0x160 == 1`), has exactly **one** `lightInfo` descriptor, configures **221 mesh samples**, and advances every channel descriptor by **2 bytes per sample**.

The selected `lightInfo` is SymbolTableID `3010`, light type `3`. Its eight 12-byte byte-field descriptors are four adjacent low/high pairs. All masks are `0xff` and all sign flags are zero. The pairs begin at EEPROM byte addresses:

- channel 0: low `0x103d`, high `0x103e`
- channel 1: low `0x11f7`, high `0x11f8`
- channel 2: low `0x13b1`, high `0x13b2`
- channel 3: low `0x156b`, high `0x156c`

`FormatLSCData` assembles each pair as an unsigned 16-bit value, converts it to float, and advances both byte descriptors by 2. Because each channel has 221 samples, the four source arrays are contiguous: **0x6e8 bytes total at EEPROM `0x103d..0x1724`**.

## Exact runtime OTP / IFELSC411 layout

`FormatLSCData` materializes each LSC calibration table as `0xdf0` bytes. `IFELSC411::CheckDependenceChange` looks for up to five such tables in `pOTPData` at `+0x168`, `+0xf58`, `+0x1d48`, `+0x2b38`, and `+0x3928`. A table participates only when its first dword is `1`.

For every available table IFELSC411 copies all `0xdf0` bytes and exposes four 221-float channel pointers at copied-table offsets `+0x0c`, `+0x380`, `+0x6f4`, and `+0xa68`. It records the number of available EEPROM tables at common-input `+0x68` and enables calibration through `+0x6c/+0x80` when that count is nonzero.

The exact LSC411 interpolation code later uses those four pointer slots in the same order as the four 221-float output planes, and performs the expected golden/EEPROM correction before request-local adaptive processing. Public older LSC34 source remains naming/architecture reference only; the offsets and instruction contracts above come from the exact Surface binary.

## Consequence

The static calibration descriptor is no longer opaque. The unresolved per-device calibration payload has been reduced to a precise **1,768-byte physical EEPROM window**. We should first search existing local Windows/cache/debug artifacts for those bytes. If they are absent, a future Windows oracle can capture only that bounded range or the already-materialized OTP table, rather than dumping an unknown EEPROM object.

This does **not** remove the other LSC adaptive inputs: request-local Tintless/ALSC state and LSC geometry/scale still have to be reproduced. GTM still requires request-local TMC state. Linux request6 remains forbidden until the complete offline LSC/GTM output matches the matched Windows request6 DMI bytes.
