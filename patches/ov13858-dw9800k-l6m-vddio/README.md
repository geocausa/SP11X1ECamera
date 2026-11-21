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
- `git apply --check --whitespace=error-all` against the exact upstream source blobs: **PASS**.
- Temporary `git apply`, reverse check, reverse apply, source restoration: **PASS**.
- Native ARM64 GCC DW9719 object build: **PASS** on SP11 Linux. DT binding check: **PASS** (dtschema 2026.9, yamllint 1.38.0).
- Hardware / actuator PM tests and a full deployable camera-enabled kernel: **NOT RUN**.
- Isolated build helper Bash syntax (`bash -n`): **PASS**; executed with native GCC fallback; object build **PASS**.
- Physical SP11 Linux access in this session: **unavailable** (device on Windows).
- Tested-by / Reviewed-by / Signed-off-by: **none claimed**.

Do **not** redistribute as validated, submit upstream, apply to production,
or update protected Golden boot artifacts until the validation plan is complete.

## 21 November 2026 provenance additions

- [Verified regulator mapping and test results](../../docs/OV13858_DW9800K_REGULATOR_MAP_20261121.md): Linux `vreg_l6m_1p8` = PM8010/m LDO6; `vreg_l16b_2p9` = PM8550/b LDO16, but the Denali PM8010 input supply remains unverified.
- [Isolated build script](../../tools/prepare-ov13858-vcm-test-kernel.sh): pins the upstream source hashes, creates only a disposable worktree and output directory and compiles the DW9719 object if a suitable Linux build host is available. It **does not install** an image and has **not been run**.

## Upstream patch split (RFC, UNTESTED)

The combined patch above remains an apply/build convenience artifact.
For upstream review **use the two separate patches below** instead:

1. [0001: DT binding optional vddio supply](upstream/0001-dt-bindings-media-i2c-dongwoon-dw9719-add-vddio-supply.patch)
2. [0002: DW9719 driver optional vddio lifecycle](upstream/0002-media-i2c-dw9719-support-optional-vddio-supply.patch)

On 2026-11-21 both files passed `scripts/checkpatch.pl --no-tree --strict`
with **0 errors, 0 warnings** and joint
`git apply --check --whitespace=error-all` with **exit code 0**.
The split-patch checkpatch results were source-level checks. Subsequently
**native driver-object and DT binding builds PASSED on SP11 Linux**, but
no new kernel was booted and no autofocus hardware test was performed. These are RFC diffs,
not signed-off upstream mail submissions.

## Native SP11 Linux validation (later on 2026-11-21)

See [native build and RPMh evidence receipt](../../evidence/SP11_OV13858_DW9800K_UPSTREAM_BUILD_20261121.md):
mainline `c44104f3642d`, arm64 GCC 15.3, `dw9719.o` built,
`dt_binding_check` and optional YAML lint passed, OLED/X1E and LCD/X1P
**baseline** DTBs built. The live RPMh command database exposes `ldom6`
and `ldob16`. The **Denali L6M input parent is unverified**;
no new camera DTB, full boot image, rail toggling or focus test was performed.
