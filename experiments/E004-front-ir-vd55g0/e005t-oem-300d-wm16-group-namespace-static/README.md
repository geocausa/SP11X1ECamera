# E005t — source-lock 0x300D to WM16 and separate three different “group” namespaces

Parent Git `a586928657e1f03eebd866c9aa9807ec5e465438` (E005s). This stage is static only on protected Golden Linux. It analyzes the SHA-pinned same-SP11 OEM `qccamisp8380.sys` locally and the pinned Qualcomm camera-driver v1.0.6 source. No camera stream, reboot, module load, MMIO write, debugger or Golden mutation occurs.

## Result

E005s proved that the live Windows output configuration for resource `0x300D` reports **Composite Group id 3**. That number must not be conflated with either the OEM software BF queue number or the VFE680 physical BUS completion group.

### 1. OEM software BF namespace: group8

The OEM resource classifier at RVA `0x28080` special-cases resource `0x300D` and sets mask `0x100`, i.e. bit8. This is the already-established BF software ring/FIFO8 namespace used by the BF dispatcher. It is not the live output-config composite-group scalar.

### 2. OEM hardware programming: resource 0x300D is WM16

The OEM hardware enable/config function at RVA `0x1D830` performs an exact resource special case:

- RVA `0x1D850`: compare against resource `0x300D`;
- RVA `0x1D864`: load literal at RVA `0x1DC18`;
- that literal is exactly **0x00020001**;
- when enable argument is 1, RVA `0x1D888` selects that value into `w21`;
- resource `0x300D` is jump-table index 13 and resolves to RVA `0x1DA6C`;
- RVA `0x1DA6C..0x1DA74` writes `w21` to the device BUS pointer at relative offset **0x1200**.

The already source-locked OEM BUS pointer is VFE base + `0xC00`, so BUS-relative `0x1200` is full VFE offset **0x1E00**. The pinned Qualcomm VFE680 table identifies `0x1E00` as **BUS Client 16 / STATS_BAF / WM16 CFG0** and `0x1E70` as WM16 `ADDR_STATUS0`.

Therefore the Windows BF resource mapping is now source-locked end to end:

`resource 0x300D -> enable 0x20001 -> VFE 0x1E00 -> WM16/STATS_BAF`.

This is independent of the live output-config group number.

### 3. VFE680 physical completion namespace: group7

The pinned Qualcomm VFE680 source assigns BUS Client 16 / STATS_BAF / WM16 to `CAM_VFE_BUS_VER3_COMP_GRP_7`. VFE680's `comp_done_mask[]` maps group7 to `BIT(7)`.

BUS-v3 derives the completion-group ID from the WM hardware descriptor itself (`hw_regs->comp_group`), stores the corresponding `comp_done_mask[index]`, and completion tests BUS status0 against that mask. The IFE manager consumes the group ID returned by the BUS acquire path.

As a useful negative control, the same VFE680 table assigns **group3 to BUS Client 10 PIXEL RAW**, not WM16.

## Consequence

There are three distinct identifiers in play:

- **8** — OEM BF software ring/FIFO namespace;
- **3** — live OEM Windows output-configuration “Composite Group id” observed for resource `0x300D`;
- **7** — pinned Qualcomm VFE680 WM16/STATS_BAF physical BUS-v3 completion group.

The values are not interchangeable. E005t does **not** invent a 3→7 translation. The exact OEM semantic/translation of live group3 into the proprietary completion machinery remains unresolved. What is now independently proven is that resource `0x300D` itself programs WM16 exactly.

Native rear processed ISP remains **DENIED** because exact same-generation FIFO8 key ↔ independently completed WM16 DMA buffer identity, DMA/IOMMU quiescence, and safe reuse are still unproven.

## Next smallest step

Stay static before another Windows run. Source-lock the OEM WM16 completion/consumed-address path around the already observed callback/read site and identify its exact hardware completion predicate/ACK relationship. Only after that should a reduced external-SP7 KD run correlate one FIFO8 key/matcher generation against a source-defined WM16 hardware completion event. Do not load E005n from this static result alone.
