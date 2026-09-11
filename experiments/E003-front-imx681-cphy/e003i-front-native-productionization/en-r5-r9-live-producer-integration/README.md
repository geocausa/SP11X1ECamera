# E003i-EN — R5–R9 gain-feed/live-producer integration

Status: **offline integration candidate; no new camera runtime.**

EN is a minimal extension of the already-passed EA/DZ current-first schedule.

Parent change: the generation-tagged CQ residual-gain pipe publishes G1..G6 instead of G1..G3. Sensor scheduling is unchanged: six AEC generations, exactly three sensor writes, release G1/G2/G3 after completed G2/G3/G4, N+2 effect at G4/G5/G6.

Producer change: consume paired STATS3A/TL_BG and gain records through G6. R5/R6 still use the unchanged EA/DW compatibility composer. R7/R8/R9 use EM. The calibrated EL GainAdj state is advanced on every generation so post-R6 triangle state is not cold-started artificially.

This stage must first prove offline that R5/R6 remain byte-identical to the accepted EA live submission hashes and R7/R8/R9 equal EM's deterministic composition hashes. A live candidate is separate and must use a fresh one-shot identity.
