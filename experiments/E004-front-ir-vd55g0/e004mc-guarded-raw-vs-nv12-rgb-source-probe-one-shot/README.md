# E004mc — guarded real RAW10 high-byte versus converted NV12 luma

Fresh distinct root-private one-shot identity, source-only until
all source SHA, clean boot, package/graph/ownership/IR and watchdog
preflights PASS. E004ma/b are CONSUMED and their physical identities
must NEVER be reused.

E004mb morning-light probe found app NV12 front p99Y18, rear p99Y16.
This test must determine whether paired TRUE PHYSICAL source RAW10
high 8-bit photosite values are also near black, or whether the
accepted RAW10->NV12 software conversion/pixel transport loses a
bright source. Front/rear candidate-only instrumentation samples
four Bayer photosites for each sparsely selected output Y location
on the SAME mmap source frame BEFORE QBUF; after unchanged software
conversion it samples the paired in-memory destination Y frame.
Reports ONLY aggregate mean, p95/p99 and >32 fractions for RAW8
and NV12 Y; no pixels/hashes/photos/tile grids are ever saved.
No uncalibrated inference of recognizable image from frame count.

Retain maintained RGBSession physical backend, exclusive opt-in
root Unix selector front→rear→off→quit, three normal independent
uid1000 120-frame app opens plus client SIGKILL/recovery each,
and separate scalar in-memory 90-frame uid1000 scene probe. Capture
sensor V4L2 exposure and gains READ-ONLY; DO NOT change exposure,
gain, frame length or IR controls in this experiment.

A result of source RAW8 p99 near-black and NV12 Y near-black still
cannot alone distinguish corner darkness from sensor programming,
optical lens blockage, CSI source format or sensor control rejection.
Source bright with converted Y near-black would isolate the
conversion/packing route for investigation. No full Windows ISP
or calibrated image-quality claim.

Candidate remains non-default, one-shot and root-private with
automatic preserved Golden return, full native 119-edge graph
neutral checks, IR streaming/illumination OFF and NO Linux OS-level
standby/suspend/resume/hibernate. Every physical attempt irrevocably
consumes E004mc.

Source-only verification includes candidate-local cloned front/rear
publishers with unchanged RAW10→NV12 conversion body, a shared
paired aggregate histogram header, their inherited 9-scenario
fake-device/STREAMOFF tests, a synthetic paired-bright-source/dark-Y
unit test and strict text-only 4-frame-per-camera validator. Source
sample points 1, 30, 90, 180 are measured before V4L2 source QBUF;
the former accepted full graph/owner and output pixel contracts
remain untouched. Both publisher binaries MUST be newly built with
E004mc's unique candidate boot token and SHA-pinned before arming.

## Final E004mc physical result — PASS diagnosis / CONSUMED / RETIRED

A fresh isolated single-use candidate boot
781fe4ab-0cc6-4cf9-a427-5fade20622ca obtained four physically
paired same-mmap-source-frame sparse RAW10 upper-eight-bit samples
and corresponding NV12 Y samples for each camera. The front RAW8
p99 was 19 while NV12 Y p99 was 18; rear RAW8 p99 and NV12 Y p99
were BOTH 16. Incoming upper8 RAW photosite measurements were
already dark: the RAW-to-NV12 software converter **did not turn an
otherwise bright captured source into a black output**. Ordinary
independent uid1000 front1080p/rear4K 90-frame scene probes again
reported essentially no spatial image contrast. Each camera
completed the earlier first/reopen/app-crash recovery lifecycle.

Both publisher processes stopped through validated STREAMOFF 143;
native complete119-edge media graph returned neutral. No unvalidated
sensor exposure/gain write, IR use, photo export or OS-level Linux
system sleep. Protected Golden boot
51309717-8e55-4ced-b347-58988305ca15 was independently verified
with unchanged saved boot entry and zero camera nodes/modules/
processes. Candidate root-private boot/services/assets RETIRED,
physical identity CONSUMED: never reuse. See RESULT.json,
CONSUMED.json and evidence/.

**Remaining uncertainty:** RAW10 high eight bits alone cannot
resolve ambient/occluded scene, actual sensor gain/integration,
sensor RAW packing or hardware upstream source processing. The
next candidate must use a fresh identity for bounded supported
V4L2 sensor control-response validation and paired RAW/Y statistics,
rather than presenting a black but correctly sized V4L2 frame as
a useful Linux webcam image.
