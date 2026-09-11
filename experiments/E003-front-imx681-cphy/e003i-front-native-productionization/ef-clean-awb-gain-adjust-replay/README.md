# E003i-EF — clean CTrigleAdjV1 AWB gain-adjust replay

Status: **OFFLINE STATIC CORE — Windows same-request differential still required.**

This stage reconstructs the normal contained-triangle path of the Surface front-camera `CamX::CTrigleAdjV1` AWB GainAdj engine without embedding proprietary tuning data. It parses the SHA-pinned shipped `com.surface.tuned.ffc_imx681.bin` through the repository QTI parameter parser at runtime.

Static authority is SHA-pinned `QcDeviceMFT8380.dll`. `CTrigleAdjV1::Run` reads the same AWB state field `+0x4f5dc` that `CSAAGWV1::Analyze` explicitly logs as `LUX_index`. It converts current decision `(RG,BG)` through the already-closed temperature converter and passes request-local **Lux + CCT** into the top-level GA trigger object.

The IMX681 `triglGAV1` tuning contains exactly **44 triangles**, **32 RG/BG vertices**, per-vertex Lux-index RGB curves, and a separate nested Lux/CCT RGB multiplier. Runtime `GetTriangleRatio` uses 24-byte triangle records (first three int32 are vertex IDs), 32-byte runtime vertex records, absolute-area barycentric weights, and componentwise float32 interpolation. The final GA vector is the triangle RGB vector multiplied by the nested Lux/CCT RGB vector.

`gain_adjust.py` implements that contained-triangle path and fails closed for out-of-mesh decisions. Windows' rare two-vertex out-of-zone fallback is intentionally not guessed here.

`verify-ef.py` pins the tuning SHA, validates topology/neighbor reciprocity, checks all 44 triangle centroids, and exercises unity, per-vertex non-unity, nested CCT, and Lux-gap interpolation fixtures directly from the vendor table.

Next gate: capture same-request Windows `(RG,BG, Lux, converted CCT, GA final RGB)` plus the request-labelled AWB frame-control publication and differential-test this core. Only after that proof may final AWB gains be wired into the existing WB/PDPC scalar backend.
