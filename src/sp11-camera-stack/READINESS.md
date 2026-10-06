## 2026-10-06 E011IJ loop counter accepted 1→0 to 0x6006DC frontier

E011IJ executes the exact `0x6006D4` decrement, obtains `w26=0`, confirms the `0x6006D8` loop-back is not taken, and stops before `0x6006DC` reads `[sp+4]`. NEXT E011IK traces that caller-local provenance before executing it. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011II accepted native 0x1608858 one to 0x6006D4 frontier

E011II reuses accepted E011FM same-boot Windows authority for `RVA 0x1608858=1`, executes the exact load/nonzero branch, and reaches `0x6006D4` with `w26=1` and `x23=RVA 0x10F03B0`; the decrement is still unexecuted. NEXT E011IJ executes the decrement/branch and stops before `0x6006DC`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IH accepted native 0x160A218 zero to 0x600474 frontier

E011IH reuses the accepted E011FL same-boot Windows authority for `RVA 0x160A218=0`, executes the exact `0x60046C` load and bit-16 test, confirms no branch, and stops before `0x600474` reads `RVA 0x1608858`. NEXT E011II reuses E011FM authority for that field. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IG second-iteration cleanup accepted to 0x60046C frontier

E011IG resumes at `0x600454` with `w0=2`, current loop counter `1`, and `x23=RVA 0x10F03B0`; the original caller takes the nonzero path, clears `x20`, zeros the output slot, and stops before the global read at `0x60046C`. NEXT E011IH reuses accepted E011FL native authority for `RVA 0x160A218=0`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IF CED2F0 CRT=2 return joined to 0x600454 frontier

E011IF executes the exact `0x600450` call instruction, rejoins E011FO same-thread CRT error `2` with the accepted E011FJ complete `CED2F0` return contract, and qualifies return `w0=2` to `0x600454`. NEXT E011IG advances the second-iteration caller to the first global read. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IE second-formatter caller accepted to CED2F0 call frontier

E011IE resumes at `0x600440` with return `26`, loop counter `1`, and `x23=RVA 0x10F03B0`, then reaches `0x600450 -> 0xCED2F0` with exact source-owned arguments and no intervening memory access. NEXT E011IF rejoins the accepted same-thread CRT error and CED2F0 return. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011ID 0x7AC38 wrapper tail accepted to 0x600440 frontier

E011ID preserves return `26` through the accepted 0x7AC38 wrapper tail, restores its frame, and stops before `0x600440`. NEXT E011IE continues the accepted formatter caller source-exactly. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IC 0x6BDD0 tail accepted to 0x7ACDC frontier

E011IC executes the `0x6BE0C..0x6BE1C` tail under return `26`, restores the 0x40-byte frame, and returns to source callsite target `0x7ACDC`. NEXT E011ID returns the accepted 0x7AC38 wrapper to `0x600440`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IB 0x6BD48 epilogue accepted to 0x6BE0C frontier

E011IB source-qualifies `0x6BE08 -> 0x6BD48`, restores the 0x50-byte frame, preserves `w0=26`, and returns to `0x6BE0C` without executing it. NEXT E011IC advances only to the first new source-exact dependency/frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IA caller result propagation accepted to 0x6BDC0 epilogue frontier

E011IA propagates return `26` through the caller frame, takes the exact `0x6BDA4 -> 0x6BDB4` branch, and reloads `w0=26`, stopping before `0x6BDC0`. NEXT E011IB uses the unique source callsite `0x6BE08 -> 0x6BD48` to restore the 0x50-byte caller frame and return to `0x6BE0C`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HZ CAD868 epilogue accepted to caller 0x6BD94 frontier

E011HZ source-qualifies the unique callsite `0x6BD90 -> 0xCAD868`, executes the epilogue at `0xCAD9B0..0xCAD9C4`, restores the saved frame and entry SP, preserves `w0=26`, and returns to `0x6BD94`. Execution stops before the caller instruction. NEXT E011IA advances that caller only to its first new source-exact dependency/frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HY CA8658 short cleanup accepted to CAD9B0 epilogue frontier

E011HY source-qualifies cleanup object bytes `+0x28=1`, `+0x30=0`, `+0x38=0`, executes `0xCAD9A8 -> 0xCA8658` on its short cleanup path, returns to `0xCAD9AC`, and restores `w0=26`. Execution stops before the `0xCAD9B0` epilogue. NEXT E011HZ uses the unique source callsite `0x6BD90 -> 0xCAD868` to execute the epilogue and stop at caller `0x6BD94`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HX cleanup argument accepted to CA8658 call frontier

E011HX qualifies `x0 = caller SP+0x10` and stops before `0xCAD9A8 -> 0xCA8658`. NEXT E011HY qualifies the cleanup-object flags and executes the short cleanup path. No camera Start, reboot, rear runtime, or kernel build; native rear remains denied.

## 2026-10-06 E011HW CAD940 caller path accepted to cleanup frontier

E011HW terminates the output at caller `SP+0x47f`, carries return `26` through the positive return branch, and stops at `0xCAD9A4`. NEXT E011HX qualifies the cleanup-call argument and stops before `CA8658`. No camera Start, reboot, rear runtime, or kernel build; native rear remains denied.

## 2026-10-06 E011HV CA6280 cookie return accepted to CAD940 frontier

E011HV passes the original cookie checker across four opaque axes, restores the CA6280 frame, and returns to `0xCAD940` with `w0=26`. NEXT E011HW qualifies the immediate caller branch path. No camera Start, reboot, rear runtime, or kernel build; native rear remains denied.

## 2026-10-06 E011HU zero cleanup leaf accepted to CA63E4 frontier

E011HU qualifies `[sp+0x478]=0`, executes the `CB1650` zero fast path, and resumes with `w0=26`. NEXT E011HV closes the CA6280 cookie/epilogue return to `CAD940`. No camera Start, reboot, rear runtime, or kernel build; native rear remains denied.

## 2026-10-06 E011HT caller branch accepted to SP+0x478 frontier

E011HT qualifies the CA634C branch chain, caller output-buffer zero write, and `w21=26`, stopping before `[sp+0x478]`. NEXT E011HU reuses E011FZ zero-frame authority for that slot. No camera Start, reboot, rear runtime, or kernel build; native rear remains denied.

## 2026-10-06 E011HS parser return accepted through CA94E8 epilogue to CA634C frontier

E011HS loads parser return `26`, restores the CA94E8 frame, and returns to `0xCA634C`, stopping before caller execution. NEXT E011HT qualifies the accepted caller-frame branch chain and output-buffer zero write, stopping before `[sp+0x478]`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HR termination counter accepted to CA9880 return frontier

E011HR reuses E011GA's accepted receiver `+0x468 = 1`, increments/stores it to `2`, and takes the equality branch to `0xCA9880`. Execution stops before receiver `+0x20 = 26` is loaded as the parser return value. NEXT E011HS executes that load and the `CA94E8` epilogue, stopping at caller `0xCA634C`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HQ zero byte accepted to termination-counter frontier

E011HQ source-qualifies RVA `0x1370766 = 0`, advances the source pointer to `0x1370767`, stores receiver `+0x39 = 0`, and falls through the byte/state checks with parser state `7`. Execution stops before `0xCA986C` reads receiver `+0x468`. NEXT E011HR reuses E011GA's accepted counter value `1`, increments/stores it to `2`, and stops at `0xCA9880` before the return-value load. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HP third vararg copied to 0x1370766 byte frontier

E011HP source-qualifies receiver `+0x658 = RVA 0x13F1F28` and its 24-byte NUL-terminated source block, then executes the repeated helper through scan/copy/stream updates and cookie return. Stream pointer/count become receiver `+0x6ca` / `26`, receiver `+0x20 = 26`, and the retained source pointer is `0x1370766`. Execution stops before the signed byte read. NEXT E011HQ source-qualifies the zero byte and stops before receiver `+0x468` is read. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HO byte 0x73 accepted to third helper frontier

E011HO source-qualifies RVA `0x1370765 = 0x73`, advances the retained pointer to `0x1370766`, and reuses accepted parser-table bytes `8`/`7` plus signed dispatch `+20` to stop at `0xCA9838` before helper execution. Receiver `+0x20` remains `2`, parser state is `7`. NEXT E011HP source-qualifies receiver `+0x658 = RVA 0x13F1F28` and its 24-byte string, then carries the helper through copy/return to the `0x1370766` read frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HN third `%` byte accepted through repeated case to 0x1370765 frontier

E011HN source-qualifies RVA `0x1370764 = 0x25`, advances the retained pointer to `0x1370765`, reuses accepted table bytes `0xF8B21B = 1` / `0xF8B230 = 1` and signed dispatch `-52`, and executes the accepted `0xCA9718` case while receiver `+0x20` remains `2`. Execution stops before the next signed read at `0x1370765`. NEXT E011HO source-qualifies that byte and reuses the accepted `0x73` parser chain to stop at `0xCA9838` before helper execution. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HM backslash vararg accepted to 0x1370764 byte frontier

E011HM joins the accepted formatter vararg layout to receiver `+0x650 = RVA 0x10F03B0`, source-qualifies the one-byte `0x5c` string, and executes the repeated helper through scan, one-byte copy, stream updates, cookie check and helper return. Stream pointer/count become receiver `+0x6b2` / `2`, receiver `+0x20 = 2`, and receiver `+0x6b1 = 0x5c`. Execution stops before `0xCA984C` reads source RVA `0x1370764`. NEXT E011HN source-qualifies that byte and reuses the accepted `%` parser/dispatch/case chain to the `0x1370765` read frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HL repeated helper accepted to receiver+0x650 vararg frontier

E011HL executes the repeated `0xCA9838 -> CAB178 -> CAB1F0 -> CACDF8` path across four opaque-cookie axes, advancing receiver `+0x18` from relative `+0x650` to `+0x658` and stopping before `0xCACE28` dereferences the qword at `+0x650`. NEXT E011HM joins the accepted formatter vararg layout to qualify that qword as RVA `0x10F03B0`, qualifies its one-byte string, and carries the helper through copy/return to the next parser-byte frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HK F8B2A2 byte 7 accepted through +20 dispatch to CA9838 frontier

E011HK source-qualifies RVA `0xF8B2A2 = 7`, stores parser state `7`, and reuses the accepted index-7 dispatch entry `0xCA9908 = +20`; original dispatch selects `0xCA9838` and stops before the case. NEXT E011HL reuses the qualified helper/cookie chain to advance receiver `+0x18` from `+0x650` to `+0x658` and stop before the next vararg qword read at `0xCACE28`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HJ F8B2B7 byte 8 accepted to F8B2A2 frontier

E011HJ source-qualifies RVA `0xF8B2B7 = 8`; the first-table read combines scaled value `72` with parser state `1`, deriving exact second lookup RVA `0xF8B2A2`. Execution stops before `0xCA95D8` reads it. NEXT E011HK source-qualifies that byte and reuses the accepted index-7 signed `+20` dispatch entry to stop at `0xCA9838` before its case body. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HI 0x1370763 byte 0x73 accepted to F8B2B7 first-lookup frontier

E011HI source-qualifies RVA `0x1370763 = 0x73`, advances the retained pointer to `0x1370764`, stores byte `115` at receiver `+0x39`, and executes the parser-loop arithmetic under receiver `+0x20 = 1` and state `1`. The exact first lookup resolves to RVA `0xF8B2B7`; execution stops before reading it. NEXT E011HJ source-qualifies that byte and derives second lookup RVA `0xF8B2A2`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HH repeat CA9718 case accepted to 0x1370763 read frontier

E011HH reuses the accepted `0xCA9718` case under the new receiver state, preserving receiver `+0x20 = 1`, parser state `1`, and source pointer RVA `0x1370763` while applying the same owned case mutations. `0xCA9848` reloads the pointer and stops before the signed byte read. NEXT E011HI source-qualifies `0x1370763`, advances to `0x1370764`, and derives first lookup RVA `0xF8B2B7` without reading it. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HG F8B230 byte 1 accepted through -52 dispatch to CA9718 frontier

E011HG source-qualifies RVA `0xF8B230 = 1`, stores parser state `1`, and reuses the accepted signed dispatch entry `0xCA98F0 = -52`; original dispatch selects `0xCA9718` and stops before the case body. The retained source pointer is `0x1370763` and receiver `+0x20 = 1`. NEXT E011HH reuses E011GF case semantics and stops before the next byte read at `0x1370763`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HF state-7 first parser lookup accepted to F8B230 frontier

E011HF executes the `0xCA9590` loop under source byte `0x25`, receiver `+0x20 = 1`, and parser state `7`. Reusing accepted first-table RVA `0xF8B21B = 1`, the exact second lookup resolves to RVA `0xF8B230`; execution stops before `0xCA95D8` reads it. NEXT E011HG source-qualifies that byte and reuses the accepted signed `-52` dispatch entry to stop at `0xCA9718` before the case body. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HE 0x1370762 byte 0x25 accepted to CA9590 loop frontier

E011HE source-qualifies RVA `0x1370762 = 0x25`, executes the signed read, advances the retained pointer to `0x1370763`, stores byte `37` to receiver `+0x39`, and takes the nonzero branch to `0xCA9590` without executing the target. NEXT E011HF reuses the accepted first table byte at `0xF8B21B = 1`, executes the first lookup under parser state `7`, and stops before the derived second-table read at RVA `0xF8B230`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HD helper-return branch accepted to 0x1370762 byte frontier

E011HD executes `0xCA9840..0xCA9848` with helper return `1`; the zero branch is not taken and receiver `+0x10` reloads exact source RVA `0x1370762`. Execution stops before `0xCA984C` reads the byte. NEXT E011HE source-qualifies that image byte, advances the retained pointer to `0x1370763`, updates receiver `+0x39`, and stops before the selected `0xCA9590` target executes. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HC CAB178 return 1 accepted through cookie check to CA9840 frontier

E011HC sets helper return `1`, executes original `0x11F0` across four accepted opaque-cookie axes with successful comparison on every axis, restores the CAB178 frame, and returns from `0xCAB658` to `0xCA9840` with `w0=1`. Execution stops before the caller instruction. NEXT E011HD executes the caller zero-test and receiver source-pointer reload to RVA `0x1370762`, stopping before `0xCA984C` reads that still-unqualified byte. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HB CAD1F0 return accepted to CAB62C helper-return frontier

E011HB executes the `CAD1F0` epilogue and returns to `0xCAB590`. Receiver `+0x20 = 1` keeps the sign branch clear, while receiver `+0x28 = 0` takes the bit-2-zero branch to `0xCAB62C`; that instruction is not executed. NEXT E011HC writes helper return `1`, reuses E011GL/E011FZ's opaque cookie frame contract, validates the original `0x11F0` cookie check and `CAB178` epilogue, and stops at `0xCA9840` before the caller branch. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011HA receiver+0x20 accepted zero-to-one at CAD1F0 epilogue frontier

E011HA reuses accepted E011FZ `0xCA6318` to source-qualify receiver `+0x20 = 0`. Original `0xCAD294..0xCAD29C` reads zero, adds the selected one-byte count, and stores `1`. Execution stops before the `0xCAD2A0` epilogue. NEXT E011HB executes the epilogue/return to `0xCAB590`, qualifies receiver `+0x20 = 1` and `+0x28 = 0`, and stops at `0xCAB62C` before the helper return value is written. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011GZ object flag zero accepted to receiver+0x20 frontier

E011GZ replays the accepted E011FZ producer and qualifies object `+0x18` (receiver `-0x8`) as zero. Original `0xCAD284` reads zero, the nonzero branch is not taken, `x22=x23=1`, and `0xCAD290` also falls through. Execution stops before `0xCAD294` reads receiver `+0x20`. NEXT E011HA source-qualifies that u32 from original `0xCA6318`, increments/stores it to `1`, and stops before the `0xCAD2A0` epilogue. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011GY stream pointer/count updates accepted to object-flag frontier

E011GY resumes at `0xCAD260`, advances the stream-object qword0 from receiver `+0x6b0` to `+0x6b1` and count from `0` to `1`, then reloads the object slot at `0xCAD280`. It stops before `0xCAD284` reads object `+0x18` (receiver `-0x8`). NEXT E011GZ source-qualifies that flag from the accepted E011FZ setup and executes only the immediate branch pair, stopping before receiver `+0x20` is read at `0xCAD294`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011GX source-qualified one-byte copy accepted to stream-update frontier

E011GX executes `0xCAD25C -> 0xF5D480` using E011GR source authority for RVA `0x1370780 = 0x2e`. The original helper copies exactly one byte to receiver `+0x6b0` and returns to `0xCAD260`; no stream object pointer/count update has executed yet. NEXT E011GY advances the qualified pointer and count by one, reloads the object at `0xCAD280`, and stops before the unqualified object `+0x18` byte read at `0xCAD284` (receiver `-0x8`). No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011GW stream-object fields accepted to one-byte copy frontier

E011GW reuses accepted E011FZ final-frame authority to qualify the stream object at receiver `-0x20`: qword0 selects receiver `+0x6b0`, while object `+0x8 = 640` and `+0x10 = 0`. Original `0xCAD21C` takes the unequal branch, selects copy length `1`, and stops before `0xCAD25C -> 0xF5D480` with source RVA `0x1370780`. NEXT E011GX reuses E011GR's `0x2e` source-byte authority, executes the one-byte copy, and stops at `0xCAD260` before stream pointer/count updates. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011GV second CAD1F0 stream pointer accepted to object-field frontier

E011GV executes the second `0xCAB58C -> 0xCAD1F0` call with `x2=1` and reaches original `0xCAD218`. Receiver `+0x460` selects the accepted E011GA object at receiver-relative `-0x20`; execution stops before `0xCAD21C` reads object fields at `-0x18/-0x10`. NEXT E011GW reuses the accepted E011FZ CA6280 final-frame construction to qualify those object qwords and proceed only to the `0xCAD25C -> 0xF5D480` call frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GU first CAD1F0 zero-count return accepted to second-call frontier

E011GU executes the first `0xCAB3EC -> 0xCAD1F0` with `x2=0`; the original helper takes its zero-count fast path without reading receiver `+0x460` or the stream object. The caller follows receiver `+0x28` bit-3 clear and `+0x4c = 0` branches and stops before the second `0xCAB58C -> 0xCAD1F0` call. That call tuple is `x0=receiver+0x460`, `x1=RVA 0x1370780`, `x2=1`, `x3=receiver+0x20`, `x4=receiver+0x4c0`. E011GA authority resolves the slot value as receiver-relative `-0x20`. NEXT E011GV executes only through the pointer load at `0xCAD218` and stops before the object-field pair read at `0xCAD21C`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GT local formatting accepted to first CAD1F0 call frontier

E011GT executes `0xCAB288..0xCAB3E8` under the exact retained receiver state. The helper-local output prefix is zeroed, E011GA resolves receiver `+0x8` as receiver-relative `+0x4c0`, and the path reaches `0xCAB3EC -> 0xCAD1F0` with `x0=receiver+0x460`, `x1=local+8`, `x2=0`, `x3=receiver+0x20`, `x4=receiver+0x4c0`; the call is not executed. NEXT E011GU executes the zero-count fast return and proceeds only to the second `0xCAB58C -> 0xCAD1F0` call frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GS CACDF8 return accepted to CAB288 helper-local write frontier

E011GS stores scan result `1` at receiver `+0x48`, completes `0xCACDF8`, returns to `0xCAB1F8`, and qualifies the common continuation through receiver `+0x38 = 0` and `+0x28` low word `0`. It stops at `0xCAB288` before the first `x22` write. `x22` is source-owned helper-local SP from `0xCAB19C`, with local qword0 sentinel `-2`. NEXT E011GT executes the deterministic local-format path to `0xCAB3EC -> 0xCAD1F0`, with E011GA supplying receiver `+0x8` as receiver-relative `+0x4c0`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GR source-backed F5E3E0 scan accepted to CACE94 store frontier

E011GR source-qualifies the first 16-byte block at RVA `0x1370780` (leading byte `0x2e`, first zero at offset `1`) and executes `0xCACE90 -> 0xF5E3E0`; the original scan returns exact length `1`. Execution stops at `0xCACE94` before receiver `+0x48` is written. NEXT E011GS executes the store and `0xCACDF8` return path to the common helper continuation, stopping before the first `x22` write at `0xCAB288`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GQ CA65A8 leaf accepted to F5E3E0 call frontier

E011GQ executes `0xCACE48 -> 0xCA65A8` under the exact E011GP inputs and qualifies return `0`. The parent takes the zero-result and nonzero-pointer branches, preserving receiver `+0x4c = 0`, then reaches `0xCACE90` with `x0 = RVA 0x1370780` and `x1 = 0x7fffffff`; the call to `0xF5E3E0` is not executed. NEXT E011GR source-qualifies its first 16-byte dependency at RVA `0x1370780`, executes only the source-backed scan to return, and stops before the receiver `+0x48` store at `0xCACE94`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GP CACE28 source qword accepted to CA65A8 call frontier

E011GP closes receiver-relative `+0x648` from existing source authority: E011FO supplies formatter `x3 = RVA 0x1370780`, and the original formatter wrappers preserve that `x3` in the exact slot propagated into the receiver pointer. Four source-exact placements execute `0xCACE28..0xCACE44`, retaining RVA `0x1370780` in receiver `+0x40` and qualifying the `0xCACE48 -> 0xCA65A8` call state as `x0=36`, `w1=115`, `w2=0`, with `w21=0x7fffffff`; the call is not executed. NEXT E011GQ executes that leaf and stops before the downstream `0xCACE90 -> 0xF5E3E0` call. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GO CACDF8 receiver pointer accepted to CACE28 dereference frontier

E011GO derives receiver `+0x18` as receiver-relative `+0x648` from accepted E011FX/E011FZ placement authority and executes helper `0xCACDF8` through its frame/pointer update. The pointer is already aligned, advances to receiver-relative `+0x650`, and execution stops before the 8-byte read at `0xCACE28` from the original `+0x648` location. That qword remains unclaimed; NEXT E011GP must source- or native-qualify it before executing to the `0xCACE48 -> 0xCA65A8` call frontier. The parser source pointer remains `0x1370762`, state remains `7`, and no camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GN selected helper case accepted to CACDF8 call frontier

E011GN executes only selected case prefix `0xCAB1F0`, qualifying `x0` as the exact retained receiver, and stops at `0xCAB1F4` before helper `0xCACDF8`. The retained source pointer remains `0x1370762` and parser state remains `7`. Helper source first consumes receiver `+0x18`, updates that pointer, then reaches an 8-byte dereference at `0xCACE28`. NEXT E011GO source-qualifies the retained receiver pointer from E011GA and executes only through the pointer update, stopping before that dereference. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GM signed helper dispatch accepted to CAB1F0 case frontier

E011GM source-qualifies helper dispatch entry `0xCAB724` as signed `-6`. Four source-exact placements execute original `0xCAB1C4..0xCAB1D0`, selecting exact target `0xCAB1F0` while stopping before the selected case. Source inspection shows `0xCAB1F0` selects the retained receiver for helper call `0xCACDF8` at `0xCAB1F4`. NEXT E011GN executes only that case prefix and stops before the helper call. The retained parser source pointer remains `0x1370762`, parser state remains `7`, and no camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GL CAB178 helper accepted to signed dispatch-read frontier

E011GL executes helper `0xCAB178` under four accepted opaque-cookie axes, qualifying its frame setup, retained receiver read `+0x39 = 0x73`, range index `50`, and not-taken range branch. Execution stops at `0xCAB1C4` before the signed 4-byte table read from `0xCAB724`; that entry and selected helper case remain unclaimed. The retained parser source pointer is `0x1370762` and parser state is `7`. NEXT E011GM source-qualifies the signed entry and executes only the original dispatch calculation to the selected-case frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GK selected case receiver accepted to helper-call frontier

E011GK executes only case prefix `0xCA9838`, qualifying `x0` as the exact retained receiver, and stops at `0xCA983C` before helper `0xCAB178`. The retained source pointer is `0x1370762`, retained byte is `0x73`, and parser state is `7`. Helper source reuses E011FZ's opaque `0x11D0` cookie contract, then reads receiver `+0x39`, derives range index `50`, and first reaches a new signed dependency at `0xCAB1C4 -> 0xCAB724`. NEXT E011GL executes the helper entry only to that frontier. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GJ signed +20 dispatch accepted to helper-call case frontier

E011GJ source-qualifies signed entry RVA `0xCA9908` as `+20`. Four source-exact placements execute original `0xCA95F4..0xCA9600`, selecting case entry `0xCA9838` while stopping before the case body. Source inspection shows `0xCA9838` moves the receiver to `x0` and `0xCA983C` calls helper `0xCAB178`. NEXT E011GK executes only that case prefix and stops before the helper call; no helper result or downstream branch is claimed. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GI second table byte accepted to signed dispatch frontier

E011GI source-qualifies image RVA `0xF8B2A2` as `0x07`. Four source-exact placements execute the original `0xCA95D8` table read, retain parser state `7`, pass the original `< 8` / `<= 7` checks, and form jump-table base `0xCA98EC` with index `7`. Execution stops at `0xCA95F4` before the signed 4-byte dispatch entry read at `0xCA9908`. NEXT E011GJ must source-qualify that exact signed entry first. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GH first table byte accepted to second lookup frontier

E011GH source-qualifies image RVA `0xF8B2B7` as `0x08`. Four source-exact placements execute the original `0xCA95B8` table read, scale the value to `72`, combine it with retained parser-state byte `1`, and derive second lookup offset `146` from table base `0xF8B210`. Execution stops at `0xCA95D8` before the newly selected table-byte read at `0xF8B2A2`. NEXT E011GI must source-qualify that exact byte first. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GG second source byte accepted to table lookup frontier

E011GG source-qualifies image RVA `0x1370761` as signed/u8 `0x73` / 115. Four source-exact placements execute the original `0xCA984C` read, advance the retained source pointer to `0x1370762`, retain the byte at receiver `+0x39`, take the nonzero branch at `0xCA9858`, and derive lookup offset `166` from table base `0xF8B211`. Execution stops at `0xCA95B8` before the newly selected table-byte read at `0xF8B2B7`. NEXT E011GH must source-qualify that byte first. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GF selected parser case accepted to next signed-byte frontier

E011GF executes original `0xCA9718..0xCA9728` in four source-exact placements, qualifies the owned receiver mutations (`+0x38 = 0`, `+0x28 = 0`, `+0x30 = 0xffffffff`, `+0x4c = 0`), rejoins at `0xCA9848`, and reloads retained source-pointer RVA `0x1370761`. Execution stops at `0xCA984C` before its signed one-byte source read; the bounded memory-read trace observes no access to `0x1370761`. NEXT E011GG must source-qualify that exact byte before executing the read. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GE signed parser dispatch accepted to selected-case frontier

E011GE qualifies the pinned signed jump-table entry at RVA `0xCA98F0` as `-52`. Four source-exact placements execute original `0xCA95F4..0xCA9600`, selecting case entry `0xCA9718` while deliberately stopping before the selected case body. Static source shape shows that case rejoins at `0xCA9848`; NEXT E011GF will qualify its owned receiver mutations and stop before the next signed source-byte read at `0xCA984C -> 0x1370761`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-05 E011GD second parser-table byte accepted to dispatch frontier

E011GD qualifies the pinned `.rdata` byte at RVA `0xF8B222` as `1`. Four source-exact placements execute the second table read, store parser state `1`, pass the current range checks, and form the parser jump-table base `0xCA98EC` with index `1`. Execution stops before the signed 4-byte dispatch entry read at `0xCA95F4 -> 0xCA98F0`; no dispatch target or selected case is claimed. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011GE qualifies that exact jump-table entry; native rear remains denied.

## 2026-10-05 E011GC first parser-table byte accepted to second lookup frontier

E011GC qualifies the pinned `.rdata` byte at RVA `0xF8B21B` as `1`. Four source-exact placements execute the first table read and current parser index arithmetic with parser state `0`, producing scaled state `9` and second lookup offset `18`. Execution stops before the one-byte read at `0xCA95D8 -> 0xF8B222`; no second lookup value or downstream parser state is claimed. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011GD qualifies that exact second table byte; native rear remains denied.

## 2026-10-05 E011GB exact source byte accepted to parser-table frontier

E011GB qualifies the pinned `.rdata` byte at image RVA `0x1370760` as `0x25` (37). Four source-exact placements execute `0xCA984C` and the selected nonzero parser path: the owned source pointer advances to `0x1370761`, the byte is retained in the receiver, and the current parser arithmetic selects lookup RVA `0xF8B21B`. Execution stops before the one-byte table read at `0xCA95B8`; no lookup value or downstream parser state is claimed. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011GC qualifies that exact table byte; native rear remains denied.

## 2026-10-05 E011GA `CA94E8` receiver prefix accepted to source-byte frontier

E011GA executes the exact `0xCA6348 -> 0xCA94E8` call and current owned-receiver prefix across four placements. The helper creates its 64-byte frame, follows only fields constructed by E011FZ, increments the owned receiver counter `0 -> 1`, clears parser-state fields, and selects image RVA `0x1370760` as the source pointer. Execution stops before the signed byte read at `0xCA984C -> 0x1370760`; no source byte or parser branch is claimed yet. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011GB qualifies that exact image byte and follows only its resulting source branch; native rear remains denied.

## 2026-10-05 E011FZ opaque cookie producer accepted to `CA94E8` frontier

E011FZ executes the current `0xCA6294 -> 0x11D0` security-cookie producer under four distinct opaque cookie fixtures. All four traverse the same six original producer instructions and the same 38-instruction current `CA6280` path; only the encoded cookie stack word changes according to the exact `SP - cookie` formula. The live process cookie value is deliberately not claimed and the file-image cookie is not substituted as native authority. Original `CA6280` setup is qualified through `0xCA6344`, stopping before `0xCA6348 -> 0xCA94E8`. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011GA enters `CA94E8` only to its first new dependency/effect; native rear remains denied.

## 2026-10-05 E011FY `CA6280` entry accepted to cookie-producer frontier

E011FY executes the exact `0xCAD93C -> 0xCA6280` call and five original `CA6280` prologue instructions across four placements. The helper creates its exact 48-byte frame, saves the current nonvolatile tuple, sets the frame pointer, and preserves the E011FX call arguments. Execution stops before `0xCA6294 -> 0x11D0`; `0x11D0` is the image security-cookie producer and is not executed or assigned a live cookie value here. No camera Start, reboot, rear runtime, or kernel build is used. NEXT E011FZ qualifies the current cookie-producer contract before resuming `CA6280`; native rear remains denied.

## 2026-10-05 E011FX native `0x16072D8` pair accepted to `CA6280` frontier

E011FX joins bounded same-boot SP7 KDNET front-only authority for the current 16-byte `0x16072D8` pair. Qword0 remains image-relative to RVA `0x1607180`; qword1 is stable, nonzero, and not image-relative, and its absolute Windows value stays private. The older file-initial qword1 RVA `0x1607650` is rejected as current native authority. Four source-exact placements execute original `0xCAD8C8..0xCAD938`, copy the pair to `SP+0x28`, store owner flag `1` at `SP+0x38`, and reach exact `0xCAD93C -> 0xCA6280` args; `CA6280` is not executed. One front Start and two Windows oracle excursions occurred since FW base (the second reconstruction-only), no rear Start/kernel build, Golden restored. NEXT E011FY executes CA6280 only to the first new qualified dependency/effect; native rear remains denied.

## 2026-10-05 E011FW native `0x16A2A84=0` branch accepted

E011FW uses bounded same-boot SP7 KDNET process-context measurement on the front Windows oracle to qualify the writable 4-byte cell at `0x16A2A84` as `0` both before reader Start and after one successful front NV12 1920x1080 Start in the same process/module context. Four source-exact cases then execute original `0xCAD8B8`, confirm the `0xCAD8BC` nonzero branch is not taken, form the `0x16072D8` address through `0xCAD8C0/0xCAD8C4`, and stop before the 16-byte read at `0xCAD8C8`; 2,620 current-path mutations plus 264 producer-API mutations are rejected. One front Start and one controlled reboot were used, Golden Linux is restored, and no rear Start or kernel build occurred. NEXT E011FX resolves the current/native 16-byte `0x16072D8` value; the older file-initial pointer-pair model is not native runtime authority. Native rear remains denied.

## 2026-10-05 E011FV current `0xCAD868` x0=36 prefix accepted

E011FV enters original `0xCAD868` under E011FU's native-qualified `x0=36` call contract. Four placements execute 18 original prefix instructions each, perform 12 exact stack-write chunks each, take the current `x5==0` branch, and stop before the 4-byte read at `0xCAD8B8 -> 0x16A2A84`; 2,584 current-path mutations plus 264 producer-API mutations are rejected. The older E011DY zero for `0x16A2A84` remains a loader-model assumption rather than native authority. No new Start, reboot, kernel build, or rear runtime was used. NEXT E011FW resolves the current/native `0x16A2A84` value before executing that read; native rear remains denied.

## 2026-10-05 E011FU native `0x17A1150=36` read accepted

E011FU uses a bounded SP7 KDNET process-context measurement on the front Windows oracle to qualify the writable 8-byte cell at `0x17A1150` as `36` both before reader Start and after a successful front NV12 1920x1080 Start in the same process/module context. This rejects the older E011DY loader-zero model as native authority without claiming an exact native `0x6BD8C` breakpoint. The source-exact four-case replay then executes original `0x6BD8C`, produces `x0=36`, preserves the current formatter tuple, and stops at untouched `0x6BD90 -> 0xCAD868`; 2,356 current-path mutations plus 264 producer-API mutations are rejected. One front Start and one controlled Windows-oracle round trip were used; Golden Linux is restored, with no rear Start or kernel build. NEXT E011FV qualifies the `0xCAD868` entry/current contract; native rear remains denied.

## 2026-10-05 E011FT `0x6BD70` reload prefix accepted

E011FT executes the exact `0x6BD70..0x6BD88` consumer reload prefix after the current E011FS leaf return. `x8` retains `base+0x17A1150`; six exact stack reads per placement restore the formatter tuple into `x1..x6`. Four placements stop before the `0x6BD8C` 8-byte dependency read and reject 2,320 current-path mutations plus 264 producer-API mutations. The older E011DY zero at writable zero-fill `0x17A1150` remains a loader/model assumption, not native runtime authority. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FU resolves the current native value before executing that read; native rear remains denied.

## 2026-10-05 E011FS current `0xEDD0` leaf return accepted

E011FS executes the current `0x6BD6C -> 0xEDD0` call. The exact 12-byte original leaf executes three instructions per placement, returns `base+0x17A1150` in `x0` at `0x6BD70`, and preserves the current stack/nonvolatile ABI. Four placements reject 2,212 current-path mutations plus 264 producer-API mutations. Execution stops before the consumer; the next dependency is the 8-byte read at `0x6BD8C` from `base+0x17A1150`, with later `0xCAD868` still unexecuted. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FT qualifies the `0x6BD70` reload prefix to that read frontier; native rear remains denied.

## 2026-10-05 E011FR `0x6BD48` to `0xEDD0` frontier accepted

E011FR executes the accepted `0x6BE08 -> 0x6BD48` call with the current formatter tuple. Original `0x6BD48` enters at outer-SP-1696, allocates its 80-byte frame to outer-SP-1776, and performs eight exact 8-byte local-save chunks (saved frame/return pair plus six arguments). Four placements reach untouched `0x6BD6C -> 0xEDD0` and stop before the dependency, rejecting 2,184 current-path mutations plus 264 producer-API mutations. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FS executes the source-pinned `0xEDD0` leaf under this current frame and qualifies its exact return/result at `0x6BD70`; native rear remains denied.

## 2026-10-05 E011FQ `0x6BDD0` to `0x6BD48` frontier accepted

E011FQ executes the accepted `0x7ACD8 -> 0x6BDD0` dependency and qualifies the exact local argument reshape through untouched `0x6BE08 -> 0x6BD48`: `x0=outer-SP-1392`, `x1=0x280`, `x2=-1`, `x3=base+0x1370760`, `x4=0`, `x5=outer-SP-1496`. `0x6BD48` itself remains unexecuted. Four placements reject 2,040 current-path mutations plus 264 producer-API mutations. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FR enters `0x6BD48` only to its first `0x6BD6C -> 0xEDD0` dependency; native rear remains denied.

## 2026-10-05 E011FP formatter wrappers to `0x6BDD0` accepted

E011FP executes the accepted `0x60043C -> 0x7AC38` formatter call and the original `0x7AC38 -> 0x7ACA0` wrapper chain, bounding all live wrapper stack writes. At untouched `0x7ACD8`, the exact `0x6BDD0` tuple is `x0=outer-SP-1392`, `x1=0x280`, `x2=-1`, `x3=base+0x1370760`, `x4=outer-SP-1496`; `0x6BDD0` itself is not executed. Four placements reject 2,004 current-path mutations plus 264 producer-API mutations. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FQ qualifies `0x6BDD0` through its `0x6BE08 -> 0x6BD48` dependency boundary; native rear remains denied.

## 2026-10-05 E011FO second-iteration formatter arguments accepted

E011FO executes original second-iteration setup through the untouched `0x60043C` call boundary and qualifies the exact `0x7AC38` helper arguments: `x0=outer-SP-1392`, `x1=0x280`, `x2=base+0x1370760`, `x3=base+0x1370780`, `x4=base+0x10F03B0`, `x5=base+0x13F1F28`, with `w26=1` and retained `x23=base+0x10F03B0`. Four placements stop before executing the helper and reject 1,940 current-path mutations plus 264 producer-API mutations. No new Start, reboot, kernel build or rear runtime was used. NEXT E011FP qualifies the `0x7AC38 -> 0x7ACA0` wrapper chain to its nested `0x6BDD0` dependency; native rear remains denied.

## 2026-10-05 E011FN loop-counter / second `x23` post-index accepted

E011FN resumes the accepted `0x6006D4` frontier with retained `w26=2` and `x23=base+0x10F03A8`. Original `0x6006D4` decrements the counter to `1`, original `0x6006D8` loops back to `0x600418`, and original `0x600420` reads the second read-only `.rdata` table entry at RVA `0x10F03A8`, yielding image RVA `0x1370780` while post-indexing `x23` to `0x10F03B0`. Four retained placements stop at `0x600424` and reject 1,904 current-path mutations plus 264 producer-API mutations. No new camera Start, reboot, kernel build or rear runtime was used. NEXT E011FO qualifies the exact second-iteration `0x60043C -> 0x7AC38` formatter/helper call setup; native rear remains denied.

## 2026-10-05 E011FM native `0x1608858` one / nonzero branch accepted

E011FM source-qualifies retained `x21` from original `0x600410` as image RVA `0x1608000`, making original `0x600474` an exact 4-byte read of RVA `0x1608858`. A bounded Windows front-camera process-context read returned `1` after front initialization before reader Start and again after one successful NV12 1920x1080 front-only Start; original `0x600478` therefore takes its nonzero branch to `0x6006D4`. Four retained placements replay the exact load/branch, reject 1,816 current-path mutations plus 264 producer-API mutations, and make no claim beyond arrival at `0x6006D4`. One front Start, zero rear Starts and one controlled one-shot Windows round trip under the project reboot-count convention return SP11 to verified Golden Linux. NEXT E011FN qualifies the `0x6006D4` loop-counter decrement and `0x6006D8` loop-back before the second iteration; native rear remains denied.

## 2026-10-05 E011FL native `0x160A218` zero / bit-16 fallthrough accepted

E011FL independently reads the live front-camera FrameServer qword at RVA `0x160A218` as zero before reader Start and again after one successful NV12 1920x1080 front-only Start. The exact `0x60046C` breakpoint remained correctly armed at the stable module address but was not observed, so the checkpoint records the native value authority without claiming a breakpoint hit. Four retained placements execute original `0x60046C` and `0x600470`, prove bit 16 clear, fall through to `0x600474`, and reject 1,768 current-path mutations plus 264 producer API mutations. One front Start, zero rear Starts and one controlled reboot return SP11 to verified Golden Linux. NEXT E011FM qualifies the retained `x21` owner and exact 4-byte `[x21+0x858]` read; native rear remains denied.

## 2026-10-05 E011FK caller nonzero return/output cleanup accepted

E011FK qualifies the original `0x600454` nonzero return branch for `w0=2`, clears `x20`, executes the exact 8-byte zero store to the retained caller output slot at outer-entry `SP-1448`, and qualifies the `0x600468` zero-`x20` fallthrough. The next untouched source is `0x60046C`, reading 8 bytes from RVA `0x160A218`. Four cases reject 1,732 current-path mutations plus 264 producer API mutations. NEXT E011FL qualifies that pointer-field dependency before its bit-16 branch.

## 2026-10-05 E011FJ outer CAECF8 CRT2 / CED2F0 return accepted

E011FJ executes the new outer `CAECF8` call under the exact same-thread error authority, returns the current-thread CRT-error pointer, qualifies the `CED33C` 4-byte load as value `2`, and completes the original `CED2F0` error epilogue back to `0x600454` with `w0=2`, SP-relative `-1456`, and the saved nonvolatile frame restored. Four cases reject 1,680 current-path mutations plus 264 producer API mutations. NEXT E011FK qualifies the caller nonzero-return branch and output cleanup.

## 2026-10-05 E011FI CED330 zero store/branch to CAECF8 frontier accepted

E011FI executes the original `0xCED330` 8-byte zero-result store through the exact caller output pointer at outer-entry `SP-1448`, qualifies the `0xCED334` zero fallthrough to `0xCED338`, and reaches the new outer `0xCAECF8` entry with return link `0xCED33C`. Same-thread authority remains exact at OS error `3` / CRT error `2`; the selected lock and 76-byte owner remain released with no subsequent original reads. Four cases reject 1,620 current-path mutations plus 264 producer API mutations. NEXT E011FJ executes the outer `CAECF8` body and qualifies the returned CRT-error pointer/value before advancing the `CED2F0` epilogue.

## 2026-10-05 E011FH CED0D8 zero return to CED330 caller frontier accepted

E011FH executes the original `0xCED194 -> 0xCED110` zero-result epilogue, restores return link `0xCED330`, and completes the enclosing CED0D8 return with `x0=0`. The caller frame is exact at SP-relative `-1488`, with its output pointer at outer-entry `SP-1448`; the `CED330` store remains deliberately unexecuted. Selected lock stays released and no selected-object or retired-owner read occurs after release. Four cases reject 1,568 current-path mutations plus 264 producer API mutations. NEXT E011FI qualifies the exact zero store/branch.

## 2026-10-05 E011FG selected-object lock release to CED194 frontier accepted

E011FG executes `0xCED190 -> 0xCB3480`, proves the exact `LeaveCriticalSection(selected+0x30)` owned contract, and transitions the selected-object lock from held to released without changing the exact E011FF cleanup image. Execution returns to `0xCED194`; the 76-byte owner remains retired and both lowIO locks remain released. Four cases reject 1,496 current-path mutations plus 264 producer API mutations. NEXT E011FH propagates zero through the `0xCED110` epilogue and qualifies the enclosing return. Native mutex bytes/concurrency and rear runtime remain unqualified.

## 2026-10-05 E011FF CC60E0 selected cleanup to lock-release frontier accepted

E011FF resumes at `0xCED188 -> 0xCC60E0`, joins the source-qualified runtime atomic flag `0x80000000` from E011EJ/E011CN, and executes the exact original cleanup plus fallback atomic exchange. The selected claim changes `0x2000 -> 0`; the remaining cleanup image is exact, the `+0x30` critical-section region is unchanged, and its owned lock remains held. Execution returns to `0xCED18C`, reloads the same pointer, and stops at `0xCED190 -> 0xCB3480` before lock release. Four cases reject 1,440 current-path mutations plus 264 producer API mutations. NEXT E011FG qualifies the exact selected-object lock release; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011FE CFA9C0 error branch to CC60E0 frontier accepted

E011FE resumes at `0xCFA9C0`: exact incoming CFCC18 return `2` takes the original nonzero branch to `0xCFA99C`, sets `x0=0`, bypasses the selected-object mutation path, executes the CFA968 epilogue/`ret`, and returns to `0xCED178`. The outer zero-result path stores zero, reloads the exact unchanged selected-object pointer, and reaches `0xCED188 -> 0xCC60E0` with its owned lock still held. The retired 76-byte owner is never read again and both lowIO lock depths remain zero. Four cases reject 1,236 current-path mutations plus 264 producer API mutations. NEXT E011FF qualifies `CC60E0` selected-object cleanup; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011FD CFCC18 error return to CFA9C0 frontier accepted

E011FD resumes at `0xCFCCE4`: all four cases restore the caller-visible result slot to `-1`, preserve error return `2`, execute the original CFCC18 epilogue/`ret`, restore its saved nonvolatile state and stack, and land exactly at `0xCFA9C0`. Both lowIO locks remain released and the retired 76-byte owner remains untouched. Four cases reject 1,212 current-path mutations plus 264 producer API mutations. NEXT E011FE qualifies the `CFA9C0` nonzero branch to `CFA99C`; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011FC caller index-0 lowIO release accepted

E011FC resumes at `0xCFCC9C`: all four cases store return `2`, read cleanup flag `1`, select index `0`, resolve lowIO record 0, preserve its already-cleared active byte, and execute original `0xCC08C0` through the owned `LeaveCriticalSection(record0)` boundary. At `0xCFCCE4` both lowIO global7 and record0 lock depths are zero; the retired 76-byte Unicode owner remains untouched. Four cases reject 1,168 current-path mutations plus 264 producer API mutations. NEXT E011FD qualifies the remaining CFCC18 tail and return to `0xCFA9C0`; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011FB CFD410 parent return to CFCC9C frontier accepted

E011FB completes the original `CFD410` epilogue from `0xCFD52C`: all four cases restore the saved nonvolatile state and caller stack, preserve return value `2`, execute the original `ret` at `0xCFD548`, and arrive exactly at caller `0xCFCC9C`. The 76-byte owner released by E011FA remains retired with no original read before the frontier. The caller instruction itself is not executed. Four cases reject 1,136 current-path mutations plus 264 producer API mutations. NEXT E011FC qualifies the caller post-return store/branch prefix and retained lock/resource cleanup; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011FA current 76-byte parent cleanup accepted

E011FA resumes the accepted `CFD570` error return at `0xCFD518`: original source reads the current owner flag as `1`, selects the exact live 76-byte UTF-16 owner, and executes original `0xCB1650` through the owned `HeapFree(handle, 0, owner)` contract. All four cases observe HeapFree success, retire the 76-byte owner, perform no original read of it before `0xCFD52C`, reject 1,112 current-path mutations plus 264 producer API mutations, and explicitly reject E011CW's older 74-byte geometry. NEXT E011FB qualifies the parent epilogue/return to `0xCFCC9C`; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011EZ CFD570 error return to parent frontier accepted

E011EZ follows the accepted error path from `0xCFD704` through original `0xCAECF8`: a third original Windows `FlsGetValue2` lookup returns the current thread CRT-error pointer, `CFD570` loads CRT error `2`, restores its caller state and reaches parent `0xCFD518`. Four cases preserve the exact live 76-byte UTF-16 owner, reject 1,020 current-path mutations plus 264 producer API mutations, and execute no parent cleanup. E011CW’s older 74-byte release geometry remains excluded. NEXT E011FA qualifies the parent ownership flag and exact 76-byte cleanup pointer before `0xCFD528 -> 0xCB1650`; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011EY current thread/FLS CAEC20 error propagation accepted

E011EY joins the accepted CRT slot/thread producer into the same current owned CRT arena: across four placements the 968-byte thread owner is exactly the current next allocation, original Windows `FlsGetValue2` retrieves it twice, and original `0xCAEC20` maps Win32 error 3 to thread OS=3 / CRT=2. Four current-path cases reject 1,020 altered contracts; the inherited producer rejects 264 API mutations. The current 76-byte UTF-16 owner remains live and E011CW’s older 74-byte cleanup geometry is explicitly not reused. NEXT E011EZ follows `0xCFD704 -> 0xCFD5DC` through `0xCAECF8` to the CFD570 error return; no new Start/reboot/build and native rear remains denied.

## 2026-10-05 E011EX exact GetLastError return accepted

E011EX executes the original `0xCFD6FC` imported `GetLastError` call under the accepted E011EW same-boot Win32 contract and requires exact return `3` (`ERROR_PATH_NOT_FOUND`). Four retained placements preserve the 76-byte UTF-16 owner and lowIO/lock state, reject 984 altered contracts, and stop at `0xCFD700` before internal helper `0xCAEC20`. No new Start/reboot/build was needed. Older E011CU/E011CW cleanup evidence remains source authority only where byte-exact; its 74-byte owner geometry is not joined into this path. NEXT E011EY establishes current thread/TLS authority for `0xCAEC20`; native rear remains denied.

## 2026-10-05 E011EW source-exact CreateFileW failure branch accepted

The exact override-file open is now qualified without claiming a debugger hit that did not occur. E011EV fixed `C:\data\test\camxoverridesettings.txt` and the original `CreateFileW` arguments; on the same bounded Windows boot the file and parent were absent and the same exact Win32 contract returned `INVALID_HANDLE_VALUE` / `ERROR_PATH_NOT_FOUND` (3). Four original-source replay placements take the invalid-handle branch, clear the lowIO record active bit and stop before `GetLastError`, rejecting 952 altered contracts. The camera callsite breakpoint itself remains explicitly unobserved. The bounded reference used three front Starts, zero rear Starts, and SP11 is back on Golden Linux after the controlled round trip. NEXT E011EX qualifies `GetLastError` and continues cleanup/error propagation; native rear remains denied.

## 2026-10-04 E011EV joined CC08E8 / CreateFileW frontier accepted

Original `0xCC08E8` now runs against the source-qualified attach-time lowIO table under the inherited owned lock contract. Record zero is claimed, global mutex 7 is released, the record lock remains held, and the original path advances to the exact `CreateFileW` call boundary with the verified 76-byte UTF-16 path and exact GENERIC_READ / FILE_SHARE_READ / OPEN_EXISTING / normal-attributes argument set. `CreateFileW` itself is not executed. Four placements reject 936 altered contracts. NEXT E011EW resolves native file/provenance/handle authority before continuing. No Start/reboot/build was required; native rear remains denied.

## 2026-10-04 E011EU startup lowIO lifetime join / CFD570 prefix accepted

The attach-time lowIO table is now source-qualified through the joined runtime camera interval rather than copied from the separate E011EF path. Pair-8 attach initialization produces the 64 × 72-byte table; its reverse uninitializer belongs to detach/finalization. Four retained placements join only that accepted state, preserve the entire block unchanged, enter original `0xCFD570`, and complete the `0xCFD0B0` parser before stopping at `0xCFD5E8 -> 0xCC08E8`. 820 altered contracts reject. NEXT E011EV executes CC08E8 under the inherited owned lock contract. No Start/reboot/build was required. Native record selection/concurrency and rear runtime remain unqualified/denied.

## 2026-10-04 E011ET post-conversion CFD570 call frontier accepted

The original parent now resumes after the complete E011ES conversion return and source-qualifies the exact seven-argument setup at `0xCFD514 -> 0xCFD570`. The owned UTF-16 pointer is carried as argument2; retained locals/scalars are exact. `0xCFD570` itself is deliberately not executed in this checkpoint. Four placements reject 772 altered contracts. No Start/reboot/build was required. NEXT E011EU enters CFD570 and stops at the first genuinely new dependency. Native rear runtime remains denied.

## 2026-10-04 E011ES exact allocator / output conversion return accepted

E011ER's exact 38-character query result now continues through original `0xCB16C0`: the source-qualified process heap handle is read, an exact 76-byte flags-zero allocation is admitted under the inherited owned HeapAlloc contract, and the second original conversion produces the independently verified 76-byte UTF-16 output. Original `0xCB76B0` then returns status zero.

Four retained placements pass with 736 altered-contract rejections total. Selected object state remains unchanged; selected logical lock held, index-8 global lock released. NEXT E011ET resumes the parent at `0xCFD4E8` and qualifies the exact setup toward `0xCFD514 -> 0xCFD570` without assigning deeper semantics prematurely. No Start/reboot/build was required. Native heap internals, live locale/default-codepage policy, general error paths and native rear runtime remain unqualified/denied.

## 2026-10-04 E011ER exact conversion query to allocator frontier accepted

The exact E011EQ query is now closed for this specific source: 37 ASCII bytes plus NUL (38 bytes total). The bounded original Windows/NTDLL conversion machinery returns 38 UTF-16 characters with no result stub, giving an exact 76-byte allocation requirement. Four retained camera placements replay the joined chain through that return and stop immediately before original `0xCB16C0` executes.

The accepted matrix rejects 612 altered contracts total. Selected object/output state remains unchanged, the selected logical lock remains held and the index-8 global lock remains released. No camera Start, reboot or kernel build was required. NEXT E011ES qualifies the exact 76-byte allocator path and only then advances to the second conversion/output phase. Native allocator internals, live default-codepage/locale policy, general error paths and native rear runtime remain unqualified/denied.

## 2026-10-04 E011EQ CB76B0 conversion-query prefix accepted

The exact E011EP result-one state now enters original `0xCB76B0`. Its retained input is a 37-byte non-NUL ASCII source followed by NUL (38 bytes including terminator), so the original non-empty branch reaches `0xCB8D88`. The dispatch preserves exact query arguments: codepage selector 0, flags 9, input count -1, null output and capacity 0, then stops before the `MultiByteToWideChar` import at RVA `0xF7E2E8`. No OS query result is supplied or claimed.

Four retained placements pass with 544 altered-contract rejections total, selected object/output unchanged, selected logical lock held and index-8 lock released. NEXT E011ER extends the accepted E011CR original conversion contract to this exact 38-byte-including-NUL source before joining any result. No Start/reboot/build was required. Native rear remains denied; front retirement/IRQ/DMA/IOMMU remain open.

## 2026-10-04 E011EP native-qualified callback cache branch accepted

A fresh front-only Windows reference closed the `0x1B60000` callback-cache dependency without promoting the whole callback table. After successful initialization and before Start, the required slot was already populated with the source-identified Windows file-API mode callback. External KD inspection of that loaded callback showed a process-local equality test, and the live FrameServer values were equal, qualifying an exact native return of one. The exact native `0xCB9F68` instruction itself was not trapped and is not claimed.

Four retained source cases execute original `0xCB9F68` on the populated-slot path, the inherited original CFG no-op check, and the native-qualified callback result-one branch. Each rejects 124 altered contracts (496 total), leaves selected object/output unchanged, keeps the selected logical lock held and index-8 lock released, then reaches `0xCFD4E4 -> 0xCB76B0` with exact mode argument `w3=0`. Three front-only Start/Stop references succeeded (449/448/43 valid handles), no rear Start occurred, and SP11 returned to Golden Linux with persistent boot state and Golden hashes unchanged. NEXT E011EQ qualifies `0xCB76B0`; front retirement/IRQ/DMA/IOMMU remain open and native rear runtime remains denied.

## 2026-10-04 E011EO native-qualified selected field zero branch accepted

A bounded native front reference after successful initialization and before Start qualified the E011EN selected first-pointer field: runtime flag 0x16A2A84=0, first pointer target RVA 0x1607180, selected field 0x160718C=0, independently confirmed by KD memory read. The same reference disproved broad file-static persistence for the second pointer/global aliases, so authority remains intentionally narrow. The exact native CFD46C instruction was not trapped and is not claimed.

Original source now executes CFD46C and takes the zero/non-match branch to CFD498. Four placements reject 448 altered contracts total with selected object/output unchanged. NEXT E011EP is the CFD498->CB9F68 callback/cache helper and its first 0x1B60000 dependency. Four front-only Start/Stop references succeeded; one Windows round-trip returned to Golden Linux with boot order and Golden payload hashes unchanged. Rear native runtime remains denied; front retirement/IRQ/DMA/IOMMU gates remain open.

## 2026-10-04 E011EN joined CFD410 / CB6520 prefix accepted

Original CFCC98->CFD410 now advances through its first dependency helper at CFD460->CB6520 under the inherited E011DY owned cold-start authority. Four retained placements qualify the exact helper return, 12 dependency reads, 36 exact local-store chunks and 428 altered-contract rejections. The selected object/output remain unchanged; selected lock held, index-8 lock released.

The new frontier is before CFD46C dereferences 0x160718C. File-initial bytes are not promoted to runtime authority, and the inherited cold flag/pointer model remains explicitly non-native. NEXT E011EO must establish source/lifetime authority for that pointed field before advancing. Native rear runtime remains denied; IRQ/DMA/IOMMU and front retirement remain open.

## 2026-10-04 E011EM CFD550 / CFCC18 validation prefix accepted

Original CFA9BC->CFD550 reshaping and the CFCC18 validation prefix now pass four retained placements. The result word is initialized to -1, CFCC18's local pair is zeroed, and the exact seven-argument CFD410 call state is qualified at CFCC98 without executing CFD410. Totals: 20 meaningful exact wrapper stores and 220 altered-contract rejections. Selected object/output remain unchanged; selected lock held, index-8 lock released.

NEXT E011EN begins at CFCC98->CFD410 and stops at the first new dependency without source authority. Native rear runtime remains denied; IRQ/DMA/IOMMU and front retirement remain open.

## 2026-10-04 E011EL joined parent mode-parser prefix accepted

Original 0xCED150 continuation now reaches 0xCFA968 with exact retained arguments and completes the source-pinned 0xCFA2E0 mode parser. Four cases return flags 0x100000000 / validity 1. The new 0x16A382C dependency is writable virtual-zero BSS with two direct reads and no direct writers; E011EL uses only a bounded cold-zero source model, never a native-runtime claim. The two-byte mode literal remains immutable, SHA-pinned and unexported.

The new frontier is before 0xCFA9BC -> 0xCFD550 with exact prepared arguments. 4 cold-global reads, 16 mode reads, 8 call-argument sets and 60 altered-contract rejections pass. Selected object/output remain unchanged; selected lock held, index-8 global lock released. NEXT E011EM follows CFD550/CFCC18 only to its next independently qualified dependency. Native rear runtime remains denied.

## 2026-10-04 E011EK joined stream-allocator return accepted

E011EJ's qualified selected-stream state is now joined back into the retained E011EC 0xCC6078 frame. Four placement cases execute original 0xCC60A0..0xCC60D8, publish the selected stream to the outer result, retain exact object bytes, release the index-8 global resource at 0x16A3000 through original 0xCB7398, and return with exact ABI state to 0xCED150. The selected object's own logical lock remains held. Totals: 8 dependency reads, 24 exact stores and 220 altered-contract rejections.

Parent frames 0xCED0D8 and 0xCED2F0 remain live. NEXT E011EL resumes at 0xCED150 and qualifies the exact setup/call at 0xCED174 -> 0xCFA968 without assigning semantics prematurely. IRQ/DMA/IOMMU and front hardware retirement remain open; native rear runtime remains denied.

## 2026-10-04 E011EJ slot-3 stream object + native front correlation accepted

The original slot-3 null path is now source-qualified under the inherited source CRT state: 4 placement cases, one exact 88-byte lazy stream object, slot-3 publication, checked +20/+24 fields, owned resource initialization/lock, complete 0xCC6108 return, 16 exact key stores and 20 altered-contract rejections. Allocation-failure and alternate source runtime-flag branches remain unqualified.

Native Windows front evidence is intentionally separate. The real FrameServer has count 512, runtime flag 0x80000001 and slot 3 already populated before Start. The front start therefore selects/reuses that existing object, publishes it to the caller result and returns from 0xCC6108 to 0xCC60A0 on the same thread; it does not exercise the source lazy-null path. Front StartAsync succeeded, while frame-handle success for this debugger-delayed run is not claimed; E011EI's 102-handle front reference remains authoritative.

Raw pointers/logs/credentials/optical material remain private and SHA-anchored. SP11 returned to Golden Linux (BootCurrent 0005, Linux-first BootOrder unchanged, saved sp11-audio-fullio-v19c, empty next_entry, camera idle).

NEXT E011EK resumes original 0xCC6078 at 0xCC60A0 to qualify result normalization, index-8 lock release and complete stream-allocator return. IRQ/DMA/IOMMU and the distinct front hardware retirement path remain open. Native rear runtime remains denied.

## 2026-10-04 E011EI source count + native Windows correlation accepted

The camera count read at 0xCC6130 / 0x16A2A50 is now source-qualified and natively correlated at 512. Original arithmetic therefore bounds the next vector scan to slots 3..511 (509 slots), ending exactly at the 4096-byte vector boundary. The next source frontier is the slot-3 load at 0xCC6140.

SP7 KDNET plus SP11 Windows CDB directly confirmed the same native stream vector/count on the real FrameServer start path. Rear OEM NV12 3840x2160 and front OEM NV12 1920x1080 both completed Start/Stop reference runs. The rear bounded ISP probe produced 81 monotonic FIFO generations, 81 matching completions and 161 WM16 consumption observations across 10 rotating addresses. IRQ retirement remains unqualified. The front run does not traverse the same rear FIFO/match probe path, so front hardware retirement remains separate.

Raw native pointers, debugger logs, transport credentials and optical material remain private; committed evidence is derived and SHA-anchored only. SP11 returned to Golden Linux with BootNext consumed, saved GRUB entry unchanged and camera nodes idle.

NEXT E011EJ starts at 0xCC6140 and qualifies the slot-3 null/allocation path and bounded stream-vector scan/return. IRQ/DMA/IOMMU retirement continues as a parallel dynamic gate. Native rear runtime remains denied.


## 2026-10-04 E011EH startup stream lifetime / camera pointer read accepted

The process-attach stream vector is now source-qualified through the retained camera caller. 0xCB3260 publishes 0x16A2A58; the paired teardown 0xCB33A0 is the only source-qualified later clearer at 0xCB3400, while camera site 0xCC6120 is a pure read. Within successful attach to runtime camera use before detach, the startup vector remains live.

All 8 accepted E011CM startup variants pass the joined E011EH verifier. Original 0xCC6120 loads the exact startup vector pointer in every case, image/vector bytes remain unchanged, and 40 altered site/address/width/value/lifetime contracts are rejected. The startup-stream-to-camera join and pointer dependency read are accepted; native loader/allocator/synchronization internals remain separate.

NEXT E011EI resumes at 0xCC6130 / 0x16A2A50 and, where stronger or faster, correlates the same state dynamically using the existing SP7 debugger / SP11 Windows target. RS/AFD, file/provenance, exact buffer generation, IRQ and DMA/IOMMU retirement remain open. Native rear runtime remains denied. Rough front/back smoke readiness is now about 80 percent, subject to native hardware-lifetime evidence.

Zero camera Starts/reboots/kernel builds/production C/PM changes in E011EH. Golden payloads, EFI/GRUB and historical repositories remain unchanged. See experiments/E004-front-ir-vd55g0/e011eh-source-qualified-stream-lifetime-camera-read/. Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EG CRT startup order accepted

Process-attach source ordering is now qualified: the pre-constructor subsystem walker must successfully pass pair eight `0xCB5DD0`, which requires `0xCC06F0` index zero to succeed, before the later constructor iterator can invoke first non-null entry `0xCB3260`. E011CM's 8-case producer/consumer matrix was rerun successfully, so the startup `CC06F0 → CB3260` state handoff and stream-initializer return are accepted within the inherited owned OS contracts.

E011EF `0xCC08E8` remains a separate valid path and is not joined here. The camera remains separate before `0xCC6120` reads `0x16A2A58`. NEXT **E011EH** qualifies startup-stream lifetime/order to that camera caller. Native CRT internals and native rear runtime remain unqualified/denied.


## 2026-10-04 E011EF low-level I/O count transition / initializer return accepted

The isolated original lowIO initializer now completes its cold owned-count path: source reads zero from 0x16A2E90, writes 64, enters record zero through the original wrapper, sets its active byte, releases the global index-seven lock and returns zero with exact NONVOL/SP.

256 cases pass: 9,472 added original visits, 512 exact source stores, 14,080 altered owned requests rejected, 1,280 exact dependency reads, 512 wrapper entries, 512 owned API calls and 256 exact initializer returns. Every E011EE ancestor row remains equal; memory/permissions and redzones match without resets. Forty-nine execution pins remain exact.

This proves the isolated cold path and return, not native count selection, native CRT/handle state or loader startup ordering. The first record logical lock remains held and the global initializer lock is released. The stream initializer still remains before 0xCB3338 / 0x16A2A90, and the camera remains before 0xCC6120 / 0x16A2A58. No state join is claimed.

NEXT **E011EG** establishes actual loader/CRT ordering and only then attempts a source-qualified lowIO-to-stream handoff. Full stream/camera state joining, file/provenance, helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EF lowIO count / initializer return](../../experiments/E004-front-ir-vd55g0/e011ef-original-lowio-count-activation-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EE isolated original low-level I/O block publication accepted

The low-level table pointer at 0x16A2A90 now has a source-qualified producer prefix in a third, isolated emulator. Original initializer 0xCC08E8 acquires its owned index-seven lock, takes the explicitly owned cold pointer-zero branch, and calls original constructor 0xCC05B8. The constructor requests 64 records of 72 bytes, initializes each record through checked source stores and owned resource successes, returns the 4,608-byte block with exact NONVOL/SP, and original 0xCC093C publishes it.

256 cases pass: 738,304 added original visits, 169,728 exact ordered source-store chunks, 1,206,784 altered owned requests rejected, 33,280 exact dependency reads, 17,152 nested entries/ABI returns, 256 owned zeroed allocations and 16,640 owned API calls. Every complete E011ED row remains equal. Camera and isolated stream-initializer memory, permissions and frontiers remain unchanged; the new low-level initializer's entry-to-frontier memory/permissions and redzones match without resets. Forty-eight execution pins remain exact.

All 64 record resources are logically ready in the owned model. Each source record has an eight-byte all-ones field at +40, zero at +48, checked four-byte value 0x0A0A0000 at +56, byte ten at +60 and zeros at +61..+66; the remaining bytes stay owned-allocation zero. This proves neither native critical-section bytes nor valid native handles. Allocation and API success are explicit provider inputs; original allocator internals and native CRT initialization remain unproved.

Stop BEFORE 0xCC0948 reads four bytes from image+0x16A2E90, at lowIO-entrySP-96. NEXT **E011EF** establishes this runtime input before continuing the low-level initializer. The block constructor returned, but the low-level initializer has not returned and its logical lock stays held. Actual loader startup ordering and any joining of the three contexts remain unqualified. The stream initializer separately remains before 0xCB3338 / 0x16A2A90 at stream-entrySP-80; the camera separately remains before 0xCC6120 / 0x16A2A58 at outer-entrySP-1648.

Camera output, nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,989,120 includes two isolated initializer matrices and is not a joined trace. Full initialization/state joining, file/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EE isolated low-level I/O block publication](../../experiments/E004-front-ir-vd55g0/e011ee-original-isolated-lowio-block-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011ED isolated original stream-table publication prefix accepted

The runtime pointer at 0x16A2A58 has an original publisher: initializer 0xCB3260. Its prefix now executes in an isolated fresh emulator with explicit owned cold count/pointer inputs. Original source sets 512 slots, requests a 4,096-byte zeroed allocation, publishes the returned pointer, initializes the first logical standard-stream resource and writes image+0x1607060 into slot zero. The remaining 511 slots stay zero. Native allocation, CRT resource initialization and pointed stream contents remain unproved.

256 cases pass: 13,056 isolated original visits, 4,096 exact ordered source stores, 36,096 altered owned requests rejected, 1,024 dependency reads, 512 nested entries/ABI returns, 256 owned zeroed allocations and 256 owned resource-model calls. All E011EC rows remain equal; camera memory, permissions and its 0xCC6120 frontier remain unchanged. Isolated initializer entry-to-frontier memory/permissions and redzones match without resets. Forty-six execution pins remain exact.

Original 0xCB1650 returns zero on its null cleanup path. Original 0xCBA4B0 tail-calls the owned InitializeCriticalSectionEx model at resource 0x1607090 with spin count 4,000 and flags zero; both nested returns preserve NONVOL including SP. Model success and readiness remain explicit provider inputs, not native observations. The camera and isolated initializer states have not been joined.

Stop BEFORE 0xCB3338 reads eight bytes from image+0x16A2A90, independently checked index zero; current SP=initializer-entrySP-80. NEXT **E011EE** establishes the low-level I/O table's authority before continuing. The initializer remains active; full return and actual loader/CRT startup invocation are pending. The camera caller separately remains at 0xCC6120 / outer-entrySP-1648, with four active stream frames and its owned stream lock held.

Camera output, all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,250,816 includes the isolated initializer matrix and does not describe a joined trace. File/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011ED isolated stream-table publication prefix](../../experiments/E004-front-ir-vd55g0/e011ed-original-isolated-stream-initializer-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EC bounded stream setup / owned CRT lock accepted

Original caller 0x600368 resumes with the completed formatter result and enters wrappers 0xCED2F0 / 0xCED0D8 / 0xCC6078 / 0xCC6108. The exact 37 private bytes plus 603 zeros remain intact. A pinned two-byte mode literal at 0x1363D40 qualifies the original first-byte nonempty gate; mode interpretation, stream selection and file contents remain open.

256 cases pass: 13,824 added original visits, 4,608 exact ordered stack stores, 37,632 altered owned requests rejected, 256 immutable mode reads, 256 inherited loader-binding reads, 1,280 exact callee entries, 256 lock-wrapper ABI returns and 256 owned lock-model calls. No allocation runs. Complete E011EB rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,237,760, with ancestor counts separate.

Original 0xCB7300 derives a critical-section request at 0x16A3000 using the inherited import binding. Its owned EnterCriticalSection model requires exact caller, argument, SP, readiness and initially unheld state; both OS-void X0 clobber cases preserve the wrapper's saved NONVOL/SP. The new stream lock model is held. Earlier publication CRT/SRW locks remain released. This does not prove native CRT resource initialization or synchronization.

Stop BEFORE 0xCC6120 reads the runtime stream-table pointer at image+0x16A2A58 / eight bytes, current SP=outer-entrySP-1648. Four stream frames remain active with pending returns 0x600454 / 0xCED330 / 0xCED150 / 0xCC60A0. NEXT **E011ED** establishes this runtime dependency's authority before continuing. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

Forty-four execution pins retain all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks. Native runtime scalar/pointer selection, native CRT resources, file/provenance collection, full helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EC bounded stream setup / owned CRT lock](../../experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EB complete selected formatter output / consumer returns accepted

Original source completes the selected three-argument formatter with lengths 12 / 1 / 24, exact 37 private bytes, and original terminators at output indices 37 and 639. The retained 640-byte destination has 603 zero bytes after the output. All seven inherited consumer frames return to their actual callers with exact NONVOL including SP; their stack contexts and cookie scratch slots retire after proof. No output or result fixture is supplied or exported.

256 cases pass: 199,680 added original visits, 30,464 exact ordered store chunks, 221,952 altered owned requests rejected, 7,936 immutable reads, 4,096 ordinary callee ABI returns, 1,792 inherited consumer ABI returns, 512 cookie-push and 768 cookie-pop convention returns. All complete E011EA rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,223,936 with ancestor counts separate.

Remaining literal authorities cover 0x10F03B0 / 16 bytes and aligned 0x13F1F20 / 48 bytes, with the second literal at offset eight. One sparse cell at 0xF8B230 and the 304-byte cold cleanup body at 0xCA8658 are pinned. Forty execution pins retain inherited runtime initial-value models. Signed write-hook values normalize to the exact unsigned word before comparison; original execution and effects remain unchanged. Cookie conventions remain SP-16 / SP+16, distinct from SP-preserving leaves or OS stack-growth proof.

Stop BEFORE actual caller instruction 0x600440 inside 0x600368, SP=outer-entrySP-1456 and X0=37. No consumer frames remain active. NEXT **E011EC** continues this caller with the completed output and all ancestor ownership retained. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, full helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied; guarded smoke remains pending and the rough ~70% estimate is unchanged.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EB complete selected formatter / consumer returns](../../experiments/E004-front-ir-vd55g0/e011eb-original-complete-constant-consumer-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EA original first argument length / copy accepted

Original source now finds the first argument's NUL in an immutable 13-byte literal, reads its exact 16-byte window, and copies twelve private bytes into the retained 640-byte destination. The eight-byte store and four one-byte vector stores match independently pinned source bytes; the remaining 628 destination bytes remain zero. No string contents or length/copy result fixture is supplied or exported.

256 cases pass: 45,824 added original visits, 6,400 exact ordered store chunks, 49,920 altered owned requests rejected, 1,792 exact argument reads, 1,024 callee ABI returns, 512 argument-consumer ABI returns and 256 cookie-pop convention returns. All complete E011DZ rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined original visits are 1,024,256; all ancestor counts remain separate.

Original 0xF5E3E0 returns length twelve; the two 0xCAD1F0 calls execute zero padding and actual copy, and original 0xF5D480 writes the private bytes. Original 0xCACDF8 and 0xCAB178 return one with exact caller ABI. The 0x11F0 cookie-pop leaf restores SP+16 and all other NONVOL; this remains separate from a standard SP-preserving leaf and OS stack-growth proof. The earlier zero-destination invariant advances only through these checked original copy effects.

Stop BEFORE the byte read at 0xCA984C from image+0x1370762. NEXT **E011EB** continues the original parser and remaining arguments with the twelve-byte output and returned handler frames retained. Current SP=outer-entrySP-3200, output cursor=outer-entrySP-1380 and variadic cursor=outer-entrySP-1488. Seven consumer frames remain active; full consumer and outer 0x5F8EA8 returns remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, callback table and registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, complete helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EA first argument length / copy](../../experiments/E004-front-ir-vd55g0/e011ea-original-first-argument-length-copy/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DZ original parser dispatch / variadic argument accepted

The retained original consumer now reads a seven-byte immutable literal (including its terminator) and seven exact sparse classification/branch cells, dispatches the first argument through original 0xCAB178 / 0xCACDF8, and advances the actual variadic cursor by eight bytes. The original 0xCA65A8 scalar helper returns zero with exact callee-saved ABI; the separate 0x11D0 cookie-frame convention again changes SP by -16. No original literal contents or string result fixture is exported or supplied.

256 cases pass: 43,008 added original visits, 9,728 exact stack store chunks, 70,912 altered owned requests rejected, 2,304 exact immutable reads, 256 scalar-helper ABI returns, 256 cookie-frame convention returns and 768 nested entries. Every complete E011DY row remains equal; cumulative original-entry-to-frontier memory and permissions match with no resets. Combined original coverage is 978,432 visits; inherited DY/DX/DW/DV/DU/DT/DS counts stay separate.

The first argument pointer is original image+0x10F0380, and the variadic cursor is outer-entrySP-1488. Its pointed string contents, read extent and length remain unqualified. The destination remains 640 zero bytes; all nine allocations, redzones, published 18,832-byte zero buffer/refcount one, nested containers, callback table and both registry locks remain retained. Native scalar/pointer selection, pointed locale tables, alternate flags and complete consumer/outer/helper/descriptor/profile startup remain open.

Stop BEFORE actual 0xCACE90 -> 0xF5E3E0, return 0xCACE94, SP=outer-entrySP-3360, X0=image+0x10F0380 and X1=0x7FFFFFFF. NEXT **E011EA** qualifies the original bounded string helper and exact pointed data/read windows in this retained parent. Its 184-byte body metadata is pinned separately; no helper execution or string-length result is accepted here. Nine consumer frames remain active; the outer 0x5F8EA8 return is pending.

E011DM remains the empty RS-query proof and E011DN the limited Windows snapshot. Populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material remain private on SP11.

See [E011DZ parser dispatch / variadic argument](../../experiments/E004-front-ir-vd55g0/e011dz-original-parser-dispatch-variadic-argument/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DY cold runtime context / nested receiver setup accepted

Under explicit loader initial-value models, original source reads the zero-fill options scalar at 0x17A1150 and flag at 0x16A2A84, then the file-initial pointer pair at 0x16072D8. Original 0xCAD868 constructs the retained stack context, and original 0xCA6280 constructs the nested receiver fields. These are source effects under declared models; native flag/pointer selection remains unqualified.

All 256 cases pass: 20,992 added original visits, 11,264 exact setup store chunks and 68,608 altered owned requests rejected. Each case validates four exact runtime reads, 44 independently authored ordered stores and two nested entries. The original 0x11D0 cookie-frame leaf returns at 0xCA6298 with its deliberate SP minus 16 effect and all other nonvolatile registers preserved. This is a cookie-frame convention, not an SP-preserving leaf ABI or OS stack-growth proof.

Complete inherited DX/DW/DV/DU/DT/DS rows remain exactly equal and separate; combined original visits are 935,424. One cumulative original-entry-to-frontier memory and permissions snapshot passes. All nine allocations, prior nodes/arrays/redzones, published 18,832-byte zero buffer/refcount one, callback table and epochs remain retained. The 640-byte output destination remains entirely zero; all 44 new stores lie below it. Both registry locks remain held and CRT/SRW released.

Stop BEFORE actual call 0xCA6348 -> 0xCA94E8, return 0xCA634C. Six consumer frames remain active; consumer, outer 0x5F8EA8, enumeration, factory and helper returns remain pending. NEXT **E011DZ** executes the next original consumer with receiver at outer-entry SP minus 3104 and runtime context at minus 1888. The next exact 1028-byte body is pinned as metadata only; accepted source pins remain 32.

The two scalar cells are writable virtual zero-fill with no file-byte hash authority; only cold zero is accepted by this model. The writable file-initial pair identifies 0x1607180 / 0x1607650, without qualifying pointed tables. Alternate native flags, initialized runtime values, pointed locale/format/string contents, complete consumer output/returns, profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instructions/decompilation/raw records/proprietary names and optical material remain private SP11. Fresh one-shot Windows oracle/external SP7 KD remain authorized with fresh atomic identities and manual-only tasks.

See [E011DY cold runtime context / nested receiver setup](../../experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DX exact constant-data / retained consumer setup accepted

Original source now reads the exact opaque eight-byte window at 0x10F03A0 and enters the original nested consumer setup at 0x7AC38 / 0x7ACA0 / 0x6BDD0 / 0x6BD48. The original 12-byte leaf at 0xEDD0 returns the address 0x17A1150 at 0x6BD70 with exact ABI preservation. No constant contents, pointed strings, formatted result or consumer return fixture substitutes for execution.

All 256 cases pass: 19,200 added original visits, 8,448 exact stack store chunks, 52,224 altered owned requests rejected, 256 exact constant reads and 256 original leaf ABI returns. The 33 setup chunks per case have independently authored source/address/width/value/order contracts. Inherited DW/DV/DU/DT/DS results remain exactly equal and separate; combined original visits are 914,432. The original-entry-to-frontier memory and permissions snapshot remains cumulative.

The constant authority is the exact eight-byte file-backed nonwritable window, not the earlier exploratory 64-byte window. Five exact function bodies extend the inherited 25 source pins to 30. Four consumer frames remain active; their returns and the outer 0x5F8EA8 return remain pending. The original 640-byte destination and published 18,832-byte buffer are still entirely zero. All nine live allocations, callback table, epochs, locks, previous nodes and redzones remain retained.

Stop BEFORE 0x6BD8C, the next eight-byte read from writable virtual zero-fill coordinate 0x17A1150. NEXT **E011DY** establishes loader/runtime scalar authority and resumes the retained consumer. A static zero-fill coordinate is not proof of its native runtime value. Pointed constant strings, complete consumer/outer/factory/helper returns, selected profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instruction text/decompilation/raw records/proprietary names and optical material remain private SP11. Authorized fresh one-shot Windows oracle/external SP7 KD remain available with fresh atomic identities and manual-only tasks.

See [E011DX exact constant-data / retained consumer setup](../../experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DW nested enumeration container / stack clear accepted

Original callee 0x600368 creates a fresh 16-byte object, executes original nested constructor 0x5E81B8 and attaches its returned 64-byte header. Original source creates and clears an 8192-byte array with 1024 zero QWORD slots, then clears a 640-byte stack buffer. No constructed-record, clear or return result fixture substitutes for source execution.

256 cases pass: 151,552 added original visits, 293,632 exact added stores and 26,624 altered owned requests rejected. All 256 nested constructor, 256 array-clear and 256 stack-clear ABI returns pass. Clear visits 122,624 and heap/stack clear chunks 262,144/20,480 are subsets. Inherited DV/DU/DT/DS visits remain separate; combined coverage is 895,232. The original entry-to-frontier memory/permissions snapshot remains exact.

The 16/64/8192-byte leases join six older disjoint live allocations, giving nine. Source constructs exact header/array/owner relations; five header reads have exact contracts. The published 18,832-byte buffer, two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and clears remain retained. Both registry locks remain held, CRT/SRW released. Native allocation, loader/runtime scalar selection, failures/concurrency/teardown and committed stack bounds remain explicit models or open gates.

Stop BEFORE 0x600420, next eight-byte read from 0x10F03A0. NEXT **E011DX** derives exact bounded constant-data authority and resumes the retained original callee. The outer callee return 0x5F8EA8 remains pending; enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DW the nested container proof, E011DV the cold buffer proof, E011DU the callback/epoch proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DW nested enumeration container / stack clear](../../experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DV cold enumeration buffer allocation / publication accepted

Under the declared virtual loader zero-fill scalar model, original enumeration requests fresh 18,832-byte storage, clears it through original source and publishes its pointer at 0x169FDF0 and reference count one at 0x169FDE8. No buffer/clear/publication result fixture substitutes for source execution.

256 cases pass: 237,568 added original visits, 603,136 exact added stores and 11,008 altered owned requests rejected. All 256 actual clear callee ABI returns and the single original entry-to-frontier memory/permissions snapshot pass. Clear visits 233,472 and chunks 602,624 are subsets. Inherited DU/DT/DS visits remain separate; combined coverage is 743,680.

All six allocations remain disjoint and live. Both registry locks remain held; CRT/SRW are released. The two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and prior clears remain exact. Loader scalar selection, allocator success/storage, native resource construction and committed stack bounds remain explicit models. Alternate nonzero scalar branch, native failures/concurrency/teardown and native selection are unqualified.

Stop BEFORE 0x5F8EA4 -> 0x600368, actual return 0x5F8EA8. NEXT **E011DW** integrates this original callee in the retained parent with the published buffer and six allocations. Its exact 1120-byte body metadata is pinned separately; no callee execution is accepted here. Enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DU the callback/epoch proof, E011DT the actual factory/enumeration bootstrap and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DV cold enumeration buffer allocation / publication](../../experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DU existing-table registration / enumeration publication accepted

Original source appends the second cleanup callback to the actual retained one-entry encoded exit table, using its existing 32-slot allocation without reallocation. Original enumeration guard publication advances its guard, global and actual TLS epoch to 80000042; the first-helper guard remains 80000041 and factory guard remains FFFFFFFF in-progress.

256 cases pass: 45,056 added original visits, 9,472 exact added store chunks and 27,392 altered owned requests rejected. All 2,048 original registration/publication callee ABI returns and the single entry-to-frontier memory/permissions snapshot pass. Inherited E011DT adds 127,744 visits and E011DS 333,312, giving 506,112 combined visits; counts remain separated.

Both registry locks and all five allocations remain owned and live. CRT/SRW are released; first callback, 30 unused slots, nodes, redzones, constructed container and prior clears remain exact. Readiness, native allocator construction and committed stack bounds remain explicit inherited models; native failures/concurrency/teardown remain open.

Stop BEFORE 0x5F8E24, four-byte dependency read from 0x1731598. NEXT **E011DV** qualifies this enumeration dependency and its subsequent branch while retaining the two-entry table and actual published epoch. The enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DT the actual factory/enumeration bootstrap, E011DI the separate bootstrap proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DU existing-table registration / enumeration publication](../../experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DT actual-parent factory / enumeration bootstrap accepted

The original factory and enumeration bootstrap now execute in the actual live first-helper parent. The helper's published negative TLS epoch is retained; two fresh 48-byte sentinel nodes remain distinct from its 24/128/256-byte ancestor allocations. Original source initializes 190 fields, clears a 1040-byte stack record and enters enumeration under declared committed-stack bounds.

256 cases pass: 127,744 added original visits and 102,656 added exact store chunks; 333,312 inherited E011DS visits give 461,056 combined visits. Added invalid-contract rejections are 15,104, separate from 43,264 inherited. All actual guard/probe/clear return checks and the single entry-to-frontier memory/permissions snapshot pass.

Both registry locks remain held, SRW/CRT released. Factory and enumeration guards are FFFFFFFF in-progress; neither callee has returned or published its guard. OS/CRT/loader/allocator readiness and committed-stack bounds remain explicit models; native failures/guard-page growth/concurrency/teardown are open.

Stop BEFORE 0x5F94A0 -> 0xCA34A0, actual return 0x5F94A4, callback 0xF7B5E0. Existing encoded exit table contains one callback in 32 slots. NEXT **E011DU** executes this new registration against that nonempty table, then enumeration guard publication and the next dependency. Reuse E011DR registration/publication source and E011DT retained ownership.

E011DM remains the empty RS-query proof, E011DI the separate factory/enumeration proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DT actual-parent factory / enumeration](../../experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DS cached object / nested lock / large clear accepted

The unchanged first helper caches inline object 0x17A4230 at 0x1731880, enters a distinct registry lock through original callbacks, writes bounded header fields and clears all 11,808 bytes at 0x17A4268 through original source. No cache/lock/clear result fixture is used.

512 cases pass: 666,624 original visits, including 345,088 added visits; 301,568 added clear visits are a subset. The large clear contributes 756,736 write chunks, counted separately from 66,560 other nonstack and 49,152 stack chunks. All 86,528 altered owned contracts reject. Whole memory/permissions, source/unmodified loader regions, actual callee returns, padding and the adjacent constructed container remain exact.

Runtime readiness, cold zero control cells and disabled tracing remain explicit models; buffer/padding poison are robustness fixtures. Native OS/CRT/allocator construction, failures/concurrency/teardown and full inline-object initialization remain open. Both registry locks are held; CRT/SRW locks are released.

Stop BEFORE actual call 0x5B8268 -> 0x5BDE08, return 0x5B826C. NEXT **E011DT** integrates this factory callee with the actual live parent, published TLS epoch and existing allocation leases. Positive global-epoch edge cases are not native cold-factory readiness proof. E011DH/DI remain separate factory/enumeration acceptance; E011DM remains the empty RS-query proof.

Full helper/descriptor registry initialization, selected profile/input deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement still precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and missing tools remain authorized; use a fresh atomic identity and preserve private originals/optical material on SP11.

See [E011DS cached object / lock / clear](../../experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DR original cleanup registration / guard publication accepted

The unchanged cold caller registers cleanup callback 0xF7B120 and publishes the helper guard through original code, without registration/guard result fixtures. The encoded exit table contains one callback in 32 slots; global, helper and TLS thread epochs agree.

512 cases pass: 321,536 original visits, including 173,056 CRT registration and 17,920 publication visits. All 62,464 nonstack chunks, 43,520 stack chunks, 5,632 added callee ABI returns and 62,976 invalid owned-contract rejections pass. Whole memory/permissions, immutable source/unmodified loader regions and the exact TLS epoch update are checked.

Loader/OS resource readiness, fresh allocation storage and a ready empty encoded CRT exit table remain explicit owned models. Native CRT initialization, failure/existing-table growth, callback execution/teardown and concurrency remain open. CRT and SRW locks are released; registry logical lock remains held.

Stop BEFORE 0x5B8104, next factory pointer 0x1731880 read at 0x5B8108. Parent/helper remain active. NEXT **E011DS** follows actual factory construction/publication in this caller; source references identify a pointer write at 0x5B8138, outside current acceptance. Full first-helper return and metadata descriptor registry initialization remain open.

E011DM remains the empty RS-query proof, E011DI separate factory/enumeration acceptance and E011DN the limited Windows snapshot. Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, permanent EFI/GRUB and historical repositories unchanged. Windows oracle/external SP7 KD and missing tools remain authorized; fresh boot and atomic identity for another oracle. Originals and optical material stay private on SP11.

See [E011DR registration / publication](../../experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DQ original cold container construction accepted

The unchanged first-helper constructor 0x2EE1A0 completes its normal path and returns at 0x5B9094 with exact ABI. Original source constructs the 64-byte container, 24-byte self-linked sentinel and 128-byte array containing 16 sentinel pointers. Allocation storage/readiness/provenance are explicit owned models; no constructed-object or constructor/helper/guard result fixture is used.

256 cases pass: 65,280 original visits, 13,056 exact nonstack chunks, 12,288 stack chunks and 17,664 invalid owned contract rejections. Whole mapped memory/permissions, source/TLS immutability, allocation redzones/relations and actual constructor/callback/guard return ABI pass. Native allocator, failure/exception cleanup and teardown remain open.

Stop BEFORE 0xCA3450, actual return 0xCA34B0 and callback argument 0xF7B120, after only the four-instruction original registration-wrapper prefix. Parent/helper/wrapper active; registry logical lock held, SRW released and helper guard in-progress. Cleanup registration, helper guard publication, full first-helper return and full metadata registry construction/publication remain open.

NEXT **E011DR** qualifies cleanup registration and original helper-guard publication in this caller. E011DM remains the original empty RS-query proof, E011DN the limited Windows snapshot, E011DI the separate factory/enumeration proof, E011DO initialized-registry reuse and E011DP cold bounds/guard prefix.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DQ container construction](../../experiments/E004-front-ir-vd55g0/e011dq-original-cold-container-construction/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals/optical material remain private on SP11; another oracle needs a fresh boot and atomic identity.

## 2026-10-04 E011DP cold literal bounds / first-helper guard prefix accepted

The unchanged initializer writes uint32 literal bounds 239 and 282, enters first helper 0x5B80A8 and executes its original fresh TLS guard acquisition. No bound/helper/guard result fixture is used; loader TLS and OS lock readiness/operations remain explicit owned models.

128 cases pass: 18,560 original visits, 384 exact nonstack field-store chunks, 4,992 stack-store chunks and 6,528 invalid owned contract rejections. Whole mapped memory/permissions, immutable source/loader regions, actual lock-callback and guard-return ABI pass. The helper body is pinned to 4,104 bytes but only its bounded prefix is accepted.

The stop is BEFORE next dependency 0x2EE1A0, actual return 0x5B9094, pointer argument 0x17A7088 and scalar 65535. Parent/helper frames remain active, registry logical lock held, SRW released and helper guard in-progress. Full helper return, allocation/construction/publication and native OS resource construction remain open.

NEXT **E011DQ** qualifies that unchanged construction dependency and complete first-helper/publication path. E011DM remains the original empty RS-query proof, E011DN the limited Windows ready snapshot, E011DI the separate factory/enumeration proof and E011DO the original initialized-registry reuse proof.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero camera Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DP cold bounds / guard](../../experiments/E004-front-ir-vd55g0/e011dp-original-cold-bounds-helper-guard/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11. Another oracle requires a fresh boot and atomic identity.

## 2026-10-04 E011DO original registry lock / initialized reuse accepted

The unchanged initializer executes its original default EnterCriticalSection/LeaveCriticalSection callbacks and complete already-initialized branch under explicit owned OS/diagnostic contracts. No callback or parent result fixture is used.

64 scenarios pass: 48 complete initialized reuse returns and 16 cold-prefix stops before 0x5DE800. All 6,848 original visits, 112 ABI-exact callback returns, whole mapped memory/permissions and stack checks pass; 2,512 invalid owned dependency requests reject. Nonzero bound fixtures do not prove registry construction. The accepted cold prefix retains its logical lock and active parent frame; cold field stores/allocation/publication are not accepted.

NEXT **E011DP** qualifies cold-bound construction and original first helper 0x5B80A8 (caller return 0x5DE844), plus resource readiness/construction ownership. Selected reader/request/profile, populated RS generation/lifetime and normal AFD input authority remain open. E011DM remains the original empty-RS-query proof, E011DN the limited Windows ready snapshot, and E011DI the separate factory/enumeration proof.

Deterministic selected-input/profile startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. No new camera Start/reboot/kernel build/production C change; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DO lock / reuse](../../experiments/E004-front-ir-vd55g0/e011do-original-registry-lock-reuse/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; SP11/SP7/PiMaster only. Windows oracle/external SP7 KD boots and tools remain authorized; originals/optical material stay private on SP11. Fresh boot and atomic identity for another oracle.

## 2026-10-03 E011DN Windows registry boundary observed

The accepted evidence is a 116-byte rear-reader-ready metadata snapshot before Start: bound/descriptor populated, seven runtime tag cells zero, and live platform callbacks equal the file default targets. Source references identify writer 0x5DE700; full initializer execution is still unqualified.

Two distinct atomic holder identities ran in one Windows boot, stopped/disposed successfully and counted 69 / 449 valid 4K handle acquisitions. A is excluded from RS qualification after observer command/filter issues. B captured only the registry snapshot; zero RS copy hits does not prove reader/query execution or general RS absence. No pixels were saved. This is not isolated-boot hardware or populated-record lifetime acceptance.

Golden return passed: payload hashes, permanent EFI/GRUB and historical repositories unchanged; Windows read-only recovery unmounted, temporary tasks removed, debuggers/holders closed. No production camera C/kernel change or Linux power-policy change.

NEXT **E011DO** qualifies original metadata registry initialization, allocation/descriptor ownership and the selected normal request/profile path before another fresh-boot oracle. E011DM remains the latest source empty-slot query proof, E011DI the separate factory/enumeration proof. Normal AFD input authority, deterministic startup/input/profile integration and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open; native rear runtime remains denied.

See [E011DN boundary](../../experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster connects SP11 Linux/Windows and SP7; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11.

## 2026-10-03 E011DM original query through selected empty slots accepted

The original reader, metadata query and selected-slot helper now execute together without query or slot-helper result fixtures for declared empty slots. All 18,816 queries return actual null records; missing RS preserves the prior 132-byte source record.

640 scenarios / 1,920 cold/warm/stale-thread reader calls pass. Added query/helper coverage is 2,916,480 original instruction visits; inherited reader/tag/guard coverage is counted separately. All 356,608 altered dependency bindings reject in the owned harness contracts. Entire nonstack memory/mapping state, immutable source/pool/slot objects, preserved ABI and stack redzones pass.

The normal path selects node+490, uses pool capacity+278 and the inline pointer array+298, with selector modulo capacity. TLS block+138 is a scalar request selector; the original reader's ninth query stack argument is zero. Registry/settings/node/context/pool/empty-slot construction and standard OS resources remain explicit owned models.

**Still open:** actual selected registry values and metadata registry initialization, populated-record identity/generation/lifetime, normal AFD H/V counts and whole-frame zero-offset producer. Private populated-slot exploration reaches 5DF780 -> 5C0A58 and image+17350E0; it is excluded from acceptance. NEXT **E011DN** resolves that selected dependency and populated RS ownership, then normal AFD policy.

Selected input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Separate factory/enumeration acceptance stays E011DI; native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DM empty-slot query](../../experiments/E004-front-ir-vd55g0/e011dm-normal-rs-empty-slot-query/README.md). Earlier current/NEXT paragraphs below are historical. User authorizes Fabric or PiMaster, one-shot GRUB Windows oracle/external SP7 KD boots and missing-tool installation. Hosts SP11/SP7/PiMaster; originals and optical material stay private on SP11.

## 2026-10-03 E011DL original runtime statistics tag initialization accepted

The actual reader's guarded first-use path now produces all seven runtime tags from declared registry fields, including RS slot5, with no tag-vector or guard-result fixture. Unchanged CRT acquisition/publication bodies execute in the real reader caller. Warm and stale-thread calls preserve published tags despite altered registry inputs.

192 scenarios / 576 reader calls, 1,344 exact tag-field stores, 5,376 initializer-path instruction visits and 76,224 rejected dependency bindings pass. The 262,848 total original visits include inherited reader/guard coverage; this is bounded emulation, not camera hardware acceptance. Entire nonstack memory/mapping state and preserved ABI/stack redzones pass.

**Still owned models:** registry values/objects, settings, metadata-query results and OS SRW/CV resources. Actual query body, selected pool/record lifetime and normal AFD count/offset policy remain open. NEXT **E011DM** resolves those dependencies, reusing E011DK copy/decoder, E011AM arithmetic, E011M initial defaults and E011AK sampled unity binding.

Required input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Latest selected RS source acceptance is E011DL; separate factory/enumeration acceptance stays E011DI. Native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DL tag initialization](../../experiments/E004-front-ir-vd55g0/e011dl-normal-rs-runtime-tag-initialization/README.md). Earlier NEXT/current statements below are historical. User reaffirmed autonomous one-shot Windows oracle/external SP7 KD boots and missing-tool installation on 2026-10-03; preserve Golden and same-SP11 private originals.

## 2026-10-03 E011DK RS metadata copy and C decoder accepted

The original RS metadata reader passes 96 present/absent/fallback cases and 39,904 instruction visits. The new checked C decoder reuses E011AM arithmetic, matches three observed records and 42 input/output fields per compiler, and rejects 21 invalid or unsupported inputs before output effects under GCC/Clang ASan/UBSan. All 132 copied bytes, owned heap changes, source immutability, original code, stack and caller state pass.

This closes the consumer/decoder contract only. Query/helper results, registry/settings/TLS/locks and runtime property tags are explicit owned fixtures. Actual tag initialization, metadata query/record publication and upstream AFD normal count policy remain open. Missing metadata preserves the prior source record; the decoder supplies no guessed defaults.

**NEXT E011DL:** follow RS tag cell 17A30F4, slot-5 query 5D4D30 and actual upstream normal count/offset publisher. Reuse E011M initial counts, E011AM numerical binding and E011AK sampled unity BG gain proof. Required selected input/profile integration, deterministic bootstrap/preflight and independent enabled-output DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate.

Latest selected RS source acceptance is **E011DK**; the separate original factory/enumeration branch remains **E011DI**. Native rear runtime remains denied. Zero camera Starts, reboots, kernel builds or optical tests here; Golden unchanged. See [E011DK metadata input](../../experiments/E004-front-ir-vd55g0/e011dk-normal-rs-metadata-input/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 E011DJ input ledger accepted; E011DK normal RS policy next

The checked selected-baseline ledger covers all 14 register-state members, five DMI families and ten replay input blocks. It reuses 15 bounded proof facts, pins 55 authored files and rejects eight invalid ledger mutations. This is source/evidence inventory; no new numerical, emulation, optical or hardware test.

Initial Titan680 RS defaults, immediate AEC BG producer lineage and AWB pre-request seed/writer lineage are already proven. Normal RS count/override authority, selected normal input/profile bindings and independent enabled-output retirement remain open. NEXT **E011DK** follows the actual normal RS pre-adjustment writer upstream of A0DFC0; reuse E011AM arithmetic/binding and E011M initial defaults. Continue generic factory/registry work only for a named selected-baseline dependency.

Latest original emulation remains E011DI. Native rear runtime remains denied; Golden unchanged. See the checked [input ledger](../../experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 evidence audit and next product gate

Latest accepted source checkpoint remains **E011DI**; native rear runtime remains denied. Earlier live front native ISP, front/rear RAW and ordinary-app/software fallback capture are retained. E011AM has zero-difference offline startup parity; E011AR is a compiled packet-isolated runner; E011AS/AV/BW supply specific cold policies. Complete deterministic startup and physical buffer retirement remain open.

**NEXT E011DJ first builds the selected-baseline input/dependency ledger**, reusing closed producers and identifying remaining normal RS count/whole-frame offset and other required normal-input authority. Continue the private registry/factory trace only for a named baseline consumer/lifetime dependency. Then integrate source-only preflight, independently prove IRQ/exact-buffer/DMA/IOMMU retirement, and target the existing eight-fresh-frame front/rear/off clean-colour app milestone. Optional effects/catalogue and protected IR/Hello remain deferred. Runtime/default promotion gates are unchanged.

Windows BF events were already live-observed in E005o; exact hardware retirement is still open. Older software-first, black-scene and historical NEXT paragraphs are snapshots, superseded by this audit for current priority. Report added coverage separately from inherited regression totals.

See [camera evidence audit](../../docs/CAMERA-STACK-AUDIT-2026-10-03.md) for evidence tiers, corrected status and acceptance gates.

## E011DI original enumeration bootstrap — BOUNDED PASS

Thirty-two cases continue the verified factory VM into original5F8DC0: combined15,936 original instructions,12,832 exact store chunks and3,488 rejected requests. Added enumeration proof contributes2,560 /1,024 /1,536.

Original stack helper1440 uses the actual112-byte initial frame and source5920-byte additional request under explicit already-committed stack bounds. Original CE7AD8 runs through second caller5F9460/guard1B30320, claimsFFFFFFFF and preserves its actual caller with balanced logical SRW ownership. Source code clears all56 bytes at169FE00. Whole memory/permissions/source reads/stores retain both48-byte records, typed owners and the1040-byte receiver.

The stop is BEFORE5F94A0→CA34A0 with callback argumentF7B5E0. Registry body/result, OS guard-page growth, file enumeration/completion/full parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/stack/native OS/allocator/canary fixtures remain explicit.

NEXT **E011DJ** follows original callback registry CA34A0/CA3450 and then enumeration completion/file provenance. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DI](../../experiments/E004-front-ir-vd55g0/e011di-original-enumeration-bootstrap/README.md).

## E011DH original factory initialization and1040-byte clear — BOUNDED PASS

Thirty-two cases across stack/node placements, loader indices, negative epochs and original/D7-canary field states execute13,376 original instructions,11,808 exact store chunks and1,952 invalid requests rejected before effects.

Original factory code clears190 image field chunks. Original F5E600 now executes through source call5BE9F8, zeros1040 bytes at incomingSP-1144 and returns destination to5BE9FC with its actual caller preserved. Its result fixture is absent. Whole mapped memory, actual permissions, exact scalar/vector/source writes and reads, both full48-byte records and logical SRW/allocation ownership pass.

The accepted stop is BEFORE5BE9FC→5F8DC0. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator/native OS models and D7 robustness fixtures are explicit. File enumeration, full factory completion/parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DI** follows original file-enumeration routine5F8DC0 through its actual caller and source-created1040-byte stack record. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DH](../../experiments/E004-front-ir-vd55g0/e011dh-original-factory-initialization-clear/README.md).

## E011DG original factory two-record construction — BOUNDED PASS

Sixteen cases across four stack/node placements, two owned loader indices and two negative cold epochs execute1,712 original instructions,672 exact store chunks and816 invalid requests rejected before effects.

Actual factory guard caller checks remain intact. Original call instructions5BE698/5BE6CC request two48-byte allocations under typed owned success models; original source then constructs and publishes both full records, with three self-pointers, two-byte257 and22 zero bytes each. Whole mapped memory, actual permissions, source reads/stores, logical allocation/SRW ownership and actual guard caller preservation pass.

The accepted stop is BEFORE5BE6F4. Allocator/native OS bodies, failure cleanup, full factory parent return/completion/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator fixtures are explicit.

NEXT **E011DH** follows original factory data initialization and library boundary, then file enumeration/context/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DG](../../experiments/E004-front-ir-vd55g0/e011dg-original-factory-two-records/README.md).

## E011DF original factory cold prefix and actual startup guard caller — BOUNDED PASS

Sixteen cases across four stack placements, two owned loader indices and two negative cold epochs execute 1,344 original instructions, 352 exact store chunks and 640 invalid requests rejected before effects.

Original factory5BDE08 now calls original CE7AD8 at5BE67C with actual guard1B302D0; it returns to5BE680 with actual guard caller SP/nonvolatile registers preserved and balanced logical SRW ownership. Original code changes the guard0→FFFFFFFF and clears three factory initialization fields. Whole mapped memory, actual permissions, exact source reads and independent store models pass.

Each case stops BEFORE allocator call5BE698→CAE740 requesting48 bytes: 84 instructions executed, with the stop call excluded. Owned loader/TLS/negative epochs/file-BSS state/native OS models remain explicit. Full factory parent return, allocation/construction/completion, Default/full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DG** qualifies the exact48-byte allocation boundary and original factory construction, then context/file enumeration/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DF](../../experiments/E004-front-ir-vd55g0/e011df-original-factory-guard-prefix/README.md).

# SP11 camera stack readiness

## E011DE original standalone startup-guard sequence — BOUNDED PASS

Sixteen scenarios cover four placements, two owned loader indices and two epochs across fresh initialization, completion and cache refresh. All48 original helper phases pass: 1,504 instructions, 304 exact store chunks and 1,168 invalid requests rejected before effects.

Original CE7AD8 claims first initialization with guardFFFFFFFF. Original CE7A48 increments epoch1607B04 and updates the guard/TLS+16; the original initialized path refreshes a stale TLS epoch. Whole memory, actual permissions, logical SRW resource order and original caller SP/nonvolatile registers pass.

Loader/TEB/TLS/SRW/CV readiness and void OS dependencies remain explicit owned models. Native OS bodies/bytes, concurrent waiting and actual factory/Default production remain open. This standalone proof is not yet joined to factory5BDE08 and its source guard1B302D0.

NEXT **E011DF** joins the original runtime guard to its exact factory caller, then resolves file enumeration/context receiver/RootOpsinput+72 and full startup/preflight/RS. Independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DE](../../experiments/E004-front-ir-vd55g0/e011de-original-startup-guard-sequence/README.md).

## E011DD original root reference-release component — BOUNDED PASS

Sixteen isolated cases at four placements cover null roots and references1/2/41. Twelve first execute original fresh-root construction. The source release branch decrements references, retains nonfinal roots and calls the typed OS root+8 deletion and sized176-byte release only for the final reference, then clears global1798458.

Combined construction/release: 2,004 original instructions, 616 exact store chunks and 464 invalid requests rejected before effects. Whole memory, actual permissions, logical resource order and paused register restoration pass. Held-lock and competing-user states also reject before effects.

This is the interior source component290988..2909D4, not a full parent destructor or parent ABI return. Native OS/allocator bodies, concurrent retry, failure cleanup, live caller ownership and hardware retirement remain open. No cleanup is appended to retained E011DC camera outputs.

Provider input+48 and RootOps candidate input+72 are distinct. Context+9552 is not established as the registered camera callback. Cold factory startup reaches an unqualified runtime helperCE7AD8 at5BE67C under guard1B302D0; actual Default/factory/context receiver production remains open.

NEXT **E011DE** resolves that source runtime/factory/Default consumer, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DD](../../experiments/E004-front-ir-vd55g0/e011dd-original-root-reference-release/README.md).

## Historical software-first proposal — superseded

The earlier software-first proposal was superseded by the user's native Qualcomm ISP decision on 2026-09-23 and clean front/back baseline scope in E011BS. E004ne remains a bounded opt-in software fallback/reference, with later structured rear-scene and supported-control evidence; native rear ISP and matched Windows optical parity remain open. Historic percentages are unmeasured planning estimates. See [RGB-PHASED-ROADMAP.md](RGB-PHASED-ROADMAP.md) and the current audit above.

## Promotion decision

**Hold full 1:1 default promotion.**

The canonical hardware package and bounded RGB application transport/lifecycle tests remain accepted. E004ne subsequently demonstrated a structured rear scene, supported controls, front1080p/rear4K near30fps source and ordinary-app negotiation. Persistent daily service, complete deterministic native-ISP startup, independent enabled-output retirement, chosen-route decoding/colour and matched Windows image quality remain open. Protected IR/Hello is separately deferred and does not gate the selected normal front/back baseline. Linux system suspend/hibernate remains prohibited; its absence is not a camera failure.

## Ready now

- unified rear RGB + front RGB + IR device-tree authority;
- exact canonical CAMSS, IMX681, OV13858 and VD55G0 module set;
- simultaneous three-sensor bind;
- Windows-exact CSIPHY0 IR receiver programming/readback (96/96);
- rear RGB exact colorbar + normal streaming under the three-camera authority;
- front RGB production R27 streaming with Windows-authoritative IQ/AWB behavior under the same authority;
- same-boot rear→neutral→front handoff from the canonical installed package;
- deterministic package build/staging;
- bounded install/update/uninstall and real-filesystem lifecycle with zero activation side effects;
- maintained offline Windows-exact protected worker source and exact SecurePD proxy/native ABI.

The non-protected hardware package supports **guarded, bounded non-default experiments**. This is not a complete daily-use RGB application stack.

## Current RGB application evidence (2026-09-21)

E004kr extends direct transport to front1080p:1800distinct app frames at30.0247fps, source30.0061fps over60s. Intentional SIGTERM/STREAMOFF, exited processes/readers and neutral graph passed before a short rear120app-frame session and the same controlled stop. Both sampled images were nearly black. This proves bounded transport and planned cancellation/handoff, not calibrated image quality, arbitrary reopen or permanent daily service. OS system standby/resume remains expressly excluded from camera tests. E004kr is consumed and retired on Golden.

E004kp subsequently removed the rear RAW/NV12 pipes and separate publisher, using direct mmap capture and V4L2 output with unchanged pixels. Rear2400sources achieved29.9496fps over80.101s and1800distinct app frames achieved30.0684fps over59.830s; source gaps0, one Gst offset gap, clean neutral shutdown and Golden return. This closes the bounded rear throughput gap, not day-long reliability or calibrated image quality. Front remains at E004km throughput pending direct transport.

E004km delivered1800 complete distinct front1080p and rear4K frames to independent standard V4L2/GStreamer applications in sequential sessions. Source2400frames each had no sequence gaps. Front app26.9873fps and rear app13.7766fps are observed over different source/app windows, not30fps parity. Both sampled scenes were dark; no calibrated scene comparison exists. The front path is a separate pRAA RAW10 software proxy, not a QC10C decoder or Windows ISP replacement. E004km is consumed, retired and returned to Golden. Historical hardware/IQ-control claims below do not establish end-to-end image quality.

## E004lz maintained physical RGBSession integration (2026-09-23)

New distinct safeguarded one-shot physically PASSED the MAINTAINED
RGBSession + exact 119-link Media Controller and ordinary source
publisher backends. Front1080p 448 and rear4K 446 full contiguous
software RAW→NV12 source/app-compatible frames, 0 source sequence
gaps. Both ordinary uid1000 endpoints completed three separate
120-frame normal app processes and an intentional client kill
followed by recovery under the SAME source publisher invocation.
Stop143/STREAMOFF, complete real neutral→front→neutral→rear→neutral
graph, lease and independent FD release passed. Golden returned and
E004lz boot/services/assets retired, consumed and documented in
e004lz RESULT/CONSUMED/evidence. It was FINITE ~15s per camera,
not a persistent/daily-user service or unlimited-client proof.
Both sampled images remained near-black meanY≈16, meaning real
controlled-lit exposure, image quality and Windows ISP parity are
still UNPROVEN. E004ly independently proved ~115s per camera with
the prior separate scripted route rather than this new controller.

## E004mc paired RAW source versus NV12 image diagnosis (2026-09-23)

**Source RAW10 upper-eight-bit photosite samples are themselves
near-black:** on four same-source-frame pairs per camera, front
source p99=19 versus converted NV12 Y p99=18; rear source p99=16
versus NV12 Y p99=16. The converter alone does NOT explain a
bright captured source going black. Independent front1080p and
rear4K app probes still showed no distinguishable spatial scene
contrast; image quality is NOT ready for an ordinary RGB release.
Ambient/occluded scene, actual sensor exposure/gain effect and
upstream source format remain unresolved. Sensor controls were
read but not written in this test. Physical root selector, app
lifecycle, STREAMOFF, full native graph neutral, IR-off and Golden
return PASSED. E004mc is retired and CONSUMED; never reuse.
Next: bounded, supported sensor control response with the paired
RAW8/Y scalar diagnostic under a NEW guarded one-shot identity,
not OS standby or speculative register programming.

## E004mb real morning-light RGB detail check (2026-09-23)

**Image quality is now an observed release blocker, not just
uncalibrated:** real 90-frame ordinary-app front1080p and rear4K
probes under morning corner light produced front mean Y~16.3,
p99 18 and rear mean Y~16.0, p99 16, with negligible spatial
contrast. Neither camera produced statistically distinguishable
scene detail. Current V4L2 sensor controls stayed at their
fixed readback values; this test made NO exposure/gain writes.
The source RAW signal and physical light at each lens remain
unmeasured, so do NOT claim scene darkness alone explains this
or that the software converter is definitely at fault.
Bounded root selector, independent apps, stop/STREAMOFF and
Golden return all passed; one-shot consumed/retired.
Next finite safely guarded test: paired RAW source versus NV12
scalar histogram and controlled supported-exposure engineering,
NO IR or OS system sleep.

## E004ma root-private RGB selector (2026-09-23)

An independent guarded one-shot proved the maintained root Unix-socket
selector commands front→rear→off→quit on real native CAMSS, front1080p /
rear4K NV12 ordinary uid1000 V4L2 clients. Three normal 120-distinct
frame app openings and intentional SIGKILL/recovery per camera retained
the same publisher. Both returned to native graph neutral with IR off;
Golden recovered, candidate retired/consumed. This closes *bounded
physical selector control*, not persistent everyday camera installation.

Both front and rear sampled luma Y ~16. A genuinely distinguishable
scene, correct exposure, dynamic range, colour and calibrated image
quality remain unproven despite successful real optical frame delivery.
Next: guarded finite daylight/low-light RAW-vs-Y in-memory scene
diagnosis; no user-image archive, IR or system sleep.

## E004ly guarded high-resolution software publisher trial (2026-09-23)

Independent fresh one-shot real hardware front1080p and rear4K
RAW10→NV12 opt-in continuous source publisher proof PASSED.
Front captured/published 3452 frames over 115.004s; rear 3444 over
114.957s, both zero source-sequence gaps. Each standard V4L2 endpoint
remained discoverable and ordinary uid1000 apps completed first,
reopen and post-SIGKILL recovery (three normal 120-frame app opens)
under the SAME publisher invocation. Intentional planned 143 stop
verified STREAMOFF; all camera users closed and complete native
media graph neutral between cameras and after rear. IR off, Golden
returned safely; candidate retired and identity consumed.
See e004ly RESULT.json/CONSUMED.json/evidence.

**Not a finished daily camera service:** two separately bounded
~115s publishers; maintained RGBSession state-machine still
source-only rather than live integrated; general multi-client
session ownership, production installation, extended uninterrupted
operation, light/exposure/image quality and matched Windows visual
parity remain unresolved. Both scenes sampled nearly black. The
separately proven 640x480-XRGB8888 libcamera processed path must
not be conflated with this 1080p/4K RAW→NV12 software path.

## E004lx guarded processed RGB soak and reopen (2026-09-23)

A new single-use, isolated root-sealed libcamera v0.7.0 test delivered
3600 real processed 640x480-XRGB8888/sRGB frames in FOUR independent
front→rear→front→rear processes (900 contiguous frames each). All four
had no observed sensor-control errors and each returned the COMPLETE
native media graph to neutral after app exit. Each had 889 steady
intervals after the first ten with no >250ms gap. First front/rear
openings had no large early gap; reopened front and rear each had one
~1s startup pause (999185us and 966638us). The previous E004lw
all-interval strict validator rightly failed on this pause; E004lx
separately reports startup vs steady cadence and does NOT claim
seamless switching. This proves bounded 2-minute processed transport
and clean independent reopen/neutral shutdown, not permanent daily
operation, native full-resolution processed RGB or Windows ISP parity.
Root-only experimental access is NOT general OS-enforced multiclient
ownership. The one-shot boot/service/private build is consumed and
retired, Golden recovered unmodified; no live camera on Golden.
See E004lx RESULT/CONSUMED/evidence.

**Next RGB product gate:** build a non-default, opt-in, independently
owned and recoverable RGB camera service with simultaneous selectable
front/rear *published* endpoints or equivalent verified ordinary-app
handoff. Verify actual libcamera-processed output through normal
unprivileged app readers and clean stop/reopen, investigate the
repeatable ~1s early-frame interruption, then validate acceptable
processed resolution and controlled-light image quality. GStreamer
libcamerasrc, videoconvert and v4l2sink are installed on Golden and
a synthetic 120-frame BGRx640x480→NV12 conversion passes offline;
this is ONLY a bridge prerequisite, not a live camera-to-loopback
or ordinary desktop client proof. Do not activate experimental camera
devices on protected Golden.

**OS sleep exclusion:** user reports SP11 Linux standby/suspend/resume
is not reliably implemented and may crash the whole OS. Never put it
into system sleep for a camera test. Normal guarded reboots and
powered-on camera open/stop/reopen tests remain authorized. Sensor
runtime-PM idle checks are distinct from OS system sleep.

## Not honestly complete yet

### Protected IR / Windows Hello

The protected provider, CPZ sample backing, FastRPC FD handoff lifetime, SecurePD worker ABI and worker implementation are mechanically closed. The exact worker is still unsigned and cannot be admitted by the production SP11 CDSP trust policy using any credential or signing service currently available to this project.

This is an external trust/admission blocker, not missing Linux algorithm code. Do not weaken verification to get runtime output.

### Front post-G3 changed native feedback — CLOSED by E004en

The original scene-gated evidence gap was resolved in E004en on
2026-09-15. The single, consumed one-shot ran 27 front-RGB frames and
observed one naturally changed post-G3 native tuple applied to IMX681
at source G4/request7 for effect at G7. It used no synthetic control
delta, second later write or same-boot camera rerun. The candidate was
retired and returned to protected Golden Linux. The earlier cap-active
observation remains historical context, NOT a current blocker. Do not
repeat the consumed E004en identity or demand another scene change.

### Native front-IR illumination and offline face processing — SEPARATE BLOCKED PATH

E004fu demonstrated 16 live ambient/unilluminated VD55G0 optical captures,
but the steady grayscale signal was low (mean 38.6–39.7/255, max 48)
and NOT validated for facial authentication. E004hi/HZ/IA demonstrate
an uninstalled ordinary Linux HLOS pixel/transaction/public visible-light
YuNet/SFace diagnostic; public-fixture inference is neither live VD55G0
near-IR face validation nor Windows Hello security or protected processing.

E004ge still lacks calibrated optical radiometry, measured electrical/
optical pulse and current, independently verified stuck-high strobe/
host-failure autonomous LED-off, physically reviewed hardware cutoff,
and exact wiring/routing evidence for native Linux IR illumination.
The discovered idle PMIC timer 0x93 is not that physical proof. Do NOT
enable native IR illumination, enroll a user or attach this offline
prototype to PAM/login on the strength of software and register evidence.

Protected Windows Hello parity is separately blocked by legitimate
production SecurePD worker signing/admission; neither a nonprotected
HLOS image nor weakening trusted-worker verification can replace it.

## Default rule

Do not make the current package the project's final 1:1/default camera stack until the protected IR/Hello admission blocker is resolved and its end-to-end runtime passes. A separate user decision could still choose the proven RGB/non-protected subset as a convenience default, but that would be a product-policy choice, not proof of complete Windows parity.
