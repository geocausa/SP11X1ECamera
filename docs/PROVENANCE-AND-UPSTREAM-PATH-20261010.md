# Data provenance, licensing and the upstream path (front camera), 2026-10-10

Not legal advice. This records where each piece of camera data comes from, what can be
published or upstreamed, and what must be replaced first. Rule kept: no Windows binaries,
firmware or tuning blobs (or tables copied from them) are redistributed.

## Sources and what they allow

| Source | Licence / status | Use |
|---|---|---|
| Qualcomm downstream camera-kernel (CodeLinaro `camera-kernel`, mirrored in vendor/LineageOS GPL trees; e.g. `cam_csiphy_2_1_2_hwreg.h`, `cam_cdm_util`, `cam_vfe680.h` module list) | GPL-2.0, published by Qualcomm | Usable with attribution. Upstream CAMSS PHY tables have historically been taken from these trees (reviewers ask for the exact version/tree). |
| Mainline Linux CAMSS / CSI2-PHY (Linaro, Qualcomm) | GPL-2.0 | Base for all kernel work. |
| Community GPL work (linux-surface `imx681.c` by Andre Gilerson) | GPL-2.0 | Usable with attribution; its tables are themselves from Windows I2C traces. (Other third-party SP11 camera repositories are deliberately not used as sources.) |
| Register values observed on this machine (our own I2C/MMIO traces of the device we own) | Functional values; not a redistributed file | Generally accepted upstream as "magic" sensor/PHY sequences when undocumented; reviewers prefer fewer, explained registers. Keep provenance notes. |
| Our own measurements (tone curves, CCM, AWB anchors, AE constants) | Ours | Free to publish (done: `front-ae/tuning/imx681-front-v9.yaml`). |
| Windows driver package files (`*.sys`, `com.surface.sensormodule.*.bin`, CamX/Chromatix tuning) | Microsoft/Qualcomm copyright, no redistribution licence | Do not redistribute, and do not copy their tuning tables (colour matrices, shading grids, tone curves). Not accepted by linux-firmware or libcamera without a vendor licence. |

## Status of each front-camera component

| Component | Where values come from | Publishable / upstreamable? | Action |
|---|---|---|---|
| CSIPHY C-PHY receive sequence (x1e80100, Gen2 v2.1.2) | Captured from the Windows CSI driver on this machine | **Yes - matches Qualcomm's GPL table.** Checked against `cam_csiphy_2_1_2_hwreg.h` (Qualcomm Innovation Center, GPL-2.0-only; LineageOS `android_kernel_qcom_sm8650-modules` lineage-22.2, sha256 1f5dc382...): our writes equal `csiphy_3ph_v2_1_2_reg` + `datarate_212_2p5Gsps` (our 2.4 Gsym/s falls in that bin) plus `csiphy_common_reg` (CTRL7=0x7a) and reset-exit 0x0e. Windows-only extras: a final per-lane 0x?94=0x09 (GPL leaves 0x01), one 0xa00=0 write, and different common IRQ masks. | Re-express the table as GPL base + 2.5 Gsps data-rate table with attribution; test whether the 0x09 lane write is needed; use GPL (or zero) IRQ masks. Upstream target: C-PHY in the standalone `phy-qcom-mipi-csi2` driver (O'Donoghue, v15, D-PHY only today). |
| IMX681 sensor init (364 + 68 writes) | I2C trace of the Windows driver on this machine | Community-acceptable (trace-derived sensor tables are common, e.g. Gilerson's linux-surface table). For mainline, reduce to explained registers. | Keep; document; later minimise. |
| ISP (IFE) startup profile `imx681-2560x1440-nv12-v1.bin` (2661 scalars + 26 KB tables) | Windows runtime command lists (CamX output) | **No.** Contains vendor tuning tables (shading, demosaic/denoise, etc.). Kept private on the lab machine. | Replace with an open profile generated from our own parameters (see below). This is the main blocker for a distributable front camera. |
| Kernel ISP topology / CDM encoding | Reconstructed; CDM encoding from Qualcomm's published GPL camera driver | Yes | - |
| Tone curves, CCM, AWB, AE (IPA) | Our measurements | Yes (published) | - |

## IFE (ISP) module map of the startup profile

Register blocks in the private profile, named from the GPL `cam_vfe680.h` IPP module list
(order DEMUX, CHANNEL_GAIN, BPC_PDPC, BINCORRECT, COMPDECOMP, LSC, WB_GAIN, GIC, BPC_ABF, BLS,
BAYER_GTM, BAYER_LTM, LCAC, DEMOSAIC, COLOR_CORRECT, GTM, GLUT, COLOR_TRANSFORM, UVG, ...) and
our own earlier register work. Names marked ? are not yet confirmed.

| Base | Contents in profile | Module | Class |
|---|---|---|---|
| 0x3b60 | 13 regs | DEMUX | functional (Bayer order, gains) |
| 0x3d08/0x3d58 | 512 B table + 10 regs | BPC_PDPC | tuning-light (PD pixel map, thresholds) |
| 0x3f60 | 3 regs | BINCORRECT | functional |
| 0x4308/0x4358 | 3 x 884 B (17x13 mesh) + 13 regs | LSC | **tuning** (lens shading) |
| 0x4560 | 13 regs | WB_GAIN | ours (AWB) |
| 0x4708/0x4758 | 512 B + 5 regs | GIC | **tuning** (noise model) |
| 0x4908/0x4958 | 256 B + 26 regs | BPC_ABF | **tuning** (denoise) |
| 0x4b60 | 7 regs | BLS | measurable (black level) |
| 0x4d60, 0x5260 | 1 reg each | BAYER_GTM / LCAC ? | probably disabled |
| 0x5408/0x5458 | 2 x 68 B + 22 regs | DEMOSAIC ? | **tuning** (interpolation) |
| 0x5660 | 5 regs | ? | to identify |
| 0x5860 | 11 regs | COLOR_CORRECT | ours (CCM) |
| 0x5a08/0x5a58 | 2048 B + 263 regs | GTM/LTM ? | **tuning** (tone mapping) |
| 0x5f08/0x5f58 | 3 x 1024 B + 3 regs | GLUT (gamma) | ours (per-frame LUT) |
| 0x6160 | 19 regs | COLOR_TRANSFORM | functional (BT.601) |
| 0x6360 | 1 reg | UVG ? | to identify |
| 0x9860-0x9e94, 0xa008-0xa2e0 | scalers, crop/round/clamp, DSX | output path | functional (from mode) |
| 0xb060-0xbe70 | AEC BE, BHIST, tintless BG, AWB BG, BF, RS | statistics | functional (geometry) |
| 0x0024, 0x002c, 0x008c, 0x0090 | top core cfg / period | top | functional |

## Path to a distributable, upstreamable front camera

1. **Open ISP profile generator.** Split the 2661 scalars into functional values (geometry, formats,
   bus/write-master, scaler, enables: derivable from the mode) and tuning values. Replace tuning
   with our own: measured black level and lens shading (flat-field captures), our tone/CCM/AWB,
   neutral demosaic and denoise settings. Validate against the current private profile with the
   same Windows-reference method used for v9.
2. **C-PHY in the CSI2 PHY driver**, with the GPL-sourced 2.1.2 table, after Heidelberg's C-PHY
   rework lands (O'Donoghue asked for C-PHY to move there).
3. **libcamera**: the IPA already computes per-frame parameters; upstream needs a stable uAPI for
   the VFE parameter and statistics buffers (as rkisp1 / mali-c55 have).
4. **RDI raw path**: review CSID RDI drop/crop defaults and the VFE-680 RDI write-master mode
   ourselves when the IR or rear camera uses RDI.

## Checked and not needed

* Line-length / FIFO overflow on a single 2.4 Gsym/s trio: our 3840x2160 mode uses line length 6752 at 30 fps (9.38 us/line, about 75% link
  occupancy even on one trio), and all runs reported zero CSID errors.

Sources: Heidelberg C-PHY CAMSS series (v5-v9); Qualcomm C-PHY
series for sa8775p/sa8300 and O'Donoghue's review; O'Donoghue `phy: qcom-mipi-csi2` v15;
linux-media review of CSIPHY Gen2 v1.2.2 tables (table sourcing from downstream trees).
