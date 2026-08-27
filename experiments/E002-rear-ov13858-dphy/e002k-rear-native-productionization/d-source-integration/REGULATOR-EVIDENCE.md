# PMIC-M regulator evidence — 2026-08-27

## Proven

- Golden's `qcom-rpmh-regulator.c` is byte-identical to vanilla Linux 7.1.5.
- That driver contains native `qcom,pm8010-rpmh-regulators` support.
- PM8010 native descriptors include LDO1, LDO5 and LDO6 and use standard RPMh VRM resource addressing/voltage/enable/mode registers.
- Live Golden currently has PMIC providers b,c,d,e,f,i,j and no PMIC-M provider.
- The accepted custom camera provider directly used the same RPMh VRM offsets and mode 7; it was a DT-topology bring-up shim, not evidence of a missing regulator protocol.
- A saved SP11 baseline DT contains a native PM8010-M provider and proves `vdd-l3-l4 = vreg_s4c_1p8` and `vdd-l5 = vreg_bob1` on this device.

## Unresolved

- Correct input supply for PM8010 M LDO1/LDO2.
- Correct input supply for PM8010 M LDO6.

These unresolved parents block removal of the custom provider from the physical sensor path. They do not block source-level driver/topology integration.
