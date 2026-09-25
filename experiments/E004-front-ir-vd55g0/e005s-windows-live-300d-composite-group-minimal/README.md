# E005s — minimal Windows live resource0x300D composite-group capture

Parent Git a4d8e280601196cb287487bfe3ee812d99cf89ed (E005r).

## Hypothesis

The exact same-SP11 OEM output configuration will expose the live composite-group scalar for resource 0x300D at output-entry field +0x8C0. A reduced three-breakpoint SP7 external-KD run should preserve enough rear 4K throughput to meet the predeclared >=10 valid-handle gate while retaining the already proven BF group8 FIFO8 -> non-null matcher path and one bounded WM16 consumed-address sample per matched event.

## Exact source anchors

The SHA-pinned original qccamisp8380.sys remains 64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c.

1. Output configuration loop RVA 0x16DE8: x21 points at the current 0x28-byte output entry; resource type is [x21+0x8B0], exact OEM composite-group id is [x21+0x8C0].
2. BF group8 FIFO return RVA 0x1FC98: non-null x0 is the popped FIFO8 entry; key/tag are +0x08/+0x16.
3. Matcher return RVA 0x1FCE8: non-null x0 is the outstanding match; x23 retains the FIFO8 entry and x19 retains the device object. Read WM16 ADDR_STATUS0 directly as dwo(qwo(@x19+0x150)+0x1270) only for this scalar observation.

No separate IFE snapshot probe, no BF-event-only print, no E005n load, no MMIO/register write, no data breakpoint and no driver patch.

## Runtime discipline

SP7 is the only kernel debugger host. All code breakpoints auto-continue. Raw pointers, DMA/consumed addresses, debugger logs and optical payload remain private on SP7/SP11. The direct EFI Windows entry is BootNext-only; persistent BootOrder and Golden GRUB saved entry are not changed. The Windows camera trigger is single-use with an atomic consumed marker. After the run, clear breakpoints, close the private log, unregister the trigger, continue the target, and normally reboot back to Golden Linux.

A full runtime PASS requires clean rear VideoRecord Start/Stop and at least 10 valid NV12 3840x2160 handles. Regardless of the observed group scalar, native rear processed ISP remains denied unless exact same-generation WM16 hardware completion and DMA/IOMMU-safe retirement are independently closed.
