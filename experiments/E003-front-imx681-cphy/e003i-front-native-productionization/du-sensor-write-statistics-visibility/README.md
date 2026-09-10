# E003i-DU — sensor write → statistics visibility closure

Status: **PASS (cross-runtime evidence; no new camera run).**

CX closed the Windows software apply boundary but deliberately left the optical first-affected frame open. CY then performed the dedicated hardware experiment CX requested: exactly one group-held IMX681 exposure step immediately after completed V4L2 sequence 0 / statistics generation G1, while keeping FLL and gains fixed. Its BHist stayed baseline-like at G2 and first changed strongly at G3.

Therefore the measured Linux sensor visibility law for this front mode and CW transaction is:

`write immediately after completed generation N -> first optically affected statistics generation N+2`.

DT uses the same CW IMX681 module and releases its three sensor transactions immediately after completed generations G2, G3 and G4. Applying CY's measured visibility boundary maps them to G4, G5 and G6 respectively, exactly matching the scheduler's existing effect labels.

This closes the timing label used by the bounded native-AEC schedule. It does not claim that scene-dependent luma magnitude in DT can independently identify each control tuple, and it does not turn the six-frame bounded loop into unrestricted continuous AEC.

No new camera runtime is performed by DU.
