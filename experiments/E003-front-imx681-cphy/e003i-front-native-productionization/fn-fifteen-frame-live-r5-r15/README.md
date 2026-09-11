# E003i-FN — consumed bounded fifteen-frame R5–R15 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded fifteen-frame integration; Golden return PASS; candidate retired.**

FN combined FM's fifteen-frame transport, FK's compiled G1..G12 CQ gain publisher, FL's authorized live-capable R5..R15 producer, CW IMX681 controls, the unchanged template-free R4 bootstrap, and the unchanged three-write delayed sensor schedule.

The single FN live attempt completed exactly fifteen QC10C frames in buffer order 0,1,2,3,0,1,2,3,0,1,2,3,0,1,2. Native AEC accepted G1..G15, paired TL_BG/3A was captured for all fifteen generations, and R5..R15 were submitted live from G2..G12. Kernel IQ consumption was observed through R15/F15/S0.

Exactly three physical IMX681 sensor writes occurred: G1 after completed G2 affecting G4, G2 after G3 affecting G5, and G3 after G4 affecting G6. No later physical sensor writes occurred.

All R5..R15 producer pipelines stayed below 33.333333 ms. The maximum was 27.722582 ms. STREAMOFF succeeded, the helper returned RC=0, and kernel-health verification passed. R15 used AWB calibration slot 5 and triangle 25.

The helper-consumed guard was created before streaming, and no same-boot retry occurred. The machine was rebooted to protected Golden, Golden return passed, and the FN boot directory and GRUB entry were retired.

Raw evidence is pinned under:

/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fn/attempt1-pass-fifteen-frame-20260911T1735

This proves bounded fifteen-frame integration through R15. It does not claim unrestricted continuous AEC or an infinite scheduler.
