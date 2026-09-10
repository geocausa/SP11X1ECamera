# E003i-DL — exact G4 native AEC failure replay

Hypothesis: the archived attempt4 G1..G4 statistics reproduce DB's G4 Short-T681 out-of-range rejection through the unchanged DJ/CU/CV recurrence. Trace the retained history, metering targets and convergence before considering any correction.

Base: `8bc6598440f5ddeb36587e140bf64f48eaee38bf`.

Scope: additive offline replay and evidence only. No sensor access, camera module loading, boot candidate installation, or change to exposure math. Golden return verified before analysis. Runtime archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-db/attempt4-live-g4-fail-20260910T181907`.

Expected observation: exact first three sensor tuples and CV `-142` at G4; inspect CU's partial output without weakening CV's atomic failure contract. Preserve policy-0 T681 rejection. Rollback: omit this additive experiment; production sources remain unchanged.

## Result

**PASS: exact offline failure reproduction and static omission proof.** The unchanged loop reproduces all three live control tuples and G4 -142. Windows applies an internal CapExposure stage before convergence publication; native CG/DJ omit it. Exact request-local bounds and conditional cap semantics must be recovered before implementing the fix. See [STATIC-PROOF.md](STATIC-PROOF.md) and [HANDOFF.md](HANDOFF.md).

Run `python3 verify-dl.py` and `python3 verify-cap-stage.py`. No new hardware run was started. Full continuous AEC remains unproven.
