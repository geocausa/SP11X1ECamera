# E011BM original symbol context and AEC metadata join

PASS_BOUNDED_ORIGINAL_SYMBOL_TABLE_CONTEXT_AND_SOURCE_REQUEST_AEC_JOIN. Base commit e97dade62f4a816a9de015b726448845f021a359. Four cases: two SHA-pinned rear files, each at aligned and unaligned placement. Acceptance job job_COu28MDhXXgKL6277ha5Vy5e completed with exit 0.

The original loader and symbol builder now execute all 194,976 symbol reader returns across four cases, returning from builder0x6F4CA8 at0x6F3524. Each original reader return has an exact224-byte object check against serialized ID/name/version/selector/payload fields and original source-backed profile callbacks, plus cursor advancement. IDs, file base/length, object-section offset, manager argument and alignment1 are verified. All resulting reader records point to the original loader's stack context. Context+0 points to source header module name at file+88, +8 matches header32:40, +24 is maximum symbol ID and +40 is the original symbol table. This context is not manager+16.

Four original AEC parent0x123CC0 full returns, eight original metadata constructor returns and eight real name/version rejections pass. Its x0 is a request descriptor: embedded name+16 must match reader+12 and U64 version+60 must match reader+52; x1 is the source-produced reader and x2 alignment1. An owned request is constructed with original metadata0x6F45D8 from source reader fields. Actual factory request selection remains open. Failed exploratory file-context/name-pointer x0 guesses are excluded.

Original name0x6F4AC0, comparison0xF5DF00 and metadata helpers execute. Name allocation/content/termination, source profile copy, header-name copy (64-byte limit), U64 and U32 numeric fields are verified. AEC object installs subclass vtable0x1335598 at original store0x123D88 and copies reader ID+8 to module+56 at0x123DFC. The base constructor's zero field56 is not a final AEC object invariant. Root cursor consumes48 bytes.

Existing qualified revision, four-grid copy spans/nested data, histogram copy spans/nested arrays and BFW/ROI/data spans are checked on the actual produced table. Every reader cursor is checked; all pre-existing allocation bytes outside cursor fields survive. Source maps/padding, original stack context, manager, mode nodes, heap outside owned request and allocation canaries are preserved. This is not an independent proof of every root/grid field.

Earlier zero-filled fixtures' padding and the entire embedded-name tail are not promoted to source policy. Actual unwritten padding may retain the owned allocator pattern. Name bytes and termination remain verified; opaque helper tail and complete padding policy remain open.

Retained shims only: security0x11D0/0x11F0, allocator0xCAE740, memset0xF5E600. The allocator uses a bounded owned32MiB arena, not OEM heap policy. No parser, profile callback, comparison, name, metadata, revision, grid, histogram, BFW, ROI, data or memcpy helper shim is added. No captured scalars are producer inputs. Original bytes, optical data and private traces stay on SP11.

Open: actual factory/caller request policy, context ownership transfer after the complete loader, whole loader return, opened filesystem filename policy, platform extension path, opaque mode wire+16, node strings/containers and remaining root/grid fields. Metadata uses the header module name; it does not establish an opened path. Cold metadata, RS, deterministic bootstrap, WM16 retirement and optical parity remain open.

Golden boot/all3 protected hashes unchanged, camera idle, NTFS unmounted. Zero new camera starts/reboots/observer/production C/kernel builds; native rear runtime denied. Evidence: CONTEXT-JOIN-SAFE.json, GUARD-SAFE.json, RESULT.json, NEXT-SOURCE.json and source-private.py.
