# E011AZ — original AEC parent-to-first-grid weight materialization

The bounded original parent reader now resolves the typed grid symbol, allocates the grid array and populates its first weight array from independent tuning bytes. This closes the offline parent-to-first-grid weight mapping left open by E011AY. Actual Windows named-source/cache ownership, full deserialization and complete initialization policy remain open.

| Original boundary | Verified behavior |
| --- | --- |
| Parent reader 0x123CC0 | Owns a 384-byte module object, with payload at object+0x120 |
| Symbol helper 0x6F4F88 | Reads serialized symbol ID and resolves an owned 224-byte reader-table record; original helper executes |
| Parent grid lookup 0x123F5C | Consumes parent wire+28 and resolves the typed gridStatsConfig symbol |
| Parent allocation/store 0x123FA4 | Allocates 4×120=480 bytes and stores the array pointer at payload+0x38 |
| First child call 0x124034 | Invokes original 0x123550 using the resolved grid reader and first array element |
| Scalar copy 0x123814 | Native memcpy copies wire+20 to grid+20, 12 bytes |
| Scope end 0x123818 | Stops immediately after that first copy; post-copy array bookkeeping and aggregate tails are excluded |

The symbol-reader table is constructed in owned memory from the independently parsed, SHA-pinned tuning symbol records. The original symbol resolver, parent integer/count reader, grid scalar reader and native memcpy execute without stubs. Security/name/comparison, allocation and memset helpers are stubbed. Revision materialization is separately stubbed and excluded after its incomplete exploratory fixture stopped at 0xDB468; that fixture is not evidence of a driver defect or a numeric-weight producer.

The three installed v10.0 Default candidates each have 4 grid records. Original parent-to-first-grid prefixes pass 548 cases across four placements: three actual independent sources plus synthetic scalar bit patterns and 128 random mutations. All 12 produced bytes match their independent wire bytes, all three candidate source results match the private E011AX cache, and source bytes/allocation canaries are preserved. Captured weights are comparison outputs only.

Original address arithmetic at 0x124024..0x124030 passes 48 checks for indices 0–3 and a 120-byte element stride. These fragments calculate addresses; they do not claim all four element bodies were deserialized. At the first-child prefix, payload+0x2C contains 4 and payload+0x30 contains 0; an initial fixture assertion wrongly assigned 4 to+0x30 and was corrected. Subsequent counter/array bookkeeping remains excluded.

The original symbol resolver passes 18 additional cases. ID 0 resolves table slot 0; a non-null result alone is insufficient type authority. Out-of-range IDs and truncated reads return null in these fixtures. The independent source qualifier rejects 16 malformed root/version/mode/count/child/type descriptions, including a grid reference to slot 0. These are source-authority rejections, not claims about whole-driver rejection behavior.

The next live join has exact source-locked sites: named aecxhwstatsconfig lookup call 3CA984, return 3CA988, holder store 3CA998. Name is argument x1. Qualify actual public/core/bank tables and loaded callback code before binding the returned module payload to ConfigureHWStats data+F0 and grid Init's supplied/retained cache. NEXT-OBSERVER.json is source-only: no identity has been created and nothing is armed. E011AX-20261001-0055A remains consumed.

Golden boot f627e38e-19d3-480a-900d-73116d63b4df, kernel 7.1.5-sp11-render-parity-v4+, saved FullIOv19c, empty next_entry, all three protected hashes unchanged, NTFS unmounted and camera idle. A transient PiMaster connection drop recovered without reboot. No camera Start, production C, kernel build, observer arming or runtime action occurred. Original binaries/tuning/decompilation and all raw records remain private on the same SP11.

Existing full offline startup parity remains 0/0/0/0 conditional on its prior observed caller inputs; this stage does not replace those inputs in the composer. Actual source/file/profile selection, cold metadata handoff, normal RS count/offset authority, complete deterministic startup, WM16 same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement and Linux optical parity remain open. Native rear runtime remains **DENIED**.
