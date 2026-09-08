# E003i BK — native AEC exposure-history request state

Status: **PASS (target-native offline)** — removes BH's abstract F−3 scalar seam. The request-state layer now accepts only seven-lane linear exposure history and derives Algorithm001's F−3 S1 `log1.03` baseline internally through BJ.

## Closed recurrence

For ordinary front request `F`:

1. read the internal `(9,8)` Lux trigger present at request entry;
2. evaluate BG `FrameSA_Target` and BD Safe<-S1 target SI from current measured luma;
3. fetch exposure history `F-3`, select internal **S1 lane 3**, and convert its linear retained exposure to the BI/BJ `log1.03` coordinate;
4. run Algorithm001 and write the new internal Lux trigger;
5. expose that Algorithm001 result on the separate external publication queue at `F+2`;
6. independently expose seven-lane exposure history `F-1` for downstream convergence.

This removes the old `commit_history_reference(frame,float)` input entirely. The only temporal history input is now the same seven-lane linear exposure state that downstream convergence already needs.

## Live cross-check

Using the committed AB2/BI S1 retained exposure `33,312,451` at `F-3`:

- internally derived coordinate = `0x4365acdd`;
- AB R1 measured-luma input = `0x3f1e9ed8`;
- Algorithm001 output = `0x43bd1baa` bit-exact.

All eight previously committed AB Algorithm001 live cases are also rechecked through the target-native C implementation when supplied their captured F−3 coordinates.

## Remaining seam

BK does **not** yet generate the next seven-lane exposure history autonomously. That requires integrating the already-separated AY/AZ/BA/BB convergence stages and BC linearization. Until then, callers commit each completed seven-lane exposure snapshot explicitly. The F−3 Lux-baseline scalar itself is no longer external.

No camera stream, sensor, module, MMIO, or Windows boot is used.
