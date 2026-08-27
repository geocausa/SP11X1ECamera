# True Golden five-patch replay

Validated after R3 runtime acceptance on 2026-08-27.

Canonical source anchor:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src`

A minimal filesystem replay copied the three source files touched by the maintained series from that exact anchor and applied, in order:

1. `0001-media-ov13858-surface-profile.patch`
2. `0002-arm64-dts-qcom-hamoa-add-x1e-camera-infrastructure.patch`
3. `0003-arm64-dts-qcom-denali-add-rear-ov13858.patch`
4. `kitchen-reconciliation/0004-sp11-preserve-phase91-touch-transport.patch`
5. `kitchen-reconciliation/0005-sp11-preserve-fullio-v19c-tx-dmic.patch`

All five applied with `patch --fuzz=0 -p1`. Offsets are permitted; no fuzz or rejects occurred.

The resulting three files were SHA-256 byte-identical to the source used for the accepted R3 runtime:

- `drivers/media/i2c/ov13858.c`: `a417ba2f0e4cc8cd0c6a3f8743f6baac40e9f378eeabc0cde186c13f2f9e94e2`
- `arch/arm64/boot/dts/qcom/hamoa.dtsi`: `f880fb137dec52f68cf558ac1b09d4499137b85dc9a78039616fdf00f44a6da5`
- `arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi`: `63b6c7e46124adaf19cb869c612c597df23c34cc48e0ddc4afbbbb8af88aca8d`

`TRUE_GOLDEN_FIVE_PATCH_REPLAY=PASS`

The previously used `.golden-v33-delta-replay/src` is **not** the canonical production base; source audit found later audio-development changes there. See `SOURCE-BASE-CORRECTION.md`.
