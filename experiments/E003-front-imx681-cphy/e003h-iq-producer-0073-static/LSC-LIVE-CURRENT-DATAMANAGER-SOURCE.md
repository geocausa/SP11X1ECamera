# Live current DataManager source identity — 2026-09-03

## Scope

This checkpoint records a deliberately narrow live Windows observation from the repaired/current SP11 installation. It answers the source-buffer half of the private `DataManager` provenance question for the freshly constructed instance captured here. It does **not** retroactively identify the exact September 2 instance, and it does not authorize Linux request6.

## Fresh construction capture

SP7 KDNET caught a newly loaded `QcDeviceMFT8380.dll` in a fresh Windows Camera FrameServer before the private manager finished construction:

- FrameServer EPROCESS: `ffffde8a3a3e6100`;
- FrameServer PID: `0x1600`;
- DeviceMFT base: `0x00007ffb3a550000`;
- DeviceMFT image size: `0x1b74000`;
- `DataManager::Construct` RVA: `0x712f50`, live `0x00007ffb3ac62f50`.

At `DataManager::Construct` entry the live object was:

- `DataManager = 0x0000022b9f8cbb30`;
- `DataManager+0x30 = 0x62a5ef` bytes;
- `DataManager+0x38 = 0x0000022ba1680000`;
- `DataManager+0x28 = 0` at this pre-construction point, as expected before the fresh tuning manager is installed.

The complete `0x62a5ef`-byte source buffer was read out through KD without modifying target memory. The host-side raw dump is intentionally outside the repository:

`C:\Users\SurfacePro7\Documents\KDNET\Codex\E003H_FRONT_DM_SOURCE_20260903.bin`

Its exact identity is:

- bytes: **6,465,007** (`0x62a5ef`);
- SHA256: **`2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`**;
- first bytes decode as `QTI Chromatix Header`.

That SHA256 and byte count are exactly the installed/archived front tuning authority `com.surface.tuned.ffc_imx681.bin`. They are not the rear `com.surface.tuned.rfc_ov13858.bin` authority (`2,595,518` bytes, SHA256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`).

## What this closes

For this freshly constructed current-Windows private DataManager, the source handed into normal tuned-mode-tree construction is byte-for-byte **front IMX681 tuning**. A source-level substitution of the rear OV13858 tuning blob is therefore excluded for this instance.

This matters because the previously proven live LSC authority crossover cannot be explained simply by saying that this fresh private DataManager was initialized from the rear tuning file. The remaining explanation class is downstream of this source boundary: request/tree selection, explicit live-tuning replacement if enabled, an abnormal write/corruption path, or a distinction between the historical September 2 instance and this current clean instance.

## Remaining correlation gate

Do not over-claim this as the missing historical September 2 identity. The next clean stream capture must mechanically correlate this source identity with **front** request execution. The preferred same-stream proof is the existing atomic Tintless gate:

1. hook `TintlessAlgorithmWrapper::Process` at RVA `0xc95fd0` from stream creation;
2. require IMX681/front config geometry, not the rejected rear `4064x2286` geometry;
3. capture sequential `x1[0:0x130]`, validated `x2` stats, `x3/x4` descriptors and four `0x374` meshes each, plus wrapper/core state;
4. replay the exact native ARM64 wrapper into the already pinned verified-front pre-Tintless boundary.

Selected Sensor ID (`0x0aff` for front) can be captured alongside that sequence as an additional provider correlation, but front Tintless geometry plus the already-closed IMX681 sensor/receiver programming is sufficient to prevent reuse of the rear TINTCTX oracle.

## Safety

This capture was observational. Windows camera binaries, drivers, firmware, registry state and camera programming were not modified. Linux request6 remains forbidden until genuine same-front-stream sequential Tintless replay closes the producer gate.
