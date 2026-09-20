# E004if — front processed-output desktop conversion investigation

2026-09-20: the maintained front launcher emits processed YUV, not Bayer.
The previous E004ie wording "raw" meant uninterpreted capture-file bytes;
it was misleading and is corrected in the maintained ordinary-camera guide.

## Confirmed current contract

Current production C defines 2560x1440, stride 3584, allocation 0x76b000,
27 frames, QC10C (fourcc Q10C). The exact same-machine Windows FULL layout
identifies processed TP10 UBWC YUV420 with Y_META/Y_TP10/C_META/C_TP10.
Source: experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/vfe1-full-layout/README.md.
That historical document's runtime-blocked conclusions are superseded by
later accepted capture work; only its independently derived layout is used.
The public kernel reserved-format documentation also identifies QC10C as
opaque, compressed 10-bit YUV420, not linear NV12 or sensor Bayer.
https://docs.kernel.org/userspace-api/media/v4l/pixfmt-reserved.html

New src/front-imx681/desktop-output-contract.json exposes the derived
contract and unresolved conversion requirements to future integration.
No kernel, capture helper or accepted package hash was changed.

## Actual installed GPU query

New tools/camera-gpu-import-status.py dynamically enumerates render nodes,
creates GBM/EGL display connections, and queries advertised DMA-BUF formats
and modifiers. It opens no camera and imports no image, submits no rendering
and changes no display mode. Handles are closed on success and failure.
The actual SP11 query enumerated 71 formats on renderD128, Mesa EGL 1.5.
NV12 advertises linear and Qualcomm compressed modifier 0x0500000000000001,
both external-only. P010 and P030 advertise only linear, external-only.

This does NOT establish a supported QC10C import/conversion route in the
installed EGL interface. Relabeling 10-bit QC10C as compressed 8-bit NV12
would be wrong. P030 packing resemblance alone also does not prove exact
QC10C-to-DRM mapping, compression version, offsets, metadata or colorimetry.
This is a capability query, not a failed actual image-import attempt.
No claim is made that the hardware, another graphics API or future driver
cannot support the conversion.

## Next concrete choice

Inspect Mesa/Freedreno's supported 10-bit compressed import implementation
and exact layout compatibility before any archived-frame import. If absent,
the alternatives are independently validated decompression support or a
separate linear-output ISP candidate. The latter changes the accepted ISP
output contract and needs a new hardware experiment; it must not silently
replace Windows-parity QC10C. Rear RAW capture is a separate standard
Bayer-processing option and does not solve front QC10C.

Only after a trustworthy conversion path is demonstrated should work expand
the current 27-frame capture into continuous desktop output. GStreamer
plugin presence and transport completion are not image-display acceptance.
IR processing/illumination and protected-signing status are unchanged.

Reproduce: python3 tools/camera-gpu-import-status.py
