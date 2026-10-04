# E011EI: source-qualified camera count and native Windows reference correlation

Status: **PASS_SOURCE_QUALIFIED_CAMERA_COUNT_AND_NATIVE_REFERENCE_CORRELATION**.

E011EH joined the process-attach-created stream vector to the retained camera caller. E011EI qualifies the next original dependency read at 0xCC6130 / 0x16A2A50. The accepted source bootstrap default is 512 entries; the original arithmetic starts scanning at slot 3 and computes the end exactly at byte 4096, so the bounded scan range is slots 3 through 511 (509 slots). The next source frontier is the slot-3 load at 0xCC6140.

The same state was then checked natively on SP11 Windows using the existing SP7 debugger topology. Before stream start and again at the original camera read, the native count is 512 and the vector is non-null. Its first three entries resolve to the same three module-relative static stream-object RVAs qualified by the source model. The original 0xCC6120 pointer read and 0xCC6130 count read were observed in sequence on the same start thread.

The Windows rear reference succeeded at OEM NV12 3840x2160. A primary debugger-correlated run completed with 449 valid-format handles; a second bounded kernel probe completed with 69. During the bounded rear probe, 81 FIFO generation events matched 81 completion events with monotonic generation keys 1 through 81. 161 WM16 consumption observations rotated across 10 addresses. This is strong native generation/buffer-consumption evidence but is not promoted to IRQ or DMA/IOMMU retirement proof; the IRQ predicate had zero qualifying events.

A Windows front reference also succeeded at OEM NV12 1920x1080 with 102 valid-format handles. The rear FIFO/match probes did not trigger on that front run, and the same WM16 probe reported only zero values. This establishes that front is not described by the rear probe path; it does not mean the front stream is inactive and it does not qualify front hardware retirement.

All debugger logs, raw native pointers/module bases, transport credentials and optical material remain private. Only derived counts, module-relative RVAs and SHA256 evidence anchors are committed. SP11 returned through the normal one-shot path to the saved Golden Linux entry after the capture; BootNext is consumed and camera nodes are idle.

NEXT E011EJ qualifies the original slot-3..511 scan beginning at 0xCC6140, especially the first null-slot 88-byte allocation/initialization/publication path and bounded return. Kernel IRQ/DMA/IOMMU retirement remains a parallel dynamic gate. Native rear runtime remains denied.
