# E004ie — desktop prerequisites and offline native IR preview

2026-09-20. User selected practical ordinary Linux camera development while
protected Windows Hello remains blocked. This does not abandon the original
parity target or authorize illumination/login.

## Machine changes

Installed only gstreamer1.0-libcamera 0.7.0-1ubuntu2 using --no-upgrade and
--no-install-recommends. The broader initial apt simulation proposed 12
PipeWire upgrades; that plan was NOT executed. The narrowed transaction
installed one package, upgraded none and removed none. gst-inspect confirms
libcamerasrc 0.7.0. PipeWire remains 1.6.2-1ubuntu1.1.

The new tools/camera-desktop-status.py reports installed versions, per-user
service states and enumerated device-node names, without opening a camera,
starting a service or loading modules. Its actual report shows PipeWire,
WirePlumber and portal active. No video/media devices exist on protected
Golden, as expected. Installed prerequisites do not prove camera readiness.

## Offline IR application bridge

New src/sp11-camera-hlos-worker/sp11-offline-preview.py accepts an ordinary
regular-file neutral NV12 batch of 1..16 frames at 644x604. It invokes the
unchanged native transaction wrapper and writes a private, new Y4M preview
only after processing completes. It never overwrites an existing output.
Neutral chroma permits lossless conversion from NV12 to planar I420.
Playback fps is user-supplied presentation timing, not measured sensor fps.
Output contains images and persists until the caller removes it. Use only
ordinary nonprotected offline inputs, not protected camera buffers.

The reproducible test compiles actual native stream and independent one-shot
workers, processes two synthetic grayscale frames, then decodes Y4M with
stock GStreamer and checks pixels against independent one-shot output.
The first comparison incorrectly assumed tightly packed decoder planes;
the corrected test removes GStreamer four-byte chroma-row padding before
pixel comparison. All pixels match. Existing output preservation and three
invalid-input cases pass. This is no live camera, optical or biometric test.

Run: PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-front-ir-vd55g0/e004ie-desktop-camera-foundation/test_preview.py

## Actual next RGB work

The front maintained launcher currently captures exactly 27 QC10C raw frames
and has a root-only hardware setup path. It is not a continuous processed
webcam producer. Do not market this as everyday app readiness merely because
libcamerasrc is installed. Next inspect the accepted RGB output format and
processing authority, implement a bounded processed-output application bridge,
then checkpoint a fresh RGB-only candidate for desktop acceptance. Continuous
control, start/stop/recovery, switching and suspend remain separate tests.
Do not reuse retired one-shot identities.

IR physical safety and protected admission remain blocked. No boot, kernel,
IR illumination, PAM/login or trust-policy changes. Golden/idle guard passed.
