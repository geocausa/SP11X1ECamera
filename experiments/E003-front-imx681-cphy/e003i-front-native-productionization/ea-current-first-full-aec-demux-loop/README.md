# E003i-EA — current-first bounded full AEC + Demux one-shot

Status: **ATTEMPT1 LIVE PASS / GOLDEN RETURN PASS.**

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

## Attempt1 result

EA attempt1 passed once on 2026-09-11 with no same-boot retry. DZ's current-first ordering removed DY's residual-gain stall: G2 gain wait fell from 23.502993 ms to 0.034842 ms, R5 and R6 both submitted successfully, all six video/statistics generations completed, exactly three sensor writes released at G2/G3/G4, and STREAMOFF/kernel-health checks passed.

The live verifier independently matched parent DZ CQ gain bits to the DX producer, recomputed DV Demux/BLS values, and checked those words inside the submitted R5/R6 capsules.

Full evidence is preserved outside Git at:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ea/attempt1-pass-20260911T0348`

SP11 returned to Golden and the consumed EA boot/GRUB candidate was retired. This proves the bounded six-frame sensor + residual-ISP Demux integration; unrestricted continuous AEC remains unproven.
