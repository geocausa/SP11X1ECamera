# E003i-HO — fresh repeated-stream shadow R27 candidate after generation-reset fix

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HO is the fresh successor to retired HL and uses HN's deterministic production package. Its only kernel delta from HJ is the HM/HN snapshot-session fix: 3A and TLBG generation counters reset to zero under their existing locks, so each fresh stream begins at generation 1.

Runtime authorization remains deliberately narrow: exactly two sequential 27-frame streams in explicit post-G3 `shadow` mode, zero post-G3 native writes, and no same-stream or same-boot retry. The existing strict producer generation contract is unchanged.

The invocation harness retains the corrected pre-stream marker logic from HL and is exercised offline without camera access. Archive creation additionally normalizes ownership in the archive copy before hashing, fixing the evidence-only permission issue encountered during HL failure archival.

## Attempt 1 result

**PASS.** The fresh HO one-shot completed two sequential 27-frame streams. Both streams produced 24 live IQ generations / 23 R5..R27 submissions, exactly three startup native sensor writes, zero post-G3 native writes, and clean STREAMOFF. The strict generation contract restarted correctly for stream 2 after the HN reset fix. Kernel health passed, no retry occurred, Golden return passed, and the HO candidate was retired.

Final archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ho/attempt1-pass-two-stream-shadow-20260912T081541`

Final manifest SHA256: `35975ea08e695d69d8ff69cf530b1236230cb43fb0d9bc739c0538dec2d2c57c`.

This proves bounded **two-stream** lifecycle robustness in shadow mode. It does not authorize changed post-G3 native feedback or claim long-duration soak robustness.
