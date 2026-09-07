# E003i-AQ — Windows front AEC arbitration table closure

Status: **PASS — active normal-preview exposure table and table/range-fit arithmetic closed offline. Continuous AEC convergence/history remains open.**

AP already live-proved the Linux IMX681 sensor-control transaction under non-default exposure/gain while six frames, paired TL_BG/3A stats, dynamic R5/R6 IQ submissions, STREAMOFF and kernel health all remained clean. AQ therefore addresses the next upstream boundary: how Windows turns an exposure quantity into an `{exposureTime, linearGain}` pair before the already-closed sensor conversion path.

## Active front-preview table

The exact Windows artifacts are SHA-pinned in `TABLE681.fixture.json`. `QcDeviceMFT8380.dll` implements `CAECXArbitration::ApplyCoreTable` at RVA `0x3c35f8` and `UtilMakeTableExposureFit` at RVA `0x3c31f8`. The front tuned blob contains five `DefaultExpTable` variants.

A final normal `Surface Camera Front` Windows session was started without a debugger. Two consecutive read-only FrameServer scans found all five tables. T1-T4 each had only their single tuning-database reference and no direct table-header reference. T5 alone had three databank references plus one direct header reference from live controller state in both scans. T5 maps byte-for-byte to tuned-blob symbol **681**, establishing it as the active front-preview table for this path.

Symbol 681 decodes to:

- priority 1, gain 1.0, time 37,516 ns
- priority 1, gain 67.0, time 33,333,333 ns
- priority 1, gain 67.0, time 66,666,666 ns
- priority 0, gain 92.0, time 66,666,666 ns

The exact serialized bytes and truncated knee products are in `TABLE681.fixture.json`.

## Windows arithmetic replay

`E003I-AQ-aec-arbitration-replay.py` is a clean replay of the positive normal-`DefaultExpTable` path needed by the active preview flow. It preserves the observed float32 operation boundaries and truncating float/double-to-unsigned conversion behavior.

Between adjacent knees Windows spends the multiplicative exposure ratio according to the **upper knee's** `incrementPriority`:

- priority `0`: gain first, then time;
- nonzero priority: time first, then gain.

After table interpolation, `UtilMakeTableExposureFit` adjusts gain/time to the current min/max range while retaining a separate desired-exposure quantity. This is why a final gain/time product can differ by one or more integer counts from that retained quantity without indicating a replay error.

The deterministic self-test covers every knee +/-2, fixed boundary/observed-pair neighborhoods, and 100,000 seeded random targets across all three table segments. On Golden Linux it reports **100,017 cases PASS**, with segment coverage `{1: 36133, 2: 36635, 3: 27249}`. A corroborative target in the observed pair neighborhood reproduces the live Windows output pair exactly: gain bits `0x40e7b95b` and exposure time `33,333,332 ns`.

## Evidence and scope

`windows-evidence/E003I-AQ-FINAL-LIVE-EVIDENCE.txt` pins the final two selector scans and SHA-256 values for the DeviceMFT, tuned blob, read-only scanner and holder. `DEBUGGER_PROCESS_COUNT=0`; the holder exited normally after the evidence capture. SP11 was then returned to Golden Linux before repository changes.

AQ **does not** claim flash/HDR arbitration, the proprietary convergence loop, the semantic identity of every nearby live controller qword, or continuous live AEC. In particular, the nearby live value `241379204` is not promoted here as a mechanically proven arbitration-input target. The exact observed gain/time pair is used only as corroboration of the reconstructed normal table path.

The next gate is to close **request-local convergence/history -> arbitration input exposure quantity**, including the seven 0x28-byte AEC history records and request latency. Only after that offline state transition is proven should Linux feed continuously changing AQ outputs into the already-live-proven AM/AP IMX681 controls.
