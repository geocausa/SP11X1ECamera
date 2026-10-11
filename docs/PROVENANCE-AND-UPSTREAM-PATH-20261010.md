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
| CSIPHY C-PHY receive sequence (x1e80100, Gen2 v2.1.2) | Captured from the Windows CSI driver on this machine | **Yes - matches Qualcomm's GPL table.** Checked against `cam_csiphy_2_1_2_hwreg.h` (Qualcomm Innovation Center, GPL-2.0-only; LineageOS `android_kernel_qcom_sm8650-modules` lineage-22.2, sha256 1f5dc382...): our writes equal `csiphy_3ph_v2_1_2_reg` + `datarate_212_2p5Gsps` (our 2.4 Gsym/s falls in that bin) plus `csiphy_common_reg` (CTRL7=0x7a) and reset-exit 0x0e. Windows-only extras: a final per-lane 0x?94=0x09 (GPL leaves 0x01), one 0xa00=0 write, and different common IRQ masks. | **Done (build 43, `csiphy_x1e_cphy_gpl=1`):** table generated from the GPL arrays (109 writes), IRQ masks zeroed as for other targets, no 0xa00 write. Runs ae-25 (with 0x09) and ae-26 (`csiphy_x1e_cphy_lane09=0`, pure GPL) both PASS: 1200/1200 frames, 0 CSID errors, 0 metadata mismatches. The Windows-only extras are not needed. Upstream target: C-PHY in the standalone `phy-qcom-mipi-csi2` driver (O'Donoghue, v15, D-PHY only today). |
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
| 0x3d08/0x3d58 | 512 B table + 10 regs | BPC_PDPC | **not needed**: disabling (0x3d60 bit0) gives no measurable change (ablation run ae-29) |
| 0x3f60 | 3 regs | BINCORRECT | functional |
| 0x4308/0x4358 | 3 x 884 B (17x13 mesh) + 13 regs | LSC | **replaced by ours**: measured flat field (camera on diffuser over the SP7, LSC off, linear), `open-profile/fit-lsc.py`, table `front-ae/tuning/imx681-front-lsc-v1.bin`. Format: 13x17 x u32, bits 0-12 channel gain, bits 14-26 green gain, Q10; sel1 R/G, sel2 B/G, sel3 zero. Uncorrected corners 0.17/0.21/0.20 (R/G/B) -> 0.64-0.67 with strength 0.82; colour spread R/G 1.29 -> 1.04, B/G 1.08 -> 1.03. |
| 0x4560 | 13 regs | WB_GAIN | ours (AWB) |
| 0x4708/0x4758 | 512 B + 5 regs | GIC | **not needed**: disabling (0x4760 bit0) gives no measurable change, no green-imbalance checker pattern (ae-30) |
| 0x4908/0x4958 | 256 B + 26 regs | BPC_ABF | **tuning, still vendor**. Enable 0x4960 = bit0 module, bit8 filter, bit9 no measurable effect. Filter off (ae-31, ae-36): temporal noise +15-20 %, isolated defects in flat areas +16 %, checker energy +27 %. **Noise LUT now ours**: the 64-entry table (bits 0-8 inverse noise level, bits 9+ decrement to next entry) is generated from our measured noise model var = 0.147*m + 0.79 (8-bit linear units, analogue gain 16; linear capture ae-40) as v_i = S/sqrt(i + 1.34), S = 450 (`open-profile/gen-abf-lut.py`, kernel `native_front_abf`). Strengths 300/450/650 (ae-41..43) all give the same noise and sharpness as the vendor table, so the filter is driven by its registers. **Register set now ours** (`front-ae/tuning/imx681-front-open-regs.txt`, runs ae-44..ae-74): 18 registers have no measurable effect alone or together and are set to 0; three thresholds (0x49d0/0x49d4/0x49e0) stay saturated (0 gives heavy smoothing); 0x4968 and 0x4988 are the filter parameters, set to the optimum of our sweep (2/8 and half/double both weaken the filter). The complete open configuration (ae-74) matches the vendor profile at fixed exposure (mean abs dY 1.16, run-to-run floor ~1.0). |
| 0x4b60 | 7 regs | BLS | **measured by us**: dark frames (BLS off, then offset 1200 at gain 1.0) give pedestal 1649 in BLS units (offset field = reg 0x4b68[31:16], gain 0x4b6c = 2048*65536/(65536-offset)). Pedestal rises to ~1900 at sensor digital gain 4x. |
| 0x4d60, 0x5260 | 1 reg each | BAYER_GTM / LCAC ? | probably disabled |
| 0x5408/0x5458 | 2 x 68 B + 22 regs | not demosaic | **not needed**: disabling (0x5460 bit0) gives no measurable change (ae-32); the demosaic itself is not in the profile |
| 0x5660 | 5 regs | colour/level stage (enable 0x5660 = 0x4001; generic constants 0, 0x80, 1<<24, 0x66) | functional: disabling darkens mid/high tones by 18-49 and shifts U/V by -30 (ae-33) |
| 0x5860 | 11 regs | COLOR_CORRECT | ours (CCM) |
| 0x5a08/0x5a58 | 2048 B + 263 regs | tone mapper (behaves locally: lifts shadows more in darker scenes) | **tuning, disabled in the open configuration**. Off (ae-34): mid tones -3 to -4 at fixed exposure, shadows -6 to -8 under auto exposure; sharpness and noise unchanged. Global part replaced by our gamma (tuning v10: lift fitted with `open-profile/fit-tone-lift.py`, open configuration within +-1.3 of the vendor profile at fixed exposure, ae-39); the local shadow lift in dark scenes (about -6 at auto exposure) is still missing and needs our own local tone mapping. |
| 0x5f08/0x5f58 | 3 x 1024 B + 3 regs | GLUT (gamma) | ours (per-frame LUT) |
| 0x6160 | 19 regs | COLOR_TRANSFORM | functional (BT.601) |
| 0x6360 | 1 reg | UVG ? | to identify |
| 0x9860-0x9e94, 0xa008-0xa2e0 | scalers, crop/round/clamp, DSX | output path | functional (from mode) |
| 0xb060-0xbe70 | AEC BE, BHIST, tintless BG, AWB BG, BF, RS | statistics | functional (geometry) |
| 0x0024, 0x002c, 0x008c, 0x0090 | top core cfg / period | top | functional |

Ablation method (2026-10-10): our own static chart on the SP7 screen (slanted edges, star,
gratings, colour patches, grey wedge; `C:\ProgramData\SP11CamCal\show-chart.ps1`), one boot per
variant with `native_front_reg_mask`, six consecutive full frames at fixed exposure plus six under
auto exposure (`open-profile/capture-front-still.cpp`), compared per pixel against a baseline boot
(`open-profile/ablate-compare.py`; run-to-run noise floor: mean |dY| ~1.0). All variants streamed
without errors. Combined open configuration (ae-38: PDPC, GIC, 0x5460 and tone mapper off, our LSC
and our black level): mean |dY| 1.08 against the vendor profile at fixed exposure, differing
only by the missing tone-mapper lift.

Known issue (2026-10-11): one of ~50 capture boots (ae-46) froze the whole machine. The capture
process stalled at frame 394 (auto exposure, 23 fps), the kernel stopped the queue after its 500 ms
IQ-packet timeout (error -110, no stop request) and the system hung in the following teardown;
the same configuration passed when repeated (ae-62). The error-path teardown needs review, and a
persistent kernel log (ramoops) should be enabled for the next occurrence. The run harness now copies
kernel messages to disk as they arrive (fsync per record). Deliberate error-path test (ae-75: capture
process stopped for 1 s at 20 s): the kernel hits the same 500 ms timeout (-110, no stop request),
the stream ends and the machine stays healthy; the freeze did not reproduce.

**Robust queue (2026-10-11, kernel build 46 `native_front_queue_robust=1` + libcamera tree 20,
`front-robust/`):** a frame without an application buffer is written to a driver-owned scratch
buffer and dropped; a frame without a new IQ packet reuses the newest parameters (stale packets
are skipped); the statistics generation still advances every frame. The pipeline accepts images
later than predicted (all admissions and the control schedule shift by the gap), retires
frame-start records of dropped frames, resynchronises after lost frame-start events (DelayedControls
reset and re-based) and the IPA accepts statistics after a gap. Results: application holding its
buffers 1.5 s (ae-77): 600/600, the pipeline's spare buffers absorb it; whole capture process
frozen 1 s (ae-80, 21 frames dropped) and 5 s (ae-83, 114 dropped, frame-start events lost): stream
recovers, 600/600, no errors. Normal streaming with the full open configuration (ae-84): 0 drops,
image identical to the earlier open run. Before: any stall over 500 ms ended the stream (ae-75).

Original gap description: the native queue is a serialized loop that needs a returned buffer and the next
IQ packet every frame. Any consumer stall over 500 ms ends the stream, and frame numbering is tied
to the IPA request id, so a later resume cannot resynchronise. A daily-driver queue needs a scratch
buffer for dropped frames, reuse of the last IQ parameters when none arrived, and resynchronisation
of the frame/request sequence, as in other V4L2 ISP drivers.

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
