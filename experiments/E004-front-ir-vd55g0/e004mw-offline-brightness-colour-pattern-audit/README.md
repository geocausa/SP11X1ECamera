# E004mw: SP11-only existing image scalar audit and camera-free brightness policy

E004mv's fresh real front/rear baseline/gain optical private originals
can be read ONLY on SP11. The audit fails closed unless the photo
container has its known exact 1080p/4K dimensions and owner geoca
dir0700/file0600. It returns just scalar channel means, gross
gray quantiles, saturation fractions and a ONE-number green-pixel
parity spread. No images, pixels, tiles, photos, thumbnails or photo
hashes go into stdout/Git/chat/other hosts; no output image saved.
It never opens a camera, native V4L2 controls, IR, firmware, network
or a Linux system sleep state.

The camera-free preview_brightness_policy.py separately sketches a
one-time choice between ONLY the physically verified baseline and
bounded native gain profile for each visible-light RGB sensor. It
does not write any controls or approve a live change. Sequence/FPS,
exact sensor readback, route ownership, IR-off, sensor timing, studio
range, clipping, and thirty consecutive real-source-frame scalar
admission are required in any future independent guarded physical
candidate. It never declares a covered lens to be scene detail,
never steps beyond prior verified native tuple, never turns on
hardware ISP or front IR, and does not self-calibrate black/white
balance. A front scene that remains dark at known gain requires more
evidence rather than repeated brightness gain.

The true colour chart/neutral surface, dark optical reference and
fixed lit object/detail test are still UNVERIFIED; aggregate RGB means
or 2x2 pixel parity alone cannot identify sensor-row offset, correct
white balance or image detail. No routine default camera change.
