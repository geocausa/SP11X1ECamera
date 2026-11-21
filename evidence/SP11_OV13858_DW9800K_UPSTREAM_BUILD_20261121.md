# SP11 upstream DW9800K shared-L6M RFC — native Linux validation receipt

**Date:** 2026-11-21 (UTC)  
**Status:** driver **BUILD PASS**, DT binding **PASS**, existing Denali board DTBs **BUILD PASS**; **HARDWARE UNTESTED / BOARD INTEGRATION INCOMPLETE**.

## Exact environment

- Target: user's Surface Pro 11, `SP11Lin`; aarch64; booted and left running `7.3.0-sp11-unified13`.
- Disposable workspace: `/home/geoca/build/sp11-vcm-upstream-rfc-20261121/`.
- Pinned unmodified upstream source checkout: `torvalds/linux` commit
  `c44104f3642da720164042623e4832836aefdd8e`.
- Camera staging branch: `wip/ov13858-dw9800k-l6m-vddio-untested-20261121`.
- Applied the staged **combined** DW9719+DT binding RFC to a detached,
  disposable mainline worktree `compile/source`; outputs in `compile/out`.
- Compiler: native aarch64 GCC **15.3.0**; `ARCH=arm64`. The script
  `tools/prepare-ov13858-vcm-test-kernel.sh` now supports native GCC when
  LLVM is absent. **It did not install any kernel.**

## Tests actually executed

| Check | Result | Scope |
|---|---|---|
| `git apply --check` | **PASS** | Exact upstream source commit |
| Driver source build | **PASS** | `make O=... ARCH=arm64 drivers/media/i2c/dw9719.o` |
| Driver build configuration | `CONFIG_VIDEO_DW9719=y` | Compiled into a relocatable object; no linked kernel/module deployed |
| `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/media/i2c/dongwoon,dw9719.yaml` | **PASS** | Changed DT binding + example, dtschema 2026.9 |
| `yamllint` integration on rerun | **PASS** | yamllint 1.38.0, no warnings on rerun |
| `scripts/checkpatch.pl --no-tree --strict` on two split RFC patches | **PASS** | 0 errors, 0 warnings each |
| `qcom/x1e80100-microsoft-denali-oled.dtb` | **BUILD PASS** | Unmodified mainline OLED/X1E baseline |
| `qcom/x1p64100-microsoft-denali.dtb` | **BUILD PASS** | Unmodified mainline LCD/X1P baseline |

### Built artifact SHA256

- `compile/out/drivers/media/i2c/dw9719.o`:
  `ed8d0cd4b0edde9f8450ac1c298ad06f0aae4279e175dbe5cda96bd791ef242f`
  (55,872 bytes, ELF64 ARM aarch64 relocatable, debug symbols).
- `compile/out/arch/arm64/boot/dts/qcom/x1e80100-microsoft-denali-oled.dtb`:
  `bfe243af6c6e1749366bf1b9588bc6a0460426a04ba38fef8a7d710b5dcdefaa`.
- `compile/out/arch/arm64/boot/dts/qcom/x1p64100-microsoft-denali.dtb`:
  `11971701283c1a17de42de343fccb98d068155739f0bb686e78efe929a1b0741`.

## Verified live SP11 Linux power-platform evidence

- Live firmware DT (`/proc/device-tree/soc@0/rsc@17500000`) lists
  RPMh PMIC groups **b, c, d, e, f, i, j**, but not PM8010 regulator
  group **m**.
- `b`: `qcom,pm8550-rpmh-regulators`, with existing
  `vdd-l5-l16-supply = <&vreg_bob1>` in Denali DTS; **LDO16B is
  not yet declared as a regulator consumer node**.
- A separate SPMI hardware PMIC `qcom,pm8010` exists at
  `/proc/device-tree/soc@0/arbiter@c400000/spmi@c42d000/pmic@c`.
  This does not by itself define its RPMh LDO6 regulator node.
- The **live RPMh command database** (`/sys/kernel/debug/cmd-db`)
  enumerates `ldob16` at **0x41400** and `ldom6` at **0x40d00**.
  This verifies the firmware exposes both controllable **resource
  identities**, but **does not prove any parent-input electrical wiring**.
- No `vreg_l6m_1p8` or `vreg_l16b_2p9` consumer-provider appears in
  the currently running regulator summary.

## Explicit unresolved gating issue

**The actual PM8010/M LDO6 input supply on this Denali SP11 remains
unverified.** The QCP board's `vdd-l6-supply = <&vreg_s6g_1p8>`
must not be copied: Denali has no corresponding `vreg_s6g_1p8`
provider. Do not invent a phandle or use `regulator-always-on` to
mask the dependency. The Linux driver can compile successfully while
this missing electrical connection prevents autofocus at runtime.

The two built Denali DTBs are **baseline DTBs** and do not contain the
new camera node or the additional L6M/L16B regulator consumers.
No `dtbs_check` of a fully integrated new camera-enabled SP11 DTB
has been possible, because that DTS is intentionally not yet produced.

## No installed or runtime changes

No camera hardware probing, rail toggling, focus movement, image capture,
suspend/resume experiment, `modules_install`, GRUB changes, `/boot`
writes or reboot after Linux became available. GRUB `next_entry`
was observed empty after boot. The protected Golden boot entry, other
kernel modules/DTBs/initrds and **all Oaklee repositories** are untouched.
Mainline source and build outputs are only in the new disposable directory.

## Next small milestone

Reconcile the L6M parent-input supply from Denali-specific board
schematics/firmware or a controlled, separately recorded electrical
observation. Once verified, add a **separate** Denali DTS patch supplying
the actual `vreg_l6m_1p8` and `vreg_l16b_2p9` regulator nodes and
VCM/sensor supply consumers, then run binding + `dtbs_check` on that
candidate. A full isolated kernel image/DTB package can then be built
as a separate one-shot test boot; **do not overwrite Golden**.
