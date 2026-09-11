# E003i-EP — EO R9 GainAdj multi-side closure

Status: **PASS offline closure of the EO attempt1 R9 failure; no new camera runtime.**

EO attempt1 submitted R5–R8 successfully and then failed closed at G6/R9 because EL's first stateful selector rejected a simultaneous two-side crossing in triangle 10. The pinned Windows `CTrigleAdjV1::GetCurrentTriangle` implementation does not treat that case as out-of-mesh. It resolves the multi-side neighbor state and continues `10 -> 8 -> 16`; triangle 16 contains the calibrated G6 decision point.

The corrected EL path also removes an over-restrictive assertion that the internal GainAdj green component must be exactly `1.0`. EO G6 legitimately produces `GA=(0x3f8147ae,0x3f7fffff,0x3f7ae148)`. Windows' normal single-camera publication converts only `RG/GA_R` and `BG/GA_B`, then normalizes with `M=max(1, adjustedRG, adjustedBG)`, so the published triplet is `0x3fcd361f / 0x3f800000 / 0x400f0441`.

`verify-ep.py` hard-pins those values and the seven PDPC/WB words. When the externally archived EO evidence is available, it also reruns the real EN producer over all six EO live STATS3A/TL_BG snapshots with the exact live CQ gains. R5–R8 must remain byte-identical to the capsules EO actually submitted; corrected R9 must compose as SHA256 `209961646647ec9a2747a553c10139f1cd303dc3a5b6cf302deca6636f173191` in triangle 16.

This does **not** claim Windows' true boundary two-vertex fallback. That path remains fail-closed. Any further live attempt must use a fresh identity; EO is consumed and retired.
