# E003i DK — native AEC failure-pair preservation

Status: **PASS_OFFLINE**.

Attempt3 proved DJ far enough to deliver all three bounded sensor writes, then failed closed at G4 with `RC=-142`. The old DB helper kept the already validated G4 TLBG/STATS3A pair only in RAM and saved raw pairs only after all six generations passed, so the exact failing pair was lost on reboot.

DK changes evidence handling only. The paired-stats worker now carries the caller's TLBG/STATS3A output prefixes. If native AEC fails after a generation pair has already passed exact generation/source/slot identity checks, DB first latches the delayed-write schedule failed, then fsync-saves that current pair as `TLBG-FAIL-GN.bin` and `STATS3A-FAIL-GN.bin`, logs the result, and returns failed. No successful-generation disk write was added, so the G1@G2/G2@G3/G3@G4 sensor timing path is unchanged.

DK does not alter DJ, CH/T681, CQ, sensor controls, the three-write cap, or any image-IQ arithmetic. It exists only to make the next bounded diagnostic failure reproducible offline.

Remote orchestration is also corrected: a pin-capable `invoke-once.sh` must be launched with a persistent PiMaster job. A finite command timeout must not be used, because a timeout can SIGTERM a deliberately pinned helper. If a future helper pins after STREAMON, inspect/archive from a separate command and reboot the whole machine; never stop/restart/retry the camera helper in that boot.
