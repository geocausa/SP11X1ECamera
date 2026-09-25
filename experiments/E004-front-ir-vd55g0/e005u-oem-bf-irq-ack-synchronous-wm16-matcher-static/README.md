# E005u — source-lock BF IRQ ACK and synchronous WM16 status sample vs matcher

Parent Git `4713bbc4e67ffb3a3e3976c329e65c039c7c6657` (E005t). This stage is static only on protected Golden Linux. It analyzes the SHA-pinned same-SP11 original `qccamisp8380.sys` locally and reduces already-accepted E005o/E005q/E005s live evidence. No camera stream, reboot, module load, MMIO write, debugger session or Golden mutation occurs.

## Result

This stage separates three things: the hardware event that creates BF event `0x0F`, the synchronous WM16 status sample taken by the BF dispatcher, and the request object returned by the FIFO key/tag matcher.

### Type-1 BF has a real status/ACK pair

The zero-mode type-1 preparer at RVA `0x1B5F0` reads the CSID mapped register at `+0x8C` into prepared status `+0x0C`. The same saved word is later written back to mapped register `+0x94`. The normalizer at `0x1B7D0` copies prepared `+0x0C` to type-1 consumer `+0x08`; the event path extracts bit7 and emits BF event `0x0F`.

Therefore BF is backed by a hardware status bit with an explicit same-word clear/ACK in the CSID type-1 domain. This is not by itself proof of WM16 DMA retirement.

### BF synchronously samples WM16 before the matcher

After event `0x0F`, the original driver pops FIFO group8 at `0x1FC94`, rejects NULL, invokes the hardware-status callback with selector `0x0F`, and selector `0x0F` lands in the WM16 case of RVA `0x1D620`. That case reads BUS `+0x1270` (VFE `+0x1E70`, WM16 `ADDR_STATUS0`) into result `+0x4C`, then reads BUS `+0x1200` (VFE `+0x1E00`, WM16 CFG0) and stores CFG0 bit0 into result `+0x48`. Only then does the BF branch pass the FIFO key/tag to matcher RVA `0x25078`.

The result base is device `+0x178`, so the synchronous consumed-address sample is device `+0x1C4`. Existing E005o/E005q/E005s live evidence already demonstrated this WM16 state is active during real rear4K BF sessions.

Crucially, RVA `0x1D620` does **not** test a BUS completion IRQ bit and does not ACK a BUS IRQ. It is a status/telemetry reader, not the independent WM16 completion fence.

### Matcher returns a real request-associated opaque object

RVA `0x25078` scans six outstanding slots and requires exact FIFO key plus 16-bit tag equality. Each slot contains an opaque object pointer at `+0x2E60 + slot*0x20`, key at `+0x2E68`, matched-count at `+0x2E70`, expected-count at `+0x2E74`, and tag at `+0x2E78`.

Installer RVA `0x24F60` receives the object as argument `x1`, stores it in the first free `+0x2E60` slot, and the matcher later returns that exact pointer. On the type-1 submission path, that installed argument is source-loaded from event/request record `+0x30`.

This proves request-object provenance but does **not** prove that the object contains the WM16 DMA address or that any object field equals `ADDR_STATUS0`.

## Consequence

A future live experiment can be much tighter than E005q: one BF path already gives CSID bit7 provenance/ACK, FIFO8 key/tag, synchronous WM16 `ADDR_STATUS0`, WM16 enabled state, and the matched request-object pointer. The remaining identity question is whether a source-defined field of that object can be tied to the exact independently completed WM16 DMA buffer.

Before claiming DMA completion, the OEM physical WM16/BUS completion predicate and retirement semantics still need independent proof. No CSID bit, FIFO match, or consumed-address sample is silently promoted into an IOMMU-safe fence.

Native rear processed ISP remains **DENIED**.

## Next smallest step

Inspect the returned request object and OEM BUS completion path. If no static object field closes exact address identity, perform one reduced SP7-external-KD run at the synchronous BF site, logging only safe correlation scalars while raw pointers/DMA addresses remain private. Do not load E005n merely from this result.
