# Public C-PHY reader semantics, 2026-10-12

The Qualcomm GPL CSIPHY2.1.2 table and its actual public reader are pinned at
LineageOS revision9f97a168359d55d3e1806a6c568bb285cfd6a906. The reference
manifest records original paths, immutable URLs, SHA256 and Git blob IDs.
No proprietary Windows inputs are used by this qualification.

`tools/test-upstream-cphy-public-reader.py` extracts the unchanged
`cam_csiphy_cphy_data_rate_config()`, three public structure declarations,
parameter definitions,28 complete data-rate arrays and their selector table.
Only device surroundings, MMIO, sleep and logging are hosted models.
CDR sweeping and auxiliary settings are disabled in this scope.

```sh
python3 -B tools/test-upstream-cphy-public-reader.py \
  --reference-directory /path/to/public-cphy-reference
```

Fetch the three files using the immutable URLs in
`cphy-public-reader-reference-20261012.json`, retaining each listed relative
path below the reference directory. The test rejects content changes or
symlinks before extracting code. It uses installed GCC and Clang.

Each compiler passes2,688 cases:28 bin boundaries (below/at/above),8 modeled
PHY indices and4 settle counts (0,34,256,65535). Tests verify16,128 dynamic
settle-byte writes and8,064 default CDR writes. Five invalid-input controls
return before MMIO. The observed missing-table no-op and above-maximum clamp
are retained as findings, not as upstream runtime admission.

This matters for the new standalone PHY:
- The nominal0x22 settle bytes in the2.5Gsymbol/s table are placeholders.
  The reader replaces them from caller settle state. Copying the bytes does
  not reproduce its timing contract.
- The public selector uses per-lane bandwidth thresholds rounded from
  2.28bits/symbol. A generic C-PHY symbol-rate interface needs an explicit,
  reviewed conversion and supported range.
- A missing table and a rate above the table maximum can return success in
  the public implementation. The new provider should reject unsupported
  configuration before power/reset/MMIO.
- The public3PH base array contains69writes and the2.5Gsymbol/s rate array36.
  Common/reset/IRQ/lane-enable operations are separate; do not treat an
  aggregate write count as proof of a complete receiver contract.

The first host harness failed because an extracted macro lacked a separator
before a structure declaration. That attempt is retained on SP11; the harness
separator was corrected, and all public source pins stayed unchanged.
These tests are source-only. They do not establish a generic PHY C-PHY ABI,
valid timing on SP11, physical power recovery, sensor topology or capture.
Existing accepted transport evidence remains useful but does not qualify
this new split-PHY candidate.
