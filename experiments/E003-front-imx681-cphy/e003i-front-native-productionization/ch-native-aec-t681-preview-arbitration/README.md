# E003i CH — native T681 preview arbitration

Status: **PASS (native/offline)**.

CH transcribes the pinned ordinary front-preview Windows T681 arbitration/range-fit path into native C. It accepts a positive in-table linear exposure target and returns the final preview `{float32 gain, exposureTime}` plus the retained exposure qword that Windows persists into AEC history.

The active table is the already-proven tuned symbol 681:

- priority 1, gain 1.0, time 37,516 ns;
- priority 1, gain 67.0, time 33,333,333 ns;
- priority 1, gain 67.0, time 66,666,666 ns;
- priority 0, gain 92.0, time 66,666,666 ns.

The ordinary preview fit is pinned to min gain 1, min time 37,516 ns, max gain 92 and max time **66,666,664 ns**, now byte-pinned by AQ's 2026-09-10 same-machine read-only controller recapture. The active T5 header is controller `+0x190`, and the same controller slice contains min gain 1, min time 37,516 ns, max gain 92, max time 66,666,664 ns, with `+0x1a0=0`. The older 33,333,332 ns fit limit was a stale nearby-value interpretation and is superseded.

A critical distinction is now explicit: AQ's `desired` quantity is retained separately during range fitting, but the feedback qword stored by `ApplyCoreTable` is recomputed after fitting as `FRINTA(gain * exposureTime * correction)`. In the deterministic CH corpus those quantities differ in 29,584 cases.

No live camera, module load, sensor write, MMIO, Windows boot or reboot is used.
