# E004nj — installed Windows CAMERA_ICP vs current Linux camera host compatibility

Date: 2026-09-23. SOURCE/HEADER-ONLY read-only
audit: NO firmware flash/load/reset, camera/sensor,
IR, Windows write or Linux OS suspend. Windows
volume was mounted read-only privately on SAME SP11
and unmounted. NO proprietary firmware, DLL/SYS,
tuning payload or optical photos/pixels/RAW/thumbs/
photo hashes were copied to Git/chat/other hosts.

## Actual Windows ISP image is not an audio-DSP-style drop-in

The installed SAME SP11 qccamisp8380 DriverStore
package contains CAMERA_ICP.mbn (905,880 bytes,
ELF32 little-endian Xtensa, 21 program headers,
no section header) and CAMERA_ICP_AAAAAA.elf
(4,738,507 bytes, ELF32 little-endian Xtensa,
19 program headers, section/debug info). Those
are READ-ONLY actual ELF header metadata, not
guesses from names. OEM camera-specific rear
tuning com.surface.tuned.rfc_ov13858.bin for
OV13858 MSHW0491 is a SEPARATE source of ISP
parameters, not ICP executable. File installation
does not by itself prove Windows actually runs
which image or that Linux can execute it.

The current Linux kernel sysfs shows two running
remote processors ONLY: adsp/qcadsp8380.mbn and
cdsp/qccdsp8380.mbn. It exposes NO camera/ICP
remoteproc. The checked SP11 Linux CAMSS camera
source DOES have request_firmware_direct call
sites, but they load E003H_PIX_ORACLE_CAPSULE
host IQ/RT-CDM instruction DATA, NOT the Windows
Xtensa camera firmware executable. The current
Golden qcom-camss module advertises no
modinfo -F firmware camera boot dependency.
This combination does not prove building a
correct camera ICP loader is impossible.
It DOES establish that simply copying the
Windows firmware to the Linux firmware path,
using existing Q6 ADSP/CDSP remoteproc loading,
or executing Xtensa ELF as ARM64 Linux cannot
make the camera behave like Windows. No camera
firmware was loaded by this audit.

## Important earlier-project result correction

E003h early front VFE PIX/QC10C diagnostics timed out,
but LATER E003i-Z ORIGINAL physically generated
six front VFE1 hardware QC10C frames WITH native
AEC_BE/BHist/AWB_BG paired 3A statistics, correctly
stopped/returned Golden. E003i-HY ORIGINAL physically
generated 27 front VFE1 PIX QC10C frames under the
Golden-derived front native hardware route with
IQ producer generations and clean STREAMOFF/Golden
return. E003i-IG/IH also passed bounded rear/front
neutral handoff BOTH ways but the rear leg uses
RAW10/RDI, not a native rear PIX processed frame.

Therefore Linux already has an actual bounded FRONT
native VFE PIX hardware-processed path without
proving any Windows Xtensa ICP firmware was loaded.
Our immediately previous E004ni note incorrectly
called the first front native hardware frame unproven.
What remains unproven is Windows-parity FRONT image
quality/colour/detail and a REAR OV13858 processed
4K hardware ISP frame, high-quality still pipeline,
and ordinary app-facing 30fps native ISP service.
E004ne full 1080p/4K normal UID1000 camera pass
is a software RAW-to-NV12 preview, not that path.

## Executable next engineering boundary

1. Reuse ACTUAL accepted front E003i-HY native
   VFE1 PIX/RT-CDM and Z native 3A proof to map
   a separate REAR sensor OV13858 native PIX
   first-frame diagnostic. First independently
   verify rear CSIPHY/CSID/IPP topology, input
   Bayer mode/crop, output QC10C or validated
   true linear format, memory/SMMU SID/geometry,
   selected rear MSHW0491 sensor tuning, clock
   and IQ module source. Never replay front
   IMX681 LSC, Bayer pattern, per-camera gain
   or buffer in rear as if optical proof.
2. Use actual SAME-machine OEM Windows rear
   4K VideoRecord versus high-quality still
   mode and metadata only for unresolved ISP
   ownership/processing stages. SP7 screen has
   user-reported broken LOWER LCD band; keep
   controlled colour chart + registered patch
   ROIs within the unaffected UPPER 60%.
3. Treat CAMERA_ICP Xtensa controller loader
   as an independent CONDITIONAL project,
   only if the selected rear OEM module path
   actually requires it. First prove source-backed
   X1E ICP power/reset/clocks/IOMMU/secure-auth,
   Xtensa loader firmware-host IPC ABI/tuning
   ownership and deterministic fault rollback.
   Do not direct existing adsp/cdsp loader at
   camera ICP and do not try to load Windows
   .sys/.dll into Linux as native camera code.
4. ONLY after a fresh distinct source-pinned
   candidate proves an ACTUAL new rear PIX
   processed optical output and signed-off
   source/stats ownership, require native
   source >=29fps full and every front/rear
   real 30frame gain window, exact supported
   sensor control restore, front/rear neutral
   handoff, complete 119-edge native neutral,
   no GPU fault, IR off and automatic Golden.
   Then compare real upper-only controlled
   per-patch detail/colour vs Windows PRIVATELY
   on the same SP11; daily opt-in service is
   a separate gate.

## Reproducibility / non-optical evidence

SCALAR-ONLY-WINDOWS-ICP-VS-LINUX-HOST-COMPATIBILITY.json
records only Windows ELF header architecture/
byte counts, running Linux remoteproc metadata,
CAMSS source-only host IQ capsule call sites
and original E003i native-front success flags.
inspect_compatibility.py repeats read-only audit
on SAME SP11 when Windows volume is deliberately
mounted PRIVATE READ-ONLY. Six SYNTHETIC ELF header
and architecture tests in test_inspect_compatibility.py.
Original native-front evidence remains in
E003i/z-live-3a-runtime/RESULT.json and
E003i/hy-production-one-stream-r27/RESULT.json.
No optical pixels, spatial arrays, RAW, thumbnails
or photo hashes were read by this static audit.
