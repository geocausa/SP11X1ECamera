# E003h 0073 — LSC41 runtime interpolation boundary

Status: **accepted Windows-live/static boundary checkpoint; upstream representation still open**. No Linux camera runtime or Linux request6 is authorized by this checkpoint.

## What the latest Windows pass closed

A deterministic on-device ARM64 CDB launcher attached to a fresh front-camera FrameServer stream early enough to capture request5 and request6 without chat/tool latency. At `LSC411Interpolation::RunInterpolation` post-point RVA **`0x93c8e8`**, exact ARM64 flow proves `x23` retains the function's `x1` destination argument and is the calibrated destination, while `x22` is loaded from generic interpolation scratch `[x20+0x38]` at RVA **`0x93c55c`** and is the **pre-calibration generic LSC41 interpolation result**.

The fresh local capture is stored only on Windows at `C:\Users\Geoca\Documents\SP11CameraOracle\E003H_20260902_LSCTRIGSRC`. Raw memory files are deliberately untracked; exact hashes are recorded in `lsc-runtime-interpolation-boundary-oracle.json`.

## Exact live LSC trigger source

`ISPInputData+0x17190` is a `std::vector<float>` object. In both requests its start/end/capacity resolve to exactly **42/42 floats**. Surface control vector `[8,2,5,100,0,6]` maps through the exact DeviceMFT control-selector logic to trigger-vector indices `[8,2,5,19,20,21,0,6]`.

Request5 mapped values are `[370, 1, 1, 1, 0, 0, 400.93280029296875, 4999]`. Request6 is identical except index0 becomes `400.27227783203125`. The adjacent common IQ trigger struct independently shows gain changing from `18.924766540527344` to `27.208637237548828`, while CCT=4999, lens=370, DRC=1 and AWB remain stable.

## The remaining contradiction is real

The exact Windows-installed `com.surface.tuned.ffc_imx681.bin` SHA256 is `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`, byte-identical to the archived tuning oracle. This is not a stale/different Windows tuning revision.

Scanning the entire serialized tuning container finds **25** region records of exactly `0xdf0` bytes, but they collapse to exactly **five unique payloads**, at offsets `3301034`, `3304602`, `3308170`, `3311738`, and `3315330`. These are the same five meshes already represented by the effective front `sid41` LSC tree; no sixth hidden serialized LSC payload exists.

Yet live pre-calibration `x22` is not reproduced by those serialized payloads under the current raw-container interpretation:

- request5 x22 SHA `e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`; best affine five-leaf fit RMS **0.06716552055**, best convex two-leaf fit RMS **0.07101981924**.
- request6 x22 SHA `3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`; best affine five-leaf fit RMS **0.06869178477**, best convex two-leaf fit RMS **0.07263366830**.

All 24 four-channel permutations failed materially. Simple identity/sqrt/reciprocal/rsqrt/square/log2 domain hypotheses also do not close the residual.

Because `x22` is conclusively **before** OTP calibration, EEPROM/OTP cannot explain this mismatch. `x23/x22` is stable across request5→6 as expected for static calibration, while only `x22` changes with the live interpolation input.

## What is already closed downstream

Do not reopen without new contrary evidence: GTM/TMC request4/5/6 replay is byte-exact (256/256 qwords); sequential Tintless request5→request6 is byte-exact including state; LSC calibration application and geometry/resampling are closed/bounded; `0x18a0` staging → Titan680 LSC0/LSC1/LSC2 is exact; LSC2 is zero on the validated stream; Windows GIC wire alias derives deterministically from LSC0/LSC1.

## Next gate

The remaining upstream problem is specifically: **how does the exact Surface runtime Chromatix object represent/materialize the LSC41 leaf data consumed by Qualcomm's generic interpolation engine?**

Static tracing has already checked two nearby helpers: DeviceMFT RVA `0x89d368` rebuilds the control-enum vector / interpolation scratch sizing and does not transform the 0xdf0 region payload; RVA `0x6f39f8` walks/selects the tuning object hierarchy and likewise shows no leaf-mesh transform. Do not repeat those two checks unless new evidence contradicts them.

Continue deeper static tracing of runtime object construction and the actual leaf pointers supplied to generic interpolation. If one more Windows observation is justified, capture the **actual runtime leaf pointer(s) and the `0xdf0` data they reference at request5/6**, not another broad ISP/Tintless dump. Compare those bytes directly to the serialized tuning leaves and live `x22`.

Only after runtime LSC interpolation is reproduced byte-for-byte should the full closed downstream chain be replayed against one atomic Windows oracle. **Linux request6 remains forbidden until that parity gate passes and a separate runtime authorization review is made.**

Proof: `prove-lsc-runtime-interpolation-boundary.py`

Oracle: `lsc-runtime-interpolation-boundary-oracle.json`
