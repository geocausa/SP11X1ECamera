# BY static proof

Pinned Windows anchors:

- arithmetic SceneAnalyzer publication `0x1803efe00..0x1803efe28` duplicates the scalar with `stp s16,s16` and calls `SetDataSceneAnalyzer`;
- type-0 target calculator branch `0x1803f10b4 -> 0x1803f11b8` direct-reads the source descriptor without interpolation;
- SceneAnalyzer bank-3 getter `0x1803d5d98..0x1803d5dcc` copies slot floats at `+4` and `+8` to the two-float calculator result;
- method 11 is `0x1803f0978..0x1803f0b74`;
- its epsilon is float bits `0x33d6bf95`, and it appends 0 and 256 before sorting;
- its error helper chain `0x1800cc200 -> 0x180cf53d0` is exact float `fabs`;
- final method-11 result is stored twice with `stp s10,s10`.

`verify-by.py` independently models every float32 operation and compares the compiled native C output bit-for-bit across deterministic random and edge cases. It also demonstrates that a direct weighted-mean shortcut differs in at least one valid finite case.
