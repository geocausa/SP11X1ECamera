# E002k-D — source-level rear-camera production integration

Status: SOURCE + KITCHEN RECONCILED / NO INTEGRATED RUNTIME MUTATION YET

## Accepted input

E002k-C proved the physical rear OV13858 path without experiment-specific DT switches:

- standard sensor supplies: DOVDD 1.8 V / DVDD 1.2 V / AVDD 2.8 V;
- four-lane D-PHY, one 592.8 MHz firmware link frequency;
- 4076x2806 @ ~30 fps, VT pixel rate 432732960 Hz;
- deterministic sensor color-bar SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
- 16/16 normal frames, sequences 0..15, clean power teardown;
- VAF/LDO16_B is external to the OV13858 sensor lifecycle and had zero enable votes.

## Base-source decision

Historical audio kernel trees are not suitable camera development bases: several contain thousands of modified/untracked files. E002k-D therefore uses a fresh writable copy of the exact Golden replay source:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src`

The original Golden replay source is read-only by policy for this experiment and must not be edited.

Vanilla Linux 7.1.5 and the Golden replay source have byte-identical:

- `drivers/media/i2c/ov13858.c`;
- `drivers/regulator/qcom-rpmh-regulator.c`.

The Golden Denali DTS differs from vanilla only because of already-accepted non-camera board deltas (audio/Wi-Fi), which must be preserved.

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
- Any integrated camera kernel uses a separate release, module tree, boot directory and one-shot GRUB entry.
- No experiment may overwrite Golden kernel/initrd/DTB or existing modules.
- One major unknown per runtime boot.

## Current Kitchen reconciliation

The exact FullIO v19c non-camera delta has now been reconstructed at source level as two additional maintained patches: Phase91 touch/QSPI transport and TX-DMIC FullIO capture closure. The five-patch Golden replay applies with `--fuzz=0`, the reconciled Denali OLED DT compiles cleanly, and `kitchen-reconciliation/verify-v19c-kitchen.py` reports `NONCAMERA_V19C_RECONCILIATION=PASS`. See `kitchen-reconciliation/RESULT.md`.

## Immediate next action

Collect the independent full kernel/modules build, require exact kernelrelease and valid `Image`/`Module.symvers`, inspect OV13858/CAMSS/CCI module vermagic and modversion CRC compatibility, and only then construct a separate one-shot integrated runtime candidate using the reconciled DTB. Golden remains the saved default.
