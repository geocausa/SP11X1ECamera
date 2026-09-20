# E004is — rear RGB Bayer10 to desktop NV12, real archived frame (offline)

2026-09-20. SP11 Golden v4. Parent `ae523f0`.

## Both RGB cameras: distinct input surfaces, common downstream target

The previously accepted **rear OV13858** camera uses the RDI0 route,
sensor/media-bus `SGRBG10_1X10 / 4076x2806`, V4L2 video format
`V4L2_PIX_FMT_SGRBG10P` (`pgAA`), and a proven `5104`-byte
padded line stride. One frame occupies precisely
`5104 * 2806 = 14,321,824` bytes. The accepted E004dz one-shot
streamed a rear colour-bar frame followed by eight normal rear frames
(sequences 0..7, approximately 30 fps), returned the route to neutral,
then streamed 27 front RGB QC10C frames in the **same boot**, with
suspend/return-to-Golden checks. This proves both hardware paths and
rear-to-front handoff at the camera level. It does **not** prove an
ordinary desktop video interface for either source.

The existing **front IMX681** accepted VFE1 FULL output is processed,
compressed `QC10C/TP10-UBWC`, 2560x1440, one frame 7,778,304
bytes. **Never** submit it to the new rear Bayer unpacker or any
linear NV12 scaler. The E004ij front desktop scaler only accepts
*already verified, genuinely linear* NV12; that front physical
source is still blocked pending exact ISP and UBWC state authority.

## E004is implementation and limitations

`rear-bayer-nv12-proxy.py` provides a bounded, offline-only
first rear desktop-format handoff. Its unpacker implements the exact
current Linux V4L2 packed-Bayer spec for `pgAA`: every four
samples comprise four high-order bytes and a fifth byte holding the
two low bits per sample in positions 0..7. It validates **full frame
size**, even image dimensions, the 16-byte-aligned per-line 5104
stride and row padding, reconstructs GRBG plane order (G/R then B/G),
and derives a simple **2x2 Bayer-tile colour proxy** (not true spatial
demosaicing). It centre-crops to the downstream 16:9 aspect ratio,
resizes to 1920x1080 and exports a single 3,110,400-byte
`NV12` frame (Y first; interleaved Cb/Cr from 2x2 UV averaging).

Colour caveats: Pillow approximates full-range BT.601 YCbCr. There
is no rear lens shading, white balance, black-level correction,
demosaic interpolation, colour-correction matrix, tone mapping,
orientation calibration, cadence control or Windows IQ parity.
The resulting image is an **uncalibrated colour preview**, not
a production camera image. Full sensor geometry is cropped in
height to 16:9 rather than being stretched or presented as a
still-photo replacement. Runtime throughput and kernel/desktop
virtual-device exposure remain UNTESTED.

Only exact-size ordinary input files are accepted; known wrong
QC10C and proposed front linear NV12 sizes are rejected. Inputs
cannot be symlinks. Output must be a new private directory below
`/tmp`, with a staging directory, frame file mode 0600,
output folder mode 0700, content SHA-256 and no overwrite. An
optional `--reference-colorbar` flag admits only the
byte-exact accepted E004dz rear colour-bar frame, independently
pinned SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`.

Do not commit, expose or retain raw optical footage or converted
preview files. The source colour bar is a previous non-user-scene
test pattern, not fresh live output. No V4L2, DRM, IR, PMIC, GRUB
or application device was opened.

## Actual SP11 validation

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004is-rear-bayer-to-nv12-offline \
  -p 'test_rear_bridge.py' -v
```

Nine tests PASS, including byte-exact V4L2 10-bit low-bit packing,
a known synthetic GRBG colour tile and exact Cb/Cr byte order,
invalid dimensions/frame lengths, QC10C/foreign-format rejection,
symlink/output confinement and non-overwrite, and a **real previously
captured SP11 rear colour-bar frame** converted to a private
1920x1080 NV12 frame of the exact expected length and verified
SHA-256. The frame also passed a real GStreamer `rawvideoparse`
NV12 caps -> `videoconvert` -> `fakesink` offline pipeline. The
archived rear colour-bar original stays unchanged.
Tests leave no converted optical file outside their temporary
directories.

For a private manual offline preview with the accepted colour bar:

```sh
python3 experiments/E004-front-ir-vd55g0/e004is-rear-bayer-to-nv12-offline/rear-bayer-nv12-proxy.py \
  --input experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw \
  --output-dir /tmp/my-new-private-sp11-rear-preview --reference-colorbar
```

This command creates a private binary preview in the new directory;
it does not activate a camera or publish a device. Remove the
directory when done.

## Remaining two-camera desktop milestones

1. Rear: validate a *new*, privacy-controlled, full optical image
   sample and calibrated Bayer-to-RGB ISP-equivalent processing;
   establish bounded live-stream latency and a standard V4L2/libcamera
   app-facing NV12/RGB device, with explicit rear controls, camera
   orientation and safe PM/session recovery.
2. Front: prove QC10C decode/import or a genuine separate uncompressed
   ISP output, safe compression-mode reset and colour correction;
   connect it to ordinary desktop NV12 only after that proof.
3. Both: expose separate, correctly named/selectable front and rear
   devices without simultaneously driving exclusive CSI/ISP paths;
   validate switching, repeated capture, long-running cadence,
   thermal/suspend/recovery, app compatibility and reversible default
   installation. E004iq's consumed pre-camera GRUB-environment failure
   remains separately gated before any new unique live experiment.
4. Protected IR/Windows Hello remain outside this ordinary RGB
   preview and require independent illumination safety and legitimate
   trusted-worker admission.
