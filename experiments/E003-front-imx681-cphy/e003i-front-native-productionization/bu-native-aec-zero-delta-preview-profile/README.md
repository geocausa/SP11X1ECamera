# E003i BU — native AEC zero-delta preview profile

Status: **PASS (native/offline)**.

BU removes the last scalar metadata field from BT's F-1 public history state for ordinary SP11 front preview: `previous_delta`.

The public convergence request state is now only:

- current target log: Short, Long, Safe;
- F-1: Short/Long/Safe retained linear exposures and DRC gain;
- F-2: Short/Long/Safe retained linear exposures and DRC gain;
- PipelineDelay/F-3: Safe retained linear exposure.

## Windows zero-delta recurrence

The pinned `QcDeviceMFT8380.dll` proves a closed recurrence for the compact convergence delta metadata on this path:

1. `RunConvProcesss` no-history initialization stores `wzr` at convergence `+0xdc` (`0x1803b471c`).
2. With history, it loads F-1 history `+0x17c` and stores that value at convergence `+0xdc` (`0x1803b47a4..0x1803b47a8`).
3. Across the complete `RunConvProcesss` body through the final `PopulateOutput` call, those are the only references to `[x22,#0xdc]`; there is no later load or store. The convergence-object base is not passed to a helper until `PopulateOutput` itself.
4. `PopulateOutput` copies convergence `+0xdc` to compact output `+0x80` (`0x1803ce048..0x1803ce04c`).
5. `runEndOfFrame` stores compact `+0x80` to the retained history payload at `+0x17c`: payload base is `controller+0x10a8`, and the store is at controller `+0x1224 = 0x10a8 + 0x17c` (`0x1803bd3ec..0x1803bd3f0`, `0x1803bd44c..0x1803bd454`).

Therefore the base case is exact `+0.0f`, and every subsequent request copies the preceding exact value unchanged. By induction, ordinary continuous normal-preview history `previous_delta` is always `+0.0f`.

BU keeps the generic private convergence carrier unchanged but binds `history1.previous_delta = 0.0f`; callers can no longer supply the field.

## Verification

`verify-bu.py` fresh-runs BT, rechecks the pinned DLL SHA-256 and every static recurrence anchor above, compiles BT and BU with strict floating-point flags, and compares the entire output struct byte-for-byte across 2048 deterministic normal-preview request states with BT projected to the proven Windows `previous_delta=+0.0f` state.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot is used.
