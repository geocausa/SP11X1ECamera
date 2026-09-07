# E003i AX — Windows AEC convergence/history recurrence

Status: **PASS (static/offline) — the normal seven-lane Windows AEC feedback loop is closed from previous-frame history through convergence, post-convergence type-5/T681 arbitration, and end-of-frame history persistence.**

Pinned oracle: `/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll`, SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

AX joins AQ–AW without booting Windows, streaming the camera, changing the kernel, or touching the already-proven Linux sensor-control path.

## One-request temporal law

AS proved that `CAECXConvergence::RunConvProcesss` asks `CAECXHistory::GetInternalFrameHistory` for offset `1`. On contiguous requests, current request/frame `F` therefore receives history from `F-1`.

The non-null convergence path reads exactly seven qwords from the previous history payload:

`history + {0x28,0x50,0x78,0xa0,0xc8,0xf0,0x118}`.

These are a 0x28-stride seven-lane array. They become the seven internal `CurrentExp(Log)` inputs. The current request's arbitration-derived target qwords are read from the seven convergence-input records at offsets `+0x10..+0x40` in 8-byte steps and become the `TargetInExp(Log)` side.

Thus normal request `F` convergence is explicitly seeded by the seven retained exposure values from request `F-1`, not same-request history.

## Pre-convergence arbitration

`CAECXControl::runConvergence` first calls helper `0x180389dd0`. That helper calls `RunControlArbitration` with `w4=1`, then copies the returned seven rich arbitration records (`0x88` stride) from each record's `+0x30..+0x7f` into seven `0x50` convergence-target records rooted at control-arbitration child `+0x688`.

So the current request's target side is already arbitration-normalized before `RunConvProcesss` executes.

## Seven compact convergence outputs

`CAECXConvergence::PopulateOutput` converts the internal seven converged exposure values at `+0xa0,+0xa8,...,+0xd0` back to seven linear qwords at output `+0x00,+0x08,...,+0x30`.

The controller passes `controller+0x14cf8` as the `RunConvProcesss` output buffer. This is the compact seven-exposure result for the current request.

## Post-convergence arbitration

On the normal frame path, the ordering is exact:

1. `CAECXControl::runConvergence` runs.
2. `RunControlArbitration` is called again with `w4=0`.
3. Its `x1` is exactly `controller+0x14cf8`, the compact seven convergence outputs.
4. The returned `0x3c0`-byte rich output block is copied to `controller+0x14da8`.

Inside `RunControlArbitration`, the selected exposure lane is mapped to a seven-element `0x28` array rooted at child `+0xe0`. For selected lane `i`:

- compact converged exposure `x1[i]` is stored at selected record `+0x18`;
- the same qword is converted to float and divided by the arbitration base exposure;
- the ratio is transformed through `log(ratio) / log(1.03f)`;
- that float coordinate is stored at selected record `+0x10`.

So the post-convergence compact exposure is not merely carried alongside arbitration: it mechanically generates the selected type-5 table coordinate.

## T681 consumption

The normal `BankIDArbitrationTable` dispatch is type `5`. In core `CAECXArbitration::RunArbitration`, type 5 jumps directly to the `ApplyCoreTable` path.

On the normal table path, `ApplyCoreTable` maps the selected exposure type and reloads from that same `0x28` record:

- selected record `+0x10`: convergence-derived log1.03 coordinate;
- selected record `+0x18`: convergence-derived linear exposure qword.

AQ/AR already proved that the active front-preview table is tuned symbol 681 and that the table helper reconstructs the desired exposure and applies `ApplyCoreTable` with the Windows float/truncation behavior.

After interpolation/range fitting, the result carries gain, exposure time and correction. `ApplyCoreTable` forms the retained exposure quantity as:

`FRINTA(gain * exposureTime * correction)`

and stores it at table-result `+0x18`. Core `RunArbitration` copies the 32-byte table-result block `+0x00..+0x1f` to rich output `+0x08..+0x27`, so the retained result qword at `+0x18` maps exactly to rich arbitration output `+0x20`.

## End-of-frame persistence

The external AEC callback table's `+0x48` adapter forwards to the core wrapper's `+0xc0` slot, `CAECXCore::runEndOfFrame`.

On the normal caller this callback receives:

- `x4 = controller+0x14cf8` — compact convergence output;
- `x5 = controller+0x14da8` — post-convergence rich arbitration block.

`runEndOfFrame` copies seven `0x28` blocks from the rich `0x88`-stride records. The source blocks begin at rich record `+0x08`; therefore the third qword copied into each history block is exactly rich record `+0x20`.

The next convergence lookup reads that qword at history record `+0x18`, i.e. history payload offsets `0x28 + 0x28*i`.

Therefore the closed steady-state recurrence is:

`retainedTableExposure(F-1) -> convergenceCurrent(F) -> convergedExposure(F) -> log1.03 coordinate(F) -> T681 arbitration(F) -> retainedTableExposure(F) -> history(F)`.

## Request latency

With AU's `AEC FrameID F = CamX request F`, AS's offset-1 history rule, AT's zero-offset `PropertyIDAECFrameControl` fetch, and AW's preservation of request `F` through sensor-packet submission:

- AEC feedback recurrence contributes exactly **one previous AEC request** of history (`F-1 -> F`);
- the AEC property-pool boundary adds **zero explicit request offset**;
- SensorNode does **not renumber** the current request before sensor submission.

The separate optical-latch label remains deliberately outside this checkpoint.

## Scope / next gate

AX closes the Windows temporal/dataflow boundary requested by AQ. It does **not** yet claim a Linux implementation of the proprietary convergence arithmetic or authorize unrestricted continuous sensor mutation by itself.

The next Golden-safe step is to inspect the existing AP Linux producer and implement the smallest deterministic request-local recurrence that reuses the already-proven Linux statistics association, AQ T681 replay and AP IMX681 sensor-control transport. Any live proof should remain bounded and fail-closed before continuous operation is enabled.
