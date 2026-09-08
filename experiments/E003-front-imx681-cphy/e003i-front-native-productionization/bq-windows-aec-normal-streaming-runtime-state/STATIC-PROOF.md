# BQ static proof anchors

- Pinned DLL SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.
- Final core `+8` interface vtable: `0x1813383b8`; slot `+0x18` -> `0x1803ae9b0`, a pure `1ULL << context` bit test against mask `+0xb8`.
- BasicSafe passes context index `3` at `0x1803ceaf0..0x1803ceb18`.
- ContextManager op-mode jump table maps operation mode `1` to mask bit `0x4` (context bit 2) and operation mode `2` to `0x8` (context bit 3).
- `CAECXControl::SetControlOpMode` maps enum value `1` to the Streaming branch; same-tree CamX maps `StatsOperationModeNormal` to `AECAlgoOperationModeStreaming`.
- Metering-lock bookkeeping calls the same context-bit helper with index `38` (`0x26`) at `0x1803b302c..0x1803b30e0`.
- The control path sets context 38 with `(index=38,value=1)` at `0x1803777d8..0x1803777f8` and clears it with `(index=38,value=0)` at `0x180378274..0x180378294`. Locked/snapshot/preflash behavior remains outside this checkpoint.
- Convergence constructor/reset zeroes `+0x2ac` and the full qword at `+0x2b0`.
- Whole AEC-region store census: all nonzero writes to `+0x2ac` and `+0x2b0` are contained in the metering-lock bookkeeping block `0x1803b3100..0x1803b3200`; there is no independent store to `+0x2b4`.

Therefore the explicitly scoped ordinary normal-streaming, metering-unlocked profile projects BP's four runtime scalar inputs to zero. This is not a claim about AEC lock, snapshot, preflash, FastAEC, or other temporary context modes.
