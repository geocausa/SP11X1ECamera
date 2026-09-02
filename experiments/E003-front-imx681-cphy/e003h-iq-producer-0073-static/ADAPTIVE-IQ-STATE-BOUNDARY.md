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

The exact binary contains explicit `IFE Store Tintless`, `IFE Store ALSC`, `BPS UsePrevious Tintless` and `BPS UsePrevious ALSC` paths. The hardware setting then scales four 221-point channels by Q10 `1024.0`, clamps to the 14-bit range, and the Titan680 packer emits the two changing `0x374`-byte LSC wire LUTs. Therefore a pure Chromatix+AEC/AWB producer is incomplete for Windows parity.

The Windows-selected IMX681 mode itself is already exact: firmware resolution index **2**, **3840×2160@30**. What remains to be captured is the exact LSC calculator's per-request output/crop offsets and scale plus its adaptive/calibration state, not the sensor mode selection.

## Exact GTM adaptive path

The default GTM13 region is a flat 257-point `4096.0` curve. Exact Surface `GTM131Interpolation` produces a `0x404`-byte 257-float region, but the downstream GTM hardware calculation has a separate TMC path selected through `IQInterface::IsModuleEnabledInTMCPath`.

When TMC is active, the hardware calculation consumes dynamic tone-mapping-control state and builds/reshapes the 257-point curve before the Titan680 `0x800`-byte LUT is packed. This cleanly explains why solving the static GTM Chromatix tree alone is not a sufficient producer model.

## Revised next gate

The remaining independent Windows-wire producer inputs are now bounded to:

1. exact per-request **LSC calibration + Tintless/ALSC adaptive state**, plus its calculator geometry offsets/scale;
2. exact per-request **GTM TMC state**.

After those inputs are captured for the same Windows request sequence, regenerate **LSC0 + LSC1 + GTM0** offline and require byte-for-byte equality with the Windows oracle. The Windows GIC wire payload is then derived automatically from the already-proven LSC alias at source bytes `0x62e..0x82e`.

Linux request6 remains forbidden until that offline comparison passes.
