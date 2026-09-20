# E004jg — isolated virtual rear webcam endpoint (synthetic-only test)

2026-09-20. Parent `a5acabb`. The E004jf physical boot already proved that eight real
rear OV13858 Bayer frames can travel directly from V4L2 through the
uncalibrated Bayer-to-NV12 converter into a real GStreamer application
consumer, followed by the separately proven 27-frame compressed front QC10C
regression. E004jg isolates the *next* gate: can the SP11's **Golden v4 ABI**
provide a standard discoverable V4L2 webcam interface for a future rear
publisher? This test NEVER activates a physical camera.

A copy of Ubuntu 26.04's packaged `v4l2loopback-source` 0.15.3-1ubuntu2 was
downloaded to a disposable private /tmp tree (source .deb SHA-256
`007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0`)
and compiled out-of-tree with the exact accepted custom kernel build tree.
The resulting GPL module SHA-256 is
`2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1`,
vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions
aarch64`. No source package is installed into Golden or committed into this
repository, and no production camera kernel/DTB/initrd is replaced.

E004jg stages a **unique one-shot** boot that copies the **protected Golden
kernel/initrd AND protected Golden DTB**, not the camera-enabled candidate DTB.
The systemd service activates only under the exact one-shot kernel marker
and only after both ordered stock GRUB environment writers succeed. The
persistent saved entry remains `sp11-audio-fullio-v19c`. It checks the
source, binary, SHA and unchanged Git identity before consuming its unique
boot. It refuses active camera nodes and prevents any sensor CAMSS or IR
driver from loading.

The candidate loads the standalone virtual video driver exclusively into
its own boot with `devices=1 video_nr=90 card_label=SP11-Rear-Preview`.
A bounded GStreamer **synthetic ball test pattern**, never optical frames,
publishes NV12 1920×1080 at a nominal 30fps to `/dev/video90` via
`v4l2sink`. A separate **standard V4L2 capture reader** opens
`/dev/video90`, retrieves eight complete NV12 frames through
`v4l2-ctl --stream-to=-`, and pipes them to the previously tested
GStreamer appsrc→videoconvert→appsink application consumer. The service
checks device discovery, exact NV12 format, eight reader/application frames
and EOS; no synthetic raw pixels are written to disk. It closes the
publisher, removes `v4l2loopback`, verifies the virtual video node is gone,
and returns automatically to Golden on success, failure or timeout.

**Scope:** success would prove that a standard, app-discoverable *synthetic*
virtual V4L2 camera is possible with this kernel, NOT a working persistent
rear camera. A later separate boot must connect the **physically proven rear
V4L2→NV12 converter** to this virtual device while checking cadence,
camera resource ownership, illumination-off guarantees and clean shutdown.
The rear conversion currently remains an uncalibrated tile colour proxy.
The front remains compressed QC10C without a demonstrated correct decoder
or genuinely linear ISP output; IR illumination and secure Windows Hello
remain excluded.

Run before arming:

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jg-virtual-rear-device-offline-one-shot \
  -p test_virtual_rear.py -v
```

Only the actual one-shot result can establish that the virtual module loads,
that generic applications can read the synthetic device, and that its
automatic removal and Golden return succeed. The unique one-shot identity
must never be rearmed after any real attempt.
