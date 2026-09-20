# E004ig — Mesa source audit of front TP10 desktop conversion

2026-09-20. Inspected official Mesa GitLab tag mesa-26.0.8, matching the
installed upstream version, plus current main snapshots of the two decisive
Freedreno implementation files. URLs and exact source digests are recorded.
The Ubuntu downstream patch set was not independently compared; the E004if
live EGL capability query remains authoritative for the installed driver.
Main URLs are mutable; their recorded SHA256 values identify this observation.

## Findings

* freedreno_screen.c delegates modifier availability to generation-specific
  support. fd6_resource.cc routes QCOM_COMPRESSED queries through
  ok_ubwc_format and checks support again when laying out imported buffers.
* ok_ubwc_format explicitly handles the NV12/8-bit YUV texture path.
* fd6_format_table.c supplies the hardware multi-plane 8-bit YUV mappings
  but no P030/TP10/P010 mapping in either inspected snapshot.
* The generic DRI frontend does have a P030 mapping. A generic format name
  in that table is not evidence of compressed support in Freedreno.
* These findings explain the installed EGL query: compressed NV12 exists;
  compressed P030 is not advertised. Merely adding a modifier allow-list
  entry would leave texture interpretation, layout and import unimplemented.

This is not proof that Adreno cannot process the format, nor an exhaustive
review of Vulkan, display hardware, proprietary interfaces or future Mesa.
No live import was attempted. No Mesa patch or package upgrade was installed.

## Engineering decision

Do not spend another camera boot repeating QC10C capture while conversion
is missing. Do not cast QC10C as NV12 or treat its TP10 data as linear.
Two independent development routes remain:

1. Implement and validate exact TP10/UBWC decode or supported hardware import.
   Requires actual compression-version, metadata/layout and texture-format
   authority, followed by archived-frame comparison and correct colorimetry.
2. Develop a new ordinary desktop ISP-output candidate using a proven linear
   YUV mode. First inspect same-machine or exact ISP public source authority
   for supported output packer/stride/client programming. Preserve the
   accepted QC10C source and hashes; linear output is a distinct experiment
   with its own format, buffer lifetime, image and runtime acceptance.

Prefer investigating route 2 next for practical desktop use while retaining
the parity QC10C path. This is a development recommendation, not evidence that
a linear candidate is ready or that changing a packer alone is sufficient.
Rear Bayer-to-desktop processing is a separate possible delivery track.

Protected IR signing and physical illumination gates remain unchanged.
Golden, GPU driver, camera state and login configuration are unchanged.
