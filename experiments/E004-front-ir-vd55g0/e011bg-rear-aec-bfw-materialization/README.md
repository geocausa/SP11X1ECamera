# E011BG: original BFW sibling and ROI materialization

The original AEC parent now validates its BFW sibling through full parent return in owned fixtures. Original ROI reader0xE8CC8 and nested data reader0xEA758 execute; no new helper stub is introduced. The proof stays on the same SP11 and exports only derived facts.

## Typed source and native mapping

All three SHA-pinned candidates contain one bfwStatsConfig v0.0, mode0, no-selector0xFFFFFFFF,140-byte symbol selected from root wire count40/ref44. Each BFW record selects five typed BFWROICombo v0.0 records from count12/ref16:160 bytes total. A typed data v0.0/no-selector4-byte record is selected from count132/ref136. The one-record/five-ROI/count1 shape is fixture scope, not a general parser rejection policy.

The runtime BFW object is160 bytes, with payload count80 and pointer88; nearby84 stays zero. Runtime0:16 equals wire0:16, runtime32:144 equals wire20:132, runtime144:148 equals wire132:136. Runtime16:24/148:152 stay zero. Pointer24 references the ROI allocation; pointer152 references the nested data allocation.

Each ROI is32 bytes, with two original16-byte reader calls at124D80/124D90 targeting0xE8CC8. Ten calls consume the selected160-byte reader in16-byte steps and write exactly the typed source. Source/output contents are compared privately, never printed. The BFW data reader at125414 selects the actual typed reader, consumes4 bytes and returns the exact allocation. Original scalar memcpy spans wire32/44/64 -> runtime44/56/76, lengths12/20/20, are independently checked.

The full parent returns its allocated module; root cursor48, BFW140, ROI160 and data4 are exact. Allocation lengths after histograms are160/160/4. Inherited revision/four-grid/histogram checks remain active, including source data, reader non-cursor bytes and allocation redzones.

## Validation

- 27 source cases: three baselines plus eight owned BFW scalar, eight ROI and eight nested-data variants.
- Four memory placements0/0x200/0x1230/0x8010.
- 108 original full-parent returns and108 BFW records.
- 540 ROI combinations,1080 original ROI-reader returns and108 nested BFW data arrays.
- 772 inherited histogram entries verified.
- 34 malformed BFW/root/nested descriptions rejected before emulation.

Run only on the original SP11:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bg-rear-aec-bfw-materialization/source-private.py
```

Historical E011BF/E011BE source/results are unchanged. BFW-SAFE.json lists remaining metadata/security/comparison/allocation/memset stubs. Proprietary bytes, private source/decompilation and optical captures stay on SP11.

## Limits and next work

This closes the bounded BFW numeric/ROI/nested mapping for these typed records. Full parent metadata, every grid member, exact opened filename, complete selector/profile semantics and loader behavior remain unproven. Prior grid checks cover weights/copy spans/nested arrays, not every scalar/reserved field. Parent return is not proof of the stubbed helpers.

Next qualify metadata6F4AC0/6F45D8 and comparisonF5DF00, audit remaining root/grid fields, then original loader6F22C8/profile selection. Cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remain open. E011BD's Windows identity remains consumed and initialization incomplete.

No production C changes, kernel build, camera start, reboot or observer. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f and all three protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Native rear runtime remains DENIED.

See BFW-SAFE.json, GUARD-SAFE.json, RESULT.json and NEXT-SOURCE.json.
