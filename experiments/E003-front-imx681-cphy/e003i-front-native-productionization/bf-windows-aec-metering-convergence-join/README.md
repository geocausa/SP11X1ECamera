# E003i-BF — Windows AEC metering → convergence → T681 join

Status: **PASS (static/offline)** — the normal front AEC target tuple is joined at object/field level from metering postprocess into convergence, then from convergence into the post-convergence type-5/T681 arbitration path and the already-proven sensor-control tail.

This checkpoint resolves the lingering FrameID-versus-pointer ambiguity. `FrameID` is a scalar field *inside* the convergence input object; it is not the pointer passed in place of that object.

## Exact convergence input object

`CAECXControl::runConvergence` is the function beginning at `0x180374ab8` (its own `CAECXControl::runConvergence` diagnostic is referenced inside this function).

On the normal path it constructs the object at `controller+0x14ca0`:

- `+0x00`: current AEC FrameID;
- `+0x08`: pointer returned by `0x180389dd0`, namely control-arbitration child `+0x688`, the first of seven `0x50` pre-arbitrated target records;
- `+0x10..+0x40`: seven qwords copied byte-for-byte from the metering target tuple at `controller+0x14b70..+0x14ba0`.

It then invokes the external convergence callback with:

`RunConvProcesss(controller+0x14ca0, controller+0x14cf8)`.

The core `RunConvProcesss` prologue preserves x1 as a pointer and later dereferences its members, confirming the first argument is the structured convergence input, not the raw FrameID.

## Metering target identity

`CAECXControl::runMetering` passes `controller+0x14b38` as the metering postprocess output object. `CAECXMetering::RunMeteringPostprocess` uses seven exposure qwords at output offsets `+0x38..+0x68`, hence those are exactly `controller+0x14b70..+0x14ba0`.

BD proves the ordinary target-analyzer SI producer and its bit-exact FrameSA measured-luma join. BE proves that all ten pinned IMX681 `aecxmetering` variants disable both antibanding modifiers, so this seven-qword tuple reaches convergence without that postprocess changing it.

## Pre-convergence arbitration

`0x180389dd0` calls `RunControlArbitration` with `w4=1`, copies seven returned `0x50` payloads into child offsets:

`0x688, 0x6d8, 0x728, 0x778, 0x7c8, 0x818, 0x868`,

and returns `child+0x688`. `runConvergence` stores that exact pointer at convergence input `+0x08`.

Thus each convergence request carries both representations of the same current target side:

- seven metering target exposure qwords at input `+0x10..+0x40`;
- seven arbitration-normalized target records reachable through input `+0x08`.

## Post-convergence T681 join

The compact seven-qword convergence result is `controller+0x14cf8`. The caller immediately invokes `RunControlArbitration(w4=0)` with that exact pointer, and copies the returned `0x3c0` rich block to `controller+0x14da8`.

AR proves the internal arbitration input is `child+0xd0`, with:

- `input+0x138 = child+0x208` coordinate;
- `input+0x160 = child+0x230` coordinate;
- `input+0x198 = child+0x268` table base exposure.

AQ proves the active front normal-preview table is T681 and that Windows reconstructs the desired exposure as the base exposure multiplied by `1.03^coordinate`, rounded with its `FRINTA` helper, before `ApplyCoreTable` produces the gain/time pair.

AX/BC close the temporal recurrence and single-exposure output; AW/AP close request-preserving sensor submission and the live-proven Linux IMX681 control transaction.

## Closed normal-path topology

```text
bit-exact FrameSA measured luma
  → target analyzer SI lanes
  → metering target[7]
  → IMX681 antibanding identity
  → pre-convergence RunControlArbitration(w4=1)
  → RunConvProcesss on request F with history(F-1)
  → compact convergence output[7]
  → RunControlArbitration(w4=0)
  → log1.03 coordinate + T681 base exposure
  → ApplyCoreTable gain/time
  → retained history(F)
  → request-F sensor packet
  → proven IMX681 sensor-control transaction
```

BF does not extend AW's deliberately bounded optical-frame-number claim.
