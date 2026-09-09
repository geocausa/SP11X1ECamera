# CU handoff

Accepted scope: ordinary cold front raw `STATS3A -> AEC request recurrence`, entirely offline.

CU mechanically joins the previously separate producers:

- raw AEC_BE -> AB-equivalent measured luma;
- raw BHist + CP-selected delayed history -> CT Bank4 `{6,7,8,19}`;
- measured luma + Bank4 + delayed Short -> CR effective analyzers;
- CR non-Frame analyzers + measured luma -> CP self-contained recurrence.

Important startup behavior is now preserved end-to-end: CP's synthetic history has `PredGain=+0.0f`, CT consequently produces exact-zero Bank4:7/:8 flag1 luma values, and CR explicitly accepts that Windows-valid zero domain.

CP exposes a read-only history-copy accessor so CU uses CP's single authoritative F-3 selector instead of duplicating it.

CU requires cold-owned uninterrupted stats generation/source sequence `F+1`, and rejects mismatches without changing recurrence state.

Verification uses generated STATS3A, not historical AP captures as a fake continuous AEC sequence. Four stateful generated frames match independent primitive composition byte-for-byte; twelve generated AEC grids match AB's Windows-backed luma model bit-for-bit.

Safety: no camera modules, no STREAMON, no V4L2 control writes, no CQ call, no GRUB changes.

## Next checkpoint

Build an offline request-to-sensor-control join on top of CU + CQ:

1. consume CU's CP/T681 request output;
2. invoke CQ's IMX681 control adapter without opening a device;
3. prove frame/generation ownership and control-delay association;
4. pin exact generated control values across synthetic recurrence fixtures;
5. retain a hard no-I/O boundary until that adapter is accepted.

Only after the full raw-stat -> request -> control chain is mechanically accepted should a new bounded Linux camera runtime be considered.
