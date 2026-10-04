# E011DQ: original cold container construction

The unchanged first-helper constructor now completes its normal path and returns to its actual caller, preserving ABI and returning the container pointer. It obtains declared fresh storage from an explicit owned allocator model; original instructions construct the object, sentinel and pointer array. No constructed-object, constructor, helper or guard result fixture replaces this execution.

| Derived authority | Qualified result |
| --- | --- |
| Constructor 0x2EE1A0, exact 260-byte body | 103 original visits per case; actual return 0x5B9094 |
| Object at 0x17A7088 | 64-byte container; original input scalar 65535 |
| Allocation return 0x2EE1D0 | 24-byte sentinel: two self pointers and a zero field |
| Allocation return 0x2EE218 | 128-byte array: all 16 pointer entries refer to the sentinel |
| Object scalar fields | Empty count, load-factor bits 3F800000, mask 7 and bucket count 8 |
| Registration wrapper 0xCA34A0 | Only four original prefix visits; stop BEFORE 0xCA3450 |
| Next dependency | Actual return 0xCA34B0, callback argument 0xF7B120 |

256 cases vary four stack/allocation placements, two loader indices, two signed-negative thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two allocation poison patterns. The fresh storage is poisoned before execution; allocator adapters return only the declared pointer and do not construct object bytes.

All 65,280 original visits pass, including 26,368 constructor visits and 1,024 registration-wrapper prefix visits. These are subsets, not extra totals. Owned allocator calls (512), OS calls (768) and diagnostics calls (256) are excluded from original counts. Exact source effects are 12,288 stack-store chunks and 13,056 nonstack chunks. All 17,664 altered owned contracts reject before effects, including incorrect allocation size/return/provenance, corrupt fresh storage and already-live reservations.

Every executed instruction matches the immutable hash-pinned private image. Whole mapped memory and actual permissions match the entry snapshot with only declared source effects. Source, loader objects and allocation redzones stay unchanged. Original vector stores are checked as their actual eight-byte memory-hook chunks. The complete constructor restores SP, X19..X29 and D8..D15 at 0x5B9094; the inherited lock callback and guard return checks also pass.

The successful constructor leaves two live owned allocations related to this container. This proves bounded construction ownership under the declared allocator model. Native allocation, failure/exception cleanup, deallocation, teardown and concurrent access remain unqualified. The early exploratory harness had incorrect vector chunk address handling; it was corrected before the accepted 256-case qualification, and no original instruction was changed.

At the boundary, parent/helper/registration-wrapper frames remain active, registry logical lock held, SRW released and helper guard FFFFFFFF in-progress. Cleanup registration has not executed, helper guard has not published and full helper return/full metadata descriptor initialization are not qualified. E011DI remains separate factory/enumeration acceptance; E011DM remains the latest original RS-query proof.

Run python3 experiments/E004-front-ir-vd55g0/e011dq-original-cold-container-construction/verify.py --selfcheck for matrix, evidence locks and scope review. source-private.py reruns only bounded Unicorn emulation on SP11. OEM binaries, original instruction text, decompilation, raw records and optical material remain private on SP11.

No camera Start, reboot, kernel build, production camera C change or power-policy change occurred. Golden boot, payloads, permanent EFI/GRUB and historical repositories remain unchanged. Next E011DR qualifies cleanup registration and original guard publication, then follows first-helper closure. Selected input/profile deterministic startup and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.
