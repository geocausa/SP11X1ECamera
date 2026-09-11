# E003i-FU — consumed bounded eighteen-frame R5–R18 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded eighteen-frame integration; Golden return PASS; candidate retired.**

FU combined FT's eighteen-frame transport, FR's compiled G1..G15 CQ gain publisher, FS's authorized live-capable R5..R18 producer, CW IMX681 controls, the unchanged template-free R4 bootstrap, and the unchanged three-write delayed physical sensor schedule.

The single FU live attempt completed exactly eighteen QC10C frames in buffer order:

`0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1`

Native AEC accepted G1..G18. Paired TL_BG/3A was captured for all eighteen generations. R5..R18 were composed and submitted live, and kernel IQ consumption was observed through R18.

Exactly three physical IMX681 writes occurred:
- G1 after completed G2, affecting G4
- G2 after completed G3, affecting G5
- G3 after completed G4, affecting G6
- no later physical sensor writes

All R5..R18 producer pipelines stayed below the 33.333333 ms frame budget. Maximum observed pipeline time was **28.516746 ms**. STREAMOFF succeeded, helper RC was 0, and kernel-health verification passed.

R18 live capsule SHA256:

`6714b533f3c866d41ceda8de69b1fd29ca3da6fa28d6ff775851c02ed2dc6ca2`

R18 used AWB calibration slot 5 and triangle 25.

The helper-consumed guard existed before streaming, and no same-boot retry occurred. The machine rebooted to protected Golden, Golden return passed, and the FU GRUB entry and boot directory were retired.

Raw evidence is pinned under:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fu/attempt1-pass-eighteen-frame-20260911T1822`

FU proves bounded eighteen-frame integration through R18. It does **not** claim unrestricted continuous AEC or an infinite scheduler.
