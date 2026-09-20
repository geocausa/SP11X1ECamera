# E004jh — real rear optical camera to standard V4L2 virtual webcam

## Actual E004jh result — real optical rear webcam PASS, candidate retired

The unique camera-capable boot
`053bfcc0-c416-4c2a-8c08-d8a61d07d36d` passed the exact source,
R4-complete camera package, separately hash-verified V4L2 loopback,
previously live-tested CAMSS mapped-DMA guard, stock GRUB writer and
hardware-free launcher/real-publisher preflights. The actual
OV13858 sensor first produced its accepted hardware colourbar and
then **27 complete normal-scene optical Bayer10 frames, hardware
sequences 0..26 at 29.9502 fps**. The source-pinned C converter
published 27 uncalibrated 1920×1080 NV12 frames into the now
**system-discoverable standard** `/dev/video90` webcam device
(`SP11-Rear-Preview`) via GStreamer `v4l2sink`, with mean
conversion-only time of **3.5107 ms per frame**.

A **separate standard V4L2 reader**, not a direct pipe from the
hardware producer, opened /dev/video90 and obtained eight successive
complete 3,110,400-byte NV12 buffers with virtual sequences **7..14**.
Its output fed a real GStreamer
`appsrc → videoconvert → I420 appsink` application consumer, which
reported **eight valid application frames**. The combined bounded
publisher/capture/reader interval was **1,247 ms**, including process
startup, stream acquisition, teardown and IPC; it does NOT measure
individual sensor-to-screen latency or prove sustained multi-minute
30fps app throughput. No normal-scene optical Bayer or NV12
intermediate file was created, and **pixel contents of the eight
virtual buffers were not saved**; consecutive buffer sequences
must not be misrepresented as independently hashed colour frames.

The virtual loopback module and /dev/video90 were unloaded before
the rear route was neutralized and the front was activated.
In the **same boot**, IMX681 again captured **27 distinct compressed
QC10C buffers (7,778,304 bytes each)** with the E004ip mapped-DMA
coverage guard, shadow policy and zero later native sensor writes.
All three sensors suspended, the final graph was neutral and no
kernel Oops/panic/IR-emitter marker occurred. Automatic return to
protected Golden boot
`e59ae47f-0081-44ca-9d86-6de7a7ee3ff6` succeeded, with
`saved_entry=sp11-audio-fullio-v19c`, an empty `next_entry`, no
video/camera/loopback modules or nodes and unchanged default
kernel/DTB/initrd. The consumed identity was proven unable to rearm;
root-private front QC10C pixels, rear colourbar, package and
standalone loopback module, isolated boot entry and test unit
were retired/deleted after recording non-image evidence in
`RESULT.json`.

**Scope of this milestone:** the rear hardware actually produces
video that a standard V4L2 application can select and consume in
a temporary, camera-capable Linux candidate boot. It is NOT yet a
persistently installed user-service camera; the colour transform is
a fast **uncalibrated GRBG tile proxy**, not a full demosaic,
auto-exposure, auto-white-balance or calibrated ISP implementation.
Likewise the validated **front** remains QC10C compressed data, not
true app-displayable NV12; a correct QC10C decoder or safe proven
linear ISP mode plus its own separate selectable webcam endpoint
are still required for front/rear Windows parity. Protected IR
illumination/Hello admission remains explicitly disabled.

2026-09-20. Parent `fb37574`. This is a **NEW unique, single-use
camera-capable Linux candidate**. E004jf separately proved real
OV13858 Bayer10→NV12→GStreamer appsrc with eight optical frames and
front IMX681 QC10C27 handoff. E004jg separately proved a Golden-v4-ABI
`v4l2loopback` synthetic 1920×1080 NV12 `/dev/video90` endpoint
visible to an independent standard V4L2 capture client. Neither
separate success proves a **real rear optical→virtual webcam**; only
this combined bounded physical run can.

## Source-locked, safe candidate

The unchanged protected Golden v4 kernel and initrd are copied into a
unique `next_entry` alongside the previously live-proven unified
three-sensor camera-capable candidate DTB. Golden's persistent saved
entry remains `sp11-audio-fullio-v19c`; neither its boot assets
nor default camera modules are replaced. The accepted hardware
manifest remains SHA-256
`ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c`,
the live-tested front mapped-DMA-guard CAMSS module SHA-256
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`,
the E004je streaming C helper
`a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15`,
and the original GStreamer app consumer
`9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613`.

The maintained source was rebuilt from the latest committed HEAD. Its
strictly verified **51-file R4-complete** package manifest SHA-256 is
`9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455`.
It differs from the first E004jd build manifest
`3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71`
because that earlier package was staged before later front README
changes were committed; **the separately verified accepted kernel
modules, camera DTB, derived R4 bootstrap and hardware manifest are
unchanged**. The candidate requires the exact *current* manifest
digest and its strict full-file SHA verification before activation.

The independently rebuilt GPL `v4l2loopback` 0.15.3 module is
SHA-256
`2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1`,
the same Golden-v4 ABI module that **already passed the real isolated
E004jg standard V4L2 eight-frame synthetic-reader test**. The module
is staged privately, not copied into `/lib/modules` or enabled on
Golden. Exact R4, front CAMSS, rear bridge, app receiver, and
virtual-device module hashes plus two earlier hardware-free launcher
and GStreamer publisher preflights are verified before enabling a
physical sensor. Both Ubuntu stock GRUB writers must complete in
the known-good E004iy order with successful timestamped execution.
Only a neutral or previously observed idle-rear graph is admitted.

## Bounded physical producer-to-standard-device test

The accepted rear hardware colourbar is verified and its test pattern
turned **off** before normal optical streaming. The candidate loads
its separately verified virtual device, requiring
`/dev/video90` label `SP11-Rear-Preview` to be discoverable. Under
independent timeouts, an actual rear `pgAA` V4L2 producer streams
**27** full real optical Bayer10 frames into the already accepted
3.1 MB NV12 frame converter, and a GStreamer `fdsrc →
rawvideoparse → v4l2sink` pipeline publishes these **real**
1920×1080 NV12 previews to the standard virtual camera.
A separate standard `v4l2-ctl -d /dev/video90` V4L2 reader
must receive **eight** complete NV12 frames and pipe them to the
previously validated GStreamer application consumer.
The candidate checks source hardware sequences 0..26, 28.5–31.5
fps source timestamps, full Bayer10 and NV12 frame lengths,
eight distinct virtual-buffer sequences, all 27 successful converter
frames and eight GStreamer application frames.

No normal optical Bayer or intermediate NV12 frame file is created.
Only temporary root-private text logs and the accepted rear colourbar
are written; the colourbar and all subsequently captured front QC10C
pixels are destroyed during post-Golden retirement. The existing
producer is only an **uncalibrated colour proxy**: proper demosaic,
black-level/white balance, continuous webcam uptime, physical
camera-to-screen latency and Windows-quality parity remain separate.

After the rear virtual camera passes, the candidate **unloads the
loopback driver and verifies video90 disappeared before activating
the front**. It then repeats E004jc's accepted 27-frame IMX681
compressed QC10C capture with the real mapped-SG DMA coverage guard,
post-G3 `shadow` policy and zero later native sensor writes.
The rear/front media handoff must be neutral, and all three sensors
must suspend after streaming. IR illumination and protected IR
sensor streaming are prohibited. A unique 360-second bounded systemd
unit unconditionally returns to protected Golden after success,
failure or timeout. The consumed one-shot identity must never
be reused.

Six candidate source/identity tests and nine inherited rear converter
and app-consumer tests passed **offline** on protected Golden. They
do NOT substitute for a real candidate-boot verdict. A successful
bounded real result will establish a temporary **app-discoverable
live rear webcam source**; it does not install a persistent desktop
service or solve front QC10C decompression and selectable front
webcam creation.
