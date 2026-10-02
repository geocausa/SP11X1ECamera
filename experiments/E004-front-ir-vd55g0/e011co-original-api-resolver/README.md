# E011CO original dynamic module/API resolution

Status: **PASS, bounded source-only owned OS-contract scope**. Base dd6467aaa2c2e3c28953192e716f08560eddd133.

Hypothesis: the original dynamic resolver reached by CN can select its module and API using catalog-backed owned OS interfaces, write/cache the actual owned pointers, restore read-only protection and release the source-initialized CRT global lock. The API result itself remains a later gate.

The original OEM image is unchanged and SHA-pinned by the inherited verifier chain. Source module and API strings are read only by original RVA/length/hash; raw names and all disassembly stay private. The requested Windows ARM64 module was read from the same SP11's unmounted Windows partition using read-only ntfscat. Its1472296 bytes/hash and1691 named exports are checked; its export module name matches the original request. The requested export is ordinal38/RVA0x70A90, present and not forwarded, with an executable-section target. This is PE catalog evidence, not proof of a live Windows load or successful invocation. No Windows OS PE is mapped into the emulator or its code executed.

| Original operation | Qualified owned relationship |
| --- | --- |
| Resolver0xCB9B88 | Complete return to0xCB9FA4 produces the owned API adapter pointer |
| LoadLibraryExW return0xCB9C14 | Original nameRVA0xF8CAA8,18 UTF16 bytes including null, HFILE0/flags2048; matching SHA-pinned catalog permits an opaque guarded handle |
| GetProcAddress return0xCB9D58 | Exact owned handle and source nameRVA0xF8CB70,16 bytes including null; selected named export permits an owned adapter pointer |
| Store0x132C→0x16A3210 | Module cache receives exact owned handle under the current owned cookie state |
| Enter return0xCB9C94 / Leave0xCB9CFC | Original initialized global CRT mutex14 at0x16A30F0 is acquired then released |
| VirtualProtect return0xCB9CBC | Exact source range0x1B60000,256 bytes; new protection4, caller-owned DWORD old-protection output |
| Store0x132C→0x1B60000 | First API cache entry receives exact owned adapter while page writable and CRT lock held |
| VirtualProtect return0xCB9CF0 | Same256-byte range; source explicitly requests protection2(read-only), not the reported previous protection |
| Wrapper0xCB9F68→indirect call0xCB9FB0 | Stops at owned adapter before any instruction executes; caller return would be0xCB9FB4 |

The cache PE section is writable in the source file metadata. Two isolated cases start with an owned writable page(4), and two with an explicit already-read-only fixture(2). The first request reports the actual modeled prior state; the second reports4 and ends the full4096-byte Unicorn page read-only. These states do not prove the actual Windows loader/CRT initialization sequence. Each successful provider operation changes real Unicorn memory permissions; provider success is contingent on exact ownership and successful emulated protection. Its four-byte output is checked against the entire caller stack immediately around the provider write. No host Windows VirtualProtect runs.

Four isolated opaque-handle placements0/1/40/1230 each execute a cold wrapper continuation and a cached continuation. All four cold resolvers return completely. All four cached wrappers reach the same unexecuted API adapter with no loader/export/protection/lock calls or image stores. These are API-boundary continuations, not whole wrapper returns.

Three fresh camera joins run the unchanged original0x36CBA0 entry, the inherited CN producer chain, complete stream allocation and then continue from CN's0xCB9C10 boundary through a complete resolver return to the unexecuted API. Each pinned tuning source uses the first camera placement only. The prior CN four-placement integration remains accepted historical evidence and is not claimed rerun across CO's new boundary.

The three joins preserve45 exact152-byte statistics records,360 statistics initializers,73 core initializers and135 total GetTag lookups,24 CRT owned-store chunks and six prior CN first-use flag stores. Entire camera arena/606264-byte inner/72-byte outer remain unchanged after CN; output remainszero, manager and mode links retained, stream and camera locks remainheld. The resolver-specific index14 lock releases in every cold case. This is neither object cleanup nor concurrency proof.

Seven cold cases give seven module loads/export lookups,14 protection changes and seven balanced resolver lock pairs. Exact original image stores total22:seven module pointers,seven API pointers,eight isolated first-use flag stores. Integrated cases already set that flag in the CN prefix. Whole mapped image, resolver arena, CRT arena, native heap and logical lock-depth models are independent of observed final memory. Earlier original numeric instructions continue unchanged; CFE600 raises and no new16A4228 logger admission exists. The inherited CE7C98 owned-TLS diagnostic fixture and original null16A4230 inert dispatch remain explicit limitations.

Forty-two negatives reject six wrong ownership/contracts per fixture: wrong loader flags, wrong handle, wrong source export-name pointer, unowned protection range, unowned old-protection pointer and wrong CRT receiver. The negative checks use cold-contract context, so a blanket cached-path refusal cannot make them pass. Complete relevant image/arena/protection/depth/event state remains unchanged.

Opaque module handles and API adapters are guarded owned objects, not native Windows handles or callable OS function pointers. Only positive selected-name catalog ownership is qualified. Actual loader initialization/protection/cookie order, module lifetime/unload, missing-export/module/failure/forwarder paths, OS policy result, actual locale/standard handles/full CRT and native mutex bytes/concurrency remain open. No file-encoding policy BOOL is synthesized.

All private input/origin/catalog/import/protection/cold-warm probes are excluded. Two full-matrix setup attempts failed before acceptance and are excluded: requiring file bytes for a zero-initialized virtual PE module cache, and reversing the CRT constructor arguments. An earlier private probe's read-only PE-section assumption was corrected from static section metadata. Original instructions were unchanged; these were verifier/probe failures, not hardware failures. Accepted source hash/job/times are in RESULT.json. The accepted job ran privately, and its exact source/results were promoted unchanged to this folder.

Scope:six experiment files and eight continuation/readiness files. Original DLLs/tuning/disassembly and optical evidence stay private on SP11. No production C/kernel/deployment/MMIO/Start/reboot/image test. Golden hashes and historical checkout digests match GUARD-SAFE.json. Rollback retains CN and this source-only evidence; Golden untouched.

Next **E011CP** qualifies file-encoding API producer/consumer and the original wrapper return without guessing its policy result, then remaining CRT/publication/full return/balanced release. Native rear remains denied pending full startup/preflight/RS whole-frame/count/offset and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical parity. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred.
