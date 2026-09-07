# E003i-AR — Windows AEC exposure-coordinate bridge

Status: **PASS (static/offline) — arbitration base-exposure field, log-coordinate construction, AQ reconstruction, and arbitration→convergence handoff closed for the normal table path. Temporal `CAECXHistory` request latency remains open.**

AQ closed the active front-preview `DefaultExpTable` (T5 / tuned symbol 681) and `ApplyCoreTable` interpolation. AR closes the immediately upstream representation used by `CAECXArbitration::RunArbitration` and corrects an intentionally unresolved AQ observation.

## Main correction

AQ deliberately did **not** name the nearby live qword `241379204`. AR proves that `RunArbitration` input field `+0x198` is **not** that live value for active T681. The field is the selected arbitration table's base/normalised exposure product. AQ's helper then applies a log-domain coordinate through `1.03f^coordinate`, rounds the resulting desired exposure, and passes that value to `ApplyCoreTable`.

For the active T681 table the first knee is `{gain=1.0, time=37516 ns}` with correction factor 1.0. The serialized T681 table has a zero normalization word, so its unnormalized base exposure is 37,516. The old `241379204` observation is retained only as a post-scale/target-neighborhood observation without an address-proven identity.

## Binary chain

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Key RVAs:

- wrapper factory: `0x3a8be0`
- `RunControlArbitration`: `0x388910`
- `RunConvProcesss`: `0x3b38c0`
- `RunArbitration`: `0x3b89f0`
- AQ exposure/table helper: `0x3c2500`
- `ApplyCoreTable`: `0x3c35f8`
- generic data-bank setter/getter: `0x3d5900` / `0x3d5b00`

The factory's external callback table maps:

- callback `+0xa8` → adapter `0x3a8280` → wrapper slot `+0xa0` → `RunArbitration`
- callback `+0xb0` → adapter `0x3a82d0` → wrapper slot `+0x78` → `RunConvProcesss`

Normal arbitration calls use `x1 = child+0xd0`. Therefore `RunArbitrationInput+0x198 == child+0x268`. `RunControlArbitration` writes that qword directly at `0x38a138`.

The type-5 bank descriptor is size `0x38` and carries the literal name `BankIDArbitrationTable`. Its table body is at bank payload `+0x10`; this matches AQ's live selector geometry (`db = hdr - 0x10`). The body consumed by `RunControlArbitration` supplies correction factor, normalization coordinate, knee count and knee pointer. The base qword is formed from the first knee as:

`max(1, round(first_gain * first_time * correction) / 1.03^normalization)`

with the division omitted when the normalization field is effectively zero. Rounding is the binary's `FRINTA` helper at `0x1800014b0`.

## Log coordinate and AQ reconstruction

At startup the DeviceMFT loads float32 literal `0x3f83d70a = 1.0299999713897705`, evaluates its float logarithm helper, takes the reciprocal, and stores the result in the global used by `RunControlArbitration`. The same helper is separately evaluated at `2.0f`, with both that result and its reciprocal cached, which fixes the operation as the logarithm scale family rather than an arbitrary tuning constant.

`RunControlArbitration` computes exposure coordinates from an exposure/base ratio, calls the double logarithm implementation, multiplies by the cached reciprocal-log(1.03f) scale, converts to float32, and stores the results at `child+0x208` and `child+0x230`.

Because `RunArbitration` input is `child+0xd0`, these become exactly:

- `input+0x138 == child+0x208`
- `input+0x160 == child+0x230`

`RunArbitration` loads those fields, optionally applies an explicit multiply/add override mode, and passes the resulting float coordinate in `s0` to helper `0x3c2500`. That helper evaluates `powf(1.03f, coordinate)`, multiplies by `input+0x198`, performs `FRINTA`, and passes the resulting uint64 desired exposure to `ApplyCoreTable`.

Thus the unmodified normal-path representation is:

`coordinate ≈ log(exposure / baseExposure) / log(1.03f)`

and AQ reconstructs:

`desiredExposure = FRINTA(baseExposure * powf(1.03f, coordinate))`.

Both coordinate and power stages contain float32 boundaries; do not infer exact hidden qword identity from a final `{gain,time}` product alone.

## Arbitration precedes convergence

AR also closes the stage ordering that was ambiguous at the end of AQ. `RunControlArbitration` returns `child+0x298`, the base of seven arbitration-output records at `0x88` stride. `0x389dd0` copies each record's `+0x30..+0x7f` 0x50-byte payload into seven convergence records rooted at `child+0x688` with `0x50` stride. That pointer is stored into the normal `RunConvProcesss` input and consumed afterwards.

So the proven ordering is:

`table/base + coordinate → RunArbitration → 7 arbitration outputs → 7 convergence records → RunConvProcesss`.

There is no pointer alias between `RunArbitration` input (`child+0xd0`) and the convergence workset (`child+0x688`).

## Scope

AR is static/offline proof from the SHA-pinned copied Windows DeviceMFT and the already-pinned AQ T681 fixture. No live camera or Windows mutation was used for this checkpoint.

AR does **not** yet close the temporal `CAECXHistory` ring, request-to-result frame latency, continuous metering/convergence feedback, flash/HDR paths, or the absolute address/semantic identity of the old `241379204` live observation. Those remain the next offline gate before continuous Linux AEC is safe to wire into the already-live-proven sensor-control path.
