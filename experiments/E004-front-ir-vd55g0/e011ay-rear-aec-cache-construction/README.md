# E011AY — named AEC hardware-stats module and grid weight reader

Offline authority now reaches the named `aecxhwstatsconfig` module rather than an untyped cache pointer. The original grid scalar reader copies 12 serialized weight bytes unchanged into the runtime grid record, and the three installed Default candidates agree with the private E011AX cache. Parent deserialization and actual live source selection remain open; this stage does not close initialization policy or authorize native rear ISP.

| Source boundary | Verified fact |
| --- | --- |
| ConfigureHWStats 0x39F070 | Owner+0x670 supplies public interface; method+0x138 returns data; data+0xF0 selects module; module payload+0x38 supplies grid cache |
| Constructor 0x3A8BE0 | Public method+0x138 installs 0x3A8730; concrete bank table 0x13383B8 replaces the initial base table at 0x3A9430 |
| Public wrapper 0x3A8730 | interface+0 -> core; core vtable+0x138 -> 0x3AF540 |
| Core accessor 0x3AF540 | **Pre-indexed** load advances this by 8; bank subobject vtable+0x68 -> 0x3AEBB0 |
| Bank accessor 0x3AEBB0 | Returns bank+0xEF8, equivalently core+0xF00 |
| Named module lookup 0x3CA4A0 | `aecxhwstatsconfig` becomes bank+0xFE8, equivalently core+0xFF0; returned module pointer is adjusted by 0x120 |
| Grid reader 0x123550 | First native memcpy at 0x123814 copies wire+0x14 to grid+0x14, 12 bytes |

The bank/core offset distinction matters. The original core accessor uses writeback on its +8 load. Using core+0xEF8 or core+0xFE8 would select the wrong locations. The owned fixture executes all three original accessors and both actual ConfigureHWStats pointer-load instructions, so it checks this adjustment mechanically.

`source-private.py` passes 128 cases across four base placements. Each runs the complete original named lookup with a semantic lookup stub for all 43 modules (5,504 calls total), then the original accessor chain with only the ARM64EC checked-dispatch helper stubbed. Actual virtual accessors are executed. Heap source and neighboring bytes are unchanged through the accessor/load path. This does not execute the complete constructor or ConfigureHWStats, choose a real profile, or qualify the corresponding live interface.

The SHA-pinned installed files each contain one aecxhwstatsconfig v10.0 Default root of 48 bytes. At wire+24/+28 they contain candidate count4 and a symbol reference to a gridStatsConfig record of 404 bytes. These parent fields are still a candidate relation until the original parent reader/array materialization is qualified; scanning other integer words for coincidental symbol IDs is excluded as schema authority.

`scalar-private.py` runs the original grid reader and native memcpy through the immediate post-copy boundary 0x123818. It passes 137 distinct scalar cases at four placements, plus one private comparison: 549 original prefix executions. Cases include the three independent installed sources and synthetic bit patterns/random mutations, with no captured producer inputs. All 12 output bytes match wire+20; source and checked neighbor bytes are preserved. The three candidate Default arrays agree and match the E011AX weights across 12 bytes. No numeric triple is embedded in the source or promoted to policy.

The prefix excludes post-copy ARM64EC array bookkeeping and the aggregate tail. An exploratory attempt beyond the prefix reached a BRK at 0x123820; that incomplete fixture is not evidence of an original-driver defect. Parent reader0x123CC0, its payload+0x38 pointer store0x123FA4 and first grid-reader call0x124034 are the concrete next boundaries. Full allocation/count/stride, symbol resolution, profile choice and live source/cache join remain unqualified.

Earlier pointer-offset search candidates did not establish this producer: 0x394E60 is the AEScan reset/test path; 0x39ECF0 is BackupFlashStats; 0x3C0E20 is cleanup, not a demonstrated numeric initializer. Their offset coincidences are not promoted to cache authority.

Golden remains boot f627e38e-19d3-480a-900d-73116d63b4df on 7.1.5-sp11-render-parity-v4+, saved FullIOv19c, empty next_entry, all three protected hashes unchanged, NTFS unmounted and camera idle. No new camera Start, reboot, production C, kernel build, MMIO, observer arming or Linux runtime occurred. E011AX-20261001-0055A remains consumed. Raw tuning, original binaries, decompilation and optical records stay private on this same SP11.

Next follow NEXT-SOURCE.json. After parent/source selection, retain the separate cold metadata bridge, RS count/offset, full deterministic startup, WM16 same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement and Linux optical parity gates. Native rear runtime remains **DENIED**.
