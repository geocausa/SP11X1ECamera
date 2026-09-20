# E004jj — front video-format ownership and false-converter gate (offline)

2026-09-20. Parent `0490d76`. **Read-only, no Windows boot or driver
execution, no Linux camera boot, no optical image/pixel read or camera/IR
activation.** This work follows E004ji's real Adreno X1-85 Vulkan format
query and the E004jh physically proven temporary rear webcam.

## Source-pinned same-machine Windows evidence

The archived Qualcomm SP11 Windows Device MFT
`QcDeviceMFT8380.dll` (23,998,368 bytes, SHA-256
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`)
contains readable UTF-16 format references
`IMAGE_FORMAT_UBWC_TP_10`, `UBWCTP10` and
`IMAGE_FORMAT_LINEAR_NV12`. This is an **offline binary-string
observation** indicating that the driver includes code referencing both
format classes. It does **not** demonstrate that the MFT itself performs
the source-to-application conversion, that the named formats are in
the same pipeline, or that Windows' conversion is reproducible in a
Linux userspace utility. In the archived binary, the linear-NV12 assertion names
`bpsStripingLib.c` and the UBWC TP10 assertion names
`ipestripingmanagerwrapper.c`: BPS and IPE striping-library
**code is present**, offering narrower static analysis targets. Neither
assertion shows a real front-camera processing graph, a converter call,
nor a captured Windows NV12 pixel. The DLL remains unmodified and
unexecuted.

The independently archived custom Windows WinRT holder, SHA-256
`c3482698b31668771a8ad531455cd03b31e26793063415a9df0444cae8707d02`,
selected `Surface Camera Front / Color / VideoRecord / NV12 /
1920x1080`, created the reader and reported start status `Success`.
It does not include an application NV12 pixel-buffer sample or
bit-exact conversion reference; its format-selection success must
**not** be confused with a proven complete Windows pixel decoder.

The native Linux IMX681 camera VFE1 FULL currently captures
**compressed QC10C** (ISP-processed TP10/UBWC 2560×1440,
7,778,304 bytes per buffer; Y_META/Y_TP10/C_META/C_TP10).
It is neither raw sensor Bayer nor uncompressed NV12/P010.
The exact captured physical front stream was repeatedly validated in
E004jc/E004jh; **displayable pixels remain unvalidated**.

## Check the current Linux Iris hardware-video-decoder input

The custom Golden 7.1.5 source tree's Qualcomm Iris Gen2 VDEC
`platform_fmts_sm8550_dec` lists ONLY encoded
`H264/HEVC/VP9/AV1` for its V4L2 `VIDEO_OUTPUT_MPLANE`
**input**. Its `iris_vdec_formats_cap` lists
`NV12` and compressed `QC08C` for V4L2
`VIDEO_CAPTURE_MPLANE` **output**, not QC10C input.
The physical camera's QC10C is a *captured compressed pixel buffer*,
**not** an encoded H264/HEVC/VP9/AV1 bitstream.

Thus **do not feed captured QC10C into a video-codec bitstream
input**, rename it HEVC or mistake the decoder's output format
support for a standalone pixel-format conversion API.
Contemporary upstream Iris 10-bit work adds **QC10C/P010
as decoder OUTPUT formats for compressed video bitstreams**,
not support for QC10C image input:
https://lists.openwall.net/linux-kernel/2026/04/17/684 .
This distinguishes both directions of the proposed shortcut.

## Protected next gate

Five actual SP11 source/archive tests validate the exact MFT and
WinRT provenance SHA values, format strings, the locally installed
Iris VDEC input/output arrays, the front four-region contract and
`format-route-gate.json`, with a PASS result. No camera/codec
driver/module was loaded or configured.

**Still needed:** (a) version-matched supported Qualcomm TP10/UBWC
decompression/import with correct 10-bit pixel unpacking, metadata,
strides, colour and an independent reference image; or (b) exact
X1E80100 ISP hardware linear Y/C output and safe UBWC compression-state
reset/mode ownership verified separately before an isolated camera
boot. Then and only then can the accepted NV12-to-V4L2 webcam bridge
be extended to the **front**. Neither the current Turnip Vulkan path,
codec-decoder bitstream path nor MFT strings clears this gate.

Replay on SP11 Golden:

```sh
python3 -m unittest discover \
 -s experiments/E004-front-ir-vd55g0/e004jj-front-windows-mft-iris-input-gate \
 -p test_format_owner.py -v
```
