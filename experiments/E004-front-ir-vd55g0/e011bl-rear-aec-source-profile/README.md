# E011BL original loader and source profile records

PASS_BOUNDED_ORIGINAL_LOADER_SOURCE_PROFILE_AND_ACTUAL_READER_CALLER. Base commit 7922b28b35df8166028edb760497699bd226569f. Job job_DJrLzyl695iEUZjiD0XTvSkx completed with exit 0 and empty stderr.

The original loader at RVA 0x6F22C8 executes its header/checksum and complete mode loops through 0x6F3520. X1 is file base and X2 is byte length. Two SHA-pinned rear files, each at aligned and unaligned placement, produce four prefixes and 3,604 verified mode records: 1,309 default and 493 rear-specific per placement. This corrects the earlier speculative X2 interface argument; failures from that argument are excluded.

Source mode records have stride 20 and runtime nodes stride 160. Runtime indexing follows serialized IDs, not file order. Source bytes0:12 match runtime bytes0:12 at ID*160. Source parent ID+12 selects runtime parent pointer+24, with null for self or sentinel. IDs are unique and complete; parent bounds and cycles are checked before emulation. Wire+16 is opaque, not assumed sentinel. Strings and child containers are not independently validated.

The original constructor, callback and decimal formatter execute. Fifty-six callback returns check source-selected numeric bytes and ancestor-first profile text, including invalid indices and exact numeric/profile memory guards. Four preserved loader states continue into the original table builder 0x6F4CA8 and actual reader call 0x6F4E84, returning at 0x6F4E88 with alignment 1. The first serialized symbol has invalid selector 0xFFFFFFFF: these four reader returns validate zero numeric/empty profile behavior, not valid AEC profile selection. Standalone callbacks cover valid source profiles.

Manager+16 points to the source header module name at file+88; this is not authority for an opened filesystem filename. Manager1104:1112 matches source header32:40. Manager24:32 policy remains open. The actual reader context does not equal manager+16 after the first return or at the next reader boundary. Exploratory manually supplied contexts failed checks and are excluded; the next checkpoint must obtain the actual AEC context via its original caller.

Source maps/padding, heap and allocation canaries pass. Retained fixture shims are security helpers 0x11D0/0x11F0, allocator 0xCAE740 and memset 0xF5E600. The allocator uses a bounded owned 32 MiB arena; this is not proof of OEM heap policy. No parser, callback or formatter shim is installed. Captured scalars are not producer inputs; original DLL/tuning/decompilation bytes stay private on SP11.

Scope excludes a complete loader return, complete symbol table, platform extension path, all node strings/containers, full parent metadata and opened filename policy. Golden boot and all three protected payload hashes are unchanged. No camera start, reboot, observer, production C or kernel build. Native rear runtime remains denied; cold metadata, RS, deterministic bootstrap, WM16 retirement and Linux optical parity remain open.

Evidence: SOURCE-PROFILE-SAFE.json, GUARD-SAFE.json, RESULT.json and NEXT-SOURCE.json. source-private.py runs locally on SP11 against private originals.
