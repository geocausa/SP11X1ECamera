# E002: Surface Pro 11 OLED rear camera + DW9800K shared-supply hardware results

**Date:** 2026-11-21 UTC. **Test machine:** Surface Pro 11 (X1E80100/OLED).
**Status:** Successful hardware integration and device PM callback tests;
not a final upstream Denali DTS or optical quality validation.

## Test environment and provenance

- Experimental kernel: `7.3.0-sp11-camera-rfc1+`, built from known-good
  `sp11/unified13-driver-maintenance` source at
  `3094f120b90e7b2df9ccb326b1193d66bcc217a5`.
  Existing touch/audio/power support retained.
- Additional out-of-tree camera components were adapted from the
  `omacom/omarchy-pkgs` Linux patch stack: X1E80100 CAMSS/CCI,
  OV13858 and supporting fixes. Exact set and provenance in
  [E002 README](README.md).
- Optional VCM `vddio` regulator patch in
  [this repository](../../patches/ov13858-dw9800k-l6m-vddio/README.md).
- Boot image SHA256
  `ec6b68c94873a761d409955fc2c65c2d559396a9a27c94235253ff1d9a5f26af`.
  Experimental OLED `RFC2` DTB (with `lens-focus = <&rear_vcm>`)
  SHA256 `5e3055f6606c64e50c016c21979745fed1d3d4eb89fc1cd6514248f99546684e`.
- Experimental DTS uses CCI0 master1: OV13858 `0x10`, DW9800K
  `0x0c`, CSIPHY1 four D-PHY lanes, rear MCLK1 19.2 MHz, reset GPIO110.
- Golden FullIO v19c and accepted unified13 kernel/DTB/initrd were
  separately SHA256 checked before and after experimental boots;
  no protected core files were replaced. GRUB `next_entry` is empty.

## Hardware/driver evidence

1. **Boot and probe PASS:** experimental kernel booted with real
   `dongwoon,dw9800k` and `ovti,ov13858` I2C devices bound. CAMSS,
   CCI, sensor and VCM modules loaded. Sensor `/dev/v4l-subdev28`,
   VCM `/dev/v4l-subdev29`, `/dev/media0`, and 16 capture nodes.
   The RFC2 `lens-focus` DT property was needed for VCM subdevice
   registration; RFC1 had bound VCM but not created its V4L2 node.
2. **Focus control PASS (not optical confirmation):** repeated
   `focus_absolute` writes at 128,512,896,256,0 returned success and
   matching readback; no actuator/CCI timeout during the tests.
   After temporarily stopping WirePlumber, five separate open/close
   focus cycles completed, and VCM returned to runtime `suspended`
   after its 1000 ms autosuspend delay.
3. **RAW capture PASS:** four 1056x784 libcamera frames at about
   30 fps; three full-resolution 4224x3136 RAW frames of 16,558,080
   bytes each at about 30 fps. Full-resolution frames captured in
   darkness establish acquisition, **not optical sharpness**.
4. **Internal sensor pattern PASS:** after enabling the sensor's
   runtime power for the pattern-control write, three
   1056x784 packed RAW10 frames had the identical SHA256
   `a5dcc50c8c634a97dff95352b4363f8c8dec193129e9929c67de00f08ac09ee2`,
   with reproducible vertical brightness bands. Afterward
   `test_pattern=0` and sensor `power/control=auto` restored.
5. **V4L2 compliance:** OV13858 sensor subdevice **46/46** succeeded,
   zero warnings. DW9719 actuator subdevice **45/46** succeeded;
   remaining failure `VIDIOC_(UN)SUBSCRIBE_EVENT/DQEVENT` for a
   control event; the actuator has no such event handler. This is
   separate from the `vddio` regulator change.
6. **Independent supply vote transitions PASS, on live hardware:**

   | Operating state | L6M enable count | L16B enable count | L5M enable count |
   |---|---:|---:|---:|
   | Sensor + actuator idle, no device opens | 0 | 0 | 0 |
   | Sensor actively streaming, lens closed | 1 | 0 | 1 |
   | Sensor streaming, lens open | 2 | 1 | 1 |
   | Lens closed while sensor keeps streaming | 1 | 0 | 1 |
   | Stream stopped, both idle | 0 | 0 | 0 |

   L6M's two consumer labels are `1-0010-dovdd` and
   `1-000c-vddio`. The actuator uses `1-000c-vdd` on L16B.
   These counts prove **proper Linux regulator vote lifetime and
   shared-consumer reference counting**; they do not directly measure
   the analog rail voltage or sleep-current consumption.
   **Important user-space confounder:** WirePlumber opens the VCM
   subdevice for the desktop camera monitor, keeping L6M and L16B
   enabled while it holds that file handle. Disabling monitoring
   temporarily during testing allowed both supplies to auto-disable.
   A production policy fix for the camera monitor is a separate item.
7. **Device suspend/resume callback exercise PASS:** four
   `pm_test=devices` + `echo mem >/sys/power/state` cycles on the
   experimental kernel, all returned automatically. After every
   cycle a focus write and 30-frame capture succeeded, then both
   devices runtime-suspended and L6M returned to 0. Kernel suspend
   counters rose from 2 (pre-test) to 6 (post-test), `fail:0`.
   Linux `pm_test` intentionally stops short of full platform/CPU
   deep sleep; do **not** call these four real deep standby cycles.

## DW9800K v4 compatibility test

- Retrieved mailing-list series
  `[PATCH v4 0/3] Dongwoon DW9800K update patchset` posted
  2026-11-19 by Griffin Kroah-Hartman, at
  https://lore.kernel.org/all/20261119-b4-dw9800k_cleanup-v4-0-df26c431595e@fairphone.com/
- v4 replaces the old DW9800K binding arrangement with a separate
  `dongwoon,dw9800k.yaml` and corrects ID/register handling.
  Reviewers on Nov 21 raised backwards-compatible DT ABI concerns;
  **v4 is not presumed merged**.
- Applied v4 driver patch atop our `vddio` source in a disposable
  directory. External module build **PASS**, correct ARM64
  `vermagic=7.3.0-sp11-camera-rfc1+`.
  On the physical SP11, temporarily replaced only the in-memory
  VCM module (no installed module file changes), confirmed probe
  and binding, focus command/readback 128/512/896/0, actuator
  autosuspend, L6M and L16B returning to **0**.
  Original installed vddio module was explicitly reloaded afterward;
  WirePlumber restarted.
- Independently added optional `vddio-supply` to the v4 separate
  `dongwoon,dw9800k.yaml` in a disposable source tree;
  `dt_binding_check`, full schema generation and SP11 test-DTB
  validation **PASS**.
- Mainline-based pre-v4 RFC and unmerged-v4 compatibility preview
  have separate mailbox-ready patch series in
  `patches/ov13858-dw9800k-l6m-vddio/mail-ready/`.
  The latter is a *preview against a synthesized unmerged v4 base*,
  **not a mail-ready series against a final upstream commit**.

## Caveats / precise scope for upstream mail

- **Unproven electrical parent:** on Denali, the experimental PM8010
  LDO6 input is provisionally mapped to `vreg_s4c_1p8` based on
  independent community work; no schematic/Windows wiring proof.
  This is not an upstream-ready regulator input claim.
- **No physical/optical autofocus proof:** successful focus-control
  transactions indicate register communication; a lit textured
  scene is still needed to confirm real lens movement/sharpness.
- **No unattended deep sleep/standby power result:** SP11's PM8xxx
  RTC currently lacks a usable `wakealarm` sysfs interface.
  Timed autonomous deep sleep without a verified wake route is
  inappropriate. System-wide actual deep suspend remains untested.
- **Userspace and sensor caveats:** libcamera 0.7.0 lists the
  camera but warns that the OV13858 driver does not expose crop
  rectangles and uses uncalibrated IPA defaults. During an earlier
  manual sensor power/clock experiment, the log recorded an
  isolated `ov13858: failed to enable clock: -16`; normal capture
  and subsequent PM tests succeeded. This should not be presented
  as a completely warning-free camera stack.
- **Independent peer result:** Haipeng Lin reported full-resolution
  streaming and VCM focus on X1P-64-100 LCD/5G, but his tests kept
  L6M on for VCM communication. Our *OLED* experiments specifically
  tested the optional-vddio fix and independent rail lifetimes.
  Do not claim that either reviewer tested the other's exact patch.

## Local SP11 evidence files (not committed as raw logs)

`/home/geoca/build/sp11-vcm-upstream-rfc-20261121/experiment/`:

- `pm-vcm-openclose-20261121.log`
- `pm-stream-v4l2.log`
- `v4l2-compliance-sensor.log`; `v4l2-compliance-lens.log`
- `pm-devices-roundtrip-20261121.log`
- `pm-devices-three-cycle-20261121.log`
- `pm-3cycle-stream-{1,2,3}.log`
- `upstream-dw9800k-v4/live-module-test-v3.log`
- `upstream-dw9800k-v4/schema-validation.log`
- `synthetic-frames/sensor-pattern-direct.raw`
- `fullres-20261121/cam.log` and RAW frames.

Raw room imagery, any proprietary firmware, and raw large local
kernel logs are deliberately not committed to GitHub.

**Proposed upstream next step:** coordinate with Griffin/Sakari on
the pending v4 binding layout, then submit the optional-vddio
binding/driver series against the final v4 base if accepted. Keep
Denali input-parent DTS discovery and userspace camera-monitor PM
policy as separately scoped follow-ups.
