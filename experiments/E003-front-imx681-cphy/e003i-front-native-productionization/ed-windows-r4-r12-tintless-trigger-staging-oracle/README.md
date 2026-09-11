# E003i-ED — Windows R4..R12 request-labelled Tintless/trigger/staging oracle

Status: **STAGED / WINDOWS ORACLE NOT YET EXECUTED.**

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
