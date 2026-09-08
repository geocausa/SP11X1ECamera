# E003i CK static proof — ordinary analyzer history offset = 3

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Front ordinary use case and CapturePipe lifecycle

The committed same-machine E003h Windows oracle records the normal front session as `camera_use_case=2` (`EV IFE_START804 id=1 usecase=2 skip=0`). In the DeviceMFT CapturePipe code, object field `+0x163480` is passed as the `useCase` argument to the helper whose diagnostic is `pickModeUseCase=%d, useCase=%d`; therefore the pipeline-delay switch's selector is the same useCase value.

The switch sends useCase 2 to `0x1802b3cd0`.

The guard at `CapturePipe+0x162e58` is lifecycle state. Exact effective writers are:

- constructor `0x1802abcd8`: zero;
- stop path `0x1802ad0ec`: 2;
- successful Start/resume tail `0x1802ae9bc`: 1.

Thus the first ordinary Configure sees state 0 and does not take the `state == 1` skip.

## CapturePipe delay publication

`0x1802b3c50..0x1802b3c84` selects:

- AutoHDR: 4;
- non-AutoHDR: **3**.

The selected halfword is stored in the global pipeline-delay slot. For useCase 2, `0x1802b3ce4..0x1802b3cf0` reloads that value and writes it to the stats/pipeline object at `+0x2478`.

## AEC input and set-param bridge

`0x180833eb8..0x180833ec8` creates AEC input ID 15 from `stats+0x2478` and stores its low byte in the input payload.

The input-15 translator at `0x18084e0d0..0x18084e0e4` emits a one-byte set-param with type 25 (`0x19`). The CAECX 50-way set-param jump table maps type 25 to `0x1803c6f2c`.

That case validates a one-byte payload and performs:

```text
0x1803c6fd4  ldr  x8,[x19]
0x1803c6fd8  ldrb w8,[x8]
0x1803c6fdc  strb w8,[x22,#0xb0c]
```

The dispatch prologue at `0x1803c5040` fixed `x22 = x0`, the concrete CAECX interface `this`.

## Identity with CJ's selector

The concrete CAECX vtable slot 0 at `0x1803ae960` is exactly `return this + 0x220`.

Therefore:

`(core+8)+0xb0c == ((core+8)+0x220)+0x8ec`

because `0x220 + 0x8ec = 0xb0c`.

CJ's AnalyzerManager path reads `context+0x8ec` at `0x1803e3a54` and passes it directly to `CAECXHistory::GetInternalFrameHistory` at `0x1803e3a98`. CK therefore proves the ordinary front normal-preview history offset is **3**.

Combined with CJ, ordinary analyzer `sourceExposure[S1]` comes from the retained S1 lane of the history record selected at offset 3. CK does not identify that S1 lane with Short.
