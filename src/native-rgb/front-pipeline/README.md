# Standard libcamera front pipeline qualification

Fresh pipeline01 uses the physically verified audit24 kernel, data-only firmware
and a real pipeline compiled into pinned libcameraff740913. The standard cam app
must capture80 hardware2560x1440 NV12 frames. No custom capture probe, daemon,
userspace command packet, software pixel ISP or Windows executable is used.

The pipeline matches only the front typed-control/data-only driver graph. It
opens descriptors on acquire and closes them on release, configures the exact
sensor/CSIPHY2/CSID1/VFE1PIX route, supplies bounded typed defaults and owns four
startup buffers internally. App buffers then use normal libcamera/V4L2 DMA-BUF
export/import. Statistics use an internally owned standard metadata queue; every
app request requires matching stream, hardware sequence and pixel timestamp
before completion. Queues stop before buffers are freed; release restores the
neutral graph. The standard cam writes private NV12 files only on SP11.

This initial pipeline advertises no automatic or per-request image controls.
It uses the qualified fixed-manual exposure/IQ to prove actual application,
buffer and request/statistics integration. Full IPA/3A, dynamic semantic tables,
rear processed capture, public ABI/clock policy, reopen/soak/switch and Windows
optical quality remain required. Build success alone does not prove hardware.

The fresh candidate requires80 application frames,80 paired request markers,
four hidden startup frames, exact Y/UV extents, metadata timestamps, at least84
kernel retirements and matching consumed owners, semantic FIFO continuity,
explicit clean stop, neutral graph, sensor standby and protected Golden return.
The identity is one-use; consume and retire after any attempt, never rearm it.
