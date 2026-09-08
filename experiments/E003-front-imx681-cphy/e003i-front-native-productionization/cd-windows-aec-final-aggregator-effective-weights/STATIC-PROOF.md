# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Pinned tuning SHA256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

The runtime target-calculator record is `0x60` bytes, with value and weight halves. In the analyzer loop:

- weight method is read at runtime calculator `+0x30`;
- method 0 branches to a generic bank read from direct descriptor `+0x34`;
- method 1 instead reads trigger descriptors `+0x40` and `+0x48`, calls the common interpolator, loads its scalar result and stores that result as the candidate weight.

ShortAggSA and LongAggSA shared Safe calculator records both have weight method 1, serialized direct descriptor `3:6`, trigger descriptors `(9:8, 9:8)`, and a one-region trigger program ending in exact `0.001f` bits `0x3a83126f`.

Because method 1 never reaches the `+0x34` generic-read branch, Frame confidence `3:6` is not part of the effective weight expression. CB's committed interpolation proof establishes the one-region clamp behavior, so both trigger coordinates collapse to the sole leaf.

The dedicated Short/Long candidate weight halves use method 0 and direct descriptors `3:58` / `3:63` respectively.
