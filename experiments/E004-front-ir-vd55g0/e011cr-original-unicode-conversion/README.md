# E011CR original Unicode conversion

Status: **PASS, bounded unchanged source in guarded owned fixtures**. Base: 0ba6f3ca5d4f2438ea5d9c260785325844ad2c42.

The original Windows API and NTDLL implementation now produce the Unicode size and output. No guessed size or conversion result is returned by a substitute. Same-SP11 private PE copies are SHA-pinned, including the new read-only NTDLL copy. Only2636 bytes of pinned API/NTDLL code and16 source data bytes are copied into guarded emulation pages on SP11; originals/disassembly/name content remain private. Original code never executes natively.

| Original relationship | Qualified behavior |
| --- | --- |
| OEM import0xF7E2E8 | Explicit fixture binding to original dependency API0x47180 |
| Dependency import0x3182B8 | Same named NTDLL export0x6E880 |
| Source ANSI/OEM fields0x63A4A4/0x63A4A0 | File-image defaults65001, unchanged during each call |
| Cache cells0x640578/0x640588 | Explicit zero virtual-data fixtures; no live loader claim |
| Cookie0x639000 | SHA-pinned file-image seed; original cookie push/check executes |
| First query return |0xCB7788;37 code units including NUL |
| Original malloc |0xCB16C0 requests flags0/74 bytes, HeapAlloc return0xCB1700 |
| Second API return |0xCB7824;37 code units written into owned74-byte allocation |
| Original converter return |0xCFD4E8, W0 status0 |
| Caller result32-byte record | Original stores at0xCB77E0/+16 owned pointer,0xCB77FC/+24 code-unit extent |

Original API/helper code runs in guarded read/execute pages. Source data and import bindings remain modeled, with actual permissions and entire poisoned pages checked. The inherited policy page remains writable as previously qualified; the API makes no global write. Initializing a file-image seed, zero caches and import bindings is an explicit emulation setup, not proof of the live Windows loader, current ACP/OEM codepage, locale or cookie environment.

Both aliases0/1 follow unchanged code into the file-image UTF-8 path. Only NUL-terminated ASCII inputs are admitted. An independent Python UTF-8→UTF-16 calculation provides expected code-unit count and output; original instructions must produce those outcomes. General Unicode, invalid-byte/error paths, alternative codepages/defaults and live Default filename semantics remain gates. The Microsoft API contract is referenced in UNICODE-SAFE.json authority: negative count-1 includes NUL, size queries use capacity0, and output extent is measured in UTF-16 code units. Original source flags9 are retained; no general claim about explicit UTF-8 flags or other locale paths is made.

Sixty-four isolated original calls cover query/output, aliases0/1, input alignments0/1 and ASCII lengths0/1/7/8/15/16/36/255 excluding NUL. Synthetic caller fixtures are explicit. Each call checks its independent Unicode outcome, full stack, preserved callee-saved registers/SP, entire image/CRT/native heap and all guarded pages/permissions. The output buffer and unrelated canaries must match exactly.

Six fresh original camera0x36CBA0 joins repeat both policies on each of three pinned tuning inputs, one camera placement only. Each completes the original API size query, original malloc under an explicit owned HeapAlloc contract, original API output conversion and complete original0xCB76B0 return. The caller byte at SP+48 remains0; alternate caller/locale receiver paths remain unqualified. Prior wider/isolated CP/CN/CO placement evidence is historical, not newly rerun here.

HeapAlloc accepts only the initialized owned process-heap handle, flags0, exactly twice the independently verified query count, original return site0xCB1700 and one fresh allocation. Uninitialized bytes remain explicit poisoned ownership fixtures until the original conversion overwrites all74 bytes. Prefix allocations, guards, locks and lifetime records remain checked; no live Windows heap metadata/failure/concurrency behavior is claimed. The allocation remains owned at this bounded stop; later release is not yet proved.

Every new store is predicted before execution from a pinned instruction, receiver/address/width and its register operands; the memory hook must match that prediction. Stack and CRT models cover entire regions. The Unicode output is also checked independently from input decoding, and the full32-byte result record is separately modeled from its old value plus the expected owned pointer and code-unit extent. Original converter saved registers and SP restore. No result-pointer assumption is inferred from the first eight bytes alone.

Totals:76 complete original API returns/76 NTDLL entries;64 isolated calls and12 calls in six camera joins. Six complete converter returns/six74-byte allocations. Integrated calls execute4980 OS instructions/426 OS stores and450 following CRT instructions/54 following CRT stores. Thirty new negatives comprise six API scope/ownership checks and24 heap handle/flags/size/source-return checks, preserving modeled state. Earlier prefix evidence remains checked:90 statistics records/720 initializers/146 core initializers/270 GetTag lookups.

A failed full-matrix candidate and all private exploration are excluded. Guards exposed missing short-input helper coverage and an incomplete store model: signed64-bit hook values needed width normalization, and original unscaled halfword stores needed explicit support. A wider pinned helper extent and corrected model passed the accepted matrix with unchanged original instructions. Other excluded mistakes include inspecting a dynamic class as built-in, an uninitialized decoder read and local orchestration string preparation. No hardware failure occurred. Accepted script/results are promoted unchanged; exact hash/job/times are in RESULT.json.

Public camera output remainszero; camera and new-stream locks remainheld. Original TLS CFE600 still raises, and earlier diagnostic TLS/inert null dispatch/owned loader/linking/import fixtures retain their limits. No new16A4228 logger or numeric/TLS/policy/Unicode success substitute is added. Actual loader/defaults/locale/cookie/lifetime/concurrency, complete CRT/file opening, publication/full outer return/balanced release remain open.

Scope: six experiment files and eight continuation/readiness files. Golden payloads/boot identity, unmounted Windows partition and both historical checkout digests match GUARD-SAFE.json. No production C/kernel/MMIO/deployment/Start/reboot/image test. Rollback preserves CQ and Golden.

Next **E011CS** follows the caller after0xCFD4E8, qualifying remaining CRT/file opening and Unicode-owner release before publication/full outer return/balanced camera/stream release. Native rear remains denied pending full startup/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical parity. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred.
