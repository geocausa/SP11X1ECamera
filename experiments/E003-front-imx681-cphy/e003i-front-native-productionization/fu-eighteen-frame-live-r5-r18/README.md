# E003i-FU — bounded eighteen-frame R5–R18 live candidate

Status: **STAGED OFFLINE / UNINSTALLED / UNARMED / NO FU CAMERA STREAM YET.**

FU is a fresh one-shot candidate identity. It does not reuse consumed FN.

Composition:
- FT bounded 18-frame transport, including new R16/R17/R18 kernel consumption.
- FR compiled C CQ gain publisher G1..G15 with G16 rejected.
- FS live-capable R5..R18 producer. R5..R15 regress exactly to the real FN live capsules; R16..R18 are authorized by FQ.
- CW IMX681 atomic control cluster.
- unchanged template-free R4 bootstrap.
- unchanged delayed physical sensor-write schedule: only G1/G2/G3 are written, released after completed G2/G3/G4 for effects G4/G5/G6.

Safety:
- persistent Golden saved_entry remains sp11-audio-fullio-v19c;
- installation is unarmed;
- grub-reboot is one-shot only;
- HELPER-CONSUMED.marker prevents a second stream attempt on the same boot;
- every outcome is archived and followed by a full reboot to Golden;
- FU proves only bounded 18-frame integration, never unrestricted continuous AEC.
