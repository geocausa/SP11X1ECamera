# E003i BZ — Windows SafeAgg publication identity

Status: **PASS (static/offline)** once `verify-bz.py` passes.

BZ closes the arithmetic step between SafeAggSA target component output `SceneAnalyzer 3:8` and its final SI/publication `3:9`. The pinned tuning record's final `AdjRatio` operator is runtime enum 2 (`MUL::(AxB)x(CxD)`), with operands `DB(3:8)`, `1.0`, `1.0`, `1.0`; the DLL executor performs three separate float32 multiplies. Thus, in the finite ordinary-preview domain already used by BY, `3:9` is bit-identical to the method-11 SafeAgg target scalar at `3:8`.

This removes one opaque arithmetic hop before ShortAgg/LongAgg. It does not yet claim the complete Short/Long post-aggregation arithmetic chains. No camera runtime or Golden mutation is used.
