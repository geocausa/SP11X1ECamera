# Ordinary Linux camera development

User-selected direction, 2026-09-20: practical RGB and ordinary-memory IR
processing alongside the still-blocked protected Windows-equivalence goal.

## Desktop inventory

Run `python3 tools/camera-desktop-status.py` (or `--json`). It queries
package/service presence and lists device nodes. It never starts capture.
Golden normally exposes no cameras; this is not itself a regression.
Desktop prerequisites now include the installed GStreamer libcamera plugin.

## Offline IR preview

`src/sp11-camera-hlos-worker/sp11-offline-preview.py --help` describes the
exporter. Input is ordinary nonprotected, neutral NV12 at 644x604, 1..16
frames. Supply an existing native `sp11-offline-nv12-stream.c` executable
in a user-owned /tmp directory through `--worker`. The unchanged worker is
compiled together with the eight `sp11-parity-worker`/SWABF/SWASF core
source files used by the E004hi verifier; the E004ie regression demonstrates
the exact build and export end to end. No signing is needed for this ARM64
userspace executable.

Example with your own already-prepared ordinary offline input and worker:

```sh
python3 src/sp11-camera-hlos-worker/sp11-offline-preview.py \
  --input /tmp/session/input.nv12 --worker /tmp/session/worker \
  --output /tmp/session/preview.y4m --playback-fps 30
gst-launch-1.0 filesrc location=/tmp/session/preview.y4m ! y4mdec ! videoconvert ! autovideosink
```

Preview files contain the processed image data and are deliberately retained
for viewing; delete them when no longer needed. Cadence is for playback only.
No camera, illuminator, protected buffer, face model or login interface is
opened by the exporter. Full transaction success is required before export.

## Work remaining

1. RGB: bridge accepted capture/processing to a standard application format;
   the existing 27-frame QC10C launcher is not a continuous webcam.
2. Validate fresh RGB-only candidate capture, then repeated use, switching,
   suspend and application integration, preserving Golden.
3. IR: use offline previews for ordinary pixel work; useful live scene signal
   and independently validated illumination safety remain unresolved.
4. Keep passwords/security keys for login. Preview and face-model experiments
   provide neither liveness nor secure biometric authentication.
