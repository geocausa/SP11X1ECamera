# Data provenance, licensing and the upstream path (front camera), 2026-10-10

Not legal advice. This records where each piece of camera data comes from, what can be
published or upstreamed, and what must be replaced first. Rule kept: no Windows binaries,
firmware or tuning blobs (or tables copied from them) are redistributed.

## Sources and what they allow

| Source | Licence / status | Use |
|---|---|---|
| Qualcomm downstream camera-kernel (CodeLinaro `camera-kernel`, e.g. `cam_csiphy_2_1_2_hwreg.h`, `cam_cdm_util`) | GPL-2.0, published by Qualcomm | Usable with attribution. Upstream CAMSS PHY tables have historically been taken from these trees (reviewers ask for the exact version/tree). |
| Mainline Linux CAMSS / CSI2-PHY (Linaro, Qualcomm) | GPL-2.0 | Base for all kernel work. |
| Community GPL work (linux-surface `imx681.c` by Andre Gilerson) | GPL-2.0 | Usable with attribution; its tables are themselves from Windows I2C traces. (Other third-party SP11 camera repositories are deliberately not used as sources.) |
| Register values observed on this machine (our own I2C/MMIO traces of the device we own) | Functional values; not a redistributed file | Generally accepted upstream as "magic" sensor/PHY sequences when undocumented; reviewers prefer fewer, explained registers. Keep provenance notes. |
| Our own measurements (tone curves, CCM, AWB anchors, AE constants) | Ours | Free to publish (done: `front-ae/tuning/imx681-front-v9.yaml`). |
| Windows driver package files (`*.sys`, `com.surface.sensormodule.*.bin`, CamX/Chromatix tuning) | Microsoft/Qualcomm copyright, no redistribution licence | Do not redistribute, and do not copy their tuning tables (colour matrices, shading grids, tone curves). Not accepted by linux-firmware or libcamera without a vendor licence. |

## Status of each front-camera component

| Component | Where values come from | Publishable / upstreamable? | Action |
|---|---|---|---|
| CSIPHY C-PHY receive sequence (x1e80100, Gen2 v2.1.2) | Captured from the Windows CSI driver on this machine | **Expected yes, once checked against and attributed to Qualcomm's GPL `csiphy_3ph_v2_1_2_reg` / data-rate tables.** Not yet compared against the original file (CodeLinaro blocks automated reading; needs a manual download). | Cite the GPL table; verify the data-rate rows against the downstream table for 2.4 Gsym/s (CodeLinaro blocks automated reading; needs a manual download). Upstream target: C-PHY support in the new standalone `phy-qcom-mipi-csi2` driver (Bryan O'Donoghue, v15, D-PHY only today), not inside CAMSS. |
| IMX681 sensor init (364 + 68 writes) | I2C trace of the Windows driver on this machine | Community-acceptable (trace-derived sensor tables are common, e.g. Gilerson's linux-surface table). For mainline, reduce to explained registers. | Keep; document; later minimise. |
| ISP (IFE) startup profile `imx681-2560x1440-nv12-v1.bin` (2661 scalars + 26 KB tables) | Windows runtime command lists (CamX output) | **No.** Contains vendor tuning tables (shading, demosaic/denoise, etc.). Kept private on the lab machine. | Replace with an open profile generated from our own parameters (see below). This is the main blocker for a distributable front camera. |
| Kernel ISP topology / CDM encoding | Reconstructed; CDM encoding from Qualcomm's published GPL camera driver | Yes | - |
| Tone curves, CCM, AWB, AE (IPA) | Our measurements | Yes (published) | - |

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
