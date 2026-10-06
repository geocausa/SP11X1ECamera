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


## 2026-10-04 E011EG source-qualified CRT startup order / lowIO-to-stream handoff accepted

The actual process-attach source path now closes the startup-order gap without copying the separate E011EF context. Before the constructor iterator can reach `0xCB3260`, original CRT startup must complete the forward subsystem table at `0xF8BA20..0xF8BB20`. Pair eight is `0xCB5DD0 / 0xCB5E20`; successful `0xCB5DD0` requires original `0xCC06F0` index zero to return success. Only afterward does the constructor iterator walk `0xF7F440..0xF7F468`, whose first non-null entry is `0xCB3260`.

This proves the conditional source order **`CC06F0` before `CB3260` whenever process attach reaches the stream initializer**. The accepted E011CM producer/consumer matrix was rerun: all 8 cases passed with zero stderr. Its default cases create the 64×72-byte lowIO table at `0x16A2A90`, then the 512-entry stream vector at `0x16A2A58`, link three static stream objects and return. The startup lowIO-to-stream handoff and complete stream-initializer return are therefore qualified within the inherited owned OS contracts.

E011EF's `0xCC08E8` path remains valid but separate and is **not** used as this startup producer. Native CRT success, loader internals, allocator internals and Windows mutex bytes/concurrency remain unproved. The retained camera caller is still separate before `0xCC6120` reads `0x16A2A58`; no camera-state join is claimed.

NEXT **E011EH** source-qualifies startup stream-vector lifetime/order to that camera caller, then resumes the dependency read only if the original path supports it. File/provenance, full helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied; rough ~70% smoke estimate remains unchanged.

Zero camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories remain unchanged. See `experiments/E004-front-ir-vd55g0/e011eg-source-qualified-crt-startup-order/`. Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EF low-level I/O count transition / initializer return accepted

The isolated original lowIO initializer now completes its cold owned-count path: source reads zero from 0x16A2E90, writes 64, enters record zero through the original wrapper, sets its active byte, releases the global index-seven lock and returns zero with exact NONVOL/SP.

256 cases pass: 9,472 added original visits, 512 exact source stores, 14,080 altered owned requests rejected, 1,280 exact dependency reads, 512 wrapper entries, 512 owned API calls and 256 exact initializer returns. Every E011EE ancestor row remains equal; memory/permissions and redzones match without resets. Forty-nine execution pins remain exact.

This proves the isolated cold path and return, not native count selection, native CRT/handle state or loader startup ordering. The first record logical lock remains held and the global initializer lock is released. The stream initializer still remains before 0xCB3338 / 0x16A2A90, and the camera remains before 0xCC6120 / 0x16A2A58. No state join is claimed.

NEXT **E011EG** establishes actual loader/CRT ordering and only then attempts a source-qualified lowIO-to-stream handoff. Full stream/camera state joining, file/provenance, helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EF lowIO count / initializer return](../experiments/E004-front-ir-vd55g0/e011ef-original-lowio-count-activation-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EE isolated original low-level I/O block publication accepted

The low-level table pointer at 0x16A2A90 now has a source-qualified producer prefix in a third, isolated emulator. Original initializer 0xCC08E8 acquires its owned index-seven lock, takes the explicitly owned cold pointer-zero branch, and calls original constructor 0xCC05B8. The constructor requests 64 records of 72 bytes, initializes each record through checked source stores and owned resource successes, returns the 4,608-byte block with exact NONVOL/SP, and original 0xCC093C publishes it.

256 cases pass: 738,304 added original visits, 169,728 exact ordered source-store chunks, 1,206,784 altered owned requests rejected, 33,280 exact dependency reads, 17,152 nested entries/ABI returns, 256 owned zeroed allocations and 16,640 owned API calls. Every complete E011ED row remains equal. Camera and isolated stream-initializer memory, permissions and frontiers remain unchanged; the new low-level initializer's entry-to-frontier memory/permissions and redzones match without resets. Forty-eight execution pins remain exact.

All 64 record resources are logically ready in the owned model. Each source record has an eight-byte all-ones field at +40, zero at +48, checked four-byte value 0x0A0A0000 at +56, byte ten at +60 and zeros at +61..+66; the remaining bytes stay owned-allocation zero. This proves neither native critical-section bytes nor valid native handles. Allocation and API success are explicit provider inputs; original allocator internals and native CRT initialization remain unproved.

Stop BEFORE 0xCC0948 reads four bytes from image+0x16A2E90, at lowIO-entrySP-96. NEXT **E011EF** establishes this runtime input before continuing the low-level initializer. The block constructor returned, but the low-level initializer has not returned and its logical lock stays held. Actual loader startup ordering and any joining of the three contexts remain unqualified. The stream initializer separately remains before 0xCB3338 / 0x16A2A90 at stream-entrySP-80; the camera separately remains before 0xCC6120 / 0x16A2A58 at outer-entrySP-1648.

Camera output, nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,989,120 includes two isolated initializer matrices and is not a joined trace. Full initialization/state joining, file/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EE isolated low-level I/O block publication](../experiments/E004-front-ir-vd55g0/e011ee-original-isolated-lowio-block-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011ED isolated original stream-table publication prefix accepted

The runtime pointer at 0x16A2A58 has an original publisher: initializer 0xCB3260. Its prefix now executes in an isolated fresh emulator with explicit owned cold count/pointer inputs. Original source sets 512 slots, requests a 4,096-byte zeroed allocation, publishes the returned pointer, initializes the first logical standard-stream resource and writes image+0x1607060 into slot zero. The remaining 511 slots stay zero. Native allocation, CRT resource initialization and pointed stream contents remain unproved.

256 cases pass: 13,056 isolated original visits, 4,096 exact ordered source stores, 36,096 altered owned requests rejected, 1,024 dependency reads, 512 nested entries/ABI returns, 256 owned zeroed allocations and 256 owned resource-model calls. All E011EC rows remain equal; camera memory, permissions and its 0xCC6120 frontier remain unchanged. Isolated initializer entry-to-frontier memory/permissions and redzones match without resets. Forty-six execution pins remain exact.

Original 0xCB1650 returns zero on its null cleanup path. Original 0xCBA4B0 tail-calls the owned InitializeCriticalSectionEx model at resource 0x1607090 with spin count 4,000 and flags zero; both nested returns preserve NONVOL including SP. Model success and readiness remain explicit provider inputs, not native observations. The camera and isolated initializer states have not been joined.

Stop BEFORE 0xCB3338 reads eight bytes from image+0x16A2A90, independently checked index zero; current SP=initializer-entrySP-80. NEXT **E011EE** establishes the low-level I/O table's authority before continuing. The initializer remains active; full return and actual loader/CRT startup invocation are pending. The camera caller separately remains at 0xCC6120 / outer-entrySP-1648, with four active stream frames and its owned stream lock held.

Camera output, all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,250,816 includes the isolated initializer matrix and does not describe a joined trace. File/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011ED isolated stream-table publication prefix](../experiments/E004-front-ir-vd55g0/e011ed-original-isolated-stream-initializer-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EC bounded stream setup / owned CRT lock accepted

Original caller 0x600368 resumes with the completed formatter result and enters wrappers 0xCED2F0 / 0xCED0D8 / 0xCC6078 / 0xCC6108. The exact 37 private bytes plus 603 zeros remain intact. A pinned two-byte mode literal at 0x1363D40 qualifies the original first-byte nonempty gate; mode interpretation, stream selection and file contents remain open.

256 cases pass: 13,824 added original visits, 4,608 exact ordered stack stores, 37,632 altered owned requests rejected, 256 immutable mode reads, 256 inherited loader-binding reads, 1,280 exact callee entries, 256 lock-wrapper ABI returns and 256 owned lock-model calls. No allocation runs. Complete E011EB rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,237,760, with ancestor counts separate.

Original 0xCB7300 derives a critical-section request at 0x16A3000 using the inherited import binding. Its owned EnterCriticalSection model requires exact caller, argument, SP, readiness and initially unheld state; both OS-void X0 clobber cases preserve the wrapper's saved NONVOL/SP. The new stream lock model is held. Earlier publication CRT/SRW locks remain released. This does not prove native CRT resource initialization or synchronization.

Stop BEFORE 0xCC6120 reads the runtime stream-table pointer at image+0x16A2A58 / eight bytes, current SP=outer-entrySP-1648. Four stream frames remain active with pending returns 0x600454 / 0xCED330 / 0xCED150 / 0xCC60A0. NEXT **E011ED** establishes this runtime dependency's authority before continuing. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

Forty-four execution pins retain all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks. Native runtime scalar/pointer selection, native CRT resources, file/provenance collection, full helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EC bounded stream setup / owned CRT lock](../experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EB complete selected formatter output / consumer returns accepted

Original source completes the selected three-argument formatter with lengths 12 / 1 / 24, exact 37 private bytes, and original terminators at output indices 37 and 639. The retained 640-byte destination has 603 zero bytes after the output. All seven inherited consumer frames return to their actual callers with exact NONVOL including SP; their stack contexts and cookie scratch slots retire after proof. No output or result fixture is supplied or exported.

256 cases pass: 199,680 added original visits, 30,464 exact ordered store chunks, 221,952 altered owned requests rejected, 7,936 immutable reads, 4,096 ordinary callee ABI returns, 1,792 inherited consumer ABI returns, 512 cookie-push and 768 cookie-pop convention returns. All complete E011EA rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,223,936 with ancestor counts separate.

Remaining literal authorities cover 0x10F03B0 / 16 bytes and aligned 0x13F1F20 / 48 bytes, with the second literal at offset eight. One sparse cell at 0xF8B230 and the 304-byte cold cleanup body at 0xCA8658 are pinned. Forty execution pins retain inherited runtime initial-value models. Signed write-hook values normalize to the exact unsigned word before comparison; original execution and effects remain unchanged. Cookie conventions remain SP-16 / SP+16, distinct from SP-preserving leaves or OS stack-growth proof.

Stop BEFORE actual caller instruction 0x600440 inside 0x600368, SP=outer-entrySP-1456 and X0=37. No consumer frames remain active. NEXT **E011EC** continues this caller with the completed output and all ancestor ownership retained. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, full helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied; guarded smoke remains pending and the rough ~70% estimate is unchanged.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EB complete selected formatter / consumer returns](../experiments/E004-front-ir-vd55g0/e011eb-original-complete-constant-consumer-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EA original first argument length / copy accepted

Original source now finds the first argument's NUL in an immutable 13-byte literal, reads its exact 16-byte window, and copies twelve private bytes into the retained 640-byte destination. The eight-byte store and four one-byte vector stores match independently pinned source bytes; the remaining 628 destination bytes remain zero. No string contents or length/copy result fixture is supplied or exported.

256 cases pass: 45,824 added original visits, 6,400 exact ordered store chunks, 49,920 altered owned requests rejected, 1,792 exact argument reads, 1,024 callee ABI returns, 512 argument-consumer ABI returns and 256 cookie-pop convention returns. All complete E011DZ rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined original visits are 1,024,256; all ancestor counts remain separate.

Original 0xF5E3E0 returns length twelve; the two 0xCAD1F0 calls execute zero padding and actual copy, and original 0xF5D480 writes the private bytes. Original 0xCACDF8 and 0xCAB178 return one with exact caller ABI. The 0x11F0 cookie-pop leaf restores SP+16 and all other NONVOL; this remains separate from a standard SP-preserving leaf and OS stack-growth proof. The earlier zero-destination invariant advances only through these checked original copy effects.

Stop BEFORE the byte read at 0xCA984C from image+0x1370762. NEXT **E011EB** continues the original parser and remaining arguments with the twelve-byte output and returned handler frames retained. Current SP=outer-entrySP-3200, output cursor=outer-entrySP-1380 and variadic cursor=outer-entrySP-1488. Seven consumer frames remain active; full consumer and outer 0x5F8EA8 returns remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, callback table and registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, complete helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EA first argument length / copy](../experiments/E004-front-ir-vd55g0/e011ea-original-first-argument-length-copy/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DZ original parser dispatch / variadic argument accepted

The retained original consumer now reads a seven-byte immutable literal (including its terminator) and seven exact sparse classification/branch cells, dispatches the first argument through original 0xCAB178 / 0xCACDF8, and advances the actual variadic cursor by eight bytes. The original 0xCA65A8 scalar helper returns zero with exact callee-saved ABI; the separate 0x11D0 cookie-frame convention again changes SP by -16. No original literal contents or string result fixture is exported or supplied.

256 cases pass: 43,008 added original visits, 9,728 exact stack store chunks, 70,912 altered owned requests rejected, 2,304 exact immutable reads, 256 scalar-helper ABI returns, 256 cookie-frame convention returns and 768 nested entries. Every complete E011DY row remains equal; cumulative original-entry-to-frontier memory and permissions match with no resets. Combined original coverage is 978,432 visits; inherited DY/DX/DW/DV/DU/DT/DS counts stay separate.

The first argument pointer is original image+0x10F0380, and the variadic cursor is outer-entrySP-1488. Its pointed string contents, read extent and length remain unqualified. The destination remains 640 zero bytes; all nine allocations, redzones, published 18,832-byte zero buffer/refcount one, nested containers, callback table and both registry locks remain retained. Native scalar/pointer selection, pointed locale tables, alternate flags and complete consumer/outer/helper/descriptor/profile startup remain open.

Stop BEFORE actual 0xCACE90 -> 0xF5E3E0, return 0xCACE94, SP=outer-entrySP-3360, X0=image+0x10F0380 and X1=0x7FFFFFFF. NEXT **E011EA** qualifies the original bounded string helper and exact pointed data/read windows in this retained parent. Its 184-byte body metadata is pinned separately; no helper execution or string-length result is accepted here. Nine consumer frames remain active; the outer 0x5F8EA8 return is pending.

E011DM remains the empty RS-query proof and E011DN the limited Windows snapshot. Populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material remain private on SP11.

See [E011DZ parser dispatch / variadic argument](../experiments/E004-front-ir-vd55g0/e011dz-original-parser-dispatch-variadic-argument/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DY cold runtime context / nested receiver setup accepted

Under explicit loader initial-value models, original source reads the zero-fill options scalar at 0x17A1150 and flag at 0x16A2A84, then the file-initial pointer pair at 0x16072D8. Original 0xCAD868 constructs the retained stack context, and original 0xCA6280 constructs the nested receiver fields. These are source effects under declared models; native flag/pointer selection remains unqualified.

All 256 cases pass: 20,992 added original visits, 11,264 exact setup store chunks and 68,608 altered owned requests rejected. Each case validates four exact runtime reads, 44 independently authored ordered stores and two nested entries. The original 0x11D0 cookie-frame leaf returns at 0xCA6298 with its deliberate SP minus 16 effect and all other nonvolatile registers preserved. This is a cookie-frame convention, not an SP-preserving leaf ABI or OS stack-growth proof.

Complete inherited DX/DW/DV/DU/DT/DS rows remain exactly equal and separate; combined original visits are 935,424. One cumulative original-entry-to-frontier memory and permissions snapshot passes. All nine allocations, prior nodes/arrays/redzones, published 18,832-byte zero buffer/refcount one, callback table and epochs remain retained. The 640-byte output destination remains entirely zero; all 44 new stores lie below it. Both registry locks remain held and CRT/SRW released.

Stop BEFORE actual call 0xCA6348 -> 0xCA94E8, return 0xCA634C. Six consumer frames remain active; consumer, outer 0x5F8EA8, enumeration, factory and helper returns remain pending. NEXT **E011DZ** executes the next original consumer with receiver at outer-entry SP minus 3104 and runtime context at minus 1888. The next exact 1028-byte body is pinned as metadata only; accepted source pins remain 32.

The two scalar cells are writable virtual zero-fill with no file-byte hash authority; only cold zero is accepted by this model. The writable file-initial pair identifies 0x1607180 / 0x1607650, without qualifying pointed tables. Alternate native flags, initialized runtime values, pointed locale/format/string contents, complete consumer output/returns, profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instructions/decompilation/raw records/proprietary names and optical material remain private SP11. Fresh one-shot Windows oracle/external SP7 KD remain authorized with fresh atomic identities and manual-only tasks.

See [E011DY cold runtime context / nested receiver setup](../experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DX exact constant-data / retained consumer setup accepted

Original source now reads the exact opaque eight-byte window at 0x10F03A0 and enters the original nested consumer setup at 0x7AC38 / 0x7ACA0 / 0x6BDD0 / 0x6BD48. The original 12-byte leaf at 0xEDD0 returns the address 0x17A1150 at 0x6BD70 with exact ABI preservation. No constant contents, pointed strings, formatted result or consumer return fixture substitutes for execution.

All 256 cases pass: 19,200 added original visits, 8,448 exact stack store chunks, 52,224 altered owned requests rejected, 256 exact constant reads and 256 original leaf ABI returns. The 33 setup chunks per case have independently authored source/address/width/value/order contracts. Inherited DW/DV/DU/DT/DS results remain exactly equal and separate; combined original visits are 914,432. The original-entry-to-frontier memory and permissions snapshot remains cumulative.

The constant authority is the exact eight-byte file-backed nonwritable window, not the earlier exploratory 64-byte window. Five exact function bodies extend the inherited 25 source pins to 30. Four consumer frames remain active; their returns and the outer 0x5F8EA8 return remain pending. The original 640-byte destination and published 18,832-byte buffer are still entirely zero. All nine live allocations, callback table, epochs, locks, previous nodes and redzones remain retained.

Stop BEFORE 0x6BD8C, the next eight-byte read from writable virtual zero-fill coordinate 0x17A1150. NEXT **E011DY** establishes loader/runtime scalar authority and resumes the retained consumer. A static zero-fill coordinate is not proof of its native runtime value. Pointed constant strings, complete consumer/outer/factory/helper returns, selected profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instruction text/decompilation/raw records/proprietary names and optical material remain private SP11. Authorized fresh one-shot Windows oracle/external SP7 KD remain available with fresh atomic identities and manual-only tasks.

See [E011DX exact constant-data / retained consumer setup](../experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DW nested enumeration container / stack clear accepted

Original callee 0x600368 creates a fresh 16-byte object, executes original nested constructor 0x5E81B8 and attaches its returned 64-byte header. Original source creates and clears an 8192-byte array with 1024 zero QWORD slots, then clears a 640-byte stack buffer. No constructed-record, clear or return result fixture substitutes for source execution.

256 cases pass: 151,552 added original visits, 293,632 exact added stores and 26,624 altered owned requests rejected. All 256 nested constructor, 256 array-clear and 256 stack-clear ABI returns pass. Clear visits 122,624 and heap/stack clear chunks 262,144/20,480 are subsets. Inherited DV/DU/DT/DS visits remain separate; combined coverage is 895,232. The original entry-to-frontier memory/permissions snapshot remains exact.

The 16/64/8192-byte leases join six older disjoint live allocations, giving nine. Source constructs exact header/array/owner relations; five header reads have exact contracts. The published 18,832-byte buffer, two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and clears remain retained. Both registry locks remain held, CRT/SRW released. Native allocation, loader/runtime scalar selection, failures/concurrency/teardown and committed stack bounds remain explicit models or open gates.

Stop BEFORE 0x600420, next eight-byte read from 0x10F03A0. NEXT **E011DX** derives exact bounded constant-data authority and resumes the retained original callee. The outer callee return 0x5F8EA8 remains pending; enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DW the nested container proof, E011DV the cold buffer proof, E011DU the callback/epoch proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DW nested enumeration container / stack clear](../experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DV cold enumeration buffer allocation / publication accepted

Under the declared virtual loader zero-fill scalar model, original enumeration requests fresh 18,832-byte storage, clears it through original source and publishes its pointer at 0x169FDF0 and reference count one at 0x169FDE8. No buffer/clear/publication result fixture substitutes for source execution.

256 cases pass: 237,568 added original visits, 603,136 exact added stores and 11,008 altered owned requests rejected. All 256 actual clear callee ABI returns and the single original entry-to-frontier memory/permissions snapshot pass. Clear visits 233,472 and chunks 602,624 are subsets. Inherited DU/DT/DS visits remain separate; combined coverage is 743,680.

All six allocations remain disjoint and live. Both registry locks remain held; CRT/SRW are released. The two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and prior clears remain exact. Loader scalar selection, allocator success/storage, native resource construction and committed stack bounds remain explicit models. Alternate nonzero scalar branch, native failures/concurrency/teardown and native selection are unqualified.

Stop BEFORE 0x5F8EA4 -> 0x600368, actual return 0x5F8EA8. NEXT **E011DW** integrates this original callee in the retained parent with the published buffer and six allocations. Its exact 1120-byte body metadata is pinned separately; no callee execution is accepted here. Enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DU the callback/epoch proof, E011DT the actual factory/enumeration bootstrap and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DV cold enumeration buffer allocation / publication](../experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DU existing-table registration / enumeration publication accepted

Original source appends the second cleanup callback to the actual retained one-entry encoded exit table, using its existing 32-slot allocation without reallocation. Original enumeration guard publication advances its guard, global and actual TLS epoch to 80000042; the first-helper guard remains 80000041 and factory guard remains FFFFFFFF in-progress.

256 cases pass: 45,056 added original visits, 9,472 exact added store chunks and 27,392 altered owned requests rejected. All 2,048 original registration/publication callee ABI returns and the single entry-to-frontier memory/permissions snapshot pass. Inherited E011DT adds 127,744 visits and E011DS 333,312, giving 506,112 combined visits; counts remain separated.

Both registry locks and all five allocations remain owned and live. CRT/SRW are released; first callback, 30 unused slots, nodes, redzones, constructed container and prior clears remain exact. Readiness, native allocator construction and committed stack bounds remain explicit inherited models; native failures/concurrency/teardown remain open.

Stop BEFORE 0x5F8E24, four-byte dependency read from 0x1731598. NEXT **E011DV** qualifies this enumeration dependency and its subsequent branch while retaining the two-entry table and actual published epoch. The enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DT the actual factory/enumeration bootstrap, E011DI the separate bootstrap proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DU existing-table registration / enumeration publication](../experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DT actual-parent factory / enumeration bootstrap accepted

The original factory and enumeration bootstrap now execute in the actual live first-helper parent. The helper's published negative TLS epoch is retained; two fresh 48-byte sentinel nodes remain distinct from its 24/128/256-byte ancestor allocations. Original source initializes 190 fields, clears a 1040-byte stack record and enters enumeration under declared committed-stack bounds.

256 cases pass: 127,744 added original visits and 102,656 added exact store chunks; 333,312 inherited E011DS visits give 461,056 combined visits. Added invalid-contract rejections are 15,104, separate from 43,264 inherited. All actual guard/probe/clear return checks and the single entry-to-frontier memory/permissions snapshot pass.

Both registry locks remain held, SRW/CRT released. Factory and enumeration guards are FFFFFFFF in-progress; neither callee has returned or published its guard. OS/CRT/loader/allocator readiness and committed-stack bounds remain explicit models; native failures/guard-page growth/concurrency/teardown are open.

Stop BEFORE 0x5F94A0 -> 0xCA34A0, actual return 0x5F94A4, callback 0xF7B5E0. Existing encoded exit table contains one callback in 32 slots. NEXT **E011DU** executes this new registration against that nonempty table, then enumeration guard publication and the next dependency. Reuse E011DR registration/publication source and E011DT retained ownership.

E011DM remains the empty RS-query proof, E011DI the separate factory/enumeration proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DT actual-parent factory / enumeration](../experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DS cached object / nested lock / large clear accepted

The unchanged first helper caches inline object 0x17A4230 at 0x1731880, enters a distinct registry lock through original callbacks, writes bounded header fields and clears all 11,808 bytes at 0x17A4268 through original source. No cache/lock/clear result fixture is used.

512 cases pass: 666,624 original visits, including 345,088 added visits; 301,568 added clear visits are a subset. The large clear contributes 756,736 write chunks, counted separately from 66,560 other nonstack and 49,152 stack chunks. All 86,528 altered owned contracts reject. Whole memory/permissions, source/unmodified loader regions, actual callee returns, padding and the adjacent constructed container remain exact.

Runtime readiness, cold zero control cells and disabled tracing remain explicit models; buffer/padding poison are robustness fixtures. Native OS/CRT/allocator construction, failures/concurrency/teardown and full inline-object initialization remain open. Both registry locks are held; CRT/SRW locks are released.

Stop BEFORE actual call 0x5B8268 -> 0x5BDE08, return 0x5B826C. NEXT **E011DT** integrates this factory callee with the actual live parent, published TLS epoch and existing allocation leases. Positive global-epoch edge cases are not native cold-factory readiness proof. E011DH/DI remain separate factory/enumeration acceptance; E011DM remains the empty RS-query proof.

Full helper/descriptor registry initialization, selected profile/input deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement still precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and missing tools remain authorized; use a fresh atomic identity and preserve private originals/optical material on SP11.

See [E011DS cached object / lock / clear](../experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DR original cleanup registration / guard publication accepted

The unchanged cold caller registers cleanup callback 0xF7B120 and publishes the helper guard through original code, without registration/guard result fixtures. The encoded exit table contains one callback in 32 slots; global, helper and TLS thread epochs agree.

512 cases pass: 321,536 original visits, including 173,056 CRT registration and 17,920 publication visits. All 62,464 nonstack chunks, 43,520 stack chunks, 5,632 added callee ABI returns and 62,976 invalid owned-contract rejections pass. Whole memory/permissions, immutable source/unmodified loader regions and the exact TLS epoch update are checked.

Loader/OS resource readiness, fresh allocation storage and a ready empty encoded CRT exit table remain explicit owned models. Native CRT initialization, failure/existing-table growth, callback execution/teardown and concurrency remain open. CRT and SRW locks are released; registry logical lock remains held.

Stop BEFORE 0x5B8104, next factory pointer 0x1731880 read at 0x5B8108. Parent/helper remain active. NEXT **E011DS** follows actual factory construction/publication in this caller; source references identify a pointer write at 0x5B8138, outside current acceptance. Full first-helper return and metadata descriptor registry initialization remain open.

E011DM remains the empty RS-query proof, E011DI separate factory/enumeration acceptance and E011DN the limited Windows snapshot. Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, permanent EFI/GRUB and historical repositories unchanged. Windows oracle/external SP7 KD and missing tools remain authorized; fresh boot and atomic identity for another oracle. Originals and optical material stay private on SP11.

See [E011DR registration / publication](../experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DQ original cold container construction accepted

The unchanged first-helper constructor 0x2EE1A0 completes its normal path and returns at 0x5B9094 with exact ABI. Original source constructs the 64-byte container, 24-byte self-linked sentinel and 128-byte array containing 16 sentinel pointers. Allocation storage/readiness/provenance are explicit owned models; no constructed-object or constructor/helper/guard result fixture is used.

256 cases pass: 65,280 original visits, 13,056 exact nonstack chunks, 12,288 stack chunks and 17,664 invalid owned contract rejections. Whole mapped memory/permissions, source/TLS immutability, allocation redzones/relations and actual constructor/callback/guard return ABI pass. Native allocator, failure/exception cleanup and teardown remain open.

Stop BEFORE 0xCA3450, actual return 0xCA34B0 and callback argument 0xF7B120, after only the four-instruction original registration-wrapper prefix. Parent/helper/wrapper active; registry logical lock held, SRW released and helper guard in-progress. Cleanup registration, helper guard publication, full first-helper return and full metadata registry construction/publication remain open.

NEXT **E011DR** qualifies cleanup registration and original helper-guard publication in this caller. E011DM remains the original empty RS-query proof, E011DN the limited Windows snapshot, E011DI the separate factory/enumeration proof, E011DO initialized-registry reuse and E011DP cold bounds/guard prefix.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DQ container construction](../experiments/E004-front-ir-vd55g0/e011dq-original-cold-container-construction/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals/optical material remain private on SP11; another oracle needs a fresh boot and atomic identity.

## 2026-10-04 E011DP cold literal bounds / first-helper guard prefix accepted

The unchanged initializer writes uint32 literal bounds 239 and 282, enters first helper 0x5B80A8 and executes its original fresh TLS guard acquisition. No bound/helper/guard result fixture is used; loader TLS and OS lock readiness/operations remain explicit owned models.

128 cases pass: 18,560 original visits, 384 exact nonstack field-store chunks, 4,992 stack-store chunks and 6,528 invalid owned contract rejections. Whole mapped memory/permissions, immutable source/loader regions, actual lock-callback and guard-return ABI pass. The helper body is pinned to 4,104 bytes but only its bounded prefix is accepted.

The stop is BEFORE next dependency 0x2EE1A0, actual return 0x5B9094, pointer argument 0x17A7088 and scalar 65535. Parent/helper frames remain active, registry logical lock held, SRW released and helper guard in-progress. Full helper return, allocation/construction/publication and native OS resource construction remain open.

NEXT **E011DQ** qualifies that unchanged construction dependency and complete first-helper/publication path. E011DM remains the original empty RS-query proof, E011DN the limited Windows ready snapshot, E011DI the separate factory/enumeration proof and E011DO the original initialized-registry reuse proof.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero camera Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DP cold bounds / guard](../experiments/E004-front-ir-vd55g0/e011dp-original-cold-bounds-helper-guard/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11. Another oracle requires a fresh boot and atomic identity.

## 2026-10-04 E011DO original registry lock / initialized reuse accepted

The unchanged initializer executes its original default EnterCriticalSection/LeaveCriticalSection callbacks and complete already-initialized branch under explicit owned OS/diagnostic contracts. No callback or parent result fixture is used.

64 scenarios pass: 48 complete initialized reuse returns and 16 cold-prefix stops before 0x5DE800. All 6,848 original visits, 112 ABI-exact callback returns, whole mapped memory/permissions and stack checks pass; 2,512 invalid owned dependency requests reject. Nonzero bound fixtures do not prove registry construction. The accepted cold prefix retains its logical lock and active parent frame; cold field stores/allocation/publication are not accepted.

NEXT **E011DP** qualifies cold-bound construction and original first helper 0x5B80A8 (caller return 0x5DE844), plus resource readiness/construction ownership. Selected reader/request/profile, populated RS generation/lifetime and normal AFD input authority remain open. E011DM remains the original empty-RS-query proof, E011DN the limited Windows ready snapshot, and E011DI the separate factory/enumeration proof.

Deterministic selected-input/profile startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. No new camera Start/reboot/kernel build/production C change; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DO lock / reuse](../experiments/E004-front-ir-vd55g0/e011do-original-registry-lock-reuse/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; SP11/SP7/PiMaster only. Windows oracle/external SP7 KD boots and tools remain authorized; originals/optical material stay private on SP11. Fresh boot and atomic identity for another oracle.

## 2026-10-03 E011DN Windows registry boundary observed

The accepted evidence is a 116-byte rear-reader-ready metadata snapshot before Start: bound/descriptor populated, seven runtime tag cells zero, and live platform callbacks equal the file default targets. Source references identify writer 0x5DE700; full initializer execution is still unqualified.

Two distinct atomic holder identities ran in one Windows boot, stopped/disposed successfully and counted 69 / 449 valid 4K handle acquisitions. A is excluded from RS qualification after observer command/filter issues. B captured only the registry snapshot; zero RS copy hits does not prove reader/query execution or general RS absence. No pixels were saved. This is not isolated-boot hardware or populated-record lifetime acceptance.

Golden return passed: payload hashes, permanent EFI/GRUB and historical repositories unchanged; Windows read-only recovery unmounted, temporary tasks removed, debuggers/holders closed. No production camera C/kernel change or Linux power-policy change.

NEXT **E011DO** qualifies original metadata registry initialization, allocation/descriptor ownership and the selected normal request/profile path before another fresh-boot oracle. E011DM remains the latest source empty-slot query proof, E011DI the separate factory/enumeration proof. Normal AFD input authority, deterministic startup/input/profile integration and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open; native rear runtime remains denied.

See [E011DN boundary](../experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster connects SP11 Linux/Windows and SP7; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11.

## 2026-10-03 E011DM original query through selected empty slots accepted

The original reader, metadata query and selected-slot helper now execute together without query or slot-helper result fixtures for declared empty slots. All 18,816 queries return actual null records; missing RS preserves the prior 132-byte source record.

640 scenarios / 1,920 cold/warm/stale-thread reader calls pass. Added query/helper coverage is 2,916,480 original instruction visits; inherited reader/tag/guard coverage is counted separately. All 356,608 altered dependency bindings reject in the owned harness contracts. Entire nonstack memory/mapping state, immutable source/pool/slot objects, preserved ABI and stack redzones pass.

The normal path selects node+490, uses pool capacity+278 and the inline pointer array+298, with selector modulo capacity. TLS block+138 is a scalar request selector; the original reader's ninth query stack argument is zero. Registry/settings/node/context/pool/empty-slot construction and standard OS resources remain explicit owned models.

**Still open:** actual selected registry values and metadata registry initialization, populated-record identity/generation/lifetime, normal AFD H/V counts and whole-frame zero-offset producer. Private populated-slot exploration reaches 5DF780 -> 5C0A58 and image+17350E0; it is excluded from acceptance. NEXT **E011DN** resolves that selected dependency and populated RS ownership, then normal AFD policy.

Selected input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Separate factory/enumeration acceptance stays E011DI; native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DM empty-slot query](../experiments/E004-front-ir-vd55g0/e011dm-normal-rs-empty-slot-query/README.md). Earlier current/NEXT paragraphs below are historical. User authorizes Fabric or PiMaster, one-shot GRUB Windows oracle/external SP7 KD boots and missing-tool installation. Hosts SP11/SP7/PiMaster; originals and optical material stay private on SP11.

## 2026-10-03 E011DL original runtime statistics tag initialization accepted

The actual reader's guarded first-use path now produces all seven runtime tags from declared registry fields, including RS slot5, with no tag-vector or guard-result fixture. Unchanged CRT acquisition/publication bodies execute in the real reader caller. Warm and stale-thread calls preserve published tags despite altered registry inputs.

192 scenarios / 576 reader calls, 1,344 exact tag-field stores, 5,376 initializer-path instruction visits and 76,224 rejected dependency bindings pass. The 262,848 total original visits include inherited reader/guard coverage; this is bounded emulation, not camera hardware acceptance. Entire nonstack memory/mapping state and preserved ABI/stack redzones pass.

**Still owned models:** registry values/objects, settings, metadata-query results and OS SRW/CV resources. Actual query body, selected pool/record lifetime and normal AFD count/offset policy remain open. NEXT **E011DM** resolves those dependencies, reusing E011DK copy/decoder, E011AM arithmetic, E011M initial defaults and E011AK sampled unity binding.

Required input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Latest selected RS source acceptance is E011DL; separate factory/enumeration acceptance stays E011DI. Native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DL tag initialization](../experiments/E004-front-ir-vd55g0/e011dl-normal-rs-runtime-tag-initialization/README.md). Earlier NEXT/current statements below are historical. User reaffirmed autonomous one-shot Windows oracle/external SP7 KD boots and missing-tool installation on 2026-10-03; preserve Golden and same-SP11 private originals.

## 2026-10-03 E011DK RS metadata copy and C decoder accepted

The original RS metadata reader passes 96 present/absent/fallback cases and 39,904 instruction visits. The new checked C decoder reuses E011AM arithmetic, matches three observed records and 42 input/output fields per compiler, and rejects 21 invalid or unsupported inputs before output effects under GCC/Clang ASan/UBSan. All 132 copied bytes, owned heap changes, source immutability, original code, stack and caller state pass.

This closes the consumer/decoder contract only. Query/helper results, registry/settings/TLS/locks and runtime property tags are explicit owned fixtures. Actual tag initialization, metadata query/record publication and upstream AFD normal count policy remain open. Missing metadata preserves the prior source record; the decoder supplies no guessed defaults.

**NEXT E011DL:** follow RS tag cell 17A30F4, slot-5 query 5D4D30 and actual upstream normal count/offset publisher. Reuse E011M initial counts, E011AM numerical binding and E011AK sampled unity BG gain proof. Required selected input/profile integration, deterministic bootstrap/preflight and independent enabled-output DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate.

Latest selected RS source acceptance is **E011DK**; the separate original factory/enumeration branch remains **E011DI**. Native rear runtime remains denied. Zero camera Starts, reboots, kernel builds or optical tests here; Golden unchanged. See [E011DK metadata input](../experiments/E004-front-ir-vd55g0/e011dk-normal-rs-metadata-input/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 E011DJ input ledger accepted; E011DK normal RS policy next

The checked selected-baseline ledger covers all 14 register-state members, five DMI families and ten replay input blocks. It reuses 15 bounded proof facts, pins 55 authored files and rejects eight invalid ledger mutations. This is source/evidence inventory; no new numerical, emulation, optical or hardware test.

Initial Titan680 RS defaults, immediate AEC BG producer lineage and AWB pre-request seed/writer lineage are already proven. Normal RS count/override authority, selected normal input/profile bindings and independent enabled-output retirement remain open. NEXT **E011DK** follows the actual normal RS pre-adjustment writer upstream of A0DFC0; reuse E011AM arithmetic/binding and E011M initial defaults. Continue generic factory/registry work only for a named selected-baseline dependency.

Latest original emulation remains E011DI. Native rear runtime remains denied; Golden unchanged. See the checked [input ledger](../experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 evidence audit and next product gate

Latest accepted source checkpoint remains **E011DI**; native rear runtime remains denied. Earlier live front native ISP, front/rear RAW and ordinary-app/software fallback capture are retained. E011AM has zero-difference offline startup parity; E011AR is a compiled packet-isolated runner; E011AS/AV/BW supply specific cold policies. Complete deterministic startup and physical buffer retirement remain open.

**NEXT E011DJ first builds the selected-baseline input/dependency ledger**, reusing closed producers and identifying remaining normal RS count/whole-frame offset and other required normal-input authority. Continue the private registry/factory trace only for a named baseline consumer/lifetime dependency. Then integrate source-only preflight, independently prove IRQ/exact-buffer/DMA/IOMMU retirement, and target the existing eight-fresh-frame front/rear/off clean-colour app milestone. Optional effects/catalogue and protected IR/Hello remain deferred. Runtime/default promotion gates are unchanged.

Windows BF events were already live-observed in E005o; exact hardware retirement is still open. Older software-first, black-scene and historical NEXT paragraphs are snapshots, superseded by this audit for current priority. Report added coverage separately from inherited regression totals.

See [camera evidence audit](CAMERA-STACK-AUDIT-2026-10-03.md) for evidence tiers, corrected status and acceptance gates.

## E011DI original enumeration bootstrap — BOUNDED PASS

Thirty-two cases continue the verified factory VM into original5F8DC0: combined15,936 original instructions,12,832 exact store chunks and3,488 rejected requests. Added enumeration proof contributes2,560 /1,024 /1,536.

Original stack helper1440 uses the actual112-byte initial frame and source5920-byte additional request under explicit already-committed stack bounds. Original CE7AD8 runs through second caller5F9460/guard1B30320, claimsFFFFFFFF and preserves its actual caller with balanced logical SRW ownership. Source code clears all56 bytes at169FE00. Whole memory/permissions/source reads/stores retain both48-byte records, typed owners and the1040-byte receiver.

The stop is BEFORE5F94A0→CA34A0 with callback argumentF7B5E0. Registry body/result, OS guard-page growth, file enumeration/completion/full parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/stack/native OS/allocator/canary fixtures remain explicit.

NEXT **E011DJ** follows original callback registry CA34A0/CA3450 and then enumeration completion/file provenance. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DI](../experiments/E004-front-ir-vd55g0/e011di-original-enumeration-bootstrap/README.md).

## E011DH original factory initialization and1040-byte clear — BOUNDED PASS

Thirty-two cases across stack/node placements, loader indices, negative epochs and original/D7-canary field states execute13,376 original instructions,11,808 exact store chunks and1,952 invalid requests rejected before effects.

Original factory code clears190 image field chunks. Original F5E600 now executes through source call5BE9F8, zeros1040 bytes at incomingSP-1144 and returns destination to5BE9FC with its actual caller preserved. Its result fixture is absent. Whole mapped memory, actual permissions, exact scalar/vector/source writes and reads, both full48-byte records and logical SRW/allocation ownership pass.

The accepted stop is BEFORE5BE9FC→5F8DC0. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator/native OS models and D7 robustness fixtures are explicit. File enumeration, full factory completion/parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DI** follows original file-enumeration routine5F8DC0 through its actual caller and source-created1040-byte stack record. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DH](../experiments/E004-front-ir-vd55g0/e011dh-original-factory-initialization-clear/README.md).

## E011DG original factory two-record construction — BOUNDED PASS

Sixteen cases across four stack/node placements, two owned loader indices and two negative cold epochs execute1,712 original instructions,672 exact store chunks and816 invalid requests rejected before effects.

Actual factory guard caller checks remain intact. Original call instructions5BE698/5BE6CC request two48-byte allocations under typed owned success models; original source then constructs and publishes both full records, with three self-pointers, two-byte257 and22 zero bytes each. Whole mapped memory, actual permissions, source reads/stores, logical allocation/SRW ownership and actual guard caller preservation pass.

The accepted stop is BEFORE5BE6F4. Allocator/native OS bodies, failure cleanup, full factory parent return/completion/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator fixtures are explicit.

NEXT **E011DH** follows original factory data initialization and library boundary, then file enumeration/context/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DG](../experiments/E004-front-ir-vd55g0/e011dg-original-factory-two-records/README.md).

## E011DF original factory cold prefix and actual startup guard caller — BOUNDED PASS

Sixteen cases across four stack placements, two owned loader indices and two negative cold epochs execute 1,344 original instructions, 352 exact store chunks and 640 invalid requests rejected before effects.

Original factory5BDE08 now calls original CE7AD8 at5BE67C with actual guard1B302D0; it returns to5BE680 with actual guard caller SP/nonvolatile registers preserved and balanced logical SRW ownership. Original code changes the guard0→FFFFFFFF and clears three factory initialization fields. Whole mapped memory, actual permissions, exact source reads and independent store models pass.

Each case stops BEFORE allocator call5BE698→CAE740 requesting48 bytes: 84 instructions executed, with the stop call excluded. Owned loader/TLS/negative epochs/file-BSS state/native OS models remain explicit. Full factory parent return, allocation/construction/completion, Default/full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DG** qualifies the exact48-byte allocation boundary and original factory construction, then context/file enumeration/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DF](../experiments/E004-front-ir-vd55g0/e011df-original-factory-guard-prefix/README.md).

## E011DE original standalone startup-guard sequence — BOUNDED PASS

Sixteen scenarios cover four placements, two owned loader indices and two epochs across fresh initialization, completion and cache refresh. All48 original helper phases pass: 1,504 instructions, 304 exact store chunks and 1,168 invalid requests rejected before effects.

Original CE7AD8 claims first initialization with guardFFFFFFFF. Original CE7A48 increments epoch1607B04 and updates the guard/TLS+16; the original initialized path refreshes a stale TLS epoch. Whole memory, actual permissions, logical SRW resource order and original caller SP/nonvolatile registers pass.

Loader/TEB/TLS/SRW/CV readiness and void OS dependencies remain explicit owned models. Native OS bodies/bytes, concurrent waiting and actual factory/Default production remain open. This standalone proof is not yet joined to factory5BDE08 and its source guard1B302D0.

NEXT **E011DF** joins the original runtime guard to its exact factory caller, then resolves file enumeration/context receiver/RootOpsinput+72 and full startup/preflight/RS. Independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DE](../experiments/E004-front-ir-vd55g0/e011de-original-startup-guard-sequence/README.md).

## E011DD original root reference-release component — BOUNDED PASS

Sixteen isolated cases at four placements cover null roots and references1/2/41. Twelve first execute original fresh-root construction. The source release branch decrements references, retains nonfinal roots and calls the typed OS root+8 deletion and sized176-byte release only for the final reference, then clears global1798458.

Combined construction/release: 2,004 original instructions, 616 exact store chunks and 464 invalid requests rejected before effects. Whole memory, actual permissions, logical resource order and paused register restoration pass. Held-lock and competing-user states also reject before effects.

This is the interior source component290988..2909D4, not a full parent destructor or parent ABI return. Native OS/allocator bodies, concurrent retry, failure cleanup, live caller ownership and hardware retirement remain open. No cleanup is appended to retained E011DC camera outputs.

Provider input+48 and RootOps candidate input+72 are distinct. Context+9552 is not established as the registered camera callback. Cold factory startup reaches an unqualified runtime helperCE7AD8 at5BE67C under guard1B302D0; actual Default/factory/context receiver production remains open.

NEXT **E011DE** resolves that source runtime/factory/Default consumer, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DD](../experiments/E004-front-ir-vd55g0/e011dd-original-root-reference-release/README.md).

## E011DC original fresh-root construction and registered camera join — BOUNDED PASS

Four isolated placements and six ANSI/OEM camera joins execute the fresh-null-root registration path: 1,530 original instructions, 500 exact store chunks and 170 invalid requests rejected before effects. Original code zeros all 176 bytes, copies the private 12-byte NUL-terminated name into root+48, calls the typed OS initializer on root+8, publishes the root at 1798458 and increments its reference to one.

The 48-byte callback record still supplies camera entry through slot 32. Independent whole memory, permission, resource and actual caller models pass; the complete source-created root, added table/stack/API regions, output/global/inner link and SAME balanced root lock survive the camera outer return. The inherited malloc adapter delegates this exact source call to the strict owned 176-byte model; all other parent observers remain enabled.

Return clarification: E011DB's existing-root path retains the input record pointer in X0. The fresh path retains a residual X0 from the void OS initializer, tested with four distinct owned values. Neither establishes a general registration status or defined record return. The name-copy helper itself returns zero on this checked success path.

Allocation and native OS critical-section bytes/concurrency remain explicit typed models. Source failure/cleanup, actual Default provider and full Windows startup/preflight/RS remain open. The provider+0x162e90 table is a derived static candidate, not complete provider execution authority.

NEXT **E011DD** follows original provider/Default consumers and registered root lifecycle, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DC](../experiments/E004-front-ir-vd55g0/e011dc-original-fresh-root-camera-join/README.md).

## E011DB original callback registration and registered camera entry — BOUNDED PASS

Twelve isolated cases cover four aligned placements and owned root reference counts 0/1/41. Six ANSI/OEM camera joins across three pinned private inputs now enter 36CBA0 through slot 32 of the 48-byte callback record produced by original 36E9C8. The caller no longer chooses a fixed entry address.

All 18 original registration returns execute 810 unchanged instructions and 234 exact store chunks. Independent complete-record/entire-memory models check size 48, slots 16/32/40, preserved reserved bytes and the original root+0 reference increment. All 126 invalid requests reject before effects. Original X0 returns the input record pointer, not a status code; actual SP/X19–X29/D8–D15 and the complete paused caller restore.

The entire added table region, initializer stack, root record and actual permissions remain unchanged after registration through the camera outer return. Inherited runtime-helper, caller, output/global/inner-link and SAME balanced-root-lock checks pass. The file-image control globals 0/1/0, owned nonnull root, placements and component ordering remain explicit fixtures; fresh 176-byte root construction, other registered-slot bodies, actual Default input production and full Windows startup remain open.

Original ARM64 exception metadata identifies 36CBA0 as 6152 bytes (the older 6160-byte source window was wider), registration 36E9C8 as 448 bytes and provider 2BC618 as 2128 bytes. Internal source call 2BC71C registers this record. The provider's complete execution and descriptor construction are not inferred from that static reference.

NEXT **E011DC** follows the fresh-root allocator/initializer/OS/name-helper ownership and provider/Default input lineage, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DB](../experiments/E004-front-ir-vd55g0/e011db-original-callback-registration-join/README.md).

## E011DA original runtime helpers in the camera join — BOUNDED PASS

All six ANSI/OEM cases across three pinned private inputs execute original CE7C98 reverse byte search inside the camera harness. Its basename result fixture is removed: 300 source calls / 77,992 original instructions use exact source callers, private literal hashes, search byte 92 and last-backslash results. Every call preserves all mapped memory, permissions, resource state and actual callee-saved registers.

The fresh TLS flag starts at 0. Original CFE600 -> CFE560 produces block+20=1 before camera startup in 204 instructions and 36 exact store chunks. Independent entire memory models permit only source stack stores and that flag byte; the original callee and complete paused caller restore. All 1,542 invalid helper requests are rejected before effects. The dedicated initializer stack stays unchanged throughout the camera join.

Inherited publication and outer-return models still match. Output/global retain the actual outer, outer+40 retains the actual inner, actual incoming SP/X19–X29/D8–D15 restore and the SAME root mutex balances one Enter/one Leave. Publication now counts 5,388 executed OEM instructions / 36 retained adapters; the tail counts 4,872 / 84. Other library/diagnostic/cookie fixtures remain explicit.

TLS loader index 0, TEB/array layout, file-image null initializer table, owned stack and component ordering remain declared fixtures. Parent harness observers pause only for the separately guarded TLS emulator component and resume in finally; exact original instructions, reads, stores and whole memory remain independently checked. Actual Windows loader initialization, nonempty callback lists, full runtime CFE600, Default/CRT/locale/concurrency and hardware readiness remain open.

NEXT **E011DB** addresses remaining Default and full-startup provenance, then preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DA](../experiments/E004-front-ir-vd55g0/e011da-original-runtime-helper-camera-join/README.md).

## E011CZ original runtime helper authority — BOUNDED PASS

Original CE7C98 is reverse byte search used by18 source callers on eight private source-path literals, not a TLS/context getter. Its inherited owned_diagnostic_context label and TLS+3000 result fixture are corrected in scope; the camera harness still retains the fixture pending E011DA.

Seventy-two original reverse-search returns (64 owned placement/search cases and8 actual private image literals) match independent last-match/NUL/NULL results in4,601 original instructions. The source-derived aligned16-byte SIMD read windows and every canary remain unchanged. Thirty-two original CFE600 -> CFE560 returns cover four owned placements/four PE TLS-index fixtures/fresh and initialized flags:928 instructions/176 store chunks independently produce block+20=1 when fresh, with actual SP/X19–X29/D8–D15 restoration and whole memory checks. All584 invalid scope requests are rejected before effects.

PE TLS AddressOfIndex matches source global16A3740. The callback table is pinned null file-image data; this is bounded empty-initializer-table proof under declared loader/TEB/array fixtures. Full actual Windows loader, nonempty initializer callbacks, Default/CRT/TLS/locale/concurrency and runtime CFE600 authority remain open. Original helpers are not yet integrated into the camera harness.

NEXT **E011DA** performs that shared camera join and rechecks whole memory, caller restoration, output/global retention and balanced locks across six source cases; then remaining full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/C/kernel changes. See [E011CZ](../experiments/E004-front-ir-vd55g0/e011cz-original-runtime-helpers/README.md).

## E011CY original publication callback and outer return — BOUNDED PASS

Six ANSI/OEM camera joins across three pinned inputs recheck the accepted publication prefix and execute the original publication callback36E670 through outer return36E394. The tail checks 3,360 executed OEM instructions plus90 explicit inherited adapter entries, 666 exact store chunks, 2,592 separately contracted owned library-clear bytes and450 invalid requests rejected before effects.

Independent entire stack/camera/caller models match; every other full inherited region, real permissions, allocation/release history and CRT resource state stays unchanged. W0 returns0; actual incoming SP, X19–X29 and D8–D15 restore. Output/global retain the actual outer object and outer+40 the actual inner. The SAME parent camera-root mutex closure records one Enter/one Leave with final depth0 at original return36E2B4.

The exact outer cookie producer11D0/checker11F0 pair now executes unchanged (36/48 instructions across six cases), with its entire producer-stack delta and caller restoration checked. Other nested cookie helpers and the clear-helper implementation remain explicit fixtures. Added owned TEB+88 linkage and the restored existing parent Leave binding are declared ABI fixtures before the tail baseline; actual Windows loader/Default/CFE600/TLS/FLS/locale/concurrency remain open.

NEXT **E011CZ** source-qualifies original TLS/context and runtime bootstrap authority, then full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero new Starts/reboots/Linux images or production C/kernel changes. See [E011CY](../experiments/E004-front-ir-vd55g0/e011cy-original-outer-return/README.md).

## E011CX original output and global publication — BOUNDED PASS

Six cases cover both ANSI/OEM fixtures across three pinned inputs. After accepted file/thread cleanup, the remaining parameter iterations run through the unchanged interface96 and core-vtable16 callbacks. Original code links outer+40 to the actual inner object and publishes the same outer object to the caller output and image global1798460.

The verifier checks 2,316 executed OEM instructions and 114 original Windows getter instructions, with 48 explicitly inherited diagnostic/CFG adapter entries counted separately. All 384 store chunks match pre-instruction/source-field models; 150 invalid callback/getter requests are rejected before effects. Independent entire stack, camera, caller and image models match, all other complete regions stay unchanged, actual permissions and allocation/lock state match, and the retired Unicode owner is never read.

The accepted stop is before guard36E178 and original outer field16 callback36E670. The camera root mutex remains held; complete outer return and full Windows loader/Default/CRT/TLS/locale/concurrency remain unqualified. The observer's initial X26 assertion now applies only to the first parameter-loop visit; subsequent visits use the original saved output at SP+96. No original code bytes change and original CFE600 remains guarded.

NEXT **E011CY** qualifies the publication callback, whole outer return and balanced camera lock with independent models and exact incoming caller checks. Separate private exploration reaches a return under extended owned ABI fixtures, but is excluded from acceptance. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate smoke testing. Golden/history unchanged; zero new Starts/reboots/Linux images. See [E011CX](../experiments/E004-front-ir-vd55g0/e011cx-original-output-publication/README.md).

## E011CW original file-error thread join and cleanup — BOUNDED PASS

Six original camera joins cover both ANSI/OEM fixtures across three pinned inputs. The unchanged slot/thread initializer runs in the same Native instance and CRT owner, with a separate owned stack and preserved paused caller. Its 2,406 OEM/258 OS instructions pass the inherited whole-memory models and 396 invalid API requests. The slot and entire 968-byte thread owner are source-produced.

The exact measured read-only file failure feeds 1,566 original cleanup instructions, 342 original Windows getter instructions and 234 exact stores; 186 invalid cleanup API requests are rejected before effects. Original thread fields receive OS error3 at+36 and CRT error2 at+32. The original path clears descriptor/stream flags, releases the74-byte Unicode owner and both held descriptor/stream locks, with no later source read of the retired Unicode owner.

Independent entire stack/CRT models and all other entire image, camera, serialized, native-heap, TEB/FLS and OS regions match; real permissions match. Public output stayszero. The bounded stop is CED194 after stream-lock release. Initializer ordering, TEB, file-image/null locale/diagnostic globals and logical OS resource adapters remain explicit fixtures; actual full Windows loader/startup/concurrency and original CFE600 remain open.

NEXT **E011CX** continues after CED194 through existing typed diagnostic ownership, remaining configuration/publication, whole outer return and balanced camera locks. Reuse only the already source-classified16A4230 diagnostic contract; no generic logger or numeric/TLS success substitute. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate smoke testing. Golden/history unchanged; zero new Starts/reboots/Linux images. See [E011CW](../experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/README.md).

## E011CV original CRT slot and thread record — BOUNDED PASS

Four owned allocation placements and fresh slots pass 1,684 unchanged OEM instructions, 165 original Windows getter/setter instructions, 307 exact store chunks and 264 invalid API requests rejected before effects. Bounded API-set parsing and the exact host export/NTDLL forwarder agree. Original CB4338 publishes the allocated slot; the original producer allocates and initializes the entire 968-byte thread record.

Independent entire image, stack, CRT, TEB and FLS byte-layout models match. All other entire regions and actual permissions match, original callee-saved registers/SP restore and locks balance. The original Windows getter retrieves the exact published owner; the original error setter restores the input error after an explicit owned API clobber.

This is standalone guarded Unicorn evidence under a fresh single-thread registry, file-image/null locale and zero diagnostic-global fixtures. FlsAlloc/FlsSetValue use strict owned adapters; their original Windows implementations, actual live loader/TLS/locale/concurrency, callback cleanup and the camera join are open. Original CFE600 remains unqualified. NEXT **E011CW** joins this producer to the original file-error path, then qualifies error mapping, descriptor/Unicode release and full outer return. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate the smoke test. Golden/history unchanged; zero new camera Starts, reboots or Linux image tests. See [E011CV](../experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/README.md).

## E011CU original measured file-failure path — BOUNDED PASS

Six unchanged original camera joins cover both ANSI/OEM fixtures across three pinned inputs, first placement only. Strict external contracts use the actual E011CT read-only file failure and thread error3, bound to the exact filename digest, seven ABI inputs, SECURITY_ATTRIBUTES, source return sites and call sequence. All432 original failure-prefix instructions,96 exact store chunks and60 invalid API requests pass full memory/state checks.

Original CFD6F0 clears descriptor0 record+56. Its invalid handle and initialized mutex remain held; the owned74-byte Unicode allocation is retained. Independent entire64KB stack and CRT models permit only original stack stores and that one flag clear. Entire other image/native-heap/camera/serialized/API regions and policy pages/permissions match; all lock depths and allocation ownership remain unchanged. The original thread-context helper reaches the stop before FlsSetValue atCBA198, with source CRT slot1607168 stillFFFFFFFF and a -1 busy marker. No FLS call/result is supplied, and original CFE600 remains unqualified.

NEXT **E011CV** source-only: original slot initializer CB4310/dynamic module-export resolution and fresh owned FLS registry, then original per-thread object producer/error mapping, descriptor/Unicode cleanup and full outer return. Actual live Default/full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/history unchanged; zero new Start/reboot/C/kernel/image tests in this source phase. See [E011CU](../experiments/E004-front-ir-vd55g0/e011cu-original-file-error-boundary/README.md).

## E011CT actual Windows file/error input — BOUNDED PASS

The fresh E011CT-OS-002 observer made one native standard ARM64 CreateFileW call with the source-verified private filename and all seven read-only ABI inputs. It returned an invalid handle; the managed capture, Kernel32 and NTDLL thread-error getters all reported3, with NTSTATUS0xC000003A. An independent known-value last-error round trip agreed. The private4096-byte shared OS page and NTDLL initialization cell were observed on SP11; the cell matched before/after. No file content was read or created, and no proprietary OEM camera DLL, camera Start, stream or optical API was invoked.

The runner preserved the existing EFI mount and returned normally to Golden boot e5f58539-ac31-427d-a718-f1970684107b. All three Golden payload hashes, persistent boot order, saved GRUB, empty next entries, idle camera and both historical checkouts match. Private evidence is archived on SP11; ESP inputs/scripts/snapshots are retired, retaining consumed markers. The earlier mount rejection is a preserved consumed abort, with no target API call.

NEXT **E011CU** source-only: bind this measured failure to the exact original caller/input contract, qualify original error/TLS/descriptor/UTF16 cleanup, then final publication/full outer return and balanced locks. Actual live Default production and full CRT/startup are still open. Native rear remains denied pending full startup/preflight/RS and independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. This is an OS-dependency observation, with zero new Linux camera images. See [E011CT result](../experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/RESULT.json) and [next source](../experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/NEXT-SOURCE.json).

## E011CT Windows file-API observation — FRESH ATTEMPT 002 PREPARED, UNARMED

Attempt E011CT-OS-001 is consumed and aborted before the observer or target API. Windows rejected the temporary mount command; read-only topology showed the existing EFI mount at Z:. The runner returned normally to new Golden boot f6b17d2b-4a76-4ab1-a748-35fcd9ee17c4, with all three payload hashes, persistent boot order and historical checkouts preserved. No camera Start, file API or shared-page observation ran. Its private input/scripts were archived on SP11 and retired from ESP; consumed evidence remains.

Fresh E011CT-OS-002 verifies the existing EFI partition GUID/type/size, uses and preserves its current mount, and removes only a mount it creates. The observer additionally requires loaded ARM64 NTDLL. Both PowerShell sources parse and the independent C# compiles on SP7 without private inputs or target calls. Publish exact prepared source, then a single guarded direct-Windows BootNext0006 observation with the owned600-second return timer and normal15-second Golden return. E011CS remains the accepted source proof; complete original startup/Default producer/cleanup and hardware gates remain open, with native rear denied. See [fresh plan](../experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/attempt-002/PLAN.json) and [consumed abort](../experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/ATTEMPT-001-ABORT-SAFE.json).

## E011CT Windows file-API observation — PREPARED, UNARMED

E011CS remains the accepted source checkpoint. Its next dependency now requires a bounded same-SP11 Windows observation: one standard CreateFileW call with the verified private filename/read-only ABI, immediate observer-thread Win32/NT status, and a private4096-byte shared OS-page snapshot. No camera API or proprietary OEM DLL is invoked by this observer. Default filename production and full CRT/startup remain open.

The independently written C# compiles on SP7 with exact24-byte Win64 SECURITY_ATTRIBUTES/offsets8/16; both final PowerShell scripts parse. No SP11 private input was transferred to SP7, and preflight invokes no target file/shared-page API. Atomic CreateNew marks the fresh E011CT-OS-001 before the target call. The Windows runner arms its own600-second reboot watchdog, removes its temporary ESP mount and requests normal Golden return after15seconds.

Next publish/verify this exact prepared source and private same-SP11 inert ESP handoff, then use existing direct-Windows BootNext0006 once. Preserve persistent Linux-first BootOrder and GRUBsavedGolden; verify a new Golden boot and emptynext entries, archive/retire evidence, then qualify original OS/result/error/CRT cleanup. Native rear stays denied pending full startup/preflight/RS and independent enabledWM16IRQ/consumedIOVA/DMA/IOMMUretirement/optical. See [E011CT plan](../experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/PLAN.json).

## E011CS original file-opening boundary — BOUNDED PASS

Six unchanged original camera startup joins cover both ANSI/OEM fixtures across three pinned inputs, first camera placement only. After the inherited complete Unicode conversion, original CRT mode parsing and descriptor allocation reach the stop before CreateFileW at0xCFD658. No file API executes and no handle/error result is supplied.

All1098 original preparation instructions,282 exact store chunks and48 lock-contract negatives pass. Independent entire64KB stack and CRT-arena models permit only stack stores plus descriptor0 record+56=1/+40=INVALID_HANDLE_VALUE. Other entire image/native-heap/camera/serialized regions and policy pages/permissions match. GlobalCRTindex7 enters/leaves balance; the initialized descriptor0 lock remains held. The owned74-byte UTF16 allocation is unchanged/retained; output remainszero and camera/new-stream locks remainheld.

All seven file-call arguments and the entire24-byte SECURITY_ATTRIBUTES match: read access, share-read, owned absolute drive-C path, null security descriptor, inherit1, OPEN_EXISTING, normal attributes, null template. This proves preparation in explicit owned fixtures, not actual Windows filesystem/default filename/last-error/TLS/concurrency or file success/failure. Earlier wider/isolated source evidence remains historical. Original numeric/TLS/policy/Unicode instructions are unchanged; CFE600 still raises.

NEXT **E011CT**: qualify file API/result/error ownership, then descriptor/UTF16 cleanup, final publication/full outer return/balanced locks. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/historical checkouts unchanged; zero Starts/reboots/deployments/C/kernel/image tests. Clean controllable front/back first; AI/effects/HDR/catalogue deferred. See [E011CS](../experiments/E004-front-ir-vd55g0/e011cs-original-file-opening-boundary/README.md).

## E011CR original Unicode conversion — BOUNDED PASS

Seventy-six original Windows conversion API returns and NTDLL entries pass in guarded Unicorn fixtures. Sixty-four isolated size/output cases cover eight ASCII lengths, two input alignments and both ANSI/OEM codepage aliases. Six original camera joins cover both policies across three pinned tuning inputs, first camera placement only. The unchanged CRT converter returns to0xCFD4E8 with status0 in all six.

Each camera path queries37 UTF-16 code units including NUL, requests74 bytes through original malloc and a strict owned HeapAlloc contract, then converts into that allocation. Original source stores the owned pointer and code-unit extent at caller record+16/+24. Independent entire32-byte result-record,64KB stack and CRT-arena models match; callee-saved registers restore. Other entire regions/pages/permissions match, output remainszero and camera/new-stream locks remainheld. All4980 integrated OS instructions,426 OS stores,450 following CRT instructions,54 following CRT stores and30 new scope/heap negatives pass.

The API/NTDLL routines execute unchanged only inside Unicorn. ANSI/OEM defaults65001 are copied from the file image, virtual caches are explicit zero fixtures, and the security cookie is the file-image seed. This qualifies ASCII conversion in that fixture, not live Windows default codepages/locale/cookie/loader initialization, general Unicode/error paths, native DLL execution or real heap/concurrency semantics. No size/conversion/numeric/TLS/policy success stub or new logger admission; original CFE600 remains unqualified and raises.

NEXT **E011CS**: follow the caller after0xCFD4E8 through remaining CRT/file-opening/cleanup, qualify dependencies and ownership, then final publication/whole outer return/balanced release. Full startup/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/historical checkouts unchanged; zero camera Starts/reboots/deployments/C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CR](../experiments/E004-front-ir-vd55g0/e011cr-original-unicode-conversion/README.md).

## E011CQ original conversion-query boundary — BOUNDED PASS

Six original camera startup joins cover both explicit ANSI/OEM policies across three pinned tuning inputs, at the first camera placement. The unchanged CRT branches call converter0xCB76B0 and reach the Unicode size-query tail at0xCB8DD4. ANSI selects codepage0; OEM selects1. Original arguments are flags9, W3=-1, a NUL-terminated owned-stack filename, null output and capacity0. Execution stops before the tail branch into the conversion API; no conversion result is supplied.

All48 exact saved-register qword stores match independent entire64KB stack models. Entire OEM image, native/CRT/camera arenas, serialized input and caller fixtures remain unchanged. The filename and zero result record remain unchanged; no allocation or lock-depth change occurs. Thirty-six scope negatives reject without state delta. Inherited prefixes retain90 exact statistics records,720 statistics initializers,146 core initializers and270 GetTag lookups. Output remainszero; camera/new-stream locks remainheld.

NEXT **E011CR**: qualify the conversion dependency and explicit codepage/locale/size-result ownership before admitting any conversion result, allocator or later file-opening continuation. Full CRT/final publication/whole outer return/balanced release, original TLS CFE600 and full startup/preflight/RS remain open. Independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. No numeric/TLS/policy/conversion success stub or new logger admission.

Golden hashes and historical checkouts are unchanged. Zero camera Starts/reboots/deployments/production C/kernel/image tests. Original OS policy code remains inherited Unicorn-only evidence; no native Windows DLL execution. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CQ](../experiments/E004-front-ir-vd55g0/e011cq-original-conversion-query/README.md).

## E011CP original file-encoding policy and wrapper — BOUNDED PASS

Fourteen original OS policy-setter, query and OEM wrapper returns pass in guarded owned memory: seven ANSI results1 and seven OEM results0. Four isolated cold/cached pairs flip the source-produced policy without reloading the cached API pointer. Six original camera0x36CBA0 joins cover both explicit policy states across three pinned tuning inputs, one camera placement each.

The requested export branches through an original import thunk into the dependency's original28-byte query. Original68-byte setters produce four policy fields each; no BOOL success substitute is used. All56 exact policy stores,392 original OS instructions,12 original consumer instructions,60 OS ownership rejections and30 policy-scope rejections pass. Entire owned pages and real permissions, OEM image, CRT/native heap/stack and camera-object guards match. Relocation/linking and uncalled conversion-pointer identities remain explicit owned fixtures, not actual Windows default policy/loader/NTDLL conversion/concurrency proof.

All six camera wrappers return to0xCFD49C. The unchanged caller reads one byte at SP+48 and branches on nonzero W0: ANSI stops before0xCFD4C0, OEM before0xCFD4A4. The source caller byte is0 in these six cases. Ninety exact statistics records,720 statistics initializers,146 core initializers and270 total GetTag lookups remain checked. Output remainszero; camera/new-stream locks remainheld; ten resolver lock pairs balance. CN/CO wider placement evidence remains historical, not rerun across this new consumer boundary.

NEXT **E011CQ**: follow those selected CRT/file-opening branches, qualify receivers/stores/dependencies, then final publication/whole outer return/balanced release. Actual conversion/codepage/locale/full CRT and original TLS CFE600 remain open. No numeric/TLS/policy success stub or new logger admission. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Original OS routines execute only inside Unicorn on SP11; no native Windows DLL call. Golden hashes and historical checkouts unchanged; zero camera Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CP](../experiments/E004-front-ir-vd55g0/e011cp-original-file-encoding-policy/README.md).

## E011CO original dynamic module/API resolution — BOUNDED PASS

Seven complete original 0xCB9B88 resolver returns pass, including three original camera 0x36CBA0 joins across three pinned tuning inputs (one placement per source). Four isolated cold/cached pairs cover four opaque-handle placements. Source-selected module/API names match a SHA-pinned same-SP11 Windows PE export catalog; the selected file-encoding policy export is present, ordinal38/RVA0x70A90, not forwarded.

All 22 exact image stores,14 real Unicorn page-protection changes,seven balanced initialized CRT index14 lock pairs and42 rejected ownership requests pass. Independent whole mapped-image/CRT/native-heap/resolver-arena models match. Cached continuations perform no loader/export/protection/lock calls or stores. The cache PE section is initially writable in the source metadata; source explicitly ends it read-only. Initial writable/read-only states and opaque OS handles/adapters remain explicit owned fixtures, not live Windows loader/init/cookie/lifetime/concurrency proof.

Three fresh camera-source joins retain45 exact statistics records,360 statistics initializers,73 core initializers and135 total GetTag lookups. The camera arena/inner/outer are unchanged after CN; public output remainszero and camera/new-stream locks remainheld. CN's prior four-placement integration remains historical accepted evidence; CO integrates one placement per source.

NEXT **E011CP**: qualify the file-encoding policy API/consumer and original wrapper return, then remaining CRT/final publication/whole outer return/balanced release. Accepted execution stops at an owned API adapter before any adapter instruction or policy result. No guessed-success numeric/TLS/policy substitute or new logger admission; CFE600 still raises. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts unchanged; zero Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CO](../experiments/E004-front-ir-vd55g0/e011co-original-api-resolver/README.md).

## E011CN original CRT integration into camera startup — BOUNDED PASS

The original camera entry 0x36CBA0 with source-produced CRT objects reaches the stop before 0xCB9C10 in 12 unmodified source/placement cases across three pinned inputs. Twelve complete original 0xCC6078 stream-allocator returns pass with independently modeled entire 88-byte streams. The return is an 8-byte argument0 pointer record, not a direct stream pointer; its two stores and adjacent stack bytes are exact.

All 96 CRT owned-store chunks and six first-use image stores match. Independent entire CRT arena/image and unchanged camera-arena/inner/outer checks pass. The CRT global index8 lock is released; the newly allocated stream and camera outer locks remain held at this bounded stop. Inherited 180 statistics records, 1440 statistics initializers, 292 core initializers and 540 total GetTag lookups pass. The three four-entry CRT bootstraps also pass; their execution order and OS heap/single-thread lock contracts remain explicit owned fixtures.

NEXT **E011CO**: qualify original dynamic DLL-loader/module/API ownership. Accepted execution stops before the LoadLibraryExW import at 0xCB9C10 / IAT 0xF7E310. Complete CRT/loader environment, original TLS 0xCFE600, actual OS locale/standard handles, final publication, whole return and balanced stream/camera lock release remain open. No guessed-success loader/numeric/TLS substitute or new logger admission. Full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts unchanged; zero Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CN](../experiments/E004-front-ir-vd55g0/e011cn-crt-startup-integration/README.md).

## E011CM original CRT object producers — BOUNDED PASS

Four unchanged original CRT routines return across eight owned cases: four placements, default count 512 and explicit preset count 128. Independent whole mapped-image/arena models pass for 512 entire 72-byte indexed records, 24 entire 88-byte static stream objects and eight full pointer vectors. All 180 source image stores, 656 logical OS mutex initializations and 16 guarded allocations match. Eight existing-table lookups allocate/initialize nothing and balance their locks; 24 invalid OS ownership requests are rejected.

Correction: global 0x16A2A50 is a 32-bit count, 0x16A2A58 a pointer vector, and 0x16A2A90 an indexed table. Their original producers return under explicit owned heap and logical single-thread OS contracts. The original global mutex initializer includes 0x16A3000. These contracts do not prove Windows mutex bytes, concurrency, actual standard handles, locale or full CRT/loader initialization.

NEXT **E011CN**: integrate exact original producers into owned outer-entry, qualify runtime CRT deltas/lock ownership, then final output publication, whole outer return and balanced release. This isolated CRT matrix does not extend E011CL's accepted camera-entry prefix. Original TLS 0xCFE600 stays unqualified and raises; no numeric/TLS success substitute or new logger admission. Full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts are unchanged. Zero camera Starts/reboots/production C/kernel changes/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CM](../experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/README.md).

## E011CL original conditional source context — BOUNDED PASS

Original entry `0x36CBA0` reaches the stop before `0x36DE04` in 24 cases: 12 unmodified and 12 explicit owned destination-poison fixtures across three pinned sources and four placements. The new 428-byte conditional portion executes unchanged original instructions. Serialized scene-change bank flags, values and names independently select record 1; source counts are 3/3/4, with guarded arrays of 528/528/704 bytes and 176-byte records. Exact comparison arguments and three context read origins pass.

All 144 original stores match the six predicted inner fields. Independent whole 606264-byte inner and whole-arena comparisons admit no other changes or new conditional allocations/releases. Inherited 360 records, 2880 statistics initializers, 584 core initializers and 1080 total GetTag lookups pass with caller/TLS, image, native heap, serialized source and allocation guards. Statistics+40 and mode+91952 remain attached; outer unchanged, output zero and owned single-thread lock held.

NEXT **E011CM**: qualify original CRT initialization/global/locale/OS ownership before final public output, whole return and balanced lock release. A static scan identifies candidate `0xCB3260` writing globals `0x16A2A50/58`; its execution, source objects and OS contract remain unqualified. Alternate context branches, full bank/metering-name producers, child payload semantics and live Default/filename/reuse/destruction remain open. No guessed locale, null-page mapping or numeric/TLS success substitute is admitted.

Golden boot and all three payload hashes, plus both historical checkouts, are unchanged. Zero camera Starts/reboots/C/kernel/image tests. Native rear runtime remains denied pending full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical gates. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CL](../experiments/E004-front-ir-vd55g0/e011cl-conditional-source-context/README.md).

## E011CK original source objects and module binding — BOUNDED PASS

Original36CBA0 entry through stop before36DC58 passes24 cases:12 unmodified+12 owned scalar poison fixtures. Independent entire606264-byte inner and complete1088/120 primary object models verify original attachments at inner+16/+24,408 exact inner stores/408 guarded allocations.48 actual aecxface/aecxmetering returns match core cache26/31;72 original accessors/72 original helper returns/24 original strcmp equal returns pass. F5DF00 is comparison, not memcpy. Inherited360 records/2880 statistics initializers/584 core initializers/1080 total GetTag lookups and whole-memory guards pass. Statistics+40/mode+91952 retained to stop; outer unchanged/output zero/lock held. Full child semantics/reuse/live Default producers remain open.

NEXT **E011CL**: conditional source context fields after36DC58, then CRT OS/global/locale ownership before final publication/whole return/balanced lock release. First-source36DE04 context and earlier second-CRT-lock/null-global reads remain excluded; no guessed locale/null mapping/numeric/TLS success substitute. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel/image tests. Native rear DENIED pending full bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CK](../experiments/E004-front-ir-vd55g0/e011ck-source-object-and-module-binding/README.md).

## E011CJ original post-attachment baseline reset — BOUNDED PASS

Original entry36CBA0 through stop before36D784 passes24 cases:12 unmodified and12 explicit owned poison fixtures across3 sources/four placements. Independent entire606264-byte inner and full-arena deltas verify72 original clears/1224 scalar store chunks and the internal inner+91816 -> inner+92976 link. Statistics+40 and mode+91952 attachments are retained to this stop; outer unchanged/output zero/lock held. Inherited360 records/2880 statistics initializers/584 core initializers/1032 cache lookups and whole-memory guards pass. Poison checks validate resets, not real object reuse or live Default producers.

NEXT **E011CK**: additional original object/module/context/cache producers after36D784, then CRT ownership/environment before final publication/whole return/balanced lock release. Excluded CRT exploration identifies null image globals16A2A58/16A2A50 before CC6140 reads address24; second CRT-lock fixture remains excluded, no guessed locale/null mapping. Actual live Default/filename/destruction/reuse and full optional semantics remain open. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel/image tests. Native rear DENIED pending full bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CJ](../experiments/E004-front-ir-vd55g0/e011cj-baseline-state-reset/README.md).

## E011CI original statistics and mode configuration attachment — BOUNDED PASS

Original `0x36CBA0` entry through the stop before `0x36D63C` passes 12 cases. The1664-byte statistics manager is attached at inner+40; the separately source-allocated96-byte configuration object is attached at inner+91952. An independent entire606264-byte inner delta allows only those two qword writes after the E011CH prefix; the72-byte outer is unchanged and public output still zero. Complete224-byte395940 returns with its actual96-byte receiver;24 original interface accessors,36 mode-record factory calls and36 record accessors pass. Inherited180 independent records/1440 statistics initializers/292 core initializers/516 cache lookups and whole-memory guards pass; numeric callbacks unchanged.

NEXT **E011CJ**: remaining post36D63C configuration fields and diagnostic/C-runtime locale environment, then final public output/outer-inner link, complete outer return and lock release. The second CRT-lock model/CC6140 unmapped locale read and first-source extended36DC58 probe are private excluded exploration, not accepted proof. Actual live Default producers/filename/destruction/reuse and complete optional field semantics stay open. Golden boot `e9983770-a981-49f9-a9f2-2fe081b5863d`/all3 protected hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel changes/new Linux image tests. Native rear DENIED pending remaining bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back baseline first; optional AI/effects/HDR/catalogue deferred. See [E011CI](../experiments/E004-front-ir-vd55g0/e011ci-outer-return-publication/README.md).

## E011CH original outer entry and actual-inner statistics — BOUNDED PASS

Original `0x36CBA0` entry through the stop before `0x36D3DC` passes 12 cases using the actual source-created inner/interface/core. Both complete statistics routines return; 180 independent entire 152-byte records, 1440 original statistics initializers, 292 core initializers and 516 cache lookups pass with whole-memory guards. Saved input is frame+32, frame+40 is diagnostic TLS and output is saved in X26. The first-kind4 search loop and nine 48-byte record vectors are exact. Explicit owned single-thread OS-lock and earlier diagnostic fixtures remain limitations; numeric callbacks are unmodified.

NEXT **E011CI**: continue after `0x36D3DC` to final inner-manager attachment, output publication and complete outer return/lock release. The current stop still holds the lock and leaves final output zero; whole outer/live Default producers/filename/destruction/reuse remain open. Golden boot `e9983770-a981-49f9-a9f2-2fe081b5863d` and all three payload hashes are unchanged; zero camera Starts/reboots/kernel/C changes/new Linux image tests. Native rear runtime remains DENIED pending remaining full bootstrap/preflight, RS, independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical gates. Clean front/back baseline first; optional AI/effects/HDR/catalogue deferred. See [E011CH](../experiments/E004-front-ir-vd55g0/e011ch-outer-startup-context/README.md).

## E011CG original inner binding and retired caller inputs — BOUNDED PASS

Original caller slice36D03C..36D27C passes12 source-created606264-byte inner/interface/core bindings across3 sources/four placements. It takes the first kind4 descriptor, then requires24 bytes; valid first-match indices1/2/5/8 pass. Exact original creator arguments are selected descriptor, inner+93032, parameter list and inner+8 output.48 caller-input regions and old stack are overwritten;12 subsequent unchanged setups, full caches/516 postretirement lookups and original interface accessors read no retired caller input. Whole preexisting arena/native/source immutability, core delta and guards pass;292 original numeric initializers are unchanged. Initial and postretirement caches total1032 lookups. Full inner field semantics/outer/statistics bootstrap and filename/destruction/reuse remain open.

NEXT E011CH complete ordinary outer startup and saved caller/context/TLS ABI after core return, then full statistics initialization using the actual original inner. Extended statistics probes lacked saved caller/diagnostic state and are excluded; no unproven numeric or logger substitute is admitted. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CG](../experiments/E004-front-ir-vd55g0/e011cg-inner-descriptor-lifetime/README.md).

## E011CF complete original core creator and interface — BOUNDED PASS

Full4980-byte3A8BE0 returns12 original320-byte interfaces/5152-byte cores under explicit owned count0 descriptors. Full516-byte3C8380/3376-byte3D4BD0,24 cache/bank updates,1032 exact cache lookups,24 unchanged skips and292 source-requested element initializers pass. Complete required core/setup delta, caller/old source immutability and guarded arenas pass. Actual source-created interface/core now supply12 full statistics setups,180 independent152-byte records and72 positive/72 exhausted full ordinary queries. Seven mode mirrors are byte stores; source initializer counts differ18+3+3 vs18+3+4. Numeric callbacks unmodified. Whole optional-bank field semantics/destruction/reuse remain unqualified.

NEXT E011CG complete ordinary outer36CBA0 and incoming/live Default descriptor, inner/context/opened filename lifetime. Full core creator is closed only under explicit owned inputs; whole outer/source bootstrap and RS/hardware gates remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CF](../experiments/E004-front-ir-vd55g0/e011cf-full-core-startup/README.md).

## E011CE full source cache and ordinary internal type search — BOUNDED PASS

Complete original1776-byte3CA4A0 producer passes12 returns across3 sources/four owned core placements:516 actual nonnull GetTag returns/exact cache stores,324 guarded32-byte temporary name allocations/releases, exact entire core delta and all preexisting native/source/manager bytes preserved. Source24-byte manager/mode/count/extra descriptor is explicit owned count0; full344-byte cache feeds12 full setups/180 independent records. Ordinary inner372FB4/373044 source initializes type0 and increments through6 only on failure, role0/output92.72 successful full queries write92;72 exhausted owned-empty-list queries give504 failed manager attempts, write0 and preserve output despite wrapper status0. Numeric callbacks unchanged. Earlier W26 request-producer gap is closed for these source paths; source constants were not supplied by the empty input fixture.

NEXT E011CF full original core/outer bootstrap and constructor descriptor provenance. Complete4980-byte3A8BE0,516-byte3C8380 setup beyond copied descriptor/cache, actual live Default descriptor/inner receiver/context/opened filename remain open.43 lookups qualify cache population, not all optional module fields; AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CE](../experiments/E004-front-ir-vd55g0/e011ce-full-source-cache-and-request-search/README.md).

## E011CD independent statistics record and attachment fields — BOUNDED PASS

Three original source files/four placements pass180 complete152-byte constructor and final records, plus180 original attachment setters with independent exact full object/ring deltas. Each allocation source is one actual loaded72-byte corestatsconfig record. Setter X1 is that original source pointer; source+16 chooses ring base216/40+48*selector, distinct from constructor normalization of source+8. Source-tail64:72 lands at object116:124 only after setter return. Full12 setups and72 ordinary post-setup query chains retain complete heap/canary/source immutability checks; numeric callbacks unchanged. E011CC's independent attached-record field gap is closed; historical evidence remains intact.

NEXT E011CE actual ordinary input-list/type producer and full core/outer ownership.372FB4/373044 source paths use role0/92 output bytes and W26 type;36CF30 is an interface store, not request producer. Live normal request, Default descriptor/inner receiver/context/opened filename, full constructor/cache producer remain open. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. Optional AI/effects/HDR/catalogue deferred. See [E011CD](../experiments/E004-front-ir-vd55g0/e011cd-statistics-record-field-lineage/README.md).

## E011CC coherent source statistics setup — BOUNDED PASS / E011CB association corrected

Source constructor3A9770 calls setup3C8380 with primaryCore+8. Correct coherent modules: aecxcorestatsconfig secondaryF18->primaryF20; aecxhwstatsconfig secondaryFE8->primaryFF0. E011CB meterweight is primaryF28; its reader/layout proof remains valid but its consumer association is superseded. Six original selected GetTag/cache fragments execute against three original loaded source managers with a controlled Default descriptor. Full39FAF8 setup passes12 runs/four placements,180 unique attached152-byte records,1440 original element-initializer returns and72 subsequent full ordinary queries; complete heap deltas/source immutability/canaries pass. All57 selected configuration records and typed channel-name/extensions pass complete native layout comparisons. Full loader2456 dispatches is not all-module field qualification.

NEXT E011CD independent attached-record field lineage and actual ordinary request role/type producer, then core/outer bootstrap. Whole constructor/cache producer, live Default descriptor/inner receiver/context/opened filename and attached-record independent semantics remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero new Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS count/whole-frame offset, full bootstrap/preflight, independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011CC](../experiments/E004-front-ir-vd55g0/e011cc-coherent-source-statistics-setup/README.md).

## E011CB ordinary metering configuration — BOUNDED SOURCE PASS

E011CB qualified the typed `aecxdb1dmeterweight` reader. E011CC corrects its consumer association to primaryCore+F28: the source producer uses secondary receiver primaryCore+8, so its relativeF20 store is not primaryF20. Its original registered368-byte prototype dispatches full parent1C0A80. Three original source contexts/factories/builders produce181,625 exact symbol readers; four output placements each give12 original parent returns. Complete80-byte payloads, revision/priority/context/descriptions and48 complete4120-byte native records pass196,800 exact numeric bytes, immutable source/context/preexisting arena and guards. Nine owned preflight child-reference rejections occur before native execution. No new semantic parser stub; historical failed capacity/mapping explorations excluded.

This historical NEXT is superseded by E011CC: following39FAF8 now uses the corrected corestatsconfig and hardware modules; required request role/type and actual live inner/context remain open. Whole core/outer bootstrap and hardware parity remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero new Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS count/whole-frame offset, full bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011CB](../experiments/E004-front-ir-vd55g0/e011cb-ordinary-metering-configuration/README.md).

## E011CA source statistics collection and source-grid selection — BOUNDED PASS

Original caller fragment36D338–36D3D8 creates1664-byte manager and two20-slot rings (160 bytes each), then complete ConfigureHWStats39F070 builds the primary list from original source counts. Primary pointer608/head610/used614/capacity618; secondary620/628/62C/630. Three pinned parents have4/9/1,4/9/1,4/7/1 grid/hist/BFW entries:14/14/12 objects. Four placements give12 builds/160 original Init returns, checked at entry and caller return, with immutable source/cache and allocation guards; numeric callbacks unmodified. Core module placement/flag storage and caller prefix remain owned interfaces.

72 full ordinary engine/outer/original-core-TLS-setter/inner/manager/grid queries against the full source list pass written92 and source weights;72 descriptors reject. Empty owned requests0/0 select the fourth source grid through last-matching-role fallback.36 direct source-type3/4/5 requests select first exact records0/1/2, including repeated type3; direct manager return/payload is distinct from inner descriptor written count.84 original append boundaries cover empty/last/wrap/full/overfull/zero capacity with complete heap deltas. Earlier incomplete ring fixture lacked proper capacity; not an OEM startup failure. Historical evidence unchanged.

NEXT E011CB source-only ordinary39FAF8 following setup, required request role/type and core module/caller ownership. Whole outer constructor, actual live primary request and inner receiver/context/opened filename remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, no new Start/reboot/C/kernel/reachable integration. Native rear DENIED: RS normal count/whole-frame offset, complete bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity open. No new Linux front/back image test. See [E011CA](../experiments/E004-front-ir-vd55g0/e011ca-rear-source-statistics-collection/README.md).

## E011BZ original grid Init and initialized query — BOUNDED PASS

The original full grid Init3A0D70 and normalizer388630 now precede the query. Three pinned source readers supply12 grid records; four placements/three context patterns/two selectors pass288 initialized typed queries, plus24 descriptor rejections. All312 Init/helper returns have nonzero source-derived masks. Full heap deltas, source cache/typed child and query/primary-conversion weights pass; numeric callbacks are unmodified. Init's observed return register matches its normalized field; a status ABI is not assumed.

Proper Init reaches39EC68, verified as a process-wide diagnostic callback from16A4230. The earlier mask-zero fixture's numeric classification did not cover this active branch; E011BZ handles288 calls as explicit logging. Historical private/model results remain unchanged. One-primary-grid selection/outer-inner-core ownership remain fixtures; full collection/constructor and actual live receiver/context are open. Incomplete broad constructor/ConfigureHWStats attempts are excluded, not OEM failures.

Golden e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, zero new Start/reboot/C/kernel/reachable integration. NEXT E011CA source-only normal collection capacities/append guards/role-type input and primary selection via39F070/39FAF8 and36CBA0 caller. Bound required ordinary consumers; optional AI/effects/HDR/catalogue deferred. Native rear DENIED pending RS normal count/whole-frame offset, full bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011BZ](../experiments/E004-front-ir-vd55g0/e011bz-rear-source-grid-initialization/README.md).

## E011BY source query forwarding and corrected profile check — BOUNDED PASS

E011BX's reported numeric profile mismatch was our source-generator error: serialization mode_id at wire40 was used instead of profile-node mode_symbol_id at wire44. The corrected source check matches all seven common fields in all four saved live modules (28 comparisons); 11 rejection checks pass. Original mode-loader prefixes, one typed root reader constructor and profile callback pass for three source files/four placements (12 cases). Alignment1 is owned; all symbol readers and OS-open filename identity remain outside this proof. Historical private capture/model is unchanged; future generator corrected.

3,552 original complete engine/outer/context-setter/GetParam/manager/grid-getter chains pass in owned fixtures. 1,776 include original core TLS setter3AE320, with zero backend context stub and identical92-byte outputs to the inert-setter comparison. Actual outer36E460 forwards through inner vtable+32 setter374050 then+24 GetParam372E40. Outer+40 is inner algorithm object; inner+40 is manager; outer+68 is context ID. Numeric callbacks unmodified; checked dispatch/allocation/TLS/logging remain controlled. Whole startup construction and actual live inner vtable/context/loaded-code qualification remain open.

Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 protected hashes unchanged; zero new camera Start/reboot/production kernel or reachable integration. E011BX identity remains consumed. NEXT E011BZ source-only ordinary producer36CBA0, outer GetParam store36CF30, inner/core/context ownership and stats-manager bootstrap39F070/39FAF8/370728. Avoid repeated closed cache/GetTag/copy probes. Native rear DENIED: RS normal count/whole-frame offset, full bootstrap/preflight, independent WM16 consumed-IOVA/DMA/IOMMU retirement and optical parity open. No new Linux front/back image test. Optional AI/effects/HDR/catalogue deferred. See [E011BY](../experiments/E004-front-ir-vd55g0/e011by-rear-query-forwarder-context/README.md).

## E011BX live cache/frame join; source/receiver scope partial

One consumed Windows rear4K Start/Stop completed450 valid handles. Four named source-array/Init pairs and both typed queries (written92, types10/21) supply the actual FIRST frame+424, converter and first2072 publication with matching pointers/thread/bytes.11loaded ranges/table qualified beforeStart; zero observer diagnostics. Same-SP11 Linux bounded validation and eight corruption negatives pass.

Seven-field source claim rejects profile high word+76; six fields match one pinned candidate. Actual outer callback36E460 differs from owned fixture372E40; full loaded524-byte receiver/inner ABI not qualified. Retained descriptors correct eight MASM decimal-offset printf fields; original logs preserved. Converter return register has no qualified status ABI. Whole source bootstrap/profile policy remains open; do not use captured constants or replay consumed E011BX-20261002-0030A.

Golden e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, idle; debugger/task cleaned. NEXT E011BY source-only36E460 delegation/actual ABI and numeric metadata76 construction. Native rear DENIED, RS/bootstrap/WM16/optical gates open, no new Linux front/back image. Clean baseline priority, optional features deferred. See [E011BX](../experiments/E004-front-ir-vd55g0/e011bx-rear-first-aec-source-query/README.md).

## E011BW source-produced cold AEC weights — DETACHED PASS

Three qualified Default tuning roots have identical weights in all twelve grid records. A new portable integer decoder requires the four records to agree and rejects unsupported shapes/values. Cold AEC weights and AWB quad now come from tuning in the detached C replay; incoming cold bytes are deliberately255 and must be overwritten. GCC/Clang ASan/UBSan each pass5,616 decoder checks and510,380 full startup/preflight assertions, with zero semantic register differences in all four packets.

592 complete original engine-query/GetParam/manager/grid-getter chains pass in owned memory across74 cases/four placements/selectors12 and20. Numeric callbacks are unmodified; dispatch/allocation/TLS/logging interfaces are explicit fixtures. The five-argument wrapper's output array is argument3, count argument4. Descriptor allocated bytes+8, written bytes+12 and type+16 are u32.24 wrong-type/undersized cases return status0 but write nothing; require the full written92 contract, never status alone.

This proves invariant Default source producibility, not the live FIRST source-cache-to-prepublication-frame pointer join or opened filename/profile. E011BV's metadata pointer/copy proof remains closed and both previous Windows identities consumed. NEXT E011BX qualify both full typed query returns and their actual cache/frame identity into first83AA1C/SP+1264 -> SP+3152, keeping the second temporary separate. Do not repeat closed GetTag/copy or use captured scalars as producer policy.

Golden boot0f8a8389-9627-42e7-9c69-98b550e5814e/all3 protected hashes unchanged, camera idle/NTFSunmounted. Zero new Start/reboot/kernel build/reachable integration/MMIO/sleep. No new Linux front/back image test; native rear runtime remainsDENIED. Clean baseline first, optional AI/effects/catalogue deferred. Required RS count/whole-frame offset, complete source bootstrap/preflight and independent enabled WM16 retirement/optical gates remainOPEN. See [E011BW](../experiments/E004-front-ir-vd55g0/e011bw-rear-source-cold-aec-weights/README.md), SOURCE-SAFE/INTEGRATION-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011AT AWB SetParam retained BG — CALLBACK EXCLUDED / GOLDEN RETURNED

One original Windows rear 4K run completed 714 valid handles, one successful Start and clean Stop. User-mode CDB explicitly detached/exited0 and the manual task was removed. The live original CAWBMain::AWBSetParameter callback is RVA68C090 through wrapper+28 -> actor+0 -> vtable+08; its same-thread return result is0 and the40-byte parameter record matches the outer call.

The actor's92-byte retained BG already has quad1 at callback entry and remains byte-identical through callback return, outer return, pre-GetParam2 and the later sampled helper689228. Publication5000001D/size128 and first request1 consumer carry1. Thus callback68C090 is not the cold initializer. The generated outer handler had one excess dereference, so its outer object/code/IO dumps are excluded; the chain was corrected while the same call remained held. The ARM64 data watch had no free slot and was removed, so no first writer is claimed.

NEXT bracket the wrapper from entry681C40 through pre-dispatch83180C, then construction/configuration if quad is already1 at wrapper entry. Do not repeat68C090 or hardcode1. Golden Linux7.1.5-sp11-render-parity-v4+ boot25a899ad-ae69-418f-86fb-d110b5bd84d0 is idle, saved FullIOv19c, next_entry empty and NTFS unmounted. Cold AEC weights, exact AWB retained initialization, RS count/offset authority, final bootstrap and WM16 retirement proof remainOPEN; native rear runtime DENIED. See [E011AT](../experiments/E004-front-ir-vd55g0/e011at-rear-awb-setparam-retained-bg-observer/README.md), VALIDATION-SAFE and RESULT. Identity consumed.

## E011AS explicit inactive cold gamma — OFFLINE / ARM64 BUILD PASS

The cold gamma gate is now closed for the bounded four-packet startup. Four additive provider derivatives and a kernel-compilable producer express inactive gamma without a dummy table. Cold selector2 production is skipped/rejected, normal gamma remains required, and packet/register/activity contradictions fail closed. The actual full composer and E011AR preflight use the explicit absence producer.

GCC/Clang ASan/UBSan each pass510,371 assertions with zero differences0/0/0/0. Nine activity negatives,38 atomic policy negatives,32 nonzero inactive-LUT negatives and9 producer-failure zeroing cases pass. Fresh isolated ARM64 W=1 v2 build haszero warnings; moduleSHA41d169f5d5d9f24cf429a6e922eca49899a5c60b9034965ea9810da97935959e, separately hash/vermagic checked via Fabric. First build preparation failed before compiler due to a host-only seed dependency; v2 is separate. Both builders/preparer consumed. No install/load/runtime/reboot/sleep/MMIO; Golden bootc0e263ed-7319-4f69-8f10-4d51f20cd1a1 remains idle.

NEXT remaining deterministic startup policy origins: E011AQ retained AWB BG initialization, AEC cold weights and RS count/offset authority. Then final full bootstrap/preflight and independent WM16 same-generation IRQ/IOVA/DMA/IOMMU retirement proof. Do not reopen the inactive cold gamma gate or repeat the closed GetParam2 copy. Native rear runtime DENIED; no live optical improvement claimed. See [E011AS](../experiments/E004-front-ir-vd55g0/e011as-rear-explicit-inactive-cold-gamma/README.md), INTEGRATION-SAFE, BUILD-SAFE, AUDIT-SAFE, BUILD-ATTEMPTS-SAFE and RESULT.

## E011AR packet-isolated Linux runner — BUILD-ONLY PASS

The new unreachable runner now consumes four E008o packet semantic records and Linux-owned command backing, replacing the archived shared-state runner shape. Materialization completes before owner acquisition/exposure; exposed commands are never rewritten. The consumed wrapper pins uncertain DMA and requires reboot after exposure. Partial RT-CDM/BUS/CSID/CSIPHY/sensor starts enter conservative emergency-stop paths before the attempt.

GCC/Clang sanitizer lifecycle tests each pass4,091 assertions with58 injected failing operations; these providers simulate hardware contracts. The exact preflight with the real composer each passes510,045 assertions and zero differences0/0/0/0. Fresh isolated ARM64 W=1 build haszero warnings; moduleSHA5545aaff892fb87eade9be4e1168f391b6cc76dab9ccd88aa213fec4b0f31604, separately hash/vermagic checked through Fabric. No install/load/runtime/boot/sleep/MMIO change. Golden bootc0e263ed-7319-4f69-8f10-4d51f20cd1a1 remains idle. Builder/preparer consumed.

NEXT complete deterministic startup policy origins (E011AQ upstream retained BG, AEC weights, RS count/offset authority) and explicit inactive cold gamma, then final integrated preflight audit and independent WM16 same-generation IRQ/IOVA/DMA/IOMMU retirement proof. Native rear runtime DENIED; do not activate the candidate or old E008n shared-state runner. See [E011AR](../experiments/E004-front-ir-vd55g0/e011ar-rear-packet-isolated-runner/README.md), LIFECYCLE-SAFE, INTEGRATION-SAFE, BUILD-SAFE and RESULT. This checkpoint changes integration code; Linux optical/image quality remains unproven.

## E011AQ AWB delegate/retained BG — LIVE COPY VERIFIED / GOLDEN RETURNED

One Windows run completed 711 valid4K frame handles, clean Stop, explicit CDB detach/exit0 and task removal. Five outer probes resolved before Start; three inner probes resolved after manual qualification, before the same GetParam2 call. Eight events/26 private records/2720 bytes validate. Two mistaken pre-capture input-as-list qualification queries are retained; corrected output1 capture has zero diagnostics. No camera retry or unattended qualification claim.

Actual original callback68E5A0 (CAWBMain::AWBGetParameter) and all six vtable targets are byte/source verified. Retained actor BG+FB744 already has quad1 at+FB798 before GetParam2. PopulateOutput68F490 returns0 at68E8D8 and copies all92 retained bytes into previously zero IO+CB4; outer return/publication/first cold request1 agree. Nested channel is output1/type1/16-byte container ->15 descriptors atIO+2080 ->BGindex5/type5/92 bytes. Input2/type2/12 bytes is a separate information record.140 original owned-memory BG copy slices preserve full u32/source/neighbors; full algorithm emulation return is not claimed.

NEXT trace upstream retained BG initialization: source SetParam wrapper681C40 -> actor/vtable slot08 ->68C090; tuning/mode helper689228 references bgStatsConfigV1. SetParam IO preservation does not exclude retained-record writes. Trace registration/configuration/construction and bracket retained BG there; do not repeat GetParam2 copy or hardcode1. Numeric initialization policy/full bootstrap/WM16 retirement OPEN; native rear runtime DENIED.

Golden boot c0e263ed-7319-4f69-8f10-4d51f20cd1a1, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. No production C/build/Linux runtime/kernel debug/BCD/MMIO change; offline parity remains0/0/0/0 conditional on input records. See [E011AQ](../experiments/E004-front-ir-vd55g0/e011aq-rear-awb-delegate-bg-observer/README.md), VALIDATION-SAFE, COPY-SAFE, SOURCE-SAFE and RESULT. Identity/builders consumed.

## E011AP earlier AWB calls — GETPARAM2 TRANSITION VERIFIED / GOLDEN RETURNED

One Windows run completed866 valid4K frame handles, clean Stop, explicit user-mode CDB detach/exit0 and task removal. Eight resolved one-shot probes ran; GetParam2 deliberately stopped for qualification. No capture diagnostics occurred. Quad stayed0 and all92 BG bytes stayed identical through SetParam; GetParam2 at831920/831924 returned0 on the same thread/processor, changing29 bytes and setting quad1. Its after record equals pre-selector12 across92 bytes; publication and first cold request1 carry1. Numeric value policy remainsOPEN.

Delegate correction: wrapper+28 -> object+0 -> vtable+10. The direct object+10 target read is excluded; input descriptors are16 bytes, so the extra40-byte input-table tail is also excluded.18 files/1824 bytes yield17 valid source records/1656 bytes. Both original wrapper targets match128 bytes. Captured object points to original vtable133A390; pinned source candidate GetParam68E5A0 is CamX::CAWBMain::AWBGetParameter, not yet live callback-code verified. Next capture the actual slot/code and nested type2/12-byte input payload, then trace retained BG initialization. Do not hardcode1.

Golden bootf4982efd-f612-4819-b1f5-de4820807375, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. No production C/build/Linux runtime/kernel debug/BCD/MMIO change. Offline parity remains0/0/0/0 conditional on source inputs. Exact cold value policy/full deterministic bootstrap and independent WM16 retirement OPEN; native rear runtime DENIED. See [E011AP](../experiments/E004-front-ir-vd55g0/e011ap-rear-awb-earlier-call-observer/README.md), VALIDATION-SAFE, ORIGIN-SAFE and RESULT. Identity/builders consumed.

## E011AO AWB initialization — LIVE ORIGIN NARROWED / GOLDEN RETURNED

One original Windows capture completed 859 valid 4K frame handles and a clean Stop. Both user-mode CDB sessions explicitly detached/exited 0; the manual-only task was removed. The actual driver owner had five resolved probes before Start after FrameServer replaced its initial process.

Quad was already 1 before initialization selector12 at 0x831964. Its same-thread/processor return at 0x831968 preserved all 92 BG bytes; publication and four consumers (request IDs1/1/2/3) carry1. The actual target is original CamX::AWBGetParam RVA 0x681B00; 128 captured instruction bytes match the pinned image. The delegate object is wrapper+0x28, callback slot+0x10, not captured by the 32-byte wrapper header. Selector12 is excluded as this invocation's origin; exact earlier writer/value policy remainsOPEN.

14 records/1324 bytes were retained privately; one auxiliary publication-node BG read has wrong object attribution and is excluded, leaving 13 source records/1232 bytes. Conditional pair/publication probes required direct control; this run does not qualify unattended observer behavior. A queued post-Stop informational query had an unresolved symbol; capture records remain valid. No retry/kernel debug/Linux camera/build/MMIO/submission occurred.

NEXT bracket the earlier SetParam 0x83180C/GetParam2 at 0x831920 and identify the underlying wrapper delegate; nested expected-output inputs may carry BG writes even when selector2 lacks a direct BG output. Keep all value-policy, cold-gamma/full-bootstrap and independent WM16 retirement gates open; native rear runtime DENIED. Golden Linux boot 68454cbe-a55e-430c-8699-206bf84435bb, saved FullIOv19c, next_entry empty, NTFS unmounted, camera idle. See [E011AO](../experiments/E004-front-ir-vd55g0/e011ao-rear-awb-init-algorithm-observer/README.md), VALIDATION-SAFE and RESULT. Never reuse the consumed Windows identity or prior builders.

## E011AN cold BG origin boundary — ORIGINAL OWNERSHIP PASS / PARITY UNCHANGED

The original AWB descriptor helpers expose a 92-byte BG algorithm output at IO+0xCB4 while preserving its contents. GetParam selector 12 uses output index 10/type 10; selector 2 does not expose BG. Initialization call/return RVAs 0x831964/0x831968 now identify the next concrete upstream boundary. FillBG carries the full IO+0xD08 field to record+0x4C; it does not generate the value. 184 original ARM64 calls pass in owned memory across four IO bases. This source boundary is NOT a physically trapped first writer or a closed numeric policy.

Full E011AM regression passes again: GCC and Clang ASan/UBSan each 509,829 assertions; semantic differences remain 0/0/0/0, and prior reports are byte-identical. No production C or kernel build changed. Initial AEC weights/AWB quad policy, normal RS/AFD count policy, whole-frame offset authority, explicit inactive cold gamma, complete deterministic bootstrap and independent WM16 generation-safe retirement remain OPEN; native rear runtime DENIED.

NEXT observe the bounded AWB selector 12 call and actual algorithm owner privately, then trace its first write/policy inputs and the independent AEC Usecase producer. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. No camera/boot/sleep/MMIO/submission occurred. See [E011AN](../experiments/E004-front-ir-vd55g0/e011an-rear-cold-bg-origin-audit/README.md), ORIGIN-SAFE, VALIDATION-SAFE and RESULT. Previous builders remain consumed.

## E011AM full offline startup comparison — ZERO DIFFERENCES / ARM64 BUILD PASS

Portable integer RS production now removes all seven remaining differences. Both original ARM64 adjustment and clean C match4,387 cases/35,096 fields per compiler; all three sampled pack shifts match original state+0x130. The detached binder preserves caller tags and unrelated modules, with70 binder and14 producer negatives. RS source schedule is0/1/2/2; all12 present RS register instances match.

The full four-phase provider replay now has zero semantic register differences:[0,0,0,0]. Prior BG, weights/quad, scalar, BF ROI/gamma, BPC and LSC/GTM/GIC checks remain exact. GCC and Clang ASan/UBSan each pass509,829 assertions. A fresh isolated ARM64 W=1 build has zero warnings, moduleSHA85c318c424d5b3380f884c2e28893dbe28d49c233c4d0874de9a95cd058a3d25, never installed/loaded.

This is offline parity conditional on independently observed semantic inputs. Cold BG weights/quad initialization, normal RS/AFD count policy and whole-frame zero-offset authority remainOPEN. Stripe policy is unsupported. Complete deterministic E008o bootstrap without observed caller inputs, explicit inactive cold gamma policy and independent WM16 same-generation IRQ/DMA/IOMMU retirement remainOPEN. Zero numeric differences do not authorize live rear ISP; runtime staysDENIED.

NEXT source-close the remaining caller-policy origins and inactive cold gamma before composing a complete deterministic bootstrap; independently prove WM16 retirement before any live rear ISP run. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. No camera/boot/sleep/MMIO/submission or platform change. See [E011AM](../experiments/E004-front-ir-vd55g0/e011am-rear-rs-full-startup-integration/README.md), RESULT, ARITHMETIC-SAFE, INTEGRATION-SAFE and BUILD-SAFE. E011AM and all prior one-use builders remain consumed.

## E011AL Bayer-grid weight/quad integration — PRIVATE PARITY AND ARM64 BUILD PASS

Portable integer L4 quantization now produces AEC Q4 luminance weights and the AWB quad flag from E011AK semantic input records. Both original ARM64 pack functions match2,164 cases/8,656 fields per sanitizer compiler, including exact rounding boundaries. The detached binder validates both source identities and every caller startup tag before mutation;35 binding and22 producer negatives preserve output/state. It changes only AEC weights and AWB quad.

The full composer now matches all four previously different weight/quad register instances. Remaining differences drop11->7, by phase1/3/3/0, exclusively RS_STATS14. Prior36 BG geometry/threshold and26 scalar register instances, BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. GCC and Clang ASan/UBSan each pass509,582 assertions. A fresh isolated ARM64 W=1 build passes zero warnings, moduleSHA1b510b04dd119bd5c1e978b54829794bf02e7f0447c79f960e3e829cc0934f10, not installed or loaded.

Cold weights/quad are caller-owned observed consumer inputs: their initialization policy is stillOPEN. Normal producer field handoffs are source-verified. Later holds are detached state only because packets2/3 do not emit BG ranges. Complete source-produced E008o startup, explicit inactive cold gamma policy and independent WM16 same-generation retirement remainOPEN; native rear ISP DENIED. No Linux camera start, boot/sleep/MMIO/submission or platform change occurred.

NEXT source-close normal RS count policy and exact shift binding, implement portable RS production and require zero remaining differences. Cold weight/quad initialization authority also remains required for complete bootstrap. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. See [E011AL](../experiments/E004-front-ir-vd55g0/e011al-rear-bg-weight-quad-integration/README.md), RESULT, ARITHMETIC-SAFE, INTEGRATION-SAFE and BUILD-SAFE. Never rerun the consumed E011AL or previous one-use builders.

## E011AK Windows statistics inputs — VALIDATED, PORTABLE INTEGRATION NEXT

Fresh consumed E011AK-20260930-1025A completed one Start/Stop with860 valid4K handles. Nine probes resolved to the actual DeviceMFT owner before Start;49 bounded input events/106 private files were verified. Original ARM64 arithmetic privately reproduces40 BG geometry/threshold fields and21 RS count/color/region/offset fields. Eight AEC producer snapshots match24 normal weight fields; eight AWB producer snapshots match8 quad fields. Producer request labels are last observed IFE hooks, not independent AEC/AWB request identities.

Sixteen captured gain inputs are unity: E011AJ's live gain binding is closed for this sampled startup window. RS horizontal count changes at the second request1 consumer, then vertical count at request2, holding through sampled request7. RS color conversion is separate from module enable. Cold weights/quad initialization origin, normal RS count policy producer and exact RS shift binding remainOPEN. The full composer has not changed:11 differences by phase3/5/3/0 remain. Do not reuse a frozen RS config or infer policy inputs from retained registers.

CDB explicitly detached/exited0 and the manual-only task was removed. An initial literal Ctrl-C cleanup line had a syntax error; the clean second command cleared breakpoints and detached. Normal reboot returned Golden Linux7.1.5-sp11-render-parity-v4+, boot b74c0760-83bb-421f-ac4d-1efa4e297294, saved v19c, next_entry empty, camera nodes/modules/processes absent. Read-only NTFS recovery is unmounted. Raw records/logs/addresses remain private on SP11; no optical pixels saved. No new kernel build, install, Linux camera start or kernel debugging.

NEXT source-close cold weights/quad and the normal RS count/shift handoff, produce portable inputs and require zero remaining differences in the full private composer. Prior source provenance remains established. Complete E008o startup, explicit inactive cold gamma policy and independent WM16 retirement remainOPEN; native rear ISP DENIED. See [E011AK](../experiments/E004-front-ir-vd55g0/e011ak-rear-stats-input-observer/README.md), RESULT and VALIDATION-SAFE. Windows identity and previous E011AJ builder are consumed.

## E011AJ bounded L4 Bayer-grid geometry/threshold → L2 full startup integration (2026-09-30)

Portable caller-side AEC_BE/AWB_BG geometry/threshold production from existing cold/normal source inputs now runs through the real full startup composer. Original AEC/AWB arithmetic matches2,056 cases privately per compiler; shared original Titan680 capability confirms the fixed bounds. All36 present geometry/threshold register instances match. Eleven register differences remain in luminance weights, AWB quad synchronization and RS configuration. Unity-only threshold gain lacks independent live field binding; other policies remain unsupported. The detached integer kernel binder preserves all other fields/tags and rejects atomically. Both sanitizer compilers and a fresh isolated ARM64 W=1 build pass. Complete startup production, inactive cold gamma policy and independent WM16 retirement still gate native rear ISP. See [E011AJ](../experiments/E004-front-ir-vd55g0/e011aj-rear-bg-geometry-threshold-integration/README.md). No runtime caller or platform change.

## E011AI portable L4 neutral scalar → L2 startup handoff (2026-09-30)

Original E011X semantic inputs are recovered/verified privately on SP11. The independent ordinary-rear Bayer2 C11 producer matches 1,038 original arithmetic cases and binds source schedule[0,1,2,2] into the actual full composer. All26 startup scalar register instances match; remaining semantic differences are25 exclusively in AEC_BE/AWB_BG/RS statistics. Floating-point policy stays in user space; the kernel binder is integer-only, rejects before mutation and preserves tags/non-scalar fields. GCC/Clang sanitizer checks and isolated ARM64 W=1 build pass. This is bounded arithmetic/phase propagation, not complete AE/AWB algorithms or camera runtime. Statistics producer lowering, inactive cold gamma policy and independent WM16 retirement remain gates. See [E011AI](../experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/README.md).

## E011AH detached L4 AF rectangle → L2 BF ROI integration (2026-09-30)

The new caller-tagged, integer-only handoff lowers the accepted interior 5×5 zero-overlap AF/BAF geometry into actual E008o packet states before sealing. Full E011AG private replay now matches four BF selector1 payloads (1,200 bytes) and three normal selector2 gamma tables (384 bytes); packet0 and non-ROI fields are preserved. GCC/Clang sanitizer checks and isolated ARM64 W=1 build pass. The existing E009e measured first-normal scalar is an explicit L4 replay input; its upstream calculation and directly tagged AF-to-RT-CDM packet identity are not newly proven. Neutral scalar/statistics portable bases, explicit inactive cold gamma policy and independent WM16 retirement still gate native rear runtime. See [E011AH](../experiments/E004-front-ir-vd55g0/e011ah-rear-request-af-roi-full-integration/README.md). No runtime caller or platform change.

## E010z BHist startup seed lifecycle (2026-09-28)

The first rear BHist selector after a cold 4K start is now request-correlated and source-closed. IFENode::HardcodeSettings seeds the default BHist ROI from the active crop with integer 90% dimensions (width-floor(width/10), height-floor(height/10)); 4064x2286 gives 3658x2058. The first post-start selector is request ID 1 and consumes this cold seed. The same request-owned slot is then overwritten by the normal request-frame bulk config copy with full 4064x2286, and a later selector for request ID 1 consumes full crop. Port this as a startup/default seed plus normal per-request replacement, not a permanent 90% rule. This closes the E009g/E009h BHist origin/timing gap but does not authorize native rear ISP runtime; remaining first-frame stats and VFE1 WM16 retirement gates still apply. See [E010z](../experiments/E004-front-ir-vd55g0/e010z-first-selector-request1-transition/README.md).

## E009g explicit AEC BHist region handoff (2026-09-28)

Pinned DeviceMFT AEC stats processing supplies an ROI per request, and BHistStats16 validates/counts/packs it. A detached request-owned handoff through E006u reproduces the private 0xB26C word in all four startup packets: packet0 with an even 90% crop candidate, packets1–3 with the accepted full crop. Both reverse controls fail. The AEC algorithm producer of the first 90% input and precise request association remain open; no fixed runtime ratio or rear ISP arm. See [E009g](../experiments/E004-front-ir-vd55g0/e009g-rear-bhist-request-handoff/README.md).

## E009f candidate origin for the live first-normal AF zoom (2026-09-28)

The independently accepted rear widths 4064 CAMIF crop and 4076 OV13858 raw sensor yield float32(4064/4076) = 0x3F7F3F0F, exactly the physically observed E009e first-normal AF zoom. An offline parameterized ratio reproduces all four startup BF ROI selectors 300/300. This is an exact numerical convergence, **not** source proof that the original metadata producer computes this quotient. Trace AF set-param case0x15 writer and first-to-settled request timing before integration; native rear ISP runtime remains denied. See [E009f](../experiments/E004-front-ir-vd55g0/e009f-rear-crop-width-zoom-hypothesis/README.md).

## E009e live AF transient and exact four-startup BF ROI (2026-09-28)

A guarded same-SP11 original Windows rear4K session and external SP7 KD read-only user-mode AF execute probe observed one first-normal zoom float32 0x3F7F3F0F (0.9970559477806091), CAMIF 4064×2286, ROI type0, loaded HAF .25/.25; twenty later calls from the same normal caller used zoom1.0. The holder acquired 52 valid 4K handles in eight seconds; KD breakpoints were cleared and SP11 returned to Golden. E009e feeds the independently measured scalar through E008z/E009c/E008t/E007e to yield selector1 300/300 for each of four startup packets and one retained steady. The AF breakpoint carried no RT-CDM packet ID: startup1 association uses E008g order and final packet shape. Upstream zoom calculation and the other semantic plus VFE1 IRQ/WM16 DMA/IOMMU gates remain open, so rear native ISP submission stays denied. E009d .998 was a retrospective diagnostic and is superseded for this bounded scalar by this live observation. See [E009e](../experiments/E004-front-ir-vd55g0/e009e-rear-af-live-zoom-forward/README.md).

## E009c/d rear AF request handoff and transient diagnostic (2026-09-28)

E009c adds a detached request-scoped AF rectangle→BFStats25 5×5 DMI handoff over isolated packet states. The source-composed 25% default rectangle is byte-exact for startup2/3 and one sampled steady selector1; packet0 has its separate exact IFENode hardcode seed. E009d demonstrates a retrospective inverse-zoom scalar 0.998 for startup1 gives 300/300 bytes, whereas 1.0 gives 250/300; the scalar is calibrated from final DMI and **not** a live AF input. First-normal ROI type, CAMIF, loaded HAF fractions and zoom must be independently observed before adopting any transient policy. E008g orders packet1 after BUS enable and before CSID start, packet2 after the first ISP_START_DONE Epoch0; that is a stage distinction, not proof of which AF scalar changed. E008p remaining AEC/AWB/LSC/GTM startup seeds and E005m/n native VFE1 WM16 comp7 generation/DMA safety remain runtime gates. Rear ISP runtime stays denied. See [E009c](../experiments/E004-front-ir-vd55g0/e009c-rear-af-request-roi-handoff/README.md), [E009d](../experiments/E004-front-ir-vd55g0/e009d-rear-af-transient-zoom-equivalence/README.md).

## E008u rear BF ROI L4→L2 boundary (2026-09-27)

The accepted 4064x2286 active rear ISP crop gives an exact offline packet0 BF selector-1 payload through clean E008t/E007e: 25/25 private same-SP11 ROI records, 300/300 bytes [P comparison, S AF/IFE source, D Linux composer]. Normal packets1–3 retain geometric differences; IDs/flags match, packet1→2 shifts uniformly, and packet2/3/steady match in the bounded retained corpus. L4 normal AF ROI policy and BFStats25 validation/adjustment must be source-implemented before L2 packet materialization can claim final selector-1 parity. L3 rear DMA/runtime remains denied. See E008u README; no captured payload bytes or hashes are published.

## E005r correction: BF is type-1 CSID status, not the separate IFE snapshot

E005r restores the source-proven E004ph path after E005p over-connected the separate 0x24A30/0x1DC20 snapshot queue to BF. Original type-1 queue B reads CSID BUF_DONE_IRQ_STATUS+0x8C in zero mode, normalizes prepared+0x0C to record+0x08, and bit7 drives BF0x0F/FIFO8. E005q then observed 35 BF/FIFO/matcher events while the snapshot probe emitted zero rows. E005q also proves resource0x300D WriteMaster W=25/H=4; that 4 is height, **not composite group**. The OEM output-resource structure names its actual composite-group field at container+0x8C0. Live 0x300D group and exact FIFO8↔WM16 DMA/IOMMU retirement remain unproven; rear ISP stays denied.

## E005p: OEM interrupt domains source-locked; BF is TOP1 bit7, not direct BUS7

The exact same-SP11 OEM top half now has a source-locked four-word interrupt packet: TOP status0/status1 plus BUS status0/status1. BF software event 0x0f is created from raw TOP status1 bit7; the BUS words are separate. This resolves the apparent E005o contradiction without promoting a hardware-completion claim. The OEM full-IFE BUS window is VFE+0xc00, so its status reads are canonical VFE 0xc28/0xc2c, but its observed status writeback uses 0xc3c/0xc40 plus 0xc30. Pinned Qualcomm VFE680 calls 0xc20/0xc24 the BUS clears and 0xc3c/0xc40 frame-header config. Keep that divergence quarantined: do not transplant the OEM write sequence into Linux. Live resource 0x300d composite-group identity and independent WM16 DMA/IOMMU retirement still require a bounded external-SP7 trace.





## E005o: live BF/FIFO8/matcher chain closes; independent BUS7 witness still missing

A bounded Windows rear4K session under external SP7 KD produced 22 original BF events, 22 nonnull group8 FIFO entries and 22 nonnull outstanding-matcher returns; WM16 consumed-status was nonzero 42 times. The camera still completed a clean 8.026-second 3840x2160 NV12 session with 13 valid frame handles. This is the first live run where every observed BF event had both a real FIFO8 object and a nonnull matcher. Two selected OEM VFE BUS-status readers saw comp-group7 bit7 zero times, so those locations do not yet establish the independent WM16 DMA-retirement fence. Treat the zero as a probe-location/aggregation unknown, not proof of hardware failure. Same-frame/generation identity and DMA/IOMMU-safe reuse remain denied.

## E005n: isolated native VFE680 comp7 / WM16 observer

The accepted SP11 VFE680 owns one dedicated, non-shared platform IRQ and currently binds it to a no-op ISR. E005n compiles an isolated replacement that latches TOP/BUS status, recognizes BUS status0 BIT(7) as comp-group7, reads WM16 ADDR_STATUS0 before ACK, and then uses canonical TOP/BUS clear+global-clear. The observer never calls vfe_buf_done, VB2, DMA unmap/free or buffer reuse. Its BIT7 mask-arm helper is source-only and has no runtime caller. Fresh fix1 ARM64 qcom-camss build is zero-warning and Golden-vermagic compatible, but was never installed/loaded. This closes compile/IRQ-ownership feasibility only; live rear WM16 completion and safe retirement remain unproven.

## E005m: exact VFE680 BF/BAF hardware completion contract

Pinned Qualcomm VFE680 source independently maps **WM16 = STATS_BAF = composite group 7**. Group7 completion is **BUS IRQ status0 BIT(7)**; the BUS-v3 top half then reads WM16 **ADDR_STATUS0 (base+0x1E70)** as last-consumed address before the bottom half reports hardware DONE. VFE680 BUS mask/clear/status0 are **0xC18/0xC20/0xC28**, clear1 is **0xC24**, and global clear is **0xC30**. The same hardware table identifies **0xC3C/0xC40 as frame-header configuration**, resolving the old E004ox offset ambiguity: they are not canonical BUS IRQ clears. This is source convergence only; accepted SP11 VFE680 ISR remains a no-op and live rear WM16 comp7/FIFO8 generation/DMA-IOMMU retirement is not yet proven. See [E005m](../experiments/E004-front-ir-vd55g0/e005m-vfe680-wm16-baf-compgrp7-busdone-static/README.md).

## E005l — STAT metadata exposes aggregate queue4 key/tag, not BF queue8 requestId

[experiments/E004-front-ir-vd55g0/e005l-original-group3-stat-aggregate-key-tag-export-static/README.md](../experiments/E004-front-ir-vd55g0/e005l-original-group3-stat-aggregate-key-tag-export-static/README.md) source-locks the non-halting STAT metadata boundary. The common qccamisp producer feeds separate group4 COMBO_STATS and group8 BF rings from the same locally built descriptor only when each independent insertion succeeds. GROUP3 pops **queue4**, and its key/tag flow through raw25 normalization into custom metadata item `0x8000000f`: aggregate key low32 at item+0x10 and tag at item+0x18. The producer's input+0x08 is diagnostically called requestId, but ring+0x08 is a separately assembled field and is **not** source-proven to equal requestId. Therefore a future user-mode STAT trace can observe an aggregate key/tag, but cannot stand in for physical BF queue8 dequeue/non-null WM16 match or hardware DMA completion.

## E005k — completed rear4K Pin2 header and Microsoft KS completion-number origin

[experiments/E004-front-ir-vd55g0/e005k-windows-ks-completed-header-origin/README.md](../experiments/E004-front-ir-vd55g0/e005k-windows-ks-completed-header-origin/README.md) reduces a fresh user-mode-only physical rear4K run plus exact installed-binary source locks. Pin2 produced 24 completed 160-byte headers with FrameExtent=DataUsed=12,441,600 (exact 3840x2160 NV12), sequential FrameCompletionNumber 1..24 and no drops; pin3 simultaneously produced 76 completed companion headers. Microsoft ks.sys RVA0x70BC sets TRACK_COMPLETION, increments its per-pin +0x240 counter and writes header+0x78 FrameCompletionNumber. Qualcomm surfacecamavs CPin::CompleteFrame instead adds only timing flags 0x110 and returns through NotifyFrameCompleted. GROUP0_IMAGE raw IDs 0x15/0x16 -> class2 -> ProcessIfeFrame -> CompleteFrame is source-locked. This is a strong completed-KS-buffer boundary, but the sequence number is Microsoft bookkeeping—not requestId/FIFO8/WM16 IRQ/DMA/IOMMU fence evidence. Native rear processed ISP remains denied.

## E005j — live rear4K pin2 bound through original AVStream request/return graph

E005h physically proved the original Windows rear NV12 3840×2160 VideoRecord stream is KS pin2 and issues real IOCTL_KS_READ_STREAM calls. [experiments/E004-front-ir-vd55g0/e005j-original-avstream-pin2-isp-roundtrip-static/README.md](../experiments/E004-front-ir-vd55g0/e005j-original-avstream-pin2-isp-roundtrip-static/README.md) source-locks original surfacecamavs8380 SHA b97c4338... around that role: CVideoPin::HandleExtBuffer→TriggerStart→SubmitPendingPackets→SendPacketInternal→IfeNode::ProcessRequest on submission; IspWorker→OnIspNotification→GetIspNotification/ProcessIfeFrame on return. The CVideoPin vtable resolves ProcessIfeFrame's +0x68 to ValidateBuffer and +0xB8 to CompleteFrame; CompleteFrame resolves +0xC0 to NotifyFrameCompleted. GROUP0_IMAGE/Frame Done IFE requestId handling is source-present. This closes L0/L1 AVStream request/return source binding but is not same-live-frame requestId/FIFO8/WM16 IRQ/DMA/IOMMU evidence. Rear native processed ISP stays DENIED.

## E005i: original BF member -> GROUP3_STATS aggregate -> Windows STAT metadata (S + parent P endpoint, not DMA proof)

[experiments/E004-front-ir-vd55g0/e005i-original-group3-bf-stat-chain-static/README.md](../experiments/E004-front-ir-vd55g0/e005i-original-group3-bf-stat-chain-static/README.md) source-locks the exact OEM chain. In pinned qccamisp8380, GROUP3 sender RVA0x26170 builds six possible event/resource entries: 0x0e/0x300c, **BF 0x0f/0x300d**, 0x10/0x300e, 0x11/0x300f, 0x12/0x3010, and 0x0d/0x301c, then stamps raw ID25. Its only direct dispatcher call is gated by RVA0x25190's configured all-stats consumed-count check. Pinned AVStream names raw25 `IFE_MSG_ID_GROUP3_STATS`, normalizes it to type4 and routes type4 to ProcessStatsFrame, which writes QCOM custom camera metadata to the STAT pin. Parent E005h physically showed the simultaneous user-mode STAT endpoint during rear4K. The GROUP3 sender still does not require the outstanding matcher result to be non-null, so neither BF bit7, GROUP3 emission, STAT delivery nor software all-stats count is an independent correct-buffer WM16 DMA fence. Next physical/source gate remains same-owner/frame FIFO8 + NONNULL WM16 identity + independently trusted IRQ/ACK/DMA/IOMMU quiescence.

## E005h: original Windows rear4K VideoRecord pin2 -> exact KS read-stream handle (P/user-mode)

[experiments/E004-front-ir-vd55g0/e005h-windows-usermode-pin2-readstream-correlation](../experiments/E004-front-ir-vd55g0/e005h-windows-usermode-pin2-readstream-correlation/README.md) source-locks Microsoft ksuser.dll KsCreatePin/KsCreatePin2 post-create state and correlates one real rear NV12 3840x2160 session. Successful pins 0,1,2,3 were created; in the same FrameServer process pin2's exact returned handle received 361 IOCTL_KS_READ_STREAM calls and pin3's received 1088, while pins0/1 received none. Prior FrameServer media-type evidence identifies pin2 as 3840x2160 VideoRecord. This closes the user-mode pin-factory -> KS streaming-handle identity gap, but not the kernel QCOM_AVStream -> selected OEM ISP device/FIFO8/WM16 completion gap.

## E005f: original Windows user-mode FrameServer -> KS rear4K boundary (P/user-mode, not DMA proof)

[experiments/E004-front-ir-vd55g0/e005f-windows-usermode-frameserver-ks-ioctl-trace](../experiments/E004-front-ir-vd55g0/e005f-windows-usermode-frameserver-ks-ioctl-trace/README.md) ran one fresh original rear NV12 3840x2160 session for 20,049 ms / 203 handles. CDB was user-mode only on Camera FrameServer. 4,598 DeviceIoControl calls were observed; SDK-backed IOCTL_KS_READ_STREAM occurred 1,225 times across exactly two pin handles (922/303). QCOM_AVStream_8380 filter open, QcDeviceMFT8380.dll and ksuser.dll loaded. This narrows L0/L1 user-mode streaming into KS but does not yet assign VideoRecord pin2 to one of those two read-stream handles and does not reach L3 FIFO8/non-null WM16 hardware completion. Rear native ISP stays denied.

# SP11 camera stack — Windows behaviour to clean native Linux port map

**Pinned architecture baseline: 2026-09-24.** Device: Surface Pro 11 (Denali/X1E80100), RGB front IMX681, RGB rear OV13858, independent IR VD55G0, Qualcomm Spectra ISP. This is the FIRST map to consult when choosing a future experiment, driver, breakpoint or Linux implementation slice. Target: ordinary, controllable, native Linux camera capture and high-quality hardware-ISP frames. **Windows services, proprietary driver code, Studio Effects and AI image enhancements are not parity requirements.**

## Evidence legend

- **P — physically observed/proven on this SP11:** a source-backed register/stream/hardware experiment within its stated sensor and profile. An actual Windows application frame is not by itself a Linux DMA proof.
- **S — same-SP11 OEM static evidence:** driver/INF/disassembly identifies a branch or component, but does not demonstrate it ran during any specific camera session.
- **H — working hypothesis / unverified link:** plausible assignment of control ownership, effect or request path, requiring further evidence.
- **D — chosen Linux design:** what we plan to implement; not a claim that Windows is architected identically.

Do not promote S or H to P by analogy. Do not infer an app requested autofocus because Windows had an active BF write master, or infer a Device MFT was loaded because its DLL is registered.

## Schematic 1: Windows request-to-hardware map, with native Linux responsibilities

~~~mermaid
flowchart TB
 subgraph W["Windows client / selection plane — do NOT port"]
  A["Camera app / browser / video call<br/>select sensor, capture type, format, controls"]
  B["MediaCapture / Frame Server / profiles<br/>client negotiation and lifetime"]
  C["OEM Device MFT (registered)<br/>actual session role UNKNOWN"]
  X["Windows Studio Effects / AI<br/>OUT OF SCOPE"]
  A --> B
  B -. "optional/unknown" .-> C
  B -. "optional" .-> X
 end
 subgraph O["OEM SP11 driver/control plane — observe, don't transplant"]
  AVS["surfacecamavs8380.sys AVStream<br/>front / rear / aux identities; 3 stream pins [S]"]
  P["qccamplatform8380.sys + Surface configs<br/>board power/resources [S/H]"]
  SEN["IMX681 / OV13858 sensor drivers<br/>power, mode, CCI controls [S/P]"]
  ISP["qccamisp8380.sys<br/>CSI/VFE config, buffers, event callbacks [S/P]"]
  IQ["IQ/3A/RT-CDM/ICP interaction<br/>rear ordering and participants UNKNOWN"]
  AVS --> P
  AVS --> SEN
  P --> ISP
  SEN --> ISP
  ISP <--> IQ
 end
 B --> AVS
 C -. "if active: prove role" .-> AVS
 subgraph PHYS["Real hardware routes [P]"]
  FRONT["IMX681 front<br/>CSIPHY2 C-PHY"] --> CSID["CSID1 PIX → VFE1<br/>one exclusive PIX owner"]
  REAR["OV13858 rear<br/>CSIPHY1 4-lane D-PHY"] --> CSID
  REAR --> RAW["Linux rear RAW fallback<br/>CSID0 → VFE0 RDI0"]
  IR["VD55G0 IR independent transport<br/>illumination/privacy guarded"]
 end
 ISP --> CSID
 subgraph L["Clean native Linux — implementation design [D]"]
  APPS["Apps / browsers / calls<br/>libcamera, PipeWire, V4L2"]
  POLICY["Minimal camera/profile/session policy<br/>select sensor and format"]
  KERNEL["Kernel media graph + CCI/CAMSS<br/>power, exclusive CSI/ISP, DMA/IRQ/stop"]
  ALG["Optional open libcamera IPA<br/>auto/manual AE, AWB, AF and IQ policy"]
  BUFS["Truthful complete portable frame buffers<br/>format and colourimetry checked"]
  APPS --> POLICY --> KERNEL --> BUFS --> APPS
  POLICY <--> ALG
 end
~~~

**Dashed Windows arrows indicate possible paths, not confirmed SP11 calls.** The Windows Camera app's front/rear switch is a client-level request; its exact Windows close/reopen, profile negotiation and hardware-stop sequence is **unmeasured**. The Linux diagram identifies responsibilities, not Windows software to reproduce. No Windows-specific runtime service is intrinsically required for the Linux hardware driver to work.

## E005b: real one-session native FRONT production BF bit7 scoped-status result; NO rear DMA fence

[E005b verified one real IMX681 production front 27-frame run](../experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot/README.md): E005a older accepted-source module cancelled and boot files removed unarmed when source parity mismatch with proven 27-frame front was discovered. Distinct E005b SHA-pinned actual production CAMSS + E004pz unchanged front-runner-scoped status-only observer compiled ARM64 W1 zero warnings, ran once in isolated boot on existing front-only DTB with unchanged front launcher, shadow post-G3, produced 27 QC10C +27 TLBG +27 STATS3A exact-size contiguous outputs, producer PASS and STREAMOFF_OK. Real kernel after-stop scalar owner_epoch1 front-scoped BF bit7=0 unattributed=0 safe_stop=1, no new independently verified DMA completion. Golden restored with unchanged v19c saved entry, temporary boot removed, one-shot consumed, camera idle. P evidence for that single bounded FRONT session only; bit7 absent there does not prove universal front exclusion or live positive BF IRQ/rear mode/event0x0F. No independent global shared front/rear VFE1 ownership across unrelated V4L2 paths, FIFO8 group8 nonnull WM16 identity/correct-buffer IRQ/ACK or DMA/IOMMU-safe stop. Native rear processed ISP DENIED, Golden/front PIX/rear RAW+SW4K/IR preserved.

## E004pz: custom front-runner source/epoch-tagged CSID1 BF status observation, NOT global front/rear owner

[E004pz isolated compiled native front runner/IRQ observer](../experiments/E004-front-ir-vd55g0/e004pz-front-owner-bf-observer-isolated/README.md): copied ARM64 CAMSS per-device sidecar starts front owner epoch after exact custom front media-graph validation before hardware power/start, pins on existing unsafe teardown; copied CSID1 ISR observes ALREADY latched/ACKed BUF_DONE bit7 with exact configured front route, no additional MMIO/IRQ ACK/BUF_DONE/DMA/VB2. Actual isolated module W1 zero warnings SHA8d0a76762683edbb128a3ec1937db0a372f27f40e87d03be04ee718718419809, not loaded; same header GCC and Clang ASAN/UBSAN each 131096 offline assertions and 24 summary negatives PASS. **Not an independently global exclusive CSID1/VFE1 front/rear grant** across unrelated V4L2/media paths; no exported diagnostic or new live physical sample. Original Windows E004py four sampled cross-mode physical register observations stay historical. No rear BF FIFO8/nonnull WM16 frame match, trusted exact WM16 IRQ/ACK/DMA/IOMMU-safe stop. Native processed rear ISP still DENIED; Golden/front PIX/rear RAW+SW4K/IR untouched.

## E004py: P-tier original Windows front/rear BF bit7 and WM16 mode discriminator, NOT a hardware completion fence

[E004py SHA-rechecked E003g front raw against E004pi rear physical scalar evidence](../experiments/E004-front-ir-vd55g0/e004py-physical-front-rear-csid1-bf-bit7-discriminator/README.md): in two original front IMX681 LIVE samples, shared CSID1 BUF_DONE status0x271/mask0x1FFFF and VFE1 WM16 CFG0=0x10 disabled. In two separately captured rear OV13858 LIVE samples, status0x2F1/mask0x1FFFF and VFE1 WM16 CFG0=0x20001 enabled; source status XOR0x80 (bit7 ONLY) in both named phase comparisons. Front captured 2026-08-28, rear 2026-09-23: not simultaneous, same-frame or a causal IRQ trace. BUS IRQ status0/1 zeros at sampled instants do not attest DMA. This supports a future independently owner/sensor/route-tagged BF bit7 observer as source-status evidence, **not** treating bit7 or WM16-enable co-occurrence as proof of nonnull group8 FIFO8/WM16-buffer match, independent correct-buffer IRQ/ACK/DMA/IOMMU fence or safe six-group stop. Golden/front PIX/rear RAW+SW4K/IR and no-arm gate unchanged.

## E004px: native L1 owner-local frame epochs and L3 unique pending FIFO8 token (isolated D, not physical P)

[E004px tested owner/frame/token revision](../experiments/E004-front-ir-vd55g0/e004px-bf-owner-handoff-token-uniqueness-isolated/README.md): the earlier bounded kernel/C11 software BF FIFO incorrectly carried frame epochs across a completed owner handoff and allowed ambiguous duplicate pending opaque tokens. Strict global owner-epoch anti-replay now permits each NEW, safely granted owner to begin at frame1; pending token duplicates return -EEXIST with no queue mutation. Tested same exact header on isolated ARM64 CAMSS W1 zero warnings (private ko SHA25705f70ffbfb41c18661f509e7b19437de9e650f847757b7c8b6e4d15cb43a9) and GCC/Clang ASAN+UBSAN 437 assertions each, 22 result-field negatives. All source-provided completion flags remain hypothetical: no real rear4K FIFO8 nonnull WM16 matched owner/frame, independent correct-buffer BUS IRQ/ACK, DMA/IOMMU or six-group safe stop. NO live ISR/V4L2 caller, no module install/load, no processed rear ISP runtime arm. Golden/front native PIX/rear RAW+software4K/IR remain protected.

## E004pv: native BF FIFO8 owner/frame ring now COMPILES inside isolated ARM64 CAMSS, not physically authorized

[E004pv shared kernel and standalone C11 BF queue](../experiments/E004-front-ir-vd55g0/e004pv-native-bf-ring-owner-compiled-isolated/README.md): 4 software entries and generation-tagged exclusive owner, queue-token/WM16 tag matching, kernel spinlock, checked producer success, bounded fullness, strict FIFO, independent external exact WM16 IRQ/ACK, DMA/IOMMU and six-group + stop evidence gating. EXACT same new source header compiled in copied ARM64 CAMSS W=1 ZERO warnings (private module SHA daec2fd45d2c1db781f5a82d98d8eb9961193e1323e675e8550e438760a07da3, NOT installed/loaded) and passes 429 GCC + 429 Clang ASAN/UBSAN offline assertions and 25 summary negatives. This solves a **kernel source / software queue design gap**, NOT the lack of real trusted owner/frame/IRQ/DMA producers. There is no active ISR/V4L2/BUF_DONE callback, and rear arm ALWAYS -EOPNOTSUPP. Do not claim live processed rear4K or use CSID bit7/Windows FIFO count as DMA-fence shortcut. Golden/front PIX/rear RAW/software4K/IR unaffected.

## E004pu: original software queue producer + FIFO8 consumer share per-device group8 slot, but may lack an actual valid queued entry

[E004pu original SHA-pinned group8 ring producer/consumer audit](../experiments/E004-front-ir-vd55g0/e004pu-original-group8-ring-producer-capacity-static/README.md) proves source-level producer helper0x26838 has three callers, iterates13 group masks/queues, and addresses group8 through device+(0x66B+8)*8 = device+0x3398, same layout as existing BF FIFO8 consumer0x26460, provided SAME device object. Producer skips absent/full queue, invokes software copy helper0x2C5B0 before increasing pending count but does NOT explicitly guard its return; pop itself NULL on missing queue or zero count. Live original rear4K instance/frame and real successful entry matching remain unproven, as does independently trusted WM16 completion/IRQ/DMA/IOMMU stop. Static 62 ARM64 anchors, 192 offline ring cases and 25 result negatives PASS. This does NOT establish real native Linux FIFO8 hardware entry/owner/WM16 DMA fence, and E004pt CSID1 bit7 counter is not a shortcut. Native processed rear ISP remains DENIED; Golden/front PIX/rear RAW/software4K/IR protected.

## E004pt: native L2 CSID1 BF bit7 observer compiles, but L1/L3 trust remains unimplemented

[E004pt isolated compiled ARM64 CSID1 observer](../experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated/README.md): The accepted Linux CSID680 ISR ALREADY latches BUF_DONE+0x8C and ACKs it at+0x94. A separately built CAMSS copy adds one software-only observer after that existing ACK; it counts full CSID1 bit7 observations and stores last status, with no new hardware read/ACK, no port7/PIX/RDI/vb2 callback and NO FIFO8/WM16 DMA retirement. The fix1 isolated ARM64 module built with zero W=1 warnings, SHA e492063f4e950aab50f3cfddd8e8a3db53f784fc0a8b724e3d76acf59961bdec, not loaded/installed; 262144 GCC + 262144 Clang ASAN/UBSAN offline cases, 26 negative scalar fields. CSID1 also serves FRONT, so such a status-only counter has NO rear owner/frame provenance and NO nonnull FIFO8/WM16 queue match, bus IRQ/DMA/IOMMU safety or six-group stop evidence. This candidate is source-integrated only in a copied module outside Golden, not live. Native rear hardware ISP DENIED; next trusted same-owner/frame WM16 buffer and independent hardware completion remain missing.

## E004ps: original WM16 outstanding matcher may return NULL without blocking BF software callback

[E004ps source-locked matcher-null/callback audit](../experiments/E004-front-ir-vd55g0/e004ps-original-bf-null-matcher-callback-gate-static/README.md) SHA-pins 26 original SP11 OEM ARM64 instructions; 512 offline nine-input gate combinations and 21 fail-closed field negatives PASS. BF FIFO8 null skips dispatch at0x1FC9C, but a nonempty FIFO8 with WM16 CFG0 lowbit clear skips outstanding identity/tag lookup at0x1FCCC and can still notify software at0x1FD28. With CFG0 true, matcher0x25078 checks up to six outstanding entries, returns null on no identity/tag match, and BF caller0x1FCEC stores that return to context+0x580 without a nonnull check before notifying software. E004pr's "matcher" must NOT be interpreted as a successful match. OEM software callbacks and Media Foundation user-mode samples never independently authorize WM16 DMA-safe retire; native Linux design must require nonnull exact FIFO8/WM16 matched buffer plus separate verified same-frame owner/generation, trusted CSID-or-VFE WM16 IRQ/ACK, DMA/IOMMU and six-group safe stop. Source/design only, NO new hardware evidence, rear ISP runtime DENIED, Golden unchanged.

## E004pr: BF event-ID assignment is before a conditional FIFO8 pop; WM16 software metadata is NOT DMA retirement

[E004pr original BF FIFO8/WM16 conditional dispatcher proof](../experiments/E004-front-ir-vd55g0/e004pr-original-bf-fifo8-wm16-software-dispatch-gates-static/README.md) locks **52 exact same-SP11 OEM ISP ARM64 anchors/31 negative tests**, interpreting the E004pq original Windows BF event-ID assignment hit correctly. Original 0x1F190 builds event0x0F in a local list, then separate 0x1FC60 selects the BF dispatch, 0x1FC94 pops **FIFO8** and 0x1FC9C skips the entire BF branch if x23 EMPTY. For nonempty queue, callback0x1FCC4 reads original WM16 address status register-window+0x1270 and CFG0 lowbit+0x1200 (branch0x1FCCC); 0x1FCE4 matches queued identity+0x08 / tag+0x16 via0x25078, stamps BF port0x300D and retains entry at device+0x6A8, then 0x1FD28 invokes **software** notification0x26340. NONE alone proves per-buffer WM16 BUS IRQ completion/DMA IOMMU lifetime. The original Windows E004pq BF assignment hit did NOT capture this same rear4K frame's nonempty FIFO8 entry/WM16 buffer or completion. Proposed next source-lock probe RVAs0x1FC60/0x1FC9C/0x1FCC8/0x1FCE4/0x1FD28 are **not live tested**. E004pj accepted CSID BF stats distinct from generic RDI/PIX; native VFE ISR still noop, rear processed ISP runtime DENIED and Golden/front PIX/rear RAW+SW4K/IR protected.

## E004pq: real original Windows KD BF event-ID instruction HIT; no per-frame FIFO8/WM16 DMA completion

[E004pq SP7 private original Windows KD hit source-lock and non-private scalar ledger](../experiments/E004-front-ir-vd55g0/e004pq-original-windows-kd-bf-hit-source-locked/README.md) records real relocated original OEM ISP breakpoints: **RVA0x1675C** config+0x8C bit1 test hit once w8=0, **RVA0x1B67C** type1 zero-format CSID preparer hit once (logged x8 window pointer NOT status word), **RVA0x1F190** BF event-ID0x0F assignment instruction hit once, nonzero preparer0x20C04 had no recorded hit in that one-shot. The symbolic `qccamisp8380+offset` breakpoints initially did **NOT** resolve; source-verified absolute PE-image-location breakpoints did and produced these three hits with short private stack logs. SP7-private full-log SHA `b9bd34f68101d987b7d86cb0de3ca713f26a62fab39295ec4661157fe250ffcc`; only safe scalar counts and bounded original instruction RVAs/identities committed. P evidence is **instruction execution in SP11 Windows**, NOT shared rear4K device/frame/owner correlation, actual per-hit CSID1 bit7, successful event0x0F FIFO8 queue enqueue, WM16 buffer identity or DMA/IOMMU completion. Historic E004nv/nq/pi/pk 'no event observed' statuses are scoped to THEIR earlier evidence/captures, not a denial of the NEW KD hit. E004PN Windows rear4K two-pass capture separately reported 653+1154=1807 valid 4K frame handles; no original KD-to-frame ID correlation was recorded. Accepted native E004pj CSID BF stats not generic RDI/PIX, E004ow VFE ISR noop; independent L1–L3 owner/WM16 IRQ-or-CSID bus done DMA stop still mandatory. Rear native processed hardware ISP remains runtime DENIED; Golden/front PIX/rear RAW+software4K/IR unchanged.

## E004pk: full-IFE worker class and type1 CSID BF preparer format are TWO independent original selectors

[E004pk same-SP11 original full-IFE class vs type1 CSID format selector](../experiments/E004-front-ir-vd55g0/e004pk-full-ife-count-vs-type1-format-mode-static/README.md) SHA-pins **71 exact original OEM ISP ARM64 instruction anchors / 31 negative tests**. Original resource enumerator0x31AC–0x3234 conditionally discovers/maps literal `IFE0`/`IFE1` and increments full-IFE count w22, stored at global0x670FC original0x3380. Source IFE constructor0x2237C–0x22478 copies discovered count to worker context+0x349C and tests `instance_index>=full_IFE_count`, storing result into worker+0x6B678. Worker modezero selects BF-capable handler0x1EF90, nonzero handler0x1C9D0. **If both IFE0 and IFE1 were mapped in same initialization, original worker instance1 would select zero-mode**, but that exact discovery count and handler were NOT captured dynamically during original rear4K E004pi physical snapshots.

**Separate original type1 status-format selector:** setup0x16748–0x16768 tests **input configuration word+0x8C bit1**, writes flag to input+0xE28, which context callback selection0x17D98–0x17E58 uses to install CSID bit7-preserving preparer0x1B5F0/normalizer0x1B7D0 when zero versus bit7-erasing preparer0x20B50/normalizer0x20CE0 when nonzero. It is **not source-proven equal** to IFE resource-class worker flag, nor is its actual original rear4K value known. The physically observed CSID1 bit7+mask alone does NOT prove BF event0x0F in worker, FIFO8 WM16 completion or DMA/IOMMU safe buffer retirement. NEXT original same-session worker class and input config bit1/queue record validation plus SP11 real trusted WM16 completion source, six-group/owner/frame/stop safe L1–L3 path. No generic RDI/PIX BF completion; native hardware rear ISP runtime DENIED, Golden/front PIX/rear RAW+software4K/IR protected.

## E004pj: CSID BF stats completion is NOT existing RDI/PIX; source-verify WM16 semantics before choosing CSID-delivered or VFE IRQ

[E004pj native SP11 CSID680 stats/RDI dispatch boundary and offline dual-source completion model](../experiments/E004-front-ir-vd55g0/e004pj-csid-bf-statistics-completion-bridge-offline/README.md): SHA-pins five accepted CAMSS sources and E004nv/ph/pi/ov, **65,536 low16 CSID IRQ patterns**, GCC & Clang/ASan/UBSan **262,267 offline C11 assertions each, 25 negatives PASS**. Accepted full CSID680 only forwards **RDI bits14–17** to `camss_buf_done(csid->id,port0..3)` while **BF statistics bit7**, which E004ph statically associates with original group8/WM16 and E004pi observes set+unmasked in two rear4K Windows snapshots, is **already ACKed but not forwarded**. Generic `camss_buf_done`→`vfe_buf_done` is a *one-WM RDI/PIX output line* with **immediate VB2 buffer return**, not a six-group FIFO8/WM16 owner/DMA fence. **DO NOT forward CSID BF bit7 as RDI port7, PIX or WM16 index16 into this generic function; do not double-ACK CSID.**

**Hardware-source qualification to E004pi:** Upstream Titan Gen3 CAMSS source explicitly moves *some bus-done IRQs into CSID*, so a separate VFE IRQ is **NOT universally required**; an independently source-verified **CSID-delivered WM16 completion** may be valid on this silicon, but **the observed SP11 CSID BF bit7 alone is NOT proof of its WM16 buffer completion semantics, frame/fifo/owner generation, DMA/IOMMU quiescence or six-group safe buffer retirement**. E004pj models both hypothetical trusted domains (proven VFE WM16 vs proven CSID stats WM16) with distinct per-frame/teardown gates, rejects untrusted self-attestation and always returns `-EOPNOTSUPP` for actual native rear arm. The proper next L3 implementation is a dedicated same-session BF stats callback with independent WM16 buffer/queue identity and DMA-safe lifetime, not reuse of generic RDI/PIX output. E004ow actual VFE ISR noop and E004ov offline six-group owner contract remain; runtime rear hardware ISP DENIED, Golden/front PIX/rear RAW+software4K/IR protected.

## E004pi: original Windows LIVE rear4K CSID1 BUF_DONE bit7 observed in BOTH captures; not a VFE WM16 DMA fence

[E004pi read-only original Windows dual LIVE rear4K scalar verification + offline domain gate](../experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/README.md) reused **same-SP11 original 2026-09-23 Windows rear VideoRecord 3840×2160 two separate original E004nq physically measured LIVE1/LIVE2 sessions**, reread **original private full physical KD logs on SP7** read-only with exact per-log SHA pin and row/region integrity, exported **safe register scalars only**. Both independent original physical LIVE CSID1 BUF_DONE_IRQ_STATUS+0x8C=`0x000002F1` (bit7 **SET**) and BUF_DONE_IRQ_MASK+0x90=`0x0001FFFF` (bit7 **enabled**), CSID1 IPP status=`0x00E11FF8`; VFE1 TOP status0=0/status1=`0x00030003`, BUS status0/1=0 (sampled at an instant, **NOT quiescence proof**), BUS mask0=`0xD0000000`/mask1=0, WM16 CFG0=`0x00020001` **enabled**, WM16 ADDR_STATUS0 nonzero boolean (underlying DMA address NOT exported). CSID BUF_DONE CLEAR register readback differed (0x80/0x201); readback is not ack/completion verification. Thus the **CSID1 BUF_DONE bit7 input to E004ph's conditional config-zero BF source** is now P/PHYSICALLY OBSERVED in two original live rear4K captured snapshots, while original actual selected BF-capable worker handler/mode and **software event0x0F/FIFO8 exact frame identity remain unobserved**. No private KD log, physical/DMA address, optical pixels or Windows executable transferred.

**E004pi native L3 fail-closed result:** accepted native CSID680 ISR already ACKs BUF_DONE. Actual accepted native VFE680 ISR still `return IRQ_HANDLED;`; no verified independent VFE1 WM16 BUS/IRQ/DMA/IOMMU producer, safe buffer lifetime or exclusive front/rear owner handoff follows from CSID bit7 + WM16 CFG0 enabled + nonzero WM16 address-status. Standalone offline `bf-wm16-domain-gate.h` and tests distinguish **CSID receive IRQ domain from independently verified VFE WM16 completion domain**; GCC + Clang ASAN/UBSAN pass 95 assertions each; SP11 verifier checks two SHA-locked original SP7 scalar snapshots and **40 false-claim negative mutations**; actual runtime authorization ALWAYS `-EOPNOTSUPP`. NEXT original live rear4K selected handler and BF0x0F/group8 queue entry with independent per-generation WM16 BUS/IRQ/DMA/IOMMU completion and shared VFE1 owner/stop validation. No native ISR writes/active rear processed ISP until then; preserve Golden, native front PIX, rear RAW/software4K fallback and IR.

## E004ph: actual original BF type1 status is CSID0/1 BUF_DONE status bit7 via DIFFERENT queue than IFE snapshot

[E004ph original type1 BF preparation to CSID resource and native CSID680 IRQ boundary](../experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/README.md) locks **200 exact same-SP11 OEM ISP ARM64 instructions / 51 negative cases**, original resource strings CSID0/CSID1 and selector7/8 jump table, native accepted CSID680 SHA and status/clear definitions. Original snapshot wrapper0x24A30 feeds **queue A per-instance+0x228**, type2 consumer; actual type1 queue B per-instance+0x60328 invokes distinct preparer0x24380 via global0x671F0 thunk0x2AC30 on envelope+0x10, then delivers **same prepared envelope** via global0x671D0 thunk0x2ACA0 to type1 producer0x243D0. Input config+0xE28 chooses config-zero preparer0x1B5F0 and normalizer0x1B7D0 or nonzero preparer0x20B50 and normalizer0x20CE0. The config-zero type1 preparer reads **original CSID0/CSID1 mapped register +0x8C (BUF_DONE_IRQ_STATUS)** for source instances0/1 (original context+0x08 resource selectors7/8 through resource table+0x10) and masks0x07FFFFFF, writes prepared+0x0C, normalizer swaps to type1 record+0x08, zero-mode BF handler tests bit7 and conditionally emits event0x0F/FIFO8. Original source separately writes same CSID **BUF_DONE_IRQ_CLEAR+0x94** and IRQ clear command+0x14. Nonzero status preparer uses mask0x1F, so bit7 cannot survive that branch; **actual original rear4K source/handler selected modes and BF event occurrence unobserved**. E004pg still proves subsequent type1 producer→software worker SAME ring on successful setup.

**CRITICAL original VFE-vs-CSID correction:** E004ox direct IFE snapshot TOP status1 and E004pb conditional 'if same IFE snapshot then BUS0' are both NOT the actual discovered queue-B BF status source. Accepted native `camss-csid-680.c` already reads/acks CSID BUF_DONE status+0x8C/+0x94/+0x14; bit7 is **not defined as an independently proven VFE1 WM16 DMA/IRQ completion**. Do not add a CSID bit7 handler to VFE ISR, double-ack CSID, return processed rear buffers or hand over shared front/rear VFE1 core on CSID bit7 alone. E004ow accepted real VFE ISR remains `return IRQ_HANDLED;`; original live mode, per-frame FIFO8↔WM16 BUS/IRQ/DMA/IOMMU quiescence and owner-safe L1–L3 stop remain missing. L3 next is independently validate VFE1 WM16 hardware completion and generation-matched DMA/IOMMU fence, not reuse CSID BUF_DONE. Rear hardware ISP runtime DENIED; Golden/front native PIX/rear RAW/software4K/IR unchanged.

## E004pg: actual original SOURCE command0x0A exports worker ring+0x08/notification address+0x20; type1→worker SAME ring static proof

[E004pg original type1-to-worker channel identity](../experiments/E004-front-ir-vd55g0/e004pg-original-source-command-a-worker-ring-identity-static/README.md) pins **93 original ARM64 anchors and 34 fail-closed mutations**. Original installer0x19E34–0x19E58 creates SOURCE endpoint from per-instance table+0x30 using constructor0x22278. The source endpoint installs **command handler0x22CD0**, not destination generic handler0x211B0; the SOURCE command0x0A jump table0x236C4 selects **0x23120**, which exports **[source context+0x08 ring pointer, ADDRESS source context+0x20 notification object]** into the same kind2 interface coordinator0x17F98–0x18024 transfers to DESTINATION table+0x40 command0x0B. The DESTINATION handler0x211B0 command0x0B writes interface ring to destination context+0x198 and notification address to destination context+0x1A0; original type1 producer0x243D0 enqueues to destination+0x198. The SOURCE constructor0x2284C allocates a 0x368-byte ring into **that same source context+0x08**, and original worker0x23900/0x23940 dequeues it. **The software type1 producer→worker SAME-ring route is source-proven for successful same-instance kind2 setup**, correcting earlier E004pc/E004pd/E004pe/E004pf ring uncertainty and E004pd's **incorrect use of destination command0x0A branch0x214BC for source**. E004pe destination+0x1B0 0x1D0-byte ring remains independently allocated but **not exported by source command0x0A**. Older E004pd v1 RESULT/verifier source+0x1B0 and unknown-notification claims are historical and SUPERSEDED; older milestone READMEs explicitly warn about this.

**Still gated:** no proof original live rear4K selected mode or BF event0x0F, actual type1 incoming x1==original IFE snapshot wrapper0x24A30 output, frame/FIFO8 identity, MMIO IRQ bit/ack or DMA-safe WM16 retirement. E004pb normalization still swaps source+0x08/+0x0C and refutes E004ox's direct TOP1→BF inference; conditional same-snapshot BUS status0 bit7 is *not a proven live IRQ*. Accepted Linux VFE680 ISR E004ow is noop; E004ov per-generation ownership guard offline; rear hardware ISP runtime DENIED. NEXT same-instance snapshot-wrapper/type1 input provenance and original mode-selected handler, then independently verify real native VFE1 BF status/mask/ack, FIFO8, WM16 BUS/DMA/IOMMU quiescence and exclusive front/rear owner. Golden/front PIX/rear RAW/software4K/IR unchanged.

## E004pf: original endpoint table identifies E004pe's 0x1D0-byte ring as DESTINATION context, not SOURCE

[E004pf exact same-SP11 source vs destination endpoint provenance](../experiments/E004-front-ir-vd55g0/e004pf-original-channel-source-vs-destination-endpoint-context-static/README.md) locks **60 original ARM64 ISA anchors / 27 negative tests** and cross-checks corrected E004pe v2 **74 anchors/32 negatives**. The original object x21 initialized at0x17660–0x176C0 is created using **per-instance table+0x40**, saved selected entry address at stack+0x38 (0x175F8–0x17610), and stored at0x17BF4. Its context+0x1B0 **0x1D0-byte** ring allocated0x17AA4/stored0x17AF0 is therefore the **command-B DESTINATION endpoint's ring**. E004pe v1 called this SOURCE and incorrectly inferred source ring allocation/ownership: that claim is RETRACTED. Original coordinator0x17FB8 accesses **per-instance table+0x30 SOURCE** for command0x0A, distinct from destination table+0x40 used by command0x0B. Command-A SOURCE context+0x1B0 ring allocation site and consumer remain untraced. Source+0x1B0→destination context+0x198 transfer E004pd is still source-proven; identity with IFE worker device+0x08, snapshot/type1 event and live BF not established.

## E004pe corrected: original destination+0x1B0 and worker+0x08 have independently located ring allocations

[Revised E004pe v2 result and erratum](../experiments/E004-front-ir-vd55g0/e004pe-original-ife-source-ring-independent-allocation-static/README.md) verifies **74 original ARM64 ISA anchors / 32 negatives** and corrects the former source-side label: original **destination** setup0x176C0 allocates its 0x1D0-byte ring at destination context+0x1B0 (0x17AA4/0x17AF0), distinct from original worker's 0x368-byte ring allocated at device+0x08 (0x2284C/0x22898) and dequeued0x23940. The **source table+0x30** context+0x1B0 ring cannot be assigned the destination's allocation; no actual same-session source-to-worker ring alias or type-1 record→BF handler proven. E004pb normalizers swap source status+0x08/+0x0C, superseding direct TOP1 BF inference. No guessed BUS IRQ writes or WM16 DMA retirement, rear ISP runtime DENIED, Golden/front PIX/rear RAW+software4K/IR unchanged.

## E004pd: original source command0x0A → destination command0x0B supplies type-1 event-channel pointer

[E004pd exact original type-1 channel supplier/receiver source](../experiments/E004-front-ir-vd55g0/e004pd-original-ife-channel-command-a-b-pointer-transfer-static/README.md) verifies **74 original same-SP11 ISP ARM64 instruction anchors, original jump-table dispatch and 25 negatives**. Original coordinator0x17F98–0x18028 stamps **interface-kind 2** at local stack+0x50/+0x60, invokes *source endpoint* per-instance table+0x30 with **core command0x0A**, 24-byte output stack+0x50, then passes the **same 24-byte buffer** to *destination endpoint* table+0x40 with **core command0x0B** if source succeeds. Dispatch command0x0A→core0x214BC exports **source context+0x1B0 ring pointer into interface+0x00**. Command0x0B→core0x21478 accepts kind2 and copies **interface+0x00→destination context+0x198 ring**, interface+0x08→destination context+0x1A0 notify. Thus the original **source context+0x1B0→destination context+0x198 pointer handoff** is source-verified, closing E004pc's unknown *supplier*; the *source of the notification field* is not established by command0x0A's one-pointer write.

**No alias promotion:** source endpoint context+0x1B0 remains **unproven equal** to original worker **device+0x08 ring**, independently allocated0x22830–0x22898 and consumed0x23940. The original kind2 interface is NOT event-record type2. No actual rear4K per-instance snapshot→type1 input, source-format/mode or BF live event established; E004pb's status-word swap supersedes E004ox TOP1 direct BF hypothesis and only conditionally makes snapshot BUS status0 the BF word. Native Linux real VFE ISR remains E004ow no-op, E004ov ownership model offline, rear ISP runtime DENIED; no guessed IRQ ack/WM16 DMA retirement. NEXT source endpoint+0x1B0 ring allocation/worker identity, snapshot-wrapper/type1 same buffer, real native VFE1 FIFO8/WM16 per-generation DMA fence; preserve Golden/front PIX/rear RAW/software4K/IR.

## E004pc: type-1 event channel interface provisioned separately from worker queue; no proven ring alias

[E004pc original source-only type-1 event-channel ring boundary](../experiments/E004-front-ir-vd55g0/e004pc-type1-event-channel-ring-alias-unproven-static/README.md) verifies **73 exact same-SP11 OEM ISP ARM64 anchors / 23 negative cases** and an offline identity-gate counterexample. Original generic core callback0x211B0 assigns incoming **interface-kind 2** pointers `x21+0x00`→per-context event-ring **+0x198** and `x21+0x08`→notification **+0x1A0** (kind 3 separately writes+0x1A8/+0x1B8). Type-1 producer0x243D0 enqueues its 16-byte **event-record type 1** using context+0x198; interface *kind 2* is NOT E004oy's separate *record type 2*. The original worker independently allocates its **device+0x08** ring0x22830–0x22898 and dequeues it0x23900–0x23940. E004oy's type-2 external producer demonstrably enqueues to this worker device+0x08; **no source evidence yet proves the supplied type-1 channel-kind-2 interface x21+0x00 equals that exact same worker queue**. Matching record format, offsets in different contexts or copy helper cannot authorize status-to-BF or DMA completion claims.

**E004ox/E004pa historical source hypothesis corrected in their READMEs:** E004pb normalizers swap source+0x08/+0x0C; conditional *same snapshot* BF candidate comes from selected BUS STATUS0 snapshot+0x0C, NOT direct TOP STATUS1+0x08. Without the original exact upstream same-buffer and ring provenance **neither status register is a proven live rear BF IRQ/ack or WM16 buffer fence**. E004ow real Linux ISR remains stub, E004ov owner guard offline, rear ISP runtime DENIED. NEXT original kind2 interface provider/queue alias/snapshot-source chain and independently safe native VFE1 IRQ/FIFO8 WM16 bus/DMA/IOMMU fence. Preserve Golden/front PIX/rear RAW+software4K/IR.

## E004pb: original type-1 event producer FOUND; status normalization swaps +0x08/+0x0C, superseding direct TOP1→BF inference

[E004pb exact original type-1 callback producer/normalization](../experiments/E004-front-ir-vd55g0/e004pb-ife-type1-record-producer-normalization-static/README.md) SHA-locks original same-SP11 OEM ISP, **129 exact ARM64 ISA anchors, 25 fail-closed mutations** and independent synthetic unequal-word source/consumer checks. Original callback0x243D0 registers in **global RVA0x67138** (beside status-wrapper global0x67140 and type2 external callback global0x67150), pops status-object pointer from per-context+0x1B0, stamps local **event type 1** at0x244E8, invokes per-context copier+0x208 on incoming x1→status-object x2, increments its software count, then conditionally enqueues event in **per-context+0x198 ring**, signalling+0x1A0. Original initializer selects copier0x20CE0 or0x1B7D0 from an independently observed +0xE28 flag. **BOTH copiers source+0x08→type1-record+0x0C and source+0x0C→type1-record+0x08**. BF handler's second status word is **type1-record+0x08 bit7**.

**Mandatory correction to E004ox/E004pa:** the original snapshot's TOP status1 at **snapshot+0x08** does *not* transparently feed BF record+0x08 through the newly discovered type1 producer: the copier swaps the words. **IF** the incoming buffer is the mode-selected original IFE snapshot, BF instead inspects **snapshot+0x0C bit7, the selected BUS status0 word**, not TOP status1. Exact upstream snapshot→type1 input identity is still UNPROVEN; **neither a TOP1 nor BUS0 BF bit is confirmed for live rear4K**. The source-format copier flag+0xE28 is not demonstrated to equal selected per-IFE mode flag+0x6B678. Per-context producer ring+0x198 has not been proven identical to earlier worker device+0x08 ring. The conditional direct TOP1 interpretation in historical E004ox is **superseded**; do NOT code an IRQ handler/ack from it, or relabel the type1 software count as WM16 DMA retirement.

**L1–L3 next:** source-trace actual original registered callback invokers, same incoming status buffer, ring/worker and FIFO8 per-buffer generation, reconcile mode-dependent BUS IRQ-clear mismatch, then independently prove native VFE1 hardware BF IRQ/FIFO8/WM16 bus/DMA/IOMMU-safe lifetime. E004ow real Linux VFE ISR still stub; E004ov owner guard offline design; rear ISP runtime DENIED, Golden/front native PIX/rear RAW software4K/IR protected.

## E004pa: original zero/nonzero IFE snapshots use distinct non-lite/lite TOP IRQ register patterns

[E004pa exact original two mode-selected IFE snapshots and native VFE680 definitions](../experiments/E004-front-ir-vd55g0/e004pa-ife-dual-mode-top-irq-layout-static/README.md) pins 77 original ARM64 anchors, accepted Linux source SHA and 22 negative cases. Original **modezero** callback0x1DC20 reads TOP STATUS0/1 original base+0x44/+0x48 and writes TOP clear0/1/command +0x3C/+0x40/+0x30 (matches accepted Linux *non-lite* TOP offsets). Separate original **nonzero** callback0x1C2B0 reads TOP base+0x1C/+0x20 and writes TOP +0x2C/+0x30/+0x38 (matches accepted Linux *lite* TOP offsets). Both put status into record+0x04/+0x08, but BUS status shape and writes differ: modezero selected-window+0x28/+0x2C status and +0x3C/+0x40/+0x30 writes; nonzero selected+0x28 status and +0x60/+0x30 writes. **Neither entire BUS-side sequence is source-proven as accepted Linux BUS IRQ clear0/clear1/global**, and TOP layout equality cannot certify safe DMA retirement. The zero-mode candidate TOP status1 bit7 BF0x0F is NOT automatically a nonzero-mode BF condition.

**Hardware restriction:** matching non-lite/lite TOP numeric patterns do NOT establish which original per-device callback or physical IFE resource the *live rear4K VFE1* selected. E004oz snapshot invoker and distinct type1 event producer remain unresolved, E004ow real Linux VFE ISR remains stub, E004ov owner model offline, runtime rear ISP DENIED. NEXT exact original selected mode/type1 status record and independently verified real VFE1 IRQ/bus/FIFO8 WM16 generation-matched DMA stop; never issue guessed BUS writes. Preserve Golden/front PIX/rear RAW/software4K/IR.

## E004oz: original ISP registers separate status-snapshot wrapper and type-2 external-event callback

[E004oz same-SP11 original ISP two original global callbacks](../experiments/E004-front-ir-vd55g0/e004oz-original-ife-dual-callback-registration-static/README.md) pins 92 original ARM64 instruction anchors/22 fail-closed mutations. Original conditional initializer RVA0x22670–0x22690 registers **RVA0x24A30 in module-global RVA0x67140** and **RVA0x24A70 separately in global RVA0x67150**. Wrapper0x24A30 calls the mode-selected IFE snapshot at per-device slot+0x6B6B0 (mode-zero snapshot0x1DC20 emits TOP/BUS status record); callback0x24A70 instead calls slot+0x6B6B8 and stamps a **type-2** external software event (E004oy). The worker still dispatches event records through slot+0x6B6D8 to conditional type1 BF0x0F/FIFO8 handling (E004ox/E004nv). **Upstream invoker of snapshot wrapper0x24A30, actual type1 record producer and matching snapshot-pointer identity are NOT yet traced.** Callback registration does not prove original live rear4K IFE mode/BF, native IRQ ack or WM16 DMA retirement.

**Native L1–L3:** distinguish callback, event-record type, source hardware status and per-generation buffer lifetime. Original mode-zero BUS-side +0xC3C/+0xC40 writes vs accepted Linux BUS clear +0xC20/+0xC24 remain unresolved: do not transplant IRQ writes. NEXT trace original registered callback invoker→type1 event record and hardware-safe Linux VFE1 BF IRQ/FIFO8 WM16 IOMMU retirement; preserve Golden/front PIX/rear RAW+software4K/IR and runtime-DENIED rear ISP.

## E004oy: exact original type-2 external callback→two software rings→event-worker route, not BF type-1 producer

[E004oy original same-SP11 ISP type-2 event record route](../experiments/E004-front-ir-vd55g0/e004oy-ife-type2-event-record-ring-producer-static/README.md) locks 86 ISA anchors/19 negative cases. Conditional external callback RVA0x24A70 stamps software **event type 2** at0x24B80, obtains a record object from **device+0x33C8 object ring**, copies external input to its fields, and enqueues a 16-byte type-2 event in the **separate device+0x08 event ring** at0x24D50. Original worker0x23900/0x23940 dequeues that same device+0x08 ring, passes record to mode-selected handler context+0x6B6D8 at0x239BC; its mode-zero type-2 case0x1FECC atomically decrements an object's **software** count at0x1FF14 and may recycle on zero through ring+0x33C8. This **closes type-2 software event provenance only**, not the separate type-1 BF status-pointer producer or live TOP1 bit7/BF0x0F/FIFO8/WM16 IRQ/DMA retirement. E004ox original snapshot→type-1 same-event record identity and OEM BUS clear discrepancy remain open; no native rear ISP runtime arm.

**Linux L1–L3:** neither type-2 record/ring count nor KeSetEvent can authorize WM16 buffer retirement or core owner handoff. NEXT independent **type-1** event-record origin, original BUS offset semantics and native rear VFE1 hardware IRQ/FIFO8 per-generation DMA stop proof. Golden/front PIX/rear RAW software fallback/IR protected.

## E004ox: original mode-zero BF bit7 aligns with TOP IRQ status1, not BUS IRQ status1; clear-offset mismatch

[E004ox exact original mode-zero IFE snapshot, type1 BF and accepted Linux VFE680 register definitions](../experiments/E004-front-ir-vd55g0/e004ox-original-ife-bf-top-status1-register-provenance-static/README.md) pins 69 original ARM64 instructions, the accepted Linux source SHA and 18 fail-closed mutations. On **original mode zero**, IFE snapshot callback0x1DC20 is registered at context+0x6B6B0, reads original base+0x44/+0x48 into record+0x04/+0x08 (**TOP status0/status1**), and selected-window+0x28/+0x2C (=original base+0xC28/+0xC2C) into record+0x0C/+0x10 (**BUS status0/status1**). The separate type1 handler0x1EF90 reads status record+0x08 as its second status word, extracts bit7 to conditionally generate BF0x0F→FIFO8. **TOP status1 bit7** is the specific *source-backed candidate*, conditional on verifying the exact snapshot→type1 event-record pointer identity and live rear selected mode; not a proven live BF or WM16 DMA completion. Crucial unresolved discrepancy: original snapshot's **BUS-side writes** target original base+0xC3C/+0xC40, while accepted Linux BUS clear0/clear1 are **+0xC20/+0xC24**. Original TOP-side +0x3C/+0x40 and +0x30 align numerically with accepted TOP clear/command, but the entire original snapshot cannot be treated as an approved Linux IRQ-ack recipe.

**Native Linux L1–L3:** distinguish TOP1 bit7 candidate from prior front TOP1 bit0 VIDEO and BUS status; do not wire the E004ow ISR stub or release buffers on that candidate alone. NEXT trace exact original snapshot→event pointer producer and reconcile BUS clear register map, verify live mode/BF event, native FIFO8 generation and hardware WM16 IRQ/bus/IOMMU DMA-stop before rear ISP arm. Golden/front PIX/rear RAW/software fallback/IR unchanged.

## E004ow: accepted native Linux VFE680 hardware IRQ handler is a no-op, blocking real rear BF completion

[E004ow four SHA-locked accepted Linux CAMSS source files](../experiments/E004-front-ir-vd55g0/e004ow-native-vfe-isr-stub-rear-bf-gate-source/README.md) prove the **entire real VFE680 `vfe_isr` body is `return IRQ_HANDLED;`** and `vfe_ops_680.isr` plus `camss-vfe.c` `devm_request_irq(...hw_ops->isr...)` bind this exact stub to the VFE hardware IRQ. It reads/acks no TOP/BUS status and retires no WM/DMA. The separately retained E003h front Epoch0 BUS-status1 bit21 and VIDEO TOP-status1 bit0 snapshot/poll recipe has no active VFE ISR/hw_ops/stream caller; preserve working front PIX's other bounded polling paths. `camss_rtcdm1_isr` is **a different command-engine IRQ**, not VFE WM16 BF retirement. The E004ov generation-tagged model remains offline/unintegrated; no original live rear BF event, native IRQ evidence producer or per-buffer WM16 DMA completion exists yet. Verifier checks four accepted-source hashes and **15 fail-closed negative cases**. This is direct D/native Linux integration source evidence, not observed rear physical completion.

**Concrete next L1–L3 gate:** independently source-prove rear VFE1 group8/WM16 IRQ status/mask/clear, generation-matched BF FIFO entry, per-WM bus/IRQ/DMA/IOMMU-safe retirement and same-session original Windows selected IFE mode/BF event. Implement/test any new isolated ISR with safe rollback without altering front PIX or removing rear runtime DENIED until verified hardware authority exists.

## E004ov: offline-only generation-tagged Linux rear six-group stop ownership DESIGN

[E004ov isolated C11 stop/owner generation contract](../experiments/E004-front-ir-vd55g0/e004ov-rear-six-group-generation-ownership-offline/README.md) identifies a prospective L1–L3 hazard in previously source-compiled but unwired E004nv: its logical group completion API has no owner/frame generation or independent group FIFO queue-entry identity, while its retire API accepts one externally supplied bus-stop Boolean. This is not evidence of a live mis-retirement. The **separate, never integrated** E004ov DESIGN source adds strict monotonic owner/frame epochs, six per-group queued-entry identities and three independently asserted per-event IRQ/FIFO/DMA-generation proof inputs. It rejects stale/duplicate events, wrong FIFO and type-2-as-BF, then requires all six groups plus distinct source-input/WM bus/IRQ/finished-DMA/IOMMU/same-generation hardware-stop predicates before modeled ownership release. The **normal and ASan/UBSan C11 builds each pass 720 six-group completion orders and 62,655 simulated assertions**. Six-group source mapping matches immutable E004nv, and original CAMSS front files are SHA-verified unchanged. **D, not P/S physical completion:** hardware evidence providers and actual WM16 safe retirement are still UNPROVEN; no live camera/runtime caller exists; Linux rear hardware ISP remains DENIED.

**Next actual L1–L3 hardware gate:** source-verify Linux rear VFE1 IRQ/ack, BF FIFO8 per-entry identity and per-generation WM16 bus/DMA/IOMMU retirement, plus permitted same-session Windows rear 4K OEM IFE selected mode/BF event observation without blocked KD. No stage permits user-space Windows services or copying original OEM binaries into Linux.

## E004ou: mode-zero IFE event-record type 2 software counter is NOT BF FIFO8/WM16 retirement

[E004ou original same-SP11 ISP mode-zero type-2 versus type-1 BF path](../experiments/E004-front-ir-vd55g0/e004ou-ife-event-record-type2-not-bf-wm16-retirement-static/README.md) source-locks 79 original ARM64 instructions and 16 negative tests. Original type **1** status word2 bit7 conditionally emits BF event0x0F and pops FIFO8, then the BF callback reads WM16 CFG0 and ADDR_STATUS0 at mode-zero selected-window+0x1200/+0x1270 (original base+0x1E00/+0x1E70). Separate original type **2** event-record branch RVA0x1FECC tests software record flags +0x0C, optionally reads **different diagnostic registers** selected-window+0x64/+0x70 (mode-zero base+0xC64/+0xC70), atomically decrements an event-record software counter RVA0x1FF14, and on zero may queue via helper0x2BEF8, **not** BF FIFO8 dequeue0x26460. No type-2 software counter or conditional diagnostic register read is an independently verified BF WM16 bus/IRQ/DMA retirement fence; other upstream hardware IRQ paths remain untraced. Original rear4K live BF0x0F and OEM selected dispatch mode unproven, though E004nq physically verified rear Windows VFE1 activity.

**Linux L1–L3 stop invariant:** do not release buffers/handoff owner on type-2 software count zero, mode-selected finalizer return, or either event; separately establish hardware IRQ source/ack, per-generation BF FIFO8/WM16 transfer completion and safe DMA retirement. Rear experimental ISP remains runtime DENIED, protected Golden/front native PIX/rear RAW/software fallback/IR intact.

## E004ot: original IFE1 descriptor is lookup selector 1; rear VFE1 is ALREADY physically observed

[E004ot original same-SP11 four resource labels and lookup branches](../experiments/E004-front-ir-vd55g0/e004ot-original-ife-resource-name-four-selector-static/README.md) source-checks 73 ARM64 anchors, four exact original PE descriptor labels and four PE selector entries: **selector 0→IFE0** (`0x4AEE0+0x50` first), **1→IFE1** (same array second), **2→IFELITE0** (`+0x20` first), **3→IFELITE_CDM0** (`+0x20` second). E004or checked 0/2/3 only; this new test explicitly includes the instance selector 1 permitted by original initializer. E004os independently establishes original `MmMapIoSpaceEx` producers for all four mapped-array entries. **P/live, separately verified by E004nq:** same-SP11 rear 3840×2160 VideoRecord used **CSID1/VFE1 with ten image/stats WMs** in two captures, while VFE0 was inactive. The old source-only rear CSID0/VFE0 route candidate is superseded for Windows hardware-behaviour parity. **S→P link still UNPROVEN:** the original ISP callback's live index, descriptor pointer and zero/nonzero mode were not observed in the same Windows session; a label and eligible selector do not establish actual callback selection, BF0x0F IRQ or WM16 DMA retirement. E004ot passed 16 negative checks guarding false promotion.

**Native Linux L1–L3:** target the already measured shared VFE1 hardware outcome with exclusive front↔rear ownership; independently source/observe true IFE mode, WM16 bus/IRQ/per-buffer retirement before rear ISP runtime arm. No Windows numeric selector, service or original binary transplantation. Golden/front PIX/rear RAW fallback/IR remain protected.

## E004os: original IFE lookup pointers are populated by genuine conditional MMIO mapping

[E004os same-SP11 original ISP resource-array MMIO producer](../experiments/E004-front-ir-vd55g0/e004os-ife-original-mmio-map-resource-array-producer-static/README.md) source-traces the E004or global resource table RVA0x4AEE0 array fields +0x50/+0x20 from conditional allocation (RVA0x2C84/0x2D00) through descriptor-matched original **`MmMapIoSpaceEx`** calls (IAT RVA0x3F170, independently distinguished from `MmUnmapIoSpace` at 0x3F328) with descriptor input start+0x18 and length+0x20. The mapped pointer is stored in first/second array entries at original RVAs0x31DC/0x3214 for global+0x50 and 0x3270/0x32F4 for global+0x20, via proven global alias 0x4A720+0x810 or +0x7E0. The IFE lookup source returns one of those mapped-array entries to context+0x140. **97 original exact ARM64 instructions, two original IAT import identities and 16 fail-closed checks PASS**. This is original software-resource-to-MMIO-map provenance [S], **not** evidence that the live rear4K selected a specific physical VFE1 entry, mapped successfully, retired BF WM16 DMA or produced native Linux optical4K.

**Linux L1–L3:** distinguish device resource mapping from per-generation WM bus/IRQ/DMA retirement. Never copy opaque Windows resource arrays or free WM16 DMA on register write, callback return or software event. Continue source-identifying the physical IFE instance and safe stop/IRQ/buffer ownership before rear experimental ISP runtime arm. Golden/front PIX/rear RAW fallback/IR protected.

## E004or: original IFE register-window base is selected from a global resource-table pointer

[E004or SHA-locked original-SP11 IFE register-window provenance](../experiments/E004-front-ir-vd55g0/e004or-ife-register-window-provenance-static/README.md) links IFE init RVA0x22408 lookup RVA0x2B568 to context+0x140 base pointer, and context+0x150 selected window at original base+0xC00 (zero-state) or +0x1200 (nonzero). The original PE jump table independently maps lookup selectors **0→0x2B590, 2→0x2B5B8, 3→0x2B5C8**, returning respectively the first pointer from global resource-table field+0x50, first pointer from field+0x20 or second pointer from field+0x20 (global table RVA0x4AEE0). The E004oq finalizer's selected-window offsets consequently mean original-base-relative +0xC18/+0xC1C/conditional +0xC08 (zero) or +0x1218/+0x1208 (nonzero). **93 exact original ARM64 instructions, three original PE jump-table branches and 16 negative tests PASS.** These are software pointer/offset relationships [S], **not** identification of the active rear physical VFE mapping, WM16 DMA/IRQ retirement or native rear processed 4K.

**Linux L1–L3:** source-map resource-table population and real per-instance MMIO identity before porting relative writes. No owner handoff, DMA buffer free or rear ISP runtime arm on finalizer return/software event alone. Preserve Golden/front PIX/rear RAW fallback/IR.

## E004oq: original mode-selected IFE finalizers write distinct registers, not DMA acknowledgements

[E004oq original same-SP11 ISP mode-selected finalizers](../experiments/E004-front-ir-vd55g0/e004oq-ife-mode-selected-finalizer-register-writes-static/README.md) resolves E004op's context+0x6B690 resource finalization pointer: IFE selector state+0x6B678 chooses source-verified **zero-state RVA0x1D2B0** or **nonzero-state RVA0x1BE80**, original PE entries, invoked at stop helper0x27358 before software pending flag+0x171. The complete nonzero finalizer writes original register base+0x24/+0x28 and selected register window+0x18/+0x8; zero-state writes original base+0x34/+0x38 and selected window+0x18/+0x1C (conditionally +0x8). Both call complete 14-instruction helper0x1C958 for software bookkeeping. **94 exact original ARM64 instruction checks, two original PE entries and 14 negative mutations PASS.** Real conditional register-control writes [S] are proven, **not** physical VFE/WM16 IRQ/DMA stop, live rear selected IFE mode/base, BF0x0F or Linux native processed rear4K.

**Native Linux L1–L3:** do not transplant mode-agnostic register writes or release DMA on finalizer return or subsequent software event. NEXT source-confirm actual mapped IFE register windows, independent VFE WM16 hardware bus/IRQ/queue retirement and same-session rear selected mode before experimental Linux rear runtime arm. Golden/front PIX/RAW fallback/IR protected; rear ISP remains DENIED.

## E004op: IFE stop-helper pending flag → two distinct software event objects

[E004op original-SP11 pending flag producer and two event-dispatch modes](../experiments/E004-front-ir-vd55g0/e004op-ife-stop-pending-flag-two-event-modes-static/README.md) checks 50 exact original ISP ARM64 anchors, four original PE function entries and 14 fail-closed negative cases. IFE bounded stop helper0x27278 sets active marker context+0x173=1 and, **after its still-untraced resource finalization callback +0x6B690**, writes pending-progress context+0x171=1 at RVA0x2738C then directly signals original imported **KeSetEvent** on context+0x38. Distinct original mode-one handler0x1C9D0 and mode-zero handler0x1EF90 each conditionally clear that same +0x171 flag and call E004oo's later event helper, which signals a **different event object context+0xC8**. This is conditional software lifecycle [S]; the selected live Windows rear mode, upstream hardware event, BF0x0F, WM16 bus/IRQ/DMA retirement and Linux native rear optical4K remain UNPROVEN.

**Linux L1–L3** must not free or hand off DMA on either KeSetEvent or flag alone; independently verify finalization callback, actual bus/IRQ completion and generation-matched per-WM buffer ownership. Rear experimental ISP stays runtime DENIED and Golden/front PIX/RAW fallback/IR safe.

## E004oo: later IFE progress helper is an EVENT SIGNAL, not DMA proof

[E004oo exact original same-SP11 IFE progress-to-event trace](../experiments/E004-front-ir-vd55g0/e004oo-ife-later-progress-event-not-dma-ack-static/README.md) resolves the E004oh later progress path: if device context flag +0x171 is nonzero, original RVA0x1F244 clears it and 0x1F254 calls helper RVA0x241D8. The entire 33-instruction helper checks context, signals through wrapper RVA0x2A1D8 and reports wrapper errors; original imported ntoskrnl IAT slot RVA0x3F2E8 is independently verified **KeSetEvent** (not wait or clear). **60 exact original ARM64 instruction checks, three original import identities and 11 negative tests PASS**. This is original static software event signalling [S], **NOT** proof of a live rear4K path, WM16 hardware fence, IRQ drain or safe buffer retirement. Another hardware-driven precursor may exist, so do not claim the whole stop lifecycle is software-only.

**Native Linux L1–L3:** neither CFG0 zero, per-resource return, context-flag clear nor KeSetEvent is by itself a safe image/statistics DMA retirement predicate. Next locate the producer of +0x171 and independent WM16 bus/IRQ/queue per-buffer completion, plus live rear selected IFE mode. Runtime rear ISP remains DENIED, Golden/front PIX/rear RAW fallback/IR intact.

## E004on: first known CSID/IFE/CDM callbacks reject 0x809 as physical stop

[E004on original same-SP11 ISP first-callback receiver trace](../experiments/E004-front-ir-vd55g0/e004on-isp-selector-809-three-concrete-core-receivers-static/README.md) independently verifies **57 exact ARM64 instructions** and 13 negative cases: if selector 0x809 is forwarded to the source-identified installed first callbacks under valid input, **CSID takes a diagnostic/default path and returns status 0**, **IFE bypasses its 0x805 stop helpers and returns status 0**, whereas **CDM's unrecognized-selector route returns 0x0E (14)**. These are separate per-core conditional *software* return contracts [S], NOT proof of live rear selected list, hardware stop, safe DMA/IRQ retirement or any Windows 0x809 meaning. The CSID/IFE zero default is emphatically **not physical stop acknowledgement**.

**Linux L1–L3:** no Windows-selector translation, no owner handoff or DMA buffer free on generic 0x809 callback status. Independently prove later IFE/WM16 bus, IRQ, queue, DMA retirement and same-session rear Windows selected mode. Rear Linux hardware ISP runtime stays denied; Golden, native front PIX, RAW/software rear fallback and IR safe.

## E004om: source-verified list producer for the generic selector 0x809 core forwarding

[E004om same-SP11 original ISP manager-list provenance](../experiments/E004-front-ir-vd55g0/e004om-isp-manager-core-list-producer-static/README.md) connects the conditional 0x802 configuration branch to E004ol's later generic 0x809 consumer: on a zero-existing-count gated path it obtains a hardware descriptor from original global +0xE3E8 and appends either two descriptor-sourced halfword core indices (RVA0x170F0/0x17110), or one selected index in alternate scans (0x1723C/0x17420), into the same manager list starting at word index six, incrementing manager count at +0x24. The generic 0x809 branch subsequently reads those exact fields. This is **S/static** original source, 80 exact ARM64 anchors and 17 fail-closed tests, NOT complete list lifetime, same-session Windows rear selected list, callback meaning, IRQ/DMA stop or native Linux optical 4K.

**Linux L1–L3 gate:** source-trace the concrete installed CSID/IFE/CDM first callback bodies' default 0x809 branches and returns. A 0x802-configured list is not automatically a physical camera-owner handoff, nor is 0x809 an alias for 0x805. Rear runtime remains denied; do not release WM16 on software stop alone.

## E004ol: selector 0x809 routes through a DIFFERENT generic core dispatcher

[E004ol same-SP11 original ISP selector0x809 trace](../experiments/E004-front-ir-vd55g0/e004ol-isp-selector-809-independent-dispatch-static/README.md) checks 58 exact original ARM64 instructions and 12 fail-closed negatives: manager selector 0x809 does **not** match explicit 0x80C/0x808/0x804/0x805/0x803/0x802 branches and instead takes generic/default RVA0x1932C, reading a configured list starting at manager index six and forwarding original w1=0x809 through eligible per-core callback records. This is a **conditional software forwarding route [S]**, NOT evidence that a particular callback executes in Windows rear VideoRecord, that 0x809 means physical stop/DMA retirement, or that the chosen list corresponds to 0x805 CDM/IFE/CSID stages. Its signed >=4 core-ID check does not independently prove a negative lower bound.

**Linux L1–L3:** never interpret an opaque Windows selector as a Linux command or a hardware-quiescence signal by analogy. Identify 0x809's actual selected record receiver(s)/argument+return ABI and independently prove IRQ/bus/WM16 DMA retirement; rear Linux ISP runtime still DENIED, Golden/front/rear RAW fallback/IR preserved.

## E004ok: original BF CFG0 stop's immediate tail is software bookkeeping, NOT DMA retirement

[E004ok exact original-ISP immediate BF callback tail](../experiments/E004-front-ir-vd55g0/e004ok-bf-stop-cfg0-postwrite-software-state-static/README.md) traces the **conditional E004oj zero-state/BF 0x300D** write at RVA0x1DA74 through its real branch 0x1DA78, common tail 0x1DB2C and **entire original 16-instruction helper RVA0x1C990–0x1C9CC**. The helper stores context mapping/software status and returns; the valid per-resource branch sets a software flag; the outer resource loop continues. The helper does **not** poll or acknowledge WM16 DMA/IRQ completion. This is **S/static**, 47 exact original ARM64 anchors and 12 fail-closed tests, **not** proof of a live rear VideoRecord selection, that no asynchronous or later drain exists, or any Linux-native rear hardware-ISP 4K optical frames.

**Linux L1–L3 stop invariant:** writing WM16 CFG0 zero and returning from a resource callback cannot authorize buffer free, ownership handoff or IRQ teardown. Trace the independent later IFE progress/event helper, BF FIFO8/WM16 IRQ and hardware bus stop/actual buffer lifetime; pair with same-session rear Windows selected state/base before runtime arm. Existing rear ISP source remains runtime-DENIED; Golden, native front PIX, rear RAW/software4K and IR privacy unchanged. Numeric Windows selector 0x809 remains independently UNKNOWN.

## E004oj: the BF resource's original zero-stop write matches WM16 CFG0 at +0x1E00

[E004oj independent register-window and BF jump-table trace](../experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/README.md) combines three SHA-pinned original-source facts: (1) IFE initialization selects **original register base +0xC00 in its zero state**, source RVA 0x22464–0x2248C, and +0x1200 in the alternate state; (2) the 0x805 bounded stop-resource loop invokes the zero-state handler **0x1D830** with **resource port 0x300D and stop flag zero** on the conditional matching path; (3) original resource jump-table entry **13** points precisely to RVA **0x1DA6C**, which writes **zero** to **`[selected_register_window+0x1200]`** at RVA 0x1DA74. **Conditional zero-state register arithmetic: original base +0xC00+0x1200 = original base +0x1E00.** The independently mapped BF-associated **WM16 CFG0 VFE+0x1E00** from E004nv matches the offset exactly. E004oj source-verifies 35 original instructions, the source jump-table entry and 14 fail-closed negative tests.

This closes a **specific conditional static control-write link** across AVStream/ISP resource stop and the independently mapped BF/WM16 CFG0 register. **It does NOT establish** the live Windows rear4K instance's selected zero-state callback or actual VFE1 mapped base, BF0x0F event/group8 FIFO/WM16 DMA completion, interrupt acknowledgement, or safe buffer retirement after the zero write. A write to CFG0 cannot alone authorize Linux to release an in-flight statistics surface. The next hardware-factual gate is **post-write bus/IRQ/WM16 drain plus same-session selected register-window provenance**. Port only independently verified low-level effects into native Linux CAMSS, not Windows opaque numeric command plumbing or AI effects.

## E004oi: selectable original IFE stop-resource callback reaches BF-associated port 0x300D

[E004oi original ISP IFE callback selection](../experiments/E004-front-ir-vd55g0/e004oi-ife-resource-callback-bf-port-static/README.md) traces the exact producer of the previously anonymous E004oh bounded stop-resource callback. Original IFE initialization compares mode/state field **+0x6B678** at code RVA 0x19FB0 and selects between two **source-checked original function entries**: nonzero state **0x1C0F0**, zero state **0x1D830**. It stores the selected function in IFE field **+0x6B688** at code RVA **0x19FE8**. The original bounded 0x805 IFE stop helper 0x27278 reads that **same field** at 0x272E4, invokes it with the resource ID and **stop flag zero** at 0x27300, and later invokes a distinct post-loop callback at 0x27358.

**The zero-state callback 0x1D830 explicitly recognises resource port 0x300D** at code RVA **0x1D850–0x1D860**. This is the same numeric BF statistics resource previously identified in the independent OEM static E004nv handler. The connection is **conditional static original source only**; the rear Windows live 4K profile's selected callback mode, actual invocation of this branch, BF event0x0F, FIFO8/WM16 DMA quiescence and Linux native ISP4K optical pixels are **not proven**. The nonzero-state callback must **not** be classified as lacking BF merely from a different dispatch style. E004oi source-locks 35 exact original ARM64 instructions and 16 fail-closed cases, with no OEM binary export or Golden runtime change.

**Next: trace resource 0x300D through the zero-state callback using stop flag 0 into actual VFE bus write-master IRQ/ack/DMA ownership and distinguish stop request from fully retired statistics surfaces**, then confirm which callback/profile Windows actually uses in a single bounded real rear session. Port hardware-specific effects into native Linux L2/L3 without copying Windows interface/control numbers or Studio Effects/AI.

## E004oh: physical stop requires more than the original 0x805 manager callback

[E004oh static multistage IFE/CSID/CDM stop analysis](../experiments/E004-front-ir-vd55g0/e004oh-isp-multistage-stop-progress-static/README.md) follows the source-verified E004og concrete original **IFE 0x805** receiver into a **first stop helper RVA 0x221A0** and a **distinct, bounded per-output/resource helper RVA 0x27278**, with separate error handling. The original IFE additionally has an **independent stop-progress path RVA 0x1F230**, which checks and clears a progress flag and invokes an event-related function at 0x241D8. The CSID original separate path guards pending state and **atomically decrements a work counter RVA 0x1BCCC**, with a distinct worker/event path at 0x21B00. CDM separately changes command-state flags and calls an event-related helper in its own 0x805 receiving function.

**This source-backed separation prevents a dangerous Linux assumption:** completion of a top-level AVStream/ISP stop call, a CSID pending counter reaching zero, or CDM command-state progress is **NOT** proof that all live image/statistics WMs have finished DMA, that BF/FIFO group8/WM16 has completed, or that IFE interrupts have been acknowledged. The next concrete source trace is the **IFE 0x27278 per-resource indirect callback** to hardware-specific VFE/WM stop/IRQ/buffer-retirement status, checked against the exact live rear capture profile. E004oh has 45 exact original ARM64 instruction anchors and 14 fail-closed tests, but no live rear BF, native Linux rear hardware-ISP4K or Golden runtime modification.

## E004og: three actual original CSID / IFE / CDM receiving core functions

[E004og exact original OEM core callback proof](../experiments/E004-front-ir-vd55g0/e004og-original-isp-three-core-callback-implementations-static/README.md) follows E004of's pointer-provenance trail to **three specific first callable functions**, each both **source-stored by its own original hardware-core initializer** and **independently present in the original ISP ARM64 PE function-entry metadata**: CSID **RVA 0x211B0** (store 0x176A4), IFE **0x22CD0** (store 0x2234C), and CDM **0x28480** (store 0x1835C). Each original implementation explicitly distinguishes selector 0x804 and 0x805, not merely the outer ISP manager. E004og checks 45 instruction anchors and 14 fail-closed tests.

The **0x805 receiving functions have different stop-progress mechanisms**: CSID has worker/event-related logic and a further stop helper, IFE sequentially calls stop-command helpers at **0x221A0 and 0x27278** with separate error paths, and CDM has its own command-state/event path. **Function-pointer registration and branch disassembly do not establish a live rear 4K profile’s selected core instances, actual physical MMIO/IRQ/DMA/WM16 quiescence, or a universal per-mode safe release point.** The exact next source target is those concrete IFE/CSID/CDM stop helpers and their real register/interrupt/buffer lifetime. `0x809` and BF0x0F live completion remain separately unproven. Only the verified hardware effects belong in a native Linux CAMSS/V4L2 driver; no opaque Windows runtime, proprietary code, Studio Effects or AI transplant.

## E004of: ISP per-core interface *producer and consumer* verified

[E004of original ISP per-core interface provenance](../experiments/E004-front-ir-vd55g0/e004of-isp-per-core-interface-provenance-static/README.md) establishes the connection *between* the original core-array producer and E004oe's software dispatcher. The original device initialization calls array allocator RVA **0x3918** at **0x69484**, invokes shared core-record initializer **0x15768** at **0x69BFC**, and uses hardware-descriptor lookup **0x156E8** at **0x69820**. Its per-core initialization loop builds **0x30-byte-stride records**, stores individually obtained callable-interface pointers into the record's vector at **0x698A8**, and the manager later indexes and checks these same record types before per-core indirect calls. E004of verifies **56 original ARM64 instructions and 15 fail-closed cases**, exporting safe scalar RVAs only.

**Crucial still missing:** the actual **first function installed in each CDM/IFE/CSID interface** and its request/result ABI are **not source-decoded** by record-pointer provenance. The mode-dependent active-core set in live Windows rear 4K, selector 0x809, BF/WM16 physical retirement, exact safe-stop hardware/IRQ/DMA proof and native Linux processed rear4K optical output remain unproven. Do not copy Windows selectors/complex interface machinery or AI effects into Linux. Next trace the dynamic hardware-descriptor-provided callable function entries into the original per-core method bodies and their physical hardware effects before changing protected Golden.

## E004oe: CDM/IFE/CSID manager dispatch order now source-verified

[E004oe original ISP six-stage source trace](../experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/README.md) independently matches each of the six lower per-core indirect calls to an original ISP **CDM/IFE/CSID failure-diagnostic reference**, checking the diagnostic’s original RVA and hash rather than inferring component identity from proximity. In the *eligible* nested hardware-manager branch **0x804** (RVA 0x15EE0), the software-dispatch order is **CDM → IFE → CSID** (call RVAs 0x15F50, 0x15FEC, 0x16208); for **0x805** (RVA 0x16300), it is **CSID → IFE → CDM** (0x163C8, 0x16434, 0x164B4). The source checker covers **55 original ARM64 instructions and 13 fail-closed tests**.

**Do not transplant a universal Linux startup sequence from these numbers.** Hardware blocks can be skipped based on current state and mode, lower callbacks may return before DMA/interrupt teardown finishes, and the active Windows rear VideoRecord backend/profile remains unobserved. The actual per-core callback bodies and ABI, 0x809, physical stop/WM16 drain/BF completion and native Linux rear processed-4K optical output all remain **UNPROVEN**. Next trace the per-core interface-array *producers* and callback implementations and verify physical effects before altering protected Golden/Linux CAMSS.

## E004od: the second ISP callback resolves to a hardware-manager pool and per-core fan-out

[E004od source-backed nested ISP hardware-manager chain](../experiments/E004-front-ir-vd55g0/e004od-isp-hw-manager-nested-start-stop-static/README.md) follows the *previously unidentified* ISP device-context field +0x10 back to a **typed-context initialization path at original ISP RVA 0x6A0A0**. A source-checked helper at 0x15A40 allocates an interface in a **bounded 16-entry pool**, with 0xE38-byte record stride and interface field at record +0x48. It installs the **actual nested callback RVA 0x15D70**. The AVStream engine's conditional ISP callback path is thus AVStream → per-GUID backend → ISP outer callback 0x4E30 → device context +0x10 → hardware-manager 0x15D70, **not a direct engine register write**.

The original hardware-manager callback has separate source-checked selector **0x804 branch at 0x15EE0** and **0x805 branch at 0x16300**, each with independently guarded fan-out to several lower per-core callable interfaces and return/error handling. The driver also has ISP HW Manager IFE/CSID/CDM start/stop diagnostics. **Neither branch yet proves the receiving per-core implementations, physical CSI/VFE register order, real stop/IRQ/DMA retirement, or that a live rear 4K Windows session chose this route.** Do not assign a hardware meaning to 0x809 from analogy: it is separately UNDECODED. E004od pins 50 original source instructions and 16 fail-closed negative tests while exporting only safe scalar evidence.

**Next implementable boundary:** trace the per-core ISP HW-manager receiving IFE/CSID/CDM callback implementations and their per-mode argument/output contracts; independently validate real Windows rear VideoRecord/preview/front-rear-switch selection before any Linux runtime change. Linux L0–L3 owns safe sensor/CSI/ISP/DMA lifecycle and verified hardware effects; Windows orchestration/AI remains out of scope.

## E004oc: nine AVStream backend identities now mapped to original OEM providers

[E004oc original same-SP11 device-interface routing](../experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/README.md) closes E004ob's static **identity** ambiguity. The original AVStream driver has a **nine-entry, 72-byte-stride device-interface table** at RVA 0x2ECE0; its binder selects a record using a GUID-derived 32-bit key and passes the corresponding GUID to IoGetDeviceInterfaces. **Seven** table identities have matching original provider **registration-code call sites** in the rear sensor, front sensor, auxiliary sensor, flash, ISP, platform and separate secure ISP drivers. In particular, **slot 1 → rear sensor, slot 4 → ISP, slot 5 → shared platform**, independently of the identical opaque interface-request number 0x002326AB previously identified in platform and ISP. The **shared platform GUID** is registered by the platform driver and separately queried by the original ISP/rear/front drivers; do not mislabel these *consumers* as duplicate platform providers. Two original AVStream slots have no provider identity in the 102 archived OEM .sys files: they remain UNKNOWN, not invented “extra sensors.”

**ISP callback follow-on, also static:** E004oc's [source-locked ISP callback delegation proof](../experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/README.md) tracks AVStream's conditional alternative callback into ISP RVA 0x4E30. For engine selectors 0x804/0x805/0x809, the ISP callback's code **forwards the numeric selector into a second nested interface at RVA 0x51E0**; 24 exact ARM64 anchors establish this, but the nested callback implementation, live rear selected route and hardware command semantics are UNKNOWN. Do not translate those selector numbers into Linux start/stop registers.

**Crucial remaining boundary:** this is **static device-interface registration/lookup code**, not observation of the *live* rear 4K session's selected backend, actual successfully registered device objects, returned callback implementation or semantic meaning of engine start/stop selectors. Next trace **ISP slot 4, rear sensor slot 1 and shared platform slot 5's specific returned callback implementations and argument shapes**, then independently validate Windows session profile/selection before implementing their hardware effects in Linux L0–L3. The registered Device MFT, BF event0x0F/WM16 physical completion and Linux-native processed rear4K are still unproven. The original binaries were read-only; do not add Windows services, proprietary effects or AI dependencies to native Linux.

## E004ob: AVStream opaque interface request has TWO OEM candidate receivers

[E004ob same-SP11 platform versus ISP request-code audit](../experiments/E004-front-ir-vd55g0/e004ob-dual-backend-ioctl-static/README.md) proves the E004oa sender's **opaque** internal request `0x002326AB` occurs in BOTH exact original OEM `qccamplatform8380.sys` and `qccamisp8380.sys`. Both independently compare the code, but their matched branches perform **different** operations: platform RVA `0x6364` clears a state flag and two fields; ISP RVA `0x566C` populates a pointer, sets its own state flag and installs an ISP callback. This is **20 exact ARM64 receiver anchors**, two original OEM SHA checks and 12 fail-closed mutations. A numeric match does **not** mean both drivers handled one request, share one structure, or that either branch ran in our live rear 4K VideoRecord.

**E004oc resolves this former identity gap statically:** AVStream slot 1 identifies the rear-sensor provider, slot 4 the ISP provider and slot 5 the shared platform provider, each with independently verified original OEM registration-code references. The **remaining** Windows→Linux boundary is the **specific returned callback implementation and parameter ABI for each selected interface**, not inventing meanings for 0x2326AB or the 0x804/0x805 engine selector numbers. Live rear profile/backend selection and ISP/WM16 physical completion remain unknown. Do not copy Windows interfaces, effects, AI or opaque identifiers into Linux.

## E004oa static bridge: actual AVStream → Windows kernel-device interface

The [E004oa backend binding trace](../experiments/E004-front-ir-vd55g0/e004oa-avstream-kernel-interface-bind/README.md) narrows E004nz's previously opaque dispatcher to a **source-backed external kernel-device interface acquisition**. Engine initialization selects a device-instance record and invokes OEM binder RVA `0x20B60`, which calls original Windows `IoGetDeviceInterfaces` and `IoGetDeviceObjectPointer`, constructs an **internal** device-control request `0x002326AB` via `IoBuildDeviceIoControlRequest` / `IofCallDriver`, and receives an **eight-byte interface result**. The engine stores that selected record; common dispatcher RVA `0x20DA8` then calls either an acquired interface-vtable entry or an alternate registered callback. Source verified by original driver SHA, **42 ARM64 instruction anchors, five PE import-table mappings, two engine virtual-table entries and 12 fail-closed negative tests**. No camera runtime was invoked.

**Crucial open boundary after E004oc:** the nine AVStream device-interface GUIDs and seven original provider registration paths are **statically identified**, but **which interface a live rear VideoRecord session selected, what the returned callback actually implements and the engine selector meanings remain UNKNOWN**. The 0x804/0x805 values are not Linux IOCTLs or a safe power/ISP recipe. Next trace the original **ISP slot-4 / rear sensor slot-1 / platform slot-5 callback implementations and parameter ABI** and then only independently verified hardware effects into L0/L1/L2/L3. The Device MFT and live BF event are separate unresolved issues.

## E004nz static bridge: the actual OEM AVStream camera engine

The new [E004nz AVStream control audit](../experiments/E004-front-ir-vd55g0/e004nz-avstream-profile-control-static/README.md) adds **66 SHA-pinned, exact same-SP11 ARM64 instruction anchors** rather than only inferring an orchestrator from a list of installed drivers. `surfacecamavs8380.sys` contains actual distinct **preview/video/still** handling and a logical **statistics pin**; `CCaptureFilter::AcquireFilterResources` rejects an already active filter and `CPin::SetState` handles stream/privacy transitions. A camera-core `OnConfig` path creates the topology and a distinct ISP worker receives completion notifications.

The OEM **configuration** path statically receives line count, gain, pipeline delay and skipped-frame information from a user-mode component, and processes a **profile ID, processing type and configuration packet**. A separate **per-request** path submits processing packets with request IDs. These are real code-level handoff points for L1/L2/L3/L4, not proof that any particular UMD, the registered Device MFT or optional IPE/BPS/FD branch was active during our rear VideoRecord test. Linux can keep deterministic hardware commands and safe buffers in CAMSS while using **small, open, user-controlled** algorithms for timing-aware AE/AWB/AF/IQ where necessary. Do not turn every Windows software effect into a Linux dependency.

`CCameraEngine::OnStart` (OEM RVA `0x1EFD0`) and `OnStop` (`0x1F130`) have **separate multi-step command call sites** through one indirect dispatch helper at RVA `0x20DA8`. The static numeric selector sequences are `0x804,0x804,0x5,0x17` and `0x805,0x809,0x805,0x18`, with branches that may skip calls. **Their recipient interface and individual meanings remain UNKNOWN**; these values are *not* Linux IOCTLs, directly proven sensor controls or a safe instruction recipe. The Windows engine separately diagnoses stopping IFE and stopping the sensor. The next static subtask is to identify the helper's backing interface/recipient and trace profile/request packet handlers across AVStream→platform/ISP/sensor, not to repeat a blind BF breakpoint.

The original OEM INF's `OEMCameraProfiles` examples are **comments**, not active profile registry assignments in **that INF**. There may be valid profiles in the driver or another installed component: the active rear 4K Windows profile is **unobserved**. MFT DLL registration remains separate from proof of any runtime MFT involvement. See E004nz `RESULT.json` / `extract-static-callgraph.py` / `verify.py`, which export/validate safe scalar RVAs only and keep original binary/Windows user-mode data private on SP11.

## Windows components and decisions — the slice ledger

| Slice | Established Windows SP11 evidence | What remains unproven and how to chase it | Independent Linux owner |
| --- | --- | --- | --- |
| W0 client/capture intent | E004nx/ny manual WinRT Color VideoRecord rear NV12 3840×2160 produced **365/366** and **1,152/1,154** valid frame handles in two no-KD sessions [P]. Script did not explicitly select preview, still-photo profile, autofocus or a front/rear switch. | Compare Camera-app preview/photo, manual VideoRecord, front↔rear switch, and a second client. Log requested stream pin, profile, format and controls; do not assume all clients invoke identical ISP instructions. | Ordinary V4L2/libcamera camera selection, formats and manual/auto controls. No Camera-app clone. |
| W1 client sharing/profile mediation | AVStream OEM INF names distinct back/front/aux filter IDs and **Pin0 preview, Pin1 still image, Pin2 video capture** [S]. | Which layer arbitrates multi-client access, what opens/closes on a switch, which negotiated profile is active? INF describes exposed interfaces, not an observed runtime call graph. | Optional small user-facing policy; **hard CSID1/VFE1 lease and stop safety remain kernel-owned**. |
| W2 OEM AVStream | surfacecamavs8380.sys registers QCCamAvs KS service; E004nz source-checks distinct preview/video/still/stats pin logic, camera-engine multi-command start/stop, topology/ISP worker and **separate config/per-request packet handoff** [S]. | Follow common helper RVA 0x20DA8 to its backing interface/recipient and map profile/packet entrypoints to actual platform, ISP and sensor handlers. Numeric selectors are not decoded and the active Windows rear 4K profile is not identified. | Media-controller graph, V4L2 subdevices, standard controls and kernel-safe hardware lifecycle; open 3A policy may remain outside kernel. No AVStream/KS service emulation. |
| W3 OEM Device MFT | OEM AVStream INF **registers** QcDeviceMFT8380.dll CLSID [S]. Separate mep_camera_component installs Windows Studio Effects [S]. | Is the OEM MFT loaded for the *specific* VideoRecord/profile? Does it apply a transform or send necessary hardware controls? Registration does **not** imply it ran or is an orchestrator. | Reproduce only demonstrated necessary hardware/profile functionality. Studio Effects/AI, synthetic background blur, eye-contact, etc. are **out of scope**. |
| W4 Qualcomm platform/resources | qccamplatform8380.sys has separate OEM Spectra 695 service and Surface board config/resource files [S]; sensor-specific power/CSI experiments already exist [P]. | Trace real per-mode power/clocks, resource votes, shared-core ownership, recovery and suspend boundaries; no invented hardware version based on driver name. | DT/ACPI-derived clocks, power/reset, CCI/interconnect runtime PM and bounded rollback in Linux kernel. |
| W5 individual sensors | Front IMX681, rear OV13858 and IR VD55G0 use distinct packages and modes [S/P]. Windows rear 4K uses CSIPHY1 4-lane D-PHY, front PIX uses CSIPHY2 C-PHY [P]. | Actual focus actuator presence/commands, still-photo differences, per-mode sensor IQ/power timing, IR emission security. **BF enabled does not prove an AF request or focus motor exists.** | Native sensor/actuator V4L2 drivers only for verified hardware; explicit controllable sensor modes, default-off IR illumination. |
| W6 ISP/CSI route | E004nq two independent Windows rear 4K sessions use **CSID1 IPP→VFE1**; front also uses CSID1/VFE1, while Linux rear RAW fallback uses **CSID0→VFE0 RDI0** [P]. Rear WM0/1 FULL Y/C, DS4/DS16, stats including WM16 enabled in the measured 4K mode [P]. | Which controller submits specific per-profile VFE, IQ/RT-CDM requests and buffer lifetime; what must change on front/rear handoff? | Independent Linux CAMSS/CCI/CSIPHY/CSID/VFE driver: verified shared-PIX state machine, specific mode recipes, protected front/RAW fallbacks. |
| W7 BF/stats completion | E005o physically observed **22 BF events with nonempty FIFO8/matcher** during **13 rear4K handles**; E005r source-locks type-1 BF to **CSID BUF_DONE bit7**, distinct from the IFE snapshot [P/S]. WM16 consumed-status activity exists; independently matched geometry is **WM16 CFG0 at VFE+0x1E00** and **WM16 ADDR_STATUS0 at VFE+0x1E70**. | Independent exact-buffer/same-generation completion, live composite-group binding, hardware stop and DMA/IOMMU retirement remain unproven. A BF callback alone is insufficient. | Source-proven per-mode IRQ/ACK, Linux-owned output identity and safe retirement; E005n is isolated/build-only. |
| W8 ICP / tuning / 3A control | Rear has separate OV13858 OEM tuning; front sensor/ISP live experiments show bounded 3A/stat paths [S/P]. | Source the REAR-specific packet command, timing, stats to 3A feedback and legal Linux-compatible firmware path before enabling. | HW-critical RT-CDM/ISP register submission and DMA lifetimes in kernel; variable-rate **AE/AWB/AF algorithms and policy generally in a small open libcamera IPA**, user-overridable. |
| W9 pixel presentation | Windows WinRT delivers *application-visible* NV12 4K handles [P]; rear VFE physical WM stride is **5120**, packer 0x0B with separate metadata offsets [P]. | Prove actual Linux native ISP frame data/colourimetry, physical vs portable layout conversion, frame identity/cadence. | V4L2/libcamera advertises **truthful** formats/strides/timestamps. HW UBWC/metadata is **not automatically linear NV12**; use validated conversion only when necessary. |

**A Windows AVStream pin is a logical stream, not a VFE write master.** A complete application NV12 frame is not equivalent to every physical hardware DMA/stat output having completed. A **registered DLL** is not proof of a running DLL or of a necessary hardware command. An OEM Windows BF branch is not proof that BF ran in a manual VideoRecord session.

## Linux port ownership: L0–L6, and what we can ignore

| ID | Port this behaviour | Keep out of kernel / what not to port | Evidence gate |
| --- | --- | --- | --- |
| **L0: physical sensor resources** | Per-sensor power, clocks, reset, CCI, CSI wiring/mode/standby; separate IR privacy. | Windows INF/driver semantics and unverified flash/IR activation. | Independent sensor hardware identities, safe power lifecycle and CSI evidence. |
| **L1: mode and exclusive ISP owner** | Kernel-owned atomic CSID1/VFE1 PIX lease, owner/capture generation, no conflicting front/rear PIX stream, quiesce/stop/IRQ drain and safe handoff. | Reproduce no Windows Frame Server; policy may be outside kernel but **hardware lock may not**. Do not infer that Windows always switches sensors without closing/reopening. | Source-verified front→rear→front hardware stop and no stale in-flight DMA/IRQ. |
| **L2: CSI/ISP configuration** | Rear/front-specific CSID RX/IPP, VFE WMs, start/stop order, per-mode IQ/RT-CDM and safe recovery in native CAMSS/CCI. | Do not mix rear D-PHY with front C-PHY registers; do not run Windows PE .sys, .dll, tuned .bin or unsupported ICP firmware in Linux. | E004nr/ns are only source-compiled and uncalled. Real rear processed ISP stream not yet achieved. |
| **L3: DMA/interrupt ownership** | Allocate ALL outputs enabled in the chosen profile (FULL, DS, metadata/stats), verify 32-bit IOMMU bounds, queue exact request generation, decode actual event groups, retire only proved-completed buffers after independent stop. | Do not pretend ten clients always apply: E004nu ten-WM contract is for the **measured OEM rear 4K mode**; optional BF can be omitted **only if a separate HW config/IRQ/buffer contract proves WM16 disabled**. No timeout-triggered unsafe free. | E004nt/nu/nv are source-compiled but runtime-denied; Windows BF/FIFO8 is live-proven in E005o, while independent WM16 retirement remains open, and Linux native rear 4K ISP frame unproven. |
| **L4: image/focus algorithms and controls** | Explicit manual exposure/gain/WB/focus where actuators exist, optional AE/AWB/AF, per-frame stats→decision→sensor/ISP update with known frame latency and user override. | Avoid embedding open-ended policy, heavy 3A loops, AI and pixel effects in kernel IRQ/ISR. A small libcamera IPA is acceptable **without a proprietary orchestrator**. | Rear calibration, AF hardware, stats frame IDs and IQ feedback unverified. Do not make BF obligatory merely because WM16 was enabled in Windows. |
| **L5: portable frames and metadata** | Truthful format, stride, colour, timestamp, monotonically owned frame ID, complete output and bounded conversion if needed. | VFE WM physical metadata/UBWC/packer does not itself mean standard linear NV12 or a good optical image. | Preserve working Linux rear RAW→software 4K and front QC10C path while independently proving rear native 4K ISP image content. |
| **L6: app integration** | Ordinary front/back selection for V4L2/libcamera/PipeWire/browser and video call; multi-client policy may use a thin open layer while kernel enforces physical limits. | Windows Camera app, Frame Server, Windows Studio Effects, background replacement, AI appearance processing, Hello identity pipeline are **not parity goals**. | Confirm the final default capture route works in an independent ordinary app; do not mask missing HW using a synthetic or software-fallback stream. |

**“Integrated into the driver” means integrating deterministic, safety-critical hardware behaviour into Linux CAMSS/V4L2 drivers**, not transplanting Windows driver code or forcing all policy into the kernel. A small, optional open userspace layer for mode negotiation and control algorithms is normally the better Linux interface, with full user control; it must not be required merely to prevent unsafe shared-hardware access.

## Schematic 2: native camera/session state machine

~~~mermaid
stateDiagram-v2
 [*] --> OFF
 OFF --> ACQUIRED: select validated camera/profile, lock PIX owner
 ACQUIRED --> POWERED: sensor regulators / clocks / reset / CCI
 POWERED --> ROUTED: CSI PHY, CSID, VFE / assert no conflicting owner
 ROUTED --> PREPARED: safe IQ/RT-CDM and all enabled DMA outputs
 PREPARED --> STREAMING: request generation / IRQ arm / sensor start
 STREAMING --> STREAMING: verified frames and optional 3A controls
 STREAMING --> QUIESCING: stop, switch, end, timeout, failure
 QUIESCING --> DRAINED: sensor off / VFE disabled / DMA+IRQ retired
 DRAINED --> OFF: free only retired buffers / power down / unlock
 DRAINED --> ACQUIRED: other camera after complete safe handoff
 QUIESCING --> FAULT: cannot prove hardware has stopped
 FAULT --> OFF: only after independently verified recovery
~~~

Front/rear PIX **share CSID1/VFE1** in the measured Windows routes. A front→rear switch is therefore not just toggling a sensor pointer: it requires quiescence and an exclusive owner transition. Independent Linux rear RAW and front IR routes have their own verified scope and must not be silently conflated with PIX ownership. No implicit IR illumination.

## Future investigation: identify the missing *request-to-hardware* link

For each named mode, keep a single-session request ledger: **client → chosen camera → OS pin/profile → active OEM AVStream controls → platform/sensor/ISP request → CCI/CSID/VFE register/output mask → IQ/stats buffers → hardware IRQ/frame completion → safe stop**. Record UNKNOWN wherever no same-session source exists.

| Controlled Windows scenario | Which architectural question it isolates | What is NOT automatically proved |
| --- | --- | --- |
| A. Manual rear 3840×2160 VideoRecord | Existing rear baseline, active WMs, dispatcher mode, BF status and IQ per frame. | Photo/focus/preview, BF IRQ, or Linux-native 4K. |
| B. Rear preview on the SAME app | Alternate preview pin, crop, stats and profile transition. | Identical VideoRecord pipeline or OS compositor effects. |
| C. Rear still-photo and **explicit focus if supported** | Whether photo/AF changes BF/WM16, actuator, IQ/RT-CDM or stats ring. | An actuator or AF request merely because BF is enabled. No automatic flash. |
| D. Front RGB known-good stream | Different C-PHY and front nine-WM contract on shared CSID1/VFE1. | That front data/colour tuning or IRQ timing applies to the rear. |
| E. Front→rear→front in one client | Actual Windows stop, close/reopen, shared-core owner and residual IRQ/DMA lifecycle. | That two front/rear physical PIX sessions run concurrently. |
| F. Two clients / video-call / browser | Whether Frame Server shares/rejects/renegotiates profiles and which layer makes that choice. | That Windows uses one universal “camera orchestrator” executable. |

**Recommended evidence order:** (1) use the E004oc static AVStream GUID→OEM provider map to trace each slot-4 ISP, slot-1 rear sensor and slot-5 shared platform returned interface's **actual callback implementation and per-selector request ABI**; check the Device MFT's role **without assuming it loaded**; (2) bounded, permissioned non-image Windows ETW/Media Foundation/KS session logs of A–F; (3) only if needed and permitted, debugger work conditioned on **already-flowing** real frames, first establishing actual IRQ handler mode, then BF bit7/group8/WM16 retirement. Do not bypass blocked debugger safety checks. Do not export Windows private OEM binaries, KD logs, firmware, image data or DMA pointers.

## Permanent evidence pointers and no-regression contract

- OEM SP11 identities: [HARDWARE.md](HARDWARE.md); original Windows methodology: [WINDOWS_ORACLE.md](WINDOWS_ORACLE.md); existing ordinary Linux/fallback: [ORDINARY-LINUX-CAMERA.md](ORDINARY-LINUX-CAMERA.md).
- [E004nq rear CSID1→VFE1 physical route](../experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase/README.md) **supersedes** a wrong Windows CSID0/VFE0 assumption.
- Rear ISP isolated sources: [E004nr graph](../experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/README.md), [E004ns CSID1](../experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline/README.md), [E004nt 4K DMA surface](../experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract/README.md), [E004nu ten WMs](../experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/README.md), [E004nv six groups](../experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/README.md): **source-only compiled, runtime DENIED, no native rear 4K ISP optical frame**.
- [Exact OEM static BF call chain](../experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/STATIC-BF-CALLCHAIN.md): *mode-0 branch* event 0x0F → WM16 hardware read, **NOT a live rear BF event**.
- [E004nx/ny actual no-KD rear WinRT 4K handles](../experiments/E004-front-ir-vd55g0/e004ny-rear4k-live-control/README.md): 365/366 and 1,152/1,154 application-visible handles, **NOT proof of live BF or Linux native ISP**.
- Preserve protected Golden FullIO v19c and front 27-frame native PIX, rear real RAW/software-NV12 fallback and IR safety. Do not install/arm newer rear source without independent hardware stop, DMA, image and rollback proof.

**New work must name one slice L0–L6 and one client/profile above, identify its evidence tier P/S/H/D and a next falsifiable test, and update this map when a new observation changes the component boundary.** Never chase a vague “orchestrator” when the missing choice can be localized to a client request, AVStream property, sensor mode, platform resource, ISP packet, stats algorithm or buffer-completion event.
