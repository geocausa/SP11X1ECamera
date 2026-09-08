# E003i BW — Windows AEC default StatsCalculator dependency map

Status: **PASS (static/offline + retained live Frame-luma proof)**.

BW closes the compact tuning boundary immediately upstream of BV. The pinned IMX681 tuning contains a `BankIDStatsCalculator` dictionary of 69 named data IDs and a metering `statsCalculators` table of 55 fixed 92-byte calculator records. The active normal sequence names calculator IDs directly, so the ordinary statistics producer can now be followed by ID rather than guessed offsets.

For the ordinary default Safe/Short/Long target tree, the exact BankIDStatsCalculator inputs are:

`1,2,6,7,8,11,12,19,20,41,42,43,48,49`

which name `AvgLumaBE16x16`, `FrameLumaBE16x16`, `SaturateStatsRatio`, the saturation/dark/brighten percentiles, Short/Long preview percentiles, and five extreme-color ratios.

The 11 configured SafeAgg candidates include Face/Touch/Depth/Tracker/Saliency, but those analyzers are not in `DefaultSequence`. BW deliberately does not yet claim how stale/missing SceneAnalyzer-bank publications are cleared; that is the next boundary to close before pruning those candidates from a native implementation.

AB is fresh-run to retain the live bit-exact `FrameLumaBE16x16` producer evidence. BV is fresh-run to retain the final method-11 Safe/Short/Long aggregation topology.

No camera mutation, module load, MMIO, reboot, or Windows boot is used.
