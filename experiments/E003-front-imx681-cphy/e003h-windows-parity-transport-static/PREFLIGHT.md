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
10. Completion ownership is now static and fail-closed. Five live cycles show VIDEO -> AEC_BE_BHIST -> TINTLESS_BG -> AWB_BG -> RS, while exact helper RVA `0x26460` proves independent per-group FIFOs; Linux `0018` therefore does not require cross-group order. It retains two-slot QC10C/aux ownership behind an unreferenced private table and leaves BUS/ISR/VFE ops/runtime untouched.
11. Static `0019-x1e-rtcdm-corpus-materializer-unreachable.patch` closes command/data materialization only: four normalized local command inputs + 16 exact payload inputs become Linux-owned 4 KiB command slots and a compact DMI arena, with 46 Linux DMI-address patches and 20 explicit dynamic-value patches. Captured blobs/Windows allocation geometry are not embedded, and no MMIO/FIFO/VFE/runtime path references the private materializer.
12. Follow-up `0020-x1e-rtcdm-startup-dynamic-ownership-unreachable.patch` narrows that conservative 20-value boundary: independent startup corpora plus fresh KMD pass-through prove 16 formerly live-volatile words are invariant startup-template data, while only four `period_cfg +0x8c` words are start-dependent caller inputs. Live `+0x3d78..+0x3d84` still mutate after startup, so their template values are not live-state assertions. `0020` remains retained-only and adds no MMIO/FIFO/VFE/runtime path.
13. Static `0021-x1e-rtcdm-period-cfg-two-value-contract-unreachable.patch` narrows the four packet-local `period_cfg` holes to two opaque upstream start inputs: packet 0 has one value and packets 1/2/3 share the second in every accepted Windows start. It embeds no captured values, keeps four patch sites, and remains retained-only with no MMIO/FIFO/VFE/runtime connection.
14. A new Windows cross-order oracle pins packet0/1 -> VFE1 BUS static config/enable/initial addresses -> packet2/3 before `ISP_START_DONE`. Static `0022` records the full host ordering only as a private validator/contract: exact front tuple, two-value period map, and lifecycle stage identities, with hardware execution explicitly false and MIPI/sensor start excluded. It adds no hardware-helper call and leaves VFE1 PIX fail-closed.
15. Post-start scheduling is closed without arming Linux. Two same-machine Windows windows prove one complete nine-client bundle before `ISP_START_DONE`, a second complete bundle after start but before the first completion cycle, and a refill after that cycle. Exact KMD call graph pins IFE Epoch0 -> BUS address update -> RT-CDM queued-BL consume/program before completion dispatch. Static `0023` records this only as unreferenced read-only data; its original no-post-start-rewrite interpretation is historical and explicitly superseded by item 16/`0024`.
16. The clean Epoch0 selector-2 batch oracle supersedes only 0023's no-rewrite interpretation, not its scheduler order. Exactly 175 steady batches use five BLs and five main-list variants (`0x958/0x868/0x83c/0x6b8/0x5a4`); every varying command dword is a DMI address or register value. `+0x008c/+0x3b70/+0x3d78..+0x3d84` are queued per-frame CDM writes, while a separate direct-MMIO rewrite remains forbidden. Static `0024` records the corrected ownership/topology only as retained data and explicitly leaves DMI payload bytes/FIFO submission unclosed.
17. Representative steady-state DMI payload bytes are now hash-closed for all five variants from local Windows source-ring/slot evidence; raw payload bytes remain untracked. Exact KMD disassembly proves the five BL sizes are upstream IQ-packet shapes, not a hidden KMD selector. Frame-varying IQ values and the exact GEN_IRQ tag source remain upstream inputs; runtime stays blocked.

18. GEN_IRQ tagging is now exact for the accepted front stream: 245 consumed requests prove BL4 userdata equals `low32(requestId)` with `subRequest=0`; the first two tags are the already-proven primed batches. A second `0x83c` payload sample confirms only `4308/1` and `4308/2` vary. The remaining steady-state producer is upstream IQ packet content, not KMD tagging/selection.
19. The exact Surface camera INF registers `QcDeviceMFT8380.dll` as DeviceMFT; its CamX Titan680 builders own all 24 changing steady register fields and all eight DMI register identities. LSC/Gamma/GTM/DSX/PDPC/WB/Demux dependency families are statically named, while proprietary algorithm reproduction remains explicitly out of scope. The next Linux step is an unreachable consumer/materializer only.

## Policy consequence

An RDI frame can be useful later as a diagnostic transport proof, but **must never be called Windows parity or accepted as the production endpoint**. E003h remains static until the IPP/VFE1 pixel pipeline and lifecycle can be represented without inventing behavior.

## Safety state

- Golden remains saved default and byte-exact.
- No candidate initrd/DTB/GRUB entry was created.
- No module was loaded.
- No sensor stream write occurred.
- No front frame was attempted.
