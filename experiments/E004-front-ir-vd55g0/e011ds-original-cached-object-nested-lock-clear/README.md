# E011DS: original cached object, nested lock and 11,808-byte buffer clear

The unchanged first helper now caches its own inline object pointer, acquires a separate registry lock through the original default callback, initializes bounded header fields and executes the original 11,808-byte clear. It stops before the actual factory call. No cache, nested-lock or clear result fixture replaces original execution.

| Derived authority | Qualified result |
| --- | --- |
| Cache store 0x5B8138 -> 0x1731880 | Actual inline object pointer 0x17A4230 |
| Nested lock object / resource | 0x1623598 / 0x16235A0; distinct from the outer registry |
| Original CFG / callback | Returns 0x5B8160 / 0x5B8164 |
| Header source effects | Eight additional chunks including the cache; scalar 32769 and declared zero fields |
| Original memset 0xF5E600 | Destination 0x17A4268, length 11808, actual return 0x5B8250 |
| Actual next call | Stop BEFORE 0x5B8268 -> 0x5BDE08, actual return 0x5B826C |

512 cases repeat the eight-axis E011DR matrix. Total source coverage is 666,624 visits: 321,536 inherited E011DR visits and 345,088 added visits. Added clear coverage is 301,568 visits, a subset of the added total. All 512 nested callback, 512 CFG and 512 large-clear return checks pass. The original constructed container at 0x17A7088 remains intact immediately after the cleared range.

The buffer begins poisoned with A5 or 5A. Source clears every byte and preserves the adjacent four-byte header padding canary, constructed container, allocations, immutable source/unmodified loader regions and actual memory permissions. The source performs 756,736 large-clear chunks; these include deliberate overlapping zero stores and are counted separately from 66,560 other nonstack chunks and 49,152 stack chunks. All 86,528 altered owned contracts reject before effects: 62,976 inherited and 23,552 added.

Code-body pins retain E011DR's 20 exact function bodies, including the 308-byte disjoint memset body. This longer clear also reads one dispatch-data byte at 0xF5E64C. A separate immutable 428-byte code-plus-literal window pins that data, reusing the E011DH window hash; it does not widen executable-body authority. The harness handles original 8-byte and 16-byte vector arrangements and excludes post-index address operands from the stored vector list. Exploratory operand handling was corrected before full qualification; no original instruction was changed.

OS/loader/CRT readiness, cold zero control cells, a disabled trace flag and fresh storage remain explicit owned models. Buffer and padding poison are robustness fixtures. Both initial global epochs are declared test inputs; the positive-epoch edge cases do not prove native cold initialization of the next factory guard. Native OS/CRT initialization, allocator failures, existing-table growth, cleanup execution/teardown, concurrency and full inline-object initialization remain unqualified.

At the boundary, outer and nested registry locks remain held; CRT and SRW locks are released. Parent/helper have not returned and the factory callee has not executed in this parent. The observed pre-call X0 retains the cleared buffer address; this is a register observation, not a claim about the factory's required arguments. E011DH/DI remain separate factory/enumeration proofs. E011DM remains the original empty RS-query proof.

Run python3 experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/verify.py --selfcheck for matrix, source-lock and scope review. source-private.py reruns only bounded emulation on SP11. Original binaries, instruction text, decompilation, raw records and optical material stay private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or power-policy changes occurred. Golden boot/payloads, permanent EFI/GRUB and historical repositories remain unchanged. E011DT integrates the actual factory callee with this live parent and its owned allocations, locks and published TLS epoch. Full descriptor registry initialization, selected profile/input deterministic bootstrap and independent exact-buffer/generation IRQ/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.
