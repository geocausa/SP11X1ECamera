# E011BF: original histogram sibling materialization

The original AEC parent now materializes and validates its histogram sibling after the revision/four-grid prefix. This is an offline proof on the same SP11 using immutable SHA-pinned originals and owned input variants. Original bytes never leave SP11.

## Source authority

The root48 record supplies histogram count at wire32 and symbol reference at36. The two default candidate files have9 entries/1548 serialized bytes; the rear-specific candidate has7 entries/1204 bytes. Each selected symbol is histStatsConfig v0.0, mode0, no-selector0xFFFFFFFF. The fixture scopes counts to7/9; this is not a claim that the original parser rejects other counts.

Each172-byte histogram record contains one typed data v0.0 record from count148/ref152, followed by a typed values v0.0 array from count160/ref164. Both require mode0/no-selector; data length4 and values length4 times its wire count are validated. The scoped values count is1..1024. Actual selected reader IDs are checked at original nested reader0xEA758 entry/return, even when different symbols alias the same source span.

## Native mapping

Runtime histogram entries use200-byte stride. Payload+64 stores count, +68 stays0, +72 holds the array. Original pointer store0x124124 uses x26. The original loop header is0x124160; exit branch0x12416C reaches0x124970. The fixture stops there before BFW source materialization, with root cursor40 and histogram cursor172 times count.

For each entry, runtime0:148 equals wire0:148. Runtime152:156 equals wire148:152; runtime168:176 equals wire156:164; runtime192:196 equals wire168:172. Runtime148/156/176/180/196 remain zero fields/padding; they are not claimed to be counters with completed semantics.

Five original memcpy spans per entry are independently checked at offsets16/44/76/108/136 with lengths16/32/32/28/12. Runtime pointers160/184 reference exact typed nested data/values allocations. Their native reader cursors consume their full record lengths; arrays equal the selected source, with allocation redzones preserved. No numeric optical or tuning values are exported.

## Validation

- 76 bounded prefixes: three baselines plus eight owned scalar and eight owned nested-array variants at four placements0/0x200/0x1230/0x8010.
- Three full-parent return smokes, with histogram fields validated and BFW fields still excluded.
- 573 histogram entries,1146 typed nested arrays and2865 original scalar memcpy spans verified.
- 150 malformed histogram/root/nested descriptions rejected before emulation.
- Original revision/four-grid checks retained; source data, reader non-cursor bytes and allocation canaries preserved.

The new run method is an isolated adaptation of the owned E011BE method. Historical E011BE/E011BB files are unchanged. No additional helper stub is introduced. Original revision, grid, histogram, nested readers, string copy and memcpy execute; metadata/security/comparison/allocation/memset stubs remain explicit in HISTOGRAM-SAFE.json.

Exploratory stop candidates0x1248F4/0x1248F8 were not reached on normal completion and fell through to the fixture's return sentinel. Candidate0x124900 was after the next root count had already advanced its cursor44. These are excluded; only actual loop exit0x124970 is used for final prefixes. The derived array-store register was corrected to source-qualified x26 before the successful matrix. No driver-defect claim follows from those fixture corrections.

## Reproduce and limits

Run only on the same SP11:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bf-rear-aec-histogram-materialization/source-private.py
```

BFW sibling fields, full loader/profile selection and metadata helper semantics remain unvalidated. Histogram values are source-derived data, not observed producer policy. This does not resolve cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement or native Linux optical parity. Full-parent return alone does not close those contracts.

Zero new camera starts/reboots/observer/kernel build/production C. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f, all three protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Native rear runtime remains DENIED. E011BD's Windows initialization remains incomplete and its identity consumed.

See HISTOGRAM-SAFE.json, GUARD-SAFE.json, RESULT.json and NEXT-SOURCE.json.
