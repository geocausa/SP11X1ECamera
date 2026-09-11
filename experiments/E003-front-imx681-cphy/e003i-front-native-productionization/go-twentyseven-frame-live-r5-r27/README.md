# E003i-GO — consumed bounded twenty-seven-frame R5–R27 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded twenty-seven-frame integration; Golden return PASS; candidate retired.**

GO combined GJ/GK R27 Windows/content authority, GL's G1..G24 compiled publisher, GM's live-capable R5..R27 producer, GN's twenty-seven-frame transport, the accepted CW IMX681 control module, and the unchanged three-write delayed physical sensor schedule.

The single GO live attempt completed exactly 27 QC10C frames in buffer order:

`0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2`

Native AEC accepted G1..G27. CQ gain publication and the producer intentionally stopped at G24 after composing R27; G25..G27 were collector-only generations. R5..R27 were submitted live and kernel IQ consumption was observed through R27.

Exactly three physical IMX681 writes occurred: G1 after completed G2, G2 after completed G3, and G3 after completed G4. No later physical sensor writes occurred.

All 23 producer pipelines stayed below the 33.333333 ms frame budget. Maximum observed pipeline time was **28.760817 ms**. STREAMOFF succeeded, helper RC was 0, and kernel-health verification passed.

Live capsule SHA256 values at the new frontier:

- R25 `ae9a88249b07b5a822512b8f98466c545801d9fc6fa56cb4e1ee27eead7e12d5`
- R26 `4cc44ec81ba51d429c612965a491d2fbf3e31ca6a661b741b266eff694926f83`
- R27 `4d143d72acda9fbeabd94894eb274cc05410cced2d79f0c61cc03ef303891ce7`

R27 used AWB calibration slot 3 and triangle 7 for this live scene.

The helper-consumed guard existed before streaming, no same-boot retry occurred, and GO is permanently consumed. SP11 returned to protected Golden on boot ID `9bf15bd9-378a-4759-aa60-25ab796e11f0`; the GO GRUB entry and boot directory were retired.

Raw evidence is pinned under:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145`

GO proves bounded twenty-seven-frame integration through R27. It does **not** claim unrestricted continuous AEC or an infinite sensor-control scheduler. The next frontier is continuous delayed sensor-control feedback and robustness, not another +3-frame extension.
