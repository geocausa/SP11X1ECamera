# EL static proof — stateful CTrigleAdjV1 triangle selection

Authority is SHA-pinned `QcDeviceMFT8380.dll` (`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`) and the shipped front IMX681 tuning SHA already pinned by EF/EJ.

The production selector is **not** a global first-containing-triangle search. `CTrigleAdjV1::GetCurrentTriangle` is the unnamed function at RVA `0x6bfcc0`. It carries a current triangle at object `+0x7c`. `Configure` (RVA `0x6be710`) resets that field to `-1`, binds triangle/vertex arrays, and binds the cold-seed selector structure at `+0x40`.

Cold selection calls RVA `0x6bfaa0`. It compares squared float32 distance from the calibrated RG/BG point to triangle centroids. The serialized `triglGAV1` header contains seed count `4` followed by triangle IDs **5, 19, 38, 41**. If a current triangle is valid it also participates as the first candidate. Strict `<` comparisons preserve earlier candidates on exact distance ties.

Containment uses helper RVA `0x6abd80`. Its three float32 edge cross-products are classified with exact thresholds:

- low: `0xb3d6bf95` = about `-1.00000001e-7`
- high: `0x33d6bf95` = about `+1.00000001e-7`

A cross-product inside that interval is zero for the sign test. When the selected triangle does not contain the point, `GetCurrentTriangle` follows the neighbor index associated with the crossed edge and persists the resulting triangle back to `+0x7c`. The rare multi-edge/out-of-zone two-vertex fallback remains outside EL and is fail-closed.

This tolerance/state rule matters for the EG R4 point: after the EJ calibration transform it lies effectively on shared vertex 28 and is accepted by both triangles 5 and 9. A naive global search selects triangle 9; Windows cold selection chooses seed triangle 5 and therefore produces the exact one-bit-sensitive GainAdj/published-gain result observed by EG. EL reproduces the stateful route without oracle triangle hints and matches Windows triangle identity and RGB publication for R4..R11 8/8.

## EO G6 multi-side traversal and single-camera publication

EO attempt1 exposed a case not present in the original EG R4..R11 oracle set. Its G6 decision is `RG=0x3f2146a9`, `BG=0x3ee089b0`; after the EJ calibration transform the mesh point is `0x3f22135c / 0x3ee64189`. With current triangle 10 `(28,16,8)`, the point crosses two sides simultaneously.

The decompiled `GetCurrentTriangle` multi-side branch does **not** immediately declare this out-of-zone. It resolves the triangle's neighbor slots and continues walking. For the EO point the exact state path is:

`triangle 10 -> triangle 8 -> triangle 16`

Triangle 16 `(25,8,29)` contains the point. Therefore EO's attempt1 failure was a Linux selector implementation bug, not evidence that this scene required Windows' true two-vertex boundary fallback. That rare fallback remains deliberately unclaimed/fail-closed.

At triangle 16, the final GainAdj vector is `R=0x3f8147ae`, `G=0x3f7fffff`, `B=0x3f7ae148`. The green component being one ULP below `1.0` is valid. `CTrigleAdjV1::Run` stores the full GA RGB vector, but the normal single-camera decision conversion stores only:

- adjusted RG = raw RG / GA_R
- adjusted BG = raw BG / GA_B

The downstream single-camera gain publisher then computes `M=max(1.0, adjustedRG, adjustedBG)` and emits `R=M/adjustedRG`, `G=M`, `B=M/adjustedBG`. GA_G is retained in shared state and is used by paths such as dual-camera mixing, but it is not an input to this normal single-camera ratio normalization. For EO G6 that yields published gains `0x3fcd361f / 0x3f800000 / 0x400f0441`.
