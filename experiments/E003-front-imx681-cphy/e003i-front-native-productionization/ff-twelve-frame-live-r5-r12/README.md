# E003i-FF — consumed bounded twelve-frame R5–R12 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded twelve-frame integration; Golden return PASS; candidate retired.**

FF combined FE's twelve-frame transport, FC's compiled G1..G9 CQ gain publisher, FD's corrected R5..R12 producer with FB dynamic AWB calibration-slot selection, CW IMX681 controls, the unchanged R4 bootstrap, and the unchanged three-write delayed sensor schedule.

The single FF live attempt completed exactly twelve QC10C frames in buffer order 0,1,2,3,0,1,2,3,0,1,2,3, accepted native AEC generations G1..G12, and submitted R5..R12 live. Kernel consumption was observed through R12/F12/S1. Exactly three physical sensor writes occurred: G1 after completed G2 affecting G4, G2 after G3 affecting G5, and G3 after G4 affecting G6. No later physical sensor writes occurred.

All R5..R12 producer pipelines stayed below 33.333333 ms; the maximum was 26.872330 ms. STREAMOFF succeeded and kernel health verification passed. FB independently replayed the exact live AWB sequence 9/9; the live calibration slots were 5,5,7,5,5,5,5,5,5, with R12 using slot 5 and triangle 25.

The helper itself returned RC=0. The first post-run verifier then produced a false negative because it incorrectly hard-coded calibration slot 5 for every live generation and rejected the legitimate G3 slot 7. No second stream was run. After the raw evidence was externally archived, the verifier was corrected to replay FB's scene-dependent selector/state, and the captured run passed in full.

The machine was rebooted to protected Golden, Golden return passed, and the FF boot directory and GRUB entry were retired. Raw evidence is pinned under /home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ff/attempt1-pass-twelve-frame-20260911T1630 with final manifest SHA256 e8c7d8d01265cd596a42da0b512fa34ee0c05cc03610fe6d5ac98bff166aeae5.

This proves bounded twelve-frame integration through R12. It does not claim unrestricted continuous AEC or an infinite scheduler.
