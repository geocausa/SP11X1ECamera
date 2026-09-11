# E003i-ER — corrected bounded live R5–R9 one-shot

Status: **ATTEMPT1 CONSUMED / FAIL-CLOSED at the R9 transport window; Golden return PASS; candidate retired.**

ER proved the corrected EP GainAdj path live through G6 and composed R9 successfully, but the final R9 userspace submission returned `-EBUSY`. This is now closed as a **transport/runner-boundary failure, not an IQ-content failure**.

The exact production CAMSS source only consumes deferred steady requests **R5 and R6** inside its six-frame hardware runner. ER successfully enqueued R7 and R8 into the depth-8 monotonic software FIFO, but there are no R7/R8 consumption gates in that runner. After the sixth hardware frame, the runner stops the sensor, reports `X1E front PIX completed provider-owned bounded six-frame live requeue`, closes/purges the provider and clears `live_active`. G6 then finishes the already-proven R9 composition (`c65242e4...`), but the outer V4L2 IQ ingress correctly rejects it with `-EBUSY` because the bounded worker is no longer live.

This means optimization of the ~20.6 ms G6 producer path cannot solve ER. The next valid experiment is a **fresh nine-frame transport successor** that keeps the hardware runner alive and explicitly consumes R7, R8 and R9 at their subsequent Epoch0 boundaries. ER must never be reused.

Run facts: six video/statistics generations completed; the G1–G3 sensor-write schedule passed and affected G4–G6; R5/R6 were consumed by the existing runner; R7/R8 were FIFO-enqueued only; R9 was composed but not enqueued. No same-boot retry occurred. Full raw evidence is checksummed under `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-er/attempt1-fail-r9-transport-20260911T1157`. Golden Linux returned with camera modules/nodes absent, and ER's one-shot GRUB/boot artifacts were retired.

See `ATTEMPT1-FAILURE.json` and `RETIRE.txt`.
