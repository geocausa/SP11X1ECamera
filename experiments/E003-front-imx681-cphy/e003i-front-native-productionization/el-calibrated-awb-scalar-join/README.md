# E003i-EL — calibrated AWB scalar join

Status: **PASS offline join; no new camera runtime.**

EL closes the remaining normal-preview AWB scalar seam between the request-local decision already produced by DS and the template-free Titan680 module state. It composes only already-proven pieces:

`held/fresh AWB decision (DS) -> EJ Linux-backed per-device calibration -> EF/EG GainAdj -> published RGB gains -> F exact PDPC/WB packing`.

The clean `awb_scalar.py` parses the shipped GainAdj tuning at runtime, obtains the active reciprocal calibration pair from EJ (which now requires EK's live Linux physical EEPROM proof), and implements the EG-proven publisher normalization. It then packs the four PDPC Q12 ratios and three WB Q10 words using the already-proven positive-domain Surface rounding. Normal-preview predictive gain is exact `1.0` under the BM/BP fixed-profile AEC authority; this is a profile fact, not a global WB assumption.

Two independent gates are required. First, the published RGB gains match the Windows EG same-request oracle for R4..R11 **8/8 bit-exact**, and the seven scalar words cross-check the pre-existing F backend. Second, the preserved successful EA Linux statistics sequence G1..G6 is replayed. All six frames take DR/DS HOLD_PREVIOUS and retain decision bits `0x3f1129ca/0x3f00e486`; after calibrated GainAdj every generation produces the already-accepted PDPC/WB words `1c80/1efc/08fc/0843` and `08000000/0f7e0000/0e400000`. Thus enabling the joined path would be regression-neutral on EA while providing a real dynamic path for non-held AWB decisions.

EL does not claim the rare out-of-mesh two-vertex GainAdj fallback. That remains fail-closed. No Linux camera module is loaded and no stream is run here.

Next gate: replace the inherited PDPC/WB words in the live composer with EL outputs, then generalize request7+ module/payload state using EB bank/GTM carry and ED sequential LSC/Tintless generation before any fresh bounded runtime candidate.
