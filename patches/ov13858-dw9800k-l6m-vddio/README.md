# RFC: OV13858 rear VCM shared L6M I/O supply

**STATUS: PROPOSED / UNTESTED / NOT SUBMITTED**

This directory stages a **candidate**, not a tested or accepted fix. No kernel,
device tree, boot configuration, or other repository has been changed by this
staging work. The branch is for review and follow-on hardware validation.

## Files

- `0001-media-i2c-dw9719-support-optional-vddio-supply.patch`: standalone
  `git apply` patch for the DW9719-family driver and its DT schema.
- `../../docs/OV13858_DW9800K_SHARED_L6M_VDDIO.md`: SP11 board integration,
  evidence, limitations, and validation/rollback plan.

## Source targeted

- `ooaklee/linux_ms_dev_kit-sp11`, branch `sp11/ubuntu-qcom-x1e-7.3.y`, **read-only reference**.
- `drivers/media/i2c/dw9719.c` blob `3b7ba88fd67c044ef9005a0aac6a5d26ab939a90`.
- `Documentation/devicetree/bindings/media/i2c/dongwoon,dw9719.yaml`
  blob `8e8d62436e0d0c4f9af9e52262b23881abd37cec`.
- Proposed change is generic and optional; it is not specific to an Oaklee
  packaging tree and has **not** been applied to Oaklee's repository.

## What changes

Add optional `vddio-supply` (keeping existing `vdd-supply` mandatory).
When present, the actuator requests I/O voltage before VDD and releases it
after VDD. Regulator reference-counting permits the rear OV13858 and its
DW9800K actuator to share L6M without declaring it always-on.

Existing boards with no `vddio-supply` retain the single-supply path.
Probe errors other than an absent optional supply propagate, including
deferred probing. I2C detection failures now unwind the enabled supplies.

## Verification status (21 November 2026)

- Patch constructed against the explicitly recorded source blobs: **yes**.
- Review / static anchor checks during preparation: **yes**.
- `git apply --check` against an extracted kernel checkout: **NOT RUN**.
- C build / DT binding validation / hardware or runtime PM tests: **NOT RUN**.
- Physical SP11 Linux access in this session: **unavailable** (device on Windows).
- Tested-by / Reviewed-by / Signed-off-by: **none claimed**.

Do **not** redistribute as validated, submit upstream, apply to production,
or update protected Golden boot artifacts until the validation plan is complete.
