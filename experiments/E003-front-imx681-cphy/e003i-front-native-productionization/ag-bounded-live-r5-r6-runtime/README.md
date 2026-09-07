# E003i-AG — corrected bounded live R5/R6 producer runtime

Status: **prepared one-shot runtime; not yet executed.**

AG is the fresh retry package after AF failed safely before STREAMON. AF's only failure was a userspace initialization dependency: the template-free composer imported the broad Capstone-based analysis extractor under root Python. Commit `bc9b4e5` removes that production dependency by using a standard-library-only SHA-pinned Epoch0 raw-log parser. Root Python still has no Capstone in the reproduced environment, yet the complete AE producer now runs successfully and emits the accepted dynamic R5/R6 hashes.

AG makes no kernel change. It reuses the exact accepted Z/Y generation-tagged 3A/TL_BG CAMSS module, accepted IMX681 module, front-only DTB, existing deferred V4L2 IQ FIFO, and AE producer. R4 is generated template-free before STREAMON. There are no R5/R6 input capsule files. The live child producer is forked on the same inherited video fd, must report READY before STREAMON, consumes G1 for state, submits R5 from G2 and R6 from G3, and the parent independently captures six QC10C frames plus paired TL_BG/3A snapshots.

`prearm-check.sh` is mandatory and runs while SP11 is still in Golden. It verifies clean Golden state and package hashes, runs the template-free composer regression, builds the capture helper with strict warnings, then executes the complete producer under root Python against retained Z G1-G3 paired snapshots. It requires exact dynamic capsule hashes:

- R5 `350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795`
- R6 `e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c`

The runtime keeps the one-shot/no-same-boot-retry and mandatory Golden-return rules. Any producer, pairing, FIFO, provider, stream, frame-order or kernel-health error fails closed. Dynamic R5/R6 is still a bounded six-frame proof only; unrestricted continuous dynamic LSC is not claimed.
