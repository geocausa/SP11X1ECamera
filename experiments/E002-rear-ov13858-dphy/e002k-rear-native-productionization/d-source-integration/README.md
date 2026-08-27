# E002k-D — source-level rear-camera production integration

Status: R3 SOURCE-INTEGRATED RUNTIME ACCEPTED / GOLDEN RESTORED

## Accepted input

E002k-C proved the physical rear OV13858 path without experiment-specific DT switches:

- standard sensor supplies: DOVDD 1.8 V / DVDD 1.2 V / AVDD 2.8 V;
- four-lane D-PHY, one 592.8 MHz firmware link frequency;
- 4076x2806 @ ~30 fps, VT pixel rate 432732960 Hz;
- deterministic sensor color-bar SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
- 16/16 normal frames, sequences 0..15, clean power teardown;
- VAF/LDO16_B is external to the OV13858 sensor lifecycle and had zero enable votes.

## Base-source decision

The canonical production anchor is the true Golden v33 reproduction source:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src`

A later audit proved that `.golden-v33-delta-replay/src` contains post-Golden audio-development changes and must **not** be used as the production base. See `SOURCE-BASE-CORRECTION.md`.

The accepted maintained five-patch series replays against the true Golden source with `patch --fuzz=0 -p1` and reproduces byte-for-byte the three source files used by R3. See `TRUE-GOLDEN-PATCH-REPLAY.md`.

The final accepted source delta relative to true Golden is exactly three files:

- `drivers/media/i2c/ov13858.c`;
- `arch/arm64/boot/dts/qcom/hamoa.dtsi`;
- `arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi`.

The Denali DTS delta includes both camera integration and the reconciled FullIO v19c / Phase91 touch-QSPI semantics.

## Patch split

E002k-D is intentionally split into reviewable concerns:

1. **OV13858 sensor driver** — standard supplies/power lifecycle plus the proven Surface mode selected from standard endpoint metadata while generic upstream modes remain unchanged.
2. **Denali rear-camera topology** — CCI/OV13858/CSIPHY/CAMSS graph, GPIO97 MCLK, four-lane 592.8 MHz endpoint and the proven CSIPHY1 8 KiB MMIO resource.
3. **PMIC-M regulator topology** — replace the temporary camera-only RPMh shim with the existing `qcom,pm8010-rpmh-regulators` driver, but only after all required input-supply parents are evidence-backed.

## Native PMIC-M finding

Linux 7.1.5 already supports PM8010 RPMh regulators and maps `ldo1`, `ldo5` and `ldo6` to the same RPMh VRM mechanism used by the bring-up shim. Live Golden lacks any `qcom,pm8010-rpmh-regulators` provider with `qcom,pmic-id = "m"`.

A saved SP11 baseline DT from this machine proves that PMIC-M was represented natively as:

- `compatible = "qcom,pm8010-rpmh-regulators"`;
- `qcom,pmic-id = "m"`;
- `vdd-l3-l4-supply = <&vreg_s4c_1p8>`;
- `vdd-l5-supply = <&vreg_bob1>`.

That baseline does **not** prove the input parents for L1_M/L2_M or L6_M. E002k-D must not guess them.

## Regulator sub-gates

- **D-R0:** source integration may retain the already-proven temporary provider only as a runtime reference while driver/DT patch structure is established.
- **D-R1:** instantiate a native PM8010-M provider with evidence-backed parent supplies and no camera consumer/boot-on vote; prove registration sends no unwanted rail vote.
- **D-R2:** only after D-R1, bind OV13858 DOVDD/DVDD/AVDD to native L6_M/L1_M/L5_M and repeat the deterministic sensor acceptance test.

## Runtime safety

- Golden v19c remains the saved GRUB default.
- R3 intentionally reused the exact Golden Image and Golden module environment because CAMCC was already built in and CCI/CAMSS were unchanged; only the reconciled DTB and production OV13858 module changed.
- R3 used a separate boot directory, isolated initrd layer and one-shot GRUB entry.
- No experiment overwrites Golden kernel/initrd/DTB or existing modules.
- One major unknown per runtime boot.

## Kitchen reconciliation

The exact FullIO v19c non-camera delta is reconstructed at source level as two maintained patches: Phase91 touch/QSPI transport and TX-DMIC FullIO capture closure. The five-patch series applies to the true Golden source with `--fuzz=0`, the reconciled Denali OLED DT compiles cleanly, and `kitchen-reconciliation/verify-v19c-kitchen.py` reports `NONCAMERA_V19C_RECONCILIATION=PASS`.

## Accepted R3 runtime

R3 booted one-shot using the exact Golden v19c Image plus the reconciled DTB and production OV13858 in an isolated initrd. It proved native PM8010-M, production OV13858 srcversion `9366B03E91F9212A1501AEC`, the accepted 4076x2806 RAW10 graph, deterministic color-bar SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`, and 16/16 normal frames at 29.9504 fps with clean teardown. Wi-Fi, FullIO playback/capture and G6 touch survived. See `r3-source-integrated-runtime/RESULT.md`.

After evidence collection the machine rebooted normally to the saved Golden v19c entry. Golden kernel/initrd/DTB hashes remained exact, `next_entry` is empty, and the post-return fault scan is clean.

## Immediate next action

Treat R3 as the accepted production camera payload. Keep Golden as the recovery/default baseline while converting the accepted five-patch series and R3 packaging into the durable production handoff/cleanup state. Do not reintroduce the post-Golden audio drift from `delta-replay`.
