# E003i CL — native self-fed retained-S1 AEC history

Status: **PASS (native/offline)**.

CL removes CI's last caller-supplied analyzer exposure seam. CK proves ordinary front preview selects retained AEC history offset 3, while CJ proves the analyzer source lane is S1. AX independently proves all seven convergence lanes pass through post-convergence type-5/T681 arbitration and are persisted to the next history record.

The native request recurrence therefore now owns:

- F-1 Short/Long/Safe + PredGain for convergence;
- F-2 Short/Long/Safe + PredGain for convergence;
- F-3 Safe for convergence;
- **F-3 S1 for analyzer sourceExposure[S1]**;
- current post-convergence retained S1 from T681 for future F+3 consumption.

`source_exposure_s1` is no longer present in the public request input. The current request takes `history[F-3].s1_exposure`, and lane `E003I_LANE_S1` is separately arbitrated through T681 and committed as S1. CL deliberately does not alias S1 to Short.

The explicit warm-up seam remains, now requiring seeded S1 in addition to CI's retained fields. Startup/no-history behavior remains a later integration boundary; ordinary warmed-up recurrence is self-fed.

No live camera, module load, sensor write, MMIO, Windows boot or reboot is used.
