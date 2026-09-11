# E003i-ET — consumed bounded nine-frame R5–R9 live successor

Status: **ATTEMPT1 CONSUMED / FAIL-CLOSED at G4 gain-feed publication; Golden return PASS; candidate retired.**

ET performed exactly one camera stream attempt. R5 and R6 were produced/submitted normally, but the G4 -> request7 CQ residual-gain publication failed with `-EINVAL` before R7 composition. The copied C gain-feed publisher still enforced the older G1..G3 validation bound even though the ET/EN helper publishes G1..G6. Six completed frames were validated; the runner later pinned on the seventh dequeue ordering after producer loss. No same-boot stream retry was performed. Raw evidence is pinned under `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-et/attempt1-fail-pinned-gainfeed-order-20260911T1324`.

The defect is isolated from the already-closed EM/EN/EL/ES content work. EU now proves a fresh C publisher with the same wire ABI accepts G1..G6 and rejects G7; any future live retry must use a new candidate identity and depend on EU rather than reusing ET.

The kernel runner consumes R5..R9 monotonically. R7/R8/R9 each emit `E003I_ES_IQ_CONSUMED` immediately after successful provider dequeue and before their Epoch0 wait; live verification requires all three exact request/frame/slot markers plus the final bounded nine-frame completion line. Userspace must DQBUF exactly nine QC10C frames in buffer order `0,1,2,3,0,1,2,3,0`, preserve each frame before reuse, and obtain paired TL_BG/3A generations 1..9. Native AEC is evaluated through G9, but CQ residual gain publication remains G1..G6 and physical sensor writes remain exactly G1..G3 at completed G2/G3/G4.

One candidate boot may perform at most one camera stream attempt. Any failure pins/archives and requires whole-machine reboot; no same-boot retry. A PASS is still bounded nine-frame integration, not unrestricted continuous AEC.
