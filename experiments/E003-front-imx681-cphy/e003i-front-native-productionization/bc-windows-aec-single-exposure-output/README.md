# E003i BC — Windows single-exposure convergence output

Status: **PASS (static/offline)** — closes the ordinary `activeExposureCount == 1` tail of Windows convergence and mechanically rejoins it to AX history/T681 arbitration and the already-proven IMX681 transport.

## Single-exposure tail

`CAECXConvergence::ConvergeSensorExposures` is at `0x1803d13f0`. It enters with the final normal block in log1.03 coordinates:

- `+0xa0` Short
- `+0xa8` Long
- `+0xb0` Safe
- `+0xb8..+0xd0` s1..s4

For active exposure count `1`, Windows seeds internal sensor exposure slot `+0x100` from Short (`+0xa0`), skips the multi-exposure loop, and replicates that same log value through `+0x108,+0x110,+0x118`. Those four internal sensor slots are then copied back to normal s1..s4 (`+0xb8,+0xc0,+0xc8,+0xd0`).

Therefore the final seven log lanes on this path are:

`Short, Long, Safe, Short, Short, Short, Short`.

The AutoHDR/multi-exposure switch/tolerance branch is deliberately outside this checkpoint.

## Final output conversion

`ConvergeSensorExposures` returns to `RunConvProcesss`, which back-edges from `0x1803b67f0` to the common output path at `0x1803b6080`. That path calls `CAECXConvergence::PopulateOutput` at `0x1803cdf50`.

`PopulateOutput` reads all seven final logs `+0xa0..+0xd0`. For each it evaluates the exact widened-`1.03f` base `1.0299999713897705`, then converts with ARM64 `FCVTZU`:

`linearExposure = uint64_trunc(pow(1.0299999713897705, logExposure))`.

The seven compact qwords are written consecutively at output `+0x00,+0x08,...,+0x30`.

## Exact downstream join

AX already proves that this compact output is `controller+0x14cf8`, immediately consumed by post-convergence `RunControlArbitration(w4=0)`, mapped into the selected 0x28 record, sent through type-5/T681 `ApplyCoreTable`, retained in the rich arbitration record and saved as history for the next frame.

BC runs the existing AX and AQ verifiers fresh. It also runs AV/AW and the AP evidence verifier, mechanically retaining the established sensor-delay, Windows sensor-request submission and live group-held IMX681 transport proofs.

Thus the ordinary single-exposure topology is now closed end-to-end at the static/evidence level:

`history(F-1) -> convergence(F) -> final 7 linear qwords -> T681 arbitration(F) -> retained history(F) -> request-F sensor packet -> proven IMX681 control transport`.

This does not claim AutoHDR/multi-exposure parity and does not perform a new live camera mutation.
