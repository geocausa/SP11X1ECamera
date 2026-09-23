# E004mz — private SP11-only same-camera repeated fine-pattern IQ audit

2026-09-23. Two DIFFERENT historical fully retired physical E004mx
and E004my camera one-shots had identical verified native front and
rear baseline/trial exposure/gain profile tuples, and both generated
original owner geoca-private RGB front1080/rear4K baseline and gain
photos. This non-mutating software-only audit read exactly those
eight ORIGINAL PNG files ONLY locally on SP11 with 0700/0600
ownership verification. No hardware/IR/boot/system service touched,
no image/RAW/pixel/tile/thumbnail/photo hash or detail map sent
to chat/Git/another host. The pure synthetic-only correlation
unit tests ran five cases PASS.

It samples every fourth original RGB pixel to gray with identical
method for all runs/cameras and computes only numerical correlations
of coarse Gaussian lowpass sigma8 and fine highpass relative to
Gaussian sigma2 on the downsampled grid. An independent bounded
5x5 relative-offset search covers +/-2 downsampled pixels (up to
8 original pixels) to flag possible tiny misregistration. It also
compares the near-black BASELINE captures across boots and within
each boot against the trial (gain+display tone) highpass.
No original image pixels, thumbnail, tile grid, highpass matrix,
photo/image-derived hash or source binary survives in archive.
All correlation/STD result fields are global scalars only.

Findings at the same original relative coordinates:
* FRONT gain fine highpass cross-boot correlation0.841871; coarse
  lowpass corr0.990579. FRONT BASELINE near-black fine highpass
  cross-boot corr0.806122, and each within-boot front
  baseline-vs-gain highpass correlation~0.445/0.431. A
  repeatable baseline pattern means the gain highpass MUST NOT
  be described as confirmed optical subject detail; fixed
  sensor/demosaic processing pattern and/or scene texture remain.
* REAR gain coarse lowpass corr0.999493 while fine highpass
  corr only0.047818; its nearly black baseline cross-boot
  fine highpass corr0.087524, same-boot baseline-vs-gain
  ~0.0038/0.0074. Under this exact uncontrolled dark-corner
  capture, coarse rear spatial structure is repeatable,
  fine-scale differences are NOT repeatable at fixed pixel
  coordinates. The bounded +/-8-original-pixel shift search
  did not recover a stronger correlation; it does NOT
  exclude real scene/camera misalignment, different
  illumination, rolling-shutter, interpolation, optical
  motion or nonstationary sensor noise.

These numerical clues make strong sharpening of current rear
low-light gain/tone output unjustified, and prevent claiming
front detail recovered merely from brightness or repeatable
highpass. They are NOT a noise estimate, camera diagnosis,
optical recognition, color/white-balance calibration or
Windows image-quality parity verdict. Lighting/position/
exposure integration were not independently matched across
the two boots, though native sensor control tuples matched;
no known high-contrast visible target or independent truly
dark optical reference was physically verified. More useful
automated work can start with camera-free synthetic colour
target/BT.601 NV12 matrix tests and fail-closed quality gates;
the next live optical detail acceptance requires verified
fixed visible target and separate dark reference, distinct
source-locked Golden-guarded one-shot only. Normal camera
preview/tone/temporal processing remains default OFF.

Source: repeatability.py (read-only exact private SP11-local
files); tests: test_repeatability.py (generated synthetic 2D
numeric arrays ONLY); scalar results:
SCALAR-ONLY-PRIVATE-SP11-REPEATABILITY.json.
