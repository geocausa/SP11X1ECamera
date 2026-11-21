# E002 hardware results — SP11 OLED / X1E80100, 21 November 2026

**Status: hardware-tested in a separately booted *downstream-derived* experimental
kernel, NOT reviewed/merged upstream, NOT a completed optical-focus test.**

This is a reproducible observation of the staged **optional `vddio` DW9719-family
driver change** and an OLED-only board Device Tree. It does **not** prove
that this exact integration will build or behave the same in unmodified
mainline Linux; separate upstream patch review and native upstream
regression testing are still needed.

## Reproducibility and boot isolation

- Physical device: Microsoft Surface Pro 11 OLED (Denali, X1E80100).
- Host OS: Ubuntu 26.10 / ARM64.
- Experimental running release: **`7.3.0-sp11-camera-rfc1+`**,
  compiled with native GCC 15.3.
- Build base: accepted unified13 source commit
  `3094f120b90e7b2df9ccb326b1193d66bcc217a5`,
  separate detached source/out; applied out-of-tree CCI, CAMSS,
  OV13858, camera DT and optional-`vddio` patches described in
  [E002 README](README.md).
- `make Image modules`: **exit 0**; installed **8,711 modules** under
  `/lib/modules/7.3.0-sp11-camera-rfc1+`; no overwrite of the
  accepted kernel's modules.
- Image: **72,776,192 bytes**,
  SHA256 `ec6b68c94873a761d409955fc2c65c2d559396a9a27c94235253ff1d9a5f26af`.
- First boot with DTS RFC1 succeeded: both drivers bound, but **lens
  not exposed in media graph** because the sensor lacked
  `lens-focus = <&rear_vcm>;`. This was corrected in RFC2 before the
  autofocus tests. A second **one-shot** boot succeeded using the same
  kernel and **RFC2 DTB** SHA256
  `5e3055f6606c64e50c016c21979745fed1d3d4eb89fc1cd6514248f99546684e`.
  The DTS files in this branch represent **RFC2**.
- Standalone camera/actuator/CAMSS binding checks: **PASS**.
  The camera-specific full schema validation passed; a non-camera
  Qualcomm TCSR clock-controller schema warning remains.
- Golden v19c and accepted unified13 `/boot` image/DTB/initramfs,
  original `grub.cfg`, original unified13 modules and all Oaklee
  repositories were unchanged. `next_entry` was consumed, leaving
  the accepted unified13 GRUB entry as the persistent default.

## Camera graph, streaming and compliance

- OV13858: `cci0` master 1, address `0x10`,
  `/dev/v4l-subdev28`, `msm_csiphy1`, 4-lane D-PHY.
- DW9800K: `cci0` master 1, address `0x0c`, driver `dw9719`,
  `/dev/v4l-subdev29` after the `lens-focus` link was added.
- `v4l2-compliance -d /dev/v4l-subdev28`: **46/46, 0 failures,
  0 warnings**, exit 0.
- `v4l2-compliance -d /dev/v4l-subdev29`: **45/46**, one failure
  (control-event subscription), exit 1. This is a distinct V4L2
  actuator interface gap; it must not be misreported as 46/46.
- `cam --camera=1 --stream=role=raw,width=4224,height=3136
  --capture=3 --file=...`: **3/3 Bayer RAW10 CSI2-packed frames**,
  exactly **16,558,080 bytes each**, with approximately 29–30 fps
  after initial frame; libcamera 0.7.0, no reported CAMSS, CCI
  transaction or regulator error. Another **nine full-resolution
  frames** were captured in three 3-frame sessions at lens focus
  positions **0, 512 and 1023**; all 3 sessions exited 0.
- Additional lower-resolution streams at **1056x784**, including a
  **120-frame** run, completed normally at approximately 30 fps.

### Important limitation: these are captured frames, not yet a clear scene

The ordinary RAW frames were nearly uniform at the sensor's black level
(`~64.25 ± 0.52` for decoded 10-bit green samples). Whether the rear
optics were obstructed, facing a surface, or too dark **was not established**.
The data therefore **cannot yet prove optical sharpness/actual focal-plane
movement**. The owner heard clicking during focus tests, consistent
with actuator motion, but we do not substitute that for a resolved
image comparison.

### Live sensor-generated test-pattern check

During a separate **120-frame, 1056x784** libcamera capture, we
set `test_pattern=1` on the sensor subdevice **while streaming**,
then restored `test_pattern=0`. Representative decoded
MIPI RAW10 first-pixel values across packed groups:

| Frame | Phase | Mean | Std. dev. | Observed min/max |
| --- | --- | ---: | ---: | --- |
| 15 | Before pattern | 64.15 | 0.39 | 63–68 |
| 25 | Pattern enabled | 539.87 | 479.49 | 64–1023 |
| 45 | Pattern enabled | 539.87 | 479.49 | 64–1023 |
| 65 | Pattern disabled | 64.15 | 0.39 | 63–69 |

This demonstrates actual changing sensor-generated pixel values delivered
across the CSI/CAMSS buffer path (rather than an empty/DMA-only stream).
The sensor's `test_pattern` control was restored to **Disabled**.

## Lens-control and shared-regulator hardware tests

The `dw9719` driver was tested with **independent `vddio` and `vdd`
consumers**, not a forced always-on L6M. `/sys/kernel/debug/regulator/regulator_summary`
showed:

- `vreg_l6m_1p8` (PM8010 LDO6_M, 1.8 V): **both**
  `1-0010-dovdd` and `1-000c-vddio` consumers.
- `vreg_l16b_2p9` (PM8550 LDO16_B, 2.912 V selector):
  `1-000c-vdd` consumer.

Six manual `VIDIOC_S_CTRL`/`G_CTRL` actuator cycles at
focus settings **0, 256, 512, 768, 1023, 128**:
**6/6 commands accepted and read back**, no relevant kernel I2C or
regulator errors. With the lens FD open, `L6M=1`, `L16B=1`;
~1.65 s after closing the FD, the lens was runtime suspended with
`L6M=0`, `L16B=0` in **all six cycles**.

**End-to-end libcamera lifecycle, 120 frames:**

| State | L6M enable count | L16B enable count | Sensor | Lens |
| --- | ---: | ---: | --- | --- |
| Before capture | 0 | 0 | suspended | suspended |
| While libcamera streaming | 2 | 1 | active | active |
| After camera release and autosuspend | 0 | 0 | suspended | suspended |

The `lens-focus` link makes libcamera open the actuator during a
camera session, explaining the two simultaneous L6M consumers.
No `regulator-always-on` hack was required.

**Desktop user-space caveat:** WirePlumber's camera monitor held
`/dev/v4l-subdev29` open while its service was running; the
actuator runtime usage count stayed 1, holding both rails on.
Stopping WirePlumber released the FD and both rails autosuspended.
This is a **userspace client lifecycle / idle-power consideration**,
not proof of a regulator leak in the driver. Normal desktop audio
requires restoring the WirePlumber service after the experiment.

## Suspend/resume scope

The SP11 `rtc-pm8xxx` `rtc0` exposed **no**
`/sys/class/rtc/rtc0/wakealarm` or
`/sys/class/rtc/rtc0/device/power/wakeup`; `rtcwake -m show`
reported RTC wake events unavailable. An unattended **real deep-sleep
suspend** was therefore deliberately **not attempted**.

Instead Linux's auto-return **`pm_test=devices`** device
suspend/resume test passed in ~7 seconds from an idle state,
leaving sensor and lens bound, suspended, and both regulators off.
The same test **with the lens FD open and focus control at 640**
also passed (~6.91 seconds): focus readback remained 640,
both actuator rails remained enabled upon return and dropped to
0 when the FD closed. Both tests restored `pm_test=[none]`.
These are **device-level simulations**, not full system deep-sleep
or measured standby-power evidence.

## Remaining work before upstream submission

1. Confirm the **physical input parent** for PM8010 LDO6_M:
   `vdd-l6-supply = <&vreg_s4c_1p8>` is inherited from independent
   experimental SP11 code and **is not independently schematic-verified**.
2. Validate the proposed DW9719 driver/binding split against the
   current **mainline** tree with upstream dependencies; the live
   device tests here used a downstream-derived kernel.
3. Reproduce optical sharpness changes with the rear camera facing
   a well-lit textured scene; current ordinary frames are near-black.
4. Investigate the VCM event-subscription compliance failure (45/46)
   and libcamera's OV13858 `VIDIOC_SUBDEV_G_SELECTION` warnings,
   which do not block RAW capture but merit upstream cleanup.
5. Resolve userspace camera enumeration that can pin the actuator's
   rails while WirePlumber is running.
6. Run real full suspend/resume/standby testing **only once a reliable
   remote or attended wake mechanism is available**.
7. Do not claim `Tested-by` for *an exact upstream email series*
   until that exact patch ancestry and test scope have been verified.

## Evidence retained on SP11 Linux

Local root:
`/home/geoca/build/sp11-vcm-upstream-rfc-20261121/experiment/`

Notable logs and scripts:
`focus-pm-cycles.log`,
`focus-optical-evidence/results.json`,
`focus-optical-evidence/raw-image-analysis.json`,
`capture-rfc2/cam-first.log`,
`capture-rfc2/testpattern-live/run.log`,
`pm-test-devices.log`,
`pm-test-lens-active.log`,
`libcamera-rail-lifecycle.log`,
`v4l2-compliance-ov13858.log`,
`v4l2-compliance-dw9800k.log`,
`preboot-evidence/PROTECTED_BOOT_SHA256_PRE.txt`,
`postboot-evidence-20261121/`.

**RAW frame buffers and any private device dumps remain local to the
user's SP11**, not copied into the public repository. The original
user and upstream repositories are not modified by these results.
