# E003i-EF — clean CTrigleAdjV1 AWB gain-adjust replay

Status: **PASS clean contained-triangle core; Windows same-request differential closed by EG, production stateful selection closed by EL.**

This stage reconstructs the normal contained-triangle path of the Surface front-camera `CamX::CTrigleAdjV1` AWB GainAdj engine without embedding proprietary tuning data. It parses the SHA-pinned shipped `com.surface.tuned.ffc_imx681.bin` through the repository QTI parameter parser at runtime.

Static authority is SHA-pinned `QcDeviceMFT8380.dll`. `CTrigleAdjV1::Run` reads the same AWB state field `+0x4f5dc` that `CSAAGWV1::Analyze` explicitly logs as `LUX_index`. It converts current decision `(RG,BG)` through the already-closed temperature converter and passes request-local **Lux + CCT** into the top-level GA trigger object.

The IMX681 `triglGAV1` tuning contains exactly **44 triangles**, **32 RG/BG vertices**, per-vertex Lux-index RGB curves, and a separate nested Lux/CCT RGB multiplier. Runtime `GetCurrentTriangle` first multiplies raw RG/BG by the selected per-device calibration reciprocal factors; `GetTriangleRatio` then uses 24-byte triangle records (first three int32 are vertex IDs), 32-byte runtime vertex records, absolute-area barycentric weights, and componentwise float32 interpolation. The final GA vector is the triangle RGB vector multiplied by the nested Lux/CCT RGB vector.

`gain_adjust.py` implements that contained-triangle path, takes the runtime RG/BG calibration scales explicitly as inputs, and fails closed for out-of-mesh decisions. It does not bake device-specific calibration into the clean core. Windows' rare two-vertex out-of-zone fallback is intentionally not guessed here.

`verify-ef.py` pins the tuning SHA, validates topology/neighbor reciprocity, checks all 44 triangle centroids, and exercises unity, per-vertex non-unity, nested CCT, and Lux-gap interpolation fixtures directly from the vendor table.

Superseding gates are closed by EG/EJ/EK/EL: Windows same-request GainAdj + publisher differential is 8/8, per-device calibration is reconstructed from the Linux-read physical OTP, and EL reproduces Windows stateful triangle selection before wiring published gains into the exact PDPC/WB scalar packer. `find_triangle()` remains a geometry/unit-test helper; production boundary/tie behavior must use the EL stateful selector.
