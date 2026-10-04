# E011DT: original factory and enumeration bootstrap in the actual cold helper

The factory now executes in the retained parent VM reached through the actual call 0x5B8268. It uses the TLS epoch published by the preceding helper, constructs two fresh sentinel nodes, clears its original globals and stack record, then enters enumeration bootstrap. No factory, guard, node-construction, probe or clear result fixture substitutes for original execution.

| Derived authority | Qualified result |
| --- | --- |
| Parent call 0x5B8268 -> 0x5BDE08 | Actual parent return address 0x5B826C; parent remains active |
| Factory body | Exact 4004-byte body, 0x5BDE08..0x5BEDAB |
| Factory / enumeration guards | 0x1B302D0 / 0x1B30320; both claimed FFFFFFFF in-progress |
| Fresh node allocation returns | 0x5BE69C / 0x5BE6D0; 48 bytes each, disjoint from ancestor allocations |
| Factory initialization | 190 zero-field chunks and two self-linked nodes, uint16 field 257 |
| Original stack clear | 1040 bytes at actual factory-entry SP minus 1144; return 0x5BE9FC |
| Enumeration / stack probe | Exact 1776-byte enumeration body; actual 5920-byte committed-stack request |
| Boundary | Stop BEFORE 0x5F94A0 -> 0xCA34A0, callback 0xF7B5E0, return 0x5F94A4 |

256 cases cover four stack/node placements, two loader indices, two initial thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two poison patterns. They select the signed-negative global epoch 80000040, actually published as 80000041 by the parent helper. The positive-epoch edge cases in E011DS are excluded from this cold-factory proof.

Added coverage is 127,744 original visits, 102,656 exact store chunks and 15,104 rejected owned requests. Inherited E011DS coverage contributes 333,312 original visits and 43,264 rejected contracts across these 256 cases. Combined original coverage is 461,056 visits; counts are separated by stage. The 29,952 factory-clear visits and 33,280 clear chunks are subsets of added coverage. All 512 guard, 256 stack-probe and 256 clear return ABI checks pass.

The same entry-to-frontier memory/permissions snapshot spans both stages. No new parent snapshot or input register fixture resets the caller. Initial readiness/poison fixtures are prepared before the parent begins. Every instruction matches its pinned original bytes, and every nonstack write matches an independently declared source-site/address/width/value contract. The native nodes begin poisoned; original source produces their links, 257 field and zero tail. Source also clears 190 poisoned image fields and the enumeration's 56-byte static record.

Both outer and nested registry locks stay held. The four new SRW leaf operations balance acquisition/release without replacing the original guard bodies. Existing 24-byte sentinel, 128-byte array and 256-byte encoded exit-table storage remain live, unchanged and separate from the two new 48-byte nodes. Source, actual loader/TLS epoch, array redzones, constructed container, prior cleared buffer and mappings remain exact. The exit table still contains only the first callback in 32 slots.

The original probe runs under explicit already-committed stack bounds; OS guard-page growth is unqualified. Fresh allocator storage, OS/loader/CRT readiness, native resource construction, failure/exception cleanup, concurrency and teardown remain owned assumptions or open gates. Poisoning is a robustness fixture. The memset code body remains the inherited exact 308-byte disjoint authority; its additional dispatch-data read at 0xF5E644 is checked against the separate immutable 428-byte code-plus-literal window.

The factory and enumeration have not returned or published their guards. Full helper/descriptor registry initialization, selected profile/input, populated RS lifetime, normal AFD authority and deterministic startup remain open. E011DI is retained as the separate bootstrap proof; E011DT qualifies its use in this actual parent with the updated epoch and non-aliasing leases. E011DM remains the original empty RS-query proof.

Run python3 experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/verify.py --selfcheck for matrix, ancestor row equality, locks and scope review. source-private.py reruns bounded emulation on SP11. Original binaries/instruction text/decompilation/raw records and optical material stay private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or PM changes occurred. Golden payloads/boot, permanent EFI/GRUB and historical repositories remain unchanged. Next E011DU executes the new callback registration against the already populated encoded table, then enumeration guard publication and the next dependency. Independent exact-buffer/generation IRQ/DMA/IOMMU retirement still precedes clean-colour front/rear/off acceptance. Native rear runtime remains denied.
