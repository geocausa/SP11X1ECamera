# E003h RT_CDM1 inert Linux resource representation

Date: 2026-08-28

Policy: same-machine Windows on this SP11 is the behavioral oracle. Qualcomm public CDM v2.1 sources are used only for register-layout bounds and implementation vocabulary. No Linux RT-CDM command submission or front-frame runtime is authorized.

## Windows facts represented

- active native front command engine: RT_CDM1;
- physical base: `0x0ac26000`;
- hardware version: `0x20010000` (CDM v2.1);
- dedicated firmware GSI/INTID: `319` (`0x13f`);
- SP11 Linux DT namespace: `GIC_SPI 287` (`0x11f`), mechanically cross-checked against six existing CSID/VFE Windows/Linux IRQ pairs;
- the Windows raw interrupt descriptors use the same latched/edge class as those known SP11 camera resources, whose Linux DT encoding is `IRQ_TYPE_EDGE_RISING`.

The 4 KiB mapping is evidence-bounded: Windows maps RT_CDM0 and RT_CDM1 on adjacent physical pages (`0x0ac25000` and `0x0ac26000`), while Qualcomm's public CDM v2.1 layout ends at the spare register `+0x3fc`. `0x1000` therefore covers the entire named v2.1 block without crossing into an unproven neighboring page.

## Patch

`0013-sp11-rtcdm1-inert-resource.patch`

SHA-256: `1ffd67b8e1e8b706a2569384e4daef41676b307148a11e64fee0e7480bfc553b`

The delta is intentionally inert:

- appends Denali-only `rt_cdm1` MMIO `<0x0ac26000, 0x1000>`;
- appends Denali-only `rt_cdm1` IRQ `GIC_SPI 287 IRQ_TYPE_EDGE_RISING`;
- preserves every existing CAMSS reg/IRQ tuple in its current order;
- generic `hamoa.dtsi` and other X1E boards are unchanged;
- driver treats the resource as optional;
- if present, driver requires X1E80100, exact physical base and exact 4 KiB size;
- resolves the named Linux IRQ and maps the aperture;
- stores only `{base, irq, present}` in CAMSS state;
- performs **no RT-CDM MMIO read or write**;
- does **not** request/enable/clear the IRQ;
- does **not** allocate command memory;
- exposes **no submit API**.

The helper is initialized only after CAMSS has successfully set its existing 32-bit coherent DMA mask. This does not yet allocate DMA; it establishes the correct ordering for the next static layer.

## CAMSS build

Build anchor: `/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826`

Command: `make O=... ARCH=arm64 M=drivers/media/platform/qcom/camss -j4 modules`

Result: PASS, no warning/error/modpost diagnostics.

`qcom-camss.ko` SHA-256:

`7bdb7e43edda74c4f9b6fc0351fe46255e9696d4a7d008c3ab2817d83b8052ad`

Vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

## Denali DT build/isolation

Target: `qcom/x1e80100-microsoft-denali-oled.dtb`

Before `0013` (already includes accepted static `0012` VFE aperture):

- bytes: `215173`
- SHA-256: `13a7faf7b5f4cbdbccfc4177145cbb179746bdfc698a273ec3c3e2bcc359bd19`

After `0013`:

- bytes: `215217`
- SHA-256: `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`

The DT compiler emitted the same pre-existing warning count for before and after. A decompiled structural diff changes exactly four CAMSS properties:

1. `reg`: append RT_CDM1 `0x0ac26000/0x1000`;
2. `reg-names`: append `rt_cdm1`;
3. `interrupts`: append SPI cell `0x11f` / 287, edge rising;
4. `interrupt-names`: append `rt_cdm1`.

No existing resource tuple, clock, power domain, IOMMU tuple, media endpoint, rear-camera property, or other DT node changes.

## Reproducibility

- reverse dry-run against the currently patched source: PASS;
- forward dry-run against the exact pre-0013 snapshots: PASS;
- raw-diff checkpatch: no code/style findings; only missing email-patch description/Signed-off-by metadata, which are not applicable to this experiment artifact.

## Runtime status

No boot, module load, IRQ request, RT-CDM MMIO access, DMA allocation, sensor transmission, or frame attempt occurred.

## Next static layer

Use the exact public CDM v2.1 layout only to implement the mechanism for IRQ status/clear/reset and FIFO0 bookkeeping while preserving Windows literals/behavior as the value authority. Add coherent command-buffer allocation with a hard 32-bit DMA-address check and deterministic teardown. Keep submission disabled until those mechanisms are built and rear-isolation/static gates pass.
