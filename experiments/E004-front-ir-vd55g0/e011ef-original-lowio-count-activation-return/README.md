# E011EF: original low-level I/O count transition, first-record activation and initializer return

The isolated original low-level I/O initializer now continues from the accepted E011EE frontier through its four-byte runtime count under explicit cold zero-fill authority. Original source reads zero at 0x16A2E90, adds 64, writes 64 back, derives record zero through original wrapper 0xCC07B0, enters its owned logical critical-section model, sets the record active byte at +56 to one, releases the initializer's owned index-seven lock through original wrapper 0xCB7398, and returns zero with exact NONVOL/SP.

The continuation is source effects under declared owned models. It qualifies neither native runtime selection for the count nor native critical-section bytes/handles. The first record's logical lock remains held at the return boundary; the initializer's global index-seven lock is released. Record zero's four-byte field at +56 advances from 0x0A0A0000 to 0x0A0A0001; records one through 63 retain the accepted E011EE layout.

| Verified item | Per case | 256 cases |
|---|---:|---:|
| Added original instruction visits | 37 | 9,472 |
| Exact source stores | 2 | 512 |
| Rejected altered owned requests | 55 | 14,080 |
| Exact dependency reads | 5 | 1,280 |
| Original wrapper entries | 2 | 512 |
| Owned OS API calls | 2 | 512 |
| Exact lowIO initializer ABI returns | 1 | 256 |

All 256 complete E011EE rows remain byte-for-byte equal as ancestors. The lowIO continuation memory/permissions and retained redzones match without resets. The separate stream initializer and camera caller remain unchanged; aggregate original visits are 1,998,592 across separate contexts, while the camera-chain count remains 1,237,760.

This closes the isolated lowIO initializer's cold path and return only. Actual loader/CRT startup caller ownership and ordering remain unqualified, so no state is copied into the stream initializer. The stream initializer remains before 0xCB3338 reading 0x16A2A90 at stream-entrySP-80, and the camera remains before 0xCC6120 reading 0x16A2A58 at outer-entrySP-1648.

NEXT **E011EG** establishes source-qualified startup ordering and permits a lowIO-to-stream handoff only if the original loader/CRT path supports it. Full stream initialization, camera-state joining, native allocator/CRT resources, file/provenance collection, full helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero new camera Starts, reboots, kernel builds, production-C or PM changes. Golden payloads, EFI/GRUB and historical repositories remain preserved. Original binaries, instructions, decompilation, raw records, proprietary names and optical material remain private on SP11.
