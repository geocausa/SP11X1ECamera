# E004iu — bounded fast rear RGB Bayer10-to-NV12 preview (offline)

Date: 2026-09-20. Parent: `8b938ca`. SP11 running protected
Golden v4 throughout. **No camera, video or IR device opened.**

## Purpose and quality boundary

The accepted rear OV13858 RDI0 path captures `V4L2_PIX_FMT_SGRBG10P`
(`pgAA`) packed Bayer10 at 4076×2806, padded stride 5104
and 14,321,824 bytes per frame. E004is first showed a previously
captured, checksum-pinned rear colour-bar frame could be converted
offline to a **basic** 1920×1080 NV12 preview that a genuine
GStreamer `rawvideoparse ! videoconvert ! fakesink` pipeline accepted.

E004is's Python/Pillow prototype takes about **53–56 ms** per
archived 14 MB frame on SP11 in this session, longer than the
33.33 ms frame interval of 30 fps. E004iu is a separately
reviewable C11 **offline** preview converter and Python
fail-closed wrapper. The C code samples the upper eight bits
of each 10-bit Bayer pixel from the four-high-byte packed
`pgAA` group (the previous E004is 8-bit preview also discards
the two low bits), takes the G/R then B/G 2×2 mosaic tile,
averages the two greens, centre-crops to 16:9 and samples
one RGB proxy per 1920×1080 output pixel. It uses a
bounded, integer **approximate full-range BT.601** RGB-to-YUV
matrix and averages RGB for the subsampled interleaved
NV12 Cb/Cr plane.

**This is a nearest-tile colour proxy, not a proper
demosaicing/ISP pipeline.** The E004iu output does not have
the same bytes as E004is's bilinear/Pillow prototype; each
has an independently verified deterministic output SHA. E004iu
does not implement lens-shading correction, sensor calibration,
black-level correction, calibrated white balance, colour matrix,
tone mapping, noise reduction, orientation, HDR or Windows
image-quality parity. It must not be promoted as a finished
desktop rear-camera image just because its conversion is fast.

The accepted **front IMX681** VFE1 FULL frame is Qualcomm
TP10/UBWC-compressed QC10C YUV, **not Bayer, not linear
NV12**. Its 7,778,304-byte frame is explicitly rejected by
E004iu. Do not reuse this converter for front frames.

## Offline batch and source protection

`rear_fast.c` reads a **regular non-symlink** file containing
exactly 1..27 packed full rear frames and emits exactly the
same count of NV12 frames into a **new** output file, using
one C helper process. It validates input size before opening
and via `fstat`, checks each full-frame read, rejects extra
bytes, bounds the count, handles short read/write, and removes
any incomplete output on failure. Its sole memory inputs are
local files; it contains no V4L2, DRM, camera, PMIC, GRUB or
IR operations.

`rear-fast-bridge.py` compiles that helper into a
unique disposable private `/tmp` directory, checks an
ordinary fixed-size input source and its before/after
SHA-256, requires non-reference optical inputs to reside
in caller-owned private `/tmp` directories, and refuses
preexisting/symlink/unconfined output names. The optional
`--reference-colorbar` check accepts ONLY a **single**
byte-exact accepted rear E004dz archived test-pattern frame,
SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`

The generated output has mode 0600. The wrapper does not
publish a virtual video device, enable camera services, or
retain a compiled helper. The **compile, SHA hashing,
startup, sensor acquisition, runtime buffer transfer,
camera control and desktop presentation costs are not
included** in the reported C per-frame measurements.
The helper's `BATCH_IO_AND_CONVERSION_MS` measures batch
disk input/output + conversion, but not compilation or
camera-to-user memory transfer.

## Actual SP11 evidence

The accepted archived one-frame rear colour bar produces
3,110,400 bytes of NV12 (1920×1080), SHA-256:

`86f496416883d7728675802c70a0c83adb10d1a02591a56de1fe45cc3e223d0b`

Its GStreamer NV12/video-convert pipeline passed. A
synthetic full-size GRBG10 Bayer fixture with RGB=(200,100,50)
was independently checked to have NV12 Y=124, Cb=86, Cr=182
throughout the frame; the known packing/channel order is
correct for this simplified proxy. GCC ASan/UBSan execution
on the accepted archived frame passed.

The first five single-frame optimised C tests reported
**4.25–5.78 ms** of conversion alone. A later **27-frame
bounded batch** repeated the *same archived rear test
pattern* 27 times (386,689,248 input bytes and 83,980,800
output bytes); the single compiled helper reported
**3.0197 ms average conversion-only** and **5.1647 ms
average batch I/O plus conversion** per frame. The
full 27-frame NV12 stream passed the ordinary GStreamer
pipeline. Output SHA-256:

`24e822c222f4b30800e3bd29b31a6e93b17fd7efa5313e42e626a04584cfc2ce`

The 27 frames were **repetitions of one old colour-bar
frame**, NOT 27 new frames captured from the camera.
This test does not demonstrate live throughput, optical
colour fidelity, motion quality, thermal behaviour,
sensor-to-display latency, frame-to-frame cadence, or
availability in any camera application. Raw and NV12 batch
files were deleted immediately after testing.

The `test_fast_rear.py` offline suite includes 15 tests
(archived colour-bar SHA and GStreamer acceptance,
known-colour GRBG-to-NV12, GCC sanitizer execution,
four-frame batch, two **different** synthetic frames
preserving order, bad lengths and counts, QC10C-input
rejection, reference spoofing, input/output symlinks,
existing-file preservation, and private-output confinement).

## Reproduce without hardware

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004iu-rear-fast-nv12-offline \
  -p 'test_fast_rear.py' -v

D=$(mktemp -d /tmp/sp11-rear-preview.XXXXXX)
python3 experiments/E004-front-ir-vd55g0/e004iu-rear-fast-nv12-offline/rear-fast-bridge.py \
  --input experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw \
  --output "$D/rear.nv12" --reference-colorbar
# Remove the private preview after inspecting it:
rm -rf -- "$D"
```

For `--frames N`, pass one private, existing file of
exactly `N * 14,321,824` bytes containing packed rear
frame payloads concatenated in capture order. The
`--reference-colorbar` option rejects N != 1.
No script performs live capture or exposes a camera.

## Next gates for BOTH RGB cameras

Rear: use a privacy-controlled **normal optical** frame
to calibrate real demosaic/IQ; measure full capture-to-app
frame cadence, colour, orientation and resource lifetime.
A fast colour proxy alone is not a production webcam.
Front: independently prove actual safe linear ISP output
and compression-state reset **or** a correct QC10C decoder,
then verify colour and delivery to a standard app endpoint.
Finally expose two independently selectable front/rear
video endpoints and validate repeated switching, power and
suspend/recovery. The consumed E004iq camera one-shot
pre-camera GRUB-environment failure remains a separate
hardware-test safety gate. Preserve Golden and keep IR
illumination/Hello protected.
