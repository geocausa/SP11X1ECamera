# E003h 0073 — IMX681 Chromatix / IQ producer boundary

Status: **accepted static + Windows-live producer checkpoint**. A read-only Windows producer capture was performed on the native camera stream and is replayed offline here. No Linux camera runtime, Linux request6 submission, Linux MMIO/sensor experiment, or new kernel module was performed by this checkpoint.

## What is now decoded

The exact Surface IMX681 tuning blob is QTI Chromatix Parameter Parser V3.4.0. Its container is decoded as three contiguous sections. Section 0 is a fixed 56-byte `ParameterFileSymbolTableEntry` table; section 1 is serialized object data; section 2 is a 20-byte selector/mode index with 55 groups × 17 tuned-module slots.

A module symbol entry contains its SymbolTableID, 32-byte type name, version, ModeId/mode-symbol selection, section-1-relative data offset, and serialized byte length. The serialized module objects then contain SymbolTableIDs for child entries, matching the `ReadPointerEntry()` architecture used by Qualcomm's generated Parameter Parser.

## Front Sensor2 result

The already-proven IMX681 hardware mode maps to tuning selector **Sensor2**. Sensor2 exposes Preview, Snapshot and Video branches, but for the nine IFE modules needed by the proven Linux request materializer there are **no Sensor2/usecase overrides**. All three usecases inherit the same default objects:

- BPC/ABF41
- Demux/BLS14
- DSX10 video full/DC4
- Gamma15
- GIC31
- GTM13
- LSC41
- PDPC31
- WB20

Therefore the still-unresolved global Windows usecase does **not** block decoding these nine IFE modules.

## Pointer-tree proof

The decoder follows real SymbolTableID references from the default root objects into their control and trigger trees. Exact root chains are asserted for BPC/ABF41 (`0x44d/0x44e/0x44f`), GTM13 (`0x497/0x498/0x499`) and LSC41 (`0x4b0/0x4b1/0x4b2`). Region payloads are summarized and hashed rather than recursively interpreted as pointers, avoiding false references from numeric LUT data.

## Adaptive producer boundary

The common request4/5/6 trigger vector is now captured and its Surface field layout is pinned. Follow-up exact-binary work shows that this still does not contain the full remaining producer state. LSC411 can apply sensor calibration, Tintless and ALSC/AWB-BG state after base Chromatix interpolation, while GTM131 can apply dynamic TMC state. The matched request5/request6 trigger values remain in the same relevant LSC/GTM tuning zones, so these adaptive inputs are now the correct unresolved boundary. See `ADAPTIVE-IQ-STATE-BOUNDARY.md`.

The Windows-selected IMX681 sensor mode is separately exact as firmware mode 2, 3840x2160@30. The live producer capture now also closes the LSC calculator geometry exactly: full 4048x3152, crop offset (104,496), output 3840x2160, scale 1, invariant across requests4/5/6.

The static EEPROM calibration descriptor is now exact too: one enabled 221-point light table maps four contiguous u16 channel arrays to physical EEPROM `0x103d..0x1724` (0x6e8 bytes total), and the Surface formatter materializes the exact five-slot/0xdf0 OTP layout consumed by IFELSC411. The IFELSC411 adaptive algorithm boundary is now exact as well: its Tintless/ALSC interfaces and cores are embedded in the same Surface DeviceMFT, Tintless preserves a `0xdf0` previous-mesh history, and the 64x48 ALSC AWB-BG input is bounded to at most `0x54020` bytes. Therefore external Tintless/ALSC algorithm code is no longer an unresolved parity dependency; only its dynamic inputs/state remain. See `EEPROM-LSC-BOUNDARY.md`, `LSC-EMBEDDED-ADAPTIVE-CORE.md` and `ADAPTIVE-IQ-OUTPUT-BOUNDARY.md`.

The GTM adaptive input is no longer an opaque TMC object. Exact call/dispatch and helper proofs first bounded generation-5 reads; the 2026-09-02 live producer capture then closed the transform empirically and exactly. For TMC generation 5 / hardware `0x60800` / mode 2, the exact Surface ARM64 adaptive helpers plus GTM131/Titan680 setting math reproduce **256/256 qwords and all 0x800 bytes** for Windows requests4, 5 and 6. The live stream is distinct from the older matched-trigger oracle and is kept separate rather than falsely correlated. See `GTM-TMC-READ-BOUNDARY.md` and `GTM-LIVE-EXACT-REPLAY.md`.

The same live session now has an exact LSC wire target without another runtime capture. The exact Surface `IFELSC411Titan680::PackIQRegisterSetting` at RVA `0xb3d8a0` converts each captured **0x18a0-byte** post-calculation staging object into 13×17/221-dword LSC0, LSC1 and LSC2 payloads. LSC2 is all-zero for live requests4/5/6, while LSC0/LSC1 vary; the proven 512-byte GIC wire alias is derived directly from their concatenation. See `LSC-LIVE-STAGING-WIRE-TARGET.md`.

The upstream LSC calibration stage is now exact too. `IFELSC411` resolves Surface `lscgolden41_ife_v2`, translates the sensor EEPROM into up to five `0xdf0` formatted slots, and `LSC411Interpolation` applies **golden / EEPROM** ratios before geometry/Tintless. Windows deliberately averages the two independently calibrated green channels and writes that same green mesh to both outputs. The live requests4/5/6 all prove **exactly one valid calibration slot**, reducing the next Windows calibration capture from `0x45b0` to only **0xdf0 bytes**. See `LSC-CALIBRATION-APPLICATION-BOUNDARY.md`.

## Safety / next gate

Request6 is neither generated by this checkpoint nor authorized. The GTM transform is now closed on an independent atomic Windows producer session and the exact LSC geometry is captured. The next gate is a narrow same-stream Windows calibration capture followed by offline replay: acquire the single 0xdf0 copied formatted EEPROM LSC slot, then reproduce LSC41 trigger interpolation -> Surface golden/EEPROM calibration -> exact geometry -> sequential Tintless-only config/stats/state -> captured 0x18a0 staging. LSC0/LSC1/GIC then follow deterministically from the closed Titan680 packer. Runtime remains forbidden until the chosen atomic Windows oracle is reproduced byte-for-byte and a separate authorization review passes.
