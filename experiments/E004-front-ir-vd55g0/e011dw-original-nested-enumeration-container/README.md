# E011DW: original nested enumeration-container construction

The original callee at 0x600368 now runs in the retained enumeration caller. It creates a fresh 16-byte object, executes the original nested constructor at 0x5E81B8 and attaches the returned 64-byte header to that object. The nested constructor creates and clears an 8,192-byte array; the outer callee then clears a 640-byte stack buffer. No constructed-record, clear or return result fixture replaces original execution.

| Derived authority | Qualified result |
| --- | --- |
| Actual outer call 0x5F8EA4 -> 0x600368 | Entry X0 is the published 18,832-byte buffer; return 0x5F8EA8 remains pending |
| Fresh 16 / 64 / 8192-byte allocation requests | Exact returns 0x600398 / 0x5E81D8 / 0x5E8244 |
| Nested constructor 0x5E81B8 | Exact 540-byte body; actual return 0x6003CC preserves ABI and returns the heap header in X0 |
| Original 8192-byte clear | Fresh array, fill zero; actual return 0x5E8258 |
| Original 640-byte clear | Actual stack destination at outer-entry SP minus 1392; return 0x6003F0 |
| Constructed relation | 16-byte object's second pointer owns the header, whose array pointer identifies 1024 zero QWORD slots |
| Boundary | Stop BEFORE 0x600420, next eight-byte read from 0x10F03A0 |

The 64-byte header has uint32 fields 1024 and 3F800000 at offsets 0 and 4. Its QWORD fields at offsets 8/16/24/32/40/48/56 are 4/0/array/4/8/12/0. These are qualified typed initialization fields; their complete later runtime meaning and populated-entry lifetime remain open. The 16-byte object stores original image pointer 0x133A100 and the constructed header pointer. No vtable dispatch or teardown is qualified here.

256 cases retain the seven E011DV axes: four stack/allocation biases, two loader indices, two initial thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two poison patterns. Every complete inherited E011DV row equals its accepted row for the same axes.

Added coverage is 151,552 original visits, including 122,624 original clear visits. The array clear contributes 262,144 chunks and the stack clear 20,480; 5,376 structural field chunks and 5,632 ordinary stack chunks give 293,632 exact added source stores. All 256 nested constructor returns, 256 array-clear returns and 256 stack-clear returns preserve SP, X19..X29 and D8..D15, with their exact X0 results. All 26,624 altered owned requests reject. The 768 fresh storage leases total 2,117,632 bytes. There are no added OS leaf calls. Clear counts are subsets of added coverage.

Inherited visits stay separate: E011DV 237,568, E011DU 45,056, E011DT 127,744 and E011DS 333,312. Combined original coverage is 895,232 visits. One original entry-to-frontier memory and permissions snapshot spans all stages; the continuation does not reset parent registers, epochs, callback table, allocations or expected memory.

All three new leases begin poisoned, have 32-byte redzones on each side and remain disjoint from the six older leases. Each nonstack structural chunk has an independently authored source-site/address/width/value and order contract, including intermediate zero writes later replaced by initialization fields. Heap-clear stores remain within the live 8192-byte lease and contain only zero. Stack-clear stores remain within the actual 640-byte destination and contain only zero. The five header reads have exact source-site/address/width/value contracts and reject altered requests before advancement.

Final whole memory and mapping permissions match the cumulative model. The published 18,832-byte buffer remains fully zero and retains reference count one; the two-entry/32-slot callback table, epochs, earlier nodes, container, clears and all redzones remain unchanged. Both registry locks remain held; CRT/SRW remain released. Nine allocations are live at the new frontier.

The new 1120-byte outer and 540-byte nested body pins extend the inherited 23 pins to 25. Each executed original instruction matches its exact original bytes. The original outer call remains active; its return 0x5F8EA8 has not been reached. Incoming scratch register values are retained from the caller rather than fabricated as semantic constructor inputs.

Loader zero-fill/scalar selection, allocator success/storage, OS/CRT/loader readiness and committed stack bounds remain explicit inherited owned models. Native allocation, failures, exceptions, concurrency, virtual dispatch, teardown and stack guard-page growth remain unqualified. The next constant-data read, file/provenance collection, complete enumeration/factory/helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS lifetime and normal AFD authority remain open.

Run python3 experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/verify.py --selfcheck for matrix, exact ancestor equality, pins and scope review. source-private.py reruns bounded original emulation on SP11. Original binaries/instruction text/decompilation/raw records, proprietary names and optical material remain private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or PM changes occurred. Golden boot/payloads, EFI/GRUB and historical repositories remain unchanged. NEXT E011DX derives bounded immutable authority for the constant-data read at 0x10F03A0 and resumes this actual callee. Independent exact-buffer/generation IRQ/DMA/IOMMU retirement still precedes clean-colour front/rear/off acceptance. Native rear runtime remains denied.
