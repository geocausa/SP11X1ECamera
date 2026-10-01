# E011BE: original AEC revision materialization

The original parent now materializes its revision through original reader RVA0xDB3A0 and copy helper RVA0xCAE7C0. The only removed inherited stub is DB3A0. E011BD independently qualified actual parent alignment1 and the bounded original initializer/caller forwarding; this experiment uses that scope.

## Verified behavior

Three SHA-pinned installed tuning candidates each reference a typed revision v0.0, mode0, no-selector0xFFFFFFFF, two-byte record from root wire offsets12(count)/16(symbol reference). The fixture accepts one nonzero byte followed by a terminator; it does not generalize this shape to arbitrary revisions.

The revision reader receives count in x2 and alignment in x3. It retains alignment in x23; CBNZ at0xDB464 skips the explicit zero-divisor trap0xDB468, then UDIV at0xDB46C performs the quotient. This explains the earlier zero-alignment fixture stop within this bounded original routine. It is not a hardware or ARM64EC defect claim.

The parent destination is payload+32. The original routine allocates two bytes, executes its original copy helper with destination capacity2 and fourth argumentU64_MAX, writes the exact two-byte typed source and advances the revision reader cursor to2. No captured scalar is an input.

- 48 parent-through-revision/four-grid prefixes: three baseline candidates plus nine owned byte variants at four placements0/0x200/0x1230/0x8010.
- 12 full-parent return smokes: three baselines at four placements.
- 60 original revision returns and60 original copy-helper calls;240 original grid returns.
- 14 malformed revision source descriptions rejected before emulation.
- Source data, reader non-cursor bytes and allocation redzones preserved; all four grid copies/nested arrays still match the typed source.

Revision adds one allocation: module384, revision2, grid array480, then four nested4-byte allocations. Checks adjust the inherited grid allocation indexes accordingly. Root cursor32 at the grid boundary and48 on full-parent return are verified.

## Scope and limits

Original revision, copy helper, memcpy, symbol resolver, grid and nested readers execute. Allocation/memset and seven explicitly listed metadata/security/comparison helpers remain stubbed; see REVISION-SAFE.json. Full-parent smoke returns do not validate sibling metadata, selector/profile semantics or full aggregate fields. E011BD's unique root/grid fingerprint remains candidate evidence rather than exact opened filename proof. The Windows initialization failure from E011BD is not diagnosed here.

No production C changes, kernel build, observer, camera start, reboot or native Linux rear activation. Original DLL, tuning bytes and decompiled C stay private on the same SP11. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f and all three protected payload hashes remain unchanged; camera idle, NTFS unmounted. Native rear runtime remains DENIED.

## Reproduce

Run only on the original SP11, in this repository:

```sh
python3 experiments/E004-front-ir-vd55g0/e011be-rear-aec-revision-materialization/source-private.py
```

The harness reads SHA-pinned private originals locally and emits derived facts only. parent-fixture-private.py is an isolated copy of the owned E011AZ fixture initializer with the revision stub removed; historical scripts/results are unchanged. source-private.py reuses E011BB typed grid validation and adds bounded revision authority.

Private read-only Ghidra source audit: ../private/E011BERevision.java and E011BE-revision-decomp.txt (never committed). An exploratory diagnostic initially mislabeled x2 as alignment; source anchors and final fixture verify x2=count, x3=alignment. The copy's fourth argument is the original truncation sentinel, not a byte count.

See REVISION-SAFE.json, GUARD-SAFE.json, RESULT.json and NEXT-SOURCE.json. Next derive and validate sibling/statistics metadata destinations beyond0x124040, then full loader/profile selection and remaining ownership/runtime gates.
