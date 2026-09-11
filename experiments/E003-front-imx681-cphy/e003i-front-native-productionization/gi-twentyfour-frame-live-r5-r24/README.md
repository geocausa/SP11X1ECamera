# E003i-GI — consumed bounded twenty-four-frame R5–R24 live PASS

Status: **ATTEMPT1 CONSUMED / PASS bounded twenty-four-frame integration; Golden return PASS; candidate retired.**

GI combined the closed GD/GE R24 Windows/content authority with GF's G1..G21 compiled gain publisher, GG's live-capable R5..R24 producer, GH's twenty-four-frame transport, the known CW IMX681 control module, and the unchanged three-write delayed physical sensor schedule.

The single GI live attempt completed exactly 24 QC10C frames in buffer order:

`0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3`

Native AEC accepted G1..G24. CQ gain publication and the producer intentionally stopped at G21 after composing R24; G22..G24 were collector-only generations. R5..R24 were submitted live and kernel IQ consumption was observed through R24 (frame 24, slot 1).

Exactly three physical IMX681 writes occurred: G1 after completed G2, G2 after completed G3, and G3 after completed G4. No later physical sensor writes occurred.

All 20 producer pipelines stayed below the 33.333333 ms frame budget. Maximum observed pipeline time was **27.555623 ms**. STREAMOFF succeeded, helper RC was 0, and kernel-health verification passed.

Live capsule SHA256 values at the new frontier:

- R22 `9b360274acb5accb967669909be98567be6b7fb015bce963c584856f74abb94f`
- R23 `c82e0e5b00334cf3b8e2931459d17ec4194e2a253dc1699324f1b4852b0dba8f`
- R24 `2421051f56b6f123d4b5c8c5ed86c28345865fcd36b6d797032663503a6e0fa6`

R24 used AWB calibration slot 3 and triangle 5 for this live scene. FY independently replayed the same live trigger sequence inside the GI verifier.

The helper-consumed guard existed before streaming, no same-boot retry occurred, and GI is permanently consumed. SP11 rebooted to protected Golden on boot ID `419bf616-5acd-4903-a56d-650b80099d53`; the GI GRUB entry and boot directory were then retired.

Raw evidence is pinned under:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035`

GI proves bounded twenty-four-frame integration through R24. It does **not** claim unrestricted continuous AEC or an infinite scheduler.
