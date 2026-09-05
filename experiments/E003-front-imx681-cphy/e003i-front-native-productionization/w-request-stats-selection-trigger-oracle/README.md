# E003i-W — request/statistics selection + LSC trigger oracle

Status: **PASS; Golden return verified**.

One direct-Windows gated cycle dynamically closed the exact request/statistics selection law without treating parser count as a request ID. The trace logged Titan680 parser output pointers at RVA `0x5f09d0` and, on the same live process, `IQInterface::LSC411CalculateSetting` request frame, selected Tintless stats pointer and request trigger block at RVA `0x88e1e8`.

Across **104 non-null LSC calls, 104/104 selected-stats pointers matched a preceding parser output pointer exactly**. Every match obeyed one invariant: **`request_frame = source_generation + 3`**. Warm-up LSC frames 1/2 had null stats; frame 3 was absent. Fourteen parser generations were not selected, and their `generation + 3` values exactly equal all later missing request frames, independently confirming the selection law. Thus request4 selects source generation1, request5 selects generation2, and request6 selects generation3. Source generation remains a source identity, not a request ID.

The same LSC calls captured the raw request-local `ISPIQTriggerData` block. `ANALYSIS.json` preserves exact request4/5/6 raw words and decoded AEC gain/lux, AWB/CCT, DRC, geometry and black-level fields. The full 74,198-byte KD log remains SHA-pinned on SP7.

This checkpoint still does **not** authorize Linux R5/R6 substitution. The next gate is Linux producer timing and live trigger-state acquisition: R5 needs source generation2 and R6 needs source generation3, so userspace/kernel scheduling must prove those generations and the corresponding trigger state are available before the respective steady IQ consumption gates.
