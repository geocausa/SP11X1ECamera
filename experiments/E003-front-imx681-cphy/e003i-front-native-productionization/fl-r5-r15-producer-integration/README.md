# E003i-FL — live-capable R5–R15 producer integration

Status: **PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION / no FL camera runtime.**

FL extends the already-live-proven FD producer architecture from G1..G9/R5..R12 to G1..G12/R5..R15. It preserves the live scheduler, generation-tagged paired-stat ingress, CQ gain feed, dynamic AWB, native Tintless/LSC, GTM/Demux composition and V4L2 submission path.

Offline proof uses immutable FF G1..G12 stats and CQ gains:
- R5..R12 reproduce the real FF live capsules 8/8 byte-exact, including key dynamic metadata.
- R13..R15 match the FJ-authorized deterministic capsule hashes exactly.
- two independent FL runs reproduce all R5..R15 capsules exactly.

FL is live-capable code but has not run camera hardware.
