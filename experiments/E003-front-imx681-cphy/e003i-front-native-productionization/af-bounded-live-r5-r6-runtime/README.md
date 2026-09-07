# E003i-AF — bounded live R5/R6 producer runtime

Status: **prepared one-shot runtime; not yet executed at this commit.**

AF makes no kernel change. It boots the exact Z/Y generation-tagged 3A/TL_BG CAMSS module and the already-accepted front-only IMX681 graph, then runs the committed AE producer through the existing deferred V4L2 IQ FIFO.

R4 is generated before STREAMON by the template-free composer and is the only bootstrap capsule. There are no R5/R6 input capsule files. The child producer is forked on the same inherited video fd, must report READY before STREAMON, processes G1 for temporal state, then computes and submits R5<-G2 and R6<-G3. The parent independently captures six QC10C frames and the paired stats snapshots for post-run verification.

This package preserves one-shot/no-same-boot-retry behavior and mandatory return to the saved Golden entry. Any producer, pairing, FIFO, provider, stream or frame-order error fails closed.
