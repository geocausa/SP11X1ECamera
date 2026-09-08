# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Windows qword-to-convergence coordinate

`CAECXConvergence::RunConvProcesss` reads current target qwords from convergence input `+0x10,+0x18,+0x20,...`. For Short, Long and Safe the first three conversions are anchored at `0x1803b47b4..0x1803b4840`:

- load qword;
- `ucvtf s0,x8`;
- call float log10 helper `0x180f5cd58`;
- load shared reciprocal scale;
- `fmul` in float32;
- `fcvt` the rounded result to double.

The same sequence is used for retained history qwords at the interleaved `+0x28,+0x50,+0x78,...` history slots.

## Exact scale

Initialization at `0x1800021dc..0x180002214` loads literal float32 `1.03f` (`0x3f83d70a`), calls the same log10f helper, then performs a separate float32 `1.0f/log10f(1.03f)` division and stores the result. Executing the pinned helper produces `log10f(1.03f)=0x3c52532c` and reciprocal scale `0x429bcc0c`.

## Native differential proof

`verify-cg.py` maps the pinned ARM64 PE into Unicorn and executes the Windows `UCVTF` instruction plus the Windows float log10 helper. The native scalar `e003i_convergence_log103_u64()` matches that executable oracle bit-for-bit over 8,215 deterministic qword cases, including values around `2^24`, `2^32`, `2^53` and `2^63`.

The verifier also compiles historical BU and CG independently. For 2,048 request states chosen so the old and corrected scalar coordinate are identical, complete convergence output structures are byte-identical, guarding against unrelated changes to the convergence kernel.
