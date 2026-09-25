# E005r — correct BF provenance to type-1 CSID queue; source-lock the real composite-group field

Parent Git `1f418e98687204627d5d3f656d714ebbcde50368`.

This stage is static on protected Golden Linux plus a conservative reduction of the already-consumed E005q private SP7 KD log. No new camera stream, boot, module load or MMIO write occurs here.

## E005p correction

E005p correctly source-locked the OEM IFE snapshot wrapper and its TOP/BUS register geometry, but over-connected that snapshot to the type-1 BF event. The repository had already closed this ambiguity in E004ph.

The actual original type-1 path is a **different queue B**:

- registered preparer callback `0x24380`;
- the matching queue-B envelope is prepared before enqueue and delivered to type-1 callback `0x243D0`;
- zero-mode status preparer `0x1B5F0` reads the mapped **CSID0/CSID1 BUF_DONE_IRQ_STATUS +0x8C**;
- normalizer `0x1B7D0` copies prepared source `+0x0C` to the type-1 consumer word `+0x08`;
- mode-zero handler tests that word's bit7 and emits BF event `0x0F`, then the established group8 FIFO / matcher path executes.

The separate `0x24A30` wrapper / `0x1DC20` IFE snapshot is queue A and is not the type-1 preparation source. Therefore E005p's historical “TOP status1 bit7 is the actual BF source” claim is superseded. Its independent IFE TOP/BUS offsets and OEM writeback-divergence facts remain useful.

E005q's zero `0x1DC20` rows while 35 BF events were observed is consistent with this separation, but the static E004ph source proof—not a zero breakpoint count—is authoritative.

## E005q live result retained conservatively

The single E005q attempt was consumed. Start/Stop were clean, but debugger overhead reduced the 8.402-s rear-4K run to five valid handles, below its predeclared ten-frame acceptance gate.

Useful same-session scalar evidence survives:

- BF event: 35;
- non-null FIFO8: 35;
- non-null matcher: 35;
- FIFO8 and matcher opaque key/tag sequences equal on all 35 events;
- 70 exact WM16 ADDR_STATUS0 reads spanning 10 distinct values;
- 33/35 pairs surrounding one opaque key were equal and 2/35 changed.

Thus WM16 consumed-address state is demonstrably live during the BF session, but the two changed pairs prove that our asynchronous sampling cannot be promoted into exact per-key DMA-buffer identity.

## Resource 0x300D field correction

E005q also logged a repeated 0x30-byte resource-0x300D record as `F14=0x19, F18=4`. Source now identifies these exactly.

At OEM RVA `0x27FF0` the driver loads record `+0x14/+0x18`; immediately after, the diagnostic string is:

`Write Master Update for PortId = %d: W = %d, H = %d`

Therefore the observed resource-0x300D values are **W=25, H=4**. The value 4 is **height, not composite-group ID**.

## Exact composite-group field

The OEM's own output-resource dump is unambiguous. It iterates 0x28-byte output entries and prints, in order:

- entry resource type at container `+0x8B0`;
- format at `+0x8B4`;
- width at `+0x8B8`;
- height at `+0x8BC`;
- **Composite Group id** at `+0x8C0`;
- split point at `+0x8C4`;
- secure flag at `+0x8C8`;
- wmMode at `+0x8CC`.

The exact diagnostic for `+0x8C0` is `Composite Group id of the group = %d`.

So the next Windows observation has a source-defined field to read. E005q did **not** capture it, and the live resource-0x300D group must remain unknown. The independent Qualcomm VFE680 reference still maps WM16/STATS_BAF to group7, but that reference must not be silently substituted for the OEM live scalar.

## Next smallest experiment

Use SP7 external KD again, but with substantially less instrumentation:

1. capture the source-defined output resource entry for resource 0x300D and its `+0x8C0` composite-group field;
2. retain only the already-proven type-1 BF/FIFO8/matcher identity markers;
3. sample WM16 completion state at the exact callback only as needed;
4. do **not** probe the separate `0x1DC20` snapshot queue;
5. do not load E005n.

The decisive remaining boundary is still exact same-generation FIFO8 ↔ WM16 hardware completion and DMA/IOMMU-safe retirement. Native rear processed ISP remains **DENIED**.
