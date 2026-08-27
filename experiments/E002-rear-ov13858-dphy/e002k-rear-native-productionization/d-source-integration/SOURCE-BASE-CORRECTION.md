# E002k-D source-base correction

Date: 2026-08-27

Runtime ABI inspection found that `.golden-v33-delta-replay/src` is not a pure FullIO v19c runtime source anchor: it contains later audio development in q6apm, TX/VA macro and X1E sound-card source.

Mechanical source comparison against `.golden-v33-repro/src` found the post-Golden drift confined to audio source. After restoring those files from `.golden-v33-repro/src` and removing generated `*.mod.c` debris, a complete source-like tree comparison proved:

- files only in Golden: 0
- files only in camera tree: 0
- different source files: exactly 3
  - `drivers/media/i2c/ov13858.c`
  - `arch/arm64/boot/dts/qcom/hamoa.dtsi`
  - `arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi`

`TRUE_GOLDEN_PLUS_CAMERA_ONLY=PASS`

The three differences are precisely the clean E002k-D camera series plus the accepted FullIO/touch Kitchen reconciliation in the Denali DTS.

A separate-release build was used as an audit tool but is intentionally **not** the first runtime integration payload because changing release would require deploying a complete rebuilt module universe. The minimum-risk R3 runtime therefore keeps the exact Golden v19c Image and Golden module environment and changes only the maintained-source DTB plus the production OV13858 module in an isolated initrd.

This is a stricter runtime isolation than replacing the kernel/module tree: CAMCC is already built into Golden, CCI/CAMSS are unchanged and Golden-compatible, and OV13858 is the only changed camera kernel module.
