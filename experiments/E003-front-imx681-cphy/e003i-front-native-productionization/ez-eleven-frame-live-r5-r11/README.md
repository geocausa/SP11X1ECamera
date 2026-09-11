# E003i-EZ — consumed bounded eleven-frame R5–R11 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded eleven-frame integration; Golden return PASS; candidate retired.**

EZ combined EY's eleven-frame transport, EW's compiled G1..G8 CQ gain publisher, EX's R5..R11 producer, CW IMX681 controls, the unchanged R4 bootstrap, and the unchanged three-write delayed sensor schedule.

The single live attempt completed exactly eleven QC10C frames in buffer order 0,1,2,3,0,1,2,3,0,1,2, accepted native AEC generations G1..G11, and submitted R5..R11 live. Kernel consumption was observed for R7/F7/S0, R8/F8/S1, R9/F9/S0, R10/F10/S1 and R11/F11/S0. Exactly three physical sensor writes occurred: G1 after completed G2 affecting G4, G2 after G3 affecting G5, and G3 after G4 affecting G6. No later physical sensor writes occurred.

All R5..R11 producer pipelines stayed below 33.333333 ms; the maximum was 28.126482 ms. STREAMOFF succeeded and kernel health verification passed. The machine then rebooted to protected Golden, Golden return passed, and the EZ boot directory and GRUB entry were removed.

Raw evidence is pinned at /home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ez/attempt1-pass-eleven-frame-20260911T1429 with final manifest SHA256 dafd5c3cc179d00ea02ef446299f1132908d82e5b76c9755f42666427cf08749.

This proves bounded eleven-frame integration through R11. It does not yet prove unrestricted continuous AEC or an infinite scheduler.
