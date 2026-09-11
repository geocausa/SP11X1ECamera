# E003i-FN — bounded fifteen-frame R5–R15 live candidate

Status: **STAGED OFFLINE / UNINSTALLED / UNARMED / NO FN CAMERA STREAM YET.**

FN is a fresh candidate identity. It does not reuse consumed FF.

Composition:
- FM bounded 15-frame transport, including new R13/R14/R15 kernel consumption.
- FK compiled C CQ gain publisher G1..G12 with G13 rejected.
- FL live-capable R5..R15 producer. R5..R12 regress exactly to the real FF live capsules; R13..R15 are authorized by FJ.
- CW IMX681 atomic control cluster.
- Unchanged template-free R4 bootstrap.
- Unchanged delayed physical sensor-write schedule: only G1/G2/G3 are written, released after completed G2/G3/G4 for effects G4/G5/G6.

Safety:
- persistent Golden saved_entry remains sp11-audio-fullio-v19c;
- installation is unarmed;
- grub-reboot is one-shot only;
- HELPER-CONSUMED.marker prevents a second stream attempt on the same boot;
- every outcome is archived and followed by a full reboot to Golden;
- FN proves only bounded 15-frame integration, never unrestricted continuous AEC.
