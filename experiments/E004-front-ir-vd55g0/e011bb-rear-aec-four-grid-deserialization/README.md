# E011BB — original four-grid deserialization

Status: BOUNDED OFFLINE FOUR-GRID MAPPING PASS; CALLER ALIGNMENT/PROFILE POLICY OPEN.

The original parent reader123CC0 now executes through all four calls to grid reader123550, stopping at the parent grid-loop boundary124040. The fixture explicitly supplies packed serialized alignment1. Across137 source/mutation cases at four placements,548 parent prefixes produce2192 complete grid-reader returns and6576 matching weight fields. Native memcpy and the original grid/symbol/array readers execute without replacement.

| Grid index | Serialized entry start | Runtime entry start | Serialized weight start | Runtime weight start |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 20 | 20 |
| 1 | 101 | 120 | 121 | 140 |
| 2 | 202 | 240 | 222 | 260 |
| 3 | 303 | 360 | 323 | 380 |

Each original reader consumes101 bytes and returns success, ending at404 bytes. All four12-byte weight blocks match source, as do16-byte copy spans at per-entry offsets32 and48. The original tail helper123B80 reads count1 at wire+89 and resolves a typed data v0.0 symbol at wire+93, copies its four bytes into an allocated nested array, and retains that pointer at runtime grid+104. These source values/pointers and all allocation canaries are checked.

Three independently parsed SHA-pinned installed Default roots each match all four E011BA private live weight blocks:12 comparisons/144 bytes. Captures are comparison outputs only. Sixty-four malformed root/child/nested-symbol descriptions are rejected. Four unsupported alignment arguments are rejected by this fixture's explicit scope check; they are not claimed as native parser policy tests. Source bytes remain unchanged.

The earlier123820 BRK is source-qualified as a zero-divisor guard: x21 retains the third argument at123570; cbnz at12381C skips the guard to udiv at123824. Zero in the previous fixture reaches the guard. It was not an ARM64EC environment requirement or an OEM defect. Packed alignment1 permits the complete four-grid reader, but its actual caller/live authority remains OPEN. The original materialized module table1335598 has deserializer123CC0 at slot8. All four E011BA named object table pointers normalize to1335598; actual loaded slot bytes and the deserializer alignment argument were not captured.

The serialized parent count materializes at payload+2C=4, while nearby+30 remains0. No completed-element interpretation is assigned to+30. Three baseline full parent-return smoke checks also pass, consuming48 root bytes. They do not validate sibling numeric fields or full metadata/profile policy.

Revision materialization and metadata/security/name/comparison/allocation/memset helpers remain excluded/stubbed as in E011AZ. The tested grid readers, nested symbol/array helper, arithmetic/cursor bookkeeping and memcpy are original. Whole-profile materialization, exact loaded filename, cold numeric policy, complete deterministic bootstrap and Linux optical parity remain OPEN. No captured weight or constant became a clean-C policy input.

The initial largest-placement check exposed insufficient owned mapping capacity. The fixture now extends only its owned table/data mapping capacity, retaining each original record's size/bounds; the final548 cases pass. Exploratory alignment2/4/8 runs are excluded, not driver-failure evidence. Private Ghidra parser inspection remains source exploration rather than caller-policy closure.

Golden boot and all three protected payload hashes remain unchanged; saved FullIOv19c, empty next_entry, NTFS unmounted and camera idle. No camera Start, reboot, production C change, kernel build or native rear activation. Raw originals, tuning, native image bytes and live captures stay private on SP11.

Next source-close the original deserializer caller's alignment argument and selected file/profile authority, then revision/metadata dependencies before detached source-only integration. Separately close cold metadata ownership, normal RS count/offset policy, complete bootstrap and independent WM16 retirement. Native Linux rear runtime remains DENIED. No new identity or observer is armed; E011BA remains consumed.

See source-private.py, DESERIALIZATION-SAFE.json, ALIGNMENT-SOURCE-SAFE.json, GUARD-SAFE.json, NEXT-SOURCE.json and RESULT.json.
