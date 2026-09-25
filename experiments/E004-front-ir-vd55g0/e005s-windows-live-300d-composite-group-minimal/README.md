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

## Runtime result — PASS

The one-shot Windows attempt was consumed exactly once under the external SP7 debugger. The rear camera opened as Surface Camera Rear / Color / VideoRecord / NV12 3840x2160, StartAsync succeeded, the bounded capture ran 8,186 ms, produced **30 valid 4K frame handles**, and StopAsync completed successfully. This exceeds the predeclared >=10-frame acceptance gate.

The source-defined output-entry probe observed resource `0x300D` with **live OEM Composite Group id = 3** exactly once during configuration. This is authoritative for this same-SP11 Windows OEM run and must not be silently replaced by the independent upstream Qualcomm VFE680 reference value of group7. The semantic relationship between OEM group3 and upstream group7 is now a source-analysis question.

The reduced BF path instrumentation preserved normal throughput and produced **56 non-null FIFO8 entries and 56 non-null matcher returns**. Their opaque key/tag sequences were identical for all 56 events, keys were consecutive 1..56, and every tag was zero. The matcher-side bounded WM16 ADDR_STATUS0 sample was non-static across the run: 56 samples spanning 10 distinct values. Raw debugger pointers/addresses remain private on SP7; the private debugger log is SHA-256 `833435b442bddaeefbadd6e937062d5cb651f58da056885fa193224d419a63ef` (8,169 bytes).

This proves the live OEM group scalar and strengthens same-session FIFO8/matcher/WM16-state correlation, but it still does **not** establish that each opaque FIFO8 key is the independently completed DMA buffer represented by the sampled WM16 address, nor DMA/IOMMU quiescence and safe reuse. Native rear processed ISP therefore remains **DENIED**.

All three KD breakpoints were cleared, the private log was closed, Windows was normally rebooted, and SP11 returned to protected Golden Linux. EFI BootNext was consumed, persistent BootOrder remained Linux-first, GRUB saved entry remained `sp11-audio-fullio-v19c`, `next_entry` was empty, no camera module/node/process was active, and `tools/camera-overlap-guard.sh` returned PASS.

## Next smallest experiment

Before another physical run, source-lock the OEM meaning and hardware mapping of **composite group 3** for resource `0x300D`: identify the exact OEM group-bit/mask/clear/dispatch path and determine how it relates to WM16/STATS_BAF and the upstream VFE680 group7 model. Do not load E005n or change the Golden driver merely to reconcile numbering.
