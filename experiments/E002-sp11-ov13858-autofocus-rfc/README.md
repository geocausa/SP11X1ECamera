# E002 — SP11 OLED OV13858 + DW9800K runtime hardware experiment

**Status:** Preboot build in progress (2026-11-21 UTC). **NO autofocus, video capture, suspend, or idle-rail success yet.**

## Purpose

Prove that the `dw9719` driver's new optional `vddio` consumer gives the
DW9800K autofocus lens independent reference-counted access to PM8010
LDO6_M (1.8 V) while the OV13858 rear sensor consumes the **same** DOVDD
rail. Avoid a permanent L6M vote, preserve idle power gating, and verify
probe, focus commands, streaming, and repeated close/reopen.

## Local device and build

- Device: user's Surface Pro 11 OLED / X1E80100 / Denali.
- Accepted running baseline: `7.3.0-sp11-unified13`, untouched.
- Detached source based on accepted `sp11/unified13-driver-maintenance`
  commit `3094f120b90e7b2df9ccb326b1193d66bcc217a5`.
- Unique experimental release from `CONFIG_LOCALVERSION`:
  `7.3.0-sp11-camera-rfc1+`.
- Isolated work:
  `/home/geoca/build/sp11-vcm-upstream-rfc-20261121/experiment/source`
  and `experiment/out`; full compile command
  `make ARCH=arm64 O=... -j8 Image modules`.
- Baseline source, original build output, accepted `/boot`,
  `/lib/modules/7.3.0-sp11-unified13` and all Oaklee repositories
  **never edited**.
- Config is accepted unified13 copied then `LOCALVERSION` made unique;
  `CONFIG_VIDEO_OV13858=m`, `CONFIG_VIDEO_DW9719=m`,
  `CONFIG_I2C_QCOM_CCI=m`, `CONFIG_VIDEO_QCOM_CAMSS=m`.
  Front IMX681 and IR VD55G0 disabled for this isolated rear test.

## Reused existing Linux work — credits and scope

Source patches taken **without modifying upstream/origin repos** from
`omacom/omarchy-pkgs` (original authors, provenance and SPDX preserved in
the local disposable worktree):

- `2121` corrected X1E CAMSS DT binding.
- `2122` OV13858/VD55G0 DT bindings.
- `2123` CAMSS unwind on failed stream start.
- `2161` X1E CAMSS + CCI DT nodes (default disabled).
- `2162` sensor drivers, SP11 OV13858 mode, regulator/runtime power.
- `2134` OV13858 initial SCCB retry.
- `2208` CCI controller reset on resume.
- `2209` 50 ms CCI autosuspend.
- User's own staged combined optional-`vddio` DW9719 driver/binding RFC
  also applied and passes source checks.

The published `2163` all-three-camera board patch was NOT applied: it
doesn't fit the accepted unified13 DTS cleanly, and it would enable the
front/IR cameras unnecessarily.

## OLED-only test Device Tree sources

- `x1e80100-microsoft-denali-autofocus-rfc.dts`
- `x1-microsoft-denali-rear-autofocus-rfc.dtsi`

These are **separate files** and do not edit the common Denali DTS. They
enable the CCI0/master1 bus (OV13858 at `0x10`, DW9800K at `0x0c`),
CAMSS CSIPHY1 four-lane D-PHY, MCLK1 19.2 MHz, reset GPIO110, PM8010
LDO1/5/6, PM8550 LDO16B and correctly shared L6M VCM I/O/sensor DOVDD
consumers. They are **not ready for upstream submission**.

**Critical uncertainty:** the PM8010 LDO6 input parent
`vdd-l6-supply = <&vreg_s4c_1p8>` is drawn from an independent SP11
experimental source which **explicitly labels its PM8010 parents
unverified**. The existing upstream QCP parent differs. We have
confirmed the firmware RPMh command database contains `ldom6` and
`ldob16`, but have no independent Denali schematic evidence for the
physical L6M input. This experiment must not be described as proving it.

## Validation completed BEFORE kernel boot

- Candidate OLED autofocus DTB: **DTC PASS**.
- Candidate DTB SHA256:
  `cd741078209eeed6fe75cdc1da0d6cf748b82f884dd8044fba950a503e9c4279`.
- `dt_binding_check` separately for CAMSS, DW9719 and OV13858 bindings:
  **PASS**, including generated binding examples.
- Full `dt-mk-schema` and `dt-validate`: **PASS** for the camera
  and regulator definitions. Unfiltered full DTB validation prints a
  pre-existing qcom,tcsr clock-controller regulator-property schema
  warning unrelated to the camera delta.
- Earlier mainline DW9719 object compiled and passed
  `checkpatch.pl`; see
  [native mainline validation](../../evidence/SP11_OV13858_DW9800K_UPSTREAM_BUILD_20261121.md).
- Installed `v4l-utils` and `libcamera-tools` via APT for testing.

## Hardware test acceptance criteria

1. One-shot boot of a **new**, separately staged kernel/Image/DTB/initrd
   with accepted `sp11-unified13-maintenance` as permanent GRUB default.
2. Check L6M and L16B regulators exist; no boot probe timeout on VCM
   CCI0/master1 `0x0c`. Preserve `dmesg` and `regulator_summary`.
3. Identify actuator subdev; successfully execute and read back focus
   controls, and check I2C errors.
4. Confirm OV13858 `0x10` binds, four-lane graph and raw capture.
5. Check regulator enabled-count while sensor/actuator individually
   active and **zero when both closed**, without `regulator-always-on`.
6. Repeated start/stop, then one cautious suspend/resume with recovery,
   optionally battery standby after initial functionality and clear
   attended timing/measurement conditions.
7. For upstream replies keep **`Tested-by` restricted to actual tested
   series**. Haipeng's LCD streaming/focus tests do **not** validate
   our optional-vddio patch. Preserve failures and exact test conditions.

## Recovery path

Never replace Golden v19c or accepted unified13 payloads. A new kernel
release, new modules directory, new /boot directory and a one-shot
GRUB entry are the only intended boot mutations. If the new kernel fails,
the accepted unified13 entry remains the permanent default.
