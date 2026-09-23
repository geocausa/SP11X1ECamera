# E004mp — bounded extra rear analogue gain, source/noise diagnostic

PHYSICAL PASS / VISUAL QUALITY NOT ACCEPTED / CONSUMED AND FULLY RETIRED. Completely new one-shot ID, NEVER reuse consumed
E004mh/E004wn/E004mg. Preserve protected Golden, IR OFF and never test
Linux OS system suspend/resume/standby/hibernate. New isolated RGB
studio-range publisher front1080 and rear4K, ordinary UID1000 app frame,
real RAW10 four-channel full-precision statistics and paired same-source
RAW-upper8/NV12 scalar checks as proven E004mh. Only trial variation:
rear analogue_gain=512 instead of256; rear exposure=3200 (verified <=
prior driver-advertised max3206) and digital_gain=2048 unchanged versus
E004mh; front target completely unchanged. Baseline rear exposure1600,
analogue_gain128,digital_gain1024 and front corresponding fixed native
baseline verified first. Validate currently advertised exact controls,
read back every write and exact baseline restoration. Do not touch
VBLANK/frame-timing/FPS, test-pattern, IR, illumination or sensor I2C.
A dark corner may have weak but nonzero scene detail; this diagnostic
measures whether more native analogue gain increases useful RAW10
contrast versus predominantly amplified black offset/noise. No
assumption that Windows auto-exposure 5000 nominal ticks maps to native
sensor registers. Windows E004wn bright rear was 18+ minutes after
E004mh and scene illumination/camera orientation was NOT verified.

Four local-only sealed RGB front/rear baseline/gain photos after bounded
control trial; any images remain on SP11, NEVER in Git/chat or network.
Images on root-private candidate stage 0700/0600 copied to user-private
`~/Pictures/SP11-Camera-Private-E004mp` 0700/0600 only after Golden
return, then temporary boot/service/root assets retired. If any
safety/provenance/restore check fails, stop and automatic Golden reboot;
never reuse attempted one-shot token. Images alone and global Y do not
prove recognizable detail, signal-to-noise or OEM image-quality parity.

## Actual physical E004mp diagnostic — 2026-09-23

The source-defined fresh one-shot physically ran at ~11:32–11:34 BST,
then automatically returned to protected Golden boot
`b3692bba-238a-4885-8f3b-9332c8284b51`. Native front/rear RGB
app frame, exact source RAW10 full10 per-Bayer channel profiler,
paired same-source RAW-upper8/NV12 scalar checks, target gain control
readback, baseline restoration, STREAMOFF/native neutral proof, IR OFF,
no Linux OS sleep and Golden overlap guard all passed. The unique
candidate `4e25a7cf-69c2-48c3-9198-ca0438e921b5` was CONSUMED;
service, GRUB, root stage and all boot assets RETIRED. NEVER rearm.

The rear analogue target was 512 with exposure3200 and digital gain2048
(the ONLY native control trial target difference from E004mh was rear
analogue256→512). At E004mp baseline the rear G0 RAW10 p01/p99 was
64/70; at trial it was 73/140 (p99–p01 6→67). G1 p01/p99 was
64/69→69/126. This is a strong *measured RAW distribution response*;
p01 also shifted under gain, so code64 must NOT be treated as a
calibrated gain-invariant optical black. The matched same-boot rear
software RGB PNG downsampled Y p99 was 15→30 and 12x16 tile-mean
std0.464→3.512. Independent UID1000 app NV12 Y p99 rose 31→48.
The front control profile was not changed from E004mh, and its
baseline/gain PNG Y p99 was 25→60 in the E004mp scene.

A separate local-only 12x16 tile correlation test compared both phases
and both experiments: E004mp rear baseline/gain correlation 0.80611;
E004mh-vs-E004mp rear gain correlation 0.97697. These support a
repeatable spatial pattern, but can include fixed sensor-pattern noise;
no recognizable scene, calibrated optical black, true SNR or OEM
Windows-quality parity is proven. Windows E004wn auto-exposed rear mean
Y148 was ~20min earlier with uncontrolled camera direction/lighting,
and NV12 mean must not be compared as an identical statistic to Linux
RGB PNG p99. Rear image remains dark in E004mp. Four ORIGINAL private
front/rear baseline/gain PNGs remain ONLY on SP11 at
`~/Pictures/SP11-Camera-Private-E004mp/` (folder0700/photos0600).
No original photos, thumbnails or hashes exported or committed.

At the current rear 4K 30fps timing, the advertised exposure max was
3206 lines and trial used3200; a longer sensor exposure needs a
separately reviewed VBLANK/frame-rate contract and must not be added
implicitly. Prioritize fixed visible-target optical/source testing
plus explicit analogue-gain vs dark-noise checks before enabling
aggressive auto-exposure/tone curves. Keep normal Golden RGB disabled,
IR OFF and Linux system sleep untested.
