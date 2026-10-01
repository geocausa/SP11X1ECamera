# E011BJ — reader pre-callback mapping and metadata widths

Bounded original-code pass on SP11. The reader now reaches its final callback boundary with correctly supplied file-relative data offsets, and isolated metadata-constructor fixtures qualify full-width numeric propagation. Callback/profile/filename authority and full-parent integration remain open.

## Corrections to earlier interpretation

The metadata constructor stores x2 as eight bytes at object+60 and x4 as eight bytes at object+72. The upper halves at +64/+76 are preserved, including nonzero owned patterns. E011BH supplied only U32 values in these two registers; its zero-high-half results remain valid within that scope, but are not general zero-field invariants. Its descriptive “major/minor/tag” argument labels must not be used as independent policy authority. This stage calls them u64 x2, u32 x3 and u64 x4.

The original AEC parent sets x2 to literal10 at 0x123D70, loads x3 as a 32-bit scalar from reader+68, and x4 as eight bytes from reader+60. Wide x2 tests qualify the generic constructor, not acceptance of arbitrary versions by that parent.

The reader constructor's x4 is an object-section offset relative to the x1 file base. Its pointer at reader+208 is file_base + section_offset + serialized u32 at record+48. Supplying an absolute payload address as x4 produces incorrect address arithmetic; exploratory fixtures doing that were incomplete, not evidence of an OEM fault.

## Accepted evidence

44 original reader prefixes stop at 0x6F4A7C, before callback target loading/dispatch. Twelve use typed AEC root records from three SHA-pinned files, and32 use eight owned numeric variants across four placements. The layout is obtained from pinned source before applying owned variants; historical typed-schema validation is unchanged.

The accepted packed-alignment1 fixture supplies a zero-filled owned file context and an unused interface placeholder. It validates serialized bytes36:44 -> reader52:60, bytes44:48 -> reader68:72, bytes52:56 -> reader200:204, the complete file-relative payload pointer, and a56-byte cursor advance. ID/name checks and original32-byte memcpy are retained. Reader+72's first byte is zeroed; reader60:68 remains untouched for the callback to supply. These are byte/width facts; semantic version/mode/profile policy is not inferred from numeric patterns.

48 original metadata-constructor full returns cover twelve numeric combinations at four placements, including nonzero high halves, sign-bit patterns and U64_MAX. Each independently executes the original name helper and matches its40-byte output; the embedded name helper also executes. Six numeric scope violations are rejected before execution.

Complete heap and source-map comparison permits only the asserted writes and one bounded primary-name allocation. Source strings, owned contexts, file contents and allocation guards remain intact. Reader prefixes execute no helper stubs. The metadata fixture retains only its explicit security-cookie, allocation and memset shims from E011BH; no new helper stub is added.

## Reproduce

Run on this SP11 only:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bj-rear-aec-reader-width-authority/source-private.py
```

Original DLL/tuning bytes, decompiled C and Ghidra logs remain private on SP11. Own fixture code and semantic results are tracked. Original source hashes are checked before execution.

## Next

Qualify the interface passed to loader0x6F22C8 and persisted into the temporary reader context, then the actual callback target at0x6F4A98 and its reader60:68/profile output. The temporary interface placeholder in this fixture is never dispatched. Complete file-context filename initialization and exact source/profile ownership before joining E011BH helpers into the full parent, accounting for the primary-name allocation. Audit remaining root/grid fields before full aggregate claims.

No full reader-constructor return or complete parent-metadata join is claimed. Historical full-parent metadata skips remain. Exact source/profile, full loader policy, cold metadata, RS authority, deterministic bootstrap, WM16 retirement and optical parity remain open. There were no camera starts/reboots/observer arms/production C changes/kernel builds. Golden and all three protected payloads remain unchanged; native rear runtime remains denied.
