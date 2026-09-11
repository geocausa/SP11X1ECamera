# E003i-GS — consumed continuous-scheduler shadow R27 PASS

Status: **ATTEMPT1 CONSUMED / PASS live shadow scheduling; Golden return PASS; candidate retired.**

GS exercised GQ/GR continuous queue/release ownership across one fresh 27-frame Linux stream without increasing sensor-write exposure beyond GO.

Results:

- 27/27 QC10C frames and G1..G27 paired statistics completed;
- continuous scheduler released sources G1..G26 at exact completed-video boundaries G2..G27;
- exactly the already-proven sources G1/G2/G3 performed physical IMX681 control ioctls;
- sources G4..G26 produced **23 shadow releases** and no sensor ioctl;
- kernel evidence contains exactly four sensor-control transactions total: one bootstrap plus the three real writes;
- producer/IQ path completed R5..R27;
- max producer pipeline time was **28.638720 ms**;
- clean STREAMOFF and kernel-health PASS;
- no same-boot retry;
- protected Golden return PASS and candidate retired.

Evidence archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gs/attempt1-pass-continuous-shadow-20260911T221117`

GS proves that the continuous scheduler owns every bounded live release window through R27 and fails no timing gate while later writes are suppressed. It does **not** prove continuous physical sensor writes. The next safe progression is a separately gated limited redundant-write experiment, not immediately enabling every later write.
