# SP11 OV13858 / DW9800K shared L6M power integration

**STATUS: PROPOSED / UNTESTED / NOT SUBMITTED**

**Scope:** rear OV13858 camera, rear VCM at 7-bit CCI/I2C address `0x0c`,
reported compatible `dongwoon,dw9800k`. This is a board-integration proposal,
not a tested Device Tree patch or a claim of autofocus parity.

## Evidence and hypothesis

Haipeng Lin's 21 November 2026 report on an **X1P / LCD 5G** Surface Pro 11:
the rear VCM responds and `focus_absolute` moves focus when the OV13858's
DOVDD (L6M) is on; independent VCM probing can time out at boot if L6M is off.
The rear camera itself streamed 4224 x 3136 at about 30 fps using George's
OV13858 DT v2 and Sergey's power v4 on his test tree. **That did not test
this proposed optional-vddio patch.**

Our X1E/Denali Windows oracle power map records rear sensor D0:
LDO6_M = 1.8 V first; LDO1_M = 1.2 V; LDO5_M = 2.8 V;
LDO16_B = 2.9 V later; then MCLK1 at 19.2 MHz and reset release.
Source: `experiments/E001-windows-oracle-map/derived/power-map.md`.
The Haipeng report identifies L16B as the actuator's `vdd` rail.

**Working hypothesis:** the VCM's 2.9 V VDD alone is insufficient for I2C
communication; it needs the same 1.8 V L6M I/O supply as the sensor.
The existing DW9719-family driver requests only `vdd` and probes without
holding the OV13858 sensor runtime-PM reference. The fix should represent
both supplies directly on the VCM and let the regulator framework share L6M.

## Device Tree change to make separately after checking the real board DTS

Place the following **illustrative, non-compilable until phandles are
resolved** node under the physical **CCI0 master 1** bus, alongside the
rear sensor on I2C address `0x10`. The placeholder phandle names below are
NOT verified Linux regulator labels:

```dts
actuator@c {
    compatible = "dongwoon,dw9800k";
    reg = <0x0c>;
    vdd-supply = <&REPLACE_WITH_L16B_2V9_REGULATOR>;
    vddio-supply = <&REPLACE_WITH_L6M_1V8_REGULATOR>;
};
```

The OV13858 sensor's `dovdd-supply` must reference the **identical underlying
L6M regulator provider**, not a separate fixed-regulator alias that bypasses
the same physical PMIC vote. Keep the sensor's own `avdd`, `dvdd`,
`dovdd`, reset, clock, and CSI routing intact. Resolve actual PMIC
phandles and per-SKU applicability from the target DTS and regulator map;
do not blindly reuse X1E labels on X1P.

The staged driver/DT-schema patch intentionally does not contain a
Surface-specific board DTS diff: no authoritative phandle spellings or
full rear-camera DTS from the target build have been validated here.

## Intended runtime lifecycle

1. At VCM probe or runtime resume, enable shared L6M I/O supply, then
   L16B VCM VDD. Existing driver initialization and focus control follow.
2. If OV13858 streaming also uses L6M, regulator consumer votes from
   both devices keep L6M on while either still needs it.
3. On VCM autosuspend, write internal shutdown, disable L16B, then
   release the VCM's L6M vote. L6M should actually turn off when the
   sensor also releases its own vote.
4. Missing `vddio-supply` remains optional for other boards; a present
   but not-yet-registered provider must defer probing rather than silently
   treating the regulator as absent.

This does not rely on `regulator-always-on`, a permanent sensor runtime PM
reference, an invented supply chain, or a boot-order delay workaround.

## Validation gate (none of these checks has been run)

- On a disposable kernel checkout matching the source blobs, run
  `git apply --check <path-to-patch>`, then apply and build `dw9719.o`.
  Use `scripts/checkpatch.pl` and `dt_binding_check` for the amended
  `dongwoon,dw9719.yaml`; compile the **actual** SP11 DTB and run
  `dtbs_check` after substituting verified regulator phandles.
- Boot only a separate test entry; preserve the proven Golden boot path.
  Begin with OV13858 **idle** and confirm VCM `0x0c` binds without
  `-ETIMEDOUT`, `-EPROBE_DEFER` loops, or regulator warnings.
- Open the VCM subdevice, inspect `focus_absolute`, move focus between
  multiple positions, close it and observe autosuspend. Validate I2C
  transactions and rail enable counts / voltage on L6M and L16B.
- Repeat with OV13858 streaming and with sensor stopped. Confirm L6M
  stays on while **either** user holds a vote, then turns off when both
  are idle. Check sensor startup still succeeds after autofocus-only use.
- Test repeated probe/bind/unbind, camera reopen, errors during focus,
  suspend/resume and fault recovery; inspect for unbalanced regulator
  reference counts and retained rails. Explicitly test failed regulator
  enables and I2C writes.
- Compare LCD/X1P and OLED/X1E device trees before describing this as
  portable across SKUs.

### Known uncertainties and risk

- No hardware test has isolated whether sensor reset, an unmodelled
  enable, level shifter, or CCI readiness also gates VCM communication.
  L6M dependence alone does **not** prove the proposed patch is sufficient.
- Exact regulator phandle names and any needed rail settling delays
  remain to be measured rather than guessed.
- If regulator disable or an I2C error occurs, power-state recovery and
  the best error-unwind behavior need targeted fault-injection review.
- `dw9719_set_ctrl()` relies on the existing subdevice open/runtime-PM
  lifecycle; this candidate does not alter userspace focus semantics.
- No guarantee of runtime PM behavior where runtime PM is disabled;
  the existing driver explicitly leaves the actuator powered in that case.

## Rollback and upstreaming

Use `git apply -R <path-to-patch>` or revert the candidate kernel commit;
remove `vddio-supply` from the board DTS and boot the proven kernel.
Do not overwrite the Golden audio/DTB/initrd. If hardware validation
succeeds, split/update RFC changes as reviewers request and include the
actual board DTS binding in a **separate**, reviewed patch.

**No physical test, build, review, upstream submission or Oaklee repository
mutation has been performed as part of this staging task.**
