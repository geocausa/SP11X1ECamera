# E003i-DZ — current CQ publish before previous sensor release

Status: **IMPLEMENTED / OFFLINE GATE PENDING.**

DY attempt1 proved the residual ISP gain and Demux/BLS arithmetic were correct, but exposed a scheduling regression: G2's CQ residual gain was not published until after the G1 sensor ioctl. That sensor ioctl took 23.5 ms in the failed run, so R5 missed its IQ submission window and returned EBUSY.

DZ changes only the parent audit-thread ordering:

1. consume the exact current generation TL_BG/STATS3A pair;
2. run the already-proven native AEC/CQ path;
3. queue the current sensor tuple;
4. publish the current CQ residual ISP gain to the producer;
5. only then release/write the previous generation sensor tuple at the same completed-DQBUF boundary.

Thus the IQ producer can compose/submit R5/R6 concurrently with the previous sensor ioctl, restoring the concurrency DS had in the successful DT run. The scheduler algebra is unchanged: source G1/G2/G3 still releases after completed G2/G3/G4 and is expected in statistics G4/G5/G6.

No camera runtime is performed by DZ.
