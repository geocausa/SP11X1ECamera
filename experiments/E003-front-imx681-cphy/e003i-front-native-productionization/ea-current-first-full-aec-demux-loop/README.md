# E003i-EA — current-first bounded full AEC + Demux one-shot

Status: **PREPARED_UNEXECUTED.**

EA is the fresh disposable successor to failed-closed DY attempt1.

The only parent scheduling change is DZ's proven ordering:

1. compute current-generation native AEC/CQ;
2. queue the current sensor tuple;
3. publish the current residual ISP gain to the unchanged DX producer;
4. release/write the previous generation sensor tuple at the same completed-DQBUF boundary.

This restores the concurrency the successful DT run had: R5/R6 can compose and submit while the previous sensor ioctl is running, instead of waiting behind that ioctl as DY did.

All other bounded safety rules remain unchanged: six frames only, three sensor writes maximum, release G1/G2/G3 after completed G2/G3/G4, expected statistics effect G4/G5/G6, no same-boot retry, fail-closed pinning, one-shot GRUB candidate, and mandatory Golden return.

The live verifier cross-checks parent DZ CQ gain bits against the DX producer's gain-feed bits, recomputes Titan680 Demux/BLS registers through DV, and checks the actual submitted R5/R6 capsule module bytes.

A successful EA run would prove this bounded six-frame integration only. Unrestricted continuous AEC remains outside this checkpoint.
