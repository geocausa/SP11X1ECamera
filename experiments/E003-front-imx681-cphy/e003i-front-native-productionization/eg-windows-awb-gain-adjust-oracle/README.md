# E003i-EG — Windows same-request AWB GainAdj oracle

Status: **PASS — 8/8 same-request bit-exact contained-triangle GA and published AWB gains; Golden returned.**

A single bounded Windows boot captured eight paired `CTrigleAdjV1::Run` final states and the immediately following request-labelled `CAWBMain` frame-control publication for requests R4..R11. The live loaded `QcDeviceMFT8380.dll` hash matched the pinned authority (`c241b7...`). CDB was armed before stream start, self-detached after pair 8, the holder stopped normally, and the machine rebooted to persistent Golden Linux.

The first clean replay mismatch was diagnostic: raw AWB `(RG,BG)` is not the mesh lookup point. Static `GetCurrentTriangle` shows Windows selects a 10-slot camera calibration entry and multiplies raw RG/BG by reciprocal calibration factors before mesh selection. R4's authoritative barycentric weights originally recovered float32 scales `RG=0x3f80a277`, `BG=0x3f83427b`; EI independently captured that exact pair from the same-device Windows calibration table, and EJ now reconstructs the full 10-slot table bit-for-bit from the shipped `sensorCalV1` tuning plus the physical OTP bytes. `verify-eg.py` consumes EJ's clean result rather than carrying those values as its calibration source, and the pair still reproduces all R5..R11 mesh weights independently.

With that runtime calibration transform, the EF clean core reproduces for all eight requests, bit-for-bit: triangle 5 / vertices (22,12,28), barycentric weights, nested Lux/CCT RGB multiplier, final GA RGB adjustment, final published RGB gain triplet, and CCT integer publication. Publisher CCT is the pre-GA RG/BG temperature result truncated to integer; RGB is derived from GA-adjusted ratios.

The algorithm is therefore closed for the normal contained-triangle path. The remaining productionization gate is **where Linux obtains the same per-device RG/BG calibration pair**. Those values are not literal constants in the static tuning or sensor-module blobs and must not be hard-coded into the reusable clean core. Windows' rare out-of-mesh two-vertex fallback is also intentionally still fail-closed.

EL now consumes this publication path without oracle triangle hints, reproduces Windows stateful triangle identity R4..R11 8/8, and packs the resulting gains into the exact Titan680 PDPC/WB scalar words.
