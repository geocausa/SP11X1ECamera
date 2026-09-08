# BR proof boundary

BR is an implementation projection, not a new Windows-semantic inference.

Prerequisites are re-run mechanically:

- BP fixes all normal-preview convergence tuning and implements the complete native convergence tail.
- BQ proves the four remaining BP scalar controls are zero for normal streaming, AEC unlocked, with temporary metering-lock context inactive.

BR removes those four fields from the public input and binds their internal carrier values to zero. It leaves target lanes and all three exposure-history snapshots explicit because those are genuine request state.

The verifier compares the full native output struct against BP configured with exactly the BQ projection. Equality is byte-for-byte over 1536 deterministic states; it is not tolerance-based.

Modes not covered by BQ are intentionally not represented by this wrapper.
