# E003i-HO — fresh repeated-stream shadow R27 candidate after generation-reset fix

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HO is the fresh successor to retired HL and uses HN's deterministic production package. Its only kernel delta from HJ is the HM/HN snapshot-session fix: 3A and TLBG generation counters reset to zero under their existing locks, so each fresh stream begins at generation 1.

Runtime authorization remains deliberately narrow: exactly two sequential 27-frame streams in explicit post-G3 `shadow` mode, zero post-G3 native writes, and no same-stream or same-boot retry. The existing strict producer generation contract is unchanged.

The invocation harness retains the corrected pre-stream marker logic from HL and is exercised offline without camera access. Archive creation additionally normalizes ownership in the archive copy before hashing, fixing the evidence-only permission issue encountered during HL failure archival.
