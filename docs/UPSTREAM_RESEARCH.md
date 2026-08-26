# Upstream and community research snapshot — 2026-08-26

This is a dated research snapshot, not timeless truth. Re-check upstream before importing patches.

## Qualcomm X1E80100

The Linux CAMSS driver and DT bindings already contain X1E80100 resources. Our deployed kernel also has `CONFIG_VIDEO_QCOM_CAMSS=m` and the module installed.

The X1E CSI PHY architecture is still evolving upstream. Late-July/August 2026 standalone CSI2-PHY patch series are D-PHY-first; C-PHY support is described as follow-on work. Therefore the SP11 IMX681 physical mode must be established from Windows evidence before choosing an implementation path.

## Surface community

Existing SP11 camera repositories/issues are useful for hardware identification and hypotheses, but at the E000 snapshot they do not constitute a mechanically proven complete Snapdragon SP11 camera stream.

Use community work as reference material after checking it against this SP11's hardware IDs, Windows resource/configuration packages and current upstream X1E code.

## Useful comparison hardware

Working X1E camera support on other Qualcomm laptops can demonstrate how CAMSS/CCI/CSI graph integration should look, but regulator/GPIO/clock/lane values are board-specific and must not be copied into Denali blindly.

## Research references captured at E000

- linux-surface SP11 camera status/playbook: https://github.com/rjindael/fedora-surface-pro-11/blob/main/CAMERA.md
- linux-surface SP11 camera bring-up notes: https://github.com/rjindael/fedora-surface-pro-11/blob/main/CAMERA_BRINGUP.md
- SP11 rear OV13858 tracking: https://github.com/ooaklee/linux-surface-pro-11-oe/issues/41
- SP11 IR VD55G0 tracking: https://github.com/ooaklee/linux-surface-pro-11-oe/issues/42
- SP11 front IMX681 tracking: https://github.com/ooaklee/linux-surface-pro-11-oe/issues/43
- X1E standalone CSI2 PHY v15 discussion snapshot: https://lkml.iu.edu/2608.0/05243.html

These URLs are evidence pointers, not authority over observations from the actual SP11.
