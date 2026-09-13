# E004u runtime diagnosis — CSIPHY0 DT aperture too small

The single E004u receiver-only attempt was consumed and was not retried.

## What passed before the fault

The already-proven native sensor lifecycle passed again: model 0x3047 / revision 0x1111 CUT1, exact 552-byte Surface patch, exact Windows final sensor state, exactly 596 sensor-data writes, final SW_STBY, sensor powered off and runtime-suspended, IR-only graph complete, fixed controls correct, and the E004k CAMSS parameter armed.

E004t then reached its receiver precheck successfully:

`E004T_RECEIVER_PRECHECK: sensor=2-0060 sensor_pm=suspended csiphy=msm_csiphy0 id=0 phy=DPHY lanes=1 lane0_pos=0 downstream_link=none fmt=Y10_1X10/644x604`

## Fault

The first CSIPHY0 power-on reset write faulted before E004k lane programming:

- PC: `csiphy_reset+0x3c/0x170 [qcom_camss]`
- caller: `csiphy_set_power+0x154/0x3a0 [qcom_camss]`
- fault VA: `ffff80008420e000`
- write fault, level-3 translation fault
- no `E004J_CSIPHY0_DPHY_WINDOWS_PARITY` marker was reached
- no receiver readback occurred

The exact X1E 3-phase CSIPHY source initializes `regs->offset = 0x1000`. `csiphy_reset()` writes common CTRL0 at `csiphy->base + 0x1000`.

The disposable E004o DT declares CSIPHY0 as physical base `0x0ace4000`, size `0x1000`. Therefore devm_platform_ioremap_resource_byname() maps only the first 4 KiB, while the first X1E common-register reset access lands exactly one page beyond it.

This aligns exactly with the Oops VA: inferred mapped virtual base `ffff80008420d000`, first required common-register access `+0x1000 = ffff80008420e000`.

## Same-machine Windows corroboration

The same-machine Windows CSIPHY0 oracle captured the aperture `0x0ace4000..0x0ace5fff`, exactly 0x2000 / 8 KiB.

Thus the resource mismatch is mechanical:

- current Linux DT: base `0x0ace4000`, size `0x1000`
- X1E driver common block begins at offset `0x1000`
- same-machine Windows aperture: base `0x0ace4000`, size `0x2000`
- CSIPHY1 begins at `0x0ace6000`, so widening CSIPHY0 to 0x2000 ends exactly at the next resource and cannot overlap it

## Safety

The sensor stayed runtime-suspended with usage 0. No sensor stream callback, CSID stream callback, VFE stream callback, capture, or illumination occurred. The fault happened before receiver lane programming. SP11 returned to Golden and the disposable candidate was retired.

No same-boot retry was performed.
