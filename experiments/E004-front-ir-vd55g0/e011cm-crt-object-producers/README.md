# E011CM original CRT object producers

Status: **PASS, bounded source-only OS-contract scope**. Base: 4ffe0b6185e19ad7b0cab319cfb728d3d37085ab.

Hypothesis: unchanged original CRT instructions produce the missing count/vector/indexed objects and mutex ownership without guessed locale blocks. Eight accepted cases cover four owned placements and default count zero or explicit owned preset 128. Source default becomes512; positive preset is preserved. This isolated CRT matrix does not rerun or extend E011CL's camera-entry prefix.

| Complete original entry | Result under explicit owned OS contracts |
| --- | --- |
| 0xCB7280 | Initializes 15 global 40-byte mutexes; counter 15; W0=1 |
| 0xCBAE10 | Gets owned opaque heap handle, stores16A3240; W0=1 |
| 0xCC06F0, index0 | Allocates 64*72 zeroed records, initializes 64 mutexes, attaches16A2A90/capacity64; balanced index7 lock; W0=0 |
| 0xCB3260 | Allocates count*8 vector at 16A2A58, links three original 88-byte static objects, initializes 3 mutexes, writes field+24=-2; W0=0 |

Independent whole 72-byte record models are zero except qword+40=all-ones and bytes+58/+59/+60=10. Independent whole 88-byte static object models are zero except source flags+20 (8193/8194/8194) and field+24=-2. Entire vectors contain three original image pointers then zeros. Opaque OS mutex bytes remain unchanged under the logical fixture; native Windows representation is unqualified.

All 180 source image-write chunks match exact site/offset/width/value. Complete mapped-image and 2 MiB owned-arena comparisons admit only independently predicted deltas, native heap is unchanged, allocation canaries intact. Totals: 32 original complete entry returns, 512 entire records, 24 entire static objects, eight whole vectors, 656 logical OS initializations, 16 guarded allocations.

Eight additional existing index0 lookups return with no new allocation/initialization. Creation and lookup each balance one enter/leave pair: 16 total enters/16 leaves.24 negative ownership requests (wrong heap handle, duplicate initialization, unbalanced leave) are rejected without accepted memory/resource/event mutation.

Five explicit OS contracts: GetProcessHeap supplies an opaque owned handle; HeapAlloc requires actual handle/flags8/source-requested size and returns aligned 16 guarded zeroed memory; InitializeCriticalSectionEx requires exact source-owned receiver/spin 4000/flags0; Enter/Leave require initialized receiver and balanced logical single-thread ownership. HeapFree/unobserved OS producers are not admitted. Original numeric routines execute; TLS initialization 0xCFE600 raises if reached. No numeric/TLS success stub, null-page mapping or new logger classification.

Correction to earlier excluded locale hypothesis: 16A2A50 is a 32-bit count,16A2A58 a pointer vector, 16A2A90 an indexed table requiring its original producer. Global mutex initializer includes 16A3000 (index8). These source relationships are qualified within owned OS contracts. Actual standard handles, locale, complete CRT, full loader dispatch order, Windows mutex bytes/concurrency remain open. Indexed records retain invalid-handle sentinels; no real Windows standard handle is synthesized.

All private candidate/checker exploration is excluded from acceptance. CB4310 reaches unmodeled LoadLibraryExW and is not admitted. Original DLL/disassembly/tuning strings/optical evidence remain private on SP11; only independently written verifier and derived relationships/hashes are committed.

Accepted job/times/source hash/checks are in RESULT.json. Scope is six experiment files plus eight continuation/readiness files. No production C/kernel/deployment/MMIO/Start/reboot/image test. Golden and historical checkouts unchanged. Rollback retains CL and this source-only evidence; Golden untouched.

Next **E011CN** integrates exact original producers into owned outer-entry, independently qualifies runtime stream/table deltas/OS locks, then output/outer-inner publication/whole return/balanced release. Full bootstrap/preflight/RS count/whole-frame offset and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Clean front/back first; optional AI/effects/HDR/catalogue deferred.
