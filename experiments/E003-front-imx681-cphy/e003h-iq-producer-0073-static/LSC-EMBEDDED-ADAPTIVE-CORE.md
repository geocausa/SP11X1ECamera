# E003h 0073 — exact IFELSC411 embedded Tintless / ALSC core boundary

Status: **accepted static/offline**. This checkpoint performs no Windows or Linux camera runtime and does not authorize Linux request6.

## The IFELSC411 adaptive algorithms are in the exact Surface DeviceMFT

The remaining LSC adaptive path is narrower than the earlier capture plan assumed. The SHA-pinned `QcDeviceMFT8380.dll` contains older LSC variants that dynamically load `libcamxtintlessalgo.dll`, but the exact **IFELSC411** creation path used by this Surface/Titan680 stack does not use that older loader path.

`IFELSC411::Create` at RVA `0xa01a20` constructs two interface objects directly inside the module:

- module `+0x19a0` → constructor RVA `0xc97258` → embedded Tintless `Process` `0xc95fd0`, `Destroy` `0xc97050`, and `FuseStats` `0xc97110`;
- module `+0x1998` → constructor RVA `0xc97428` → embedded ALSC `Process` `0xc972e0` and `Destroy` `0xc97370`.

Both constructors allocate their internal `0x1090`-byte wrapper context through RVA `0xc97508`. `TintlessAlgorithmWrapper::Process` dispatches to the exact embedded Tintless core at `0xca01b0`; stats fusion dispatches to `0xca1410`. `ALSCProcess` dispatches to the exact embedded ALSC core at `0xc975f0`.

`IFELSC411::RunCalculation` then wires those exact objects into the common LSC input:

- `common+0xb0 <- module+0x19a0` for Tintless;
- `common+0xb8 <- module+0x1998` for ALSC;
- when ALSC is enabled and AWB-BG stats exist, `common+0xa8 <- module+0x1c08`.

Therefore the **algorithm implementation itself is no longer an opaque Windows-only input**. It is recoverable from the exact Surface DeviceMFT and can be ported/replayed offline. The remaining Windows capture requirement is the dynamic input/state that feeds those embedded algorithms.

## Tintless is explicitly stateful

The exact embedded Tintless wrapper lazily allocates a `0x126e8`-byte core state object. Its `0x1090` wrapper context also retains four previous 221-float meshes at offsets:

`0x268`, `0x5dc`, `0x950`, `0xcc4`.

Each mesh is exactly `0x374` bytes, making the previous-output block a contiguous `0xdf0` bytes ending exactly at `+0x1038`; `+0x1038` is the previous-output-valid flag checked by the next call.

That closes an important sequencing requirement: **request6 LSC is not safely reproducible as an isolated one-frame calculation**. Offline replay must either start from stream creation and feed the adaptive inputs in request order, or begin from a precisely captured pre-request context state. For the eventual Linux implementation, sequential state evolution is the required model.

## ALSC AWB-BG stats are now bounded exactly

`LSC411Setting::CalculateHWSetting` passes the constant `0x00300040` to the embedded ALSC interface. The embedded core splits this into **64 × 48 = 3072** AWB-BG regions.

The first stats word bit 1 chooses the parsed-region layout:

- ordinary layout: stride `0x38`; highest referenced address ends at per-record `+0x58`; full 3072-region read boundary is **`0x2a020` bytes** from the stats base;
- saturated-info layout: stride `0x70`; highest referenced address ends at per-record `+0x90`; full boundary is **`0x54020` bytes** from the stats base.

So the future Windows capture no longer needs an unbounded/guessed AWB-BG object dump. Validate bit 1 first and take the matching bound; `0x54020` is the fail-closed maximum for this exact 64×48 path.

## Revised LSC parity gate

The exact offline producer path is now:

Chromatix base mesh + per-device EEPROM calibration + exact LSC geometry + **embedded Tintless replay with preserved history** + **embedded ALSC replay from bounded AWB-BG stats** → exact common LSC output → Titan680 packing → Windows `LSC0`/`LSC1`.

The preferred Windows validation capture is now adaptive inputs from stream start through request6 rather than only requests 4/5/6. A pre-request4 Tintless context checkpoint can be used as a validation shortcut, but the final Linux implementation must evolve the same state itself.

`prove-lsc-embedded-adaptive-core.py` pins the Surface DeviceMFT SHA and all critical ARM64 instructions for the constructor/dispatch, state-history, and ALSC read-boundary claims above.

## 2026-09-02 live branch validation

The subsequent Windows producer capture narrows the active IFELSC411 path for requests4/5/6: Tintless is enabled (`common+0xc0 == 1`), its request-local stats pointer at `common+0xa0` is non-null, and the stable Tintless interface at `common+0xb0` is present. In the same requests, `common+0xa8 == 0`, `common+0xb8 == 0`, and `common+0x10c == 0`; the captured ALSC state fields are also zero. **ALSC is therefore disabled in this live session.**

Exact analysis of `TintlessAlgorithmWrapper::Process` (`0xc95fd0`), its preprocessor (`0xc9f438`) and embedded core (`0xca01b0`) reduces the request-local Tintless stats object to a fail-closed conditional bound. `u32(stats+4)` must equal `0x300`; bit1 of `u32(stats+0)` selects 0x32- or 0x64-byte records; the readers cover records 0..767 and their highest per-record access ends at +0x50. The resulting maximum reads are **0x961e** or **0x12bec** bytes. See `LSC-LIVE-TINTLESS-BOUNDARY.md` and `lsc-live-tintless-boundary-oracle.json`.

The same capture also closes geometry as full 4048×3152, offset (104,496), output 3840×2160, scale 1. The remaining live LSC parity work is therefore calibration/config plus sequential Tintless state/stats, not ALSC and not unknown geometry.
