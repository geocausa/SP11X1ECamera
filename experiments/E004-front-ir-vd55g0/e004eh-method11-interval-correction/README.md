# E004eh — restore Windows method-11 interval semantics

E004eg disproved the lighting hypothesis and localized the runaway front AEC before the cap. E004eh closes the remaining root cause.

The old native implementation specialized Windows target aggregation method 11 to scalar points. Fresh live Windows startup tracing proved that specialization false for ordinary front preview: SatPrev, DarkPrev, ShortSatPrev and Illuminance publish genuine low/high ranges. Windows method 11 applies zero penalty while a candidate range overlaps the test interval. Collapsing those ranges to their high endpoints pulls SafeAgg far away from FrameSA and causes the Linux exposure recurrence to inflate.

The correction restores `[low, high, confidence]` candidates and the exact generic Windows range method-11 arithmetic. FrameSA remains a point. Tuned ordinary ranges are restored as follows:

- SatPrev: `[0, computed_high]`.
- DarkPrev: `[computed_low, computed_high]`, including the distinct low-target/method2 tree.
- ShortSatPrev: `[0, computed_high]`.
- Illuminance: `[0, computed_high]`.
- zero-confidence analyzers remain inert.

The fixture `evidence/E004EG-G1-STATS3A.bin` is the exact first Linux statistics generation from E004eg. G1 is causally clean for this counterfactual because it was captured before any output from the old wrong recurrence could affect a later sensor frame. The old point implementation produced Short convergence 154,912,929. The interval-corrected replay produces 84,034,875, versus the historical authoritative Windows request-4 value 82,061,904 from the earlier DI oracle. The fresh darker-scene E004EH request-4 value is 133,645,888 and is retained only as a structural range oracle, not as a same-scene numerical comparison.

No live camera runtime is authorized by this checkpoint. It is an offline/source correction gate only.
