# E003i-AO — generation-matched parent paired-stats audit

Status: **PASS — static/offline closure; fresh AP runtime required.**

AN live-closed the AM IMX681 sensor-control transaction and the producer successfully submitted R5/R6, but the redundant parent audit pinned after DQBUF0 because it read the two volatile latest-snapshot controls non-atomically: TL_BG once, then 3A once. The kernel publishes TL_BG immediately before 3A for each common source sequence/slot, and each control has its own mutex. A new publication can therefore land between those reads.

AO changes only the parent capture helper. After the producer reports READY and before STREAMON, AO starts a lightweight paired-stats collector thread. For target generations 1..6 it waits for target 3A first, then reads TL_BG. Because the runner has already published that generation's TL_BG before making its 3A visible, the pair is stable for the remainder of the frame interval. AO requires exact `(generation, source_seq, slot)` equality and fails closed if a target is missed. The old DQBUF-coupled one-shot snapshot reads are removed.

The collector polls at 2 ms, much slower than the deadline-sensitive producer, and performs no evidence-file I/O until all six frames are complete. The producer, kernel, AM sensor module, IQ transport and R5/R6 logic are unchanged.

`prove-ao.py` verifies the AN classification, all six kernel TL_BG->3A publish sites, the producer's 3A->TL_BG matching contract, collector-before-STREAMON ordering, absence of DQBUF-coupled snapshot reads, strict target-generation checks, and a 20,000-case interleaving timing model. The helper builds with `-Wall -Wextra -Werror -pthread`.

AP must live-prove the same AM transaction, six frames, collector pairs generations 1..6, live R5/R6 submissions, clean kernel health and mandatory Golden return. No same-boot retry is allowed.
