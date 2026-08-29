# E003h preflight — Windows-parity transport architecture, static only

Date: 2026-08-29

## Purpose

Close the remaining host/receiver/sensor lifecycle gaps under the project rule that the exact same-machine Windows stack is the behavioral oracle. E003h is not an RDI bring-up gate and does not authorize a frame.

## Windows facts now mechanically established

- physical path: `IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`;
- sensor mode: 3840x2640 RAW10 VC0, one-trio C-PHY;
- CSID1 RX: `RX_CFG0=0x11300000`, `RX_CFG1=0x00000001`;
- CSID1 IPP: enabled RAW10 VC0, crop/measure 3840x2160;
- VFE1 Windows ISP output: FULL Y 2560x1440, FULL C 2560x720, DS4 320x180, DS16 80x45 plus statistics clients;
- VFE0 is inactive for the front WinRT stream;
- sensor stream-on/off is exactly `0x0100=1` / `0x0100=0`, zero delay; group hold `0x0104` is separate;
- Windows ISP internal start order is CDM -> IFE -> initial IFE/SFE/CSID packets -> CSID;
- Windows ISP internal stop order is CSID -> IFE -> CDM/remaining core;
- native front IFE command execution uses hardware RT_CDM1 v2.1 at physical `0x0ac26000`, FIFO0;
- RT_CDM1 registers as interrupt class 3 / instance 1 with firmware GSI `319` (`0x13f`), which maps to Linux `GIC_SPI 287` (`0x11f`) on this SP11;
- two independent dynamic cycles prove ISP start completion before sensor `0x0100=1`, and ISP stop completion before sensor `0x0100=0`.

## Linux gaps

1. CSID680 did not propagate the parsed C-PHY type into RX_CFG0 and omitted Windows' reproducible bit-28 field. `0009-...patch` fixes only that proven RX mismatch and builds successfully. It is not deployed.
2. CSID680 Linux streaming supports RDI paths only; the Windows path is IPP.
3. VFE680 Linux output supports RDI only. Its generic PIX line mapping is explicitly invalid for PIX and would map line 3 through `RDI_WM(3)` to WM27/LTM_STATS. Enabling PIX as-is would be wrong.
4. Windows uses VFE1 FULL Y/C and real ISP scaling from 3840x2160 to 2560x1440, not a raw RDI write master.
5. Linux generic stop ordering VFE -> CSID does not match Windows. Static-only `0010-x1e-windows-stop-order.patch` changes X1E teardown to CSID -> VFE -> existing remaining upstream tail, while non-X1E traversal is unchanged. The patch reproducibly builds to qcom-camss SHA-256 `b7c9ed932e2dccca4eaf73d085d2c5c8e6104d7cb807bafd00804051a9e82591`; it is not deployed.
6. Lifecycle placement is fully resolved. Four MIPI-instrumented Windows cycles prove strict ISP -> MIPI -> sensor start ordering and an unordered sensor-off/MIPI-stop tail after ISP teardown. `0010`'s current CSIPHY -> sensor tail is an observed-valid serialization, not a claimed Windows requirement.
7. Static `0015-sp11-rtcdm1-windows-static-recipe.patch` now compiles the exact Windows-derived RT_CDM1 preflight/init/start/FIFO0/stop recipe behind an unreachable private ops table. FE_CFG/FIFO0_CFG remain read-only validation targets, the optional CGC path is absent, no `CORE_EN=0` shutdown is invented, and no runtime code references the recipe.
8. Static `0016-x1e-vfe1-pix-qc10c-static-contract.patch` closes only the VFE1 PIX memory/completion representation: IFE1-only RAW10 -> fixed 2560x1440 QC10C, FULL WM0+WM1, exact surface offsets and Windows VIDEO completion contract. VFE1 PIX stream-on remains rejected before hardware setup; IFE0/Lite/RDI behavior remains unchanged.
9. The dynamic BUS-address path is now exact: Windows RVA `0x1dd20` writes `IMAGE_ADDR +0x04` and FULL `META_ADDR +0x40` in the nine-client order, with the initial set after BUS enable/before ISP start completion and later sets per frame. Static `0017` accepts Linux DMA IOVAs only and retains `prepare/update/stop` behind an unreferenced private table. Captured Windows IOVAs/ring strides are forbidden and VFE1 PIX remains stream-blocked.

## Policy consequence

An RDI frame can be useful later as a diagnostic transport proof, but **must never be called Windows parity or accepted as the production endpoint**. E003h remains static until the IPP/VFE1 pixel pipeline and lifecycle can be represented without inventing behavior.

## Safety state

- Golden remains saved default and byte-exact.
- No candidate initrd/DTB/GRUB entry was created.
- No module was loaded.
- No sensor stream write occurred.
- No front frame was attempted.
