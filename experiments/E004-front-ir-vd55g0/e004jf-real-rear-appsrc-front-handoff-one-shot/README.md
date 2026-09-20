# E004jf — actual rear V4L2 → NV12 → GStreamer appsrc, then front QC10C

2026-09-20. Parent `280de0a`. A NEW unique source-locked, one-shot
camera-capable Linux candidate after E004jc's successful bounded 8-rear
then 27-front **hardware capture and mapped-DMA guard** and E004je's
offline rear Bayer10→NV12→GStreamer application consumer.

## New physical question

The old rear converter consumed private *files* after the camera had
already stopped. E004je proved that the exact same uncalibrated GRBG10
colour proxy instead accepts a bounded anonymous STDIN pipe and feeds
a real in-process GStreamer `appsrc → videoconvert → appsink`
consumer using NV12 1920×1080 buffers, without intermediate optical
or NV12 files. The archived input was a REPEATED hardware colourbar,
NOT a real camera producer. E004jf checks this pipe with eight **new
real rear optical frames from the physical OV13858 node**, then
performs the already accepted front QC10C handoff on the same boot.

The rear producer uses the accepted `pgAA` 4076×2806 format and
media path `msm_csiphy1 → msm_csid0 → msm_vfe0_rdi0`. After its
one-frame exact hardware colourbar, the sensor's test pattern is
disabled. Only then, under a 40-second fail-closed timeout, the
candidate runs:

```text
v4l2-ctl --stream-mmap=4 --stream-count=8 --stream-to=-
      | rear-bayer-stdin-to-nv12 --frames 8
      | python3 nv12-appsrc-consumer.py --frames 8
```

The shell uses `pipefail`. **All three processes must succeed**;
the converter requires eight full Bayer frames and exact EOF; the
GStreamer application must receive eight valid timestamped I420
samples and EOS, derived from eight 3,110,400-byte NV12 buffers.
The command stores only short *textual status logs*, not any of
the eight normal optical frames or intermediate NV12 frames.
It then requires suspended sensors and a neutral graph before
the original 27-frame front QC10C/shadow-policy regression.
The separate front QC10C raw files remain root-private and are
deleted at retirement; do not mislabel them as linear NV12.

## Boot, package, and bounded failure handling

The candidate uses an unmodified protected Golden v4 kernel and
initrd plus ONLY the previously proven unified candidate camera
DTB and E004ip mapped-DMA-guard CAMSS module. The full package
is the **51-file R4-complete E004jd production stage**, manifest
SHA-256
`3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71`.
The accepted front bootstrap is already included in the manifest
and must NOT be appended again; the candidate front module remains
the live-tested E004jc module SHA
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`.
The package is locally staged only and does not replace Golden's
camera modules or persistent kernel/DTB/initrd.

The E004je standalone converter executable and GStreamer Python
consumer are separately source-locked and copied into a
root-private candidate `/var/lib/sp11-camera-e004jf/bridge/`
tree, respectively mode 0700 and 0600. The candidate binary
SHA-256 is
`a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15`;
the accepted consumer SHA-256 is
`9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613`.
Before **arming**, the installer tests these **actual root-copied**
files against the accepted archived colourbar via GStreamer,
then validates the packaged front launcher in a hardware-free
offline plan. The root runner checks both binaries, both text
preflights, exact module/package hashes and both ordered stock
GRUB writer services before loading any camera module.

A separate unique GRUB `next_entry`, exact service commandline
condition, 360-second outer timeout and unconditional
`ExecStopPost` Golden reboot prevent the experiment becoming a
default or a same-boot retry. Only a verified idle `neutral`
or previous known idle `rear-only` graph may be normalized.
Any unexpected route, failed stream, malformed GRUB environment,
missing provenance or sensor/IR/kernel health check aborts
the one-shot. No IR stream, IR emitter, protected SecurePD,
Windows Hello, changed native post-G3 sensor writes,
PMIC illumination write or unverified linear front NV12 is
authorized.

## What a success would and would not mean

A successful **real** run would prove the rear V4L2 *producer* can
pass eight actual optical frames directly through this uncalibrated
Bayer-to-NV12 proxy into a real GStreamer application's appsink,
and still hand off to the front 27-frame compressed QC10C
V4L2 capture on the same boot. It would **not** establish a
durable desktop system camera device: SP11's Golden kernel has no
`v4l2loopback` module, no PipeWire camera service was installed,
and the GStreamer appsrc pipeline is a private in-process
application. Genuine live capture-to-display latency and full
30fps continuous thermal/colour parity remain unproven.
The front still needs a correct QC10C decoder or validated true
linear NV12 ISP route to supply ordinary Linux applications.

Run the eight candidate offline/static tests before any boot:

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jf-real-rear-appsrc-front-handoff-one-shot \
  -p test_live_rear_appsrc_one_shot.py -v
```
