# E011BI — original reader initializer and ID/name prefix

Bounded pass on SP11 in Golden Linux. This stage qualifies the reader's initial state and typed ID/name loading; the complete constructor, numeric metadata, profile and filename ownership remain open.

The original initializer at RVA 0x6F4790 returns at four placements. It zeros only reader byte ranges 0:8, 52:68 and 208:224. Every other heap byte remains unchanged. The table builder 0x6F4CA8 calls constructor 0x6F47B8 at 0x6F4E84. Its reference to the initializer is not asserted as a direct call.

The original constructor prefix stops at 0x6F4870. It loads the symbol ID into reader+8, executes original memcpy at 0x6F4864 to copy 32 bytes from serialized record+4 to reader+12, and writes a terminator at reader+44. It zeros reader+208 and preserves the supplied file-context pointer. This boundary precedes later cursor updates and numeric/profile work.

60 prefix cases pass: 12 typed AEC root records from three SHA-pinned candidates across four placements, plus 48 owned variants covering ASCII name lengths 0/1/14/31/32, case, IDs 0/U32_MAX and source offsets 0/1/7/31. ID patterns are propagation tests, not symbol-selection policy. Nine malformed fixture inputs are rejected before execution. Complete heap comparison verifies every byte outside the qualified fields; source records, cursor, context and allocation guards remain intact. No helper is stubbed or allocated in these prefixes.

The prefix establishes x1 as source base, x2 as available source bytes, x3 as a pointer to a byte offset. Explicit x6=1 is this fixture's packed scope; its full constructor caller policy remains unqualified. The 32-byte name slot is distinct from the metadata module's 40-byte name-helper output proven in E011BH.

Later source includes parser-interface dispatch 0x6F4A98, reached through two loads at 0x6F4A7C/0x6F4A84. Its correct source interface and loaded target are not qualified. Exploratory incomplete fixtures used guessed interfaces or arguments and failed; they are excluded from results and are not evidence of an OEM fault. The complete constructor must not be treated as returned, and historical full-parent metadata skips remain.

## Reproduce

Run on this SP11 only:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bi-rear-aec-reader-context-prefix/source-private.py
```

Own code and semantic evidence are tracked. Original DLL/tuning bytes, decompiled C and Ghidra logs remain private on SP11. The private reader decomp covers 0x6F4790, 0x6F47B8, 0x6F4C30 and 0x6F4CA8; caller navigation joins the table builder to the constructor. Original files are hash pinned before execution.

## Next boundary

Derive the actual parser-interface construction and callback target from the loader's temporary context, including ARM64EC/guard dispatch semantics. Then qualify the complete reader constructor's numeric/profile fields and file-context filename initialization with owned records. Integrate E011BH metadata helpers only after that source authority is sufficient, accounting for the extra name allocation; audit remaining root/grid fields before claiming full aggregate parity.

Exact selected filename/profile, full loader policy, cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remain open. Native rear runtime remains denied. There were no camera starts, reboots, production C changes or kernel builds; Golden and its protected payloads remain unchanged.
