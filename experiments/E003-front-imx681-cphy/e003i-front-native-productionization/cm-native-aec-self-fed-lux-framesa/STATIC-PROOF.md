# E003i CM static/composition proof

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.
Pinned IMX681 tuning SHA-256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`.

## FrameSA publication

BG identifies the three FrameSA component blocks. Its target component uses trigger `(9,8)` and the six-region target curve already implemented by BK. The confidence component's value program has one `0..1000` terminal with exact bits `0x3a83126f` (`0.001f`); its component weight is `1.0f`.

BZ corrects the final FrameSA publication identity: SceneAnalyzer `3:7` is not a qword SI. It is phase-2 arithmetic `3:7 = 3:5 target / 3:4 luma`, executed as float arithmetic. CM therefore produces CE's Frame candidate as exact float32 `target / measured_luma` and confidence `0.001f`.

## Lux temporal order

BH proves FrameSA reads trigger `(9,8)` present at request entry and Algorithm001 writes the next `(9,8)` only after current FrameSA target/SI evaluation. BK removes the abstract Algorithm001 F-3 scalar and derives its baseline from retained history lane S1 through BJ's bit-exact `log1.03` coordinate.

CL and CK further prove ordinary analyzer source S1 is retained `F-3.S1`. CM uses that same qword both as the final analyzer source exposure and as the Algorithm001 history baseline, without aliasing S1 to Short.

CM constructs CE's `lux_index` and Frame pair internally from request-entry state. The remaining seven analyzer pairs stay explicit because their semantic producers are not yet reconstructed natively.

## Fail-closed mutation boundary

CM calculates final targets, convergence, four T681 retained qwords, and next Lux before mutating history or the internal Lux trigger. Invalid/missing temporal state or non-finite arithmetic therefore returns before the current request is committed.

## Composed verification domain

CM's successful recurrence differential inherits CL's proven ordinary analyzer publication domain (`0.72..1.45`) for the seven still-open pairs. Measured luma remains AB-realistic (`0.55..2.75`), so FrameSA `target/luma` is intentionally allowed to be much larger than 1 while retaining BG's exact `0.001f` confidence. This tests the real low-luma weighting behavior without feeding unrelated analyzers synthetic `5..50` ratios that drive CH's finite T681 table out of range.
