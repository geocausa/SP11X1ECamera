# E011I — rear post-stop DMA reclaim candidate

Parent Git: c403422edf7e70e5e904bbc042fc69d38482381f (E011H). Status: **source-only ARM64 W=1 build pass; no runtime**.

E008k's unreachable two-slot runner deliberately pins both output DMA sets even on successful stop and then discards their allocation handles with the software wrapper. This checkpoint copies that runner into a separate source candidate and adds a post-stop reclaim helper. The original E008k evidence stays unchanged.

The helper is reached only after both exact-IOVA ledgers are complete, CSID1 is quiesced, all ten VFE1 WM CFGs and IRQ masks are stopped/drained, RT-CDM1 is stopped/closed, and CSIPHY1 and sensor stop succeed. It checks the current REAR owner epoch, both request generations and pending masks, the expected full surface and eight auxiliary allocations in each slot, and all four stop result flags **before freeing either set**. It then clears the two full-surface in-flight guards, uses the existing coherent-DMA release routine, releases both ledgers, pipeline PM, and the owner in that order. Any failed precondition leaves both DMA sets pinned. Fault/partial-stop paths still pin owner and DMA.

This is a compile-only lifecycle candidate. The CSID BUF_DONE event and VFE ADDR_STATUS0 sampling in E008i have not been physically proved to refer to the same WM16 generation at the IOMMU retirement boundary. The snapshot occurs after the CSID clear write and reads ten VFE registers serially; the code itself does not make those observations atomic. External serialization of a future runtime caller against another owner release/reacquire is also still required. **Do not wire a call site or authorize native rear ISP on this evidence.**

A fresh isolated copy of E008k's accepted CAMSS build was given the E011I runner include. ARM64 W=1 -j4 modules passed with zero warnings/errors. The private module was not installed or loaded. RESULT.json pins source/module hashes and Golden vermagic. The build copy remains local on SP11 under 02-kernel; only source-safe code and scalar results are committed.

Next: independently prove E008i's exact WM16 completion/consumed-IOVA generation and stop/IOMMU lifetime, and close the remaining E008p semantic seeds. The E011H RS upstream 16/1024 producer remains open.
