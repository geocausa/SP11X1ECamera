# CO static/native proof

## Prerequisite

CN (`8720706`) proves the exact ordinary Windows history bootstrap:

- synthetic 0x1b0 start record;
- frame ID 0, marker 1;
- seven retained exposure lanes = 33,333,332;
- real history marker 0, capacity 10;
- lookup rule: START before real history, then newest-to-oldest first sufficiently old record, falling back to the oldest available real record during warm-up;
- startup DRC history zero is the ordinary identity case.

## Native reduction

CO preserves CM's FrameSA/Lux and CF/CG/CH dataflow but changes the recurrence boundary:

1. `init()` owns a synthetic start-history entry with all retained lanes 33,333,332 and zero predictive-gain history.
2. `process()` accepts frame 0 and enforces strictly sequential frame IDs.
3. F-1/F-2/F-3 are selected by the CN lookup rule rather than exact-frame-only lookup.
4. No public or internal `seed_history()` API remains.
5. Current Short/Long/Safe/S1 post-T681 retained qwords and PredGain are committed only after the full request succeeds.

## Differential

`verify-co.py` compiles the native chain with strict FP flags and compares every request to an independently assembled reference using:

- CN history selection;
- CM FrameSA + Algorithm001 ordering;
- CF final exposure publication;
- CG convergence;
- CH T681 arbitration.

192 sequences × 12 requests = 2,304 requests PASS byte-exact.
