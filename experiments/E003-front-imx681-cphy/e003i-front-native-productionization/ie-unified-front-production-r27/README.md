# Camera IE — unified-DTB front production R27 regression

Status: **PASS live front regression / Golden restored / candidate retired**.

IE is the front counterpart to accepted ID. It uses the exact IB unified rear+front DTB that already passed the rear regression and replays the proven HY production front contract under a fresh one-shot identity. The module set is exact front-production CAMSS + IMX681 plus accepted OV13858 solely so the unified async graph can bind. Rear streaming is forbidden.

The live contract is exactly one 27-frame front production stream with explicit shadow post-G3 policy. Acceptance is HY-equivalent: fresh generation-1 statistics, 24 producer generations / 23 R5..R27 submissions, startup native writes G1..G3 only, zero post-G3 native writes, four hardware control transactions including bootstrap, exact QC10C/TLBG/STATS3A artifact sizes, STREAMOFF and clean kernel health.

Before the attempt, IE must discover both sensors on the unified graph and prove the rear mutable route remains disabled. IE never enables the rear route and never opens the rear video node. There is no same-stream or same-boot retry. The attempt is consumed immediately before the single launcher invocation. After any attempt the machine returns directly to protected Golden, evidence is archived, and the candidate is retired.

The exact IE candidate is now installed under /boot/sp11-7.1.5-camera-ie-unified-front-r27. Golden remains the saved default and next_entry is empty. Installed-unarmed state must be committed and pushed before arming.

## Live result

IE passed exactly one unified-DTB front production stream. Both sensors bound on the unified graph; the rear mutable route was disabled before the attempt and remained disabled after STREAMOFF. The front stream delivered 27/27 buffers, fresh generation-1 statistics, 24 producer generations with 23 R5..R27 submissions, startup sensor writes G1..G3 only, zero post-G3 native writes, four hardware control transactions including bootstrap, clean STREAMOFF and clean kernel health. No rear stream and no retry occurred.

Candidate boot ID ac146025-d952-47e5-9625-6c1db7691f4b; Golden return boot ID 3c716d5b-7f1e-4fa8-a370-e4814150b2b3. The candidate is retired. Final archive manifest SHA256: 9ad7fa2649d688a23105d99dc1782d7b3b8eeb14cfe894c2fc435e5c21c9496e.

Together, ID + IE prove the accepted rear path and the HY-equivalent front production path separately under the same unified IB DTB and module authority. They do not yet prove same-boot camera switching or repeated-stream reset ownership.
