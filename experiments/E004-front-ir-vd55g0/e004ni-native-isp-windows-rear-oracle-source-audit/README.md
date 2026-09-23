# E004ni — user-selected native Qualcomm ISP + SP11 Windows camera oracle

Date: 2026-09-23. SOURCE-ONLY/read-only investigation, no camera or
IR hardware experiment and no change to Golden or Windows. User now
selects the previously optional SECOND track: pursue real native
Qualcomm hardware ISP and the same-SP11 Windows OEM camera stack
as the reference for FRONT and REAR usable RGB image quality.
The proven software RAW10->NV12 app-facing front1080/rear4K path
is RETAINED as safe non-default fallback, not discarded or
silently re-promoted as final image-quality solution.
This selection supersedes the earlier software-FIRST and ask-later
priority in AGENTS.md and RGB-PHASED-ROADMAP.md. It does NOT
grant permission to install Windows drivers in Linux, flash
unverified firmware, rearm old candidates, change the persistent
Golden image, activate IR or treat OEM parity as already done.

## 2026-09-23 installed Windows stack — this physical SP11, READ-ONLY

Linux read-only mounted the SAME SP11 Windows NTFS partition privately,
read original DriverStore INF text and file metadata, compared the
selected actual rear packages to pre-existing independent machine
Windows ACPI/driver inventory, and UNMOUNTED the Windows volume
without alteration. No camera photos, pixels, RAW or image hashes
were opened or sent, and NO proprietary binary/firmware/tuning
payload is committed or copied to another machine.

Exact rear device: ACPI OVTID858, Microsoft Surface board subsystem
MSHW0491, OmniVision OV13858, on Qualcomm X1E80100 Spectra 695
family ISP. Previously established Windows live rear sensor driver:
CameraRearSensor, MIPI qcCameraMipiCsi, ISP qcISP, common platform
qcCameraPlatform. Selected Surface rear extension is
surfacecamrearsensor_extension8380.inf, dated2025-04-25 driver
version1.0.4258.7908. Its MSHW0491 install SECTION links
the exact filenames:
  SCFG_REAR_MSHW0491.bin          (sensor configuration)
  CAMS_RES_MSHW0491.bin          (camera resource map)
  com.surface.sensormodule.rfc_ov13858.bin
  com.surface.tuned.rfc_ov13858.bin   (selected rear tuning)
  com.qti.tuned.default.bin          (default Qualcomm tuning)
The same INF includes a DISTINCT MSHW0561 branch that selects
com.surface.tuned.rfc_ov13858_MSHW0561.bin; this is NOT the
verified selected MSHW0491 board tuning. Do not swap revisions
or casually substitute front/IR/another Surface SKU calibration.
Read-only SHA-256 of FOUR selected files matches earlier
oracle/windows-e000-inventory.md:
  sensor module: f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14
  selected tuning: 4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635
  sensor cfg: fa1d4b79ac3305ed822aae7fb2d1676d28eb130cb651b2b7f84d208aab64652a
  resource cfg: 2d356bbfaf07ced1e5c03014a5c496b12107f5dc489c4333052565d5a5dcc2
This proves installed file identity/selection, NOT how every
ISP module parameter is applied live or whether any Windows
tuning blob can be consumed by the Linux camera subsystem.

Windows OV13858 sensor driver surfacecamrearsensor8380.sys
implements ACPI OVTID858. Qualcomm qccamisp8380.sys Windows
kernel driver installs CAMERA_ICP.mbn and CAMERA_ICP_AAAAAA.elf
(ELF32 Xtensa device firmware, NOT a Linux ARM64 executable).
The Windows camera AVStream stack surfacecamavs8380.sys
registers the ARM64 Windows PE QcDeviceMFT8380.dll and MFT
CLSID {4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}.
The Surface AVStream extension for the REAR camera enables
the DeviceMFT chain and rear OEM camera profiles; its
high-quality-photo/profile settings and the selected rear
extension have light-dependent multi-frame configuration
(normal4 frames, low-light8, ADRC-based-selection0) for
this MSHW0491 branch. A specific Windows VideoRecord 4K
NV12 capture is NOT evidence the high-quality/multiframe
photo profile was active. Actual preview rendering, photo
processing and OEM calibration must be kept distinct.

Existing E003h front-only Windows live+static oracle work
already associated QcDeviceMFT/CamX with DemuxBLS, PDPC,
LSC, WB, GIC, BPCABF, GTM, Gamma and DSX instruction
inputs to qccamisp. Front IQ producer/consumer boundary
and module-input materializer have been derived offline,
with more extensive local 007x front LSC/tintless traces.
DO NOT present those front ISP captures as an independently
measured REAR steady-state ISP tuning stream. Reuse the
front infrastructure, EXPLICITLY substitute observed
MSHW0491 OV13858 rear sensor modes, correct camera ID,
real selected rear tuning and rear graph/CSI path.

## What Linux has and what it does NOT yet have

E004ne (last complete original both-camera RGB test) captured
real native front1080 and rear4K RAW10 via CSI/CAMSS RDI
bypass, CPU Bayer-to-NV12 software publisher and ordinary
UID1000 app endpoints at >=29fps with exact controls
restored, final complete neutral and Golden return.
That is NOT Windows native hardware ISP output; consumer
BT601 tags do not provide demosaic, native AWB, LSC,
black-level calibration, tone mapping, advanced noise
control or window-equivalent picture detail.

The earliest E003h front VFE1 PIX/QC10C one-shots initially
timed out before first Epoch0; they are HISTORICAL failures.
LATER E003i-Z independently proved 6 REAL source-generation-
matched front VFE1 hardware QC10C output frames with actual
AEC/BHist/AWB stats, correct STREAMOFF and Golden return.
E003i-HY then passed an ORIGINAL 27-frame native front
VFE1 PIX QC10C production stream on the protected-Golden-
derived camera DTB; E003i-IG and IH independently validated
bounded front/rear same-boot neutral handoff in both orders.
Those are ACTUAL native Linux FRONT hardware processed output
and IQ stats, NOT a Windows-colour-parity front app-facing
linear NV12, dynamic native AWB/AE perfection or proof of
any rear OV13858 hardware-processed 4K frame. The rear
hardware PIX route is independently UNPROVEN;
do not reuse front CSI, LSC, geometry or camera ID.

The Windows kernel .sys / user MFT .dll are Windows
ARM64 PE components and cannot be simply loaded by
Linux as its native camera drivers. The Xtensa ICP
firmware and proprietary tuning resources may be
usable only with a separately validated compatible
Linux loader/control/IPC and appropriate local
licensing/usage, not by copying the Windows stack
or flashing unknown firmware into a Golden boot.
No proprietary Windows driver files are in Git.
A September2026 Linux CAMSS OPE upstream patch series
adds a memory-to-memory Bayer-to-YUV ISP for OTHER
Agatti/Shikra/QCM2290 platforms, not proven compatible
with the X1E80100 Spectra pipeline. Do not assume
it is the same hardware or install it blindly:
https://lists.openwall.net/linux-hardening/2026/09/07/14
https://lists.openwall.net/linux-hardening/2026/09/07/18
https://lists.openwall.net/linux-kernel/2026/07/10/727

## Execution priorities and exact decision gates

0. Reuse existing E003h/007x Windows front ISP evidence and
   Windows rear-on-device E000/E001 oracle BEFORE new tracing.
   Identify absent rear-specific CamX config and real HAL/ISP
   active chain from source-backed records, not image colour.
1. Prepare a fresh uniquely source-locked **WINDOWS** rear
   3840x2160 RGB and high-quality-photo oracle on SAME SP11.
   Restrict to visible-light OV13858; measure camera mode,
   app/native automatic controls, metadata, rear camera ID,
   selected MSHW0491 tuning, driver components actually active
   and preview-vs-still processing differences; where needed,
   narrowly bounded SP7 KD observation of actual rear path.
   Exclude SP7's FAULTY lower LCD band: known chart upper60%
   only, with verified chart-visible window and independent
   screen-content/lighting/timing/pose registration.
   No optical image/pixel/RAW/hash export to SP7, Git or chat.
   Return Windows to protected Golden with proven EFI/boot
   restoration, preserve local-only private image originals.
2. Source-only build FRONT and REAR native Linux ISP boundary:
   distinguish proven CSI->RDI transport vs PIX/ISP
   hardware-producing and accepted host/buffer/firmware
   paths, front vs rear sensor topology and selected tuning.
   No default kernel/firmware replacement, no IR/OS suspend.
   Require independent evidence of compatibility before any
   Windows firmware, QCOM OPE, IQ command or vendor-package
   attachment. Do not run outdated 003x/004x payloads or
   rearm prior Windows/Linux one-shots.
3. Only after hardware path and source-only safety tests,
   execute a NEW distinct one-shot protected candidate:
   one live optical hardware ISP frame with expected
   actual first-frame bytes, geometry/format, native
   metadata/controls, independent app decode; no unsafe
   stale buffer replay and no mock/canned ISP output.
   Keep separate strict front1080/rear4K >=29fps entire
   and EVERY real 30-frame gain interval, source gaps0,
   native supported controls exact restore, front->rear->
   off->quit, independent final119-edge neutral, GPU/
   firmware checks and automatic protected Golden return.
4. With real processed frame, compare same registered
   upper-panel RGB/neutral/dark chart on SP11 only,
   determine colour channel/CFA, AE/AWB/LSC and genuine
   detail/noise vs OEM Windows, verify no overexposure
   or generated pseudo-detail. Only then consider
   opt-in native-ISP ordinary daily service readiness.

No new Windows boot, camera candidate or optical image
capture occurred during THIS source-only ISP priority
audit. Windows NTFS read-only mount was unmounted and
Golden camera/IR defaults remained OFF. Open research
questions are explicitly NOT treated as completed proof.
