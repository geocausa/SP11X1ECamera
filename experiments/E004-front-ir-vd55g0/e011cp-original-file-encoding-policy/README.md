# E011CP original file-encoding policy and wrapper

Status: **PASS, bounded original-source execution in explicit owned OS fixtures**. Base: 47b7301a26fe12609785ba8e65d7d550d2e7310a.

Hypothesis: the dynamically selected file-encoding policy query can return a value produced by its original state setters, and the original OEM wrapper and immediate consumer can return/use that value without a guessed-success BOOL adapter. Four isolated cold/cached pairs and six fresh camera joins pass.

The two same-SP11 OS PE files remain private and SHA-pinned. No native Windows DLL is loaded or called. Only 180 bytes covering the requested export/thunk, dependency query and two setter bodies are copied into guarded, relocated Unicorn pages on SP11. Original code/disassembly/module names stay private. Git contains this independently written verifier and derived scalar/RVA/hash evidence.

| Original source operation | Qualified relationship |
| --- | --- |
| Requested export 0x70A90, 4 bytes | Branches to original thunk 0x6CC0C |
| Requested thunk 0x6CC0C, 12 bytes | Import cell 0xF8038 binds the same named API in the SHA-pinned dependency |
| Dependency query 0x1E0910, 28 bytes | Returns whether policy qword 0x639880 equals local ANSI conversion identity 0x2CE8B0 |
| ANSI setter 0x185C50, 68 bytes | Original 17 instructions write four exact policy qwords; query then returns1 |
| OEM setter 0x185CA0, 68 bytes | Original 17 instructions write four exact policy qwords; query then returns0 |
| Original OEM wrapper 0xCB9F68 | Entire wrapper returns the source-produced BOOL |
| Camera caller return 0xCFD49C | Exact original direct call at0xCFD498 is checked |
| Consumer 0xCFD49C / 0xCFD4A0 | Reads a single byte at SP+48, then branches on nonzero W0 |
| ANSI / OEM bounded stop | Before0xCFD4C0 / before0xCFD4A4 respectively |

Producer inputs are explicit ANSI/OEM policy choices. They do not claim the live Windows default. Four imported NTDLL conversion-pointer cells bind guarded owned identity tokens; local conversion-thunk addresses are guarded owned identity ranges. No conversion function executes, no conversion result is stubbed, and no actual NTDLL/loader initialization is claimed. The query's equality compares the original setter's produced local identity and returns by original instructions. Only positive catalog-selected loader/linking behavior from CO is retained; its initialization/cookie/lifetime/failure/concurrency limits remain.

The exact setter-store sites, slots and value origins are listed in POLICY-SAFE.json authority. Each source setter performs four qword stores. Complete poisoned pages are independently modeled from pinned code plus explicit import bindings and four predicted policy fields. Code/identity pages are read/execute only, import/token pages read-only, and the policy page writable; all final actual Unicorn permissions match. The setters leave entire OEM image/native heap/CRT arena/stack unchanged.

Four opaque-handle placements0/1/40/1230 also relocate the small OS module pairs. Two cases begin ANSI then switch to OEM; two begin OEM then switch to ANSI. Each cold wrapper qualifies a full resolver, original OS query and full OEM wrapper return. After the opposite original setter runs, each cached wrapper returns the changed policy value without a new loader/export/protection/lock call or resolver image write. Cached function-pointer selection is therefore independent of current policy value.

Six camera joins each run original0x36CBA0, inherited CN/CO prefixes, complete stream allocation, complete dynamic resolver, original OS policy query and entire OEM policy wrapper. Both policy choices are covered on each of three SHA-pinned tuning inputs. Each uses the first camera placement only. Earlier CN/CO wider matrices are retained historical evidence, not claimed rerun across this new boundary.

All six wrappers return to0xCFD49C. Two original consumer instructions read the caller's one-byte field and select the appropriate branch by actual returned W0. The field is0 in these source cases; its other values and following receiver/locale branches are not newly qualified. Execution stops before0xCFD4C0 for ANSI1 and before0xCFD4A4 for OEM0. The rest of the consumer/CRT/file-opening path remains a gate.

The policy query, OEM wrapper epilogue and two-instruction consumer write no memory. Entire policy pages/imports/canaries/permissions, OEM image, native heap, CRT arena and original caller stack remain checked. Entire camera arena/606264-byte inner/72-byte outer are unchanged after the inherited prefix; manager/mode links remain attached and public output remainszero. Source-created stream and camera locks remainheld; this is not full entry return, cleanup or concurrency proof.

Totals:14 original setter returns,14 dependency query returns,14 entire OEM wrapper returns; seven results1/seven results0. All56 exact policy qword stores,392 original OS instructions and12 consumer instructions match. Ten complete resolvers produce28 exact image stores/20 protection changes/ten balanced CRT global14 lock pairs. Six inherited joins verify90 entire152-byte statistics records/720 statistics initializers/146 core initializers/270 GetTag lookups,48 CRT owned stores and12 earlier CN flag stores.

Sixty inherited CO ownership negatives reject. Thirty policy-scope negatives reject conversion-identity execution, query writes and a producer store at a wrong slot with a valid source-store site. Negative checks preserve complete pages/permissions/image/counters/registers. Actual conversion/codepage/locale/standard handles/full CRT/native loader environment/default policy/concurrency remain unqualified. Original TLS CFE600 still raises; earlier CE7C98 diagnostic TLS and original null16A4230 inert dispatch remain limitations. No numeric/TLS/policy success substitute or new16A4228 logger admission.

All private static/import/origin/width/policy/camera-join probes are excluded. A setter-name derivation missed its To component, a private probe used text casefold on bytes, and one full-matrix setup check mistook the consumer byte load for a word load; these were corrected before acceptance. Local orchestration/preparation mistakes are also excluded. Original instructions were unchanged; no hardware camera failure occurred. The accepted private job/source/results were promoted unchanged, with exact hash/job/times in RESULT.json.

Scope:six experiment files and eight continuation/readiness files. Original binaries/tuning/disassembly and optical evidence stay private on SP11. No production C/kernel/MMIO/deployment/Start/reboot/image test. Golden hashes, unmounted Windows partition and both historical checkout digests match GUARD-SAFE.json. Rollback retains CO and this source-only checkpoint; Golden untouched.

Next **E011CQ** follows the selected CRT/file-opening branch and qualifies its receiver/stores/dependencies before final publication/full outer return/balanced release. Native rear remains denied pending full startup/preflight/RS whole-frame/count/offset and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical parity. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred.
