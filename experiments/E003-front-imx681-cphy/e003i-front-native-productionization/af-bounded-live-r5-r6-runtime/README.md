# E003i-AF — bounded live R5/R6 producer runtime

Status: **FAIL_PRESTREAM_PRODUCER_DEPENDENCY; one-shot boot executed, no STREAMON, Golden return verified.**

AF makes no kernel change. It boots the exact Z/Y generation-tagged 3A/TL_BG CAMSS module and the already-accepted front-only IMX681 graph, then runs the committed AE producer through the existing deferred V4L2 IQ FIFO.

R4 is generated before STREAMON by the template-free composer and is the only bootstrap capsule. There are no R5/R6 input capsule files. The child producer is forked on the same inherited video fd, must report READY before STREAMON, processes G1 for temporal state, then computes and submits R5<-G2 and R6<-G3. The parent independently captures six QC10C frames and the paired stats snapshots for post-run verification.

This package preserves one-shot/no-same-boot-retry behavior and mandatory return to the saved Golden entry. Any producer, pairing, FIFO, provider, stream or frame-order error fails closed.

## Executed result

The AF boot was consumed once. The producer failed during initialization because the template-free composer imported the broad `extract_vfe1_epoch0_cdm_batches.py` analysis module, whose top-level Capstone dependency is absent from root's runtime Python environment. The parent never observed producer READY and therefore refused to call STREAMON. There were zero QC10C frames, zero TL_BG/3A snapshots, and no R5/R6 dynamic capsules or submissions. The post-attempt kernel fault scan was clean and SP11 returned directly to the saved Golden entry without a same-boot retry. `RESULT.json` pins the local RUN/POST/DMESG evidence hashes.
