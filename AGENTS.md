## 2026-10-06 E011IU parent cookie epilogue accepted to 0x5BEA00 frontier

E011IU passes the parent `0x5F9438 -> 0x11F0` cookie check, restores the `0x5F8DC0` frame/nonvolatiles, preserves the return object in `x0`, and returns through `0x5F9458` to source caller `0x5BEA00`. NEXT E011IV advances only to the `0x5BEA08 -> 0xCAE740` 0xB0 allocator frontier. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IT parent status publication accepted to 0x5F9438 frontier

E011IT writes caller status `1` to `RVA 0x1731598`, preserves the caller-owned return object into `x0`, restores `0x1720` bytes of local stack, and stops before `0x5F9438 -> 0x11F0`. NEXT E011IU qualifies the parent cookie epilogue and return to `0x5BEA00`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IS helper cookie epilogue accepted to 0x5F9420 frontier

E011IS executes the `0x5F9724` helper epilogue under the accepted opaque-cookie contract, passes `0x11F0`, restores the frame/nonvolatiles, returns `x0=0` through `0x5F9748`, and stops at caller `0x5F9420`. NEXT E011IT qualifies the caller status publication and stops before its cookie check. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IR zero-backed publication accepted to 0x5F9724 frontier

E011IR executes the E011IQ zero-global branch through the helper publication stores: the `0x160A1F0` block is populated with source-owned zero state and ready flag `0x160A270=1`; secondary `0x16A3FE0/+8` stays zero. It stops before the helper epilogue at `0x5F9724`. NEXT E011IS qualifies the opaque-cookie epilogue and return to `0x5F9420`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IQ native 0x160A260 zero accepted to 0x5F96A0 frontier

E011IQ used the bounded SP11 Windows oracle because `RVA 0x160A260` is writable `.data`: the exact QcDeviceMFT8380.dll qword was zero after front-only initialization and remained zero after one successful NV12 1920x1080 front reader Start. The original `0x5F968C` load therefore yields zero and `0x5F9690` branches to `0x5F96A0`. NEXT E011IR continues from that branch target. One Windows one-shot/front Start was used; rear runtime stayed denied, no rear Start or kernel build occurred, and the machine returned to Golden Linux.

## 2026-10-06 E011IP zero enumeration fields accepted to 0x160A260 frontier

E011IP proves the E011DV-published enumeration buffer remains zero through the accepted callee return, executes all current helper field loads, takes the zero-byte branch to `0x5F9684`, and stops before global `RVA 0x160A260`. NEXT E011IQ resolves that global from existing authority/Ghidra/Windows oracle in that order. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IO published buffer accepted to 0x5F95AC frontier

E011IO reuses E011DV publication authority for nonzero global `RVA 0x169FDF0`, executes `0x5F95A4/0x5F95A8`, and stops before published-buffer offset `0x4950` is dereferenced. NEXT E011IP traces any intervening buffer writes before qualifying that field. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IN helper prologue accepted to 0x169FDF0 frontier

E011IN executes `0x5F941C -> 0x5F9578` and its exact save/cookie prologue, stopping before `0x5F95A4` reads global `RVA 0x169FDF0`. NEXT E011IO reuses accepted E011DV publication authority for that pointer. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IM parent return/store accepted to 0x5F941C frontier

E011IM stores the returned nonzero owned object pointer at parent `+0x18`, selects status `8` from the preserved pre-call `w22=8`, and takes the exact branch to `0x5F941C`. NEXT E011IN enters helper `0x5F9578` and stops before global pointer `RVA 0x169FDF0`. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IL outer epilogue accepted to 0x5F8EA8 frontier

E011IL executes the original `0x60079C..0x6007C4` epilogue, reuses the accepted opaque process-cookie contract, restores the complete saved frame/entry SP, and returns the nonzero owned object pointer to the E011DV caller at `0x5F8EA8`. NEXT E011IM qualifies the parent compare/store/status branch. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

## 2026-10-06 E011IK caller local zero accepted to 0x60079C frontier

E011IK source-qualifies `[sp+4]=0` from the original `0x6003D8` CSEL and `0x600400` store on the accepted allocation-success path, then executes `0x6006DC/0x6006E0` and selects the zero branch to `0x60079C`. NEXT E011IL advances the outer epilogue/cookie return. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.

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

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EF lowIO count / initializer return](experiments/E004-front-ir-vd55g0/e011ef-original-lowio-count-activation-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EE isolated original low-level I/O block publication accepted

The low-level table pointer at 0x16A2A90 now has a source-qualified producer prefix in a third, isolated emulator. Original initializer 0xCC08E8 acquires its owned index-seven lock, takes the explicitly owned cold pointer-zero branch, and calls original constructor 0xCC05B8. The constructor requests 64 records of 72 bytes, initializes each record through checked source stores and owned resource successes, returns the 4,608-byte block with exact NONVOL/SP, and original 0xCC093C publishes it.

256 cases pass: 738,304 added original visits, 169,728 exact ordered source-store chunks, 1,206,784 altered owned requests rejected, 33,280 exact dependency reads, 17,152 nested entries/ABI returns, 256 owned zeroed allocations and 16,640 owned API calls. Every complete E011ED row remains equal. Camera and isolated stream-initializer memory, permissions and frontiers remain unchanged; the new low-level initializer's entry-to-frontier memory/permissions and redzones match without resets. Forty-eight execution pins remain exact.

All 64 record resources are logically ready in the owned model. Each source record has an eight-byte all-ones field at +40, zero at +48, checked four-byte value 0x0A0A0000 at +56, byte ten at +60 and zeros at +61..+66; the remaining bytes stay owned-allocation zero. This proves neither native critical-section bytes nor valid native handles. Allocation and API success are explicit provider inputs; original allocator internals and native CRT initialization remain unproved.

Stop BEFORE 0xCC0948 reads four bytes from image+0x16A2E90, at lowIO-entrySP-96. NEXT **E011EF** establishes this runtime input before continuing the low-level initializer. The block constructor returned, but the low-level initializer has not returned and its logical lock stays held. Actual loader startup ordering and any joining of the three contexts remain unqualified. The stream initializer separately remains before 0xCB3338 / 0x16A2A90 at stream-entrySP-80; the camera separately remains before 0xCC6120 / 0x16A2A58 at outer-entrySP-1648.

Camera output, nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,989,120 includes two isolated initializer matrices and is not a joined trace. Full initialization/state joining, file/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EE isolated low-level I/O block publication](experiments/E004-front-ir-vd55g0/e011ee-original-isolated-lowio-block-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011ED isolated original stream-table publication prefix accepted

The runtime pointer at 0x16A2A58 has an original publisher: initializer 0xCB3260. Its prefix now executes in an isolated fresh emulator with explicit owned cold count/pointer inputs. Original source sets 512 slots, requests a 4,096-byte zeroed allocation, publishes the returned pointer, initializes the first logical standard-stream resource and writes image+0x1607060 into slot zero. The remaining 511 slots stay zero. Native allocation, CRT resource initialization and pointed stream contents remain unproved.

256 cases pass: 13,056 isolated original visits, 4,096 exact ordered source stores, 36,096 altered owned requests rejected, 1,024 dependency reads, 512 nested entries/ABI returns, 256 owned zeroed allocations and 256 owned resource-model calls. All E011EC rows remain equal; camera memory, permissions and its 0xCC6120 frontier remain unchanged. Isolated initializer entry-to-frontier memory/permissions and redzones match without resets. Forty-six execution pins remain exact.

Original 0xCB1650 returns zero on its null cleanup path. Original 0xCBA4B0 tail-calls the owned InitializeCriticalSectionEx model at resource 0x1607090 with spin count 4,000 and flags zero; both nested returns preserve NONVOL including SP. Model success and readiness remain explicit provider inputs, not native observations. The camera and isolated initializer states have not been joined.

Stop BEFORE 0xCB3338 reads eight bytes from image+0x16A2A90, independently checked index zero; current SP=initializer-entrySP-80. NEXT **E011EE** establishes the low-level I/O table's authority before continuing. The initializer remains active; full return and actual loader/CRT startup invocation are pending. The camera caller separately remains at 0xCC6120 / outer-entrySP-1648, with four active stream frames and its owned stream lock held.

Camera output, all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, callbacks, epochs and both registry locks remain retained. Its source-chain count stays 1,237,760; aggregate 1,250,816 includes the isolated initializer matrix and does not describe a joined trace. File/provenance collection, full helper/descriptor/profile startup, native runtime/CRT resources, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011ED isolated stream-table publication prefix](experiments/E004-front-ir-vd55g0/e011ed-original-isolated-stream-initializer-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EC bounded stream setup / owned CRT lock accepted

Original caller 0x600368 resumes with the completed formatter result and enters wrappers 0xCED2F0 / 0xCED0D8 / 0xCC6078 / 0xCC6108. The exact 37 private bytes plus 603 zeros remain intact. A pinned two-byte mode literal at 0x1363D40 qualifies the original first-byte nonempty gate; mode interpretation, stream selection and file contents remain open.

256 cases pass: 13,824 added original visits, 4,608 exact ordered stack stores, 37,632 altered owned requests rejected, 256 immutable mode reads, 256 inherited loader-binding reads, 1,280 exact callee entries, 256 lock-wrapper ABI returns and 256 owned lock-model calls. No allocation runs. Complete E011EB rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,237,760, with ancestor counts separate.

Original 0xCB7300 derives a critical-section request at 0x16A3000 using the inherited import binding. Its owned EnterCriticalSection model requires exact caller, argument, SP, readiness and initially unheld state; both OS-void X0 clobber cases preserve the wrapper's saved NONVOL/SP. The new stream lock model is held. Earlier publication CRT/SRW locks remain released. This does not prove native CRT resource initialization or synchronization.

Stop BEFORE 0xCC6120 reads the runtime stream-table pointer at image+0x16A2A58 / eight bytes, current SP=outer-entrySP-1648. Four stream frames remain active with pending returns 0x600454 / 0xCED330 / 0xCED150 / 0xCC60A0. NEXT **E011ED** establishes this runtime dependency's authority before continuing. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

Forty-four execution pins retain all nine allocations/redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks. Native runtime scalar/pointer selection, native CRT resources, file/provenance collection, full helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied; rough ~70% smoke estimate unchanged.

Zero new camera Starts/reboots/kernel builds/production C/PM changes. Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EC bounded stream setup / owned CRT lock](experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EB complete selected formatter output / consumer returns accepted

Original source completes the selected three-argument formatter with lengths 12 / 1 / 24, exact 37 private bytes, and original terminators at output indices 37 and 639. The retained 640-byte destination has 603 zero bytes after the output. All seven inherited consumer frames return to their actual callers with exact NONVOL including SP; their stack contexts and cookie scratch slots retire after proof. No output or result fixture is supplied or exported.

256 cases pass: 199,680 added original visits, 30,464 exact ordered store chunks, 221,952 altered owned requests rejected, 7,936 immutable reads, 4,096 ordinary callee ABI returns, 1,792 inherited consumer ABI returns, 512 cookie-push and 768 cookie-pop convention returns. All complete E011EA rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined visits are 1,223,936 with ancestor counts separate.

Remaining literal authorities cover 0x10F03B0 / 16 bytes and aligned 0x13F1F20 / 48 bytes, with the second literal at offset eight. One sparse cell at 0xF8B230 and the 304-byte cold cleanup body at 0xCA8658 are pinned. Forty execution pins retain inherited runtime initial-value models. Signed write-hook values normalize to the exact unsigned word before comparison; original execution and effects remain unchanged. Cookie conventions remain SP-16 / SP+16, distinct from SP-preserving leaves or OS stack-growth proof.

Stop BEFORE actual caller instruction 0x600440 inside 0x600368, SP=outer-entrySP-1456 and X0=37. No consumer frames remain active. NEXT **E011EC** continues this caller with the completed output and all ancestor ownership retained. The enclosing 0x5F8EA8 return, enumeration, factory, helper and parent remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, object/header/zero-array graph, callbacks, epochs and both registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, full helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied; guarded smoke remains pending and the rough ~70% estimate is unchanged.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EB complete selected formatter / consumer returns](experiments/E004-front-ir-vd55g0/e011eb-original-complete-constant-consumer-return/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011EA original first argument length / copy accepted

Original source now finds the first argument's NUL in an immutable 13-byte literal, reads its exact 16-byte window, and copies twelve private bytes into the retained 640-byte destination. The eight-byte store and four one-byte vector stores match independently pinned source bytes; the remaining 628 destination bytes remain zero. No string contents or length/copy result fixture is supplied or exported.

256 cases pass: 45,824 added original visits, 6,400 exact ordered store chunks, 49,920 altered owned requests rejected, 1,792 exact argument reads, 1,024 callee ABI returns, 512 argument-consumer ABI returns and 256 cookie-pop convention returns. All complete E011DZ rows remain equal; cumulative original-entry-to-frontier memory and permissions match without resets. Combined original visits are 1,024,256; all ancestor counts remain separate.

Original 0xF5E3E0 returns length twelve; the two 0xCAD1F0 calls execute zero padding and actual copy, and original 0xF5D480 writes the private bytes. Original 0xCACDF8 and 0xCAB178 return one with exact caller ABI. The 0x11F0 cookie-pop leaf restores SP+16 and all other NONVOL; this remains separate from a standard SP-preserving leaf and OS stack-growth proof. The earlier zero-destination invariant advances only through these checked original copy effects.

Stop BEFORE the byte read at 0xCA984C from image+0x1370762. NEXT **E011EB** continues the original parser and remaining arguments with the twelve-byte output and returned handler frames retained. Current SP=outer-entrySP-3200, output cursor=outer-entrySP-1380 and variadic cursor=outer-entrySP-1488. Seven consumer frames remain active; full consumer and outer 0x5F8EA8 returns remain pending.

All nine allocations, redzones, published 18,832-byte zero buffer/refcount one, callback table and registry locks remain exact. Native runtime scalar/pointer selection, pointed locale tables, complete helper/descriptor/profile startup, populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement still gate clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material stay private on SP11. See [E011EA first argument length / copy](experiments/E004-front-ir-vd55g0/e011ea-original-first-argument-length-copy/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DZ original parser dispatch / variadic argument accepted

The retained original consumer now reads a seven-byte immutable literal (including its terminator) and seven exact sparse classification/branch cells, dispatches the first argument through original 0xCAB178 / 0xCACDF8, and advances the actual variadic cursor by eight bytes. The original 0xCA65A8 scalar helper returns zero with exact callee-saved ABI; the separate 0x11D0 cookie-frame convention again changes SP by -16. No original literal contents or string result fixture is exported or supplied.

256 cases pass: 43,008 added original visits, 9,728 exact stack store chunks, 70,912 altered owned requests rejected, 2,304 exact immutable reads, 256 scalar-helper ABI returns, 256 cookie-frame convention returns and 768 nested entries. Every complete E011DY row remains equal; cumulative original-entry-to-frontier memory and permissions match with no resets. Combined original coverage is 978,432 visits; inherited DY/DX/DW/DV/DU/DT/DS counts stay separate.

The first argument pointer is original image+0x10F0380, and the variadic cursor is outer-entrySP-1488. Its pointed string contents, read extent and length remain unqualified. The destination remains 640 zero bytes; all nine allocations, redzones, published 18,832-byte zero buffer/refcount one, nested containers, callback table and both registry locks remain retained. Native scalar/pointer selection, pointed locale tables, alternate flags and complete consumer/outer/helper/descriptor/profile startup remain open.

Stop BEFORE actual 0xCACE90 -> 0xF5E3E0, return 0xCACE94, SP=outer-entrySP-3360, X0=image+0x10F0380 and X1=0x7FFFFFFF. NEXT **E011EA** qualifies the original bounded string helper and exact pointed data/read windows in this retained parent. Its 184-byte body metadata is pinned separately; no helper execution or string-length result is accepted here. Nine consumer frames remain active; the outer 0x5F8EA8 return is pending.

E011DM remains the empty RS-query proof and E011DN the limited Windows snapshot. Populated RS/AFD identity/generation/lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero new Starts/reboots/kernel builds/production C/PM changes; Golden payloads, EFI/GRUB and historical repositories unchanged. Originals and optical material remain private on SP11.

See [E011DZ parser dispatch / variadic argument](experiments/E004-front-ir-vd55g0/e011dz-original-parser-dispatch-variadic-argument/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DY cold runtime context / nested receiver setup accepted

Under explicit loader initial-value models, original source reads the zero-fill options scalar at 0x17A1150 and flag at 0x16A2A84, then the file-initial pointer pair at 0x16072D8. Original 0xCAD868 constructs the retained stack context, and original 0xCA6280 constructs the nested receiver fields. These are source effects under declared models; native flag/pointer selection remains unqualified.

All 256 cases pass: 20,992 added original visits, 11,264 exact setup store chunks and 68,608 altered owned requests rejected. Each case validates four exact runtime reads, 44 independently authored ordered stores and two nested entries. The original 0x11D0 cookie-frame leaf returns at 0xCA6298 with its deliberate SP minus 16 effect and all other nonvolatile registers preserved. This is a cookie-frame convention, not an SP-preserving leaf ABI or OS stack-growth proof.

Complete inherited DX/DW/DV/DU/DT/DS rows remain exactly equal and separate; combined original visits are 935,424. One cumulative original-entry-to-frontier memory and permissions snapshot passes. All nine allocations, prior nodes/arrays/redzones, published 18,832-byte zero buffer/refcount one, callback table and epochs remain retained. The 640-byte output destination remains entirely zero; all 44 new stores lie below it. Both registry locks remain held and CRT/SRW released.

Stop BEFORE actual call 0xCA6348 -> 0xCA94E8, return 0xCA634C. Six consumer frames remain active; consumer, outer 0x5F8EA8, enumeration, factory and helper returns remain pending. NEXT **E011DZ** executes the next original consumer with receiver at outer-entry SP minus 3104 and runtime context at minus 1888. The next exact 1028-byte body is pinned as metadata only; accepted source pins remain 32.

The two scalar cells are writable virtual zero-fill with no file-byte hash authority; only cold zero is accepted by this model. The writable file-initial pair identifies 0x1607180 / 0x1607650, without qualifying pointed tables. Alternate native flags, initialized runtime values, pointed locale/format/string contents, complete consumer output/returns, profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instructions/decompilation/raw records/proprietary names and optical material remain private SP11. Fresh one-shot Windows oracle/external SP7 KD remain authorized with fresh atomic identities and manual-only tasks.

See [E011DY cold runtime context / nested receiver setup](experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DX exact constant-data / retained consumer setup accepted

Original source now reads the exact opaque eight-byte window at 0x10F03A0 and enters the original nested consumer setup at 0x7AC38 / 0x7ACA0 / 0x6BDD0 / 0x6BD48. The original 12-byte leaf at 0xEDD0 returns the address 0x17A1150 at 0x6BD70 with exact ABI preservation. No constant contents, pointed strings, formatted result or consumer return fixture substitutes for execution.

All 256 cases pass: 19,200 added original visits, 8,448 exact stack store chunks, 52,224 altered owned requests rejected, 256 exact constant reads and 256 original leaf ABI returns. The 33 setup chunks per case have independently authored source/address/width/value/order contracts. Inherited DW/DV/DU/DT/DS results remain exactly equal and separate; combined original visits are 914,432. The original-entry-to-frontier memory and permissions snapshot remains cumulative.

The constant authority is the exact eight-byte file-backed nonwritable window, not the earlier exploratory 64-byte window. Five exact function bodies extend the inherited 25 source pins to 30. Four consumer frames remain active; their returns and the outer 0x5F8EA8 return remain pending. The original 640-byte destination and published 18,832-byte buffer are still entirely zero. All nine live allocations, callback table, epochs, locks, previous nodes and redzones remain retained.

Stop BEFORE 0x6BD8C, the next eight-byte read from writable virtual zero-fill coordinate 0x17A1150. NEXT **E011DY** establishes loader/runtime scalar authority and resumes the retained consumer. A static zero-fill coordinate is not proof of its native runtime value. Pointed constant strings, complete consumer/outer/factory/helper returns, selected profile/input deterministic startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production C or PM changes; Golden payloads/full EFI/GRUB/history unchanged. Original binaries/instruction text/decompilation/raw records/proprietary names and optical material remain private SP11. Authorized fresh one-shot Windows oracle/external SP7 KD remain available with fresh atomic identities and manual-only tasks.

See [E011DX exact constant-data / retained consumer setup](experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DW nested enumeration container / stack clear accepted

Original callee 0x600368 creates a fresh 16-byte object, executes original nested constructor 0x5E81B8 and attaches its returned 64-byte header. Original source creates and clears an 8192-byte array with 1024 zero QWORD slots, then clears a 640-byte stack buffer. No constructed-record, clear or return result fixture substitutes for source execution.

256 cases pass: 151,552 added original visits, 293,632 exact added stores and 26,624 altered owned requests rejected. All 256 nested constructor, 256 array-clear and 256 stack-clear ABI returns pass. Clear visits 122,624 and heap/stack clear chunks 262,144/20,480 are subsets. Inherited DV/DU/DT/DS visits remain separate; combined coverage is 895,232. The original entry-to-frontier memory/permissions snapshot remains exact.

The 16/64/8192-byte leases join six older disjoint live allocations, giving nine. Source constructs exact header/array/owner relations; five header reads have exact contracts. The published 18,832-byte buffer, two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and clears remain retained. Both registry locks remain held, CRT/SRW released. Native allocation, loader/runtime scalar selection, failures/concurrency/teardown and committed stack bounds remain explicit models or open gates.

Stop BEFORE 0x600420, next eight-byte read from 0x10F03A0. NEXT **E011DX** derives exact bounded constant-data authority and resumes the retained original callee. The outer callee return 0x5F8EA8 remains pending; enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DW the nested container proof, E011DV the cold buffer proof, E011DU the callback/epoch proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DW nested enumeration container / stack clear](experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DV cold enumeration buffer allocation / publication accepted

Under the declared virtual loader zero-fill scalar model, original enumeration requests fresh 18,832-byte storage, clears it through original source and publishes its pointer at 0x169FDF0 and reference count one at 0x169FDE8. No buffer/clear/publication result fixture substitutes for source execution.

256 cases pass: 237,568 added original visits, 603,136 exact added stores and 11,008 altered owned requests rejected. All 256 actual clear callee ABI returns and the single original entry-to-frontier memory/permissions snapshot pass. Clear visits 233,472 and chunks 602,624 are subsets. Inherited DU/DT/DS visits remain separate; combined coverage is 743,680.

All six allocations remain disjoint and live. Both registry locks remain held; CRT/SRW are released. The two-entry/32-slot callback table, epochs, earlier nodes, redzones, constructed container and prior clears remain exact. Loader scalar selection, allocator success/storage, native resource construction and committed stack bounds remain explicit models. Alternate nonzero scalar branch, native failures/concurrency/teardown and native selection are unqualified.

Stop BEFORE 0x5F8EA4 -> 0x600368, actual return 0x5F8EA8. NEXT **E011DW** integrates this original callee in the retained parent with the published buffer and six allocations. Its exact 1120-byte body metadata is pinned separately; no callee execution is accepted here. Enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DU the callback/epoch proof, E011DT the actual factory/enumeration bootstrap and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DV cold enumeration buffer allocation / publication](experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DU existing-table registration / enumeration publication accepted

Original source appends the second cleanup callback to the actual retained one-entry encoded exit table, using its existing 32-slot allocation without reallocation. Original enumeration guard publication advances its guard, global and actual TLS epoch to 80000042; the first-helper guard remains 80000041 and factory guard remains FFFFFFFF in-progress.

256 cases pass: 45,056 added original visits, 9,472 exact added store chunks and 27,392 altered owned requests rejected. All 2,048 original registration/publication callee ABI returns and the single entry-to-frontier memory/permissions snapshot pass. Inherited E011DT adds 127,744 visits and E011DS 333,312, giving 506,112 combined visits; counts remain separated.

Both registry locks and all five allocations remain owned and live. CRT/SRW are released; first callback, 30 unused slots, nodes, redzones, constructed container and prior clears remain exact. Readiness, native allocator construction and committed stack bounds remain explicit inherited models; native failures/concurrency/teardown remain open.

Stop BEFORE 0x5F8E24, four-byte dependency read from 0x1731598. NEXT **E011DV** qualifies this enumeration dependency and its subsequent branch while retaining the two-entry table and actual published epoch. The enumeration, factory and first helper have not returned.

E011DM remains the empty RS-query proof, E011DT the actual factory/enumeration bootstrap, E011DI the separate bootstrap proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DU existing-table registration / enumeration publication](experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DT actual-parent factory / enumeration bootstrap accepted

The original factory and enumeration bootstrap now execute in the actual live first-helper parent. The helper's published negative TLS epoch is retained; two fresh 48-byte sentinel nodes remain distinct from its 24/128/256-byte ancestor allocations. Original source initializes 190 fields, clears a 1040-byte stack record and enters enumeration under declared committed-stack bounds.

256 cases pass: 127,744 added original visits and 102,656 added exact store chunks; 333,312 inherited E011DS visits give 461,056 combined visits. Added invalid-contract rejections are 15,104, separate from 43,264 inherited. All actual guard/probe/clear return checks and the single entry-to-frontier memory/permissions snapshot pass.

Both registry locks remain held, SRW/CRT released. Factory and enumeration guards are FFFFFFFF in-progress; neither callee has returned or published its guard. OS/CRT/loader/allocator readiness and committed-stack bounds remain explicit models; native failures/guard-page growth/concurrency/teardown are open.

Stop BEFORE 0x5F94A0 -> 0xCA34A0, actual return 0x5F94A4, callback 0xF7B5E0. Existing encoded exit table contains one callback in 32 slots. NEXT **E011DU** executes this new registration against that nonempty table, then enumeration guard publication and the next dependency. Reuse E011DR registration/publication source and E011DT retained ownership.

E011DM remains the empty RS-query proof, E011DI the separate factory/enumeration proof and E011DN the limited Windows snapshot. Full helper/descriptor registry initialization, selected profile/input deterministic startup, populated RS/AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open before clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot/payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and tools remain authorized; use fresh atomic identity and keep originals/optical material private on SP11.

See [E011DT actual-parent factory / enumeration](experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DS cached object / nested lock / large clear accepted

The unchanged first helper caches inline object 0x17A4230 at 0x1731880, enters a distinct registry lock through original callbacks, writes bounded header fields and clears all 11,808 bytes at 0x17A4268 through original source. No cache/lock/clear result fixture is used.

512 cases pass: 666,624 original visits, including 345,088 added visits; 301,568 added clear visits are a subset. The large clear contributes 756,736 write chunks, counted separately from 66,560 other nonstack and 49,152 stack chunks. All 86,528 altered owned contracts reject. Whole memory/permissions, source/unmodified loader regions, actual callee returns, padding and the adjacent constructed container remain exact.

Runtime readiness, cold zero control cells and disabled tracing remain explicit models; buffer/padding poison are robustness fixtures. Native OS/CRT/allocator construction, failures/concurrency/teardown and full inline-object initialization remain open. Both registry locks are held; CRT/SRW locks are released.

Stop BEFORE actual call 0x5B8268 -> 0x5BDE08, return 0x5B826C. NEXT **E011DT** integrates this factory callee with the actual live parent, published TLS epoch and existing allocation leases. Positive global-epoch edge cases are not native cold-factory readiness proof. E011DH/DI remain separate factory/enumeration acceptance; E011DM remains the empty RS-query proof.

Full helper/descriptor registry initialization, selected profile/input deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement still precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C/PM changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged. Fresh one-shot Windows oracle/external SP7 KD and missing tools remain authorized; use a fresh atomic identity and preserve private originals/optical material on SP11.

See [E011DS cached object / lock / clear](experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DR original cleanup registration / guard publication accepted

The unchanged cold caller registers cleanup callback 0xF7B120 and publishes the helper guard through original code, without registration/guard result fixtures. The encoded exit table contains one callback in 32 slots; global, helper and TLS thread epochs agree.

512 cases pass: 321,536 original visits, including 173,056 CRT registration and 17,920 publication visits. All 62,464 nonstack chunks, 43,520 stack chunks, 5,632 added callee ABI returns and 62,976 invalid owned-contract rejections pass. Whole memory/permissions, immutable source/unmodified loader regions and the exact TLS epoch update are checked.

Loader/OS resource readiness, fresh allocation storage and a ready empty encoded CRT exit table remain explicit owned models. Native CRT initialization, failure/existing-table growth, callback execution/teardown and concurrency remain open. CRT and SRW locks are released; registry logical lock remains held.

Stop BEFORE 0x5B8104, next factory pointer 0x1731880 read at 0x5B8108. Parent/helper remain active. NEXT **E011DS** follows actual factory construction/publication in this caller; source references identify a pointer write at 0x5B8138, outside current acceptance. Full first-helper return and metadata descriptor registry initialization remain open.

E011DM remains the empty RS-query proof, E011DI separate factory/enumeration acceptance and E011DN the limited Windows snapshot. Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, permanent EFI/GRUB and historical repositories unchanged. Windows oracle/external SP7 KD and missing tools remain authorized; fresh boot and atomic identity for another oracle. Originals and optical material stay private on SP11.

See [E011DR registration / publication](experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/README.md). Earlier current/NEXT paragraphs below are historical.


## 2026-10-04 E011DQ original cold container construction accepted

The unchanged first-helper constructor 0x2EE1A0 completes its normal path and returns at 0x5B9094 with exact ABI. Original source constructs the 64-byte container, 24-byte self-linked sentinel and 128-byte array containing 16 sentinel pointers. Allocation storage/readiness/provenance are explicit owned models; no constructed-object or constructor/helper/guard result fixture is used.

256 cases pass: 65,280 original visits, 13,056 exact nonstack chunks, 12,288 stack chunks and 17,664 invalid owned contract rejections. Whole mapped memory/permissions, source/TLS immutability, allocation redzones/relations and actual constructor/callback/guard return ABI pass. Native allocator, failure/exception cleanup and teardown remain open.

Stop BEFORE 0xCA3450, actual return 0xCA34B0 and callback argument 0xF7B120, after only the four-instruction original registration-wrapper prefix. Parent/helper/wrapper active; registry logical lock held, SRW released and helper guard in-progress. Cleanup registration, helper guard publication, full first-helper return and full metadata registry construction/publication remain open.

NEXT **E011DR** qualifies cleanup registration and original helper-guard publication in this caller. E011DM remains the original empty RS-query proof, E011DN the limited Windows snapshot, E011DI the separate factory/enumeration proof, E011DO initialized-registry reuse and E011DP cold bounds/guard prefix.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DQ container construction](experiments/E004-front-ir-vd55g0/e011dq-original-cold-container-construction/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals/optical material remain private on SP11; another oracle needs a fresh boot and atomic identity.

## 2026-10-04 E011DP cold literal bounds / first-helper guard prefix accepted

The unchanged initializer writes uint32 literal bounds 239 and 282, enters first helper 0x5B80A8 and executes its original fresh TLS guard acquisition. No bound/helper/guard result fixture is used; loader TLS and OS lock readiness/operations remain explicit owned models.

128 cases pass: 18,560 original visits, 384 exact nonstack field-store chunks, 4,992 stack-store chunks and 6,528 invalid owned contract rejections. Whole mapped memory/permissions, immutable source/loader regions, actual lock-callback and guard-return ABI pass. The helper body is pinned to 4,104 bytes but only its bounded prefix is accepted.

The stop is BEFORE next dependency 0x2EE1A0, actual return 0x5B9094, pointer argument 0x17A7088 and scalar 65535. Parent/helper frames remain active, registry logical lock held, SRW released and helper guard in-progress. Full helper return, allocation/construction/publication and native OS resource construction remain open.

NEXT **E011DQ** qualifies that unchanged construction dependency and complete first-helper/publication path. E011DM remains the original empty RS-query proof, E011DN the limited Windows ready snapshot, E011DI the separate factory/enumeration proof and E011DO the original initialized-registry reuse proof.

Selected input/profile deterministic startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. Zero camera Starts/reboots/kernel builds/production C changes; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DP cold bounds / guard](experiments/E004-front-ir-vd55g0/e011dp-original-cold-bounds-helper-guard/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11. Another oracle requires a fresh boot and atomic identity.

## 2026-10-04 E011DO original registry lock / initialized reuse accepted

The unchanged initializer executes its original default EnterCriticalSection/LeaveCriticalSection callbacks and complete already-initialized branch under explicit owned OS/diagnostic contracts. No callback or parent result fixture is used.

64 scenarios pass: 48 complete initialized reuse returns and 16 cold-prefix stops before 0x5DE800. All 6,848 original visits, 112 ABI-exact callback returns, whole mapped memory/permissions and stack checks pass; 2,512 invalid owned dependency requests reject. Nonzero bound fixtures do not prove registry construction. The accepted cold prefix retains its logical lock and active parent frame; cold field stores/allocation/publication are not accepted.

NEXT **E011DP** qualifies cold-bound construction and original first helper 0x5B80A8 (caller return 0x5DE844), plus resource readiness/construction ownership. Selected reader/request/profile, populated RS generation/lifetime and normal AFD input authority remain open. E011DM remains the original empty-RS-query proof, E011DN the limited Windows ready snapshot, and E011DI the separate factory/enumeration proof.

Deterministic selected-input/profile startup and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied. No new camera Start/reboot/kernel build/production C change; Golden boot, payloads, EFI/GRUB and historical repositories unchanged.

See [E011DO lock / reuse](experiments/E004-front-ir-vd55g0/e011do-original-registry-lock-reuse/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster works; SP11/SP7/PiMaster only. Windows oracle/external SP7 KD boots and tools remain authorized; originals/optical material stay private on SP11. Fresh boot and atomic identity for another oracle.

## 2026-10-03 E011DN Windows registry boundary observed

The accepted evidence is a 116-byte rear-reader-ready metadata snapshot before Start: bound/descriptor populated, seven runtime tag cells zero, and live platform callbacks equal the file default targets. Source references identify writer 0x5DE700; full initializer execution is still unqualified.

Two distinct atomic holder identities ran in one Windows boot, stopped/disposed successfully and counted 69 / 449 valid 4K handle acquisitions. A is excluded from RS qualification after observer command/filter issues. B captured only the registry snapshot; zero RS copy hits does not prove reader/query execution or general RS absence. No pixels were saved. This is not isolated-boot hardware or populated-record lifetime acceptance.

Golden return passed: payload hashes, permanent EFI/GRUB and historical repositories unchanged; Windows read-only recovery unmounted, temporary tasks removed, debuggers/holders closed. No production camera C/kernel change or Linux power-policy change.

NEXT **E011DO** qualifies original metadata registry initialization, allocation/descriptor ownership and the selected normal request/profile path before another fresh-boot oracle. E011DM remains the latest source empty-slot query proof, E011DI the separate factory/enumeration proof. Normal AFD input authority, deterministic startup/input/profile integration and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open; native rear runtime remains denied.

See [E011DN boundary](experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/README.md). Earlier current/NEXT paragraphs below are historical. PiMaster connects SP11 Linux/Windows and SP7; Windows oracle/external SP7 KD boots and missing tools are authorized. Originals and optical material stay private on SP11.

## 2026-10-03 E011DM original query through selected empty slots accepted

The original reader, metadata query and selected-slot helper now execute together without query or slot-helper result fixtures for declared empty slots. All 18,816 queries return actual null records; missing RS preserves the prior 132-byte source record.

640 scenarios / 1,920 cold/warm/stale-thread reader calls pass. Added query/helper coverage is 2,916,480 original instruction visits; inherited reader/tag/guard coverage is counted separately. All 356,608 altered dependency bindings reject in the owned harness contracts. Entire nonstack memory/mapping state, immutable source/pool/slot objects, preserved ABI and stack redzones pass.

The normal path selects node+490, uses pool capacity+278 and the inline pointer array+298, with selector modulo capacity. TLS block+138 is a scalar request selector; the original reader's ninth query stack argument is zero. Registry/settings/node/context/pool/empty-slot construction and standard OS resources remain explicit owned models.

**Still open:** actual selected registry values and metadata registry initialization, populated-record identity/generation/lifetime, normal AFD H/V counts and whole-frame zero-offset producer. Private populated-slot exploration reaches 5DF780 -> 5C0A58 and image+17350E0; it is excluded from acceptance. NEXT **E011DN** resolves that selected dependency and populated RS ownership, then normal AFD policy.

Selected input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Separate factory/enumeration acceptance stays E011DI; native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DM empty-slot query](experiments/E004-front-ir-vd55g0/e011dm-normal-rs-empty-slot-query/README.md). Earlier current/NEXT paragraphs below are historical. User authorizes Fabric or PiMaster, one-shot GRUB Windows oracle/external SP7 KD boots and missing-tool installation. Hosts SP11/SP7/PiMaster; originals and optical material stay private on SP11.

## 2026-10-03 E011DL original runtime statistics tag initialization accepted

The actual reader's guarded first-use path now produces all seven runtime tags from declared registry fields, including RS slot5, with no tag-vector or guard-result fixture. Unchanged CRT acquisition/publication bodies execute in the real reader caller. Warm and stale-thread calls preserve published tags despite altered registry inputs.

192 scenarios / 576 reader calls, 1,344 exact tag-field stores, 5,376 initializer-path instruction visits and 76,224 rejected dependency bindings pass. The 262,848 total original visits include inherited reader/guard coverage; this is bounded emulation, not camera hardware acceptance. Entire nonstack memory/mapping state and preserved ABI/stack redzones pass.

**Still owned models:** registry values/objects, settings, metadata-query results and OS SRW/CV resources. Actual query body, selected pool/record lifetime and normal AFD count/offset policy remain open. NEXT **E011DM** resolves those dependencies, reusing E011DK copy/decoder, E011AM arithmetic, E011M initial defaults and E011AK sampled unity binding.

Required input/profile integration, deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate. Latest selected RS source acceptance is E011DL; separate factory/enumeration acceptance stays E011DI. Native rear runtime remains denied. No camera Starts, reboots, kernel builds, optical tests or production C changes; Golden unchanged.

See [E011DL tag initialization](./experiments/E004-front-ir-vd55g0/e011dl-normal-rs-runtime-tag-initialization/README.md). Earlier NEXT/current statements below are historical. User reaffirmed autonomous one-shot Windows oracle/external SP7 KD boots and missing-tool installation on 2026-10-03; preserve Golden and same-SP11 private originals.

## 2026-10-03 E011DK RS metadata copy and C decoder accepted

The original RS metadata reader passes 96 present/absent/fallback cases and 39,904 instruction visits. The new checked C decoder reuses E011AM arithmetic, matches three observed records and 42 input/output fields per compiler, and rejects 21 invalid or unsupported inputs before output effects under GCC/Clang ASan/UBSan. All 132 copied bytes, owned heap changes, source immutability, original code, stack and caller state pass.

This closes the consumer/decoder contract only. Query/helper results, registry/settings/TLS/locks and runtime property tags are explicit owned fixtures. Actual tag initialization, metadata query/record publication and upstream AFD normal count policy remain open. Missing metadata preserves the prior source record; the decoder supplies no guessed defaults.

**NEXT E011DL:** follow RS tag cell 17A30F4, slot-5 query 5D4D30 and actual upstream normal count/offset publisher. Reuse E011M initial counts, E011AM numerical binding and E011AK sampled unity BG gain proof. Required selected input/profile integration, deterministic bootstrap/preflight and independent enabled-output DMA/IOMMU retirement still precede the clean-colour front/rear/off app gate.

Latest selected RS source acceptance is **E011DK**; the separate original factory/enumeration branch remains **E011DI**. Native rear runtime remains denied. Zero camera Starts, reboots, kernel builds or optical tests here; Golden unchanged. See [E011DK metadata input](experiments/E004-front-ir-vd55g0/e011dk-normal-rs-metadata-input/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 E011DJ input ledger accepted; E011DK normal RS policy next

The checked selected-baseline ledger covers all 14 register-state members, five DMI families and ten replay input blocks. It reuses 15 bounded proof facts, pins 55 authored files and rejects eight invalid ledger mutations. This is source/evidence inventory; no new numerical, emulation, optical or hardware test.

Initial Titan680 RS defaults, immediate AEC BG producer lineage and AWB pre-request seed/writer lineage are already proven. Normal RS count/override authority, selected normal input/profile bindings and independent enabled-output retirement remain open. NEXT **E011DK** follows the actual normal RS pre-adjustment writer upstream of A0DFC0; reuse E011AM arithmetic/binding and E011M initial defaults. Continue generic factory/registry work only for a named selected-baseline dependency.

Latest original emulation remains E011DI. Native rear runtime remains denied; Golden unchanged. See the checked [input ledger](experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/README.md). Earlier NEXT statements below are historical.

## 2026-10-03 evidence audit and next product gate

Latest accepted source checkpoint remains **E011DI**; native rear runtime remains denied. Earlier live front native ISP, front/rear RAW and ordinary-app/software fallback capture are retained. E011AM has zero-difference offline startup parity; E011AR is a compiled packet-isolated runner; E011AS/AV/BW supply specific cold policies. Complete deterministic startup and physical buffer retirement remain open.

**NEXT E011DJ first builds the selected-baseline input/dependency ledger**, reusing closed producers and identifying remaining normal RS count/whole-frame offset and other required normal-input authority. Continue the private registry/factory trace only for a named baseline consumer/lifetime dependency. Then integrate source-only preflight, independently prove IRQ/exact-buffer/DMA/IOMMU retirement, and target the existing eight-fresh-frame front/rear/off clean-colour app milestone. Optional effects/catalogue and protected IR/Hello remain deferred. Runtime/default promotion gates are unchanged.

Windows BF events were already live-observed in E005o; exact hardware retirement is still open. Older software-first, black-scene and historical NEXT paragraphs are snapshots, superseded by this audit for current priority. Report added coverage separately from inherited regression totals.

See [camera evidence audit](docs/CAMERA-STACK-AUDIT-2026-10-03.md) for evidence tiers, corrected status and acceptance gates.

## E011DI original enumeration bootstrap — BOUNDED PASS

Thirty-two cases continue the verified factory VM into original5F8DC0: combined15,936 original instructions,12,832 exact store chunks and3,488 rejected requests. Added enumeration proof contributes2,560 /1,024 /1,536.

Original stack helper1440 uses the actual112-byte initial frame and source5920-byte additional request under explicit already-committed stack bounds. Original CE7AD8 runs through second caller5F9460/guard1B30320, claimsFFFFFFFF and preserves its actual caller with balanced logical SRW ownership. Source code clears all56 bytes at169FE00. Whole memory/permissions/source reads/stores retain both48-byte records, typed owners and the1040-byte receiver.

The stop is BEFORE5F94A0→CA34A0 with callback argumentF7B5E0. Registry body/result, OS guard-page growth, file enumeration/completion/full parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/stack/native OS/allocator/canary fixtures remain explicit.

NEXT **E011DJ** follows original callback registry CA34A0/CA3450 and then enumeration completion/file provenance. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DI](experiments/E004-front-ir-vd55g0/e011di-original-enumeration-bootstrap/README.md).

## E011DH original factory initialization and1040-byte clear — BOUNDED PASS

Thirty-two cases across stack/node placements, loader indices, negative epochs and original/D7-canary field states execute13,376 original instructions,11,808 exact store chunks and1,952 invalid requests rejected before effects.

Original factory code clears190 image field chunks. Original F5E600 now executes through source call5BE9F8, zeros1040 bytes at incomingSP-1144 and returns destination to5BE9FC with its actual caller preserved. Its result fixture is absent. Whole mapped memory, actual permissions, exact scalar/vector/source writes and reads, both full48-byte records and logical SRW/allocation ownership pass.

The accepted stop is BEFORE5BE9FC→5F8DC0. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator/native OS models and D7 robustness fixtures are explicit. File enumeration, full factory completion/parent return/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DI** follows original file-enumeration routine5F8DC0 through its actual caller and source-created1040-byte stack record. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DH](experiments/E004-front-ir-vd55g0/e011dh-original-factory-initialization-clear/README.md).

## E011DG original factory two-record construction — BOUNDED PASS

Sixteen cases across four stack/node placements, two owned loader indices and two negative cold epochs execute1,712 original instructions,672 exact store chunks and816 invalid requests rejected before effects.

Actual factory guard caller checks remain intact. Original call instructions5BE698/5BE6CC request two48-byte allocations under typed owned success models; original source then constructs and publishes both full records, with three self-pointers, two-byte257 and22 zero bytes each. Whole mapped memory, actual permissions, source reads/stores, logical allocation/SRW ownership and actual guard caller preservation pass.

The accepted stop is BEFORE5BE6F4. Allocator/native OS bodies, failure cleanup, full factory parent return/completion/Default/startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Owned loader/TLS/cold file-BSS/negative epochs/stack/allocator fixtures are explicit.

NEXT **E011DH** follows original factory data initialization and library boundary, then file enumeration/context/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DG](experiments/E004-front-ir-vd55g0/e011dg-original-factory-two-records/README.md).

## E011DF original factory cold prefix and actual startup guard caller — BOUNDED PASS

Sixteen cases across four stack placements, two owned loader indices and two negative cold epochs execute 1,344 original instructions, 352 exact store chunks and 640 invalid requests rejected before effects.

Original factory5BDE08 now calls original CE7AD8 at5BE67C with actual guard1B302D0; it returns to5BE680 with actual guard caller SP/nonvolatile registers preserved and balanced logical SRW ownership. Original code changes the guard0→FFFFFFFF and clears three factory initialization fields. Whole mapped memory, actual permissions, exact source reads and independent store models pass.

Each case stops BEFORE allocator call5BE698→CAE740 requesting48 bytes: 84 instructions executed, with the stop call excluded. Owned loader/TLS/negative epochs/file-BSS state/native OS models remain explicit. Full factory parent return, allocation/construction/completion, Default/full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open.

NEXT **E011DG** qualifies the exact48-byte allocation boundary and original factory construction, then context/file enumeration/RootOpsinput+72/Default. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DF](experiments/E004-front-ir-vd55g0/e011df-original-factory-guard-prefix/README.md).

## E011DE original standalone startup-guard sequence — BOUNDED PASS

Sixteen scenarios cover four placements, two owned loader indices and two epochs across fresh initialization, completion and cache refresh. All48 original helper phases pass: 1,504 instructions, 304 exact store chunks and 1,168 invalid requests rejected before effects.

Original CE7AD8 claims first initialization with guardFFFFFFFF. Original CE7A48 increments epoch1607B04 and updates the guard/TLS+16; the original initialized path refreshes a stale TLS epoch. Whole memory, actual permissions, logical SRW resource order and original caller SP/nonvolatile registers pass.

Loader/TEB/TLS/SRW/CV readiness and void OS dependencies remain explicit owned models. Native OS bodies/bytes, concurrent waiting and actual factory/Default production remain open. This standalone proof is not yet joined to factory5BDE08 and its source guard1B302D0.

NEXT **E011DF** joins the original runtime guard to its exact factory caller, then resolves file enumeration/context receiver/RootOpsinput+72 and full startup/preflight/RS. Independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical remain open. Golden/history unchanged; zero Starts/reboots/images/production C or kernel changes. See [E011DE](experiments/E004-front-ir-vd55g0/e011de-original-startup-guard-sequence/README.md).

## E011DD original root reference-release component — BOUNDED PASS

Sixteen isolated cases at four placements cover null roots and references1/2/41. Twelve first execute original fresh-root construction. The source release branch decrements references, retains nonfinal roots and calls the typed OS root+8 deletion and sized176-byte release only for the final reference, then clears global1798458.

Combined construction/release: 2,004 original instructions, 616 exact store chunks and 464 invalid requests rejected before effects. Whole memory, actual permissions, logical resource order and paused register restoration pass. Held-lock and competing-user states also reject before effects.

This is the interior source component290988..2909D4, not a full parent destructor or parent ABI return. Native OS/allocator bodies, concurrent retry, failure cleanup, live caller ownership and hardware retirement remain open. No cleanup is appended to retained E011DC camera outputs.

Provider input+48 and RootOps candidate input+72 are distinct. Context+9552 is not established as the registered camera callback. Cold factory startup reaches an unqualified runtime helperCE7AD8 at5BE67C under guard1B302D0; actual Default/factory/context receiver production remains open.

NEXT **E011DE** resolves that source runtime/factory/Default consumer, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DD](experiments/E004-front-ir-vd55g0/e011dd-original-root-reference-release/README.md).

## E011DC original fresh-root construction and registered camera join — BOUNDED PASS

Four isolated placements and six ANSI/OEM camera joins execute the fresh-null-root registration path: 1,530 original instructions, 500 exact store chunks and 170 invalid requests rejected before effects. Original code zeros all 176 bytes, copies the private 12-byte NUL-terminated name into root+48, calls the typed OS initializer on root+8, publishes the root at 1798458 and increments its reference to one.

The 48-byte callback record still supplies camera entry through slot 32. Independent whole memory, permission, resource and actual caller models pass; the complete source-created root, added table/stack/API regions, output/global/inner link and SAME balanced root lock survive the camera outer return. The inherited malloc adapter delegates this exact source call to the strict owned 176-byte model; all other parent observers remain enabled.

Return clarification: E011DB's existing-root path retains the input record pointer in X0. The fresh path retains a residual X0 from the void OS initializer, tested with four distinct owned values. Neither establishes a general registration status or defined record return. The name-copy helper itself returns zero on this checked success path.

Allocation and native OS critical-section bytes/concurrency remain explicit typed models. Source failure/cleanup, actual Default provider and full Windows startup/preflight/RS remain open. The provider+0x162e90 table is a derived static candidate, not complete provider execution authority.

NEXT **E011DD** follows original provider/Default consumers and registered root lifecycle, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DC](experiments/E004-front-ir-vd55g0/e011dc-original-fresh-root-camera-join/README.md).

## E011DB original callback registration and registered camera entry — BOUNDED PASS

Twelve isolated cases cover four aligned placements and owned root reference counts 0/1/41. Six ANSI/OEM camera joins across three pinned private inputs now enter 36CBA0 through slot 32 of the 48-byte callback record produced by original 36E9C8. The caller no longer chooses a fixed entry address.

All 18 original registration returns execute 810 unchanged instructions and 234 exact store chunks. Independent complete-record/entire-memory models check size 48, slots 16/32/40, preserved reserved bytes and the original root+0 reference increment. All 126 invalid requests reject before effects. Original X0 returns the input record pointer, not a status code; actual SP/X19–X29/D8–D15 and the complete paused caller restore.

The entire added table region, initializer stack, root record and actual permissions remain unchanged after registration through the camera outer return. Inherited runtime-helper, caller, output/global/inner-link and SAME balanced-root-lock checks pass. The file-image control globals 0/1/0, owned nonnull root, placements and component ordering remain explicit fixtures; fresh 176-byte root construction, other registered-slot bodies, actual Default input production and full Windows startup remain open.

Original ARM64 exception metadata identifies 36CBA0 as 6152 bytes (the older 6160-byte source window was wider), registration 36E9C8 as 448 bytes and provider 2BC618 as 2128 bytes. Internal source call 2BC71C registers this record. The provider's complete execution and descriptor construction are not inferred from that static reference.

NEXT **E011DC** follows the fresh-root allocator/initializer/OS/name-helper ownership and provider/Default input lineage, then full startup/preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DB](experiments/E004-front-ir-vd55g0/e011db-original-callback-registration-join/README.md).

## E011DA original runtime helpers in the camera join — BOUNDED PASS

All six ANSI/OEM cases across three pinned private inputs execute original CE7C98 reverse byte search inside the camera harness. Its basename result fixture is removed: 300 source calls / 77,992 original instructions use exact source callers, private literal hashes, search byte 92 and last-backslash results. Every call preserves all mapped memory, permissions, resource state and actual callee-saved registers.

The fresh TLS flag starts at 0. Original CFE600 -> CFE560 produces block+20=1 before camera startup in 204 instructions and 36 exact store chunks. Independent entire memory models permit only source stack stores and that flag byte; the original callee and complete paused caller restore. All 1,542 invalid helper requests are rejected before effects. The dedicated initializer stack stays unchanged throughout the camera join.

Inherited publication and outer-return models still match. Output/global retain the actual outer, outer+40 retains the actual inner, actual incoming SP/X19–X29/D8–D15 restore and the SAME root mutex balances one Enter/one Leave. Publication now counts 5,388 executed OEM instructions / 36 retained adapters; the tail counts 4,872 / 84. Other library/diagnostic/cookie fixtures remain explicit.

TLS loader index 0, TEB/array layout, file-image null initializer table, owned stack and component ordering remain declared fixtures. Parent harness observers pause only for the separately guarded TLS emulator component and resume in finally; exact original instructions, reads, stores and whole memory remain independently checked. Actual Windows loader initialization, nonempty callback lists, full runtime CFE600, Default/CRT/locale/concurrency and hardware readiness remain open.

NEXT **E011DB** addresses remaining Default and full-startup provenance, then preflight/RS and independent WM16 IRQ/exact consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/production C or kernel changes. See [E011DA](experiments/E004-front-ir-vd55g0/e011da-original-runtime-helper-camera-join/README.md).

## E011CZ original runtime helper authority — BOUNDED PASS

Original CE7C98 is reverse byte search used by18 source callers on eight private source-path literals, not a TLS/context getter. Its inherited owned_diagnostic_context label and TLS+3000 result fixture are corrected in scope; the camera harness still retains the fixture pending E011DA.

Seventy-two original reverse-search returns (64 owned placement/search cases and8 actual private image literals) match independent last-match/NUL/NULL results in4,601 original instructions. The source-derived aligned16-byte SIMD read windows and every canary remain unchanged. Thirty-two original CFE600 -> CFE560 returns cover four owned placements/four PE TLS-index fixtures/fresh and initialized flags:928 instructions/176 store chunks independently produce block+20=1 when fresh, with actual SP/X19–X29/D8–D15 restoration and whole memory checks. All584 invalid scope requests are rejected before effects.

PE TLS AddressOfIndex matches source global16A3740. The callback table is pinned null file-image data; this is bounded empty-initializer-table proof under declared loader/TEB/array fixtures. Full actual Windows loader, nonempty initializer callbacks, Default/CRT/TLS/locale/concurrency and runtime CFE600 authority remain open. Original helpers are not yet integrated into the camera harness.

NEXT **E011DA** performs that shared camera join and rechecks whole memory, caller restoration, output/global retention and balanced locks across six source cases; then remaining full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero Starts/reboots/Linux images/C/kernel changes. See [E011CZ](experiments/E004-front-ir-vd55g0/e011cz-original-runtime-helpers/README.md).

## E011CY original publication callback and outer return — BOUNDED PASS

Six ANSI/OEM camera joins across three pinned inputs recheck the accepted publication prefix and execute the original publication callback36E670 through outer return36E394. The tail checks 3,360 executed OEM instructions plus90 explicit inherited adapter entries, 666 exact store chunks, 2,592 separately contracted owned library-clear bytes and450 invalid requests rejected before effects.

Independent entire stack/camera/caller models match; every other full inherited region, real permissions, allocation/release history and CRT resource state stays unchanged. W0 returns0; actual incoming SP, X19–X29 and D8–D15 restore. Output/global retain the actual outer object and outer+40 the actual inner. The SAME parent camera-root mutex closure records one Enter/one Leave with final depth0 at original return36E2B4.

The exact outer cookie producer11D0/checker11F0 pair now executes unchanged (36/48 instructions across six cases), with its entire producer-stack delta and caller restoration checked. Other nested cookie helpers and the clear-helper implementation remain explicit fixtures. Added owned TEB+88 linkage and the restored existing parent Leave binding are declared ABI fixtures before the tail baseline; actual Windows loader/Default/CFE600/TLS/FLS/locale/concurrency remain open.

NEXT **E011CZ** source-qualifies original TLS/context and runtime bootstrap authority, then full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. Golden/history unchanged; zero new Starts/reboots/Linux images or production C/kernel changes. See [E011CY](experiments/E004-front-ir-vd55g0/e011cy-original-outer-return/README.md).

## E011CX original output and global publication — BOUNDED PASS

Six cases cover both ANSI/OEM fixtures across three pinned inputs. After accepted file/thread cleanup, the remaining parameter iterations run through the unchanged interface96 and core-vtable16 callbacks. Original code links outer+40 to the actual inner object and publishes the same outer object to the caller output and image global1798460.

The verifier checks 2,316 executed OEM instructions and 114 original Windows getter instructions, with 48 explicitly inherited diagnostic/CFG adapter entries counted separately. All 384 store chunks match pre-instruction/source-field models; 150 invalid callback/getter requests are rejected before effects. Independent entire stack, camera, caller and image models match, all other complete regions stay unchanged, actual permissions and allocation/lock state match, and the retired Unicode owner is never read.

The accepted stop is before guard36E178 and original outer field16 callback36E670. The camera root mutex remains held; complete outer return and full Windows loader/Default/CRT/TLS/locale/concurrency remain unqualified. The observer's initial X26 assertion now applies only to the first parameter-loop visit; subsequent visits use the original saved output at SP+96. No original code bytes change and original CFE600 remains guarded.

NEXT **E011CY** qualifies the publication callback, whole outer return and balanced camera lock with independent models and exact incoming caller checks. Separate private exploration reaches a return under extended owned ABI fixtures, but is excluded from acceptance. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate smoke testing. Golden/history unchanged; zero new Starts/reboots/Linux images. See [E011CX](experiments/E004-front-ir-vd55g0/e011cx-original-output-publication/README.md).

## E011CW original file-error thread join and cleanup — BOUNDED PASS

Six original camera joins cover both ANSI/OEM fixtures across three pinned inputs. The unchanged slot/thread initializer runs in the same Native instance and CRT owner, with a separate owned stack and preserved paused caller. Its 2,406 OEM/258 OS instructions pass the inherited whole-memory models and 396 invalid API requests. The slot and entire 968-byte thread owner are source-produced.

The exact measured read-only file failure feeds 1,566 original cleanup instructions, 342 original Windows getter instructions and 234 exact stores; 186 invalid cleanup API requests are rejected before effects. Original thread fields receive OS error3 at+36 and CRT error2 at+32. The original path clears descriptor/stream flags, releases the74-byte Unicode owner and both held descriptor/stream locks, with no later source read of the retired Unicode owner.

Independent entire stack/CRT models and all other entire image, camera, serialized, native-heap, TEB/FLS and OS regions match; real permissions match. Public output stayszero. The bounded stop is CED194 after stream-lock release. Initializer ordering, TEB, file-image/null locale/diagnostic globals and logical OS resource adapters remain explicit fixtures; actual full Windows loader/startup/concurrency and original CFE600 remain open.

NEXT **E011CX** continues after CED194 through existing typed diagnostic ownership, remaining configuration/publication, whole outer return and balanced camera locks. Reuse only the already source-classified16A4230 diagnostic contract; no generic logger or numeric/TLS success substitute. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate smoke testing. Golden/history unchanged; zero new Starts/reboots/Linux images. See [E011CW](experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/README.md).

## E011CV original CRT slot and thread record — BOUNDED PASS

Four owned allocation placements and fresh slots pass 1,684 unchanged OEM instructions, 165 original Windows getter/setter instructions, 307 exact store chunks and 264 invalid API requests rejected before effects. Bounded API-set parsing and the exact host export/NTDLL forwarder agree. Original CB4338 publishes the allocated slot; the original producer allocates and initializes the entire 968-byte thread record.

Independent entire image, stack, CRT, TEB and FLS byte-layout models match. All other entire regions and actual permissions match, original callee-saved registers/SP restore and locks balance. The original Windows getter retrieves the exact published owner; the original error setter restores the input error after an explicit owned API clobber.

This is standalone guarded Unicorn evidence under a fresh single-thread registry, file-image/null locale and zero diagnostic-global fixtures. FlsAlloc/FlsSetValue use strict owned adapters; their original Windows implementations, actual live loader/TLS/locale/concurrency, callback cleanup and the camera join are open. Original CFE600 remains unqualified. NEXT **E011CW** joins this producer to the original file-error path, then qualifies error mapping, descriptor/Unicode release and full outer return. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical still gate the smoke test. Golden/history unchanged; zero new camera Starts, reboots or Linux image tests. See [E011CV](experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/README.md).

## E011CU original measured file-failure path — BOUNDED PASS

Six unchanged original camera joins cover both ANSI/OEM fixtures across three pinned inputs, first placement only. Strict external contracts use the actual E011CT read-only file failure and thread error3, bound to the exact filename digest, seven ABI inputs, SECURITY_ATTRIBUTES, source return sites and call sequence. All432 original failure-prefix instructions,96 exact store chunks and60 invalid API requests pass full memory/state checks.

Original CFD6F0 clears descriptor0 record+56. Its invalid handle and initialized mutex remain held; the owned74-byte Unicode allocation is retained. Independent entire64KB stack and CRT models permit only original stack stores and that one flag clear. Entire other image/native-heap/camera/serialized/API regions and policy pages/permissions match; all lock depths and allocation ownership remain unchanged. The original thread-context helper reaches the stop before FlsSetValue atCBA198, with source CRT slot1607168 stillFFFFFFFF and a -1 busy marker. No FLS call/result is supplied, and original CFE600 remains unqualified.

NEXT **E011CV** source-only: original slot initializer CB4310/dynamic module-export resolution and fresh owned FLS registry, then original per-thread object producer/error mapping, descriptor/Unicode cleanup and full outer return. Actual live Default/full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/history unchanged; zero new Start/reboot/C/kernel/image tests in this source phase. See [E011CU](experiments/E004-front-ir-vd55g0/e011cu-original-file-error-boundary/README.md).

## E011CT actual Windows file/error input — BOUNDED PASS

The fresh E011CT-OS-002 observer made one native standard ARM64 CreateFileW call with the source-verified private filename and all seven read-only ABI inputs. It returned an invalid handle; the managed capture, Kernel32 and NTDLL thread-error getters all reported3, with NTSTATUS0xC000003A. An independent known-value last-error round trip agreed. The private4096-byte shared OS page and NTDLL initialization cell were observed on SP11; the cell matched before/after. No file content was read or created, and no proprietary OEM camera DLL, camera Start, stream or optical API was invoked.

The runner preserved the existing EFI mount and returned normally to Golden boot e5f58539-ac31-427d-a718-f1970684107b. All three Golden payload hashes, persistent boot order, saved GRUB, empty next entries, idle camera and both historical checkouts match. Private evidence is archived on SP11; ESP inputs/scripts/snapshots are retired, retaining consumed markers. The earlier mount rejection is a preserved consumed abort, with no target API call.

NEXT **E011CU** source-only: bind this measured failure to the exact original caller/input contract, qualify original error/TLS/descriptor/UTF16 cleanup, then final publication/full outer return and balanced locks. Actual live Default production and full CRT/startup are still open. Native rear remains denied pending full startup/preflight/RS and independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical. This is an OS-dependency observation, with zero new Linux camera images. See [E011CT result](experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/RESULT.json) and [next source](experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/NEXT-SOURCE.json).

## E011CT Windows file-API observation — FRESH ATTEMPT 002 PREPARED, UNARMED

Attempt E011CT-OS-001 is consumed and aborted before the observer or target API. Windows rejected the temporary mount command; read-only topology showed the existing EFI mount at Z:. The runner returned normally to new Golden boot f6b17d2b-4a76-4ab1-a748-35fcd9ee17c4, with all three payload hashes, persistent boot order and historical checkouts preserved. No camera Start, file API or shared-page observation ran. Its private input/scripts were archived on SP11 and retired from ESP; consumed evidence remains.

Fresh E011CT-OS-002 verifies the existing EFI partition GUID/type/size, uses and preserves its current mount, and removes only a mount it creates. The observer additionally requires loaded ARM64 NTDLL. Both PowerShell sources parse and the independent C# compiles on SP7 without private inputs or target calls. Publish exact prepared source, then a single guarded direct-Windows BootNext0006 observation with the owned600-second return timer and normal15-second Golden return. E011CS remains the accepted source proof; complete original startup/Default producer/cleanup and hardware gates remain open, with native rear denied. See [fresh plan](experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/attempt-002/PLAN.json) and [consumed abort](experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/ATTEMPT-001-ABORT-SAFE.json).

## E011CT Windows file-API observation — PREPARED, UNARMED

E011CS remains the accepted source checkpoint. Its next dependency now requires a bounded same-SP11 Windows observation: one standard CreateFileW call with the verified private filename/read-only ABI, immediate observer-thread Win32/NT status, and a private4096-byte shared OS-page snapshot. No camera API or proprietary OEM DLL is invoked by this observer. Default filename production and full CRT/startup remain open.

The independently written C# compiles on SP7 with exact24-byte Win64 SECURITY_ATTRIBUTES/offsets8/16; both final PowerShell scripts parse. No SP11 private input was transferred to SP7, and preflight invokes no target file/shared-page API. Atomic CreateNew marks the fresh E011CT-OS-001 before the target call. The Windows runner arms its own600-second reboot watchdog, removes its temporary ESP mount and requests normal Golden return after15seconds.

Next publish/verify this exact prepared source and private same-SP11 inert ESP handoff, then use existing direct-Windows BootNext0006 once. Preserve persistent Linux-first BootOrder and GRUBsavedGolden; verify a new Golden boot and emptynext entries, archive/retire evidence, then qualify original OS/result/error/CRT cleanup. Native rear stays denied pending full startup/preflight/RS and independent enabledWM16IRQ/consumedIOVA/DMA/IOMMUretirement/optical. See [E011CT plan](experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/PLAN.json).

## E011CS original file-opening boundary — BOUNDED PASS

Six unchanged original camera startup joins cover both ANSI/OEM fixtures across three pinned inputs, first camera placement only. After the inherited complete Unicode conversion, original CRT mode parsing and descriptor allocation reach the stop before CreateFileW at0xCFD658. No file API executes and no handle/error result is supplied.

All1098 original preparation instructions,282 exact store chunks and48 lock-contract negatives pass. Independent entire64KB stack and CRT-arena models permit only stack stores plus descriptor0 record+56=1/+40=INVALID_HANDLE_VALUE. Other entire image/native-heap/camera/serialized regions and policy pages/permissions match. GlobalCRTindex7 enters/leaves balance; the initialized descriptor0 lock remains held. The owned74-byte UTF16 allocation is unchanged/retained; output remainszero and camera/new-stream locks remainheld.

All seven file-call arguments and the entire24-byte SECURITY_ATTRIBUTES match: read access, share-read, owned absolute drive-C path, null security descriptor, inherit1, OPEN_EXISTING, normal attributes, null template. This proves preparation in explicit owned fixtures, not actual Windows filesystem/default filename/last-error/TLS/concurrency or file success/failure. Earlier wider/isolated source evidence remains historical. Original numeric/TLS/policy/Unicode instructions are unchanged; CFE600 still raises.

NEXT **E011CT**: qualify file API/result/error ownership, then descriptor/UTF16 cleanup, final publication/full outer return/balanced locks. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/historical checkouts unchanged; zero Starts/reboots/deployments/C/kernel/image tests. Clean controllable front/back first; AI/effects/HDR/catalogue deferred. See [E011CS](experiments/E004-front-ir-vd55g0/e011cs-original-file-opening-boundary/README.md).

## E011CR original Unicode conversion — BOUNDED PASS

Seventy-six original Windows conversion API returns and NTDLL entries pass in guarded Unicorn fixtures. Sixty-four isolated size/output cases cover eight ASCII lengths, two input alignments and both ANSI/OEM codepage aliases. Six original camera joins cover both policies across three pinned tuning inputs, first camera placement only. The unchanged CRT converter returns to0xCFD4E8 with status0 in all six.

Each camera path queries37 UTF-16 code units including NUL, requests74 bytes through original malloc and a strict owned HeapAlloc contract, then converts into that allocation. Original source stores the owned pointer and code-unit extent at caller record+16/+24. Independent entire32-byte result-record,64KB stack and CRT-arena models match; callee-saved registers restore. Other entire regions/pages/permissions match, output remainszero and camera/new-stream locks remainheld. All4980 integrated OS instructions,426 OS stores,450 following CRT instructions,54 following CRT stores and30 new scope/heap negatives pass.

The API/NTDLL routines execute unchanged only inside Unicorn. ANSI/OEM defaults65001 are copied from the file image, virtual caches are explicit zero fixtures, and the security cookie is the file-image seed. This qualifies ASCII conversion in that fixture, not live Windows default codepages/locale/cookie/loader initialization, general Unicode/error paths, native DLL execution or real heap/concurrency semantics. No size/conversion/numeric/TLS/policy success stub or new logger admission; original CFE600 remains unqualified and raises.

NEXT **E011CS**: follow the caller after0xCFD4E8 through remaining CRT/file-opening/cleanup, qualify dependencies and ownership, then final publication/whole outer return/balanced release. Full startup/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. Golden/historical checkouts unchanged; zero camera Starts/reboots/deployments/C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CR](experiments/E004-front-ir-vd55g0/e011cr-original-unicode-conversion/README.md).

## E011CQ original conversion-query boundary — BOUNDED PASS

Six original camera startup joins cover both explicit ANSI/OEM policies across three pinned tuning inputs, at the first camera placement. The unchanged CRT branches call converter0xCB76B0 and reach the Unicode size-query tail at0xCB8DD4. ANSI selects codepage0; OEM selects1. Original arguments are flags9, W3=-1, a NUL-terminated owned-stack filename, null output and capacity0. Execution stops before the tail branch into the conversion API; no conversion result is supplied.

All48 exact saved-register qword stores match independent entire64KB stack models. Entire OEM image, native/CRT/camera arenas, serialized input and caller fixtures remain unchanged. The filename and zero result record remain unchanged; no allocation or lock-depth change occurs. Thirty-six scope negatives reject without state delta. Inherited prefixes retain90 exact statistics records,720 statistics initializers,146 core initializers and270 GetTag lookups. Output remainszero; camera/new-stream locks remainheld.

NEXT **E011CR**: qualify the conversion dependency and explicit codepage/locale/size-result ownership before admitting any conversion result, allocator or later file-opening continuation. Full CRT/final publication/whole outer return/balanced release, original TLS CFE600 and full startup/preflight/RS remain open. Independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied. No numeric/TLS/policy/conversion success stub or new logger admission.

Golden hashes and historical checkouts are unchanged. Zero camera Starts/reboots/deployments/production C/kernel/image tests. Original OS policy code remains inherited Unicorn-only evidence; no native Windows DLL execution. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CQ](experiments/E004-front-ir-vd55g0/e011cq-original-conversion-query/README.md).

## E011CP original file-encoding policy and wrapper — BOUNDED PASS

Fourteen original OS policy-setter, query and OEM wrapper returns pass in guarded owned memory: seven ANSI results1 and seven OEM results0. Four isolated cold/cached pairs flip the source-produced policy without reloading the cached API pointer. Six original camera0x36CBA0 joins cover both explicit policy states across three pinned tuning inputs, one camera placement each.

The requested export branches through an original import thunk into the dependency's original28-byte query. Original68-byte setters produce four policy fields each; no BOOL success substitute is used. All56 exact policy stores,392 original OS instructions,12 original consumer instructions,60 OS ownership rejections and30 policy-scope rejections pass. Entire owned pages and real permissions, OEM image, CRT/native heap/stack and camera-object guards match. Relocation/linking and uncalled conversion-pointer identities remain explicit owned fixtures, not actual Windows default policy/loader/NTDLL conversion/concurrency proof.

All six camera wrappers return to0xCFD49C. The unchanged caller reads one byte at SP+48 and branches on nonzero W0: ANSI stops before0xCFD4C0, OEM before0xCFD4A4. The source caller byte is0 in these six cases. Ninety exact statistics records,720 statistics initializers,146 core initializers and270 total GetTag lookups remain checked. Output remainszero; camera/new-stream locks remainheld; ten resolver lock pairs balance. CN/CO wider placement evidence remains historical, not rerun across this new consumer boundary.

NEXT **E011CQ**: follow those selected CRT/file-opening branches, qualify receivers/stores/dependencies, then final publication/whole outer return/balanced release. Actual conversion/codepage/locale/full CRT and original TLS CFE600 remain open. No numeric/TLS/policy success stub or new logger admission. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Original OS routines execute only inside Unicorn on SP11; no native Windows DLL call. Golden hashes and historical checkouts unchanged; zero camera Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CP](experiments/E004-front-ir-vd55g0/e011cp-original-file-encoding-policy/README.md).

## E011CO original dynamic module/API resolution — BOUNDED PASS

Seven complete original 0xCB9B88 resolver returns pass, including three original camera 0x36CBA0 joins across three pinned tuning inputs (one placement per source). Four isolated cold/cached pairs cover four opaque-handle placements. Source-selected module/API names match a SHA-pinned same-SP11 Windows PE export catalog; the selected file-encoding policy export is present, ordinal38/RVA0x70A90, not forwarded.

All 22 exact image stores,14 real Unicorn page-protection changes,seven balanced initialized CRT index14 lock pairs and42 rejected ownership requests pass. Independent whole mapped-image/CRT/native-heap/resolver-arena models match. Cached continuations perform no loader/export/protection/lock calls or stores. The cache PE section is initially writable in the source metadata; source explicitly ends it read-only. Initial writable/read-only states and opaque OS handles/adapters remain explicit owned fixtures, not live Windows loader/init/cookie/lifetime/concurrency proof.

Three fresh camera-source joins retain45 exact statistics records,360 statistics initializers,73 core initializers and135 total GetTag lookups. The camera arena/inner/outer are unchanged after CN; public output remainszero and camera/new-stream locks remainheld. CN's prior four-placement integration remains historical accepted evidence; CO integrates one placement per source.

NEXT **E011CP**: qualify the file-encoding policy API/consumer and original wrapper return, then remaining CRT/final publication/whole outer return/balanced release. Accepted execution stops at an owned API adapter before any adapter instruction or policy result. No guessed-success numeric/TLS/policy substitute or new logger admission; CFE600 still raises. Full startup/preflight/RS and independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts unchanged; zero Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CO](experiments/E004-front-ir-vd55g0/e011co-original-api-resolver/README.md).

## E011CN original CRT integration into camera startup — BOUNDED PASS

The original camera entry 0x36CBA0 with source-produced CRT objects reaches the stop before 0xCB9C10 in 12 unmodified source/placement cases across three pinned inputs. Twelve complete original 0xCC6078 stream-allocator returns pass with independently modeled entire 88-byte streams. The return is an 8-byte argument0 pointer record, not a direct stream pointer; its two stores and adjacent stack bytes are exact.

All 96 CRT owned-store chunks and six first-use image stores match. Independent entire CRT arena/image and unchanged camera-arena/inner/outer checks pass. The CRT global index8 lock is released; the newly allocated stream and camera outer locks remain held at this bounded stop. Inherited 180 statistics records, 1440 statistics initializers, 292 core initializers and 540 total GetTag lookups pass. The three four-entry CRT bootstraps also pass; their execution order and OS heap/single-thread lock contracts remain explicit owned fixtures.

NEXT **E011CO**: qualify original dynamic DLL-loader/module/API ownership. Accepted execution stops before the LoadLibraryExW import at 0xCB9C10 / IAT 0xF7E310. Complete CRT/loader environment, original TLS 0xCFE600, actual OS locale/standard handles, final publication, whole return and balanced stream/camera lock release remain open. No guessed-success loader/numeric/TLS substitute or new logger admission. Full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts unchanged; zero Starts/reboots/production C/kernel/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CN](experiments/E004-front-ir-vd55g0/e011cn-crt-startup-integration/README.md).

## E011CM original CRT object producers — BOUNDED PASS

Four unchanged original CRT routines return across eight owned cases: four placements, default count 512 and explicit preset count 128. Independent whole mapped-image/arena models pass for 512 entire 72-byte indexed records, 24 entire 88-byte static stream objects and eight full pointer vectors. All 180 source image stores, 656 logical OS mutex initializations and 16 guarded allocations match. Eight existing-table lookups allocate/initialize nothing and balance their locks; 24 invalid OS ownership requests are rejected.

Correction: global 0x16A2A50 is a 32-bit count, 0x16A2A58 a pointer vector, and 0x16A2A90 an indexed table. Their original producers return under explicit owned heap and logical single-thread OS contracts. The original global mutex initializer includes 0x16A3000. These contracts do not prove Windows mutex bytes, concurrency, actual standard handles, locale or full CRT/loader initialization.

NEXT **E011CN**: integrate exact original producers into owned outer-entry, qualify runtime CRT deltas/lock ownership, then final output publication, whole outer return and balanced release. This isolated CRT matrix does not extend E011CL's accepted camera-entry prefix. Original TLS 0xCFE600 stays unqualified and raises; no numeric/TLS success substitute or new logger admission. Full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical keep native rear denied.

Golden boot/payload hashes and both historical checkouts are unchanged. Zero camera Starts/reboots/production C/kernel changes/image tests. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CM](experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/README.md).

## E011CL original conditional source context — BOUNDED PASS

Original entry `0x36CBA0` reaches the stop before `0x36DE04` in 24 cases: 12 unmodified and 12 explicit owned destination-poison fixtures across three pinned sources and four placements. The new 428-byte conditional portion executes unchanged original instructions. Serialized scene-change bank flags, values and names independently select record 1; source counts are 3/3/4, with guarded arrays of 528/528/704 bytes and 176-byte records. Exact comparison arguments and three context read origins pass.

All 144 original stores match the six predicted inner fields. Independent whole 606264-byte inner and whole-arena comparisons admit no other changes or new conditional allocations/releases. Inherited 360 records, 2880 statistics initializers, 584 core initializers and 1080 total GetTag lookups pass with caller/TLS, image, native heap, serialized source and allocation guards. Statistics+40 and mode+91952 remain attached; outer unchanged, output zero and owned single-thread lock held.

NEXT **E011CM**: qualify original CRT initialization/global/locale/OS ownership before final public output, whole return and balanced lock release. A static scan identifies candidate `0xCB3260` writing globals `0x16A2A50/58`; its execution, source objects and OS contract remain unqualified. Alternate context branches, full bank/metering-name producers, child payload semantics and live Default/filename/reuse/destruction remain open. No guessed locale, null-page mapping or numeric/TLS success substitute is admitted.

Golden boot and all three payload hashes, plus both historical checkouts, are unchanged. Zero camera Starts/reboots/C/kernel/image tests. Native rear runtime remains denied pending full bootstrap/preflight/RS and independently enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical gates. Clean controllable front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CL](experiments/E004-front-ir-vd55g0/e011cl-conditional-source-context/README.md).

## E011CK original source objects and module binding — BOUNDED PASS

Original36CBA0 entry through stop before36DC58 passes24 cases:12 unmodified+12 owned scalar poison fixtures. Independent entire606264-byte inner and complete1088/120 primary object models verify original attachments at inner+16/+24,408 exact inner stores/408 guarded allocations.48 actual aecxface/aecxmetering returns match core cache26/31;72 original accessors/72 original helper returns/24 original strcmp equal returns pass. F5DF00 is comparison, not memcpy. Inherited360 records/2880 statistics initializers/584 core initializers/1080 total GetTag lookups and whole-memory guards pass. Statistics+40/mode+91952 retained to stop; outer unchanged/output zero/lock held. Full child semantics/reuse/live Default producers remain open.

NEXT **E011CL**: conditional source context fields after36DC58, then CRT OS/global/locale ownership before final publication/whole return/balanced lock release. First-source36DE04 context and earlier second-CRT-lock/null-global reads remain excluded; no guessed locale/null mapping/numeric/TLS success substitute. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel/image tests. Native rear DENIED pending full bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CK](experiments/E004-front-ir-vd55g0/e011ck-source-object-and-module-binding/README.md).

## E011CJ original post-attachment baseline reset — BOUNDED PASS

Original entry36CBA0 through stop before36D784 passes24 cases:12 unmodified and12 explicit owned poison fixtures across3 sources/four placements. Independent entire606264-byte inner and full-arena deltas verify72 original clears/1224 scalar store chunks and the internal inner+91816 -> inner+92976 link. Statistics+40 and mode+91952 attachments are retained to this stop; outer unchanged/output zero/lock held. Inherited360 records/2880 statistics initializers/584 core initializers/1032 cache lookups and whole-memory guards pass. Poison checks validate resets, not real object reuse or live Default producers.

NEXT **E011CK**: additional original object/module/context/cache producers after36D784, then CRT ownership/environment before final publication/whole return/balanced lock release. Excluded CRT exploration identifies null image globals16A2A58/16A2A50 before CC6140 reads address24; second CRT-lock fixture remains excluded, no guessed locale/null mapping. Actual live Default/filename/destruction/reuse and full optional semantics remain open. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel/image tests. Native rear DENIED pending full bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back first; optional AI/effects/HDR/catalogue deferred. See [E011CJ](experiments/E004-front-ir-vd55g0/e011cj-baseline-state-reset/README.md).

## E011CI original statistics and mode configuration attachment — BOUNDED PASS

Original `0x36CBA0` entry through the stop before `0x36D63C` passes 12 cases. The1664-byte statistics manager is attached at inner+40; the separately source-allocated96-byte configuration object is attached at inner+91952. An independent entire606264-byte inner delta allows only those two qword writes after the E011CH prefix; the72-byte outer is unchanged and public output still zero. Complete224-byte395940 returns with its actual96-byte receiver;24 original interface accessors,36 mode-record factory calls and36 record accessors pass. Inherited180 independent records/1440 statistics initializers/292 core initializers/516 cache lookups and whole-memory guards pass; numeric callbacks unchanged.

NEXT **E011CJ**: remaining post36D63C configuration fields and diagnostic/C-runtime locale environment, then final public output/outer-inner link, complete outer return and lock release. The second CRT-lock model/CC6140 unmapped locale read and first-source extended36DC58 probe are private excluded exploration, not accepted proof. Actual live Default producers/filename/destruction/reuse and complete optional field semantics stay open. Golden boot `e9983770-a981-49f9-a9f2-2fe081b5863d`/all3 protected hashes and historical checkouts unchanged; zero Starts/reboots/C/kernel changes/new Linux image tests. Native rear DENIED pending remaining bootstrap/preflight/RS/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. Clean front/back baseline first; optional AI/effects/HDR/catalogue deferred. See [E011CI](experiments/E004-front-ir-vd55g0/e011ci-outer-return-publication/README.md).

## E011CH original outer entry and actual-inner statistics — BOUNDED PASS

Original `0x36CBA0` entry through the stop before `0x36D3DC` passes 12 cases using the actual source-created inner/interface/core. Both complete statistics routines return; 180 independent entire 152-byte records, 1440 original statistics initializers, 292 core initializers and 516 cache lookups pass with whole-memory guards. Saved input is frame+32, frame+40 is diagnostic TLS and output is saved in X26. The first-kind4 search loop and nine 48-byte record vectors are exact. Explicit owned single-thread OS-lock and earlier diagnostic fixtures remain limitations; numeric callbacks are unmodified.

NEXT **E011CI**: continue after `0x36D3DC` to final inner-manager attachment, output publication and complete outer return/lock release. The current stop still holds the lock and leaves final output zero; whole outer/live Default producers/filename/destruction/reuse remain open. Golden boot `e9983770-a981-49f9-a9f2-2fe081b5863d` and all three payload hashes are unchanged; zero camera Starts/reboots/kernel/C changes/new Linux image tests. Native rear runtime remains DENIED pending remaining full bootstrap/preflight, RS, independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical gates. Clean front/back baseline first; optional AI/effects/HDR/catalogue deferred. See [E011CH](experiments/E004-front-ir-vd55g0/e011ch-outer-startup-context/README.md).

## E011CG original inner binding and retired caller inputs — BOUNDED PASS

Original caller slice36D03C..36D27C passes12 source-created606264-byte inner/interface/core bindings across3 sources/four placements. It takes the first kind4 descriptor, then requires24 bytes; valid first-match indices1/2/5/8 pass. Exact original creator arguments are selected descriptor, inner+93032, parameter list and inner+8 output.48 caller-input regions and old stack are overwritten;12 subsequent unchanged setups, full caches/516 postretirement lookups and original interface accessors read no retired caller input. Whole preexisting arena/native/source immutability, core delta and guards pass;292 original numeric initializers are unchanged. Initial and postretirement caches total1032 lookups. Full inner field semantics/outer/statistics bootstrap and filename/destruction/reuse remain open.

NEXT E011CH complete ordinary outer startup and saved caller/context/TLS ABI after core return, then full statistics initialization using the actual original inner. Extended statistics probes lacked saved caller/diagnostic state and are excluded; no unproven numeric or logger substitute is admitted. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CG](experiments/E004-front-ir-vd55g0/e011cg-inner-descriptor-lifetime/README.md).

## E011CF complete original core creator and interface — BOUNDED PASS

Full4980-byte3A8BE0 returns12 original320-byte interfaces/5152-byte cores under explicit owned count0 descriptors. Full516-byte3C8380/3376-byte3D4BD0,24 cache/bank updates,1032 exact cache lookups,24 unchanged skips and292 source-requested element initializers pass. Complete required core/setup delta, caller/old source immutability and guarded arenas pass. Actual source-created interface/core now supply12 full statistics setups,180 independent152-byte records and72 positive/72 exhausted full ordinary queries. Seven mode mirrors are byte stores; source initializer counts differ18+3+3 vs18+3+4. Numeric callbacks unmodified. Whole optional-bank field semantics/destruction/reuse remain unqualified.

NEXT E011CG complete ordinary outer36CBA0 and incoming/live Default descriptor, inner/context/opened filename lifetime. Full core creator is closed only under explicit owned inputs; whole outer/source bootstrap and RS/hardware gates remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CF](experiments/E004-front-ir-vd55g0/e011cf-full-core-startup/README.md).

## E011CE full source cache and ordinary internal type search — BOUNDED PASS

Complete original1776-byte3CA4A0 producer passes12 returns across3 sources/four owned core placements:516 actual nonnull GetTag returns/exact cache stores,324 guarded32-byte temporary name allocations/releases, exact entire core delta and all preexisting native/source/manager bytes preserved. Source24-byte manager/mode/count/extra descriptor is explicit owned count0; full344-byte cache feeds12 full setups/180 independent records. Ordinary inner372FB4/373044 source initializes type0 and increments through6 only on failure, role0/output92.72 successful full queries write92;72 exhausted owned-empty-list queries give504 failed manager attempts, write0 and preserve output despite wrapper status0. Numeric callbacks unchanged. Earlier W26 request-producer gap is closed for these source paths; source constants were not supplied by the empty input fixture.

NEXT E011CF full original core/outer bootstrap and constructor descriptor provenance. Complete4980-byte3A8BE0,516-byte3C8380 setup beyond copied descriptor/cache, actual live Default descriptor/inner receiver/context/opened filename remain open.43 lookups qualify cache population, not all optional module fields; AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. See [E011CE](experiments/E004-front-ir-vd55g0/e011ce-full-source-cache-and-request-search/README.md).

## E011CD independent statistics record and attachment fields — BOUNDED PASS

Three original source files/four placements pass180 complete152-byte constructor and final records, plus180 original attachment setters with independent exact full object/ring deltas. Each allocation source is one actual loaded72-byte corestatsconfig record. Setter X1 is that original source pointer; source+16 chooses ring base216/40+48*selector, distinct from constructor normalization of source+8. Source-tail64:72 lands at object116:124 only after setter return. Full12 setups and72 ordinary post-setup query chains retain complete heap/canary/source immutability checks; numeric callbacks unchanged. E011CC's independent attached-record field gap is closed; historical evidence remains intact.

NEXT E011CE actual ordinary input-list/type producer and full core/outer ownership.372FB4/373044 source paths use role0/92 output bytes and W26 type;36CF30 is an interface store, not request producer. Live normal request, Default descriptor/inner receiver/context/opened filename, full constructor/cache producer remain open. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS/full bootstrap-preflight/independent enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement/optical. No new Linux front/back image test. Optional AI/effects/HDR/catalogue deferred. See [E011CD](experiments/E004-front-ir-vd55g0/e011cd-statistics-record-field-lineage/README.md).

## E011CC coherent source statistics setup — BOUNDED PASS / E011CB association corrected

Source constructor3A9770 calls setup3C8380 with primaryCore+8. Correct coherent modules: aecxcorestatsconfig secondaryF18->primaryF20; aecxhwstatsconfig secondaryFE8->primaryFF0. E011CB meterweight is primaryF28; its reader/layout proof remains valid but its consumer association is superseded. Six original selected GetTag/cache fragments execute against three original loaded source managers with a controlled Default descriptor. Full39FAF8 setup passes12 runs/four placements,180 unique attached152-byte records,1440 original element-initializer returns and72 subsequent full ordinary queries; complete heap deltas/source immutability/canaries pass. All57 selected configuration records and typed channel-name/extensions pass complete native layout comparisons. Full loader2456 dispatches is not all-module field qualification.

NEXT E011CD independent attached-record field lineage and actual ordinary request role/type producer, then core/outer bootstrap. Whole constructor/cache producer, live Default descriptor/inner receiver/context/opened filename and attached-record independent semantics remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero new Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS count/whole-frame offset, full bootstrap/preflight, independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011CC](experiments/E004-front-ir-vd55g0/e011cc-coherent-source-statistics-setup/README.md).

## E011CB ordinary metering configuration — BOUNDED SOURCE PASS

E011CB qualified the typed `aecxdb1dmeterweight` reader. E011CC corrects its consumer association to primaryCore+F28: the source producer uses secondary receiver primaryCore+8, so its relativeF20 store is not primaryF20. Its original registered368-byte prototype dispatches full parent1C0A80. Three original source contexts/factories/builders produce181,625 exact symbol readers; four output placements each give12 original parent returns. Complete80-byte payloads, revision/priority/context/descriptions and48 complete4120-byte native records pass196,800 exact numeric bytes, immutable source/context/preexisting arena and guards. Nine owned preflight child-reference rejections occur before native execution. No new semantic parser stub; historical failed capacity/mapping explorations excluded.

This historical NEXT is superseded by E011CC: following39FAF8 now uses the corrected corestatsconfig and hardware modules; required request role/type and actual live inner/context remain open. Whole core/outer bootstrap and hardware parity remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged; zero new Start/reboot/C/kernel/reachable integration. Native rear DENIED pending RS count/whole-frame offset, full bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011CB](experiments/E004-front-ir-vd55g0/e011cb-ordinary-metering-configuration/README.md).

## E011CA source statistics collection and source-grid selection — BOUNDED PASS

Original caller fragment36D338–36D3D8 creates1664-byte manager and two20-slot rings (160 bytes each), then complete ConfigureHWStats39F070 builds the primary list from original source counts. Primary pointer608/head610/used614/capacity618; secondary620/628/62C/630. Three pinned parents have4/9/1,4/9/1,4/7/1 grid/hist/BFW entries:14/14/12 objects. Four placements give12 builds/160 original Init returns, checked at entry and caller return, with immutable source/cache and allocation guards; numeric callbacks unmodified. Core module placement/flag storage and caller prefix remain owned interfaces.

72 full ordinary engine/outer/original-core-TLS-setter/inner/manager/grid queries against the full source list pass written92 and source weights;72 descriptors reject. Empty owned requests0/0 select the fourth source grid through last-matching-role fallback.36 direct source-type3/4/5 requests select first exact records0/1/2, including repeated type3; direct manager return/payload is distinct from inner descriptor written count.84 original append boundaries cover empty/last/wrap/full/overfull/zero capacity with complete heap deltas. Earlier incomplete ring fixture lacked proper capacity; not an OEM startup failure. Historical evidence unchanged.

NEXT E011CB source-only ordinary39FAF8 following setup, required request role/type and core module/caller ownership. Whole outer constructor, actual live primary request and inner receiver/context/opened filename remain open. Optional AI/effects/HDR/catalogue deferred. Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, no new Start/reboot/C/kernel/reachable integration. Native rear DENIED: RS normal count/whole-frame offset, complete bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity open. No new Linux front/back image test. See [E011CA](experiments/E004-front-ir-vd55g0/e011ca-rear-source-statistics-collection/README.md).

## E011BZ original grid Init and initialized query — BOUNDED PASS

The original full grid Init3A0D70 and normalizer388630 now precede the query. Three pinned source readers supply12 grid records; four placements/three context patterns/two selectors pass288 initialized typed queries, plus24 descriptor rejections. All312 Init/helper returns have nonzero source-derived masks. Full heap deltas, source cache/typed child and query/primary-conversion weights pass; numeric callbacks are unmodified. Init's observed return register matches its normalized field; a status ABI is not assumed.

Proper Init reaches39EC68, verified as a process-wide diagnostic callback from16A4230. The earlier mask-zero fixture's numeric classification did not cover this active branch; E011BZ handles288 calls as explicit logging. Historical private/model results remain unchanged. One-primary-grid selection/outer-inner-core ownership remain fixtures; full collection/constructor and actual live receiver/context are open. Incomplete broad constructor/ConfigureHWStats attempts are excluded, not OEM failures.

Golden e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, zero new Start/reboot/C/kernel/reachable integration. NEXT E011CA source-only normal collection capacities/append guards/role-type input and primary selection via39F070/39FAF8 and36CBA0 caller. Bound required ordinary consumers; optional AI/effects/HDR/catalogue deferred. Native rear DENIED pending RS normal count/whole-frame offset, full bootstrap/preflight, independent WM16 IRQ/consumed IOVA/DMA/IOMMU retirement and optical parity. No new Linux front/back image test. See [E011BZ](experiments/E004-front-ir-vd55g0/e011bz-rear-source-grid-initialization/README.md).

## E011BY source query forwarding and corrected profile check — BOUNDED PASS

E011BX's reported numeric profile mismatch was our source-generator error: serialization mode_id at wire40 was used instead of profile-node mode_symbol_id at wire44. The corrected source check matches all seven common fields in all four saved live modules (28 comparisons); 11 rejection checks pass. Original mode-loader prefixes, one typed root reader constructor and profile callback pass for three source files/four placements (12 cases). Alignment1 is owned; all symbol readers and OS-open filename identity remain outside this proof. Historical private capture/model is unchanged; future generator corrected.

3,552 original complete engine/outer/context-setter/GetParam/manager/grid-getter chains pass in owned fixtures. 1,776 include original core TLS setter3AE320, with zero backend context stub and identical92-byte outputs to the inert-setter comparison. Actual outer36E460 forwards through inner vtable+32 setter374050 then+24 GetParam372E40. Outer+40 is inner algorithm object; inner+40 is manager; outer+68 is context ID. Numeric callbacks unmodified; checked dispatch/allocation/TLS/logging remain controlled. Whole startup construction and actual live inner vtable/context/loaded-code qualification remain open.

Golden boot e9983770-a981-49f9-a9f2-2fe081b5863d/all3 protected hashes unchanged; zero new camera Start/reboot/production kernel or reachable integration. E011BX identity remains consumed. NEXT E011BZ source-only ordinary producer36CBA0, outer GetParam store36CF30, inner/core/context ownership and stats-manager bootstrap39F070/39FAF8/370728. Avoid repeated closed cache/GetTag/copy probes. Native rear DENIED: RS normal count/whole-frame offset, full bootstrap/preflight, independent WM16 consumed-IOVA/DMA/IOMMU retirement and optical parity open. No new Linux front/back image test. Optional AI/effects/HDR/catalogue deferred. See [E011BY](experiments/E004-front-ir-vd55g0/e011by-rear-query-forwarder-context/README.md).

## E011BX live cache -> FIRST frame — BOUNDED PASS / SOURCE-RECEIVER SCOPE PARTIAL

One consumed original Windows rear4K Start/Stop completed450 valid handles.11 loaded source ranges/grid table qualified beforeStart; zero observer diagnostics. Four named source arrays/Init pairs and two complete typed query/getter returns join the actual FIRST frame+424 to first converter/publication. Independent descriptors prove allocated92/written92/types10,21; full2072 output/publication equal. Same-SP11 Linux bounded checks pass66records/24,308bytes/eight corruption negatives;90files rechecked against read-only Windows snapshot.

Strict seven-field source check REJECTS numeric profile high word+76; other six fields match one pinned candidate. Actual direct callback36E460 differs from owned fixture372E40;524-byte original callback's loaded code/inner receiver not qualified. MASM +12/+16 printf offsets were hex; eight scalar fields decoded from complete retained descriptors, original logs retained. Converter return register has no qualified status ABI. Do not promote the bounded pointer/weight join to whole source/profile/bootstrap proof or captured constants.

CDB/holder/task exit0/task removed; Golden e9983770-a981-49f9-a9f2-2fe081b5863d/all3hashes unchanged, idle/NTFSunmounted. E011BX-20261002-0030A consumed; never retry. NEXT E011BY source-only actual36E460 inner receiver/ABI and numeric metadata76 construction; closed cache/GetTag/cold-copy probes need no repeat. Native rear DENIED; RS/fullbootstrap/independent WM16 retirement/optical open. No new Linux front/back image test. Optional AI/effects/HDR/catalogue deferred. See [E011BX](experiments/E004-front-ir-vd55g0/e011bx-rear-first-aec-source-query/README.md), VALIDATION-SAFE/DIAGNOSTIC-SAFE/RECEIVER-SOURCE-SAFE/CLEANUP-SAFE/RESULT/NEXT-SOURCE.

## E011BW source-produced cold AEC weights — DETACHED PASS

Three qualified Default tuning roots have identical weights in all twelve grid records. A new portable integer decoder requires the four records to agree and rejects unsupported shapes/values. Cold AEC weights and AWB quad now come from tuning in the detached C replay; incoming cold bytes are deliberately255 and must be overwritten. GCC/Clang ASan/UBSan each pass5,616 decoder checks and510,380 full startup/preflight assertions, with zero semantic register differences in all four packets.

592 complete original engine-query/GetParam/manager/grid-getter chains pass in owned memory across74 cases/four placements/selectors12 and20. Numeric callbacks are unmodified; dispatch/allocation/TLS/logging interfaces are explicit fixtures. The five-argument wrapper's output array is argument3, count argument4. Descriptor allocated bytes+8, written bytes+12 and type+16 are u32.24 wrong-type/undersized cases return status0 but write nothing; require the full written92 contract, never status alone.

This proves invariant Default source producibility, not the live FIRST source-cache-to-prepublication-frame pointer join or opened filename/profile. E011BV's metadata pointer/copy proof remains closed and both previous Windows identities consumed. NEXT E011BX qualify both full typed query returns and their actual cache/frame identity into first83AA1C/SP+1264 -> SP+3152, keeping the second temporary separate. Do not repeat closed GetTag/copy or use captured scalars as producer policy.

Golden boot0f8a8389-9627-42e7-9c69-98b550e5814e/all3 protected hashes unchanged, camera idle/NTFSunmounted. Zero new Start/reboot/kernel build/reachable integration/MMIO/sleep. No new Linux front/back image test; native rear runtime remainsDENIED. Clean baseline first, optional AI/effects/catalogue deferred. Required RS count/whole-frame offset, complete source bootstrap/preflight and independent enabled WM16 retirement/optical gates remainOPEN. See [E011BW](experiments/E004-front-ir-vd55g0/e011bw-rear-source-cold-aec-weights/README.md), SOURCE-SAFE/INTEGRATION-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BV original live cold AEC metadata handoff — BOUNDED PASS

One fresh manual-only atomic original Windows rear4K Start/Stop completed449 valid handles.12loaded source ranges match beforeStart; zero observer diagnostics. Actual data getter0x5C2FC0/return0x5D54D0 supplies the exact pointer used by cold2072copy. First output SP+3152 -> publication -> actual store write/GetTag -> cold source/destination/source-after preserve everybyte, with actual property0x5000001C, pool/store and caller/thread identities. The second SP+5232 record is separately attributed even though equal. Windows and independent same-SP11 Linux validation pass11events/16records/23,032bytes,51privatefiles/88,082bytes and9 corrupted-fixture rejections.

This closes the bounded original LIVE metadata pointer/payload handoff; numeric source initialization and actual opened tuning profile/file remainOPEN.128 original Node interface-fixture returns separately qualify flag-vs-pointer ABI; those exclude API impls. E011BU remainspartial/consumed:5C4D78 is publication flag1 and its invalid reader dump is excluded. Do not replay either attempt or relabel source fixtures as hardware.

CDB explicit clear/detach/exit0, holder/task exit0 removed; Golden boot0f8a8389-9627-42e7-9c69-98b550e5814e/all3hashes unchanged, idle/NTFSunmounted. No Linux runtime/image/C/kernelbuild/KD/BCD/sleep. Native rear remainsdenied. NEXT E011BW independent numeric/mode source feeding FIRST cold AEC record (83AA1C/83DF68, E011BA and original loader/profile evidence); then requiredRS/fullbootstrap/preflight and independent enabledWM16 retirement/optical. Clean front/back baseline first; optionalAI/effects/catalogue deferred. See [E011BV](experiments/E004-front-ir-vd55g0/e011bv-rear-cold-aec-gettag-pointer/README.md), VALIDATION-SAFE/LOADED-QUALIFICATION-SAFE/CLEANUP-SAFE/RESULT/NEXT-SOURCE.

## E011BU live store/payload join — PARTIAL; E011BV getter pointer PREPARED

E011BU completedone original rear Windows4K Start/Stop,57valid handles.12loaded ranges source-match beforeStart. Actual UsecasePool/store and property0x5000001C agree; first output/publication/store write/cold source/destination preserve all2072bytes. Independent same-SP11 validation agrees. Strict pointer check rejected:0x5C4D78 returns published flag1, not data; zero-length READ_OUT is excluded. Actual getter0x5C2FC0 returns at0x5D54D0. Full cold pointer/metadata bridge and numeric initialization remainOPEN; do not relabel partial result.

Both attached CDB sessions explicitly detached/exit0; stale-owner second launch failed before enumeration. C++&& callback error corrected to MASM and in same single Start before capture; errors retained. Holder/task exit0,task removed; Golden bootb2a53069-ad78-4582-838b-a6ca90fe2188/all3hashes unchanged, idle/NTFSunmounted. Identity consumed. NEXT fresh E011BV-20261001-2310A actual GetTag pointer capture, prepared UNARMED; see e011bv README/PRE-RUNTIME-SAFE and e011bu VALIDATION-SAFE/CLEANUP-SAFE. Native rear denied; clean baseline first, optional features deferred.

## E011BU cold metadata observer — PREPARED, UNARMED

Fresh identity E011BU-20261001-2230A targets the actual first AEC2072 output -> publication -> original metadata store write/read -> cold IFENode copy. Twelve source ranges must be checked in the loaded user-mode DLL before arming/Start. Manual-only task with atomic entry guard, maxone camera Start, bounded original rear Color VideoRecord NV12 3840x2160 run; no kernel debugging/sleep/BCD or Linux rear activation. Scripts and validators prepared; no live result yet. See [E011BU](experiments/E004-front-ir-vd55g0/e011bu-rear-cold-aec-live-metadata/README.md), PRE-RUNTIME-SAFE/PRE-BOOT-GUARD-SAFE. Numeric tuning initialization and opened filename/profile remain separate from metadata handoff. Preserve clean baseline priority, optional features deferred and existing rear ownership gates. Inspect current attempt evidence before continuing; never infer the attempt is unconsumed after a UI interruption.

## E011BT cold AEC metadata route/copy — BOUNDED PASS

Clean front/back baseline remains first; optional AI/effects and unrelated catalogue work stay deferred. Original source selects property0x5000001C, reader vector index2, Node+1200 UsecasePool and2072 bytes.40 original writer/reader routing prefixes reach the correct store boundaries using explicit single-slot owned pools;20 publication slices and128 full original memcpy slices pass with strict memory guards. Trace/TLS context is owned; original trace construction and metadata store implementations are excluded.

Publisher0x83ABD4 sends the first temporary SP+3152. A separate second temporary SP+5232 supplies a retained processor copy; matching previous values did not identify the published record. Whole prepublisher/default reader returns, numeric initialization and actual live pool/store/payload lineage remain OPEN. Native rear denied; no image/start/reboot/C/kernel changes. Golden/all3 hashes unchanged, idle/NTFS unmounted.

NEXT E011BU source-qualified bounded Windows metadata observer from first setter output through publication/store write/read to cold2072 copy; see [E011BT](experiments/E004-front-ir-vd55g0/e011bt-rear-cold-aec-metadata-route/README.md), METADATA-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE/NEXT-OBSERVER. Do not treat the unarmed plan as a completed live join. Then baseline dependency/required RS/bootstrap/preflight and independent enabled WM16 ownership/optical validation. Entire74 renamed-key queue remains conditional on baseline consumers; full catalogue is not a first-pair prerequisite.

## E011BS user priority: clean front/back baseline before optional features

User2026-10-01 asks to deploy necessary clean front/back functionality and skip unwanted AI/effects. This changes the queue: one normal-colour mode per RGB camera, a finite front->rear->off app/image test, then expanded features/Windows1:1 parity. Full tuning catalogue port is not a prerequisite. Explicit manual exposure/WB/focus may be used for the first controlled scene with its limits reported; extra modes/HDR/multiframe/AI/beautification/portrait/advanced stabilization are deferred.

Bounded inventory over two original full rear loaders shows1,246 module instances but242 distinct embedded source names: default914instances/234names across77 ordinary profile nodes; specific332/239 across29. Names are not feature counts and do not prove the minimal enabled set. Existing detached rear register schema has14 state member groups plus its DMI wrapper. Required modules must be selected by actual enabled consumers/dependencies. Never infer a safe hardware bypass just from a name or skip an enabled stats/DMA channel.

NEXT E011BT baseline-required cold AEC metadata consumer join and selected-mode dependency closure, then required RS/bootstrap/preflight and hardware ownership. Entire74 different-name queue is deferred unless a chosen baseline consumer needs a key. Keep rear BF/WM16 retirement gating until enabled lifecycle proof or a separately proven disable/bypass. E004kg/E004ne already prove bounded RAW/software front/rear transport/switching, not clean native ISP quality parity. No new deployment/image/start/reboot/C/kernel changes; Golden/all3 hashes unchanged, idle/NTFS unmounted, native rear denied. See [E011BS](experiments/E004-front-ir-vd55g0/e011bs-clean-front-rear-scope/README.md), INVENTORY-SAFE/BASELINE-SCOPE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BR common module headers and selected nonroot retrieval — BOUNDED PASS

Four original full rear loaders at two placements pass194,976 exact readers and2,492 actual module returns. Seven common source-backed fields at16/56/60/68/72/80/208 match at actual return and remain intact after loader/input retirement;52,332 repeated field checks pass. Owned dynamic names and map keys are active/terminated and equal each other. Name-map stores preserve typed source leaf/flag-derived map owner.

Original source-derived selectors and map lookups pass4,688 selected existing-key returns before/after source unmap, old context overwrite and retired-storage poison:2,940 nonroot and1,748 root. Eligible source-exact keys are872(default)/300(specific), across40/9 nonroot owners. Original string construction uses typed source names. All preexisting allocation/heap bytes survive; no missing keys are queried.

NEXT E011BS independent naming authority for42(default)/32(specific) different owned names,148 excluded across placements, then remaining typed payload consumers. Common header/retrieval success does not qualify other tuning bodies, whole manager lifetime, destruction/reuse, platform/opened filename or camera parity. Golden/all3 hashes unchanged, idle/NTFS unmounted; zero starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical open; native rear denied; no new front/back image test. Originals private on SP11. See [E011BR](experiments/E004-front-ir-vd55g0/e011br-rear-selected-module-metadata/README.md), RETRIEVAL-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BQ source hierarchy and nonroot selection — BOUNDED PASS

Four full original rear loaders at two placements pass 194,976 exact reader returns and 86,496 source-derived hierarchy pointer checks. Original selector0x6F3BD0 returns match the independent typed model in2,072 queries, including1,248 nonroot and784 null returns, before and after source/context retirement. Direct helper0x6F1D68 adds7,208 returns,128 nonnull. All eight links per node are verified: source wire16 becomes primary/inheritance pointer16; flag-derived48 points to parent map owner; ordinary children32/40, flagged children56/64 and sibling72 preserve physical record order.

Query index0 is ignored. Contiguous category grouping uses fullU32 words; child matching uses lowU16 category/value. Original repeated-category recursion passes nine separate owned seven-node graph queries (six positive/three null), including primary fallback. Three malformed primary reference shapes are rejected before execution. No selector allocations or source/heap changes occur. Original module/AEC ownership checks and five existing shims are retained.

NEXT E011BR nonroot loaded-module retrieval and independently source-backed common metadata. Entire manager source lifetime, other module bodies/root/grid/padding/platform/opened path and destruction/reuse remain open. Golden/all3 hashes unchanged; idle/NTFS unmounted; no camera starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical open, native rear denied, no new front/back image test; originals private on SP11. See [E011BQ](experiments/E004-front-ir-vd55g0/e011bq-rear-source-mode-selection/README.md), SELECTION-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BP both rear full loaders / retained AEC root lookup - BOUNDED PASS / NONROOT POLICY OPEN

Four original production factory/full loader success1 returns cover both rear sources at placements0/1:194,976 exact readers,2,492 module dispatches and four source-qualified actual AEC parent returns. Larger rear-default full-loader coverage is now qualified. Immutable AEC module spans0:280/288:384 and all30(default)/26(specific) deep allocations survive full loader return;280 is the mutable sibling link.3,604 bounded node lists/2,492 active module memberships pass.

Actual loader store6F3654 places AEC in owned56-byte name-map entry/value48. It lives in a source-flagged leaf sibling list while root profile map96 owns lookup. Eight original root selector6F3BD0 and eight original loaded name-map6F3F48 returns pass before/after source unmap, old48-byte context overwrite and retired-storage poison, with native reads rejecting stale context/retired storage. Entire manager source lifetime remains OPEN: header-name pointer16 still borrows source88. Root querycount1 skips index0; visible profile text is not a unique selector.

NEXT E011BQ typed nonroot/repeated-group queries and node children16/32,sibling72,alias48/wire16, then selected consumers. Destruction/reuse, other module fields/root/grid/padding/platform/opened path remain open. Scoped27-site instrumentation and binary-search extent checks preserve accepted original outputs/five shim targets; no new semantic parser shim. Golden/all3 hashes unchanged, idle/NTFS unmounted, no starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical open, native rear denied, no new image test; originals private on SP11. See [E011BP](experiments/E004-front-ir-vd55g0/e011bp-rear-aec-output-ownership/README.md), OWNERSHIP-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BO full production factory / rear-specific loader - BOUNDED PASS / LIFETIME AND FULL PROFILE OPEN

Four original factory returns and eight actual name lookups pass over both rear files/two placements:565 registry stores per factory,194,976 exact reader returns and four qualified direct AEC joins. The prior0xCB167C stop is unresolved HeapFree import; guarded owned release0xCAE730 validates allocation start/no double release/canaries and defers retirement without reuse. No OEM heap defect is claimed.

Two additional full production loader0x6F22C8 returns on rear-specific source have success1,35,462 exact reader returns total and664 actual module lookups/dispatches. Actual AEC caller0x6F35AC -> parent0x123CC0 -> return0x6F35B0 selects the registered OEM request with alignment1. Both actual AEC returns pass qualified revision/grid/histogram/BFW fields, non-cursor preservation and source/allocation guards. Other dispatched module fields are unqualified. Slot8=0xD2AC0 is deleting destructor; slot24=0xD2A20 is name lookup. BN labels corrected, counts retained.

NEXT E011BP output ownership/source-context lifetime after loader return, full-loader coverage for larger rear-default file, full profile/mode/node-container selection, destruction/reuse. Remaining root/grid fields/padding/platform/opened path remain open. Golden/all3 hashes unchanged, idle/NTFS unmounted; no starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical open; native rear denied; no new image test; originals private on SP11. See [E011BO](experiments/E004-front-ir-vd55g0/e011bo-rear-aec-factory-registry/README.md), REGISTRY-SAFE/LOADER-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BN production AEC request - BOUNDED PREFIX/JOIN PASS / REGISTRY SELECTION OPEN

Four original production-constructor prefixes reach0xD979C -> AEC request constructor0x1231D8 and stop at0xD979A0,986 allocations per prefix. Name and version10 now originate in original code, not tuning-file supplied request arguments. Four AEC parent full returns, four metadata returns and eight original incompatible-name/version rejections pass against 194,976 exact source symbol-reader returns. Original source context/cursors and qualified revision/grid/histogram/BFW checks are retained.

Production object extent5696 includes cache at5632; base1112 extent does not cover it. Production vtable0x1335288 shares profile slot0=0x6F3B50 but uses deleting-destructor slot8=0xD2AC0 and name-lookup slot24=0xD2A20 (labels corrected by E011BO). The four-table callback statement refers to each table's first slot, not adjacent slots. Factory prefix is intentionally stopped; direct source consumer join does not prove registry selection or complete factory/loader return.

NEXT qualify production completion/runtime path0xCB1650/0xCB167C, registry lookup/creation, loader after0x6F3524 and context transfer; no failed exploration is OEM failure evidence. Opaque name tail/padding, every root/grid field, platform/mode16/node containers/opened path remain open. Golden/all3 hashes unchanged, idle/NTFS unmounted; no starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical open; native rear denied; originals private on SP11. See [E011BN](experiments/E004-front-ir-vd55g0/e011bn-rear-aec-factory-request/README.md), FACTORY-REQUEST-SAFE/GUARD-SAFE/RESULT/NEXT-SOURCE.

## E011BM original symbol context and AEC join - BOUNDED PASS / FACTORY POLICY OPEN

Four original symbol-builder returns, 194,976 exact symbol-reader returns, four AEC parent full returns, eight original metadata constructor returns and eight original name/version gate rejections pass over two rear files at two placements. All source readers use the original loader's stack context: header module name+0, header version+8, maximum ID+24 and table+40. Builder returns at0x6F3524. No metadata/name/comparison shim remains in this join.

Parent0x123CC0 x0 is a request descriptor, not file context: embedded name+16 and U64 version+60 must match reader+12/+52. The owned request is source-backed and built with original metadata helper; actual factory request policy remains OPEN. AEC subclass vtable0x1335598 and reader ID+8 -> module+56 are verified. Qualified revision/grid/histogram/BFW fields and exact cursor-only changes pass. Unwritten padding and opaque embedded-name tail are unqualified; prior zero-filled fixture bytes are not source zero-policy.

NEXT trace actual factory/caller request construction and complete loader/context ownership after0x6F3524; audit remaining root/grid fields, mode wire+16/platform/node strings and opened filename policy. Golden/all3 hashes unchanged, camera idle, NTFS unmounted; zero starts/reboots/observer/C/kernel build. Cold metadata/RS/bootstrap/WM16/optical remain open; native rear runtime denied. Originals private on SP11. See [E011BM](experiments/E004-front-ir-vd55g0/e011bm-rear-aec-original-context/README.md), CONTEXT-JOIN-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE.

## E011BL original source profile records - BOUNDED PASS / ACTUAL AEC CONTEXT OPEN

Four original loader prefixes over two SHA-pinned rear files at two placements pass: 3,604 source mode records, 56 original profile callback returns and four actual table-builder reader returns. Runtime node stride160 is indexed by serialized ID, not file order; source bytes0:12 and parent ID+12 -> pointer+24 are verified. Loader X1 is file base and X2 byte length. The first actual reader selector is invalid sentinel: its zero numeric/empty profile return does not close valid AEC selection.

Manager+16 points to the header module name at file+88, not an opened filesystem filename. Header32:40 -> manager1104:1112 is verified; manager24:32 policy remains open. Actual reader context is not manager+16. Manually guessed AEC contexts failed checks and are excluded. NEXT reach the actual AEC reader via original caller state after 0x6F4E88, then join parent0x123CC0 metadata/name allocation. Opaque wire+16, platform path, node strings/containers and full loader return remain open.

Golden boot/all three protected hashes unchanged; camera idle/NTFS unmounted. Zero camera starts, reboots, observer, production C or kernel build. Cold metadata/RS/bootstrap/WM16/optical gates remain open; native rear runtime denied. Originals remain private on SP11, captured scalars are not producer inputs. See [E011BL](experiments/E004-front-ir-vd55g0/e011bl-rear-aec-source-profile/README.md), SOURCE-PROFILE-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE.

## E011BK original profile callback — COMPLETE READER FIXTURE PASS / SOURCE PROFILE SELECTION OPEN

Original interface constructor0x6F3D08 installs table0x133B740 whose slot0 is callback0x6F3B50; slot0 in four distinct interface tables shares that callback; their other methods differ. Four constructor returns,72 callback returns,44 independent recursive formatter returns and72 complete reader returns pass at four placements, with eight pre-execution scope rejections. Reader dispatch0x6F4A98 now executes the original callback and original decimal formatter0xCB6300. No new helper shim/allocation; only inherited security-cookie shims execute.

Callback node table/count are interface+1072/+1080, stride160. Reader index is wire+44; selected node bytes4:12 -> reader60:68 exactly. Null table/negative signed index/out-of-range zero only numeric output. Valid callback clears one profile byte; parent-first formatting follows node+24, emits U16+4/+6 decimal pairs for zero U32+8, joining included pairs with a vertical bar. Exact whole-heap/source-map guards pass, including128-byte profile buffer and formatter terminal byte127. Scope: acyclic owned graphs<=12 nodes/generated text<=100; zero-filled owned file context/alignment1. Actual loader subclass/instance, tuning-file node selection and filename remain OPEN; captured values are not producer inputs.

NEXT qualify loader node-table/count stores0x6F3188/0x6F318C and table update0x6F34A4, then actual interface argument at loader0x6F3520 -> table builder0x6F4CA8 -> reader call0x6F4E84. Prove source nodes/parent links/filename before full-parent metadata join with extra name allocation; audit remaining root/grid fields. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f/all3 hashes unchanged, FullIOv19c/empty next_entry/camera idle/NTFS unmounted. Zero Start/reboot/observer/production C/kernel build. Remaining loader/cold metadata/RS/bootstrap/WM16/optical gates OPEN; native rear runtime DENIED. See [E011BK](experiments/E004-front-ir-vd55g0/e011bk-rear-aec-profile-callback/README.md), CALLBACK-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BJ reader mapping and metadata widths — BOUNDED PASS / CALLBACK AND PROFILE OPEN

44 original reader prefixes reach0x6F4A7C before callback dispatch:12 typed roots from three pinned files +32 owned numeric variants at four placements. Wire36:44 -> reader52:60 (8bytes), wire44:48 -> reader68:72 (4), wire52:56 -> reader200:204 (4); cursor advances56. x4 is source-relative object-section offset: reader208 = x1 filebase + x4 sectionoffset + wireu32at48. Complete source/heap guards pass. Zero-filled owned context/explicit alignment1 are fixture scope; callback output reader60:68 remains untouched, profile firstbyte72 zeroed. Actual caller/context/profile policy remains OPEN.

48 original metadata-constructor full returns plus48 standalone/48 embedded original name-helper calls and six pre-execution numeric rejections pass. Constructor x2/x4 are U64 stored at+60/+72; nonzero high halves at+64/+76 survive. E011BH's zero high halves apply only to its U32 inputs, not general zero-field invariants; its minor/tag labels are not independent semantic policy. Parent x2 is literal10, x3 loads U32 reader68, x4 loads U64 reader60. Numeric variants are propagation tests. Existing typed validation and historical full-parent skips remain.

NEXT qualify loader-supplied interface/actual0x6F4A98 callback and reader60:68/profile output; then filename/source authority and full-parent metadata join with extra name allocation; audit remaining root/grid fields. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f/all three hashes unchanged, saved FullIOv19c/empty next_entry, camera idle/NTFS unmounted. Zero Start/reboot/observer/production C/kernel build. Exact filename/profile/full loader/cold metadata/RS/bootstrap/WM16/optical parity remain OPEN; native rear runtime DENIED. See [E011BJ](experiments/E004-front-ir-vd55g0/e011bj-rear-aec-reader-width-authority/README.md), WIDTH-READER-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals remain private on SP11.

## E011BI original reader context — INITIALIZER/ID/NAME PREFIX PASS / PARSER INTERFACE OPEN

Original reader initializer 0x6F4790 returns at four placements; exact zero ranges 0:8, 52:68 and 208:224, all other heap bytes preserved. Table builder 0x6F4CA8 calls constructor 0x6F47B8 at 0x6F4E84. 60 prefixes stop at 0x6F4870: 12 typed AEC roots from three pinned sources and 48 owned variants. ID -> reader+8, original 32-byte memcpy record+4 -> reader+12, terminator+44. Source bytes/cursor/context and complete heap guards pass; nine scope rejections before execution; no prefix stubs or allocations.

x1 source base/x2 available source bytes/x3 offset pointer are qualified in this owned prefix, under explicit x6 alignment1. Full constructor caller alignment remains open. Later parser-interface dispatch 0x6F4A98 is not qualified/executed in accepted fixtures; exploratory guessed interfaces/arguments are excluded and not OEM fault evidence. Numeric versions/profile/filename construction and full-parent metadata join remain OPEN. Historical metadata skips are unchanged. NEXT derive actual temporary source-interface construction/target and guard semantics, then complete reader/filename authority and metadata integration; audit remaining root/grid fields.

Golden boot 50edbeb8-e42d-41b1-8b37-3d536443604f and all three protected hashes unchanged; saved FullIOv19c, empty next_entry, camera idle/NTFS unmounted. Zero Start/reboot/observer/production C/kernel build. Exact source/profile selection, cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and optical parity remain OPEN; native rear runtime DENIED. See [E011BI](experiments/E004-front-ir-vd55g0/e011bi-rear-aec-reader-context-prefix/README.md), READER-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BH original metadata helpers — OWNED-FIXTURE PASS / PARENT CONTEXT JOIN OPEN

Original6F45D8 metadata constructor,6F4AC0 name helper andF5DF00 comparison execute in isolated owned fixtures:44 constructor returns,44 standalone+44 embedded name-helper calls,192 comparison cases,15 scope rejections before execution. Original name allocation/source strings/heap field guards pass. ASCII names<=32 preserve case; profile+80 truncates127 chars, filename+208 truncates64. x2/x3/x4 forward into+60/+68/+72. Opaque name-helper tail and names>32 remain excluded; numeric patterns are not selector/mode policy.

Source caller reads profile at reader+72, minor+68, reader->file context at+0 and filename pointer context+0. Original compiled AEC name matches the typed source. Loader initialization of those fields is stillOPEN; owned strings do not prove actual filename/profile. Metadata skips are removed only in the isolated helper fixture; historical full-parent metadata skips remain unchanged. NEXT trace source/selector/header ownership, then integrate the original helpers while accounting for the additional name allocation. Audit remaining root/grid fields before full aggregate claims.

Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f/all3 protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Zero Start/reboot/observer/production C/kernel build. E011BD identity consumed/Windows initialization incomplete. Exact source/profile selection, cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native rear runtime **DENIED**. See [E011BH](experiments/E004-front-ir-vd55g0/e011bh-rear-aec-metadata-authority/README.md), METADATA-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BG original BFW sibling — BOUNDED PASS / METADATA AND FULL PROFILE OPEN

Original parent full returns now validate typed bfwStatsConfig v0.0/mode0/no-selector140-byte ->160-byte runtime, one root count40/ref44. Five BFWROICombo records count12/ref16 produce160 bytes through10 original E8CC8 reader calls; nested data count132/ref136 uses original EA758. Payload count80/pointer88, BFW pointers24/152, exact scalar mapping/selected IDs/cursors/source copies verified. No new helper stubs or captured producer inputs.

108 full-parent returns/BFW records across four placements validate540 ROI combinations,1080 original ROI returns and108 BFW data arrays;34 malformed source descriptions rejected. Eight owned scalar/eight ROI/eight nested-data variants; inherited revision/grid/histogram checks retained, including772 histogram entries, source data/reader non-cursor bytes/allocation canaries preserved. Full metadata/profile authority and every grid scalar/reserved field remainOPEN.

Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f/all3 protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Zero Start/reboot/observer/production C/kernel build. NEXT qualify metadata6F4AC0/6F45D8/comparisonF5DF00, audit remaining root/grid fields, then complete loader6F22C8 and exact selector/source policy. E011BD identity still consumed/Windows initialization incomplete. Cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native rear runtime **DENIED**. See [E011BG](experiments/E004-front-ir-vd55g0/e011bg-rear-aec-bfw-materialization/README.md), BFW-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BF original histogram sibling — BOUNDED PASS / BFW AND FULL PROFILE OPEN

Original parent histogram materialization is validated through loop exit124970, before BFW source fields: root count32/ref36; typed histStatsConfig v0.0/mode0/no-selector. Default candidates have9 entries, rear-specific7; wire stride172/runtime200, payload count64/pointer72. Native nested readerEA758 selects typed data/values IDs, with pointer160/184, exact source copies and consumed cursors. Aliased source spans do not substitute for selected-reader authority.

76 prefixes across four placements plus3 full-parent return smokes verify573 histogram entries,1146 nested arrays and2865 original scalar memcpy spans;150 malformed source descriptions rejected. Eight owned scalar/eight nested-array variants preserve source/reader non-cursor bytes and allocation canaries. Original revision/grid checks retained; no additional stubs or captured producer inputs. Full-parent smokes do not validate BFW fields or full metadata/profile selection.

Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f and all3 protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Zero Start/reboot/observer/production C/kernel build. NEXT typed bfwStatsConfig at root count40/ref44, BFWROICombo/nested fields, then remaining metadata/comparison helpers and full loader selection. E011BD Windows identity remains consumed/initialization incomplete. Cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native rear runtime **DENIED**. See [E011BF](experiments/E004-front-ir-vd55g0/e011bf-rear-aec-histogram-materialization/README.md), HISTOGRAM-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BE original revision materialization — BOUNDED PASS / FULL PROFILE OPEN

Original revision reader0xDB3A0 and original copy helper0xCAE7C0 now execute without stubs, using E011BD-qualified packed alignment1. Revision x2=count2, x3=alignment1; guard0xDB468 is an explicit zero-divisor trap, not a demonstrated ARM64EC/hardware defect. Three pinned sources provide typed revision v0.0/mode0/no-selector/two-byte terminated records. Original output at payload+32 equals its source and cursor advances2.

48 parent/revision/four-grid prefixes plus12 full-parent return smokes pass at four placements, including nine owned revision variants:60 original revision returns/copy calls and240 original grid returns. Fourteen malformed revision descriptions rejected; source data, reader non-cursor bytes and allocation canaries preserved. No captured value becomes policy. Full-parent returns are smokes only; sibling metadata and full aggregate/profile authority remainOPEN. Seven metadata/security/comparison/allocation/memset helpers remain explicitly stubbed.

Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f and all3 protected hashes unchanged; camera idle/NTFS unmounted. Zero new Start/reboot/observer/production C/kernel build. Prior E011BD Windows initialization remains incomplete and its identity consumed. NEXT derive typed sibling/statistics metadata fields beyond124040, qualify remaining metadata helpers and full loader selection. Cold metadata ownership, RS authority, deterministic bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native rear runtime **DENIED**. See [E011BE](experiments/E004-front-ir-vd55g0/e011be-rear-aec-revision-materialization/README.md), REVISION-SAFE, GUARD-SAFE, RESULT and NEXT-SOURCE. Originals stay private on SP11.

## E011BD original deserializer caller — ENTRY/SOURCE PASS, INITIALIZATION INCOMPLETE, GOLDEN RETURNED

One qualified original123CC0 entry receives alignment1. Actual module table1335598/slot8 and reader bounds match; caller return6F35B0/code window matches the pinned original, with indirect call6F35AC. The48-byte root/full404-byte grid fingerprint matches only rear-specific com.surface.tuned.rfc_ov13858.bin among three pinned candidates; exact opened filename/full selection policy remainOPEN.

Original temporary context+48 is initialized to1 at6F26C4/6F26C8 and loaded into the third argument at6F3594. Four owned initializer cases and24 caller-prefix cases pass, preserving source heap and arguments; original virtual target loading executes. The fixture skips guard check6F35A8 and stops before dispatch. Full loader/revision/all-paths policy is excluded; no captured value becomes a producer input.

Nine loaded code ranges/four tables and21 private records/2388 bytes pass native PowerShell plus independent Linux checks. An incomplete first entry log is rejected: CDB supports @lr, not @x30; correction occurred at the same held entry before Start. Initialization ended with holder result1, before READY/START.GO: zero Start/Stop and no current frame run or named/cache join. Cause is not independently diagnosed. Identity E011BD-20261001-0933A consumed, holder entered once; CDB detached/exited0/task removed. Prior E011BA4K success remains separate evidence.

Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f, kernel7.1.5-sp11-render-parity-v4+, all3 protected hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. No production C/kernel build/native rear activation. NEXT complete loader/profile/revision authority and extend parent fixture beyond excluded DB3A0 and sibling/profile helpers. Any Windows run needs a fresh identity and @lr; never reinvoke this holder. Cold metadata ownership, RS authority, full bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native rear runtime **DENIED**. See [E011BD](experiments/E004-front-ir-vd55g0/e011bd-rear-aec-deserializer-caller/README.md), ENTRY-SAFE, CALLER-SOURCE-SAFE, CLEANUP-SAFE, GUARD-SAFE, NEXT-SOURCE and RESULT. Originals remain private on SP11.

## E011BC parser alignment audit — BOUNDED PASS / CALLER POLICY OPEN

Three SHA-pinned tuning roots each have zero in header field0x26. Reject the simple hypothesis that this field directly supplies the explicit packed alignment1 used by E011BB; a conversion or separate caller policy remains possible. Original header-labelled manager constructor6F3D08 returns at four owned-memory placements, with48 exact member writes total and every other heap byte preserved; no helpers are stubbed. The candidate halfword read6F0258/function6F01E8 has not been joined to the AEC deserializer caller. Readonly manager/root/factory navigation anchors are documented; polluted871610 decompiler semantics are excluded.

E011BB's548 four-grid prefixes/2192 original grid returns/6576 matching weight fields and12 private live/source comparisons remain valid under explicit alignment1. Actual caller alignment, exact selected filename/profile, revision materialization and complete bootstrap remainOPEN. No captured value becomes policy. No new identity, observer, camera Start, reboot, production C or kernel build. Golden boot d1ebda3c-7b12-4b35-8819-296ed4b29f4b/all3 protected hashes unchanged; saved FullIOv19c, empty next_entry, NTFS unmounted/camera idle.

NEXT qualify actual module-table1335598/slot8/target123CC0 caller and third argument. Use a fresh loaded-code/table-qualified single-use Windows entry observation if source navigation cannot resolve it. Then source/profile/revision authority, cold metadata ownership, RS authority, deterministic bootstrap and WM16 retirement. Native Linux rear runtime remains **DENIED**. See [E011BC](experiments/E004-front-ir-vd55g0/e011bc-rear-aec-parser-alignment-authority/README.md), SOURCE-SAFE, GUARD-SAFE, NEXT-SOURCE and RESULT. Originals/decompiled C remain private on this SP11.

## E011BB original four-grid mapping — OFFLINE PASS / CALLER POLICY OPEN

548 original parent-through-four-grid prefixes pass at four owned-memory placements:2192 complete grid-reader returns and6576 matching weight fields. Serialized entries start0/101/202/303 and each consumes101 bytes; runtime entries use120-byte stride. Three SHA-pinned Default sources each match all four E011BA live cache weight triples,12 comparisons/144 bytes. Additional16-byte copies at offsets32/48 and typed nested4-byte data arrays are verified;64 malformed source descriptions are rejected. Source bytes and allocation canaries stay intact.

The earlier123820 stop is an explicit zero-divisor guard for the serialized-alignment argument retained at123570. The complete fixture passes alignment1 explicitly; actual caller/live alignment policy remainsOPEN. This was not an ARM64EC requirement or driver defect. Root virtual table1335598/slot8 points to123CC0 in source, and all four prior named objects have that table pointer; actual loaded slot bytes/entry argument were not captured. Payload+2C=4 and nearby+30=0; do not call+30 a completed count.

Three full parent-return smoke checks pass, but revision/name/security/allocation/memset helpers remain excluded/stubbed; sibling field/profile metadata policy is not closed. No captured scalar becomes a producer input. No camera Start/reboot/production C/kernel build/native rear activation. Golden boot d1ebda3c-7b12-4b35-8819-296ed4b29f4b/all three hashes unchanged, saved FullIOv19c, empty next_entry, NTFS unmounted/camera idle.

NEXT source-close deserializer caller alignment, selected file/profile and revision/metadata authority before detached source integration. Cold metadata bridge, RS authority, complete bootstrap, WM16 retirement and Linux optical parity remainOPEN; native rear runtime **DENIED**. See [E011BB](experiments/E004-front-ir-vd55g0/e011bb-rear-aec-four-grid-deserialization/README.md), DESERIALIZATION-SAFE, ALIGNMENT-SOURCE-SAFE, GUARD-SAFE, NEXT-SOURCE and RESULT. Originals remain private on SP11.

## E011BA live named AEC source/cache — PASS / GOLDEN RETURNED

One fresh original Windows rear Color VideoRecord NV12 3840x2160 Start/Stop completed874 valid4K frame handles. Seven loaded code ranges and three tables matched before Start; actual public/core/bank callback slots and grid vtable matched before use. Four named aecxhwstatsconfig lookups join module+120 payload to bank+FE8, through Configure returned data+F0 to payload+38 grid array.

Grid Init retains array elements at byte offsets0/120/240/360, with all120 bytes preserved per element. The first element's12 weight bytes join the named selected module and match three independently parsed SHA-pinned Default roots. Later elements have pointer-retention proof only; their numeric source mapping remainsOPEN. Initial validator's all-first-pointer assumption was corrected without altering captures. Windows and independent same-SP11 Linux validation pass78 private records/8256 bytes. No captured weights become producer inputs.

Identity E011BA-20261001-0749A consumed; CDB explicitly detached/exited0, task ended0/removed, no automatic triggers. Normal reboot returned protected Golden boot d1ebda3c-7b12-4b35-8819-296ed4b29f4b, kernel7.1.5-sp11-render-parity-v4+, saved FullIOv19c/empty next_entry and unchanged three payload hashes. NTFS unmounted, camera idle. No kernel debugging, BCD/sleep changes, production C/kernel build/native rear activation.

NEXT complete original grid reader/typed aggregate and all-four source mapping, then independently resolve profile/source-selection authority before source-only integration. Exact loaded filename/full profile, cold numeric policy/metadata bridge, RS authority, whole bootstrap, WM16 retirement and Linux optical parity remainOPEN. Native Linux rear runtime **DENIED**. See [E011BA](experiments/E004-front-ir-vd55g0/e011ba-rear-aec-live-source-cache/README.md), VALIDATION-SAFE, CLEANUP-SAFE, GUARD-SAFE, NEXT-SOURCE and RESULT. Originals remain private on this SP11.

## E011AZ AEC parent-to-first-grid weights — OFFLINE PASS / LIVE SOURCE JOIN OPEN

The original parent reader now resolves the grid symbol at wire+28, allocates 4×120=480 bytes, stores the first-grid array at payload+38 and copies 12 weight bytes from wire+14 to grid+14. 548 original prefixes pass across three independent installed Default roots and scalar mutations, plus 48 array-address and 18 original symbol-helper checks. Source bytes/allocation canaries are preserved; 16 malformed source descriptions are rejected. Captured weights are comparison outputs only.

Original symbol/count/grid readers and native memcpy execute; metadata/security/name/comparison/allocation/memset and revision materialization helpers are excluded/stubbed. Prefix stops 123818; full aggregate/post-copy bookkeeping and actual Windows selected profile/source/cache join remain OPEN. At the first-grid prefix, payload+2C=4 and +30=0; do not assign the total to the wrong counter. ID 0 resolves symbol slot 0 and requires separate type authority.

NEXT fresh qualified live named-source/cache join: hwstats name x1 at call 3CA984, return 3CA988, bank-holder store 3CA998; then actual public/core/bank callbacks and ConfigureHWStats 39F0B8/39F0BC -> module payload+38 -> grid Init 3A0D70. NEXT-OBSERVER is source-only, no fresh identity or arming; E011AX identity remains consumed. Cold metadata bridge, RS authority, complete startup, WM16 retirement and Linux optical parity remain OPEN; native rear runtime **DENIED**. Existing full offline parity remains 0/0/0/0 conditional on prior observed inputs.

Golden boot f627e38e-19d3-480a-900d-73116d63b4df/all 3 payload hashes unchanged, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. Transient PiMaster drop recovered without reboot. No camera Start/production C/build/runtime action. See [E011AZ](experiments/E004-front-ir-vd55g0/e011az-rear-aec-grid-materialization/README.md), MATERIALIZATION-SAFE, GUARD-SAFE, NEXT-OBSERVER and RESULT. Originals remain same-SP11 private.

## E011AY named AEC module and grid reader — OFFLINE PASS / POLICY OPEN

The original public/core/bank accessor chain now selects the named aecxhwstatsconfig payload. 128 owned cases execute all three accessors and the cache loads, with 43 original named lookups per case. The core accessor's **pre-indexed +8** matters: data is bank+EF8 =core+F00; hwstats is bank+FE8 =core+FF0. Do not reuse offsets with the wrong owner base.

Three SHA-pinned installed Default v10.0 roots each have a candidate gridStatsConfig child. The original grid reader/native memcpy copies wire+14 to grid+14 across 12 weight bytes; 137 cases at 4 placements plus private comparison pass 549 executions. Candidate source weights match E011AX across 12 bytes; captured weights are never producer inputs. Parent deserialization, array bookkeeping/aggregate tail, actual profile choice and live named-module/cache join remainOPEN. Matching values do not close numeric policy.

NEXT qualify parent reader 123CC0, payload+38 pointer store 123FA4 and first grid reader 123550 call 124034, then actual selected source/cache ownership. Prefix ends 123818; do not treat the exploratory post-prefix BRK as a driver defect. Prior E011AX live identity remains consumed; no new observer armed. Cold metadata bridge, RS authority, whole bootstrap, WM16 retirement and Linux optical parity remainOPEN; native rear runtime **DENIED**.

Golden boot f627e38e-19d3-480a-900d-73116d63b4df/all 3 payload hashes unchanged, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. No camera Start/reboot/production C/build/runtime action. See [E011AY](experiments/E004-front-ir-vd55g0/e011ay-rear-aec-cache-construction/README.md), SOURCE-SAFE, SCALAR-SAFE, GUARD-SAFE and NEXT-SOURCE. Originals remain same-SP11 private.

## E011AX live AEC cache/frame lineage — PASS / EARLIER WRITER AND METADATA BRIDGE OPEN

One qualified original Windows rear4K Start/Stop completed710 valid frame handles. Actual grid Init/cache/getter ownership is joined across4 captures, with selector12/type10/92-byte primary descriptor. Two same-object/cache getter observations write the primary output; final observed92-byte block equals the consumed frame. First BG-joined getter weights and4 primary scalar-copy records match. Only selector12 callback was logged; do not assign the second getter's selector by timing (source has subsequent selector20 at852984). Full GetParam return is not instrumented.

Cold default2072-byte copy is exact and source-preserving. Its weights match primary fields, but cold source pointer differs: metadata ownership bridge remainsOPEN. Weights were already present when original grid Init retained its pointer; numeric cache construction lies earlier and remainsOPEN. No observed triple became policy. Windows/independent Linux private validation pass67 files/13616 bytes; originals remain same-SP11 private. CDB exited, task ended0/removed, identity E011AX-20261001-0055A consumed.

Golden boot f627e38e-19d3-480a-900d-73116d63b4df, kernel7.1.5-sp11-render-parity-v4+, saved FullIOv19c, empty next_entry/all3 hashes unchanged. NTFS unmounted, camera idle. No production C/kernel build/native rear runtime. NEXT trace caller-selected cache construction before Init3A0D70 via ConfigureHWStats39F070/x25+38; qualify owner/writer before fresh single-use oracle. Then cold metadata bridge, RS authority, complete startup and WM16 IRQ/IOVA/DMA/IOMMU retirement. Native rear runtime remainsDENIED. See experiments/E004-front-ir-vd55g0/e011ax-rear-aec-hwstats-source-authority.

## E011AW cold AEC weight origin — BOUNDED COPY PASS / INITIALIZER OPEN

Source-locked engine call8528EC binds algorithm BG selector12/output type10/size92 into frame+1A8, which later supplies hardware AEC_BE weights. Do not assume hardware AEC_BE naming selects algorithm BE20. AEC GetParam372E40 uses24-byte typed descriptors (query output pointer+18/count+20 hex);48 valid routes and24 wrong-type/undersized routes are mechanically verified before39EA40 dispatch.

Original grid getter3A0DB0 copies cache+14/+18/+1C through object+18 into output+44/+48/+4C. Original primary fragment83E01C..83E034 copies frame+1EC/+1F0/+1F4 into stats+30/+34/+38. Each bounded copy passes908 owned cases across4 bases,5448 matching fields total and checked neighbor/source preservation. Neither bounded fragment generates the numeric triple. The original default AEC copy is precisely73C090, length818(hex), retained node destination+72A58 from E011AN.

Cold numeric initialization and live cache/selector lineage remainOPEN. Full C++ dispatch-manager/context exploration is incomplete; diagnostic tails, full getter/engine return and zero-count diagnostic behavior are excluded. No captured value or constant became policy. No production C/kernel build/runtime action occurred. Last full E011AV replay remains0/0/0/0 conditional on observed cold AEC/normal inputs. Protected Golden boot25999320-3114-4f2c-bbce-a6335b0e2046/all3 payload hashes unchanged; NTFS unmounted/camera idle.

NEXT fresh qualified Windows observation of the earliest primary AEC BG query and actual cached grid weights during initialization/prepublish, then trace the cache+14/+18/+1C writer/source policy. Capture only BE20 would miss the static primary path. Follow E011AW NEXT-OBSERVER plan; it is source-only, not armed. Then RS count/offset authority, complete bootstrap/preflight and independent WM16 IRQ/consumed-IOVA/DMA/IOMMU retirement. Native rear Linux runtime remainsDENIED. See experiments/E004-front-ir-vd55g0/e011aw-rear-cold-aec-weight-origin README, SOURCE-SAFE, VALIDATION-SAFE and RESULT. Originals/decomp remain private on SP11.

## E011AV source-derived cold AWB quad — BOUNDED OFFLINE PASS

The clean integer decoder now derives the initial AWB quad from the independently parsed bgStatsConfigV1 v1.0 Default root, rather than a captured cold flag or constant. Three SHA-pinned applicable tuning files have one named 93-byte Default root each and the same quad1. Original immutable scalar-reader execution agrees across137 inputs/28 scalar bytes, including quad0 mutations;12 malformed source-authority cases are rejected. E011AU independently proves the live source-to-retained lineage.

The full E011AS composer/E011AR preflight now passes using this source flag. A deliberately invalid cold input byte255 must be overwritten by the C decoder before binding. GCC/Clang ASan/UBSan each pass510,374 assertions, with packet differences0/0/0/0. Captured cold AEC weights and normal semantic inputs remain in use. No new kernel build or runtime action occurred.

Closure is bounded to this scalar and three qualified Default roots: exact loaded tuning filename, full aggregate deserialization and whole-profile materialization remainOPEN. Metadata/name/security/allocation helpers are stubbed in the owned-memory scalar fixture; the aggregate tail is excluded. Do not promote this to complete bootstrap or Linux optical parity. Protected Golden boot25999320-3114-4f2c-bbce-a6335b0e2046 and all three payload hashes are unchanged; camera remains idle.

NEXT independently derive cold AEC weights, resolve RS normal count/offset policy authority and source-selection requirements, then final deterministic startup preflight and independent WM16 same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement proof. Native rear Linux runtime remainsDENIED. Do not repeat the verified AWB writer/GetParam2 copy or hardcode1. See experiments/E004-front-ir-vd55g0/e011av-rear-source-cold-awb-quad/README.md, SCALAR-SAFE, INTEGRATION-SAFE and RESULT. Raw tuning/originals remain private on SP11.

## E011AU named AWB configuration writer — LIVE PASS / GOLDEN RETURNED

Fresh Run B E011AU-20260930-2327B completed one successful Start, 713 valid rear4K handles and clean Stop. The actual original DeviceMFT module was qualified at its load event with three exact code ranges before the CreateAWBAlgorithm probe was armed. Create/configuration occurred during StartAsync, after InitializeAsync completed: the earlier pre-Init timing hypothesis is corrected.

Three events match the same thread/actor. All92 retained BG bytes are stable from create-call to lookup return; quad is0 before population. The selected bgStatsConfigV1 source remains byte-identical across96 bytes, has quad1 at source+20, and the retained actor has1 at+FB798 after the source-identified store688290. Nine private records/716 bytes validate with zero capture-command diagnostics. This closes the live named-config-to-retained-field lineage for the sampled startup, NOT independent source-profile materialization or complete deterministic bootstrap.

Run A is consumed/inconclusive without START.GO; both idle manually started FrameServer hosts were replaced before actual initialization. Fresh B used immediate gate release (0.130029s after debugger readiness), then a module-load qualification hold. B user-mode CDB detached/exited0 and manual task was removed. Normal reboot returned protected Golden Linux7.1.5-sp11-render-parity-v4+, boot25999320-3114-4f2c-bbce-a6335b0e2046, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle; all three Golden payload hashes unchanged.

NEXT independently derive/materialize the selected bgStatsConfigV1 source profile (never hardcode1 or use captured source bytes as producer inputs), independent AEC cold weights and RS count/offset authority, then final full startup preflight and independent WM16 same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement proof. Native rear Linux runtime remainsDENIED. Do not repeat the verified GetParam2 copy or SetParam exclusion, reuse either AU identity or activate any rear candidate. See E011AU README, RESULT, VALIDATION-SAFE and validate-private.py. Raw records/originals stay private on this SP11.

## E011AU pre-Init AWB writer — RUN A INCONCLUSIVE / FRESH RUN B PREPARED

Run A E011AU-20260930-2000A initialized the original rear camera but never released START.GO. The manually started FrameServer service twice terminated/replaced its idle host; the actual DeviceMFT owner initialized outside the attached process, so no writer event was captured. Both user-mode CDB sessions detached/exited0, the manual task was stopped/removed, and normal reboot returned protected Golden boot c0667dd5-a17d-4531-8fd1-21e20530deb2. No first-writer/value-policy closure is claimed.

Fresh Run B E011AU-20260930-2327B shortens the idle window: prepare holder first, then start FrameServer and attach user-mode CDB, release enumeration and initialization immediately after debugger readiness, and qualify the original loaded module at its load event before arming the CreateAWBAlgorithm probe. No same-boot camera retry. Static exact writer and original source hashes remain valid; native rear Linux runtime stays DENIED. See E011AU README, RUN-A-SAFE and PREPARE-B-SAFE. Run A is consumed.

## E011AT AWB SetParam retained BG — CALLBACK EXCLUDED / GOLDEN RETURNED

One original Windows rear 4K run completed 714 valid handles, one successful Start and clean Stop. User-mode CDB explicitly detached/exited0 and the manual task was removed. The live original CAWBMain::AWBSetParameter callback is RVA68C090 through wrapper+28 -> actor+0 -> vtable+08; its same-thread return result is0 and the40-byte parameter record matches the outer call.

The actor's92-byte retained BG already has quad1 at callback entry and remains byte-identical through callback return, outer return, pre-GetParam2 and the later sampled helper689228. Publication5000001D/size128 and first request1 consumer carry1. Thus callback68C090 is not the cold initializer. The generated outer handler had one excess dereference, so its outer object/code/IO dumps are excluded; the chain was corrected while the same call remained held. The ARM64 data watch had no free slot and was removed, so no first writer is claimed.

NEXT bracket the wrapper from entry681C40 through pre-dispatch83180C, then construction/configuration if quad is already1 at wrapper entry. Do not repeat68C090 or hardcode1. Golden Linux7.1.5-sp11-render-parity-v4+ boot25a899ad-ae69-418f-86fb-d110b5bd84d0 is idle, saved FullIOv19c, next_entry empty and NTFS unmounted. Cold AEC weights, exact AWB retained initialization, RS count/offset authority, final bootstrap and WM16 retirement proof remainOPEN; native rear runtime DENIED. See [E011AT](experiments/E004-front-ir-vd55g0/e011at-rear-awb-setparam-retained-bg-observer/README.md), VALIDATION-SAFE and RESULT. Identity consumed.

## E011AS explicit inactive cold gamma — OFFLINE / ARM64 BUILD PASS

The cold gamma gate is now closed for the bounded four-packet startup. Four additive provider derivatives and a kernel-compilable producer express inactive gamma without a dummy table. Cold selector2 production is skipped/rejected, normal gamma remains required, and packet/register/activity contradictions fail closed. The actual full composer and E011AR preflight use the explicit absence producer.

GCC/Clang ASan/UBSan each pass510,371 assertions with zero differences0/0/0/0. Nine activity negatives,38 atomic policy negatives,32 nonzero inactive-LUT negatives and9 producer-failure zeroing cases pass. Fresh isolated ARM64 W=1 v2 build haszero warnings; moduleSHA41d169f5d5d9f24cf429a6e922eca49899a5c60b9034965ea9810da97935959e, separately hash/vermagic checked via Fabric. First build preparation failed before compiler due to a host-only seed dependency; v2 is separate. Both builders/preparer consumed. No install/load/runtime/reboot/sleep/MMIO; Golden bootc0e263ed-7319-4f69-8f10-4d51f20cd1a1 remains idle.

NEXT remaining deterministic startup policy origins: E011AQ retained AWB BG initialization, AEC cold weights and RS count/offset authority. Then final full bootstrap/preflight and independent WM16 same-generation IRQ/IOVA/DMA/IOMMU retirement proof. Do not reopen the inactive cold gamma gate or repeat the closed GetParam2 copy. Native rear runtime DENIED; no live optical improvement claimed. See [E011AS](experiments/E004-front-ir-vd55g0/e011as-rear-explicit-inactive-cold-gamma/README.md), INTEGRATION-SAFE, BUILD-SAFE, AUDIT-SAFE, BUILD-ATTEMPTS-SAFE and RESULT.

## E011AR packet-isolated Linux runner — BUILD-ONLY PASS

The new unreachable runner now consumes four E008o packet semantic records and Linux-owned command backing, replacing the archived shared-state runner shape. Materialization completes before owner acquisition/exposure; exposed commands are never rewritten. The consumed wrapper pins uncertain DMA and requires reboot after exposure. Partial RT-CDM/BUS/CSID/CSIPHY/sensor starts enter conservative emergency-stop paths before the attempt.

GCC/Clang sanitizer lifecycle tests each pass4,091 assertions with58 injected failing operations; these providers simulate hardware contracts. The exact preflight with the real composer each passes510,045 assertions and zero differences0/0/0/0. Fresh isolated ARM64 W=1 build haszero warnings; moduleSHA5545aaff892fb87eade9be4e1168f391b6cc76dab9ccd88aa213fec4b0f31604, separately hash/vermagic checked through Fabric. No install/load/runtime/boot/sleep/MMIO change. Golden bootc0e263ed-7319-4f69-8f10-4d51f20cd1a1 remains idle. Builder/preparer consumed.

NEXT complete deterministic startup policy origins (E011AQ upstream retained BG, AEC weights, RS count/offset authority) and explicit inactive cold gamma, then final integrated preflight audit and independent WM16 same-generation IRQ/IOVA/DMA/IOMMU retirement proof. Native rear runtime DENIED; do not activate the candidate or old E008n shared-state runner. See [E011AR](experiments/E004-front-ir-vd55g0/e011ar-rear-packet-isolated-runner/README.md), LIFECYCLE-SAFE, INTEGRATION-SAFE, BUILD-SAFE and RESULT. This checkpoint changes integration code; Linux optical/image quality remains unproven.

## E011AQ AWB delegate/retained BG — LIVE COPY VERIFIED / GOLDEN RETURNED

One Windows run completed 711 valid4K frame handles, clean Stop, explicit CDB detach/exit0 and task removal. Five outer probes resolved before Start; three inner probes resolved after manual qualification, before the same GetParam2 call. Eight events/26 private records/2720 bytes validate. Two mistaken pre-capture input-as-list qualification queries are retained; corrected output1 capture has zero diagnostics. No camera retry or unattended qualification claim.

Actual original callback68E5A0 (CAWBMain::AWBGetParameter) and all six vtable targets are byte/source verified. Retained actor BG+FB744 already has quad1 at+FB798 before GetParam2. PopulateOutput68F490 returns0 at68E8D8 and copies all92 retained bytes into previously zero IO+CB4; outer return/publication/first cold request1 agree. Nested channel is output1/type1/16-byte container ->15 descriptors atIO+2080 ->BGindex5/type5/92 bytes. Input2/type2/12 bytes is a separate information record.140 original owned-memory BG copy slices preserve full u32/source/neighbors; full algorithm emulation return is not claimed.

NEXT trace upstream retained BG initialization: source SetParam wrapper681C40 -> actor/vtable slot08 ->68C090; tuning/mode helper689228 references bgStatsConfigV1. SetParam IO preservation does not exclude retained-record writes. Trace registration/configuration/construction and bracket retained BG there; do not repeat GetParam2 copy or hardcode1. Numeric initialization policy/full bootstrap/WM16 retirement OPEN; native rear runtime DENIED.

Golden boot c0e263ed-7319-4f69-8f10-4d51f20cd1a1, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. No production C/build/Linux runtime/kernel debug/BCD/MMIO change; offline parity remains0/0/0/0 conditional on input records. See [E011AQ](experiments/E004-front-ir-vd55g0/e011aq-rear-awb-delegate-bg-observer/README.md), VALIDATION-SAFE, COPY-SAFE, SOURCE-SAFE and RESULT. Identity/builders consumed.

## E011AP earlier AWB calls — GETPARAM2 TRANSITION VERIFIED / GOLDEN RETURNED

One Windows run completed866 valid4K frame handles, clean Stop, explicit user-mode CDB detach/exit0 and task removal. Eight resolved one-shot probes ran; GetParam2 deliberately stopped for qualification. No capture diagnostics occurred. Quad stayed0 and all92 BG bytes stayed identical through SetParam; GetParam2 at831920/831924 returned0 on the same thread/processor, changing29 bytes and setting quad1. Its after record equals pre-selector12 across92 bytes; publication and first cold request1 carry1. Numeric value policy remainsOPEN.

Delegate correction: wrapper+28 -> object+0 -> vtable+10. The direct object+10 target read is excluded; input descriptors are16 bytes, so the extra40-byte input-table tail is also excluded.18 files/1824 bytes yield17 valid source records/1656 bytes. Both original wrapper targets match128 bytes. Captured object points to original vtable133A390; pinned source candidate GetParam68E5A0 is CamX::CAWBMain::AWBGetParameter, not yet live callback-code verified. Next capture the actual slot/code and nested type2/12-byte input payload, then trace retained BG initialization. Do not hardcode1.

Golden bootf4982efd-f612-4819-b1f5-de4820807375, saved FullIOv19c, empty next_entry, NTFS unmounted, camera idle. No production C/build/Linux runtime/kernel debug/BCD/MMIO change. Offline parity remains0/0/0/0 conditional on source inputs. Exact cold value policy/full deterministic bootstrap and independent WM16 retirement OPEN; native rear runtime DENIED. See [E011AP](experiments/E004-front-ir-vd55g0/e011ap-rear-awb-earlier-call-observer/README.md), VALIDATION-SAFE, ORIGIN-SAFE and RESULT. Identity/builders consumed.

## E011AO AWB initialization — LIVE ORIGIN NARROWED / GOLDEN RETURNED

One original Windows capture completed 859 valid 4K frame handles and a clean Stop. Both user-mode CDB sessions explicitly detached/exited 0; the manual-only task was removed. The actual driver owner had five resolved probes before Start after FrameServer replaced its initial process.

Quad was already 1 before initialization selector12 at 0x831964. Its same-thread/processor return at 0x831968 preserved all 92 BG bytes; publication and four consumers (request IDs1/1/2/3) carry1. The actual target is original CamX::AWBGetParam RVA 0x681B00; 128 captured instruction bytes match the pinned image. The delegate object is wrapper+0x28, callback slot+0x10, not captured by the 32-byte wrapper header. Selector12 is excluded as this invocation's origin; exact earlier writer/value policy remainsOPEN.

14 records/1324 bytes were retained privately; one auxiliary publication-node BG read has wrong object attribution and is excluded, leaving 13 source records/1232 bytes. Conditional pair/publication probes required direct control; this run does not qualify unattended observer behavior. A queued post-Stop informational query had an unresolved symbol; capture records remain valid. No retry/kernel debug/Linux camera/build/MMIO/submission occurred.

NEXT bracket the earlier SetParam 0x83180C/GetParam2 at 0x831920 and identify the underlying wrapper delegate; nested expected-output inputs may carry BG writes even when selector2 lacks a direct BG output. Keep all value-policy, cold-gamma/full-bootstrap and independent WM16 retirement gates open; native rear runtime DENIED. Golden Linux boot 68454cbe-a55e-430c-8699-206bf84435bb, saved FullIOv19c, next_entry empty, NTFS unmounted, camera idle. See [E011AO](experiments/E004-front-ir-vd55g0/e011ao-rear-awb-init-algorithm-observer/README.md), VALIDATION-SAFE and RESULT. Never reuse the consumed Windows identity or prior builders.

## E011AN cold BG origin boundary — ORIGINAL OWNERSHIP PASS / PARITY UNCHANGED

The original AWB descriptor helpers expose a 92-byte BG algorithm output at IO+0xCB4 while preserving its contents. GetParam selector 12 uses output index 10/type 10; selector 2 does not expose BG. Initialization call/return RVAs 0x831964/0x831968 now identify the next concrete upstream boundary. FillBG carries the full IO+0xD08 field to record+0x4C; it does not generate the value. 184 original ARM64 calls pass in owned memory across four IO bases. This source boundary is NOT a physically trapped first writer or a closed numeric policy.

Full E011AM regression passes again: GCC and Clang ASan/UBSan each 509,829 assertions; semantic differences remain 0/0/0/0, and prior reports are byte-identical. No production C or kernel build changed. Initial AEC weights/AWB quad policy, normal RS/AFD count policy, whole-frame offset authority, explicit inactive cold gamma, complete deterministic bootstrap and independent WM16 generation-safe retirement remain OPEN; native rear runtime DENIED.

NEXT observe the bounded AWB selector 12 call and actual algorithm owner privately, then trace its first write/policy inputs and the independent AEC Usecase producer. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. No camera/boot/sleep/MMIO/submission occurred. See [E011AN](experiments/E004-front-ir-vd55g0/e011an-rear-cold-bg-origin-audit/README.md), ORIGIN-SAFE, VALIDATION-SAFE and RESULT. Previous builders remain consumed.

## E011AM full offline startup comparison — ZERO DIFFERENCES / ARM64 BUILD PASS

Portable integer RS production now removes all seven remaining differences. Both original ARM64 adjustment and clean C match4,387 cases/35,096 fields per compiler; all three sampled pack shifts match original state+0x130. The detached binder preserves caller tags and unrelated modules, with70 binder and14 producer negatives. RS source schedule is0/1/2/2; all12 present RS register instances match.

The full four-phase provider replay now has zero semantic register differences:[0,0,0,0]. Prior BG, weights/quad, scalar, BF ROI/gamma, BPC and LSC/GTM/GIC checks remain exact. GCC and Clang ASan/UBSan each pass509,829 assertions. A fresh isolated ARM64 W=1 build has zero warnings, moduleSHA85c318c424d5b3380f884c2e28893dbe28d49c233c4d0874de9a95cd058a3d25, never installed/loaded.

This is offline parity conditional on independently observed semantic inputs. Cold BG weights/quad initialization, normal RS/AFD count policy and whole-frame zero-offset authority remainOPEN. Stripe policy is unsupported. Complete deterministic E008o bootstrap without observed caller inputs, explicit inactive cold gamma policy and independent WM16 same-generation IRQ/DMA/IOMMU retirement remainOPEN. Zero numeric differences do not authorize live rear ISP; runtime staysDENIED.

NEXT source-close the remaining caller-policy origins and inactive cold gamma before composing a complete deterministic bootstrap; independently prove WM16 retirement before any live rear ISP run. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. No camera/boot/sleep/MMIO/submission or platform change. See [E011AM](experiments/E004-front-ir-vd55g0/e011am-rear-rs-full-startup-integration/README.md), RESULT, ARITHMETIC-SAFE, INTEGRATION-SAFE and BUILD-SAFE. E011AM and all prior one-use builders remain consumed.

## E011AL Bayer-grid weight/quad integration — PRIVATE PARITY AND ARM64 BUILD PASS

Portable integer L4 quantization now produces AEC Q4 luminance weights and the AWB quad flag from E011AK semantic input records. Both original ARM64 pack functions match2,164 cases/8,656 fields per sanitizer compiler, including exact rounding boundaries. The detached binder validates both source identities and every caller startup tag before mutation;35 binding and22 producer negatives preserve output/state. It changes only AEC weights and AWB quad.

The full composer now matches all four previously different weight/quad register instances. Remaining differences drop11->7, by phase1/3/3/0, exclusively RS_STATS14. Prior36 BG geometry/threshold and26 scalar register instances, BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. GCC and Clang ASan/UBSan each pass509,582 assertions. A fresh isolated ARM64 W=1 build passes zero warnings, moduleSHA1b510b04dd119bd5c1e978b54829794bf02e7f0447c79f960e3e829cc0934f10, not installed or loaded.

Cold weights/quad are caller-owned observed consumer inputs: their initialization policy is stillOPEN. Normal producer field handoffs are source-verified. Later holds are detached state only because packets2/3 do not emit BG ranges. Complete source-produced E008o startup, explicit inactive cold gamma policy and independent WM16 same-generation retirement remainOPEN; native rear ISP DENIED. No Linux camera start, boot/sleep/MMIO/submission or platform change occurred.

NEXT source-close normal RS count policy and exact shift binding, implement portable RS production and require zero remaining differences. Cold weight/quad initialization authority also remains required for complete bootstrap. Golden boot b74c0760-83bb-421f-ac4d-1efa4e297294 stays idle, saved FullIOv19c, next_entry empty, NTFS unmounted. See [E011AL](experiments/E004-front-ir-vd55g0/e011al-rear-bg-weight-quad-integration/README.md), RESULT, ARITHMETIC-SAFE, INTEGRATION-SAFE and BUILD-SAFE. Never rerun the consumed E011AL or previous one-use builders.

## E011AK Windows statistics inputs — VALIDATED, PORTABLE INTEGRATION NEXT

Fresh consumed E011AK-20260930-1025A completed one Start/Stop with860 valid4K handles. Nine probes resolved to the actual DeviceMFT owner before Start;49 bounded input events/106 private files were verified. Original ARM64 arithmetic privately reproduces40 BG geometry/threshold fields and21 RS count/color/region/offset fields. Eight AEC producer snapshots match24 normal weight fields; eight AWB producer snapshots match8 quad fields. Producer request labels are last observed IFE hooks, not independent AEC/AWB request identities.

Sixteen captured gain inputs are unity: E011AJ's live gain binding is closed for this sampled startup window. RS horizontal count changes at the second request1 consumer, then vertical count at request2, holding through sampled request7. RS color conversion is separate from module enable. Cold weights/quad initialization origin, normal RS count policy producer and exact RS shift binding remainOPEN. The full composer has not changed:11 differences by phase3/5/3/0 remain. Do not reuse a frozen RS config or infer policy inputs from retained registers.

CDB explicitly detached/exited0 and the manual-only task was removed. An initial literal Ctrl-C cleanup line had a syntax error; the clean second command cleared breakpoints and detached. Normal reboot returned Golden Linux7.1.5-sp11-render-parity-v4+, boot b74c0760-83bb-421f-ac4d-1efa4e297294, saved v19c, next_entry empty, camera nodes/modules/processes absent. Read-only NTFS recovery is unmounted. Raw records/logs/addresses remain private on SP11; no optical pixels saved. No new kernel build, install, Linux camera start or kernel debugging.

NEXT source-close cold weights/quad and the normal RS count/shift handoff, produce portable inputs and require zero remaining differences in the full private composer. Prior source provenance remains established. Complete E008o startup, explicit inactive cold gamma policy and independent WM16 retirement remainOPEN; native rear ISP DENIED. See [E011AK](experiments/E004-front-ir-vd55g0/e011ak-rear-stats-input-observer/README.md), RESULT and VALIDATION-SAFE. Windows identity and previous E011AJ builder are consumed.

## E011AJ BG geometry/threshold full integration — PRIVATE PARITY / ARM64 BUILD PASS

New bounded portable C11 L4 AEC_BE/AWB_BG geometry and threshold production uses the existing E011B cold crop seed, E011N normal AEC frame control and E011Q prerequest AWB record. Original shared Titan680 capability execution verifies region limits16..512, max64x64 grid and18-bit thresholds. Both sanitizer compilers match2,056 original AEC/AWB arithmetic cases/20,560 fields privately; only clean C results enter the detached integer L2 binder. The actual full composer now matches all36 present BG geometry/threshold register instances. Remaining semantic differences drop25->11, by phase3/5/3/0: AEC Q4 luminance weights(two), AWB quad synchronization(two), RS config(seven). Prior scalar/BF/BPC/LSC/GTM/GIC comparisons remain exact.

GCC+Clang ASan/UBSan each pass509,427 assertions with90 new binding and14 producer negatives. New isolated ARM64 W=1 build passes zero warnings, moduleSHAa763e03440cf2fce81a89e338b90867cd3df5fbea4129492e8d8535e049bab71, not installed/loaded/called. The threshold gain policy is unity only; independent live binding of request trigger+0x44 remainsOPEN. Later BG holds are detached design state (packets2/3 do not emit these register ranges). E011H request+0x80 is source-confirmed RS color conversion, separate from module enable; normal RS transitions still need audit. Full source-produced E008o composition, explicit inactive cold gamma policy and independent WM16 retirement remainOPEN; native rear ISP DENIED.

NEXT independently source the remaining weights/quad/RS/gain inputs and require all11 remaining differences to vanish in the full private replay. Preserve prior established provenance. Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 stayed idle; no camera/boot/sleep/MMIO/submission. Read-only Windows NTFS inspection is unmounted. See [E011AJ](experiments/E004-front-ir-vd55g0/e011aj-rear-bg-geometry-threshold-integration/README.md), BG-SAFE, INTEGRATION-SAFE, BUILD-SAFE and RESULT. Never rerun the consumed one-use builder.

## E011AI clean neutral scalar full integration — PRIVATE PARITY / ARM64 BUILD PASS

Recovered the original E011X input trace privately from SP11 Windows with exact trace/holder/corpus hashes; Windows NTFS was read-only and is unmounted. A strict parser verifies all 32 events/eight samples, coherent PDPC/WB AWB inputs and the cold/request1/request2/request3-hold ordering. New portable C11 L4 arithmetic is independent of Windows; both sanitizer compilers match 1,038 original ARM64 arithmetic cases / 10,380 scalar fields privately. PDPC near-zero denominator correctly yields minimum128, not unity4096. Only the clean C-produced results bind to L2, with source IDs0/1/2 and schedule[0,1,2,2]; caller IDs remain separate.

The actual E011AG/E011AH full composer matches all26 present scalar register instances (8/8/8/2). Remaining semantic differences are reduced from51 to25, by phase3/19/3/0, exclusively AEC_BE/AWB_BG/RS statistics. BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. GCC+Clang ASan/UBSan each pass509,118 assertions with32 composition,61 AF,69 scalar binder and69 scalar producer negatives. New isolated integer-only ARM64 CAMSS W=1 build passes zero warnings; moduleSHAbe35b2da4905b63549a4fef65f89f0299f46f4bc79404c7a720a278648113c5b, not installed/loaded/called; no user-space float producer enters the kernel. Existing source/live provenance gates are not reopened.

NEXT lower the already established statistics geometry/threshold/weight/black-level/RS handoffs into portable bases and require full private parity. Cold gamma remains explicit unused host-only completion. Optional WB normalization/other Bayer policies are outside this bounded rear slice; no full AE/AWB/AF algorithm port is claimed. Complete source-produced E008o startup composition and independent WM16 safe retirement remainOPEN; native rear ISP DENIED. Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 stays idle; no camera/boot/sleep/MMIO/submission. See [E011AI](experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/README.md), SCALAR-SAFE, INTEGRATION-SAFE, BUILD-SAFE and RESULT. Recovered original authority is /home/geoca/Documents/SP11-PROJECT/06-camera/private/E011X-source-recovered; keep it private on SP11. Never rerun the consumed one-use builder.

## E011AH request AF/BF ROI full integration — PRIVATE PARITY / ARM64 BUILD PASS

The accepted source AF rectangle/BAF adjustment now runs through the actual E011AG four-packet composer. A new integer-only detached handoff validates all three normal request/phase tags and geometry before mutation; packet0, ROI IDs/flags/gamma and all other fields are preserved. GCC+Clang ASan/UBSan each pass508,760 assertions,32 inherited negatives and61 new AF negatives. All16,385 bounded one-fifth dimensions and18,157 odd/even maps agree with the original float source helper. Private full-path BF selector1 matches300/300 bytes in all4 phases; normal selector2 matches128/128 in all3 phases. Neutral first-zoom control remains250/300. New isolated ARM64 W=1 build haszero warnings; moduleSHA9f1de3bb49cbc47b8a8a8b52e8d8a59c97ea511781cd98107e0006aaa6ccf760, binder/recipe retained, not installed/loaded/called.

This closes the bounded request-specific BF ROI propagation/parity seam, not an AF algorithm or newly tagged live AF-to-RT-CDM identity. Replay uses existing independently measured E009e first-normal zoom0x3f7f3f0f, then1.0; upstream zoom calculation remains unproven. Neutral scalar/statistics bases still have11/27/11/2 semantic register differences by phase and need source-owned producer lowering; prior E011X/E010Z/E011A–R/E011T–W provenance remains closed. Cold gamma remains an explicit unused host completion (enable0, selector2 absent). Complete source-produced E008o composition and independent WM16 same-generation IRQ/DMA/IOMMU safe retirement remainOPEN; native rear ISP DENIED. Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 stayed idle, no camera/boot/sleep/MMIO/submission. See [E011AH](experiments/E004-front-ir-vd55g0/e011ah-rear-request-af-roi-full-integration/README.md), RESULT, INTEGRATION-SAFE and BUILD-SAFE. Never rerun the consumed one-use builder.

## E011AG full real-provider startup integration — OFFLINE / ARM64 BUILD PASS

The four-packet path now runs 34 actual provider/contract includes, actual recursive E008o validation, actual E008l layout and complete E007y materialization. GCC+Clang ASan/UBSan each pass 1,872 assertions and 32 negatives; all 2,268 register positions and 46 DMI identities match corpus shape. Source BPC retains all21 present words; four LSC/four GTM/three GIC payloads propagate exactly. New composer validates the full register-family union, rejects aliasing/exposed/submitted/malformed arenas, and clears all accepted-domain incomplete output. Caller request IDs100/101/102/103 are explicit fixtures, separate from source requests0/1/2. A fresh isolated ARM64 CAMSS W=1 build passes zero warnings; composer/recipe retained, module SHA6ed7738dcc2ba1a197e162e8b4cff1ca5fb98492ed90bde98703799ce9f4d488, not installed/loaded.

This closes integration mechanics, NOT complete source-produced startup bases. Neutral scalar/statistics inputs remain host fixtures (11/27/11/2 mismatched semantic words by phase); previously closed E011X/E010Z/E011A–R/E011T–W provenance gates are NOT reopened. Normal BF ROI still needs its accepted request-specific adjustment through the integrated DMI path. Cold BF gamma is disabled/selector2 absent, while generic validation needs an explicitly completed unused gamma state; host completion is not a Windows producer policy. Static flat GTM replay now proves grid independence and needs no private normal-TMC domain file. NEXT lower existing source-owned scalar/statistics handoffs into four portable bases, then full register/DMI parity. Independent WM16 same-generation IRQ/DMA/IOMMU retirement remains OPEN; native rear ISP DENIED. Idle Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 is unchanged; no camera, boot, sleep, MMIO or submission. See [E011AG](experiments/E004-front-ir-vd55g0/e011ag-rear-full-provider-startup-integration/README.md), RESULT, INTEGRATION-SAFE and BUILD-SAFE. Do not replay the consumed one-use build.

## E011AF startup AEC/context -> shared object -> source BPC — LIVE/PRIVATE C BINDING PASS

Fresh RunB completed 705 valid rear 4K handles and 250 private files. The startup AEC/context-to-BPC shared-object binding is closed: 16 gain fields, 16 sensitivity fields, 48 generic scalars, 321 region fields, 90 common scalars, 15 anchors and 21 retained startup words match source production. Actual BPC function 0xA08850 owns builder/interpolation/common caller RVAs 0xA08DCC/0xA08DFC/0xA08E38. The gain hook's global log tag precedes the atomic request hook in four transitions; bind using observed hook order, object identity and unchanged semantic inputs. The real E011AE C binder/E007a provider passes four independent packet states and 28 words with schedule [0,1,2,2], explicit host fixture IDs [4,5,6,7], and unready/unsealed output. Full recursive E008o validation is not exercised by the host shape adapter. Snapshot metadata/full AEC are not newly ported; the cold seed uses invariant Default leaves, with no zero-vector policy inferred. RunA's 711 handles remain an incomplete upstream result, followed by Golden return before fresh RunB. RunB's WinDbg register alias was repaired from @x30 to @lr in the same held session; no second StartAsync or camera retry occurred. Both tasks were removed and debugger cleanup used normal reboot after Stop. Current idle Golden boot is 208d6c65-0103-40e2-8ff4-fa25395f2534; NTFS is unmounted. Next compose the remaining independent E008o base objects and run full recursive packet validation. Independent WM16 same-generation IRQ/DMA/IOMMU retirement remains OPEN; native Linux rear ISP remains denied. See E011AF README, RESULT and LIVE-VALIDATION-SAFE.

## E011AF live upstream AEC/BPC lineage — RunA PARTIAL, corrected RunB PREPARED

Fresh RunA E011AF-20260929-2235A completed711 valid4K handles/106privatefiles and cleanStop;16source gain events/67snapshot returns/3startup output groups observed, but oldCALC/GEN hooks0, so upstream object lineage remainsOPEN. GENoldhook897dc0wasnull-path return; source positiveepilogue897d6ccorrected. Builder890208 now filtersactual[2,5,1] and recordsdirect sharedvector identity pluscaller RVAs to identifyactualBPCproducer; no ISP base guessed. Taskremoved/rebootGolden c04ce22e-b7f9-416c-a5b3-34b354cd7772;NTFSprivatecopyread-onlythenunmounted. Corrected freshRunB E011AF-20260930-0535B prepared, notconsumed. No samebootretry. NativeLinuxrearISPdenied, completeE008o/independentWM16retirementOPEN. See E011AF README/RUN-A-SAFE.json.

## E011AE rear request generic triggers and offline BPC startup binding — SOURCE/HOST PASS, LIVE UPSTREAM OPEN

Source type IDs2/5/1 are DRC gain / mid-short sensitivity ratio / selected AEC sensor linear gain; the terminal type1 is not exposure time or post-sensor dGain. Independent explicit-context producer passes674 original-fragment cases (2022 scalars),1348 full native interval/blend/common chains (4044 decisions,144236 region fields,40440 common scalars) and9436 exact words through actual C E007a. Snapshot metadata context is caller-owned; separately observed IPE QLL override rejected; no actual live node/context guessed. Cold BPC common is independently source-produced from invariant Default leaves, without assuming initial gain. New offline BPC binder validates four caller-owned E008o packet identities, installs schedule0/1/2/2, preserves unrelated state, leaves all packets unready and set unsealed; host20 rejects/no partial mutation pass. Full recursive E008o DMI validation not exercised. No new Windows camera run, kernel build/load, camera/MMIO/DMI/RT-CDM/IR/suspend/boot change. Idle Golden FullIO v19c boota6a56cbc-7618-43e0-b77c-297ece7ff69d, Windows NTFS unmounted. NEXT: live upstream AEC/context/override-to-actual-BPC startup binding, then remaining E008o base composition. Independent WM16 same-generation IRQ/DMA/IOMMU retirement remains OPEN; native rear Linux ISP denied. See experiments/E004-front-ir-vd55g0/e011ae-rear-request-generic-trigger-producer/README.md and safe JSON.

## E011AD rear BPC source exposure interval and startup scalar bridge — LIVE PASS

Independent source interval selection passes593 inputs /1779 exact original helper comparisons. Fresh Windows RunB captured nine actual nested trigger vectors with type IDs2/5/1 and completed714 valid4K handles. Source tuning + mode selectors + the observed input scalar reproduce all three startup regions (321 fields), common outputs (90 selected scalars), reserve anchors (15) and retained phases0/1/2 register words (21). Root IDs remain Default0x1a then Sensor1 Video0x100. No captured region/register bytes enter the producer. Actual runtime leaf ordinals are not directly observed; source reconstruction and full output bridge pass. Upstream request trigger1 scalar production remains caller-owned/open, as do complete E008o per-packet composition and independent WM16 same-generation IRQ/DMA/IOMMU retirement. RunA711 handles/zero captures was unbound and inconclusive, recorded and returned to Golden before fresh RunB; no same-boot retry. Both tasks removed, debugger cleaned by normal reboot after Stop, back on idle Golden FullIO v19c boota6a56cbc-7618-43e0-b77c-297ece7ff69d; NTFS unmounted. Native rear Linux ISP denied. Next: shared request trigger1 scalar provenance, then remaining startup base-object assembly. See experiments/E004-front-ir-vd55g0/e011ad-rear-bpcabf411-trigger-interval-selector/README.md and safe JSON results.

## E011AC rear BPCABF411 source tuning selection — ROOT/RESERVE/BLEND CLOSED, TRIGGER INTERVAL OPEN

Fresh single-session Windows rear4K Start/Stop delivered 713 valid handles. Direct root IDs at cold/request1/request2 are 0x1a/0x100/0x100: Default then Sensor1 Video. The independently parsed source selector paths resolve both live mode vectors; 15 serialized/runtime reserve anchors match. Independent 107-field blending uses binary64 intermediates with final binary32 rounding and matches 235 original-source cases (25,145 fields). All three selected-root live regions match source leaves (321 fields); the whole cold region is independently producible because all six Default leaves are identical. Active exposure interval/ratio policy remains OPEN: captured 72-byte vectors contain nested pointer triplets, not numeric trigger contents. One observer syntax pause was repaired in the same held session, with no camera retry; generator corrected. Task removed, debugger cleaned by normal reboot after Stop, returned to idle Golden FullIO v19c. Complete E008o composition and independent VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement remain open; native rear Linux ISP denied. Next: exact nested trigger selection, then remaining per-packet base-object composition. See experiments/E004-front-ir-vd55g0/e011ac-rear-bpcabf411-tuning-selection/README.md, RESULT.json and VALIDATION-SAFE.json.

## E011AB rear BPCABF411 startup input bridge — LIVE SELECTED ARITHMETIC CLOSED

Fresh Windows rear4K Start/Stop delivered 712 valid handles. Independent E011AA calculations match all eight live selected common outputs (240 scalars) and seven register words in each retained startup phase 0/1/2 (21 matches). Actual BPC schedule: cold pre-request, request1 recalculation, request2 recalculation, request3 hold; two distinct selected semantic states. This differs from LSC/GTM: preserve each module schedule. Actual bounded request coverage was 22 because MASM parsed 16 as hex; generator now uses explicit 0n16. First unbound observer run was inconclusive and never retried on that boot. Both tasks removed; SP11 returned to FullIO v19c Golden, camera idle. Runtime tuning-root/leaf selection and serialized reserve structural mapping remain open, as do complete E008o four-packet composition and independent VFE1 WM16 same-generation IRQ/DMA/IOMMU safe retirement. Native rear Linux ISP runtime remains denied. See experiments/E004-front-ir-vd55g0/e011ab-rear-bpcabf411-startup-input-binding/README.md, RESULT.json and LIVE-VALIDATION-SAFE.json. Next: source-generated selection/interpolation and remaining E008o base-object binding.

## E011AA rear BPCABF411 common producer — OFFLINE ARITHMETIC CLOSED, REQUEST INPUT BINDING OPEN

An independent semantic-input producer now calculates E007a's seven BPC/ABF411 words. 149 native-source arithmetic differential cases pass; all 22 retained seven-register records, including three startup records, match clean-produced installed-leaf candidates (154 register matches). Candidate output coverage does NOT prove runtime leaf selection or packet/request binding. Rear Sensor-specific tuning differs from Default; exact interpolated common inputs, reserve runtime mapping and request-phase provenance are the next narrow Windows observer gate. The separate E007u DMI provider is already closed. Complete E008o four-packet composition and VFE1 WM16 same-generation IRQ/DMA/IOMMU safe retirement remain open; native rear ISP runtime remains denied. No module build/load, camera/MMIO/DMI/RT-CDM access or boot change. Current engineering checkout: /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean. See experiments/E004-front-ir-vd55g0/e011aa-rear-bpcabf411-common-producer/README.md and RESULT.json.

## E011z rear startup clean LSC/GTM replay — OFFLINE SOURCE REPLAY CLOSED, E008O ADAPTIVE BINDING DEFINED

SP11 Linux now reproduces the two Windows/E006B startup LSC states entirely from the clean rear/default OV13858 authority: cold CCT 0 selects the first lower-CCT child by the exact LSC411Interpolation below-first rule and produces phase-0 selector hashes c5a990dc.../ed004c38...; CCT 5000 selects leaf 0x2a0 and produces phase-1 d8c34f9f.../efa6f261.... Selector3 is the proven zero payload and phases2/3 contain no LSC DMI, holding phase1 only for recursive validation. Startup GTM is source-generated from the pre-valid-TMC static 257x4096 region through the clean Titan680 packer, exactly reproducing b71d4b3e... for all four phases; normal valid-TMC processing begins at request4. The E008o adaptive binder preserves caller-supplied per-packet materializer IDs and passed a structural compile/run test with IDs 4/5/6/7. No Windows DMI bytes are producer inputs. Complete non-adaptive E008o base-object composition and the separate VFE1 WM16 retirement/lifecycle gate remain open. No module load/camera/MMIO/DMI/RT-CDM runtime. See E011Z README/RESULT/REPLAY-SAFE.

## E011y rear startup LSC/GTM semantic binding — WINDOWS SOURCE + LIVE CLOSED, CLEAN REPLAY OPEN

Fresh E011Y Windows tracing closes the four-packet adaptive startup schedule without promoting captured DMI bytes into policy. LSC has two genuine pre-R4 startup semantic states, both request-labelled 1: cold lux/CCT 220/0 and populated request-1 lux/CCT 232.247802734375/5000. Their source-locked Titan680 staging packs reproduce E006B startup phases 0 and 1 exactly; phases 2/3 contain no LSC DMI. The module Tintless-enable flag is set on both startup calculations, but the first actual request-local Tintless callback is request 4. GTM likewise has two semantic TMC states: pre-request state 0 then request-1 state 1, with documented runtime/control validity fields transitioning 0->1; both produce the same exact GTM payload, and phases 2/3 hold state 1. All four startup GTM payloads are byte-identical to E006B. Three bounded rear4K runs passed Start/Stop with 1,865 / 1,454 / 533 valid handles. Raw dumps/addresses/logs remain private. Next: SP11 Linux offline clean replay through E007h and E007p/q; no Linux camera/module/MMIO/DMI/RT-CDM runtime. Native rear ISP remains denied. See E011Y README/RESULT/LIVE-VALIDATION-SAFE.

## E011x rear neutral-3A scalar bootstrap - SOURCE + LIVE CLOSED

Fresh E011X-1412A closes the neutral AEC/AWB scalar bootstrap gate. The exact installed Demux/BLS141, PDPC311 and WB201 source/tuning paths were already pinned; the bounded rear Color VideoRecord NV12 3840x2160 trace added eight atomic request hooks (request IDs 1 through 8) plus eight entries at each scalar common calculation. PredictiveGain was 1.0 for all eight sampled WB calculations; Demux BLS/channel input tuples were stable across the sampled startup window; request-time dGain and AWB state evolved coherently. Private E006a validation reproduced every scalar register instance actually present in the four startup MAINs: 8/8, 8/8, 8/8 and Demux-only 2/2 = 26/26 exact. The event order proves one pre-request scalar seed, new states for requests 1 and 2, and no scalar recalculation for request 3, so packet phase 3 legitimately holds the preceding Demux state rather than inventing a fourth scalar set. Start/Stop passed with 1,807 valid 4K handles; raw bytes, register values, process addresses and debugger logs remain private. Neutral-3A is CLOSED. Next semantic gate is request-tagged LSC/GTM; VFE1 WM16 same-generation retirement remains separate; native rear ISP runtime remains denied. See E011X README/RESULT/LIVE-VALIDATION-SAFE.

## E011w rear AF/BF pre-request hardcode timing — SOURCE + LIVE CLOSED

Fresh E011W-0942A separates the two callsites of the shared hardcoded BF ROI helper. Static analysis identifies `IFENode::HardcodeSettings` entry RVA 0x735940 and its helper call at 0x736438, while `IFENode::Get3AFrameConfig` has the distinct zero-ROI fallback call at 0x741D38 after branch RVA 0x741D08. Live, the shared ROI helper ran exactly twice before request 1, both with return RVA 0x73643C, proving the calls came from HardcodeSettings; the semantic helper likewise ran twice. The Get3AFrameConfig zero-ROI branch recorded zero hits. Thereafter 2,237 consecutive IFENode BF-count observations covered request IDs 1–2237 and every one had ROI count 25. Start/Stop passed with 2,366 valid 4K handles; raw transcripts remain private. E008s remains authoritative for the already-closed hardcode filter/coring/ROI/-3/0 semantics. AF/BF bootstrap timing is now closed; proceed to neutral-3A, then LSC/GTM, while VFE1 WM16 same-generation retirement remains separate. Native rear ISP remains denied. See e011w README.

## E011v rear AFStatsControl request-1 full-payload bridge — SOURCE + LIVE CLOSED

Fresh E011V-0810A closes E011U's two remaining request-1 AF/BF publication gaps. Pinned data RVA 0x147ABC4 is PropertyIDAFStatsControl 0x3000000E; the CAF publication path emits a 0x1CC0-byte property. In `CAFIOUtil::PublishOutput` RVA 0x817710, live call site 0x818B7C copied exactly 0x1CC0 bytes from the completed CAF AF/BF record into the request-indexed output. Before the copy source BF words +0x1C88/+0x1C8C were 0,25 while destination was 0,0; after the copy destination was 0,25 and all 25 ROI validity fields at +0x354+n*0x24 were 1. The same request ID 1 then reached `IFENode::Get3AFrameConfig` BF count load RVA 0x741C7C with a distinct metadata-pool pointer, count 25, all 25 validity fields 1, and a complete 0x1CC0 dword comparison against the CAF publication destination returned zero differences. Thus the request-1 full AFStatsControl payload bridge is closed by content identity, not pointer aliasing. E011V Start/Stop passed with 103 valid 4K handles; CDB detached, breakpoints cleared and fresh KDNET stopped. Raw CDB/holder/KD transcripts were archived privately before checkpoint and remain off Git. A distinct earlier packet-0 hardcode event is not excluded; neutral-3A, LSC/GTM and VFE1 WM16 generation-safe retirement remain separate gates. Native rear ISP remains denied. See e011v README.

## E011u rear AF/BF request-1 count bridge â€” SOURCE + LIVE COUNT CLOSED, FULL VALIDITY OPEN

Pinned source maps PropertyIDAFStatsControl 0x3000000E through CAFIOUtil::PublishOutput RVA 0x817710. AF type-2 ROI mapper RVA 0x819418 writes source copied-entry count to its internal destination +0x1C88, maps 0x20-byte source ROI entries to 0x24-byte output records with validity at +0x350, and the 0x1CC0-byte publish copy starts four bytes before that destination. Thus published +0x1C8C is the same 25 count checked by IFENode at RVA 0x741C7C. Fresh atomic E011U-0757A live trace saw pre-request mapper source header 1,0,25 and first two validity flags 1; after CAF Execute request ID 1 a mapper hit again showed 25 copied entries and first two validity flags 1; request-1 IFENode consumed published adjacent words 0,25 and selected normal BF. Source plus live closes the count mapping; all 25 request-1 validity flags, exact metadata allocation identity and any separate packet-0 hardcode event remain open. Fresh SP7 KDNET connected and was stopped; local ARM64 CDB completed the trace. StartAsync succeeded, 970 valid 4K handles, Stop passed, breakpoints cleared and debugger detached. Native rear ISP remains denied. Next trap 0x1CC0 copy and metadata boundary with a new one-shot, verify all 25 validity flags and generation ownership, then continue neutral-3A/LSC/GTM and WM16 retirement. See e011u README and RESULT.json.
## E011t rear BF request-1 normal ROI boundary â€” LIVE CONSUMER BRANCH OBSERVED, PRODUCER OPEN

E011S's list of packet-0 BF filter/coring, IIR shifts, 25-ROI seed and phase validity as unresolved was stale: E008s already source-closed those, and E008t/u/E009e validated the offline phase composer. New static work shows the AF outer SetParam 0x15 arm at RVA 0x619910 stores a 0xA0-byte settings pointer and calls HAF settings handoff RVA 0x622020; no direct BF field map is claimed. IFENode checks the published BF ROI count at RVA 0x741C7C and selects the zero-count hardcode branch at 0x741D08 or the normal copy at 0x741C94. In fresh atomic Windows E011T-0838B, the first observed request-1 sequence was BFStats25 CheckDependenceChange, CAFStatsProcessor ExecuteProcessRequest, then IFENode Get3AFrameConfig. At the latter consumer request ID 1 had published ROI count 25, selecting the normal branch at that observed point. It does not exclude a separate earlier packet-0 fallback, and the request property producer, individual ROI validity and exact per-packet ordering remain open. Fresh SP7 KDNET connected then break-in retried; job stopped, local ARM64 CDB completed the trace. StartAsync succeeded, 618 valid 4K handles, Stop passed, breakpoints cleared, debugger detached. The erroneous E011T-0732A pre-enumeration staging identity was consumed without camera access. Next: source-map exact CAF/BAF request BF property writer, then fresh one-shot trace writer -> published property -> IFENode consumer and validity. Native rear ISP runtime denied. See e011t README and RESULT.json.
## E011s rear AF / BFStats25 static reconnaissance — SOURCE-ONLY CHECKPOINT, LIVE OPEN

E011R closed the rear AWBStatsControl request bridge, so the next semantic blocker is E008r's BFStats25/AF first-frame bootstrap. Static reconnaissance maps `CAFStatsProcessor::Initialize` RVA 0x827940, `ExecuteProcessRequest` RVA 0x8288C0, settings snapshot helper 0x82D450, and `SetSingleParamToAlgorithm` RVA 0x82D820. Initialize snapshots AF/HAF static settings into a fixed 0xA0-byte block at data RVA 0x176B640, then after algorithm setup sends SetParam 0x16 followed by SetParam 0x15 using that block. This gives a concrete upstream anchor for E008r's unresolved packet-0 BF filter/coring, numeric IIR shifts, accepted ROI set and per-packet validity, but individual field semantics and the request-1 live producer/consumer are not yet closed. No E011S live one-shot identity has been consumed. Previous KD terminal job_qK4sPUlE1b73bjuBzXCzvZ11 is stopped after transport retry exhaustion and must not be reused; start a fresh KDNET session before any live trace. Native rear ISP remains denied. See e011s README.

## E011r rear AWBStatsControl exact request bridge — SOURCE + LIVE CLOSED

Fresh request-1 tracing closes E011Q's remaining AWB property boundary. Static property tables identify `0x5000001D` as `PropertyIDUsecaseAWBStatsControl` and `0x3000000D` as `PropertyIDAWBStatsControl`. The request output descriptor at data RVA 0x840E58 is `0x803000000D`, binding a 0x80-byte PropertyIDAWBStatsControl output to CAWBIOUtil qword index 0x5FD (byte offset +0x2FE8). Live request ID 1 entered `CAWBStatsProcessor::ExecuteProcessRequest` RVA 0x82EF50; its call at 0x82FA60 to helper 0x846020 (`CAWBIOUtil::FillBGConfigurationData`) entered with the qword-index 0x5FD output (byte offset +0x2FE8) zero while the internal +0xCB4 source already held 64x48, full effective 4064x2286, four 0x3c3fe thresholds and adjacent 0x12, then returned at 0x82FA64 with that exact normal record materialized in the request output. In the same request, `IFENode::Get3AFrameConfig` RVA 0x741570 requested the adjacent 0x3000000C..0x3000000F group; index 3 is PropertyIDAWBStatsControl, and the live source load at 0x741BA8 carried the same normal 0x80-byte payload before E011P's store at 0x741BC8 into request +0xCF8. The metadata pointer is a distinct pool allocation, so this proves producer -> published request property -> consumer, not pointer aliasing. E011Q's 0x5000001D Usecase payload is a sibling output built from the same internal +0xCB4 source, not a demonstrated direct Usecase-to-request memcpy. E011R-0732A Start/Stop passed with 446 valid 4K handles; breakpoints cleared. Native rear ISP remains denied. See e011r README.

## E011q rear AWB_BG pre-request normal seed + Usecase prepublish writer — SOURCE + LIVE SEED CLOSED, BRIDGE OPEN

Fresh Windows tracing moves upstream of E011P. A live call from `CAWBStatsProcessor::Initialize` (container RVA 0x82E140) at call site 0x82ED9C entered helper RVA 0x831510 with AWB IO BG config uninitialized and returned at 0x82EDA0 with the normal seed already materialized: 64x48, ROI selection 2 resolving through default sensor resolution to full 0,0,4064x2286, four 0x3c3fe thresholds and adjacent mode word 0x12. A separate request-1 `CAWBStatsProcessor::ExecuteProcessRequest` RVA 0x82EF50 entered with the same values already present, and the first request-1 AWB algorithm return RVA 0x82F5F8 preserved them, so request 1 does not originate this seed. Pinned source of helper 0x831510 identifies `CAWBIOUtil::PrePublishMetadata` and an unconditional 0x80-byte UsecasePool publication at RVA 0x831E00 through helper 0x5D6A18 for property 0x5000001D before the function's single return. This source-closes the prepublish writer but does not yet equate Usecase property 0x5000001D with the exact per-request 3A property later consumed by E011P; that explicit bridge remains the narrow upstream gap. E011Q-0230E Start/Stop passed with 7,496 valid 4K handles; stale KD transport retired and fresh KDNET reconnected cleanly. Native rear ISP remains denied. See e011q README.

## E011p rear AWB_BG request-1 normal consumer + 3A handoff — SOURCE + LIVE CLOSED

Fresh same-Windows tracing closes E011O's remaining request-1 consumer gap. Pinned source identifies `CamX::IFENode::Get3AFrameConfig` RVA 0x741570 as the request-side 3A handoff; its AWB branch consumes the returned 3A AWB property and copies the complete record into request +0xCF8, with first live SIMD store at RVA 0x741BC8. The normal record is 64x48, ROI 0,0,4064x2286, four 0x3c3fe thresholds and adjacent mode word 0x12. A later request-ID-1 `AWBBGStats17::Execute` RVA 0x9FE780 entered with that normal request record while the module's cached +0x60 record still held the cold 64x48, 3658x2058, four-0x3ffff seed. `CheckDependenceChange` RVA 0x9FDF60 copied the request record into the module; at `AdjustROIParams` RVA 0x9FE120 entry the cached record already matched the normal request, and AdjustROI preserved the primary grid/ROI/threshold semantics while deriving 62x46 region dimensions. Supporting E011O-0100A holder Start/Stop passed with 1,403 valid 4K handles; KD breakpoints cleared. The earlier AWB policy/algorithm writer that creates the upstream 3A property payload remains open. Native rear ISP remains denied by BFStats25/AF, neutral-3A, LSC/GTM and VFE1 WM16 IRQ/DMA/IOMMU retirement/lifecycle gates. See e011p README.

## E011o rear AWB_BG request-1 cold-to-normal bulk transition — SOURCE + LIVE SAME-SLOT REPLACEMENT CLOSED

Fresh original rear4K tracing caught the first `AWBBGStats17::Execute` (RVA 0x9FE780) carrying request ID 1 while request `+0xCF8` still held the cold `64x48`, ROI `0,0,3658x2058`, four-`0x3ffff` AWB_BG seed. A process-scoped watch on that same request-owned slot then caught the first semantic-changing replacement inside the active IFE request-data bulk-copy path. Static reduction identifies helper RVA 0x740D88, reachable from `CamX::IFENode::ExecuteProcessRequest`, with the full `0xF508`-byte copy returning at RVA 0x740E5C into `IFENode + 0x145B0`. The upstream source carried `64x48`, ROI `0,0,4064x2286`, four `0x3c3fe` thresholds and the same adjacent `0x12`; single-step proof showed the watched destination change in place to those normal values while H/V remained 64x48. Thus the same-slot cold-to-normal replacement mechanism and immediate normal source payload are closed. The earlier policy/producer that populates that upstream normal AWB_BG source remains open, and a second AWBBG Execute after replacement was not independently trapped. Holder Start/Stop passed with 789 valid 4K handles; breakpoints cleared. Native rear ISP remains denied by remaining E008p semantic seeds plus VFE1 WM16 IRQ/DMA/IOMMU retirement/lifecycle gates. See e011o README.

## E011n rear AEC_BE request-1 normal producer — SOURCE + LIVE IMMEDIATE PRODUCER CLOSED

Fresh original rear4K tracing plus pinned source closes the immediate producer behind E011C's cold-to-normal AEC_BE transition. `CAECStatsProcessor::SetStatsConfigFromAlgoConfig` RVA 0x83DF68 consumes AEC engine frame-control region counts, ROI-selection policy and thresholds; ROI selection 1 routes through `GetCropWindow` RVA 0x83D7B0. A pre-request call already carried 32x32 with four 0x3e7ff thresholds, then the first observed `ExecuteProcessRequest` RVA 0x8356E0 carried request ID 1 and its normal SetStatsConfig call again carried 32x32, ROI selection 1, full 4064x2286 and four 0x3e7ff thresholds. Combined with E011C's exact watched request-slot replacement, this identifies the request-1 normal AEC algorithm/frame-control producer and order behind the 64x48/3658x2058/0x3ffff cold seed transition. This run did not independently trap the immediate second request-1 IFE validation after the producer, so that downstream application remains linked by E011C rather than re-proved here. Holder Start/Stop passed with 383 valid 4K handles; breakpoints cleared. Native rear ISP remains denied by AWB_BG, BFStats25/AF, neutral-3A, LSC/GTM and VFE1 WM16 IRQ/DMA/IOMMU retirement/lifecycle gates. See e011n README.

## E011m rear RSStats14 Titan680 preset origin — SOURCE + LIVE FIRST-WRITER CLOSED

Fresh same-SP11 tracing closes E011H's upstream 16/1024 question for the active Titan680 path. IFENode construction began with +0x9764..+0x977C zero; an exact write watch on +0x9770 caught the first store at QcDeviceMFT8380.dll RVA 0x8A2158 inside the Titan680 pipeline vtable +0x80 function RVA 0x8A2150, called from CamX::IFENode::ConfigureIFECapability. Static source shows that function writes the literal capability/default-statistics block 18,14,14,16,1024 at IFENode +0x9764..+0x9774. A separate E011L trace showed ReadDefaultStatsConfig enters only after 16/1024 is already present. Thus HardcodeSettings is downstream: the initial active-Titan680 RS preset is pipeline capability initialization, not an AFD/request algorithm seed. This is not proof of universality across other Titan generations or absence of later overrides. E011M Start/Stop passed with 1,593 valid 4K handles; breakpoints cleared; ordinary reboot returned Golden Linux 7.1.5-sp11-render-parity-v4+, saved v19c, next_entry empty, no camera modules/nodes. Native rear ISP remains denied by remaining E008p semantic seeds and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle gates. See e011m README.

## E011h rear RSStats14 request-1 semantic handoff — SOURCE + LIVE, PRESET ORIGIN OPEN

Fresh original rear4K first RS Execute carried request ID 1. Request +0x2C50 and IFENode +0x9770/+0x9774 both held 16/1024, adjacent source offsets were zero, and request crop was 4064x2286. Pinned HardcodeSettings copies these node fields to the request record; RS dependence changed zero cached state into 16x1024 with 254x2 regions, zero offsets, shift 5, matching E006v's AdjustROI/packer law. The upstream writer/policy for IFENode's 16/1024 preset remains open; do not hardcode this session's values as a universal seed. Holder Start/Stop passed with 416 valid 4K handles, CDB detached, Golden guard PASS. Native rear ISP still denied by other E008p seeds and VFE1 WM16 generation-safe retirement. See e011h README.

## E011g rear Tintless_BG first-consumer seed — SOURCE + LIVE CLOSED

The E011F 18-to-14 boundary is explained by the pinned original `IFENode::HardcodeSettings` RVA 0x735940: its Tintless branch (change bit 0x100, cold argument 1, or uninitialized node state) writes the same request/retained +0x500 record with 32x24 grid, active geometry, source-derived four thresholds, and explicit record +0x28=14. The geometry helper RVA 0x736DB0 had first written +0x28=18; request ID 1 Tintless dependency consumed +0x28=14 with full 4064x2286 and four 0x3ffff thresholds; Tintless Execute RVA 0xA1174C later wrote 18, and request ID 2 consumed it. The exact true Hardcode branch arm/store instruction was not trapped live. This closes the pinned rear4K Tintless first-consumer seed, not the other E008p gates or VFE1 WM16 generation-safe retirement. Native rear ISP remains denied. See e011g README.

## E011f Tintless retained writer / first consumer ordering — LIVE PARTIAL

Fresh rear4K tracing hit IFENode's Tintless writer RVA 0x736DB0 before the first dependency. It wrote retained node config +0x500 from zero to 32x24/full 4064x2286/four 0x3ffff thresholds and record +0x28=18, with source node +0x9764=18, half-width flag 0, override flag 0. The first request-ID-1 Tintless dependency then read its request +0x500 with the same geometry/thresholds but +0x28=14; retained +0x28 was also 14. A later direct store in Tintless Execute RVA 0xA1174C changed retained +0x28 from 14 back to 18. The intervening 18-to-14 writer and request-copy timing remain open. Holder Start/Stop passed with 1,242 valid 4K handles, CDB detached and Golden guard PASS. Rear ISP remains denied. See e011f README.

## E011e Tintless_BG request writer shape — SOURCE PASS, PRODUCER ORDER OPEN

Pinned original IFENode helper RVA 0x736DB0 writes the request +0x500 Tintless record through pointer table entry 1 (+0x360) plus +0x1A0. It derives 32x24 zero-origin geometry from active bounds, with a conditional half-width and separate-window override, and derives thresholds plus record word +0x28 from node field +0x9764. E011D's first request-1 consumer had thresholds 0x3ffff but +0x28=14; the later copy changed that word to 18. This mismatch means the helper's exact first-consumer ordering/intervening writer remains open even though the source record mapping is proved. Rear ISP stays denied by other E008p seeds and VFE1 WM16 retirement. See e011e README.

## E011d rear Tintless_BG request-1 first consumer — LIVE, PRODUCER OPEN

Fresh original rear4K request ID 1 Tintless_BG dependency read the distinct request +0x500 record at grid 32x24, zero origin, full 4064x2286 rectangle and four 0x3ffff thresholds. It was already populated before the first AEC_BE validation and differs from the AEC_BE 64x48 90%-bounds cold seed. A watched broad copy preserved Tintless geometry/thresholds while record word +0x28 changed 14 to 18; request ID 2's Tintless dependency consumed that same slot with the latter word. The upstream producer and semantic meaning of +0x28 remain open. E011D holder Start/Stop passed with 246 valid 4K handles, CDB detached and Golden guard PASS. Other E008p seeds and VFE1 WM16 retirement still deny native rear ISP. See e011d README.

## E011c rear AEC_BE request slot cold-to-caller transition — LIVE PARTIAL

Fresh original rear4K request ID 1 AEC_BE validation first read its normal request slot at 64x48, 3658x2058, four 0x3ffff thresholds. A hardware write watch on that exact slot caught the bulk config copy, changing it to 32x32 and full 4064x2286; two threshold lanes changed at the watched SIMD store and all four read 0x3e7ff at a later AEC_BE validation of the same slot. The later hit was request ID 1153 because the validation breakpoint was temporarily cleared, so the immediate second request-1 consumer remains open. Holder Start/Stop passed with 1,302 valid 4K handles; CDB detached and Golden guard passed. Tintless_BG/RS and other E008p seeds plus VFE1 WM16 generation-safe retirement still gate native rear runtime. See e011c README.

## E011b rear BG cold slot identities — SOURCE MAP PASS, REPLACEMENT OPEN

The pinned original IFENode request pointer table and HardcodeSettings now map the four 64x48 AEC_BE cold records to normal request +0x3E0 and HDR exposure types 0/1/2 at +0x798/+0x818/+0x718. A separate AWB_BG cold record is request +0xCF8. E011A directly observed only the normal AEC_BE and AWB_BG cold consumers. Tintless_BG reads request +0x500 and is not covered by those records; RS and per-request BG replacement remain open. Native rear ISP stays denied. See e011b README.

## E011a first rear stats cold geometry — SOURCE + LIVE PARTIAL

The original HardcodeSettings cold branch derives four 64x48 BG-style grids with zero origin and 90% active-bound width/height. E011A's request-1 AEC_BE and AWB_BG validation saw 3658x2058 from 4064x2286 active bounds; Tintless_BG and per-request replacement remain open. The debugger-paused holder recovered: 656 rear 4K handles, clean Stop, CDB detached, Golden guard PASS. Do not hardcode the observed rectangle or arm rear ISP. See e011a README.

## E010z first-selector request-1 BHist cold seed — SOURCE + LIVE TIMING CLOSED

Fresh same-SP11 rear4K tracing now closes the startup BHist ambiguity. The pinned IFENode::HardcodeSettings helper derives the cold/default BHist rectangle from active bounds as width-floor(width/10), height-floor(height/10); 4064x2286 therefore yields 3658x2058. A selector breakpoint armed before START.GO showed the first BHist selector after start belongs to request ID 1 and consumes that 3658x2058 request-owned slot. A write watch on that same slot then caught the request-frame bulk config copy replacing it with the live full-crop 4064x2286 config, and the next selector for request ID 1 consumed full crop. Model this as a cold first-selector seed followed by per-request replacement; do not treat 90% as a permanent request policy or hard-code 3658x2058. The run closed cleanly with 418 valid rear 4K handles. Native rear ISP remains denied by the remaining first-frame stats seeds and VFE1 WM16 IRQ/DMA/IOMMU retirement gate. See e010z README.

## E010p cold BHist memory timing — aborted capture

Local CDB caught MFT load before Init; no setter/selector hit during Init. After Start, a bounded private-memory scan saw no smaller ROI at the first full-crop setter entry and 24 matches by the first selector, including the actual selected request context. This narrows the observed write interval but does not identify the writer or request ID. The CDB pause let the holder's 30-second WinRT wait expire; no frames or clean Stop are claimed. CDB closed, Golden return guard passed. Use a debugger-safe timeout or private time-travel trace for a new identity; do not promote this aborted run into rear ISP authorization. See e010p README.

## E010o BHist setter before selector — initial writer open

A fresh Windows rear4K Start showed the first observed AEC BHist setter consume full crop and a zero destination before the first observed BHist selector returned the smaller ROI from a separate request context. No numeric request ID or setter-to-selected-context causal link was captured. The holder returned 226 valid 4K handles, KD was cleared, and Golden return guard passed. E009h's direct smaller-to-full transition stands; source-close the initial request-context writer before integrating policy. See e010o README.

## E010n live AEC crop selection — startup ROI writer still open

The first observed rear4K SetStats call selected GetCropWindow (ROISelection=1); its returned rectangle and the subsequent BHist setter argument were full active crop. Direct EngineFrameControl rectangle was zero. The bounded Windows holder returned 230 valid 4K handles, KD breakpoints were cleared, and Golden return guard passed. This call has no direct startup packet ID; E009h directly observed the initial smaller BHist ROI in a separate clean start; do not infer it was produced by this setter call or use it as a runtime constant. Trace the algorithm BHist ROI writer and correlate requests. See e010n README.

## E009h initial BHist ROI and next transition — LIVE, POLICY OPEN

E009h directly observed the original BHist path consume the smaller initial ROI, then a write to its request configuration and the next calculation consuming full active crop in the same rear4K start. The setter RVA 0x83E8F8 did not hit at the expected first-start point in that trace. Numeric request ID and the original algorithm/tuning policy producer remain unproven; keep E009g caller-owned and rear ISP disarmed. See e009h README.

## E009g initial AEC BHist ROI — REQUEST HANDOFF EXACT OFFLINE, ORIGIN OPEN

The detached request-owned E009g handoff validates the caller AEC BHist ROI and generates the E006u Titan680 region word. Private startup0 matches the smaller rectangle later observed directly by E009h, and startup1–3 match full active crop; reverse controls fail. Static DeviceMFT traces algorithm-output copy through CAECStatsProcessor/IFENode to BHistStats16, but do not prove the first AEC algorithm ROI writer or its request timing. Do not freeze 90% as a native default or arm rear ISP. E009g README has the bounded evidence.

## E009f first-normal zoom geometry candidate — EXACT BITS, PRODUCER OPEN

The independent accepted rear crop width4064 divided by raw sensor width4076 rounds to live first-normal AF zoom float32 bits0x3f7f3f0f exactly. Feeding this parameterized ratio into E009e yields startup0–3 and one steady BF ROI selector1 each 300/300. The CamX writer of AF parameter case0x15/state+0x1a4d8 and its request transition are not source-closed, so this is a high-confidence geometry hypothesis, not an authorized driver constant or runtime ISP permission. See experiments/E004-front-ir-vd55g0/e009f-rear-crop-width-zoom-hypothesis/README.md.

## E009e live first-normal AF zoom — PHYSICAL INPUT, FOUR ROI PAYLOADS EXACT OFFLINE

One bounded original rear4K SP11 Windows session under external SP7 KD observed a first-normal `af_util_adjust_roi` zoom float32 0x3f7f3f0f (0.9970559477806091), CAMIF 4064x2286, ROI type0 and loaded HAF 0.25/0.25; twenty later same-caller hits used zoom1.0. The holder produced 52 valid 4K handles/8s, debugger breakpoints were cleared, and SP11 returned to Golden. A source-forward host composer using this independent physical scalar gives exact selector1 300/300 for all four retained startup packets and one steady; zoom1.0 negative control is packet1 250/300. The AF hit itself lacks direct RT-CDM packet ID, and zoom upstream derivation plus broader semantic/DMA gates remain open. Do not hardcode the transient into a native runtime seed. See experiments/E004-front-ir-vd55g0/e009e-rear-af-live-zoom-forward/README.md.

## E009d packet1 AF scalar equivalence — CALIBRATED, NOT OBSERVED

An illustrative packet1 zoom input 0.998 in the pinned default AF source path reproduces private selector1 300/300; that same input breaks packet2/3 (250/300), while zoom 1.0 gives packet2/3 300/300 and packet1 250/300. The scalar was calibrated against final DMI. This identifies a falsifiable transient AF input target, not the actual Windows value or a runtime seed. Observe first normal AF ROI type, rectangle, CAMIF geometry, selected HAF and zoom before use. See experiments/E004-front-ir-vd55g0/e009d-rear-af-transient-zoom-equivalence/README.md.

## E009c request-scoped AF/BF ROI handoff — OFFLINE SETTLED PARITY

Source-derived handoff now consumes an explicit per-request AF rectangle into the isolated E008o/E008t BF selector-1 state. Packet0 is rejected/preserved; invalid or consumed requests fail closed. Pinned private startup2/3 comparisons are each 300/300 bytes; startup1 remains 250/300 with only position fields open. This is detached host code, not runtime authorization. Source-derive or independently observe startup1 AF selection before treating its ROI as resolved. See experiments/E004-front-ir-vd55g0/e009c-rear-af-request-roi-handoff/README.md.

## E009b settled rear AF/BF ROI — OFFLINE BYTE PARITY FOR NAMED SAMPLES

The pinned rear HAF 25% scalar pair, accepted 4064x2286 crop, source-derived default/even/BAF/5x5/BF valid path and E008t/E007e packer now give selector1 300/300 bytes exact for packet0, packet2, packet3 and one retained steady sample. Packet1 is 250/300: all 25 left and top fields differ, while width/height/IDs/flags match. This is a forward source candidate validated against private final DMI, not a live AF request-stage observation. Do not hard-code packet1 coordinates or arm native rear ISP. Next close first normal AF state and ROI update order, then require four startup packets exact. See experiments/E004-front-ir-vd55g0/e009b-rear-af-settled-forward/README.md.

## E009a normal AF centered inverse — PRIVATE SHAPE PASS

The exact AF-even / BAF-height-and-clamp / 5x5-grid / BF-valid direct path has centered AF-size candidates for all 100 normal/steady ROI records under the accepted 4064x2286 active crop: two candidates per axis per sample. The tested raw sensor and video output dimensions have none. Packet1/2 candidate sizes are disjoint with possible 1–3 size deltas per axis despite unchanged final cell dimensions; a centered size change can therefore explain the uniform position shift. This is an inverse fit to private final DMI, not independent request input or predictive 300-byte parity. Native rear ISP stays denied. See experiments/E004-front-ir-vd55g0/e009a-rear-af-centered-inverse/README.md.

## E008z tuning layout guard

Do not equate serialized rear HAF record offsets with the loaded CamX HAF object offsets used by `af_util_get_roi_default` without proving the loader layout. A private direct-offset candidate matched 0/25 in every ROI geometry field across four normal/steady samples; this is a negative control, not evidence against the default branch. See experiments/E004-front-ir-vd55g0/e008z-rear-af-default-rectangle/README.md.

## E008z source-derived default AF rectangle — OFFLINE SOURCE SLICE

A parameterized offline helper now models the pinned default AF ROI producer: selected CAMIF geometry, tuning fractions, inverse zoom, optional PD scale, the selected 200/400 minimum and centered rectangle. The request can instead select face/track/salient/touch/PD multiwindow paths; no live packet1/2 input or normal full DMI parity is established. Do not treat the helper as a runtime seed. See experiments/E004-front-ir-vd55g0/e008z-rear-af-default-rectangle/README.md.

## E008y original rear AF ETW oracle — STREAM PASS, STAGE UNRESOLVED

One bounded original-Windows 12-second rear4K VideoRecord stream acquired 281 valid handles. The pinned DeviceMFT ETW provider emitted 195450 events, but generic decoding lacked its schema and the capture did not expose a request-tagged AF/BAF rectangle or BFStats25 intermediate ROI. Source analysis separately shows a BAF coordinate handoff that adds vertical grid count plus 11 to the adjusted rectangle height before a geometry clamp; it does not identify the live request input. SP11 returned to Golden with overlap guard PASS. Do not rerun this trace unchanged, hard-code coordinates, or arm native rear ISP. See experiments/E004-front-ir-vd55g0/e008y-rear-af-etw-oracle/RESULT.md.

## E008x normal AF/BAF and BF ROI map — OFFLINE SHAPE PASS

Exact pinned mapper and BF valid-branch arithmetic now has a generic offline transform requiring an explicit AF rectangle. Four private normal/steady payloads (100 ROI records) satisfy its vertical relative-step and parity structure, but this does not prove absolute coordinates or full DMI parity. The simple 2336-basis hypothesis fails this source-shape test. Source-close request-tagged AF geometry and origin before integration; native rear ISP remains denied. See experiments/E004-front-ir-vd55g0/e008x-rear-af-bf-roi-map/README.md.

## E008w normal BF ROI width — OFFLINE PARTIAL PASS

Exact pinned BFStats25 non-clipping even-width adjustment produces 75/75 normal ROI widths matching the private same-SP11 packet1–3 corpus. Left/top/height remain open, packet0 remains byte exact, and no normal selector-1 payload is fully exact. Do not wire native rear runtime. See experiments/E004-front-ir-vd55g0/e008w-rear-bf-width-source-slice/README.md.

## E008v rear normal ROI Windows oracle — BOUNDED STREAM PASS

Original-Windows rear 4K NV12 holder produced 284 valid handles, and QcDeviceMFT8380.dll loaded in FrameServer. The disposable user-mode debugger auto-detach test failed; no camera process was attached and no intermediate ROI stage was observed. Packet1–3 geometry source closure remains open. SP11 is back on Golden Linux. Continue static AF/BAF and BFStats25 source analysis, private offline parity only; do not arm native rear ISP. See experiments/E004-front-ir-vd55g0/e008v-rear-normal-bf-roi-windows-oracle/RESULT.md.

## E008u rear BF ROI geometry audit — OFFLINE PARTIAL PASS

E008t's clean packet0 ROI seed, passed the accepted 4064x2286 rear ISP crop, matches 25/25 records and 300/300 selector-1 bytes in a private same-SP11 comparison. Normal packets1–3 retain geometry mismatches; do not replay observed coordinates, claim final four-packet DMI parity, or arm rear ISP. Source-close the normal AF ROI mapper and BFStats25 validate/adjust path next. See experiments/E004-front-ir-vd55g0/e008u-rear-bf-roi-geometry-audit/README.md. No runtime.

## E008r rear BFStats25 request-state source closure — STATIC PASS

Exact DeviceMFT BFStats25::CheckDependenceChange/Titan680 source now fixes the request ownership boundary. The normal LUT-bank state toggles as one value and drives ROI-index/gamma banks together, matching E006z startup phase parity. Gamma/luma/scale plus FIR/IIR enables are caller semantic fields, not transport guesses. BCA8's two signed4 nibbles are the two AF BF IIR-filter shift fields; their producer identity is closed but their numerical initial values are not yet promoted. Nonzero ROI input is copied from upstream AF BFStatsROIConfig and then boundary-adjusted; the accepted 25-entry grid is therefore upstream AF policy, not a Titan-generated table. Do not wire runtime from E008r. Remaining BF seed work is now upstream AF/BAF only: packet0's distinct filter/coring seed, numerical shifts, 25 ROI semantics and per-packet validity choices.

## E008q rear BFStats25 clean seed authority — STATIC PASS

Selected rear BAF tuning now cleanly owns the normal packet1+ BF gamma, both Q14 filter coefficient groups and both coring/threshold tails. Private validation is aggregate-only: gamma 4/4 exact retained selector2 payloads; filter and coring 34/35 complete BF register records, with startup packet0 the sole distinct case. No captured Windows register words or DMI payload bytes are committed. Do not yet build a runtime BF seed: packet0's distinct initial filter state, feature/LUT-bank policy, signed4 shift fields and the 25-entry ROI generator still need source-backed producers. Close those from BFStats25::CheckDependenceChange/Titan680 + rear AF tuning before recomposing E008o.

## E008p first-frame semantic bootstrap audit — OFFLINE PASS

E008o packet isolation is necessary but not sufficient to arm rear hardware. E008p identifies the remaining clean-bootstrap boundary: eight provider families are already self-contained, while eleven semantic seed families still need deterministic initial inputs. In particular BFStats25 register state and its 25-ROI/gamma DMI are upstream policy, and a private aggregate-only audit proves all 29 BFStats25 words vary across the four accepted Windows startup packets. Do not replace them with one frozen state. Long-run live AEC/AWB/AF convergence is still not required for the first proof; only bounded initial seeds are. No captured values/bytes are committed. Close statistics/AF seed first, then neutral AEC/AWB and request-tagged LSC/GTM startup seeds before recomposing any consumed runtime runner.

## E008o rear packet-isolated semantic state — BUILD-ONLY PASS

Do not wire E008n/E008k's shared `regs` / shared `dmi_state` preflight to hardware. E008o's static audit proves E006z startup bank selection depends on packet phase while E007i LSC and E007q GTM are request-tagged, so all four startup packets require independently frozen semantic state at materialization time. E008o defines one complete E007d + E007v state per packet, requires startup_phase == packet index, coherent request identity, valid PERIOD_CFG and recursive E007v readiness, and materializes only into an unsubmitted E008l command arena. It embeds no captured Windows register/DMI bytes and has no runtime call site. W=1/PiMaster/Fabric PASS. The next gate is a clean first-frame semantic bootstrap for all four packet states; only after that may a fresh consumed one-shot runner be recomposed.

## E008n rear consumed single-use wrapper — BUILD-ONLY PASS

E008n wraps E008l command-DMA ownership around E008k under a consumed one-shot identity. Preflight validates the exact rear route and materializes all four E007y packets while commands are definitely unsubmitted; immediately before E008k, every command slab is conservatively marked exposed. Any later uncertainty therefore pins command/output DMA until reboot. A successful return requires RT-CDM stopped, both exact-consumed-IOVA rear frames complete and the shared REAR owner released before command DMA may be freed. Output DMA is intentionally never reused in this boot even on success. Every post-preflight return requires protected-Golden reboot and forbids a second camera attempt. This closes the lifetime policy for a first disposable rear-native proof but not persistent runtime. There is still no runtime call site and the authorization stub remains -EOPNOTSUPP. Fresh W=1 build PASS, exact Golden vermagic, PiMaster+Fabric verify PASS; no install/load/camera/reboot. Next use a fresh guarded runtime candidate with one explicit invocation path only; do not attach E008n to ordinary V4L2/probe/autostart.

## E008m rear IFE0x804 logical-state closure — STATIC PASS

Do not invent a Linux IFE-start MMIO stage for the E008f IFE804 event. Exact qccamisp analysis proves IFE804 only stores usecase/frames-to-skip and has no direct hardware-start action; its only downstream effect is optional frame-drop override. The accepted rear BUS snapshots already pin every active WM to period0/pattern1 and E008d programs those exact values. Rear numeric usecase remains intentionally unpromoted.

## E008l rear Linux command-DMA arena — BUILD-ONLY PASS

E008l closes E008k caller-owned command backing: four packet-local coherent slabs provide E007y MAIN/wrapper/DMI bytes under a validated 32-bit DMA aperture; DMI payload sizes are derived directly from each E007y skeleton. CPU-only dynamic scratch stays off the hardware DMA surface. Release is allowed before any submit, but once hardware_exposed is marked the entire command set stays pinned until RT-CDM stop is independently proven. No call site exists. Preserve this conservative lifetime in any one-shot integration.

## E008k complete rear two-slot runner — BUILD-ONLY PASS / still unreachable

E008k mechanically composes the source-locked rear startup, two-slot ownership/completion and pair-aware teardown in one unreachable function. Exact order is E008j alloc/bind no-MMIO -> packet0 -> slot0 BUS disabled prepare -> E008h enable/rewrite -> packet1 -> CSID1 enable -> CSIPHY1 -> OV13858 -> Epoch0 slot1 retarget + packet2 -> next Epoch0 + packet3 -> E008i exact consumed-IOVA completion -> one CSID quiesce + one VFE BUS stop -> both ledgers retireable/released -> RT-CDM/source stop -> PM/owner release. Do not wire a runtime call site yet: caller-owned Linux command DMA for E007y and successful post-stop output-DMA release/reuse remain unresolved. Hardware-exposed failures and current successful path conservatively pin DMA.

## E008j rear pre-BUS two-slot ordering adapter — BUILD-ONLY PASS

E008j resolves the E008h/E008g integration seam: final rear orchestration must not use e008h_rear_alloc_prime_pair() directly because it performs disabled BUS preload before packet0. Use E008j zero-MMIO allocation + zero-MMIO ledger bind, submit E007y packet0, then E008j disabled slot0 prepare, E008h slot0 enable/address rewrite, then packet1. This preserves both the Windows-proven packet0-before-BUS order and the Linux safety rule that enabled WMs never contain stale/unowned addresses. No runtime call site exists.

## E008i rear CSID1 IRQ/consumed-IOVA observer — build-only PASS

Rear native mode cannot use the accepted front-only CSID software latches. E008i adds an isolated-build rear observer gated by exact E004ns CSID1 D-PHY mode. It consumes the already-read BUF_DONE value immediately after the existing clear write, adds no CSID ACK, and snapshots VFE1 ADDR_STATUS0 for exactly rear completion groups0/4/5/6/7/9 into a bounded 16-event owner-epoch-seeded history. It also latches rear Epoch0 from the already-read IPP status. The ring never overwrites; overflow/snapshot error is a hard failure. Future runner must seed observer only after exclusive REAR owner acquire and before IRQ masks are armed, then validate the owner epoch while draining records into E008h/E007z. Build-only PASS, no install/load/runtime. Next compose the complete unreachable runner; do not arm rear hardware yet.

## E008h rear two-slot prime ownership — build-only PASS

E008e/E008g show a BUS address phase after ISP_START_DONE before startup packet2 is consumed at first IFE Epoch0. E008d owned only one ten-WM output set, so E008h adds a conservative two-slot Linux ownership scaffold to preserve the first processed rear frame while later hardware writes target another complete set. Each slot is a full E008d allocation (0x1369D00 bytes); cross-slot owned spans are mechanically required disjoint and the pair budget is 0x26D3A00 bytes. Slot0 valid Linux addresses are preloaded while WMs are disabled, then the live E008f resource order is enabled and slot0 addresses rewritten/read back post-enable; first Epoch0 retargets all ten WMs to slot1 before E007y packet2. Each slot has its own E007z exact-consumed-IOVA ledger. Completion is routed only by exact programmed IOVA to a programmed pending slot; stale/unknown/ambiguous observations fail closed. No safe-free path exists after MMIO: E008a-c stop/quiescence remains mandatory. Build-only fix1 PASS with exact Golden vermagic; no module load or camera runtime. Next compose the complete unreachable rear runner; do not arm hardware yet.

## E008g rear startup-batch static correlation — no runtime

Exact-driver and retained-oracle correlation maps E008f batches0..3 one-to-one to E007y startup packets0..3. The pre-CSID selector2 call0x2491c is inside CSID DAL_csid_process_iq_packet function0x246f0; packet0 is consumed before BUS setup and packet1 after BUS config/enable/initial addresses but before CSID start. E008f CALL_B0x25ec8 is the already source-locked IFE Epoch0 consumer, so packets2/3 are the first two post-ISP_START_DONE Epoch0 consumes and batch4 is steady state. Never copy the front all-four-pre-CSID startup ordering into rear. Linux source activation should preserve CSID1 IPP -> CSIPHY1 -> OV13858; the CSIPHY1->OV13858 relative order is physically accepted by E004lr rear RAW. Next gate is not another broad Windows trace: close a second complete ten-WM DMA slot / initial prime-depth ownership before any rear native runner can be composed or armed.

## E008e/E008f live rear startup-order oracle — safe reduction, Golden returned

Two fresh same-SP11 Windows Rear Color VideoRecord NV12 3840x2160 sessions were observed only from the external SP7 KDNET debugger and returned to protected Golden. E008e proves broad order: RT-CDM count4 batch -> ten BUS config callbacks -> nine BUS enables -> ten initial address writes -> count6 batch -> CSID start -> ISP start done -> later count6 work. E008f pins pre-CSID selector2 RVA0x2491c and Epoch0/steady selector2 RVA0x25ec8, both calling RT-CDM dispatcher0x28480, and live resource IDs 0x3000(two FULL planes),0x3001,0x3002,0x301c,0x3010,0x300f,0x300e,0x300c,0x300d. E004oj already source-identified 0x300d as BF; E008f now proves the live accepted rear session configures/enables/addresses that resource. Do NOT equate enable/address with safe DMA retirement: E007z exact consumed-IOVA matching plus E008a-c quiescence/stop remain mandatory. No pixels, DMA contents or IOVAs are committed. Next statically map function0x246f0 / call0x2491c and batch identities to E007y, then close CSIPHY1/OV13858 stream-on order before composing any unreachable rear runner. Another Windows boot is allowed only for a specific residual edge; never use on-target KD.

## E005i original GROUP3/BF aggregate source lock

Pinned OEM static analysis plus E005h's already-published live user-mode endpoint proves BF event0x0f/resource0x300d is a member of original raw GROUP3_STATS ID25. GROUP3 is emitted only after original software all-stats gate0x25190 returns1, and AVStream routes raw25 through normalized type4 into ProcessStatsFrame/STAT custom metadata. **Do not treat this as DMA completion:** GROUP3 sender0x26170 calls matcher0x25078 without requiring a nonnull result. Runtime rear ISP remains denied until exact FIFO8/WM16 same-buffer hardware completion and DMA/IOMMU safe stop are independently proved. See experiments/E004-front-ir-vd55g0/e005i-original-group3-bf-stat-chain-static/README.md.

## SP11 remote-debug safety rule (2026-09-25)

SP11 is remote-only unless the user explicitly says a person is physically present. **Never use on-target KD/local kernel debugging, kernel WinDbg attach, kernel breakpoints, or any debugger operation that can halt the SP11 Windows kernel.** A kernel stop strands PiSlave/Fabric/network control. User-mode WinDbg/CDB is permitted only for ordinary camera processes (camera client, FrameServer/DeviceMFT user-mode host) and should prefer auto-continue/logpoint behavior. Non-halting ETW/WPP and static analysis are permitted. Kernel debugging may be reconsidered only with a separate live external debugger host. Do not alter BCD debug settings for user-mode work.

# Agent operating contract — SP11 camera

This file is the durable working agreement for assistants/agents operating this repository.

## E005b real PRODUCTION front 27-frame scoped CSID1 BF observer, Golden returned

[E005b one-shot original front native physical result](experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot/README.md): previous E005a older-source front module caught before BOOT, retired unarmed (no camera trial). New E005b SHA-pinned ACTUAL 27-frame production front CAMSS, same verified E004pz owner-epoch existing-CSID1-IRQ-status-only observer, isolated ARM64 W1 zero-warning module SHA f9a170c7add6f35621a9c9e4a64292cfc082b1c85a168a57ee52fb978b93a3b7. Exactly one front 27-frame shadow-policy production stream successfully produced 27 QC10C +27 TLBG +27 STATS3A exact-sized files, producer PASS/STREAMOFF_OK, actual after-safe-stop scalar owner_epoch1 bf_count0 unattributed0 safe_stop1. E005b Golden return new boot a2e56094-3583-4d17-8bce-e81603c4a448 verified, camera modules/nodes absent, temporary boot entry/dir removed, attempted identity consumed NEVER REARM. Zero scoped BF on ONE FRONT run is not proof BF impossible on front and gives no positive BF IRQ proof, global front/rear CSID1/VFE1 owner, rear frame FIFO8/nonNULL WM16 match, independent exact-buffer IRQ/DMA/IOMMU completion or native rear authorization. Golden/front PIX/rear RAW+software4K/IR unchanged. Private QC10C/stats payloads, logs and module on SP11 ONLY.

## E004pz isolated ARM64 front-runner-scoped BF observer: NOT globally exclusive VFE1 or WM16 DMA proof

[E004pz original native shared C11/kernel front-runner CSID1 observer](experiments/E004-front-ir-vd55g0/e004pz-front-owner-bf-observer-isolated/README.md): accepted CAMSS SHA pinned; isolated copied ARM64 CAMSS custom FRONT runner acquires epoch after validated front graph and before power/start, releases on its own verified safe teardown or pins on unsafe stop; one CSID1 software observer consumes EXISTING already-latched/ACKed BUF_DONE bit7 with live-config front route predicate. GCC+Clang ASAN/UBSAN each 131096 offline assertions (131072 status×route), 24 result negatives and W1 ZERO warnings ARM64 module SHA8d0a76762683edbb128a3ec1937db0a372f27f40e87d03be04ee718718419809. **Runner scope is NOT an independent global front/rear VFE1 owner; unrelated V4L2 paths not serialized, no real new live event, no per-frame WM16/FIFO8 IRQ/DMA completion, no readout or kernel module load.** Rear runtime stays -EOPNOTSUPP; Golden/front PIX/rear RAW+SW4K/IR protected. Do not replay consumed one-use builder.

## E004py historical PHYSICAL front/rear BF bit7 and WM16 source-mode discriminator

[E004py verified four original Windows physical snapshots](experiments/E004-front-ir-vd55g0/e004py-physical-front-rear-csid1-bf-bit7-discriminator/README.md): E003g front IMX681 existing SHA-locked raw KD 2026-08-28 LIVE1/LIVE2 CSID1 BUF_DONE status0x271, mask0x1FFFF, VFE1 WM16 CFG0=0x10 disabled; existing SHA-verified E004pi rear OV13858 2026-09-23 LIVE1/LIVE2 status0x2F1, mask0x1FFFF, WM16 CFG0=0x20001 enabled. Paired NAMED live phases differ EXACTLY CSID status bit7 (XOR0x80) in both source captures; masks and instant BUS IRQ status zeros are identical. These are DIFFERENT camera sessions/dates, NOT same frame, not proof BF callback FIFO8/nonnull WM16 or DMA/IOMMU completion. Shared CSID1/VFE1 native BF observer must require independently proven live owner/sensor/route provenance; bit7 and WM16 co-occurrence in Windows snapshots never authorizes VB2/DMA retirement or native rear runtime. Golden/front/rearRAW+software4K/IR unchanged.

## E004px shared front/rear BF ring owner handoff correction (OFFLINE ONLY)

[E004px owner-local frame epoch and unique pending-token correction](experiments/E004-front-ir-vd55g0/e004px-bf-owner-handoff-token-uniqueness-isolated/README.md) is a distinct isolated ARM64 compiled/C11 tested BF software-ring revision, parent f2617111. A fresh strictly higher owner epoch can start frame1 after independently verified all-group/DMA/IOMMU safe stop; old owner epoch remains stale. Duplicate opaque token while pending fails -EEXIST, preserving count/frame epoch; already verified/popped token may later be reused. Exact source header SHA7293d95a... compiled ARM64 W1 zero warnings, 437 GCC and 437 Clang ASAN/UBSAN assertions and 22 conservative result-field negatives PASS. This does NOT implement a live evidence producer, driver ISR/V4L2 caller or rear ISP authorization; do not conflate synthetic predicates with real DMA safety. Isolated module was not loaded, installed or booted; Golden/front PIX/rear RAW+software4K/IR protected.

## E005j original Windows AVStream pin2 roundtrip source lock

[experiments/E004-front-ir-vd55g0/e005j-original-avstream-pin2-isp-roundtrip-static](experiments/E004-front-ir-vd55g0/e005j-original-avstream-pin2-isp-roundtrip-static/README.md) source-locks the original surfacecamavs8380 video-pin request/completion loop around the already-proven E005h rear4K pin2 role. Request: CVideoPin HandleExtBuffer → TriggerStart → SubmitPendingPackets → SendPacketInternal → IfeNode ProcessRequest. Completion: ISP worker/notification → GetIspNotification + ProcessIfeFrame → video-pin ValidateBuffer → CompleteFrame → NotifyFrameCompleted. This is original static source evidence plus parent user-mode physical identity, not per-frame kernel-object/FIFO8/WM16 DMA evidence. No local KD is permitted on remote-only SP11; native rear hardware ISP remains denied.

## Canonical Windows → native Linux camera architecture and slice map (2026-09-24)

Before selecting a porting task, driver function, Windows app, breakpoint,
or camera mode, read [docs/CAMERA-STACK-PORT-MAP.md](docs/CAMERA-STACK-PORT-MAP.md).
It is the PINNED Windows request/AVStream/platform/sensor/ISP/DMFT/physical
graph and separate L0–L6 Linux responsibility map, with two schematics,
evidence classes P=physical, S=static, H=hypothesis, D=design, and
mode-specific test ledger. Its acceptance verifier is
`PYTHONDONTWRITEBYTECODE=1 python3 tools/verify-camera-stack-port-map.py`.

USER SCOPE: clean, controllable, native Linux stack with essential Windows-
observed sensor, ISP, DMA, power, controls and safe front/rear switching;
**no required Windows Camera app, Frame Server, .sys/.dll translation,
Windows Studio Effects, AI image enhancements or proprietary orchestrator**.
Put deterministic physical safety/ownership in kernel CAMSS/V4L2; put
optional AE/AWB/AF algorithm/policy behind standard controls or a small
open libcamera IPA where appropriate. Existing E004nr–E004nv rear native
ISP source is compiled but UNCALLED and DENIED; static BF group8 does
not prove a live event; front 27-frame, rear RAW/software fallback and
Golden remain protected. Every new experiment MUST name a Linux L0–L6
slice, an explicit mode/client, evidence tier and falsifiable next gate;
update the map if the Windows→Linux component boundary changes.

## E004pv first shared native/C11 BF owner+frame FIFO8 ring actually ARM64-CAMSS COMPILED, rear still DENIED

[E004pv independent native bounded BF queue source]( experiments/E004-front-ir-vd55g0/e004pv-native-bf-ring-owner-compiled-isolated/README.md): exact same privately staged Linux kernel include and offline C11 source SHA2459b21e...; 4-entry BF group8/WM16 owner/frame/tagged software FIFO and Linux spinlock, explicit rejected failed entry-copy, stale/duplicate owner/frame, overflow, wrong FIFO8/WM16 token/tag, missing separately witnessed IRQ/ACK/DMA/IOMMU/all-other-groups/stop. 429 GCC and 429 Clang ASan+UBSan assertions PASS, 25 scalar negative-result fields; isolated ARM64 CAMSS W=1 zero warnings module SHA daec2fd45d2c1db781f5a82d98d8eb9961193e1323e675e8550e438760a07da3; module NOT loaded/installed. This is DESIGN with caller-supplied synthetic evidence, NO actual producer or V4L2/ISR/buffer-return caller; native rear-arm ALWAYS -EOPNOTSUPP, no reliable physical same-frame WM16 completion yet. Golden/front/rear RAW+software4K/IR unchanged. Do not replay one-use build script.

## E004pu original BF software FIFO8 producer can SKIP/overflow; count is not DMA or a verified entry

[E004pu SHA-pinned original group8 ring producer/consumer audit](experiments/E004-front-ir-vd55g0/e004pu-original-group8-ring-producer-capacity-static/README.md): source-verified 62 original ARM64 anchors, 192 synthetic queue domains, 25 conservative result negatives. Original three producer callers0x23454/0x234A4/0x235C0 to0x26838: loop13 groups; either of two SOFTWARE selection masks may include group8; producer index8 and BF FIFO8 pop helper0x26460 access same per-device queue-pointer SLOT+0x3398, conditional on SAME device object (live rear correlation unproven). Producer skips absent/full queue, calls software entry copy0x2C5B0 then increments pending count WITHOUT explicit copy-helper return check; pop returns NULL on no queue/count. No queue count, BF status, event ID, software callback or CSID1 bit7 observation proves valid same-frame WM16 buffer, nonnull outstanding matching return or independent IRQ/DMA/IOMMU stop. Native rear ISP runtime DENIED, Golden/front/rearRAW+SW4K/IR protected.

## E004pt isolated ARM64 CSID1 BF status observer compiled with zero W=1 warnings, NOT a DMA-fence producer

[E004pt non-retiring native CSID1 BF observer](experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated/README.md): same SP11 accepted source SHA-pinned and isolated copied ARM64 CAMSS built. One additional software call after EXISTING CSID BUF_DONE read/ACK observes CSID1 non-lite bit7 into diagnostic-only per-device counter/last status; no extra read/ACK, generic RDI/PIX callback, vb2 return, WM16 queue identity, owner/frame generation or DMA/IOMMU fence. GCC/Clang ASAN+UBSAN 262,144 offline cases EACH and 26 result-field negatives PASS. First compiled module was warning-bearing (missing prototype) and builder exited141 on nm|grep-q SIGPIPE; preserved first build unchanged. Distinct fix1 build adds isolated prototype, ARM64 W=1 ZERO WARNINGS, private local ko SHA e492063f4e950aab50f3cfddd8e8a3db53f784fc0a8b724e3d76acf59961bdec, NOT installed/loaded. Actual original rear4K event and independently trusted exact WM16 DMA completion NOT proven; Golden/front PIX/rear RAW+SW4K/IR protected, native rear ISP runtime DENIED. NEVER replay either one-use build script or claim BF status counter is rear-only/per-frame/hardware retirement.

## E004ps original BF matcher may return NULL while OEM software callback remains reachable

[E004ps same-SP11 OEM matcher-null audit](experiments/E004-front-ir-vd55g0/e004ps-original-bf-null-matcher-callback-gate-static/README.md): 26 exact ARM64 instruction anchors, 512 offline 9-input scenarios and 21 fail-closed result-field negatives. FIFO8 nonempty is necessary to reach BF callback; WM16 CFG0 zero SKIPS identity/tag lookup and still reaches software notify. When CFG0 nonzero, six-slot outstanding matcher at original0x25078 defaults to NULL on no identity/tag match; BF caller original0x1FCEC stores its return but does NOT null-guard before software callback0x1FD28. E004pr "matcher" means ATTEMPTED LOOKUP, NOT proven nonnull. Native design must reject null/mismatched WM16 identity regardless of software callback, plus independently proven same owner/frame IRQ/DMA/IOMMU and six-group stop. STATIC/DESIGN only, no live rear4K matched frame or HW fence; Golden/front PIX/rear RAW+SW4K/IR unchanged and rear hardware ISP runtime DENIED.

## E004pr actual BF event-ID hit still must pass independent FIFO8+WM16 conditional software gates, NOT DMA-safe retirement

[E004pr original BF FIFO8 group8/WM16 software-dispatch gates static](experiments/E004-front-ir-vd55g0/e004pr-original-bf-fifo8-wm16-software-dispatch-gates-static/README.md): original same-SP11 OEM ISP **52 exact ISA anchors /31 fail-closed negatives PASS**. E004pq real KD hit RVA0x1F190 assigns BF event-ID0x0F into a local event array; actual BF branch only selected at0x1FC60, FIFO8 pop0x1FC94 returns x23 and **0x1FC9C can skip the whole BF dispatch on EMPTY queue**. Nonempty group8 entry invokes original WM16 status register callback0x1FCC4; original 0x1D714/+0x1270 address status and0x1D720/+0x1200 &1 copied to scratch for conditional metadata, NOT proven DMA fence. Original FIFO8 entry identity+0x08/tag+0x16 matched via0x1FCE4→0x25078; BF port0x300D, retained entry device+0x6A8 and **software** callback0x1FD28→0x26340 (success not independent hardware retirement). E004pr original one-shot next probes 0x1FC60/0x1FC9C/0x1FCC8/0x1FCE4/0x1FD28 are **source-identified only; NOT executed**. Need same original rear4K owner/frame generation and independently trusted CSID or VFE WM16 IRQ/DMA/IOMMU per-buffer quiescence before native BF/4K arm; E004pq actual BF assignment not yet proof. Golden/front PIX/rear RAW+SW4K/IR safe and native rear ISP runtime DENIED.

## E004pq three REAL original Windows driver instruction hits from SP7 KD — NOT same-frame WM16 DMA completion

[E004pq source-locked SP7 E004PS original Windows instruction-hit ledger](experiments/E004-front-ir-vd55g0/e004pq-original-windows-kd-bf-hit-source-locked/README.md): original private KD log remains on SP7 SHA `b9bd34f68101d987b7d86cb0de3ca713f26a62fab39295ec4661157fe250ffcc`; its safe scalar audit records verified original **absolute PE-instruction /1 breakpoints after symbolic ones failed**. REAL one-shot hits: RVA0x1675C input-config bit1 test (w8=0), RVA0x1B67C type1 zero-format CSID status preparer (x8 register-window pointer, NOT sampled status), RVA0x1F190 BF event-ID0x0F assignment instruction. Nonzero preparer0x20C04 was armed but had NO recorded hit in this finite trace. Exact original OEM ISP instruction identities SHA-locked by E004pq Linux verifier, 4 ARM64 source anchors/26 negative tests. **E004nv/pi/pk older historical 'no BF hit in THOSE observations' remains historically valid, but claiming 'all original Windows traces have no real BF hit' is now FALSE.** These 3 hits have NO common frame timestamp, rear4K device/owner/generation, source CSID1 bit7 sample, FIFO8 queue WM16 buffer ID, independent BUS/IRQ DMA/IOMMU retirement or original callback delivery; do NOT combine them into one proven frame or authorize Linux processed rear4K. SP11 now back in Golden Linux, no KD process, camera nodes/modules/active camera processes, tracked Git clean at milestone preflight. NEXT independent same-session original FIFO8 WM16 buffer generation completion and native L1–L3 stop; E004ow VFE ISR noop, E004pj CSID stats not generic RDI, native rear ISP runtime DENIED.

## E004pk source proves independent original worker-resource class and type1-CSID bit7 preparation selector; live rear mode and DMA remain UNPROVEN

[E004pk IFE resource-count vs type1 source-format independent selectors](experiments/E004-front-ir-vd55g0/e004pk-full-ife-count-vs-type1-format-mode-static/README.md) original same-SP11 OEM ISP **71 exact ARM64 anchors/31 fail-closed negatives PASS**. Original resource enumerator0x31AC–0x3234 counts successfully mapped IFE0/IFE1 resources into global0x670FC. IFE source/worker constructor0x2237C/0x22380/0x22474 compares worker instance index to copied full-IFE count; modezero BF-capable handler0x1EF90 is selected for instance1 **IF both IFE0 and IFE1 discovered**, nonzero otherwise. Distinct original input config word+0x8C bit1 sets source-format input flag+0xE28 at0x16748–0x16768, choosing type1 zero/preparer0x1B5F0 CSID bit7 preserving and normalizer0x1B7D0 vs nonzero prep0x20B50 bit7 masked/normalizer0x20CE0 at0x17D98–0x17E58. **No source identity between selectors; physical rear4K captures show CSID1 bit7+mask and WM16 enabled, NOT actual original resource count/config bit1/event0x0F/FIFO8 matching WM16 DMA**. Do not infer BIT7-triggered BF event or safe buffer retire from one selected flag. E004pj dedicated CSID/VFE stats WM16 completion source still hypothetical; E004ow ISR noop/E004ov owner gate offline, rear ISP runtime DENIED. Preserve Golden/front native PIX/rear RAW/software4K/IR. NEXT actual original same-session resource class/config bit1 and WM16 generation-safe DMA/owner source before enabling.

## E004pj accepted native CSID680 RDI bits14–17 vs BF STATS bit7 segregated; WM16 completion may originate CSID OR VFE only with per-buffer proof

[E004pj SHA-pinned actual SP11 CAMSS source and OFFLINE C11 dedicated BF bridge](experiments/E004-front-ir-vd55g0/e004pj-csid-bf-statistics-completion-bridge-offline/README.md) PASS **25 negative mutations, 65,536 status patterns and 262,267 C11 assertions EACH under GCC and Clang/ASan/UBSan**. Accepted full CSID680 already reads/ACKs BUF_DONE, forwards **only RDI bits14..17** as per-port generic `camss_buf_done`, while BF bit7 is a SEPARATE STATISTICS source not forwarded. `camss.c`→`camss-vfe.c` generic callback immediately completes a one-WM RDI/PIX VB2 output, no six-group FIFO8/WM16 ownership or DMA/IOMMU fence; never route CSID BF bit7 via RDI port7, PIX or raw WM16 index16 or double-ACK CSID. **QUALIFY E004pi:** newer Titan Gen3 bus done can be CSID-delivered, so a separately proven VFE IRQ is not inherently mandatory, but on THIS SP11 neither CSID BF bit7 nor VFE1 IRQ yet has per-frame WM16 buffer identity/DMAsafe verified completion; only independently demonstrated exact WM16 bit meaning plus owner/frame/FIFO8/buffer/gen, six groups, DMA/IOMMU and stop permit promotion. Offline model supports both trusted hypothetical sources; actual rear ISP runtime `-EOPNOTSUPP` DENIED. NO CAMSS/Golden hardware change. Next investigate original and native same-buffer WM16 completion/IRQ source before any rear runtime arm, preserve front PIX/rear RAW+SW4K/IR.

## E004pi BOTH original rear4K Windows LIVE CSID1 BUF_DONE bit7/mask PHYSICALLY observed; NOT a VFE WM16 DMA fence

[E004pi same-SP11 original rear4K live physical snapshots + offline BF/WM16 domain gate](experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/README.md): SP7 read-only reverified SHA-pin original private E004nq LIVE1/LIVE2 complete KD physical logs and selected safe register scalars. CSID1 BUF_DONE status+0x8C=`0x000002F1` and mask+0x90=`0x0001FFFF` **bit7 physically set and enabled BOTH verified live original rear4K sessions**. VFE1 WM16 CFG0=`0x00020001` enabled, ADDR_STATUS0 nonzero Boolean; VFE1 BUS STATUS0/1 zero in same snapshots but **zero register readback is NOT a DMA/IOMMU quiescence or per-frame completion fence**. E004ph now connects original CSID bit7 to conditional config-zero software BF event0x0F, but original live rear4K source-format+0xE28/worker handler selection, actual event0x0F FIFO8 generation and VFE1 WM16 DMA done remain UNPROVEN. Accepted native CSID ISR ALREADY acknowledges CSID BUF_DONE; accepted native VFE680 real ISR still no-op E004ow. **Never relabel CSID bit7 as VFE WM16 IRQ or retire/handoff buffer on CSID alone.** E004pi offline C11 domain gate 95 assertions each GCC+Clang ASAN/UBSAN and SP11 scalar verifier 40 negatives PASS, never included in kernel, separate runtime `-EOPNOTSUPP`. NEXT independent VFE1 WM16 BUS/IRQ/DMA/IOMMU completion with matching owner/frame group8 FIFO and original live event identity before any rear hardware ISP activation. Golden/front native PIX/rear RAW/software4K/IR protected, no camera/boot/kernel/MMIO change.

## E004ph actual type1 BF status input proven CSID BUF_DONE +0x8C bit7 via QUEUE B; NO WM16 DMA completion authorization

[E004ph same-SP11 original callback-queue/CSID BF provenance](experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/README.md) 200 exact original ARM64 ISA anchors/51 negative mutations + original CSID0/CSID1 PE resource names, selectors7/8, SHA-pinned accepted Linux CSID680 source PASS. Original IFE snapshot wrapper0x24A30 is **queue A+0x228/type2**, NOT actual BF type1 record source. Queue B+0x60328 invokes preparer callback0x24380 via thunk0x2AC30 on envelope+0x10; SAME envelope consumed via thunk0x2ACA0 and type1 callback0x243D0. Config-zero preparer0x1B5F0 reads **CSID0/CSID1 BUF_DONE_IRQ_STATUS register+0x8C** through mapped CSID resource window context+0x08 for instances0/1, AND0x07FFFFFF→prepared source+0x0C; normalizer0x1B7D0→type1 record+0x08, BF handler0x1EF90 tests bit7 for conditional event0x0F/FIFO8. Original clear +0x94 and IRQ cmd+0x14, accepted native CSID ISR ALREADY ACKs BUF_DONE. Nonzero preparer0x20B50 AND0x1F removes bit7. Original source format+0xE28 ≠ source-proven same live rear4K worker-mode+0x6B678, no actual BF0x0F occurrence or independent VFE1 WM16 DMA/IOMMU completion. **E004ox TOP1 and E004pb hypothetical queue-A BUS0 status are NOT the discovered queue-B type1 BF source.** Do not map CSID BUF_DONE bit7 to VFE WM16 DMA release, duplicate CSID ack, change real VFE ISR (E004ow noop), arm source-only rear ISP or hand front/rear shared VFE1 ownership. E004ov guard offline, Golden/front PIX/rear RAW+software4K/IR protected. NEXT original live mode/per-frame BF0x0F and independently real VFE WM16 BUS/IRQ/DMA/IOMMU generation-safe stop, not more queue-origin speculation.

## E004pg exact original type1 producer→SOURCE worker ring static identity PROVEN; live BF/DMA still NOT

[E004pg SOURCE command0x0A / worker ring proof](experiments/E004-front-ir-vd55g0/e004pg-original-source-command-a-worker-ring-identity-static/README.md) **93 original ISP ISA anchors/34 fail-closed negatives PASS**. Installer0x19E10 selects SOURCE table+0x30, constructor0x22278 source handler0x22CD0 allocates **0x368-byte ring into source context+0x08 at0x2284C/0x22898**, worker0x23940 dequeues **same context+0x08**. SOURCE cmd0x0A dispatcher0x23120 exports **context+0x08 ring pointer and ADDRESS &context+0x20 notification object**; coordinator0x17F98–0x18024 passes same kind2 interface to DESTINATION table+0x40 cmd0x0B handler0x211B0, installing ring into destination context+0x198 and notify into+0x1A0. Type1 callback0x243D0 enqueues via destination+0x198 into that SAME worker ring *on successful setup*. E004pd's source+0x1B0/unknown-notify claim wrongly used destination handler as source and is SUPERSEDED; original source callback is DIFFERENT. E004pe 0x1D0-byte DESTINATION+0x1B0 ring is unrelated to TYPE1 channel. Historical E004pc/pd/pe/pf READMEs flagged. **No live rear4K BF event/mode, exact snapshot input, BF status bit/ack, actual WM16 FIFO8 per-generation DMA/IOMMU quiescence. E004pb's source-word swap still refutes TOP1 direct BF mapping**. E004ow real Linux ISR stub, E004ov owner guard offline, native rear ISP runtime DENIED; protect Golden/front native PIX/rear RAW/software4K/IR. NEXT original snapshot wrapper→type1 input x1 and mode-selected worker handler, independent native hardware IRQ/stop before rear arm.

## E004pf corrected original command-A SOURCE vs command-B DESTINATION endpoint attribution; E004pe v1 superseded

[E004pf exact same-SP11 source/destination endpoint proof](experiments/E004-front-ir-vd55g0/e004pf-original-channel-source-vs-destination-endpoint-context-static/README.md) **60 original ISA anchors/27 negatives PASS**, cross-check corrected E004pe **74 anchors/32 negatives PASS**. At original0x175F8–0x17610, endpoint being created and whose context+0x1B0 ring is allocated **0x1D0 bytes** at0x17AA4 and stored0x17AF0 is selected from per-instance **table+0x40 (command-B DESTINATION)**, not source table+0x30. At0x17BF4, newly created endpoint object is stored in the selected +0x40 slot. Coordinator0x17FB8 source command0x0A instead uses **table+0x30** and exports *that distinct source context+0x1B0* via core0x214BC; destination command0x0B installs it in destination context+0x198. The old E004pe attribution of its 0x1D0-byte ring to the SOURCE endpoint was WRONG and has been corrected in E004pe README/verify/RESULT v2. Source+0x1B0 ring allocation/consumer and source↔worker device+0x08 exact identity remain untraced. Historical E004pe folder name is not evidence of a source ring. E004pb status copier swap supersedes E004ox direct TOP1 BF hypothesis; no live rear BF or native VFE1 IRQ/FIFO8 WM16 per-generation BUS/DMA/IOMMU retirement. E004ow real ISR noop/E004ov offline owner contract; rear ISP runtime DENIED, protect Golden/front PIX/rear RAW+SW4K/IR.

## E004pe corrected erratum: destination context+0x1B0 has 0x1D0-byte ring, worker device+0x08 separate allocation

[Corrected E004pe v2](experiments/E004-front-ir-vd55g0/e004pe-original-ife-source-ring-independent-allocation-static/README.md) locks original ISA for the **destination** 0x1D0-byte context+0x1B0 allocation and separately allocated worker 0x368-byte device+0x08 ring, not command-A source+0x1B0 allocation. Source channel source+0x1B0→destination context+0x198 pointer handoff remains proven by E004pd. Source+0x1B0 vs worker ring alias, type1 record-to-worker status and physical BF DMA remain unknown; no guessed register writes.

## E004pd original command0x0A→0x0B transfers source+0x1B0 ring to type1 channel+0x198; worker queue alias NOT proven

[E004pd original two-endpoint event-channel pointer-transfer source](experiments/E004-front-ir-vd55g0/e004pd-original-ife-channel-command-a-b-pointer-transfer-static/README.md) **74 original ARM64 anchors/original jump-table decode/25 negatives PASS**. Coordinator0x17F98–0x18028 stamps interface-kind2 in 24-byte stack+0x50, queries source endpoint table+0x30 with command0x0A (core branch0x214BC returns source context+0x1B0 into interface+0x00), passes identical buffer to dest endpoint table+0x40 command0x0B (core branch0x21478 copies interface+0x00 into dest context+0x198 event ring, interface+0x08 into dest+0x1A0 notification). Source of interface+0x08 notification not independently proven by cmd0x0A. **Source context+0x1B0 ring NOT established identical to separately allocated worker device+0x08 queue**; type1 snapshot upstream input/selected rear mode/live BF and real IRQ/FIFO8/WM16 per-generation DMA remain UNPROVEN. E004pb normalization swaps source+0x08/+0x0C so historical E004ox direct TOP1 BF invalid; don't code guessed BUS0 either. NEXT identify source context+0x1B0 pool allocation and exact worker same-object identity, then original snapshot wrapper→type1 status and native VFE1 IRQ/bus/IOMMU DMA fence. E004ow ISR stub/E004ov offline owner contract; runtime rear ISP DENIED, Golden/front PIX/rear RAW+SW4K/IR unchanged.

## E004pc type1 event ring supplied by separate interface kind2; original worker ring alias NOT yet verified

[E004pc original per-context type1 event-channel interface vs worker queue](experiments/E004-front-ir-vd55g0/e004pc-type1-event-channel-ring-alias-unproven-static/README.md) **73 exact original ISP ARM64 anchors/23 negatives PASS**. Original core callback0x211B0 **interface kind2** assigns supplied x21+0x00→type1 producer context+0x198 event ring, x21+0x08→context+0x1A0 notification; **interface kind2 != event-record type2**. Original worker separately allocates device+0x08 queue at0x22830/0x22898 and dequeues at0x23940; type2 external producer directly uses worker device+0x08, but the *type1 channel interface's supplier* and its exact ring pointer alias have NOT been traced. Do not infer source/queue identity from matching 16-byte records or identical numeric offsets in different objects. E004pb type1 copier source+0x0C→BF record+0x08 **supersedes historic E004ox TOP status1→BF register candidate**; both original E004ox and E004pa READMEs now carry explicit correction. BF status source still conditional on exact snapshot input, original live rear mode and native VFE1 BF FIFO8 WM16 IRQ/DMA retirement unproven. Linux ISR stub E004ow/owner model offline E004ov/rear ISP runtime DENIED remain; keep Golden/front PIX/rear RAW+SW4K/IR safe.

## E004pb original type1 producer and source→record word SWAP supersedes older direct TOP1 BF bit7 inference

[E004pb original type1 event producer/copy proof](experiments/E004-front-ir-vd55g0/e004pb-ife-type1-record-producer-normalization-static/README.md): 129 original ARM64 anchors/25 negatives/synthetic distinct-word checks PASS. Original 0x243D0 in module-global0x67138, **separate** from snapshot wrapper global0x67140 and type2 callback global0x67150. Type1 producer pops status-object pointer context+0x1B0, stamps local type1 record, copies incoming x1 using context+0x208 callback selected from independent +0xE28 flag (either0x20CE0 or0x1B7D0), enqueues to context+0x198 event ring and signals+0x1A0. **BOTH copy functions swap source+0x08→type1-record+0x0C and source+0x0C→type1-record+0x08.** Original BF handler reads type1-record+0x08 bit7, so E004ox's direct TOP status1 snapshot+0x08→BF record+0x08 assertion is **superseded by the discovered normalization**. IF same snapshot is input, BF word comes from snapshot+0x0C=BUS status0; actual upstream input and producer→worker ring+0x198 vs device+0x08 identity UNPROVEN. Do NOT code either TOP1 or BUS0 BF IRQ without same-session status provenance/real hardware ack and WM16 DMA lifetime. Earlier E004pa dual TOP register patterns remain valid per callback, but not live BF assignment. E004ow ISR noop/E004ov offline owner model and rear ISP runtime DENIED; protect Golden/front PIX/rear RAW+SW4K/IR. NEXT original type1 and snapshot-wrapper invokers/status buffer/ring identity, native VFE1 BF FIFO8 generation-safe IRQ bus DMA quiescence.

## E004pa different original zero/nonzero IFE TOP IRQ modes; never generalize TOP1 BF bit7 or BUS IRQ ACK

[E004pa original mode-dependent IFE IRQ snapshot register pattern](experiments/E004-front-ir-vd55g0/e004pa-ife-dual-mode-top-irq-layout-static/README.md) 77 original ARM64 anchors/accepted Linux VFE680 SHA/22 negatives PASS. Original modezero0x1DC20 TOP STATUS base+0x44/+0x48 and TOP clear/command+0x3C/+0x40/+0x30 match accepted non-lite layout; nonzero0x1C2B0 TOP STATUS+0x1C/+0x20 and clear/command+0x2C/+0x30/+0x38 match accepted lite layout. BUS-side status and writes differ and neither write sequence is a verified accepted Linux BUS IRQ ack recipe. **Do not infer actual rear4K VFE1's original callback mode, physical lite mapping, live BF0x0F/FIFO8 or WM16 DMA completion from static numerical matching**. E004oz snapshot invoker/type1 producer unknown; source-only E004ov owner model not integrated, E004ow ISR stub unchanged. NEXT original per-session mode/type1 record provenance then actual rear BF FIFO8 per-generation WM16 IRQ/bus/IOMMU DMA fence; keep rear hardware ISP runtime DENIED and Golden/front PIX/rear RAW+SW4K/IR protected.

## E004oz original dual status/type2 callback registration source verified; type1 BF upstream still unknown

[E004oz same-SP11 original ISP callback registration boundary](experiments/E004-front-ir-vd55g0/e004oz-original-ife-dual-callback-registration-static/README.md) **92 original ISA anchors / 22 negatives PASS**. Gated initializer registers snapshot wrapper RVA0x24A30 in global slot RVA0x67140 and separate external-event callback RVA0x24A70 at global slot RVA0x67150. Wrapper calls per-device mode-selected IFE status snapshot slot+0x6B6B0 (mode0 TOP status1→record+0x08); external callback uses slot+0x6B6B8 and creates type2 software event (E004oy). **Actual snapshot-wrapper invoker and original type1 BF event-record producer/exact pointer into event worker remain unverified**; do not conflate type2 or static TOP1 bit7 with live BF FIFO8 and WM16 DMA safe retirement. BUS clear offset discrepancy E004ox unresolved; no guessed IRQ writes. Linux ISR stub E004ow, offline E004ov design and rear ISP runtime DENIED unchanged. NEXT trace registered callback invoker/source status pointer and verified native WM16 IRQ FIFO8 generation-safe DMA, preserving Golden/front PIX/rear RAW+software4K/IR.

## E004oy original type-2 external event producer/ring-worker source VERIFIED, not BF type-1

[E004oy same-SP11 original OEM type-2 software path](experiments/E004-front-ir-vd55g0/e004oy-ife-type2-event-record-ring-producer-static/README.md) 86 exact original ISA anchors and 19 negative tests PASS. External callback0x24A70 stamps type2; obtains object from device+0x33C8 ring, puts local type2 event into distinct device+0x08 event ring at0x24D50; worker0x23940 pops that ring and dispatches via context+0x6B6D8 to modezero type2 handler0x1FECC (software counter0x1FF14/recycle0x1FF44). Does NOT identify different original type1 BF record producer or prove source-backed TOP1 bit7 candidate was live in rear4K, nor physical IRQ/bus/DMA retirement. No Linux ISR integration; E004ov remains offline, rear ISP runtime DENIED, front/Golden/RAW fallback/IR safe. NEXT original type1 producer→snapshot+0x08 and reconcile BUS write mismatch plus real native VFE1 WM16 IRQ/FIFO8 DMA fence.

## E004ox BF original mode-zero TOP IRQ status1 bit7 source candidate; BUS clear mismatch BLOCKS guessed IRQ writes

[E004ox original-SP11 BF status register provenance](experiments/E004-front-ir-vd55g0/e004ox-original-ife-bf-top-status1-register-provenance-static/README.md): 69 original ARM64 anchors/accepted Linux VFE680 source SHA/18 negative tests PASS. Original mode-zero snapshot0x1DC20 stores TOP status1 (base+0x48) at status record+0x08; type1 handler0x1EF90 extracts bit7 of its second record word+0x08 to conditionally emit BF0x0F/FIFO8. Snapshot→exact live type1 pointer identity and rear4K selected mode UNPROVEN: TOP status1 bit7 is source-backed *conditional candidate*, not live DMA fence. Snapshot original BUS-side writes base+0xC3C/+0xC40 DIFFER from accepted Linux BUS clear0/1 base+0xC20/+0xC24. Do not transplant writes, infer IRQ ack or free WM16 buffers. NEXT original event status-record producer and BUS register semantics, then real native VFE1 IRQ/WM16 generation-safe DMA proof. Protect Golden/front PIX/rear RAW+SW4K/IR and keep experimental rear runtime DENIED.

## E004ow native VFE680 real ISR is a stub; no rear BF/WM16 hardware completion producer

[E004ow four SHA-pinned accepted Linux CAMSS files](experiments/E004-front-ir-vd55g0/e004ow-native-vfe-isr-stub-rear-bf-gate-source/README.md): 15 fail-closed tests PASS. `camss-vfe-680.c` hardware `vfe_isr(int irq, void *dev)` body **only returns IRQ_HANDLED**, and real `vfe_ops_680.isr` / `camss-vfe.c devm_request_irq` installs exactly that stub: no hardware VFE status read/ack/WM completion. E003h raw Epoch0/VIDEO snapshot poll recipe retained separately and has NO active ISR/stream caller; preserve existing working front polling path. `camss_rtcdm1_isr` is separate command-engine IRQ, not BF/WM16 DMA completion. E004ov source-only generation guard remains unintegrated; no native rear IRQ/FIFO8 generation producer or bus/IRQ/DMA-safe buffer retirement proven. NEXT independently source-verify native VFE1 BF group8 status/mask/clear/queue per-generation producer and safe WM16 stop, then isolated offline/rollback-safe ISR tests and permitted original rear selected mode/BF live observation; do not bypass blocked KD. Keep rear Linux ISP runtime DENIED, Golden/front PIX/rear RAW fallback/IR protected.

## E004ov offline-only six-group rear owner/frame generation design tested; runtime remains DENIED

[E004ov standalone strict C11 anti-stale rear stop guard](experiments/E004-front-ir-vd55g0/e004ov-rear-six-group-generation-ownership-offline/README.md) is **D/design**, not proof of hardware IRQ/DMA. Existing E004nv source-only group ack does not accept frame/owner epochs or per-group queued-entry identity; prospective stale-completion risk caught before ISR integration. New never-integrated standalone guard requires source-verified external owner/frame/queue identity and IRQ/FIFO/DMA inputs for each completion, all six groups and separately verified source/WM-bus/IRQ/DMA/IOMMU same-generation stop before modeled retire; normal and ASan/UBSan strict C11 **each pass 720 completion permutations/62,655 assertions** with simulated evidence. Existing three CAMSS front-critical sources and original E004nv group map pinned; no kernel include, firmware, camera, boot or Golden modified. Real rear BF0x0F/live IFE mode and hardware evidence providers remain UNPROVEN; never set design proof predicates from 0x805/0x809 stop returns, type-2 count or KeSetEvent. Keep source-compiled Linux rear ISP runtime DENIED and front native PIX/rear RAW fallback/IR safe. NEXT native VFE1 IRQ/FIFO8/per-generation WM16 hardware retirement.

## E004ou mode-zero type-2 record software count is not BF group8/WM16 DMA retirement

[E004ou source-locked same-SP11 original ISP mode-zero event type distinction](experiments/E004-front-ir-vd55g0/e004ou-ife-event-record-type2-not-bf-wm16-retirement-static/README.md): 79 original ARM64 anchors and 16 negative tests PASS. Type-1 input status-word2 bit7 conditionally emits BF0x0F, pops FIFO8, and BF callback reads WM16 original-base+0x1E00/+0x1E70 (mode0). Separate type-2 event record uses flags+0x0C, optional selected-window+0x64/+0x70 diagnostic reads (**base+0xC64/+0xC70**, NOT WM16 BF registers), LDAXR/STLXR software counter decrement, zero-counter record clear and optional software queue helper0x2BEF8 (not BF dequeue0x26460). Neither counter nor diagnostic read proves BF DMA/IRQ retirement; actual hardware IRQ source/ack, live rear BF event and selected mode unverified. NEXT trace upstream type-1 event producer/IRQ ack and BF FIFO8→WM16 per-generation buffer retirement. Preserve Golden/front PIX/rear RAW fallback/IR; rear Linux ISP remains runtime DENIED.

## E004ot IFE1 selector 1 and accepted Windows rear VFE1 live route MUST NOT be confused

[E004ot original same-SP11 OEM resource names and fourth lookup case](experiments/E004-front-ir-vd55g0/e004ot-original-ife-resource-name-four-selector-static/README.md): 73 original ARM64 anchors/four original PE descriptor-label strings/four source jump-table entries/16 negative tests PASS. Original lookup0x2B568 maps selectors 0→IFE0, **1→IFE1**, 2→IFELITE0, 3→IFELITE_CDM0; old E004or checked 0/2/3 but did not exclude 1. Independently established **P/live E004nq rear Windows 4K VFE1 ACTIVE/VFE0 INACTIVE**, despite older E004nl Linux source-only VFE0-first idea; preserve VFE1 exclusive owner shared with native front PIX. What remains unproven is original live rear IFE callback's selected index/base/mode, BF0x0F FIFO8 and WM16 IRQ/DMA retirement. Do not infer selected Windows context from names or force the rear Linux driver. Protected Golden/front native PIX/rear RAW+SW4K/IR and runtime-denied Linux rear ISP intact.

## E004os IFE original resource arrays originate in MmMapIoSpaceEx, not DMA stop proof

[E004os original same-SP11 ISP mapping producer](experiments/E004-front-ir-vd55g0/e004os-ife-original-mmio-map-resource-array-producer-static/README.md): 97 exact original ARM64 instructions, original `MmMapIoSpaceEx` vs `MmUnmapIoSpace` IAT check and 16 negative tests PASS. Resource-table global0x4AEE0 fields+0x50/+0x20 are allocated arrays conditionally populated with four descriptor-match `MmMapIoSpaceEx` return pointers from descriptor start+0x18, length+0x20; IFE original lookup0x2B568 chooses their first/second entries for context+0x140, then mode+0xC00/+0x1200 yields selected window+0x150. This proves *static original MMIO pointer provenance*, not which physical VFE1 instance the live rear4K selects, successful live mapping, BF0x0F or WM16 IRQ/DMA retirement. NEXT map selected resource name/physical device and independent WM16 bus/IRQ/per-buffer retirement; no rear runtime arm or blocked KD attempt. Golden/front PIX/rear RAW fallback/IR protected.

## E004or IFE register-base software pointer provenance source-verified, not physical VFE1

[E004or same-SP11 original ISP base lookup](experiments/E004-front-ir-vd55g0/e004or-ife-register-window-provenance-static/README.md) verifies 93 exact original ARM64 instructions, three source-decoded PE jump-table entries and 16 negatives: IFE init calls resource lookup0x2B568, selecting global resource-table RVA0x4AEE0 field+0x50 first pointer for selector0 or field+0x20 first/second pointer for selectors2/3, stores base at context+0x140 and selects window at +0x150 by base+0xC00 (mode zero) or +0x1200 (nonzero). Source-derived original finalizer offsets are +0xC18/+0xC1C/conditional +0xC08 versus +0x1218/+0x1208. Actual live rear4K selected physical VFE1 base, global resource-table population, BF0x0F WM16 DMA retirement remain UNKNOWN. NEXT map global resource-table pointer producers to mapped physical IFE instance and independent IRQ/bus per-buffer DMA completion. No rear ISP runtime activation; protect Golden/front PIX/rear RAW+SW4K/IR.

## E004oq actual original IFE finalizer callbacks are mode-specific register writes, not DMA fences

[E004oq same-SP11 original ISP finalizer source](experiments/E004-front-ir-vd55g0/e004oq-ife-mode-selected-finalizer-register-writes-static/README.md): 94 exact original ARM64 instructions/two PE function entries/14 negative tests PASS. IFE context+0x6B678 zero-state selects finalizer RVA0x1D2B0, nonzero-state RVA0x1BE80, stored context+0x6B690 and invoked from E004op stop helper0x27358. Both bounded callback bodies write different original base/selected register-window offsets and call software-bookkeeping helper0x1C958; neither directly validates WM16 DMA quiescence or IRQ retirement. Live rear Windows mode/base/BF event remain unproven. NEXT independent original register-window/WM16 bus/IRQ/DMA stop acknowledgement and active Windows rear selected mode before any native Linux rear hardware ISP activation. Do not free DMA on callback return/event. Preserve Golden/front native PIX/rear RAW fallback/IR; rear compiled Linux ISP runtime DENIED.

## E004op distinct original IFE stop-progress flags and two software events

[E004op original same-SP11 ISP flag producer](experiments/E004-front-ir-vd55g0/e004op-ife-stop-pending-flag-two-event-modes-static/README.md): 50 exact original ARM64 instructions + four PE entries + 14 negative tests PASS. Bounded IFE stop helper sets software active context+0x173, after selected finalization callback +0x6B690 sets pending context+0x171=1, and signals KeSetEvent on context+0x38. Separate mode-one0x1C9D0 and mode-zero0x1EF90 handler branches clear that flag and use later helper signalling **different context+0xC8 event**. Neither signal independently proves live rear4K path, BF0x0F, WM16 bus/IRQ or DMA retirement. NEXT trace +0x6B690 callback's actual physical ack and independent selected Windows mode; do not free/handoff on flags/events. Keep Golden/front native PIX/rear RAW/software4K/IR protected; experimental rear Linux ISP runtime-denied.

## E004oo IFE later-progress event is KeSetEvent, no DMA-stop inference

[E004oo original same-SP11 ISP later IFE event](experiments/E004-front-ir-vd55g0/e004oo-ife-later-progress-event-not-dma-ack-static/README.md) checks 60 exact original ARM64 instructions, all 33 instructions of helper RVA0x241D8 and three source-resolved original imported API slots, with 11 fail-closed negatives. Conditional context flag+0x171 is cleared before calling helper; wrapper RVA0x2A1D8 invokes original imported **KeSetEvent**. This is SOFTWARE EVENT signalling, not an independent WM16 DMA/IRQ bus drain or buffer fence. Other hardware-driven callers may exist; do not claim entire stop sequence lacks a hardware ack. NEXT trace flag producer and independent BF/WM16 per-buffer bus/IRQ retirement, live rear selected IFE mode. Preserve Golden, front PIX, rear RAW+software4K and IR safeguards; source-compiled experimental Linux rear ISP runtime remains denied.

## E004on three concrete 0x809 first callbacks do not acknowledge physical stop

[E004on original same-SP11 ISP first callback source](experiments/E004-front-ir-vd55g0/e004on-isp-selector-809-three-concrete-core-receivers-static/README.md): E004og-installed CSID/IFE/CDM first callback valid-input 0x809 paths source-checked at 57 original ARM64 instructions + 13 negatives. CSID default diagnostic status 0, IFE default status 0 **without** 0x805 IFE stop helpers, CDM unsupported-selector status 0x0E. Conditional [S], no claim that live rear Windows 4K selects any of them. Neither zero return nor 0x809 is physical WM16 DMA/IRQ quiescence; never release buffer or switch native Linux shared-core owner from these selectors/statuses. NEXT independent IFE later progress/bus/IRQ/WM16 DMA retirement and live rear selection evidence; maintain source-compiled rear ISP runtime DENIED and protect Golden/front/rear RAW fallback/IR.

## E004om conditional manager per-core list writer identified, no live rear inference

[E004om same-SP11 ISP manager list](experiments/E004-front-ir-vd55g0/e004om-isp-manager-core-list-producer-static/README.md) 80 original ARM64 instruction anchors and 17 fail-closed tests PASS: conditional 0x802 hardware-descriptor configuration can append two paired descriptor indices or one selected index to manager indexed words starting at six and increments manager +0x24 count. E004ol 0x809 generic dispatch reads the SAME record/count. Count-nonzero branch skips the checked builder; not all producer/teardown cases are closed. Actual live rear4K configured core IDs, callback semantics, IRQ/BF/WM16 DMA retirement remain unproven. NEXT trace actual 0x809 branch/return of concrete E004og CSID/IFE/CDM first callbacks and independent physical stop. Preserve Golden, front PIX, rear RAW/software fallback, IR privacy; experimental rear Linux ISP remains runtime DENIED.

## E004ol selector0x809: generic default forwarding, not a decoded stop command

[E004ol original same-SP11 ISP source](experiments/E004-front-ir-vd55g0/e004ol-isp-selector-809-independent-dispatch-static/README.md) independently traces 0x809 through dedicated-case fallthrough into manager generic/default branch RVA0x1932C; eligible configured core callbacks receive original w1=0x809. 58 exact original ARM64 instruction anchors + 12 fail-closed checks PASS. Generic list starts at manager index six, but actual live rear VideoRecord selected cores, receiving callback bodies and 0x809 argument/return/hardware semantics remain UNKNOWN. Do not equate with 0x805, a physical stop, or DMA buffer retirement. Signed >=4 ID guard is not proof of nonnegative IDs. Next find exact generic-list producers/receivers; independently trace IFE/WM16 IRQ/bus/DMA stop and live selected rear profile. Linux rear native ISP remains runtime-denied; Golden/front PIX/rear RAW fallback/IR safe.

## E004ok immediate BF stop callback is NOT physical WM16/DMA retirement

[E004ok source-only original ISP trace](experiments/E004-front-ir-vd55g0/e004ok-bf-stop-cfg0-postwrite-software-state-static/README.md) establishes that the conditional BF0x300D WM16 CFG0 zero-write at original RVA0x1DA74 branches to a common tail and entire 16-instruction helper RVA0x1C990–0x1C9CC, which only updates original context mapping/software status. Valid resource flag update/return and the outer IFE loop also do **not** provide a hardware IRQ/DMA completion acknowledgement. Exactly 47 original ARM64 instructions + 12 fail-closed checks PASS, **static-only**. Next independently source-trace later IFE progress/event and BF/WM16 bus/IRQ/queue buffer-retirement; confirm live rear Windows selected instance/mode separately. Never free WM16 DMA or switch Linux shared PIX owner based solely on CFG0 zero or callback return. 0x809 independently unknown. Protected Golden, front native PIX, rear RAW/software4K, IR safeguards unchanged; experimental Linux rear ISP still runtime-denied.

## E004nz OEM AVStream camera-engine handoff — next reverse-engineering slice

The same-SP11 `surfacecamavs8380.sys` has now been independently
verified **statically** at 66 exact ARM64 instruction anchors, see
`experiments/E004-front-ir-vd55g0/e004nz-avstream-profile-control-static/README.md`
and `RESULT.json` and rerunnable `verify.py` (17 negative cases).
Not merely a list of Windows drivers: we pinned AVStream preview/still/
video/stats pin handlers, single-active-filter policy, privacy state,
CameraEngine OnStart/OnStop, actual separate user-mode sensor timing
and profile/processing CONFIG packet path, separate PER-REQUEST packet,
and separate ISP notification worker. Windows INF **registers**
QcDeviceMFT8380.dll but its actual involvement in the rear recording
is UNPROVEN; OEMCameraProfiles syntax in that INF is COMMENTED EXAMPLE.
CCameraEngine engine start RVA0x1efd0 / stop RVA0x1f130 both call
indirect helper RVA0x20da8 with potential ordered selector sites
0x804,0x804,0x5,0x17 (start) and 0x805,0x809,0x805,0x18 (stop).
These NUMERIC VALUES ARE **NOT DECODED COMMAND MEANINGS OR LINUX
IOCTLS**. Do not port them until the helper's backing interface and
actual platform/ISP/sensor recipient have source-backed mapping;
branches may skip certain command calls. Source code proves Windows
separately handles IFE and sensor stop and timing-aware user-mode
control without requiring a Windows AI/effects pipeline. Linux kernel
must preserve hardware safety/ISP/DMA ownership; optional 3A/IQ policy
may be small open libcamera IPA / explicit standard user controls.
The E004nv mode0 BF branch, live rear BF and Linux native4K ISP frame
remain unproven; no new runtime code loaded, Golden untouched.

## E004oa backend interface — next Windows→Linux source slice

The original same-SP11 AVStream CameraEngine's common dispatcher now has
a SOURCE-VERIFIED **external Windows kernel-device interface acquisition**
path, see
`experiments/E004-front-ir-vd55g0/e004oa-avstream-kernel-interface-bind/README.md`.
Exact OEM SHA pinned, 42 ARM64 instructions + five Windows IAT mappings
+ two engine virtual-table entries + 12 negative mutations pass.
Engine→binder RVA0x20b60 actually calls IoGetDeviceInterfaces,
IoGetDeviceObjectPointer, then internal device-control
**opaque request code 0x002326AB** with 8-byte output via
IoBuildDeviceIoControlRequest/IofCallDriver; chosen backend interface
record later feeds engine common indirect dispatcher RVA0x20da8,
which calls the returned vtable or alternate callback. This proves
there is an external driver interface; it does **NOT** identify the
active rear-session device-interface identity, receiving
qccamplatform/qccamisp/sensor driver, selector meanings, nor live BF.
E004nz engine start/stop selector numbers must NEVER be treated as
Linux commands until original OEM receiving handler/request ABI
is matched. NEXT static trace: original OEM device-instance interface
identity + receiver for 0x2326AB, then hardware-only necessary
sensor/ISP command lifecycle. No Windows services/AI needed for native
Linux hardware safety. Golden/front/native27/rearRAW/software4K intact.

## E004ob actual matching OEM interface-code receiver branches

E004oa's source-verified opaque internal request0x2326AB is NOT
a unique marker for one camera backend! The next static audit
`experiments/E004-front-ir-vd55g0/e004ob-dual-backend-ioctl-static/README.md`
and `verify.py` source-locks originals qccamplatform8380.sys and
qccamisp8380.sys (20 exact ARM64 receiver instructions, both OEM
SHA256, 12 fail-closed mutations). Platform matches same code at
RVA0x6334→0x6364 and clears a state flag/two fields; ISP matches
at RVA0x5638→0x566c and populates its pointer/flag/callback.
Do NOT equate those structures/semantics or presume both received
one request. **LIVE rear VideoRecord selected interface and receiving
driver unverified.** Next map AVStream binder's device-instance
interface identity to original platform/ISP/sensor registration;
only then decode the opaque OnStart/OnStop selectors into real
hardware effects. Current source-only audit changes no Golden,
front native27, rearRAW/software4K, IR or Linux rear native4K status.
Do not port Windows orchestrator, hidden .sys/.dll code or AI effects.

## E004oc closes static backend-GUID routing, NOT callback semantics

[E004oc device-interface routing](experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/README.md) SHA-pins original same-SP11 OEM Windows binaries and **nine** AVStream table identities; **seven** have independently checked original provider registration-code call sites. The correct static provider mapping is **rear sensor slot 1, front sensor slot 2, ISP slot 4, shared platform slot 5**, flash slot 0, auxiliary slot 3, secure ISP slot 8. Slots 6–7 remain UNKNOWN in the scoped archive. The ISP, rear and front sensors also **query** the platform-common GUID, which is **registered** by the platform driver: do not mislabel consumers as duplicate providers. One opaque 0x2326AB request appearing in both platform and ISP does not mean it broadcasts a single command.

**Live rear VideoRecord selected identity remains UNKNOWN**, as do the original returned callback implementations/selector argument ABI, true BF/WM16 DMA retirement and native Linux rear ISP4K optical frames. Next only source-trace **ISP slot-4, rear sensor slot-1 and platform slot-5 returned interfaces**, then map physical effects into independent Linux CAMSS L0–L3. No Windows Frame Server/AI/effects dependence; no numeric Windows engine selector promoted to a Linux command without source-backed receiver evidence.

## E004oc ISP nested callback source proof — do not name Windows selectors yet

The original same-SP11 ISP matching interface-acquisition branch sets callback RVA0x4E30. Only if the AVStream alternative-dispatch path is selected, its engine selector is passed to that ISP callback. Source-locked original ARM64 code at ISP RVA0x50C4–0x5210 sends selector values 0x804/0x805/0x809 to a **SECOND, currently unidentified callback interface at ISP state/context +0x10**. Proof: experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/verify_isp_callback_delegation.py (24 exact instruction anchors) and README addendum. Do not map these numbers to native ISP/sensor start/stop or assume this was the actual rear video runtime path. The next static dependency is the nested callback producer and its actual receiving hardware request ABI. Protect original Golden/front/rear RAW fallback, no Windows AI/effects port.

## E004od resolves the ISP hardware-manager callback, but NOT core-side MMIO semantics

The prior ISP context +0x10 callback UNKNOWN is now resolved in original same-SP11 OEM source: ISP context initialization at RVA 0x6A0A0 passes +0x10 to a 16-record pool helper RVA 0x15A40, which installs a real callback **RVA 0x15D70**. The hardware-manager callback distinguishes 0x804 and 0x805, forwards them to different per-core interface arrays with conditional error paths, and does not directly prove the physical IFE/CSID/CDM per-core implementation, Linux-equivalent register order or actual runtime selection in Windows rear VideoRecord. 0x809 is separately UNKNOWN. See experiments/E004-front-ir-vd55g0/e004od-isp-hw-manager-nested-start-stop-static/README.md and 50 original ARM64 source anchors/16 negative tests in verify.py. Next trace ISP HW-manager per-core receiving IFE/CSID/CDM callback implementations and parameter ABI; port only independently verified hardware effects. Keep Golden native front/rear RAW fallback protected, no Windows AI or opaque command transplantation.

## E004oe: verified ISP-manager core dispatch order, NOT physical stop acknowledgement

[Same-SP11 original ISP E004oe analysis](experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/README.md) checks 55 exact original ARM64 instructions, six distinct diagnostic-hash/code-xref stage identities and 13 fail-closed mutations. Conditional selector 0x804 branch source software dispatch **CDM→IFE→CSID**; 0x805 branch **CSID→IFE→CDM**. These stage labels are now source-backed in the manager; their receiving per-core callback implementations/ABI and physical hardware register/IRQ/DMA completion are NOT identified. 0x809 and live rear Windows 4K session path also remain UNKNOWN. Next static only: identify CDM, IFE, CSID interface array producers and lower callback bodies; don't encode opaque Windows selectors into protected Linux Golden. No Windows AI/effects dependence or native rear4K claim.

## E004of exact per-core interface provenance — next function-body boundary

[E004of](experiments/E004-front-ir-vd55g0/e004of-isp-per-core-interface-provenance-static/README.md) source-locks original ISP core-array allocators 0x3918/0x15768, dynamic descriptor lookup 0x156E8, and 0x30-byte per-core records populated with independently obtained callable pointers at 0x698A8, then read/checked/indirectly called from E004oe's CDM/IFE/CSID manager. 56 exact original ARM64 anchors + 15 negative tests PASS; all static only. NEXT: locate actual first callback function bodies in the core descriptors; verify argument and physical MMIO/interrupt/DMA lifetimes before implementing native Linux L0–L3. No live rear profile, 0x809, BF/WM16 retirement or Linux-native rear ISP4K proven. No opaque Windows interface/effects transplant or Golden runtime changes.

## E004og original CSID / IFE / CDM *actual* callable functions now identified

[Exact same-SP11 original ISP first core callback functions](experiments/E004-front-ir-vd55g0/e004og-original-isp-three-core-callback-implementations-static/README.md): original init code stores CSID RVA0x211B0 at 0x176A4, IFE RVA0x22CD0 at 0x2234C, and CDM RVA0x28480 at 0x1835C into their respective original core interface slots. All three are independently original PE function-entry metadata and each has explicit 0x804/0x805 dispatch, source-locked with 45 ARM64 instruction checks and 14 negative tests. Original IFE 0x805 branch calls separate stop helpers RVA0x221A0 and 0x27278; CSID and CDM have distinct worker/event/state progress paths. **Those are static installed original function bodies, NOT live rear session execution nor proof of VFE DMA/WM16 safe physical retirement**; do not infer source-only group8 BF event live. Next source trace IFE stop helpers, CSID stop worker and CDM event/hardware completion and per-mode DMA/IRQ before runtime-changing Golden. No Windows command/code/AI port.

## E004oh original multistage stop: never free DMA on the outer callback alone

[E004oh original same-SP11 ISP source proof](experiments/E004-front-ir-vd55g0/e004oh-isp-multistage-stop-progress-static/README.md) traces the concrete IFE 0x805 receiver through two distinct stop helpers 0x221A0 and **bounded per-resource stop helper 0x27278**, plus separate later IFE progress path 0x1F230/event helper 0x241D8. Original CSID also has separate atomic pending-work decrement RVA0x1BCCC and worker/event stop RVA0x21B00; CDM its own command state/event. 45 actual original ARM64 anchors and 14 fail-closed tests PASS, static only. **Do not interpret CSID pending zero, IFE stop callback return, or CDM event progress as hardware VFE WM16/DMA/IRQ quiescence**. NEXT trace IFE per-resource indirect callback in 0x27278 to original VFE/WM stop/ack and actual frame/stats buffer ownership. No Windows AI/Frame Server, original OEM binary transplant, Golden camera activation or 4K-native rear proof.

## E004oi actual IFE resource callback is mode-selected and BF-port aware

[E004oi source-locked original ISP resource callbacks](experiments/E004-front-ir-vd55g0/e004oi-ife-resource-callback-bf-port-static/README.md): original IFE init tests +0x6B678 state and chooses **0x1C0F0 for nonzero, 0x1D830 for zero**; stores chosen original PE function into IFE +0x6B688 at 0x19FE8. E004oh bounded stop loop at 0x27278 reads SAME field at 0x272E4 and invokes with resource ID and stop flag zero. **The zero-state alternate callback 0x1D830 explicitly branches for BF-associated resource 0x300D**. Static-only 35 original instruction anchors and 16 negative tests; do not assume live rear 4K selects zero state or that BF FIFO8/WM16 DMA completed. Next trace 0x1D830 BF resource+stop flag 0 to specific VFE bus register/IRQ/WM16 safe retirement, validate active rear session, preserve Golden/native front and RAW fallback. Do NOT transplant Windows selector/AI/effects stack.

## E004oj conditional BF0x300D IFE stop-zero write matches original WM16 CFG0 offset

[E004oj source-verified original IFE register math](experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/README.md) proves the IFE zero-state callback uses original register base+0xC00; the E004oi bounded 0x805 stop helper calls this handler for resource 0x300D with zero flag; original switch-table entry 13 selects RVA0x1DA6C which writes zero at chosen window+0x1200. Thus **original register base+0xC00+0x1200 = base+0x1E00**, matching independently E004nv BF/WM16 CFG0 relative offset. 35 exact original ARM64 instructions and original jump-table source plus 14 negative mutants. Static conditional register write != proof actual live Windows rear4K selected this mode/base, BF0x0F FIFO8 event, IFE bus stop/WM16 safe DMA retirement or Linux rear ISP4K optical pixels. NEXT source-check original post-write WM16 bus/IRQ/queue stop and live selected rear4K mode before Linux runtime arm; no direct Windows command/AI transplant, Golden preserved.

## Mission

Develop a native Linux camera stack for Surface Pro 11 (Denali/X1E80100) with the same evidence discipline used for the successful SP11 audio work. Windows on the same hardware is the behavioural oracle. The objective is native Linux implementation, not wrapping or redistributing Windows drivers.

## RGB product priority (latest user decision, 2026-09-23 ~19:36 BST)

User EXPLICITLY selected the previously optional SECOND route:
resume native Qualcomm Spectra hardware ISP / SAME SP11 Windows
OEM camera stack as the engineering oracle to seek improved real
front1080/rear4K image detail, color and brightness. This decision
SUPERSEDES the earlier software-FIRST / ask-before-ISP wording
below. The proven opt-in Linux RAW10-to-NV12 software camera
(E004ne last complete original acceptance) is RETAINED as a
fallback and for safe baseline comparison, not silently promoted
to final Windows-parity production. CORRECTION: E003i-HY
physically captured 27 REAL hardware-generated front VFE1 PIX
QC10C frames under protected Golden; E003i-Z previously passed
six actual native front AEC/BHist/AWB generation-matched stats.
Windows-equivalent FRONT colour/detail/true linear NV12 and
any REAR hardware-ISP processed 4K image are NOT proven.
The earlier E003h initial PIX first-frame attempts failed but
do not invalidate LATER successful E003i front evidence.
Front IQ materializer is a source reference, NOT independently
a working rear OV13858 service. Read both source-only
audits FIRST:
experiments/E004-front-ir-vd55g0/e004nj-icp-firmware-host-compatibility-readonly/README.md
experiments/E004-front-ir-vd55g0/e004ni-native-isp-windows-rear-oracle-source-audit/README.md.
Do not blindly load Xtensa Windows CAMERA_ICP firmware
with Linux Q6 AUDIO remoteproc. Linux currently has
ADSP/CDSP only and the checked CAMSS source firmware
requests are HOST IQ capsules, not an ICP loader.
Re-use ACTUAL validated E003i native front PIX QC10C/
3A hardware evidence for a source-locked OV13858
REAR-specific native PIX first-frame design, NOT
as if front tuning or the rear processed frame
were already proven.
The installed MSHW0491 rear OV13858 selects its OWN Windows
sensor module and tuning; do not confuse with MSHW0561 or front
IMX681 package, nor try to run Windows PE .sys/.dll as Linux
drivers. Windows binaries/firmware, optical photos/pixels/RAW/
thumbs/image hashes never enter Git/chat/other hosts.
All existing Golden one-shot source-pin, >=29fps each actual
gain window, complete native neutral, IR OFF and NO Linux
OS-level sleep rules remain mandatory. Do not enable a default
native ISP or flash unverified Windows firmware.


## E004nq rear-native Windows route supersedes rear RAW parity assumption

2026-09-23 E004nq physically captured TWO same-SP11 Windows Rear OV13858
VideoRecord 3840x2160 sessions using the **original working front E003g
SP7 KDNET `dd /p` PHYSICAL register command** at IDLE/LIVE1/POST/LIVE2/POST2.
The later E004nm `!dd` was NOT the same physical acquisition and its
all-0x80000000 camera values must NOT block hardware work.
E004nq's five-phase/repeated OEM proof shows Windows REAR uses:

- CSIPHY1, **4 D-PHY lanes**, CSID1 RAW10 IPP crop **x0..4063/y0..2285**
  (4064x2286, GRBG Bayer phase unchanged);
- shared VFE1 FULL WM0 luma 3840x2160 and WM1 chroma 3840x1080,
  **physical WM stride 5120**, packer reg0x0b, plus DS4/DS16 and stats;
- CSID0 IPP disabled and VFE0 inactive in BOTH actual Windows rear PIX
  capture passes. Both stopped states return exactly to all-sentinel idle.

Front E003g ALSO uses CSID1/VFE1, but has IMX681 C-PHY CSIPHY2,
input crop3840x2160 and output2560x1440: the two OEM camera modes
**time-multiplex the same processing cores** with distinct CSI and IQ
profiles. Preserve the existing Linux rear CSIPHY1→CSID0→VFE0 RAW
E004lr diagnostic capture and E004ne SW4K fallback: they are REAL,
but NOT Windows rear native ISP parity. Historical E004nk/E004nl rear
VFE0 source preflight/route must not be used as a *Windows native rear
4K processed route gate*. Do NOT copy front-only predicates, tuning,
2560x1440 QC10C output or MF app stride3840 into new rear hardware.
New Linux rear PIX must have separately source-locked CSI1/VFE1
graph ownership, 4K hardware output surface, OV13858 Bayer crop, IQ/
RT-CDM/3A scheduling, checked DMA/SMMU and Golden-safe cleanup;
**Linux rear native 4K ISP frame remains unproven**. The reusable E003g
method is physical `dd /p`, not a dependency on private OEM WPP/TMF
decoders. See E004nq README.md/RESULT.json/WINDOWS-RESULT.json/verify.py.

## E004nr compiled rear native-ISP source-only profile (NOT an arm gate)

The next Linux rear native-ISP graph/profile is now real **compiled ARM64
CAMSS kernel source**, independently staged against the existing integrated
CAMSS base instead of changing the deployed Golden or accepted front path:
`experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/`.
It rejects any sensor other than physical rear OV13858 GRBG4076x2806
CSIPHY1 four-lane D-PHY linked to **CSID1 PIX → VFE1 PIX**; it is
not the still-useful diagnostic rear CSID0/VFE0 RAW media graph.
E004nq-proven Windows rear IPP 4064x2286 x0/y0, FULL Y3840x2160,
C3840x1080, physical WM stride5120 packer0xb are separate from the front
IMX681 QC10C profile. New SP7-private-KD whitelisted WM two-live-pass
registers show WM0 frame-incr0x00a9d000, WM1 frame-incr0x00559000,
FULL metadata cfg0x800, WM modes0x23/0x33; this still does NOT prove
a safe Linux DMA/UBWC allocation/IOVA/V4L2 buffer format or IQ.
`camss_e004nr_rear_pix_runtime_authorization` unconditionally returns
`-EOPNOTSUPP`; no runtime caller/module parameter was added.
The isolated new qcom-camss module was actually compiled and validated,
but it was NEVER installed/loaded/booted. The original integrated
CAMSS camss.c is byte-identical and the accepted Golden/front sources
are not changed. See E004nr verify.py and README.md for source-lock
checks and 15 fail-closed negative tests; do not rerun an already-used
staged build directory without an independently new source identity.
NEVER promote the source-only rear profile to live hardware without
separately establishing 4K buffer metadata/IOMMU ownership, sensor IQ/
3A/RT-CDM packet lifecycle, and safe exclusive shared CSID1/VFE1
front/rear switching. A Linux-native rear 4K optical ISP frame is
**still unproven**.

## E004ns source-only compiled rear CSID1 IPP register configuration

A NEW isolated ARM64 kernel build now includes real rear-only CSID1 IPP
mode/receiver-word/prepare/enable routines from
`experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline/`.
The code is compiled with the prior E004nr rear graph check but **has NO
caller in any runtime path**; authorization always returns
`-EOPNOTSUPP` and no module is installed/loaded on protected Golden.
Both original E004nq Windows rear KD LIVE1/LIVE2 samples match ALL 26
whitelisted CSID1 configuration dwords. Rear `RX_CFG0=0x10232103`
contains `TPG_NUM_SEL=1` despite FOUR-lane D-PHY; the existing
`__csid_configure_rx()` only sets that bit for the front C-PHY, so it
MUST NOT be reused unchanged for rear. Rear IPP register +0x330 is
`0x02000000` (front companion writes zero); rear HCROP x0..4063,
VCROP y0..2285; +0x388 is **IPP_FORMAT_MEASURE_CFG1** configured
expected dimensions 4064x2286, NOT an independently observed
completed-frame width/height register. See E004ns README.md/verify.py
for 17 negative tests, isolated module SHA and source preservation.
Only final LIVE register targets, not OEM startup order, were observed.
Do NOT connect rear prepare/enable to front code, probe, V4L2 or sysfs
until independently implemented 4K FULL Y/C+metadata/IOMMU-safe buffer
surface, RT-CDM/IQ/3A lifecycle, rear-specific startup order,
CSID1/VFE1 front/rear mutual-exclusion and Golden-safe rollback are
validated. Existing front E003i, Linux rear E004lr RAW and E004ne
software fallback remain unchanged.

## E004nt compiled rear 4K VFE1 coherent-DMA surface — still offline

A NEW source-only isolated ARM64 CAMSS build, E004nt at
`experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract/`,
retains original E004nr graph and E004ns rear IPP and adds actual
compiled Linux rear VFE1 FULL Y/C surface alloc/address/free routines.
SP7 PRIVATE E004nq Windows rear LIVE1/LIVE2 register snapshots gave
the identical RELATIVE layout: Ymeta=0, Ydata=0x11000,
Cmeta=0xA9D000, Cdata=0xAA6000, frame increments Y0xA9D000,
C0x559000, combined output window0xFF6000=16,736,256 bytes,
both WM physical stride5120. NO Windows DMA address or optical bytes
were exported; only relative geometric offsets were committed.
Linux source uses the ACTUAL CAMSS device for a single coherent
DMA allocation, verifies whole 4K-aligned IOMMU DMA aperture fits in
the 32-bit VFE registers, compile-time bounds metadata+row coverage,
and refuses address-rebind/free in-flight. **This is NOT already
allocated, NOT a V4L2 NV12 format, NOT UBWC metadata correctness**.
`vfe680_e004nt_rear_4k_runtime_authorization` still ALWAYS
returns `-EOPNOTSUPP`; no source caller, module installation,
Golden boot mutation, real device DMA allocation or rear native 4K
optical frame has occurred. Existing front 27-frame E003i, rear RAW
E004lr and software4K E004ne implementations remain intact.
The new qcom-camss module compiled cleanly in a unique isolated
directory, NOT installed/loaded; see E004nt README/verify.py for
actual module SHA, byte-for-byte original-source preservation and 18
negative tests. Next integrate rear-only VFE1 WM programming,
exclusive CSID1/VFE1 ownership, ISP IQ/RT-CDM/3A and safe hardware
retire before ANY Golden-safe live rear 4K native optical-frame test.

## E004nu rear VFE1 BUS ten-client source-only implementation

The new independently compiled ARM64 CAMSS experiment
`experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/`
incorporates all prior E004nr graph/E004ns rear CSID1 IPP/E004nt coherent
4K buffer source-only gates and adds a distinct ten-WM rear VFE1 BUS
static configuration and conservative candidate per-client frame lifecycle.
Windows rear had WMs 0,1,2,3,11,12,13,14,**16**,18 in BOTH live
recordings; the working front BUS recipe only has nine, OMITTING the
active rear WM16 BAF autofocus stats. DO NOT reuse front's nine-master
configuration for rear. New rear code checks all ten existing enable
bits BEFORE writing anything and writes only STATIC config fields with
WM enables cleared, and NO Windows/Linux DMA image/meta addresses.
The ten-client frame model refuses buffer release until all ten verified
master completions (including WM16) and independent HW BUS STOP.
**Actual rear WM16 completion event/group mapping remains UNKNOWN,**
so DO NOT connect this model to any real ISR, deem a front VIDEO event
sufficient, or free a timed-out in-flight buffer. The rear-only runtime
authorization still unconditionally returns -EOPNOTSUPP and the new
source has NO callers in the active Golden kernel. The isolated kernel
module was actually compiled with zero warnings/errors and verified
against exact two-phase rear WM nonpointer physical evidence, 20 negative
tests and byte-identical original front CAMSS/CSID/VFE source.
No module installed/loaded, no camera activated, no DMA allocated,
and Linux native rear 4K ISP optical frame is still UNPROVEN.
See E004nu README, verify.py and BUILD-RESULT.json.

## E004nv OEM static BF completion group8, six-group rear candidate

The NEW isolated same-SP11 E004nv
`experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/`
recovered a previously-unexercised OEM Windows BF stats IRQ branch in
the exact private same-SP11 qccamisp8380.sys (SHA64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c):
event 0x0F at RVA0x1fc60, diagnostic "IFE%d IFE BF stats buf done
Irq occured." RVA0x37b88, passes group index8 at RVA0x1fc8c
to the SAME independent FIFO helper RVA0x26460, and stores resource
port0x300D at RVA0x1fce8. Both Windows rear 4K physical live
snapshots showed active extra WM16 BAF, absent from the working front.
This supports a new **static-candidate** sixth rear completion group:
VIDEO0x03/idx0 WM0-3, AEC_BE_BHIST0x0D/idx5 WM11-12,
TL_BG0x0E/idx6 WM13, AWB_BG0x10/idx7 WM14,
BF0x0F/idx8 WM16, RS0x12/idx9 WM18.
IMPORTANT: BF event 0x0F was **NOT ACTUALLY OBSERVED** during either
Windows rear live session, nor was a WM16 DMA completion proven.
Do not present a static OEM BF branch as a proven LIVE rear DMA/IRQ
lifecycle. E004nv source-only six-group mapping compiled on ARM64
with 720 offline cross-order simulations and 20 negative tests but
the runtime stays DENIED -EOPNOTSUPP, NO new caller, and Golden/front
sources remain unchanged. Private OEM binary remains only SAME SP11.
Next is a dedicated private Windows REAR LIVE BF completion trace,
then real per-group stats DMA/retire, RT-CDM/IQ/3A and safe exclusive
CSID1/VFE1 hardware lifecycle before any Linux-native rear4K run.

## E004nx/E004ny Windows rear 4K delivery control — KD contrast

Real SAME-SP11 Windows rear NV12 3840x2160 frame-reader delivery is
REPRODUCIBLE with NO KD attached. E004nx delivered 365 and 366 valid
rear4K handles across 2×35sec successful Start/Stop passes; E004ny
delivered 1152 and 1154 handles across 2×110sec successful passes,
after recording ≥12 valid handle pre-KD checkpoints EACH PASS.
The earlier E004nw SP7 KDNET one-shot BF0x0F branch was armed but
its Windows WinRT StartAsync=Success delivered ZERO handles, so no
actual BF event/WM16 completion was observed. E004ny debugger launch
was blocked by a tool safety check; **NO debugger was attached** in
that healthy test and the block MUST NOT be circumvented. Comparing
KD-armed zero frames and these two no-KD healthy runs does NOT
establish KD causation; camera timing/state may differ. See
`experiments/E004-front-ir-vd55g0/e004ny-rear4k-live-control/README.md`
and E004nx RESULT, E004nw previous failure scalar, E004ny RESULT +
verify.py with 14 fail-closed mutations. Windows ScheduledTask removed,
original private logs and binary remain private, Windows NTFS mounted
read-only and unmounted, user-authored frame-count-only source/evidence
in Git; new Linux boot verified protected Golden v19c BootCurrent0005
Linux-first order, no loaded camera/process, no Golden modifications.
Maintain E004nv BF0x0F/group8 as STATIC driver-dispatch candidate
until an authorized live debugger event is observed DURING confirmed
rear4K frame delivery, with independently established WM16/stats DMA
and IQ/RT-CDM lifecycle. Linux-native rear 4K ISP optical frame is
still UNPROVEN.

## E004nv BF static callgraph — direct WM16 proof and mode caveat

`experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/STATIC-BF-CALLCHAIN.md`
and `verify_static_bf_callchain.py` (47 SHA-locked OEM ARM64
instruction anchors) now trace **who invokes and where BF goes**.
Registration at RVA0x1a100 installs mode0 event handler RVA0x1ef90
or mode1 alternate RVA0x1c9d0 at object+0x6bd8; real event
worker at RVA0x239a0 loads/calls that handler. In mode0, incoming
second 32-bit status word bit7 generates BF event0x0F; event branch
pops FIFO group8, invokes mode0 per-event callback RVA0x1d620,
event15 target RVA0x1d710. Its mapped MMIO window begins at
VFE_base+0xc00; direct BF hardware reads VFE+0x1e00 = **WM16 CFG0**
and VFE+0x1e70 = **WM16 ADDR_STATUS0**. It stores WM16 CFG0 bit0
in device+0x1c0, which is EXACTLY the subsequent extended BF
completion gate. A nonempty/enabled path matches queued item/tag,
stamps BF resource port0x300d and notifies via RVA0x26340.
**IMPORTANT:** same binary has TWO event dispatch modes selected by
per-device instance/threshold, and actual Windows rear 4K runtime
mode is UNPROVEN; no BF input bit7, event0x0F LIVE or WM16 DMA
retirement was observed. This static route is real evidence of
BF↔WM16 connection but does NOT authorize Linux runtime, ISR or
Golden installation. Full report + offline verifier in above path.

## Active workspace and historical records

The current camera source-of-truth checkout is `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean` on
`experiment/e004-front-ir-vd55g0`. PiMaster workspace `sp11-camera-handoff`
and the project-level CURRENT-CAMERA-WORKSPACE.txt pointer must agree with it.
See [docs/MACHINE_MAP.md](docs/MACHINE_MAP.md) for retained historical clones.

Top-level state fields identify the current/next experiment and next action.
Nested experiment records and older handoff paragraphs retain historical
results; their old paths, NEXT statements and boot IDs do not override the
current frontier. Preserve older checkouts and untracked evidence.

## Resume behaviour

When asked to continue camera work:

- Do **not** ask the user to re-explain the project.
- Read `CONTINUE.md`, `PROJECT_STATE.md`, `state/project.yaml`, and the latest experiment.
- Query live machine state before acting.
- Treat repository state as authoritative for what was mechanically proven; treat hypotheses as hypotheses.

## Lab topology

- **SP11 Linux** — primary build/deploy/log/DT/V4L2 target.
- **SP11 Windows** — same physical SP11, used as hardware oracle for DriverStore, ACPI, ETW/WPP, live behaviour and KD target. It will normally be offline from PiMaster while Linux is booted and vice versa.
- **SP7 Windows** — companion/debug host. May be used for KD into SP11, USB/EEM debugging, tracing and comparative tooling.
- PiMaster is the normal remote-control plane. Rediscover exact endpoint identifiers from the tool rather than hard-coding secrets.

Reboots, static inspection, dynamic tracing and debugger work are normal parts of this lab workflow. Still preserve the known-good boot path and checkpoint before mutations.

## Access and lab quirks

- SP7 has a dedicated SSH key for SP11 Linux at `%USERPROFILE%\.ssh\sp11_project_ed25519`; the public key is already authorized on SP11. Never commit private-key material.
- SP7 also carries the established KD tooling/configuration for SP11 Windows. Reuse the configured KDNET secret locally; do not record credentials in Git. Interactive KD requires a true PTY.
- Never hardcode SP11 IPv4/MAC. Wi-Fi privacy/randomization and DHCP change them across boots; rediscover via PiMaster, mDNS, ARP/IPv6 or SP7.
- Never hardcode CCI adapter numbers such as `3-0010`; discover the bound sensor dynamically because numbering changes across boots.
- PiMaster loss during reboot, Windows/KD ownership or Wi-Fi startup is not itself evidence of a crash. Use independent SP7 reachability when needed and allow adequate boot/network time before concluding failure.
- Initrd extra-module paths may disappear after switch-root; for a manual post-boot harness, use a SHA-checked repo/build copy if the initrd copy is no longer visible.
- Do not use `.golden-v33-delta-replay/src` as the production camera source. Use `.golden-v33-repro/src` for true Golden reference and `sp11-camera-e002k-d-src` for the accepted integrated camera source.

## SP11 Linux system sleep: prohibited camera test path

The user reports that **OS-level standby/suspend/resume is not yet
implemented reliably on SP11 Linux and may crash the whole OS**.
Do NOT initiate system suspend, resume, hibernate, hybrid-sleep,
systemctl suspend, loginctl suspend, rtcwake suspend, or
write a sleep state into /sys/power/state for camera testing.
Do not schedule automated suspend/resume loops or label their absence
as a camera failure. Normal independent camera experiments and
guarded reboots with verified Golden fallback remain authorized.
Test sustained capture, sequential camera switching, stop/reopen,
service lifecycle and recovery WITHOUT putting Linux into system sleep.
Read-only observation that individual camera sensors enter ordinary
runtime-PM suspended/idle state while Linux remains awake is distinct
from OS-level standby and remains permitted. Do not change system
power-management policies. Revisit system standby/resume only after
independent platform support is established and explicit user
authorization is obtained.

## Golden protection

Current deployed Golden is the FullIO v19c audio kernel/DT/initrd stack. Camera work must not overwrite it.

- Never replace the v19c `/boot` payload in-place.
- Never make an unproven camera candidate the permanent saved GRUB default.
- Prefer a separate camera kernel release/build directory and a one-shot GRUB candidate.
- Preserve the working `7.1.5-sp11-render-parity-v4+` module tree and prepared build anchor.
- Camera changes must not silently change audio, touch, display, power or USB behaviour.

## Experiment discipline

Every meaningful hardware experiment uses `E###-slug`.

Before runtime mutation record:

- hypothesis;
- exact source/base commit or snapshot;
- files changed;
- kernel release/DTB/initrd hashes;
- expected observation;
- rollback path.

After the run record:

- boot result;
- relevant dmesg/media graph/V4L2 output;
- Windows comparison when applicable;
- conclusion: proven / disproven / inconclusive;
- next smallest experiment.

One major unknown per experiment whenever possible.

## Evidence hierarchy

Prefer, in order:

1. behaviour observed on this SP11 under Windows or Linux;
2. static data from this SP11's ACPI/DriverStore/configuration packages;
3. upstream kernel code/documentation for X1E80100 and the exact sensors;
4. working Linux implementations on closely related X1E hardware;
5. community SP11 notes/issues;
6. inference.

Never silently promote (5) or (6) into fact.

## Clean-room / repository hygiene

Do not commit proprietary Microsoft/Qualcomm binaries, firmware extracted from Windows, raw DriverStore packages, ETL dumps containing private data, or credentials. Derived facts, hashes, structure names, register observations and independently written Linux code are appropriate.

`.gitignore` intentionally blocks common proprietary/raw extensions. `tools/check-repo-hygiene.sh` is a pre-push sanity gate.

## Kernel strategy

Do not rewrite generic Qualcomm infrastructure merely because Surface support is absent from DT. Reuse and, when necessary, minimally extend upstream:

- X1E80100 CAMSS;
- CCI;
- CSI PHY;
- CSID/VFE;
- media-controller/V4L2 infrastructure.

Independently derive the Denali board graph, power rails, GPIOs, clocks, sensor modes and link configuration from Windows evidence.

## Definition of success

Transport parity and image-quality parity are separate milestones.

First achieve stable native RAW capture with correct power, reset, link, mode, exposure/gain and lifecycle. Only then work on ISP/libcamera processing, tuning and Windows-like image quality.

## User authorization — 2026-09-05

The user explicitly authorizes installation of useful missing tools on the project machines/OSes, discretionary Linux/Windows reboots, KD, ETW/ETL, Ghidra and static/dynamic analysis, and saving/committing/pushing meaningful progress. Proceed without repeatedly asking for these routine project actions. The user reaffirmed on 2026-09-23 that ANY lab machine and useful static/dynamic tool may be used; this supersedes the prior SP11/SP7/PiMaster-only HOST restriction. Same-SP11 proprietary Windows tuning/drivers/firmware and camera optical pixels/photos/RAW/thumbs/image hashes must still remain private on SP11; do not put originals in Git/chat or export them to another host. Preserve Golden and checkpoint exact hardware experiments. SP11 can remain on one-shot Windows for an extended oracle session; a normal reboot returns via persistent Linux-first EFI BootOrder and saved Golden GRUB entry. SP7's LCD NEVER sleeps, but has a permanently non-rendering thick dark LOWER band: use only registered healthy upper display ROI for private SP11 rear-camera comparison, and never classify its dark lower band as a camera/lens/exposure defect.


## Windows oracle scheduled-task single-use guard — E004nn correction

On 2026-09-23 E004nn a signed-in Windows user task was manually started
and THEN automatically re-ran at its `New-ScheduledTaskTrigger -Once -At
(Get-Date).AddMinutes(1)` time. Separate private original JSON files
and the original first-run ETW time boundary proved two invocations.
The ETW covers the FIRST ONLY; never merge their counts or claim
single-use. This does not invalidate the recorded first-run Windows
FrameServer 297/295 unique timestamped client samples, but is an
execution-control failure. The Windows Scheduled Task was unregistered. Source-only guarded future-task helper and duplicate-rejection selftest live in experiments/E004-front-ir-vd55g0/e004nn-rear-oem-ife-windows-observer/windows-atomic-consumed-guard.ps1 and test-windows-atomic-consumed-guard.ps1, verified on SP11 pwsh7.6.5 and SP7 native Windows PowerShell5.1. The helper was NOT used in historical E004nn and does NOT negate its second invocation.

Future Windows camera oracle tasks MUST use a persisted atomic
`[System.IO.File]::Open($marker,[System.IO.FileMode]::CreateNew,
[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)` at script
ENTRY, before any camera access, so a later unintended trigger fails
closed; also unregister the task after the intended invocation ends.
Do not assume a file-exists check only at task REGISTRATION protects
against a later automatic trigger. Do not re-use an already-consumed
Windows or Linux experiment identity. Keep original source ETL and
optical files private; commit only verified scalar evidence and
source, with explicit unproven hardware contracts.

## Concurrent-turn / UI-disconnect safety

The user-facing UI can disconnect while a backend command or another turn remains active. Never assume a missing response means the operation stopped.

Before every meaningful mutation run `tools/camera-overlap-guard.sh`, compare local HEAD/origin, inspect tracked status and active camera/build processes, verify Golden/`next_entry` for boot work, and inspect the proposed stage/evidence path.

If unexpected stage or attempt evidence exists, audit it first. For a one-shot runtime, evidence that a stream may have started makes that identity consumed until proven otherwise. Never same-boot retry and never reuse a consumed candidate.

Do not mass-clean historical untracked evidence and do not use `git add -A`; stage explicit intended paths only.
