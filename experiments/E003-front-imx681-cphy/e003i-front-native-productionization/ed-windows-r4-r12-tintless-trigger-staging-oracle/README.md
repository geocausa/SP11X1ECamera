# E003i-ED — Windows R4..R12 request-labelled Tintless/trigger/staging oracle

Status: **PASS_WINDOWS_ORACLE / CLEANROOM R4..R12 9/9 BYTE-EXACT / GOLDEN RETURN PASS.**

EC proved that post-R6 LSC wire state continues evolving through R12. The clean-room LSC/Tintless implementation is already complete; its remaining live inputs are raw 768-region Tintless statistics plus ordinary request-local trigger state.

ED captures those inputs and the matching final IFELSC411 staging in **one Windows front-camera stream**.

At `IFELSC411::CalculateSetting` RVA `0x88e1e8`, exact prior authority gives:

- request frame = `qwo(x1+0x1ff8)`;
- selected Tintless stats = `poi(x0+0xa0)`;
- raw trigger block = `x1+0x2080`.

For requests R4..R12, ED fails closed unless the stats pointer is non-null, `u32(stats+4)==0x300`, and bit1 of `u32(stats+0)` is set. The verified front R4/R5/R6 stream uses this saturated 0x64-byte-record branch, whose exact bounded read is **0x12bec bytes**. ED dumps exactly that object plus a same-request **0x100-byte trigger block**.

At the proven post-calculation hook RVA `0xa03b34`, request = `qwo(x20+0x1ff8)` and final staging = `x19+0xac`; ED dumps exactly **0x18a0 bytes** for the same R4..R12 range.

The camera holder remains gated before StartAsync. Streaming starts only after both debugger breakpoints are visibly armed. The R12 post hook clears breakpoints, closes the log, detaches and exits. Raw captures stay outside Git.

Offline acceptance will replay R4→R12 sequentially through the already-clean front chain using the captured stats and trigger-derived Lux/CCT, then compare generated LSC0/LSC1/GIC with the exact Surface-packed wire derived from each same-request staging object. No Linux camera runtime is performed by ED, and continuous AEC is not claimed until that sequence is byte-exact.

## Result — 2026-09-11

The first Windows execution was rejected before use because WinDbg bare numeric literals are hexadecimal: labels R10/R11/R12 had actually sampled decimal requests 16/17/18. That attempt is quarantined at `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ed/attempt1-invalid-hex-20260911`. The committed scripts now use explicit `0n4..0n12` decimal literals.

The accepted second execution captured request-labelled entry and post-stage pairs exactly for decimal R4,R5,R6,R7,R8,R9,R10,R11,R12. It is preserved outside Git at `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ed/windows-r4-r12-20260911`.

Offline replay feeds each captured bounded 0x12bec parsed Tintless object and same-request Lux/CCT trigger state sequentially through the existing production DX selector plus the native clean-room Tintless core. The unread allocation tail is zero-padded only to the already-proven 0x12c20 standalone-core ABI length. Surface packer replay of each same-request 0x18a0 staging object is the target.

**Result: 9/9 byte-exact LSC0, LSC1, LSC2 and GIC.** Bank parity is exactly `1,0,1,0,1,0,1,0,1`. The sequence exercises lower AEC, the 390→490 AEC interpolation band at R7/R8, upper AEC from R9 onward, the 4500→5000 CCT interpolation path, and the >5000 warm-leaf path.

This closes the request7+ LSC algorithm/state blocker. Linux can generate the evolving LSC sequentially from generation-tagged TL_BG plus current Lux/CCT using the already-existing clean production chain; freezing R6 LSC is incorrect. Continuous AEC is still not claimed until the complete request7+ IQ capsule/scheduler path is bounded and live-proven.
