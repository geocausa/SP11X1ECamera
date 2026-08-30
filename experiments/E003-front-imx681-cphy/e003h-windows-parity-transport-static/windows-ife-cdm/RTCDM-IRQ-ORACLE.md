# Same-machine Windows RT-CDM interrupt oracle

Date: 2026-08-28

This closes the RT-CDM interrupt-resource ambiguity using the exact Windows ISP driver on this SP11. No external Qualcomm platform is used as behavioral evidence.

## Canonical raw capture

`../raw/E003H_RTCDM_IRQ_MAP_20260828.log`

- bytes: `7428`
- SHA-256: `0f4b30273ddd7af23bbad5158b2da57a320c143b43ce5119927bbfbcfa6cbf1b`
- encoding: UTF-16LE with BOM, CRLF
- capture point: the exact `qccamisp8380.sys` generic interrupt-registration routine during WDF `PrepareHardware`
- call-stack anchor: `Wdf01000!FxPnpDevicePrepareHardware::InvokeClient`

The capture was produced during a controlled restart of only the Windows ISP PnP device. The device returned `Started/OK` afterward. No WinRT stream, sensor stream-on, or frame capture was performed.

## Mechanical mapping

The same registration function receives the interrupt class, instance number, raw firmware `CM_PARTIAL_RESOURCE_DESCRIPTOR`, and Windows-translated descriptor.

- RT_CDM0: class `3`, instance `0`, raw firmware GSI/vector `0x1e8` = `488`.
- RT_CDM1: class `3`, instance `1`, raw firmware GSI/vector `0x13f` = `319`.
- RT_CDM1 Windows-translated descriptor: level `0x0b`, vector `0x0b53`.

The translated Windows vector is OS-local and is **not** the value to place in Linux DT.

## Linux GIC namespace conversion

The SP11 CAMSS DT and the same Windows ISP resource list provide an internal cross-check for the GIC namespace:

- Linux `csid0` `GIC_SPI 464` -> Windows GSI `496`;
- Linux `vfe0` `GIC_SPI 465` -> Windows GSI `497`;
- Linux `csid1` `GIC_SPI 466` -> Windows GSI `498`;
- Linux `vfe1` `GIC_SPI 467` -> Windows GSI `499`;
- Linux `csid_lite0` `GIC_SPI 468` -> Windows GSI `500`;
- Linux `vfe_lite0` `GIC_SPI 469` -> Windows GSI `501`.

All six satisfy `firmware GSI/INTID = GIC_SPI DT cell + 32`. Therefore the exact RT_CDM1 DT interrupt cell is:

**`GIC_SPI 287` (`0x11f`)**, corresponding to firmware GSI/INTID `319` (`0x13f`).

## Deterministic extractor

`extract_rtcdm_irq_oracle.py` verifies the raw byte count and SHA-256 before decoding UTF-16, requires both class/instance sections, decodes the interrupt descriptor header and raw/translated level/vector fields, requires the WDF `PrepareHardware` call-stack anchor, and rejects any mismatch.

Generated result: `rtcdm-irq-oracle-summary.json`.

The fail-closed smoke test rejects a one-byte mutation before parsing.

## Parity consequence

The Linux RT_CDM1 prerequisite is now pinned to a dedicated interrupt instead of borrowing VFE1 completion or guessing a neighboring SPI. The current static target is:

- RT_CDM1 physical block: `0x0ac26000`;
- hardware generation: CDM v2.1;
- command path: FIFO0;
- firmware GSI/INTID: `319` (`0x13f`);
- Linux DT interrupt cell: `GIC_SPI 287` (`0x11f`);
- DMA source / translation domain: **not established by this oracle**. The current Linux `dma_alloc_coherent(camss->dev, ...)` choice is an implementation hypothesis and remains runtime-blocking until same-machine Windows proves the RT-CDM1 requester/SID/context/domain and command-buffer visibility;
- power/clock ownership: existing Windows-proven IFE1/Titan/CPAS context, with no independently proven RT-CDM clock or GDSC.

No Linux MMIO write or command submission is authorized by this document alone.
