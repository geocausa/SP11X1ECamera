# Camera IE — unified-DTB front production R27 regression

Status: **prepared / not installed / not armed / no runtime**.

IE is the front counterpart to accepted ID. It uses the exact IB unified rear+front DTB that already passed the rear regression and replays the proven HY production front contract under a fresh one-shot identity. The module set is exact front-production CAMSS + IMX681 plus accepted OV13858 solely so the unified async graph can bind. Rear streaming is forbidden.

The live contract is exactly one 27-frame front production stream with explicit shadow post-G3 policy. Acceptance is HY-equivalent: fresh generation-1 statistics, 24 producer generations / 23 R5..R27 submissions, startup native writes G1..G3 only, zero post-G3 native writes, four hardware control transactions including bootstrap, exact QC10C/TLBG/STATS3A artifact sizes, STREAMOFF and clean kernel health.

Before the attempt, IE must discover both sensors on the unified graph and prove the rear mutable route remains disabled. IE never enables the rear route and never opens the rear video node. There is no same-stream or same-boot retry. The attempt is consumed immediately before the single launcher invocation. After any attempt the machine returns directly to protected Golden, evidence is archived, and the candidate is retired.
