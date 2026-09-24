# E004ps — Original BF callback can run without a nonnull outstanding-buffer match

**2026-09-24; parent E004pr 245775448fd51f99518a43c369a3a1e1a75b9347.** Original SP11 Windows rear OV13858 NV12 3840x2160 is the intended oracle; NO LIVE CAMERA in this milestone. Native Linux slices L1 (exclusive front/rear VFE1 owner), L2 (BF event source), L3 (FIFO8/WM16 identity and DMA-safe completion). Evidence S = exact same-SP11 OEM ARM64 STATIC; D = independent offline Linux safety design. No P/same-frame hardware evidence.

## New distinction: lookup attempted is not lookup succeeded

The original ISP binary SHA256 is 64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c, retained only on SP11. FIFO8 null at original RVA 0x1FC9C skips BF notification. With a nonempty FIFO8 entry, WM16 CFG0-lowbit false branches at 0x1FCCC directly to 0x1FD14: it skips the outstanding identity/tag match and can still reach the software callback at 0x1FD28.

For CFG0 lowbit true, RVA 0x1FCDC/0x1FCE0 passes the FIFO8 entry identity+0x08 and 16-bit tag+0x16 to outstanding matcher 0x25078. That matcher initializes x23=NULL at 0x250A0, compares both fields in up to six slots at 0x250B4–0x250D8, loads the matched object only on its matching branch at 0x250F4, and returns x23 at 0x2516C. The no-match branch 0x250DC reaches that same null return.

**At original RVA 0x1FCEC, the BF caller stores matcher result x0 into software context+0x580 without a null guard.** The contiguous 0x1FCEC–0x1FD28 path then retains the popped FIFO8 entry at 0x1FD18 and calls the software callback at 0x1FD28. The later cbz w0 at 0x1FD2C checks the callback return, NOT the earlier matcher result. This source proves callback reachability even with a missing outstanding match, NOT that this scenario occurred on a live rear4K frame or that callback success implies any DMA fence. In E004pr, "match" describes the **invoked lookup**, not an observed nonnull matching return.

## Independent Linux porting decision — offline only

The proposed Linux BF/WM16 buffer-reuse contract requires selected event0x0F, a nonempty FIFO8 entry, WM16 configuration, a **nonnull** outstanding match, same FIFO8 entry identity/tag and queued WM16 buffer, same exclusive VFE1 owner/frame generation, independently verified CSID- or VFE-delivered exact WM16 bus-done IRQ/ACK, DMA/IOMMU quiescence and six-group safe stop/drain. Neither original software callback, CSID BF bit7, CFG0, nor a nonempty FIFO8 by itself may meet any missing predicate.

This is a stricter native DESIGN contract, not a claim that real Linux IRQ/DMA predicate producers exist. Current native VFE680 ISR remains noop; accepted CSID680 owns BUF_DONE ACK and forwards generic RDI only. No BF bit7 shortcut to PIX/RDI VB2 retirement, no double ACK, no camera buffer reuse. Existing E004ov/E004pj models remain offline; experimental processed rear ISP runtime DENIED; protected Golden/front PIX/rear RAW/software-4K/IR remain intact.

## Verification and next gate

Run PYTHONDONTWRITEBYTECODE=1 python3 verify.py. It locally SHA-pins original SP11 OEM binary, verifies 26 precise ARM64 instructions and control flow, parent E004pr status, 512 synthetic nine-predicate input combinations and 21 fail-closed result-field negative tests. RESULT.json carries only source and design scalars. Private original binary, raw ETL, kernel pointers, DMA addresses, KD logs and optical pixels are not exported.

Next physically bind the **same original rear4K frame and owner generation** from source BF status to nonempty FIFO8 entry+tag, actual nonnull outstanding WM16 match and independently trusted exact WM16 hardware bus/IRQ/DMA/IOMMU completion, then obtain real native six-group owner-safe stop evidence. The E004QB Windows ETW evidence is user-mode software timing only and does not close these hardware gates.

No camera stream, kernel/boot/module/MMIO change, or reboot occurred in this milestone.
