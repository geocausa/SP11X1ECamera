# E003i-AP — live AM sensor controls with AO paired-stats audit

Status: **READY / UNEXECUTED — fresh one-shot after AN live-closed AM but exposed the parent audit race.**

AP is not an AN retry. AN proved the exact AM group-held sensor transaction live and its producer submitted both R5 and R6, then the parent pinned because its old TL_BG-first/3A-second one-shot audit straddled a latest-snapshot publication boundary. AN returned Golden without retry.

AP changes only the parent capture helper to AO. AO starts a 3A-first -> TL_BG target-generation collector before STREAMON, stores generations 1..6 in memory, and writes evidence after all six frames. AM, Z/Y CAMSS, front-only DTB, template-free R4 and the deadline-hardened producer are unchanged.

Acceptance requires cached controls FLL 3554 / exposure 3500 / analogue 0x040 / global digital 0x0110, the exact AM `ret=0` transaction, six QC10C frames, AO paired generations 1..6, live R5/R6 submissions, clean kernel health, no same-boot retry and mandatory Golden return.
