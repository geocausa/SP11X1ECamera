# E002 — proposed threaded upstream email replies (NOT SENT)

These are ready-to-copy responses, reflecting on-device results collected
2026-11-21 on a **separate X1E80100/OLED Surface Pro 11**. None of these
drafts claims an optical autofocus test, real deep sleep, or a reviewed
upstream implementation. Do **not** add a broad `Tested-by` tag to
someone else's exact patch revision without testing that revision.

## 1. Reply to Haipeng's message in George's OV13858 DT v2 thread

**To:** Haipeng Lin <jimmie.lin@gmail.com>
**Cc:** Sakari Ailus <sakari.ailus@linux.intel.com>; linux-media@vger.kernel.org
**Subject:** Re: [PATCH v2 2/2] media: i2c: ov13858: Add device tree support

Hi Haipeng, Sakari,

Thank you for the X1P/LCD testing and, especially, for identifying the
DW9800K dependency on OV13858 DOVDD (PM8010 L6M). I have now tested a
solution on my separate Surface Pro 11 OLED (X1E80100).

The actuator has its own 2.9 V VDD on L16B but needs the shared 1.8 V
L6M rail for its I/O interface. I modified dw9719 to acquire an optional
`vddio-supply`, enabling it before VDD and disabling it after VDD; the
OV13858 retains its independent `dovdd-supply` consumer. In the board
DTS the OV13858 also references the DW9800K via `lens-focus`.

On the real hardware the sensor probes at CCI0/master1 0x10, the lens
probes at 0x0c and exposes `focus_absolute`. Repeated focus writes
128/512/896/256/0 succeeded with readback. RAW capture works at
4224x3136 around 30 fps; OV13858 v4l2-compliance passed 46/46.

Most importantly, with the desktop camera monitor temporarily closed,
the L6M enable count was 0 with both devices idle, 1 with the sensor
streaming alone, 2 with the sensor and lens both open, 1 after the lens
closed while streaming continued, and 0 after the stream stopped.
L16B followed the actuator independently and returned to 0 when closed.
This removes the need for an always-on L6M vote. Four Linux
`pm_test=devices` callback cycles followed by focus writes and camera
captures also passed.

These are tests of my downstream-derived X1E/OLED integration, not a
new `Tested-by` for an exact standalone upstream commit. The precise
Denali L6M regulator input parent is still unverified, and optical
sharpness and full deep-standby remain untested. The camera monitor
currently holds the VCM node open while active, so its runtime-PM vote
also needs userspace attention.

I have split the optional-vddio binding and driver changes into an RFC.
Since Griffin's 19 November DW9800K v4 series introduces a separate
`dongwoon,dw9800k.yaml`, I am coordinating the final binding location
rather than posting an incompatible pair.

Detailed data and source:
https://github.com/geocausa/SP11X1ECamera/tree/wip/ov13858-dw9800k-l6m-vddio-untested-20261121/experiments/E002-sp11-ov13858-autofocus-rfc

Thanks,
George

## 2. Reply to Haipeng and Sergey in the OV13858 regulator/clock v4 thread

**To:** Sergey Lebedev <lsa.uz@pm.me>
**Cc:** Haipeng Lin <jimmie.lin@gmail.com>; Sakari Ailus <sakari.ailus@linux.intel.com>; linux-media@vger.kernel.org
**Subject:** Re: [PATCH v4] media: i2c: ov13858: add regulator, clock and reset GPIO handling

Hi Sergey, Haipeng, Sakari,

Thank you for the power-sequencing work and LCD test results. I have
independently tested the rear OV13858 camera on the X1E80100
Surface Pro 11 OLED with an isolated downstream-derived Linux kernel
and native CCI/CAMSS.

The sensor identifies on CCI0/master1 (0x10), with four-lane CSIPHY1,
19.2 MHz MCLK, reset GPIO110 and supplies DOVDD=L6M 1.8 V,
DVDD=L1M 1.2 V and AVDD=L5M 2.8 V. It captured three RAW10
4224x3136 frames through libcamera at roughly 30 fps and passed
46/46 V4L2 subdevice compliance tests. We also captured and inspected
three identical on-chip RAW colour-bar frames in a dark room.

The sensor's L6M and AVDD regulator consumer counts return to 0
when streaming ends. When the separate DW9800K actuator acquires L6M
through optional `vddio-supply`, L6M correctly stays on as long as
either sensor or actuator is using it and goes off when both close.
The 0/1/2/1/0 L6M transitions were observed on the physical machine.

I also ran four `pm_test=devices` suspend/resume callback cycles,
each followed by a successful focus-control write and 30-frame
capture. These are not real deep-platform standby cycles, and I have
not attempted full suspend while streaming.

This verifies my X1E/OLED integration, not precisely the unmodified
v4 series on the Intel IPU platform; I therefore offer it as separate
hardware evidence rather than a formal `Tested-by` for v4.
The provisional L6M input parent in our test DTS is not independently
schematic-confirmed.

Evidence:
https://github.com/geocausa/SP11X1ECamera/blob/wip/ov13858-dw9800k-l6m-vddio-untested-20261121/experiments/E002-sp11-ov13858-autofocus-rfc/EVIDENCE-SHARED-RAIL-PM-20261121.md

Thanks,
George

## 3. Reply to Griffin's pending DW9800K v4 discussion

**To:** Griffin Kroah-Hartman <griffin.kroah@fairphone.com>
**Cc:** Sakari Ailus <sakari.ailus@linux.intel.com>; André Apitzsch <git@apitzsch.eu>; linux-media@vger.kernel.org; devicetree@vger.kernel.org
**Subject:** Re: [PATCH v4 0/3] Dongwoon DW9800K update patchset

Hi Griffin, Sakari and all,

I have independent hardware data on the DW9800K in the Surface Pro 11
OLED (X1E80100) that may be useful for this series.

The DW9800K's VDD is L16B 2.9 V, but its I/O needs PM8010 L6M
1.8 V, which is shared with the rear OV13858's DOVDD. Without an
independent regulator vote from the lens, probe depends on the camera
sensor powering L6M or on keeping that rail permanently enabled.

I added optional `vddio-supply` handling to dw9719: enable before VDD,
disable after VDD, and release on power-up failure. With my
pre-v4 experimental camera stack, I measured L6M enable-count transitions
0/1/2/1/0 as lens/sensor consumers open and close. L16B turns off
independently when the actuator closes, without interrupting sensor
streaming. RAW sensor capture, lens focus-control transactions and
four device-PM callback tests also succeeded.

I downloaded the posted v4 driver patch and applied it **together with
my optional-vddio driver change** in a separate module build. On the
real SP11, that combined module bound the DW9800K, accepted lens
positions 128/512/896/0 with matching readback, and auto-suspended
with L6M and L16B enable counts back at 0. I then restored my
original tested module.

The v4 binding moves this compatible into `dongwoon,dw9800k.yaml`;
I also tested adding optional `vddio-supply` there. The binding
schema examples and the SP11 test DTB validated successfully.
I have a two-patch compatibility preview against a **synthetic v4
base** but am not sending that as a patch against merged mainline
while the v4 DTS compatibility review is unresolved.

Would you prefer the optional I/O property be sent separately once
the DW9800K binding is settled, or folded into a future revision of
the v4 binding? I can rebase the two signed-off binding/driver patches
to the final agreed layout.

This test verifies driver communication and regulator counts, not
optical lens movement, real deep standby or unmodified v4 alone.

Evidence and patch previews:
https://github.com/geocausa/SP11X1ECamera/tree/wip/ov13858-dw9800k-l6m-vddio-untested-20261121/patches/ov13858-dw9800k-l6m-vddio/mail-ready

Thanks,
George
