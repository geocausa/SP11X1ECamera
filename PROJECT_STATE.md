# SP11X1ECamera — current project state

**Updated:** 2026-11-21 21:40 UTC
**Active state:** E002 — rear OV13858 / DW9800K shared regulator hardware test
**Current active boot:** experimental `7.3.0-sp11-camera-rfc1+` on OLED/X1E80100
**Protected known-good:** accepted `7.3.0-sp11-unified13` and Golden v19c
**Branch:** `wip/ov13858-dw9800k-l6m-vddio-untested-20261121`
**Scope:** own camera repository only; no Oaklee repository changes

## Results confirmed on the physical SP11

- Kernel and 8,711 modules compiled; experimental kernel booted using
  one-shot GRUB. Golden and unified13 boot file hashes preserved.
- OV13858 rear camera on CCI0/master1 `0x10`, CSIPHY1 four D-PHY lanes,
  OV13858 V4L2 compliance **46/46**.
- DW9800K actuator `0x0c` driven by `dw9719`, standard
  `lens-focus` fwnode link; focus control updates succeed.
  Actuator V4L2 compliance **45/46**, known missing control-event
  subscription support (separate from supply fix).
- RAW capture: three full-res **4224×3136** ~30 fps frames via
  libcamera, four 1056×784 frames, and three verified identical
  1056×784 OV13858 on-chip synthetic colour-bar frames.
- Shared PM8010 L6M 1.8 V consumer reference counts:
  **0 idle, 1 sensor-only, 2 sensor+actuator, 1 sensor-only, 0 idle**.
  Actuator L16B 2.912 V automatically switches off when actuator closes,
  without killing sensor streaming.
- Four `pm_test=devices` cycles succeeded, each followed by focus
  updates and 30-frame capture, no suspend failures (total kernel
  successful fake suspend counter 6, including two earlier).
- Griffin Kroah-Hartman's unmerged DW9800K v4 driver patch **plus**
  optional-vddio built as isolated module and **hardware-tested**
  with probe, 4 focus positions, autosuspend, L6M/L16B 0 idle.
  Original module explicitly restored.
- New v4 separate `dongwoon,dw9800k.yaml` modified with optional
  `vddio-supply` and schema-checked successfully.

Detailed evidence:
[shared regulator + PM](experiments/E002-sp11-ov13858-autofocus-rfc/EVIDENCE-SHARED-RAIL-PM-20261121.md);
[dark room RAW capture](experiments/E002-sp11-ov13858-autofocus-rfc/EVIDENCE-LOW-LIGHT-CAPTURE-20261121.md).

## Not established

- No independent schematic proof of L6M input parent:
  `vreg_s4c_1p8` is a provisional DTS implementation.
  No camera-enabled Denali board DTS is upstream-ready.
- No proof of actual optical lens motion/sharpness due to unlit scene.
- No **real full deep standby** or standby battery-power result:
  PM8xxx RTC wakealarm unavailable. `pm_test=devices` is not deep sleep.
- WirePlumber holds the VCM subdevice open, and thus L6M/L16B enabled
  during desktop camera monitoring. Idle-off test requires closing
  the VCM camera monitor. Production userspace policy still needed.
- Current libcamera warns about OV13858 crop rectangles and uncalibrated
  IPA. One earlier manually forced camera clock-enable error -16
  does not invalidate successful subsequent capture, but must not
  be misrepresented as a warning-free integration.
- Front IMX681, IR VD55G0, and complete optical parity not covered
  by this rear-specific E002 validation.

## Patches, provenance, and mainline

- Mainline pre-v4 base pinned at
  `c44104f3642da720164042623e4832836aefdd8e`.
- Pre-v4 RFC 2-patch binding+driver signed-off series is in
  `patches/ov13858-dw9800k-l6m-vddio/mail-ready/pre-v4-rfc/`;
  strict checkpatch **0 errors / 0 warnings** on both.
- Pending Griffin Kroah-Hartman DW9800K v4 series
  `20261119-b4-dw9800k_cleanup-v4-0-df26c431595e@fairphone.com`
  proposes a separate `dongwoon,dw9800k.yaml`; maintainers
  raised DT backwards-compatibility concerns on 2026-11-21.
  A preview of our 2-patch adaptation for v4 is in
  `mail-ready/post-v4-preview/`, validated against a synthesized
  **unmerged** v4 base. Do **not** submit it unchanged as a
  patch based on a merged kernel commit.
- Independent X1P/LCD Haipeng Lin upstream correspondence on
  OV13858 v2 OF and Sergey's power v4 corroborates routing,
  sensor capture, and the need to power L6M for VCM CCI.

## Next action

Use the two threaded upstream reply drafts in E002 to explain the
**fully tested optional vddio solution** without claiming a real
deep-sleep or optics test. Ask Griffin/Sakari which DW9800K binding
layout will survive review, then rebase/send one `vddio` two-patch
series. Independently investigate L6M input parent from Windows
hardware evidence; address WirePlumber camera monitor idle-vote
policy separately. Keep Golden/unified13 default unchanged.

For original Windows oracle routing and power maps, see the E001
experiment and `docs/` rather than reinterpreting this test.
