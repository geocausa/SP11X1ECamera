# E003i-EV — consumed nine-frame R5-R9 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded nine-frame integration; Golden return PASS; candidate retired.**

EV is the fresh successor to consumed ET and closes ET's G4 gain-feed failure. EV keeps the ET/ES nine-frame transport and closed EN/EP/EM/EL content path, but sources the C gain publisher from EU. EU's compiled publisher accepts G1..G6, rejects G7, preserves request = generation + 3, and retains the 24-byte wire ABI.

The single EV live attempt completed exactly nine QC10C frames in buffer order 0,1,2,3,0,1,2,3,0, accepted AEC generations G1..G9, submitted R5..R9 live, and produced the required kernel consumption markers for R7/R8/R9. Exactly three physical sensor writes occurred: G1 released after completed G2 affecting G4, G2 after G3 affecting G5, and G3 after G4 affecting G6. No later physical sensor writes occurred.

All R5..R9 producer pipelines were below 33.333333 ms; the maximum was 27.485150 ms. STREAMOFF succeeded and kernel health verification passed. The machine was then rebooted to Golden, Golden return passed, and the EV boot directory/GRUB entry were retired. No same-boot stream retry was performed.

Raw evidence is pinned under /home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ev/attempt1-pass-nine-frame-20260911T1352 with final manifest SHA256 3112281038c79522b1612572a98e2bab54b9c1bdfaf735f9d4f4bc4f3c5f48cf.

This PASS proves bounded nine-frame integration only. It does not claim unrestricted continuous AEC or a reusable infinite scheduler.
