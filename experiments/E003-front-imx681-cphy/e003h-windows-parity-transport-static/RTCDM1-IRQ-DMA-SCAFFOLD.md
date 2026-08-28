# E003h RT_CDM1 disabled IRQ/DMA scaffold — static only

Date: 2026-08-28

Same-machine Windows remains the behavioral oracle. Qualcomm camera-driver commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` is used only for RT-CDM v2.1 register names, bit positions, and generic mechanism.

## Input already closed

- active front hardware engine: RT_CDM1 v2.1;
- physical base: `0x0ac26000`;
- resource span: 4 KiB;
- command path: FIFO0 only;
- dedicated Windows firmware GSI/INTID: `319` (`0x13f`);
- Denali Linux DT interrupt: `GIC_SPI 287` (`0x11f`), edge rising;
- Windows live FIFO0 IRQ mask: `0x00070007`.

The v2.1 public status definitions name those mask bits as reset-done `0x1`, inline IRQ `0x2`, BL-done `0x4`, invalid-command `0x10000`, overflow `0x20000`, and AHB error `0x40000`. Their union is exactly the Windows literal `0x00070007`; the Linux candidate enforces this equality with a compile-time assertion. The public source is not used to substitute any Windows runtime value.

## Static `0014` layer

`0014-sp11-rtcdm1-disabled-irq-dma-scaffold.patch` builds on inert resource patch `0013` and adds only scaffolding:

1. Registers the already-proven `rt_cdm1` IRQ using the same CAMSS pattern as CSID/CSIPHY: `IRQF_TRIGGER_RISING | IRQF_NO_AUTOEN`.
2. There is deliberately **no API that arms/enables the IRQ**, and there is no assignment that sets `irq_armed=true`.
3. The compiled ISR is therefore unreachable in this layer. Its future-facing body is restricted to FIFO0, records context/status/user-data, uses the v2.1 status/clear/clear-command mechanism, and fail-closes by disabling the Linux IRQ on an unexpected FIFO, unknown status bit, or any known RT-CDM error bit.
4. Adds a caller-sized coherent DMA arena helper. It allocates from the CAMSS device after the existing 32-bit coherent DMA mask has been installed, independently rejects any returned DMA address above `0xffffffff`, allows only one arena at a time, and never assigns that address to an RT-CDM register.
5. The arena is zeroed after allocation and `memzero_explicit()` is used before deterministic `dma_free_coherent()` teardown.
6. There is no FIFO0 base/length/store/config write, no IRQ-mask write, no reset write, no core/FE configuration write, no core-enable write, and no submission API.

## Build/isolation proof

- CAMSS module build: PASS, no warning/error diagnostics.
- `qcom-camss.ko` SHA-256: `0a3f1e64af5e69d428f08982aad1ad7dd39d32a5eb5baa11df6c4c78a9ce9a10`.
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.
- Denali DT source is byte-identical to the `0013` source.
- rebuilt Denali DTB remains byte-identical to `0013`: SHA-256 `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`, 215217 bytes.
- forward and reverse patch dry-runs: PASS.
- policy scan: zero added IRQ-arm, FIFO-submit, IRQ-mask, reset, core-config, or core-enable write paths.
- checkpatch reports only absent mail-patch description/Signed-off-by metadata; no code/style defect is reported.

No module was loaded. No IRQ was requested on live Linux. No DMA arena was allocated on live Linux. No RT-CDM MMIO was read or written. No sensor transmission or frame attempt occurred.

## Next evidence gate

Do **not** turn the scaffolding into an enabled RT-CDM path from public Qualcomm defaults or the Windows live snapshot alone. The next static oracle must mechanically recover the exact same-machine Windows RT_CDM1 initialization/write ordering and distinguish one-time initialization from dynamic FIFO submission/completion state. In particular, resolve when/how Windows writes core configuration, FE configuration, FIFO0 configuration, IRQ mask/clear state, reset/core enable, and the first FIFO0 base/length/store relative to IFE start and the captured initial IFE command packets. Only then may a write-capable Linux layer be designed.
