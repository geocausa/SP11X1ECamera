# E003i-EN — integrated R5–R9 producer gate

Status: **offline integration PASS; no new camera runtime.**

EN extends the already-successful EA current-first architecture without changing its sensor-control schedule. The parent still queues native AEC for G1..G6 and releases exactly three sensor writes at G2/G3/G4. The only parent-side semantic change is that the generation-tagged CQ residual-gain pipe now publishes G1..G6 instead of stopping at G3; the 24-byte `IGF1` ABI is unchanged.

The child runs one continuous trigger/Tintless/GainAdj sequence for G1..G6:

- G1 advances state only;
- G2/G3 use the unchanged EA/DX composer and must remain byte-identical R5/R6;
- G4/G5/G6 use EM component composition for R7/R8/R9 with EL calibrated AWB scalars, DV Demux, sequential LSC/Tintless, stable clean post-R6 GTM and parity banks.

`verify-en.py` is fail-closed and uses the exact preserved EA six-generation STATS3A fixtures plus EM's exact EA TL_BG fixtures. It independently builds the AArch64 helper under `-Werror`, exercises six real C gain-feed records through a pipe (and rejects G7/wrong request), invokes the actual producer CLI, and repeats the full stateful sequence after live-style prewarm for timing.

Required capsule identities:

- R5 `818b65e439b3df9723ce2447e7f5d39f39a44c24cea35aa410bcef279393e4de` — exact successful EA regression;
- R6 `7e6f2503165706b1f0f81069a33aae09244ccc5a1c5bc3ae6a8c3626d766199a` — exact successful EA regression;
- R7 `681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e`;
- R8 `79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e`;
- R9 `1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda`.

The next gate is a **fresh one-shot** Linux candidate using a new boot/helper identity. It may submit R5–R9 once, with no same-boot retry. DP, DT, EA and EK identities remain consumed and must never be reused. Continuous/unrestricted AEC is still not claimed.
