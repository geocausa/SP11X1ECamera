# E003i-EO — bounded live R5–R9 one-shot

Status: **fresh unexecuted candidate until armed.**

EO is the fresh live successor to the consumed EA candidate. It keeps EA's six-frame/three-write sensor schedule and current-first parent ordering unchanged, while EN extends the generation-tagged CQ gain feed through G6 and submits five IQ requests:

`R5<-G2, R6<-G3, R7<-G4, R8<-G5, R9<-G6`.

R5/R6 remain on the exact EA composer path. R7–R9 use the EM component path: live CQ Demux, Linux-OTP-calibrated stateful GainAdj/PDPC/WB, sequential live LSC/Tintless, stable clean post-R6 GTM, parity banks and E template-free transport.

Safety remains bounded: six video/statistics generations, exactly three possible sensor writes (G1/G2/G3 released after completed G2/G3/G4), one helper invocation, no same-boot retry, fail-closed producer/parent behavior, whole-machine reboot after the attempt, persistent Golden saved entry, and fresh EO boot/helper identity. A pass proves this bounded five-IQ-request integration only; unrestricted continuous AEC is not claimed.
