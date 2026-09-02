# E003h 0073 — adaptive LSC/GTM producer-state boundary

Status: **accepted offline/static**. No camera runtime, MMIO, sensor operation or Linux request6 submission is authorized by this checkpoint.

## Why the remaining problem is not only AEC/AWB trigger interpolation

The exact IMX681 tuning objects and matched Windows request5/request6 trigger vectors now close the base interpolation boundary more tightly.

- LSC41's exact control vector is `[8, 2, 5, 100, 0, 6]`, matching its six-level lens-position → DRC → HDR-AEC → LED → AEC → CCT tree.
- GTM13's exact control vector is `[2, 5, 0]`, matching its DRC → HDR-AEC → AEC tree.
- LSC's final AEC branch spans `1..390` before the next branch begins at `490`; GTM's final AEC branch spans `1..900`.
- The matched request5/request6 real gains (`14.7202` → `43.2985`) and lux indices (`374.1765` → `374.1929`) remain inside those same first AEC branches. DRC gain, lens position and CCT are unchanged.
- CCT remains exactly `4999`, in the same `4500..5000` interpolation gap immediately below the `5000..10000` region.

This means the matched request5→6 trigger movement does **not** cross a new LSC or GTM Chromatix region. The exact Surface producer nevertheless has additional stateful paths after base interpolation.

## Exact LSC adaptive path

The SHA-pinned Surface DeviceMFT proves the full LSC411 path:

`IFELSC411::RunCalculation` → `IQInterface::LSC411CalculateSetting` → `LSC411Interpolation::RunInterpolation` → `LSC411Setting::CalculateHWSetting` → `IFELSC411Titan680::PackIQRegisterSetting`.

The implementation can combine the interpolated 4×221 mesh with:

- sensor lens-shading calibration tables;
- Tintless state/results;
- ALSC state driven by AWB-BG statistics;
- previous adaptive LSC state where the pipeline selects reuse.

The exact binary contains explicit `IFE Store Tintless`, `IFE Store ALSC`, `BPS UsePrevious Tintless` and `BPS UsePrevious ALSC` paths. More importantly, the exact IFELSC411 creation path now proves that its Tintless and ALSC implementations are **embedded in the same SHA-pinned DeviceMFT**: IFELSC411 constructs the Tintless interface at RVA `0xc97258` and ALSC interface at `0xc97428`, which dispatch to embedded cores at `0xca01b0` and `0xc975f0`. Older LSC variants in the image contain a dynamic `libcamxtintlessalgo` loader, but that is not the IFELSC411 path. The adaptive algorithm code itself is therefore no longer an opaque Windows-only dependency. See `LSC-EMBEDDED-ADAPTIVE-CORE.md` and `lsc-embedded-adaptive-core-oracle.json`.

The embedded Tintless wrapper is explicitly stateful: it retains four previous 221-float meshes as a contiguous `0xdf0`-byte history block ending at a previous-output-valid flag at `+0x1038`. Exact request6 replay must therefore preserve the stream sequence (or use an exact pre-request context only as a validation shortcut). The embedded ALSC call is also bounded precisely: Surface passes a `64x48` grid, and the parsed AWB-BG stats read is `0x2a020` bytes for the ordinary record format or `0x54020` bytes when saturated-info records are present. The hardware setting then scales four 221-point channels by Q10 `1024.0`, clamps to the 14-bit range, and the Titan680 packer emits the two changing `0x374`-byte LSC wire LUTs.

The Windows-selected IMX681 mode itself is already exact: firmware resolution index **2**, **3840×2160@30**. The 2026-09-02 live producer capture now also closes the LSC calculator geometry exactly and invariantly across requests4/5/6: full **4048×3152**, crop offset **(104,496)**, output **3840×2160**, scale **1**. The unresolved LSC state is adaptive/calibration/config content, not mode or geometry.

The static EEPROM side is now independently decoded as well. The Surface sensor-module descriptor enables one 221-point calibration light table whose four unsigned 16-bit channel arrays occupy one contiguous **0x6e8-byte** physical EEPROM window at `0x103d..0x1724`. `FormatLSCData` materializes that data into the exact `0xdf0` OTP-table layout consumed by IFELSC411. See `EEPROM-LSC-BOUNDARY.md` and `eeprom-lsc-boundary-oracle.json`.

## Exact GTM adaptive path

The default GTM13 region is a flat 257-point `4096.0` curve. Exact Surface `GTM131Interpolation` produces a `0x404`-byte 257-float region, but the downstream GTM hardware calculation has a separate TMC path selected through `IQInterface::IsModuleEnabledInTMCPath`.

When TMC is active, the hardware calculation consumes dynamic tone-mapping-control state and builds/reshapes the 257-point curve before the Titan680 `0x800`-byte LUT is packed. This cleanly explains why solving the static GTM Chromatix tree alone is not a sufficient producer model.

The exact generation-5 GTM read boundary is now closed as well. IFE GTM obtains the published TMC/ADRC object from `ISPInputData+0x21d0`, converts it into the internal layout consumed through GTM common-input `+0x50`, and calls the exact GTM131 hardware setting at RVA `0x9aa6e0`. The 2026-09-02 live producer session then validates the whole transformation end-to-end: generation 5, hardware `0x60800`, mode 2, and the exact Surface ARM64 helpers plus setting/packing reproduce **256/256 GTM qwords** for each captured request4/5/6. This independent stream is deliberately kept distinct from the older matched-trigger oracle. See `GTM-TMC-READ-BOUNDARY.md`, `GTM-LIVE-EXACT-REPLAY.md`, and their oracles.

A separate byte-level output proof confirms both adaptive requirements directly: all 24 possible assignments of the exact base LSC channels fail to reproduce matched Windows LSC0+LSC1 (best case still 1,496 byte differences), while the exact static GTM region is 257×4096 but matched Windows GTM base values span 4097..4442 with no 4096 entries. See `ADAPTIVE-IQ-OUTPUT-BOUNDARY.md`.

## Revised next gate

The live producer capture closes two previously unresolved boundaries:

- GTM's generation-5 TMC→GTM0 transform is byte-exact on an independent atomic Windows stream;
- LSC geometry is exact, and the live adaptive branch is **Tintless-only**: Tintless is enabled, while `common+0xa8`, `common+0xb8` and `common+0x10c` prove ALSC/AWB-BG is disabled.

Exact binary analysis further bounds the only live adaptive stats object. `stats+4` must equal `0x300`; bit1 of `stats+0` selects 0x32- or 0x64-byte records; both exact readers cover indices 0..767 through per-record end `+0x50`. Therefore the request-local Tintless stats read is exactly bounded to **0x961e bytes** (ordinary) or **0x12bec bytes** (bit1 layout). See `LSC-LIVE-TINTLESS-BOUNDARY.md`.

The remaining harder independent wire transform is now LSC: same-device calibration/config + exact **4048×3152 / (104,496) → 3840×2160, scale 1** geometry + **sequential Tintless stats/state** must regenerate **LSC0 + LSC1** byte-for-byte. Wire GIC then derives automatically from the already-proven LSC alias at source bytes `0x62e..0x82e`.

Because the new live producer session is not the earlier matched-trigger request4/5/6 stream, do not mix producer inputs from one with wire output from the other. Build or use one atomic Windows producer/output capsule and reproduce that stream offline. Linux request6 remains forbidden until that comparison passes.
