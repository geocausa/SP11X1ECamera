# E011DK — normal RS metadata handoff and checked input decoder

**PASS, bounded source and C qualification.** The original statistics metadata reader copies the supplied RS record into the pre-adjustment input. A new C decoder converts that record into the existing E011AM numerical producer's input, without choosing or freezing normal counts.

| Boundary | Added evidence | Remaining scope |
| --- | --- | --- |
| Original reader RVA 740E70, 1792 bytes | 96 cases, 39,904 original instruction visits; all 132 RS bytes exact | Query helper, registry, runtime tag-vector initialization and upstream AFD publisher are fixtures or unexecuted |
| Present / absent / fallback record | 32 cases each; absent preserves the prior destination record | No claim about actual runtime query results or absent-record policy in the whole pipeline |
| Checked C decoder | GCC and Clang ASan/UBSan; three observed records and 42 input/output fields exact per compiler | Whole-frame crop and zero incoming stripe offsets only |
| Invalid or unsupported input | 21 rejection cases per compiler, before output effects | Unsupported scopes fail closed |
| Existing RS arithmetic / initial counts | Reuses E011AM / E011M | Upstream normal count policy is still open |

The metadata reader queries seven slots through RVA 5D4D30. RS is slot 5 in the property vector at RVA 17A30E0 (RS tag cell 17A30F4); its destination is crop/stripe owner + 2C50. Present data is copied as 128 bytes plus the final four bytes. An absent primary query can use the fallback query; if both are absent, the previous 132-byte record remains intact.

The new `normal-rs-input.h` decodes H/V counts at record +0/+4, requires zero offsets at +8/+12, and reads color conversion at +128 separately from module enable. Crop dimensions are inclusive, whole-frame only; the caller supplies a normalized half-width flag. E011AM validates all numerical constraints before the decoder writes its output. Null, non-132-byte, unsupported offsets/crop origin, invalid counts/flags, dimension overflow and overlapping output storage are rejected. A missing record does not acquire a guessed default.

The source reader runs unchanged, including its original frame save/restore helpers. Four placements and eight payloads (three previously observed records plus five owned synthetic records) cover each query state. Entire owned heap changes are checked against only the expected RS copy; source records, executable bytes, incoming SP, callee-saved registers and stack redzones remain intact. Logical lock ownership balances.

**Explicit fixtures:** API results, registry/settings objects, loader/TLS state, lock objects and runtime property tag-vector values. The body of query helper 5D4D30 and actual property-tag initialization are not executed. On-disk BSS is not runtime tag authority. This proof establishes the consumer and decoder contract; it does not establish an AFD count-producing algorithm, full startup, concurrency or hardware behavior.

Earlier work is retained: E011M already establishes initial Titan680 RS defaults, E011AM supplies numerical adjustment/binding, and E011AK already proves sampled unity BG gain binding (16 samples; arbitrary gain unsupported). E011DJ remains the unchanged selected-baseline input ledger. The separate original factory/enumeration branch remains at E011DI.

Run `python3 -B verify.py` for read-only source/evidence lock and scope checks. `source-private.py` is an authored SP11-only qualification harness using private originals and prior private fixtures. It exports only derived facts in `SOURCE-SAFE.json`; no raw records, original instruction text or optical data belong in Git.

**NEXT E011DL:** trace the actual RS property-tag initialization/publication and slot-5 query dependency, then the upstream normal AFD count/offset policy. Reuse closed numerical and initial-count work. Required selected input/profile integration, deterministic bootstrap/preflight, independent enabled-output DMA/IOMMU retirement and the finite clean-colour front/rear/off app gate remain open. Native rear runtime stays denied. No camera Starts, reboots, kernel builds or optical tests were performed here.
