# E005n — isolated VFE680 WM16 / comp-group-7 hardware-done observer

2026-09-25; parent E005m Git 92d9b8d59f98726d83802ced1e539cfee9f6c0e7. This is a source/build milestone only. No camera stream, module installation/load, reboot, MMIO access from the candidate, DMA allocation, KD session, or Golden change occurred.

E005m pinned the exact VFE680 contract: WM16 is STATS_BAF, belongs to composite group 7, completion is BUS status0 BIT(7), and WM16 ADDR_STATUS0 is base+0x1e70. Source review also established that Linux requests one dedicated, non-shared VFE IRQ directly with vfe_ops_680.isr; on accepted SP11 source that ISR is still a no-op. Therefore there is no second Linux VFE handler whose ACK would race a future isolated candidate.

## Candidate design

The isolated copy adds a VFE1/X1E-only observer. Its ISR latches TOP0/TOP1/BUS0/BUS1 once. If BUS0 comp-group-7 bit7 is present it reads WM16 ADDR_STATUS0 before interrupt acknowledgement, stores private telemetry and logs only the first eight events locally. The handler then acknowledges the exact latched TOP/BUS status words through their canonical clear registers and issues the TOP/BUS global clears.

IRQ acknowledgement is deliberately separated from camera-buffer retirement. The candidate does not call vfe_buf_done, VB2 completion, DMA unmap/free, queue pop, or any buffer-reuse path. A source-only arm helper preserves the existing BUS mask and ORs BIT(7), but the helper has no runtime caller in E005n. The module therefore cannot be described as a live BF path and is not installed or loaded.

A raw consumed DMA address is private same-SP11 evidence. It must never be copied into Git/chat/another host. Later evidence may record only derived correlations/hashes/scalars that do not expose the private address itself.

## Build result and consumed identities

The first one-shot build identity was created and then failed before compilation because its injector incorrectly asserted that camss-vfe.h already contained linux/atomic.h. No module was produced. That directory is preserved as consumed and must never be reused.

A fresh fix1 identity rebuilt from the unchanged accepted source, added the include correctly, and compiled the cumulative rear source-only candidate plus E005n with W=1. The ARM64 qcom-camss.ko is 13,738,248 bytes, SHA256 63d238b9eee09558487b94619a350f340e55f0e4333fadd1dfdb2b65ad1b5077, zero compiler warnings/errors, and exact Golden vermagic 7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64. The module/build log remain private outside Git.

Accepted camss-vfe-680.c, camss-vfe.h, and camss-vfe.c remained byte-identical after the build.

## What remains unproven

E005n proves that a conservative observer can be compiled against the real SP11 kernel ABI. It does not prove that rear native runtime produces VFE BUS comp7, that a WM16 consumed address matches a BF FIFO8 entry/generation, that all six rear groups retire, or that DMA/IOMMU lifetime is safe. Rear native processed ISP therefore remains denied.

The next experiment must have a new identity. It may wire/arm this observer only inside a bounded one-shot non-Golden rear candidate with explicit front/rear ownership and rollback. A BUS bit7 hit plus address is telemetry, not permission to release or reuse a buffer.
