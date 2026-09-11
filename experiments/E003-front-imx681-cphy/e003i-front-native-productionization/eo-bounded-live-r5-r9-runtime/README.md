# E003i-EO — bounded live R5–R9 one-shot

Status: **ATTEMPT1 CONSUMED / FAIL-CLOSED at R9 GainAdj selector; Golden return PASS; candidate retired.**

EO is the fresh live successor to the consumed EA candidate. It keeps EA's six-frame/three-write sensor schedule and current-first parent ordering unchanged, while EN extends the generation-tagged CQ gain feed through G6 and submits five IQ requests:

`R5<-G2, R6<-G3, R7<-G4, R8<-G5, R9<-G6`.

R5/R6 remain on the exact EA composer path. R7–R9 use the EM component path: live CQ Demux, Linux-OTP-calibrated stateful GainAdj/PDPC/WB, sequential live LSC/Tintless, stable clean post-R6 GTM, parity banks and E template-free transport.

Safety remains bounded: six video/statistics generations, exactly three possible sensor writes (G1/G2/G3 released after completed G2/G3/G4), one helper invocation, no same-boot retry, fail-closed producer/parent behavior, whole-machine reboot after the attempt, persistent Golden saved entry, and fresh EO boot/helper identity. A pass proves this bounded five-IQ-request integration only; unrestricted continuous AEC is not claimed.

## Attempt1 result — consumed

EO ran exactly once. The six-frame sensor/AEC schedule completed and R5–R8 were submitted successfully. At G6/R9 the producer failed closed before submission because the first EL selector treated a simultaneous two-side triangle crossing as the unimplemented out-of-mesh fallback. No same-boot retry occurred. The machine rebooted to Golden, `next_entry` cleared, camera modules/nodes were absent, and the EO boot identity was retired.

Subsequent static reconstruction proved the G6 point is still inside the configured mesh: Windows walks triangle `10 -> 8 -> 16`; triangle 16 contains the point. The corrected EL replay preserves EO's live R5–R8 capsule hashes byte-for-byte and composes R9 as `209961646647ec9a2747a553c10139f1cd303dc3a5b6cf302deca6636f173191`. EO remains consumed and must never be reused; any rerun requires a fresh boot/helper identity.
