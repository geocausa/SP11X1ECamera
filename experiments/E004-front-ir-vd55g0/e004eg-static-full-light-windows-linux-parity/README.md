# E004eg — static full-light Windows/Linux AEC parity

The room is static and empty, with side and main lights on. A fresh Windows oracle was captured immediately before this Linux one-shot.

Windows Camera had Studio Effects **Off**. A central preview-only crop measured mean luma 110.9/255 and median 115/255, so the scene is not underexposed. A fresh 12-request QcDeviceMFT8380 DM trace returned `capflag=0` on all requests and a stable compact block containing 954,179,854 and 1,340,473,362.

This experiment runs the canonical Linux package **unchanged** with post-G3 policy `shadow`; no later native write is authorized. It preserves the live STATS3A/TLBG blobs and QC10C frames. Analysis happens offline afterward through the same native request-loop sources, so diagnostics cannot alter live sensor behavior.

## E004eg closure — lighting disproven, FrameSA is the first observable divergence

A fresh Windows oracle under the same static empty-room/full-light scene disproved the lighting hypothesis. Windows Camera had Studio Effects Off. A preview-only crop was normally exposed (mean luma 110.9/255, median 115/255), and a fresh 12-request DeviceMFT DM trace reported `capflag=0` on every request.

The exact Windows `SetDataSceneAnalyzer` setter was then traced directly. Four consecutive steady frames published:

- bank3:4 FrameSA luma: 45.389797, 45.338123, 45.302635, 45.381428;
- bank3:5 FrameSA target: 47.097954, 47.094101, 47.091454, 47.097328;
- bank3:7 FrameSA AdjRatio: 1.037633, 1.038731, 1.039486, 1.037811.

For each captured frame, bank3 IDs 8 through 13 (Safe target/AdjRatio, Short target/AdjRatio, Long target/AdjRatio) were also essentially the same ~1.04 value. Windows was therefore near-neutral and not requesting a large exposure increase.

The unchanged canonical Linux shadow run under the matched scene reproduced the opposite state. Late G24 had measured luma 83.621101, FrameSA target 40, Frame AdjRatio 0.478348, Safe target 6.958843, Short target 0.774501, published Short exposure 30,486,355,401, convergence 11,133,280,747 and cap 6,133,333,088. The exact offline replay reproduces those values from the captured Linux STATS3A bytes.

Therefore the first **observable** Windows/Linux AEC parity divergence is already at FrameSA luma/target/AdjRatio, before SafeAgg, ADRC, final exposure publication, convergence, or the post-G3 cap-release policy. This does not yet prove whether the root cause is Linux AEC_BE/stats-plane parity or the preceding exposure/history recurrence: Linux and Windows have already reached different sensor-control states by steady state. The next work must separate those two possibilities before changing production code.

No production source was changed by E004eg. SP11 returned to Golden, the candidate was retired, and the canonical package was uninstalled.
