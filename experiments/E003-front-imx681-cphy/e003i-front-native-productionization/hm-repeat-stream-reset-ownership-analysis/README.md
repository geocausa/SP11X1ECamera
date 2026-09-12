# E003i-HM — repeated-stream reset ownership analysis

Status: **PASS / offline only**.

HL's second-stream failure is now causally closed. The front PIX snapshot reset functions clear payload validity/source metadata but leave `x1e_3a_generation` and `x1e_tlbg_generation` untouched. Stream 1 publishes 27 generations; stream 2 therefore publishes generation 28 first, while the production IQ producer deliberately requires a fresh session to begin at generation 1.

The later `DQBUF ... sequence 0` mismatch is **secondary fallout, not a second proven sequence-reset defect**. After the producer rejects stale generation 28 it never submits R5. The kernel runner completes frames 1–3, then requires request5 before frame4 completion. That wait fails and the fourth buffer is returned with `VB2_BUF_STATE_ERROR`; the error path does not assign a V4L2 sequence, so userspace sees zero and pins fail-closed as designed.

CSID completion software counters already have an explicit zeroing epoch in `csid_reset`; HL contains no independent evidence that those counters were stale.

Next: HN adds generation=0 to both snapshot reset functions, then rebuilds and validates the production module/package offline before any new live identity exists.
