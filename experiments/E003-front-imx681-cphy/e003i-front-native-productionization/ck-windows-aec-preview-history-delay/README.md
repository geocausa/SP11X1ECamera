# E003i CK — Windows AEC normal-preview history delay

Status: **PASS (static/offline)**.

CK closes CJ's remaining temporal selector ambiguity. For the ordinary SP11 front IMX681 session, Windows configures the non-AutoHDR AEC pipeline delay to **3**, publishes that byte through AEC input ID 15 / set-param 25, and stores it into the exact CAECX byte that `CAnalyzerManager` later passes to `CAECXHistory::GetInternalFrameHistory`.

Exact joined path:

`front useCase 2 + initial CapturePipe Configure -> non-AutoHDR delay 3 -> stats/pipeline +0x2478 -> AEC input 15 -> set-param 25 -> (core+8)+0xb0c -> concrete context+0x8ec -> AnalyzerManager history offset 3 -> retained-history S1@+0xa0`.

The CapturePipe guard is lifecycle state, not a second delay. It is zero at construction, becomes 1 after successful Start/resume, and 2 on stop. Thus the first ordinary Configure refreshes the delay while the state is 0; later Start does not invalidate the already-published value.

CK does **not** claim that retained S1 equals retained Short. The next native reduction must preserve a three-request delayed **S1 history lane**, not substitute Short merely because the temporal offset is now known.

Static/offline only: no camera stream, module load, sensor write, MMIO, reboot, or Windows mutation.
