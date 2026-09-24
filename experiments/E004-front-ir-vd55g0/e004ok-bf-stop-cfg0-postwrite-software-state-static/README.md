# E004ok — immediate original BF WM16 stop tail is software bookkeeping, not DMA retirement

**2026-09-24; parent E004oj HEAD `756d3d50fec4317af76000fcfcb5d3a1b2d8d791`.** Same-SP11 original OEM ARM64 `qccamisp8380.sys`, SHA256 pinned by `verify.py`. Offline static inspection only; no live Windows capture, Linux camera runtime, installation, Golden mutation, flash/IR, KD, firmware or optical capture.

**Scope:** Linux **L1 exclusive ISP owner, L2 safe VFE/WM stop, L3 IRQ/DMA buffer ownership**. Explicit client/profile: original Windows **rear OV13858 3840×2160 VideoRecord** is the desired oracle, but **its actual selection of this IFE zero-state/BF branch is UNKNOWN**. Evidence **S** only; not a live hardware observation.

## Source-checked conditional path

E004oi identifies a conditional IFE stop-resource callback and E004oj proves that **if** zero-state callback `0x1D830` is selected for BF-associated resource `0x300D` with stop flag zero, code at `0x1DA74` writes zero to the selected register window +`0x1200`, equal to original selected base +`0x1E00` (the independent WM16 CFG0 relative offset).

E004ok follows **the actual next instructions, not a presumed physical stop**:

| Original driver location (RVA) | Static finding, bounded to this branch | Does not prove |
| --- | --- | --- |
| `0x1DA78 → 0x1DA04 → 0x1DA08 → 0x1DB24` | The BF CFG0 write joins the original common per-resource tail; zero is carried into the helper as a software status value. | Hardware stopped, or the Windows rear VideoRecord mode selected this path. |
| `0x1DB2C → 0x1C990–0x1C9CC` | The complete 16-instruction helper reads a context field, calculates/stores a context mapping, writes the supplied status in a context field, and returns. It contains no hardware-status poll, wait, DMA-IRQ acknowledgment or indirect call. | A separately scheduled IRQ worker or later bus/WM16 hardware drain does not exist. |
| `0x1DB30–0x1DB48 → 0x1DB88–0x1DBA0` | The valid resource path updates a software per-resource flag and returns; diagnostic out-of-range code is a different branch. | Permission to free the selected or any other in-flight DMA buffer. |
| `0x27300 → 0x27304 → 0x2731C–0x27358` | The outer IFE stop loop advances to further resources, resets software state and invokes another selected callback; a per-resource callback returning is not a verified bus/IRQ completion. | All resource WMs/stats have retired before outer callback exit. |

The verifier checks **47 exact original ARM64 instructions**, including **every instruction** of the immediate 16-instruction helper, its call/branch provenance, the original resource-loop continuation, the independent E004oj BF offset contract and **12 fail-closed negative mutations**. Its output is strictly source-derived scalars and conservative false/unproven gates. Neither OEM binary nor bulk disassembly, DMA addresses, KD material or optical data is stored in Git.

## Native Linux consequence and falsifiable next gate

Do **not** implement `WM16 CFG0 := 0; free(BF DMA)`, and do not use the return of the immediate resource callback as a complete-stop signal. Maintain kernel CAMSS/V4L2 exclusive mode ownership and retain all enabled DMA/IRQ surfaces until an independent verified **bus/write-master/interrupt and IOMMU buffer-retirement gate** is satisfied. A timeout or failure must keep buffers held or enter a safely recoverable fault state; it must not silently free potentially active memory.

**Next source/static gate (separate slice):** trace the independent original IFE later-progress callback `0x1F230`, event helper `0x241D8`, and the original BF/WM16 event/group8 buffer-completion/IRQ/bus-stop path; establish which event truly authorizes specific buffer retirement and how it relates to the write at `0x1DA74`. Separately prove the *same live Windows rear VideoRecord session* selects zero/nonzero callback, VFE1 base and BF/WM16 event `0x0F` before any physical Linux rear ISP activation. Analyze selector `0x809` independently; no semantic assignment by analogy.

**Still UNPROVEN:** live rear BF event 0x0F, FIFO8/WM16 DMA quiescence, actual selected Windows IFE state, Linux native rear hardware-ISP 4K optical frame. Source-compiled experimental Linux rear ISP remains runtime-DENIED. Front 27-frame native PIX, rear RAW/software-4K fallback, protected Golden and IR privacy remain untouched.
