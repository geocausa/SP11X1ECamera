# E003i BY — native Windows method-11 point aggregation

Status: **PASS (native/offline)**.

BY transcribes the final Windows target-component aggregation method used by BV into native C for the exact point-value case present on the ordinary analyzer path.

The missing structural fact is now closed: arithmetic SceneAnalyzer publications write `stp s16,s16` before `SetDataSceneAnalyzer`, and type-0 target calculators direct-read those two floats from the SceneAnalyzer bank. Therefore the final Safe/Short/Long method-11 inputs are duplicated point pairs `[v,v]`, not arbitrary low/high ranges.

The implementation deliberately preserves the complete interval search. It does **not** replace it with a weighted average: float32 rounding makes that shortcut observably wrong by one ULP in valid finite cases such as a single positive-weight candidate.

The native function retains Windows' positive-weight boundary filter, epsilon `0x33d6bf95`, appended 0/256 bounds, sorted interval scan, float32 weighted sums, clamped candidate and `fabsf` metric with initial best value -1 and metric 100000.

This checkpoint closes the aggregation primitive only. It does not yet claim that all upstream analyzer scalar publications have been natively reproduced.
