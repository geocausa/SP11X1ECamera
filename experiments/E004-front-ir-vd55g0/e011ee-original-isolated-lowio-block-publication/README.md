# E011EE: isolated original low-level I/O block construction and publication

Original 0xCC08E8 constructs and publishes the first low-level I/O block under explicit owned cold/runtime-provider preconditions. This runs on a fresh emulator independent of the E011ED stream initializer and the E011EC camera caller. No states are joined.

The owned entry begins at 0xCC08E8 with a direct-entry return fixture. The actual loader/CRT startup caller and its ordering remain unqualified. The eight-byte table cell at 0x16A2A90 is in writable virtual-zero space; owned initial zero is explicit, and no empty file-data hash is used as native authority. The inherited EnterCriticalSection binding at 0xF7E0B8 is modeled ready. Original 0xCB7300 derives lock index seven/resource 0x16A2FD8; the owned API model preserves NONVOL/SP and applies the inherited OS-void X0 axis.

Original 0xCC05B8 requests [64,72] at 0xCB75E0 -> 0xCC05DC. An owned zeroed allocation provider reserves a fresh aligned, nonalias 4,608-byte lease at heap+0x26000+bias with 32-byte poison redzones. It does not execute or qualify the original allocator body. No formal arguments are claimed for the block constructor: its explicit allocation arguments are produced by original source, independent of the inherited volatile X0 value.

The original loop invokes 0xCBA4B0 sixty-four times with [block+72*k,4000,0] and return 0xCC061C. The inherited InitializeCriticalSectionEx binding at 0xF7E230 points to an explicit owned success provider returning one. Each original wrapper returns with exact NONVOL/SP. Logical resource readiness does not modify or prove native critical-section bytes.

For every 72-byte record, source writes all-ones eight bytes at +40, zero eight bytes at +48, 0x0A0A0000 four bytes at +56, byte ten at +60, byte zero at +61 and five zero bytes at +62..+66. The source byte read at +61 is independently checked against owned zero allocation provenance. Remaining bytes retain zero. The temporary null cleanup invokes original 0xCB1650 -> 0xCC0668, which returns zero. Constructor 0xCC05B8 -> 0xCC093C returns the block pointer, preserving all NONVOL including SP. Original 0xCC093C publishes the pointer with a source-indexed store independently checked as signed-extended index zero shifted three.

Qualification stops before 0xCC0948 reads four bytes at 0x16A2E90. Current SP is lowIO-entrySP-96. The initializer is active, its owned logical lock held, and all nested constructor/resource/cleanup frames returned. Full low-level initializer return, remaining runtime fields, handles/file contents, native allocation/CRT resources, actual loader invocation and joining with the stream/camera contexts remain unqualified.

| Verified item | Per case | 256 cases |
|---|---:|---:|
| Original instruction visits | 2,884 | 738,304 |
| Exact ordered source-store chunks/contracts | 663 | 169,728 |
| Rejected altered owned requests | 4,714 | 1,206,784 |
| Exact dependency reads | 130 | 33,280 |
| Original nested ABI returns / entries | 67 / 67 | 17,152 / 17,152 |
| Owned zeroed allocations | 1 | 256 |
| Owned zeroed allocation bytes | 4,608 | 1,179,648 |
| Owned API calls | 65 | 16,640 |

The seven-axis Cartesian matrix retains the exact 256 E011ED rows. It independently verifies cumulative lowIO entry-to-frontier memory/permissions, redzones and constructor return, then checks both existing contexts' memory/permissions/current PC remain unchanged. Camera original visits remain 1,237,760; aggregate 1,989,120 counts three separate contexts. The lowIO block is not a tenth live camera allocation.

Two added execution pins are exact: 0xCC08E8 / 332 bytes / SHA256 0fd5d934868e2d438d497d94de0922455cf909e3553a24833a1f8cf659c7893b, and 0xCC05B8 / 204 bytes / SHA256 2e8f62889f5850eb5275da5b71bc43cf777b62913547526e8c8c2b5ab5b53b87. The inherited 46 pins remain exact. Source instructions, decompilation, original names, bytes and optical material stay private on SP11.

The source-store observer models pending pieces of a paired store before Unicorn applies them. It requires each pending piece's old physical bytes to remain exact and checks actual writes through the inherited pending-store hook. This permits no memory reset. Indexed publication additionally checks source index zero and signed extension/shift geometry. Exploratory probes are excluded from accepted results.

Run the portable review with `python3 verify.py --selfcheck`; it needs authored source/evidence, not original binaries. Execute `source-private.py` only on SP11 with the inherited private original present. NEXT E011EF establishes the 0x16A2E90 runtime input before any read or continuation. Golden, historical repositories, camera fallback paths and native rear runtime denial are preserved.
