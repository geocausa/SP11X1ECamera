# E003i-GC — consumed bounded twenty-one-frame R5–R21 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded twenty-one-frame integration; Golden return PASS; candidate retired.**

GC combined the closed FY/FW/FV R21 content authority with FZ's G1..G18 compiled gain publisher, GA's live-capable R5..R21 producer, GB's twenty-one-frame transport, the known CW IMX681 control module, and the unchanged three-write delayed physical sensor schedule.

The single GC live attempt completed exactly 21 QC10C frames in buffer order:

`0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0`

Native AEC accepted G1..G21. CQ gain publication and the producer intentionally stopped at G18 after composing R21; G19..G21 were collector-only generations. R5..R21 were submitted live and kernel IQ consumption was observed through R21 (frame 21, slot 0).

Exactly three physical IMX681 writes occurred: G1 after completed G2, G2 after completed G3, and G3 after completed G4. No later physical sensor writes occurred.

All 17 producer pipelines stayed below the 33.333333 ms frame budget. Maximum observed pipeline time was **28.438943 ms**. STREAMOFF succeeded, helper RC was 0, and kernel-health verification passed.

Live capsule SHA256 values at the new frontier:

- R19 `09fe9eccf5c63f93de9b53538898ceec3d5d602aeccc34c4dcbe9ec7df45716d`
- R20 `c71a418d0bf598b738cb6ec39408e0f50b48bfabd146618d4e032d8b97f2ebd2`
- R21 `ef5ed20fefe989c8344a56f9e0aeebe82fa9fd11a979547960f6252360b5b53e`

R21 used AWB calibration slot 3 and triangle 10 for this live scene. FY independently replayed the same live trigger sequence inside the GC verifier.

The helper-consumed guard existed before streaming, no same-boot retry occurred, and GC is permanently consumed. SP11 rebooted to protected Golden on boot ID `66b3ed57-85ae-44fa-9f8b-f0c5729c4319`; the GC GRUB entry and boot directory were then retired.

Raw evidence is pinned under:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gc/attempt1-pass-twentyone-frame-20260911T1941`

GC proves bounded twenty-one-frame integration through R21. It does **not** claim unrestricted continuous AEC or an infinite scheduler.
