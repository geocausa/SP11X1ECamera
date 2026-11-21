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

## Primary target: upstream Linux

- **Primary target: Linux media upstream** (`torvalds/linux` current master
  as inspected 21 November 2026). This RFC is **not yet submitted**.
- `drivers/media/i2c/dw9719.c` baseline blob `5d5da0439dba01e5d9c458e6c357d579b5c54157`.
- `Documentation/devicetree/bindings/media/i2c/dongwoon,dw9719.yaml`
  baseline blob `8e8d62436e0d0c4f9af9e52262b23881abd37cec`.
- Oaklee's `ooaklee/linux_ms_dev_kit-sp11` is a **read-only compatibility
  reference**, not our development destination. No changes have been made
  to his kernel or project repositories.
- The intent is a generic optional supply addition plus a separately
  reviewed Surface board DT patch once exact supply phandles are verified.

## What changes

Add optional `vddio-supply` (keeping existing `vdd-supply` mandatory).
When present, the actuator requests I/O voltage before VDD and releases it
after VDD. Regulator reference-counting permits the rear OV13858 and its
DW9800K actuator to share L6M without declaring it always-on.

Existing boards with no `vddio-supply` retain the single-supply path.
Probe errors other than an absent optional supply propagate, including
deferred probing. I2C detection failures now unwind the enabled supplies.

## Verification status (21 November 2026)

- Patch rebased against the explicitly recorded mainline source blobs: **yes**.
- Review / static anchor checks during preparation: **yes**.
- `git apply --check` against an extracted kernel checkout: **NOT RUN**.
- C build / DT binding validation / hardware or runtime PM tests: **NOT RUN**.
- Physical SP11 Linux access in this session: **unavailable** (device on Windows).
- Tested-by / Reviewed-by / Signed-off-by: **none claimed**.

Do **not** redistribute as validated, submit upstream, apply to production,
or update protected Golden boot artifacts until the validation plan is complete.
