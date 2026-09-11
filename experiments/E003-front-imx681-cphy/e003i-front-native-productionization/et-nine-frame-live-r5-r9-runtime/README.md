# E003i-ET — fresh bounded nine-frame R5–R9 live successor

Status: **STAGED / NO CAMERA RUNTIME YET.**

ET is the fresh one-shot successor to consumed ER. ER proved the corrected IQ content through G6/R9 composition but exposed a six-frame transport ceiling. ET changes only that transport boundary: it uses ES's deterministic nine-frame CAMSS runner and nine-generation native helper/scheduler, while retaining the already-proven EN/EP IQ producer, CW IMX681 control driver, R4 bootstrap, three-write sensor schedule and Golden rollback discipline.

The kernel runner consumes R5..R9 monotonically. R7/R8/R9 each emit `E003I_ES_IQ_CONSUMED` immediately after successful provider dequeue and before their Epoch0 wait; live verification requires all three exact request/frame/slot markers plus the final bounded nine-frame completion line. Userspace must DQBUF exactly nine QC10C frames in buffer order `0,1,2,3,0,1,2,3,0`, preserve each frame before reuse, and obtain paired TL_BG/3A generations 1..9. Native AEC is evaluated through G9, but CQ residual gain publication remains G1..G6 and physical sensor writes remain exactly G1..G3 at completed G2/G3/G4.

One candidate boot may perform at most one camera stream attempt. Any failure pins/archives and requires whole-machine reboot; no same-boot retry. A PASS is still bounded nine-frame integration, not unrestricted continuous AEC.
