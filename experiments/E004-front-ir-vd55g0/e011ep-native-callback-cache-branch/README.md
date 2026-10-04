# E011EP: native-qualified callback cache and result-one branch

Status: **PASS_NATIVE_QUALIFIED_CALLBACK_CACHE_BRANCH**.

E011EP closes the callback/cache dependency left by E011EO without treating the whole runtime callback table as known. A fresh native front-camera reference after successful initialization and before Start found the required `.fptable` slot at RVA `0x1B60000` already populated. Source analysis identifies that slot as a Windows file-API mode query. External KD inspection confirmed the populated target corresponds to that source-identified callback and showed its return is determined by a process-local comparison. The live FrameServer comparison was equal, so the callback's native return for the qualified reference state is exactly one.

The exact native `0xCB9F68` instruction was **not** trapped and is not claimed as observed. Authority is deliberately narrower: source-qualified slot identity plus native pre-start slot target, native callback implementation semantics, and the live process-local comparison. No other callback-table slots are promoted to native truth.

Using that authority, four retained placements execute unchanged original `0xCB9F68` on its already-populated-slot path, execute the inherited original CFG no-op check, invoke an owned callback provider constrained to the native-qualified return value one, and return with exact nonvolatile state. `0xCFD410` then takes the result-one branch, observes its local byte as zero, selects mode argument `w3=0`, and reaches the next original call at `0xCFD4E4 -> 0xCB76B0`. Each case rejects 124 altered contracts, 496 total. Selected object/output state remains unchanged; the selected logical lock remains held and the index-8 global lock remains released.

Three front-only native Start/Stop references succeeded during the Windows oracle round-trip, with 449, 448 and 43 valid front frame handles. No rear Start occurred. SP11 returned to Golden Linux with persistent boot order and Golden kernel/initrd/DTB hashes unchanged. No kernel build, production-C or PM change was made. Raw process addresses, debugger logs and transport secrets remain private.

NEXT **E011EQ** qualifies original `0xCB76B0` from the exact E011EP arguments and stops at its first unqualified OS/runtime dependency. Front hardware retirement, IRQ, DMA and IOMMU gates remain open. Native rear runtime remains denied.
