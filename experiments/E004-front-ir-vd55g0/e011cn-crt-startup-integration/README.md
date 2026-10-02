# E011CN original CRT integration into camera startup

Status: **PASS, bounded source-only OS-contract scope**. Base: 26424022418adb9ecb934cc2d92db92153616a06.

Hypothesis: the exact original CRT count/vector/indexed-object producers qualified in CM can run on the same owned Native instance as the original camera startup, supplying initialized CRT locks and stream objects without guessed locale blocks. Twelve unmodified cases cover three pinned tuning sources and four camera placements each. The CM four-entry producer chain runs once per source fixture before the camera cases; this explicit owned order does not qualify the actual Windows loader's full initialization order. CM's separate preset128 and CL's poison variants remain historical evidence, not rerun variants here.

Original camera entry 0x36CBA0 and the entire CL prefix execute first. Execution continues after 0x36DE04, with original numeric instructions intact, through a complete stream allocator and then stops immediately before the original indirect LoadLibraryExW call at 0xCB9C10 (IAT 0xF7E310). The call target is checked against the original import cell. No Windows DLL loader is invoked and no loader success result is synthesized.

| Source operation | Qualified owned relationship |
| --- | --- |
| Original 0xCC6078, caller return 0xCED150 | Argument0 is a caller-owned 8-byte pointer-result record; returned X0 points to this record |
| Result stores 0xCC608C / 0xCC60A4 | Clear record to zero, then attach the actual new stream pointer; adjacent 24 stack bytes preserved through allocator return |
| Original calloc, return 0xCC61B4 | Count 1 * stride 88; HeapAlloc uses actual owned handle / flags 8 / size 88 |
| Pointer-vector store 0xCC61B4 | Original vector attaches each new stream at successive indices 3/4/5/6 |
| Original stream stores | Entire 88 bytes zero except flags+20=8192 and field+24=unsigned32 all-ones |
| Original mutex initialization, return 0xCC61E4 | Exactly stream+48, 40 zero bytes, spin4000/flags0 |
| Enter returns 0xCC6098 / 0xCC61FC | Initialized global mutex8 / new stream mutex |
| Leave return 0xCC60C8 | Global mutex8 releases; stream mutex remains held |
| Original image stores 0x13F8 / 0x1420 | Field 0x1607B00 becomes 0x80000000 on first use; subsequent cases retain it without stores |

The result-record ABI is independently checked against the original stores and complete record/adjacent bytes. Twelve complete allocator returns preserve this link, release the global lock and retain the source-created stream lock. Pointer-record ownership, not an assumed direct-stream return, is the acceptance contract.

All 96 exact CRT owned-write chunks match by site, address, width and value. The image flag is independently modeled from preexisting state: per source, first case makes two stores and later cases make none, giving six stores total. Its complete native meaning is not newly claimed.

Independent complete 2 MiB CRT-arena and complete mapped-image models cover bootstrap objects, vector additions, all prior held streams and current stream. Allocation alignment/canaries, native heap, serialized input, entire camera arena and entire 606264-byte inner remain checked. The outer is unchanged and public output zero; statistics+40 and mode+91952 stay attached. The caller/diagnostic model inherited from CI also passes.

Totals: 12 stream allocations / 12 new logical OS mutex initializations / 12 complete 88-byte stream models / 12 complete pointer-result records. Runtime CRT locks enter 24 times and the global lock leaves 12 times. Each source fixture retains four new stream locks and accumulates four holds on its single logical camera outer lock at the bounded stops. This deliberately incomplete lifetime is not cleanup, actual object reuse or concurrency proof.

Three CM bootstraps provide 12 complete original entry returns, three existing-table lookups,192 complete 72-byte indexed records, nine complete 88-byte static stream objects, 246 logical initializations and six guarded allocations. Nine inherited negative OS ownership requests reject. Inherited camera checks pass 180 entire 152-byte statistics records / 1440 statistics initializers / 292 core initializers / 516 core-cache plus 24 additional module GetTag lookups, 540 total.

Five heap/single-thread mutex APIs remain explicit owned OS contracts. Original TLS CFE600 raises, previously disclosed CE7C98 diagnostic fixture and null 16A4230 inert dispatch remain limitations; no new 16A4228 logger admission. Actual standard handles/locale, opaque Windows mutex bytes/concurrency, full loader dispatch order and complete CRT remain unqualified.

All private candidate/origin/ABI probes are excluded. Three rejected matrix attempts were corrected before acceptance: premature stream-lock address construction, direct-stream-return assumption, and fixed two-write-per-case assumption. Syntax/diagnostic attempts are also excluded. These are verifier/exploration failures, not hardware camera failures; original instructions were unchanged. The accepted source hash/job/times are in RESULT.json.

Scope is six experiment files and eight continuation/readiness files. Original DLL/disassembly/tuning strings/optical evidence stay private on SP11. No production C/kernel/deployment/MMIO/Start/reboot/image test. Golden hashes and historical checkouts match GUARD-SAFE.json. Rollback retains CM/CL and this source-only evidence; Golden untouched.

Next **E011CO** qualifies original dynamic DLL-loader/module/API ownership and remaining CRT dependencies before final output/outer-inner publication, whole return and balanced release. Full bootstrap/preflight/RS whole-frame/count/offset and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred.
