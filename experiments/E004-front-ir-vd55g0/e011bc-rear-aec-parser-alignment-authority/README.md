# E011BC: parser alignment source audit

Status: **PASS bounded source audit; caller alignment and profile authority OPEN**.

The complete four-grid E011BB proof remains conditional on explicit packed alignment 1.
This stage checks a proposed source for that argument and records a reproducible
manager-construction anchor. It does not extend the grid fixture into production.

## Verified facts

- All three independently SHA-pinned tuning roots have zero in the 16-bit header
  field at offset `0x26`. That field is not a direct source of the fixture's value 1.
  A conversion, normalization, or separate caller policy remains possible.
- Original constructor `0x6F3D08` returns at four owned-memory placements without
  helper stubs. Each execution makes exactly 12 checked member writes: the
  manager table pointer (`0x133B740`), the header identifier pointer
  (`0x1419FC8`), and zero-initialized members. Every other heap byte is preserved.
  This qualifies a header-labelled manager constructor, not a deserializer caller.
- An original halfword read at `0x6F0258`, in candidate function `0x6F01E8`,
  accesses an input offset `0x26`. Its association with the AEC deserializer
  caller is unproven.
- Readonly private source exploration identified manager/root-loading and factory
  candidates `0x6F1EA0`, `0x6F3F48`, `0x6F4238`, and `0xDAEF8`.
  Candidate loading function `0x6F0470` is another bounded follow-up.
  These are navigation anchors, not qualified alignment or profile policy.
- The second header-identifier reference (`0x871644`) belongs to a large
  decompilation with implausible offsets. Its inferred semantics are excluded.

## Limits and next work

No actual entry argument for `0x123CC0` or loaded slot bytes were captured.
The prior source vtable `0x1335598`, slot +8, still points to that deserializer.
Resolve the actual caller and any zero-to-nonzero conversion independently.
If a fresh original Windows observation is needed, qualify loaded code and slot
bytes first, observe the entry alignment and reader lineage, and use a new
single-use identity. No observer or identity was created here.

Exact selected tuning filename, whole profile/revision materialization, cold
metadata ownership, normal RS authority, deterministic bootstrap, WM16 retirement,
and native Linux optical parity remain open. No captured scalar becomes a
producer input. Native Linux rear runtime remains **DENIED**.

## Reproduction and evidence

Run on the same SP11 with its private originals:

```bash
python3 experiments/E004-front-ir-vd55g0/e011bc-rear-aec-parser-alignment-authority/source-private.py
```

`SOURCE-SAFE.json` contains only hashes, booleans, offsets, counts, and RVAs.
`GUARD-SAFE.json` records Golden protection checks.
`NEXT-SOURCE.json` and `RESULT.json` preserve the precise remaining gates.
Original OEM code, decompiled C, tuning bytes, and prior captures remain private
on this SP11. No production C, kernel build, camera Start, or reboot occurred.
