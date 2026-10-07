# Standard libcamera front pipeline qualification

Fresh pipeline02 uses the physically verified audit24 kernel, data-only firmware
and the corrected build03 real pipeline compiled into pinned libcameraff740913. The standard cam app
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

Pipeline01 is consumed and retired: it delivered79 application frames before
the final output waited for a further queued buffer. Zero kernel faults occurred;
Golden was restored. Pipeline02 reuses only fully paired and retired internal
startup buffers as spare outputs when queued depth falls below two. This lets
finite application captures drain the last request without exposing spare frames.
The corrected build passes Werror and8 selected tests with2 VIMC skips; pipeline02 hardware qualification passed80 app frames at30.0056fps,425
owner checks across85 retirements and clean stop/release. Both identities retired. Timeout output is retained privately on SP11.
