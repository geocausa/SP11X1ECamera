# E011DV: original cold enumeration buffer allocation and publication

The original enumeration cold branch now executes from its actual retained caller. Under the declared loader zero-fill scalar model it requests fresh 18,832-byte storage, clears the entire allocation through the unchanged original memset body, publishes its pointer and writes reference count one. No allocation-clear, pointer or reference-count result fixture replaces original execution.

| Derived authority | Qualified result |
| --- | --- |
| Scalar read 0x5F8E24 -> 0x1731598 | Four-byte virtual zero-fill cell, retained zero under the loader model |
| Actual allocation call 0x5F8E34 -> 0xCAE740 | Request 18,832 bytes; actual return 0x5F8E38 |
| Actual clear call 0x5F8E50 -> 0xF5E600 | Fresh buffer, fill zero, count 18,832; return 0x5F8E54 |
| Pointer publication at 0x5F8E58 | 0x169FDF0 receives the actual owned buffer |
| Reference count publication at 0x5F8E5C | 0x169FDE8 receives one |
| Boundary | Stop BEFORE 0x5F8EA4 -> 0x600368, actual return 0x5F8EA8 |
| Next callee metadata only | Exact 1120-byte body, 0x600368..0x6007C7; not executed in this acceptance |

256 cases retain the seven E011DU axes: four stack/allocation biases, two loader indices, two initial thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two poison patterns. Each complete inherited E011DU row equals its accepted row for the same axes. The enumeration/global/TLS epoch stays 80000042, the first-helper guard stays 80000041 and the factory guard stays FFFFFFFF in-progress.

Added coverage is 237,568 original visits, including 233,472 original clear visits. The clear contributes 602,624 store chunks; the two publication fields contribute 512 more, giving 603,136 exact added source store chunks. All 256 clear callee ABI returns pass, and 11,008 altered owned requests reject. The 256 fresh storage leases total 4,820,992 bytes. There are no added OS leaf calls. Clear visits are a subset of added visits and clear chunks are a subset of added stores.

Inherited coverage stays separate: E011DU 45,056 visits, E011DT 127,744 and E011DS 333,312. Combined original coverage is 743,680 visits. A single original entry-to-frontier memory and permissions snapshot spans all stages; the continuation does not reset parent registers, epochs, callback table, allocations or expected memory.

The new 18,832-byte lease begins fully poisoned and has 32-byte redzones on both sides. Its placement remains disjoint from the original 24-byte head, 128-byte array, 256-byte encoded exit table and two 48-byte factory nodes. Every original clear store is required to remain within the live new allocation, contain only zero and occur inside the actual clear callee. The two subsequent field stores have independently authored source-site/address/width/value and order contracts. SP, X19..X29 and D8..D15 are checked at the real clear return, with X0 equal to the original buffer. Final whole memory and permissions match the cumulative effect model, including all redzones, immutable source and loader regions, earlier clears and constructed objects.

The scalar at 0x1731598 lies beyond the section's file-backed raw span and inside its declared virtual size. It has no four-byte file payload to hash. Its zero is an explicit virtual loader zero-fill/readiness model, checked before the original parent begins and at the actual read. Its nonzero branch and native runtime selection remain unqualified. The pointer and reference-count cells begin at their original file-backed zero values; source writes the new results. Fresh allocator success/storage, OS/CRT/loader readiness and committed stack bounds remain owned models. Native allocation, failures, exceptions, concurrency and teardown remain open.

The 23 inherited exact original body pins are unchanged. The clear's one-byte dispatch read at 0xF5E644 matches the immutable inherited 428-byte code-plus-literal authority. BOUNDARY-AUTHORITY-SAFE.json separately pins the original allocation/clear/next call targets and read-only next-function metadata; next-function metadata is not execution proof.

Both registry locks stay held; CRT/SRW stay released. The actual two-entry, 32-slot encoded callback table remains unchanged, including callbacks 0xF7B120 and 0xF7B5E0 and all unused slots. Earlier epochs, five allocations, nodes, redzones, container and static records stay retained. Enumeration, factory and first helper have not returned. File/provenance collection, full descriptor registry initialization, selected profile/input deterministic startup, populated RS lifetime and normal AFD authority remain open.

Run python3 experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/verify.py --selfcheck for matrix, exact ancestor equality, locks and scope review. source-private.py reruns bounded original emulation on SP11. Original binaries/instruction text/decompilation/raw records and optical material stay private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or PM changes occurred. Golden boot/payloads, EFI/GRUB and historical repositories remain unchanged. NEXT E011DW integrates the original 0x600368 callee with this caller and retained six live allocations. Independent exact-buffer/generation IRQ/DMA/IOMMU retirement still precedes clean-colour front/rear/off acceptance. Native rear runtime remains denied.
