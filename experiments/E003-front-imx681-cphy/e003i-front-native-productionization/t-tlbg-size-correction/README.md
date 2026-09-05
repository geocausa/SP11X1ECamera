# E003i-T — TL_BG raw-size correction

Status: **static PASS; runtime not yet repeated with the corrected userspace ABI**.

E003i-S proved the live transport and exposed a pre-existing arithmetic typo in later handoff/Q documentation. The accepted stage-N parser proof has always defined:

- 32 × 24 = 768 regions;
- Titan680 raw record = `0x50` (80) bytes;
- required parser raw authority = **768 × 80 = 61,440 bytes = `0xF000`**.

The later statement `768 × 0x50 = 0x25800` was wrong. E003i-S showed why the mistake had remained benign: all six Linux snapshots and both preserved Windows raw captures have real nonzero data only in the first `0xF000`; the extra `0x16800` bytes through `0x25800` are identically zero.

This checkpoint changes only `CAMSS_X1E_TLBG_RAW_BYTES` from `0x25800` to `0xF000`. Therefore the read-only V4L2 snapshot becomes 32-byte header + 61,440 raw bytes = **61,472 bytes (`0xF020`)**. Existing VFE aux DMA allocation remains `0x48000`, completion/event semantics remain unchanged, all six ownership-safe publication points remain, and deferred R5/R6 IQ semantics remain intact. No MMIO or hardware programming is added or changed.

The patch round-trips exactly, checkpatch passes, and the Golden-ABI module builds cleanly. Historical Q/S manifests remain unchanged because they accurately record the oversized ABI that was actually built/tested.
