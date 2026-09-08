# BU proof boundary

BU is a Windows-state projection plus native differential proof over BT.

## Static Windows invariant

Pinned DLL SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

For `CAECXConvergence::RunConvProcesss` (`0x1803b38c0` body used by the existing AX/BC chain):

- no-history: `0x1803b471c  str wzr,[x22,#0xdc]`;
- history-present: `0x1803b47a4 ldr s16,[x24,#0x17c]`, then `0x1803b47a8 str s16,[x22,#0xdc]`;
- complete-body census: no other `[x22,#0xdc]` reference;
- direct convergence-base argument census: `x22` itself is first passed as `x0` only at `0x1803b63ec`, immediately before `PopulateOutput` at `0x1803b63f0`. Earlier helpers receive other objects or subobjects, not the convergence base.

`PopulateOutput` is read-only for this metadata: `0x1803ce048` loads `+0xdc`, `0x1803ce04c` stores compact `+0x80`.

`runEndOfFrame` materializes the retained history payload at `controller+0x10a8`; `0x1803bd44c` loads compact `+0x80` and `0x1803bd454` stores controller `+0x1224`, exactly payload `+0x17c`.

Thus `delta(0)=+0.0f` and `delta(F)=delta(F-1)`, proving `delta(F)=+0.0f` for every ordinary contiguous request.

## Native projection

BU deletes `previous_delta` from public F-1 history and writes exact `0.0f` into the unchanged private Windows-style carrier. All other BT inputs and arithmetic are unchanged.

The differential verifier compares complete outputs, byte-for-byte, over 2048 deterministic states and preserves the same fail-closed required-exposure checks.

Locked, preflash/FastAEC, HDR and multi-exposure modes remain outside this profile.
