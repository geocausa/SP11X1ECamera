# E011DU: original second callback registration and enumeration guard publication

The original enumeration cleanup registration now runs against the actual one-entry encoded exit table produced by the retained parent. Source appends callback 0xF7B5E0, preserves the first callback 0xF7B120 and uses the existing 32-slot allocation. Original enumeration publication then advances the global and actual thread epoch to 80000042. No registration, table, callback or publication result fixture replaces this execution.

| Derived authority | Qualified result |
| --- | --- |
| Actual enumeration call 0x5F94A0 -> 0xCA34A0 | Return 0x5F94A4; callback 0xF7B5E0 |
| Existing encoded table at 0x16A2760 | Used entries 1 -> 2; capacity stays 32 |
| Existing allocation | Same 256-byte lease; no allocation, clear or reallocation leaf |
| Original publication 0xCE7A48 | Actual return 0x5F94AC; guard at 0x1B30320 |
| Published enumeration / global / TLS epoch | 80000042, produced by original source |
| Retained first-helper guard at 0x17A4220 | 80000041 |
| Factory guard at 0x1B302D0 | FFFFFFFF in-progress |
| Boundary | Stop BEFORE 0x5F8E24, a four-byte read from 0x1731598 |

256 cases retain the seven E011DT axes: four stack/allocation biases, two loader indices, two initial thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two poison patterns. Every complete inherited E011DT row equals its accepted row for the same axes. Signed-negative initial global epoch 80000040 remains selected; the first helper actually publishes 80000041 before this new enumeration publication.

Added coverage is 45,056 original visits, 9,472 exact source store chunks, 1,792 nonstack field chunks and 27,392 rejected owned requests. The 2,048 original callee return checks cover eight registration/publication frames per case; the five owned OS leaves contribute 1,280 calls and 256 wakes. These counts exclude inherited coverage: 127,744 E011DT visits plus 333,312 E011DS visits. Combined original coverage is 506,112 visits. There are no new allocator leaves.

A single original entry-to-frontier memory and permissions snapshot spans all three stages. The continuation does not reset the parent, registers, TLS, table or allocation leases. Every executed instruction matches the 23 inherited exact body pins. Each of the seven nonstack chunks matches an independently authored source-site/address/width/value and order contract. The second registration legitimately rewrites table fields and the global/TLS epoch that were written earlier; its separately declared phase effects update the same cumulative memory model.

Actual SP, X19..X29 and D8..D15 are restored at each of the eight callee returns. Declared integer return values are checked where applicable. CRT entry/release and SRW acquisition/release/wake use exact resources, actual return addresses, readiness and held-state contracts. Altered arguments, returns, ownership, table pointers/callbacks/capacity, epoch cells, cookie, loader pointers and node relations reject without advancing the retained model. Both registry locks remain held; CRT and SRW locks are released at the new boundary.

The original 24-byte head, 128-byte array, 256-byte encoded table and two 48-byte factory nodes remain disjoint and live. Source bodies, immutable loader regions, all redzones, the constructed container, the earlier 11,808-byte clear, factory fields, 56-byte enumeration record and actual TLS remain exact. The first callback and all 30 unused slots remain unchanged.

OS/CRT/loader readiness, existing allocator construction and committed stack bounds remain explicit owned models inherited from E011DT. Native construction, concurrency, failures, exceptions, callback teardown and stack guard-page growth are unqualified. The enumeration guard's publication proves this initialization stage; enumeration, factory and first helper have not returned. Full descriptor registry initialization, selected profile/input deterministic startup, populated RS lifetime and normal AFD authority remain open.

Run python3 experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/verify.py --selfcheck for matrix, exact ancestor row equality, locks and scope review. source-private.py reruns bounded original emulation on SP11. Original binaries/instruction text/decompilation/raw records and optical material remain private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or PM changes occurred. Golden boot/payloads, EFI/GRUB and historical repositories remain unchanged. NEXT E011DV qualifies the four-byte enumeration dependency at 0x1731598 and its subsequent original branch under the retained two-entry table and updated epoch. Independent exact-buffer/generation IRQ/DMA/IOMMU retirement still precedes clean-colour front/rear/off acceptance. Native rear runtime remains denied.
