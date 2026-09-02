# E003h 0073 — byte-exact LSC41 runtime tuning-source closure

Status: **accepted static + Windows-live/offline byte-exact proof**. This closes the pre-calibration `x22` source that remained open in `LSC-RUNTIME-INTERPOLATION-BOUNDARY.md`. No Linux camera runtime or Linux request6 is performed or authorized.

## Result

The prior contradiction was real but its interpretation was wrong: Windows is **not numerically transforming the five serialized IMX681 LSC leaves** into a hidden runtime representation.

The first live generic interpolation input captured at DeviceMFT RVA `0x93c940` is SHA256

`d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d`.

That exact `0xdf0` byte sequence does not exist in `com.surface.tuned.ffc_imx681.bin`. It exists byte-for-byte in the Surface rear tuning package `com.surface.tuned.rfc_ov13858.bin` at absolute offset **1,008,426**, region symbol **0x2a0**. The callback's second input is SHA256

`f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8`,

which is rear region symbol **0x2a4** at absolute offset **1,012,018** and is the all-ones LSC mesh. The exploratory `E003H_20260902_LSCCALLBACK` capture independently records those exact two runtime buffers as callback A/B.

This proves byte provenance of the live runtime leaves. It does **not** by itself claim that Windows is configuring the rear physical sensor for the front stream. The remaining loader/overlay provenance question is why the front stream's resolved tuning root exposes this rear/default LSC41 object. That question no longer blocks reproducing LSC output.

## Exact rear/default LSC41 tree

`com.surface.tuned.rfc_ov13858.bin` SHA256 is

`4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`.

Its Default `lsc41_ife_v2` module is symbol `0x29`. The serialized module points to:

- revision `0x293`;
- control vector `0x294`;
- trigger root `0x295`.

The control vector is exactly:

`[8, 2, 5, 100, 0, 6]`

which is the same vector already recovered from the live DeviceMFT selector logic. It maps to live trigger-vector indices:

`[8, 2, 5, 19, 20, 21, 0, 6]`.

At the selector-0 level, symbol `0x299` has two populated bands:

- lower: `[1, 340]` -> CCT subtree `0x29a`;
- upper: `[430, 900]` -> CCT subtree `0x2a2`.

The lower CCT subtree has three regions; for the live CCT `4999`, it selects `[4800,10000]` -> region `0x2a0`, the exact runtime A mesh. The upper subtree has `[1,10000]` -> region `0x2a4`, the exact runtime B mesh.

Because the live selector-0 value is between 340 and 430, Qualcomm's generic tree builder interpolates those two child results with float32 ratio:

`ratio = float32((trigger - 340) / (430 - 340))`.

## Request5 / request6 byte-exact replay

For request5, live trigger-vector index 0 is `400.93280029296875`, giving float32 ratio:

`0.6770310997962952`.

The exact DeviceMFT callback at RVA `0x93c940` converts the float32 endpoints and ratio to float64, computes `(B-A)*ratio + A` in float64, then converts once back to float32. Replaying those instructions on rear regions `0x2a0/0x2a4` produces SHA256:

`e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`

which is **byte-for-byte identical** to the accepted Windows request5 `x22`.

For request6, live trigger-vector index 0 is `400.27227783203125`, giving float32 ratio:

`0.6696919798851013`.

The same replay produces SHA256:

`3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`

which is **byte-for-byte identical** to accepted Windows request6 `x22`.

The second callback observed in the exploratory capture receives the first callback result as both A and B, so it merely propagates that result to the root interpolation scratch. This matches the already-proven `x22` ABI at `LSC411Interpolation` post-point `0x93c8e8`.

## What this closes

The previously open chain

`serialized tuning -> unknown runtime LSC representation -> x22`

is replaced by the exact chain

`Surface rear/default LSC41 tree -> exact live trigger selection -> generic interpolation callback -> x22`.

No unexplained numerical materialization remains in the pre-calibration LSC41 stage for the validated request5/request6 pair.

The following downstream stages were already independently closed and remain unchanged:

`x22 -> golden/EEPROM calibration -> geometry/resampling -> sequential stateful Tintless -> 0x18a0 staging -> Titan680 LSC0/LSC1/LSC2 -> GIC`.

GTM/TMC is independently byte-exact.

## Remaining gate

The immediate next gate is an **integrated same-stream replay**, not more LSC trigger fitting: feed this now-byte-exact `x22` source through the already-closed downstream stages and compare one atomic request5/request6 capsule through Titan680/GIC. Separately document the tuning-loader/overlay provenance that causes the front stream to resolve this rear/default LSC branch, because that may matter elsewhere in the full stack.

Linux request6 remains fail-closed until the integrated parity proof passes and a separate runtime authorization review is made.

Proof: `prove-lsc-runtime-tuning-source.py`

Oracle: `lsc-runtime-tuning-source-oracle.json`
