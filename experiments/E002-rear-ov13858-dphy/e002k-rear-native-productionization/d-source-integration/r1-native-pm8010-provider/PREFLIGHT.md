# E002k-D-R1 — native PM8010-M provider-only gate

Status: PREPARED / NOT YET BOOTED

## Question

Can the kernel's native `qcom,pm8010-rpmh-regulators` provider register PMIC ID `m` on this SP11 with the X1 upstream-backed input topology, while no camera consumer exists and no M-rail vote is sent?

## Parent topology

The provider uses:

- L1/L2 input: `vreg_s5j_1p2`;
- L3/L4 input: `vreg_s4c_1p8`;
- L5 input: `vreg_bob1`;
- L6 input: `vreg_s4c_1p8`;
- L7 input: `vreg_bob1`.

This combines direct SP11 baseline evidence for L3/L4 and L5 with current upstream X1 PM8010 review/board evidence for L1/L2 and L6. No sensor, CAMSS, CCI or camera pinctrl node is added in this gate.

## Child constraints

Only LDO1, LDO5 and LDO6 are described. Each uses a non-fixed allowed voltage range containing the Windows-proven camera voltage. The gate intentionally omits `regulator-boot-on`, `regulator-always-on` and initial-mode properties.

Expected provider-only state after boot:

- PM8010-M provider bound;
- L1/L5/L6 regulators present;
- zero consumers/users;
- no camera rail enable vote;
- no regression to Golden audio/Wi-Fi.

## Payload

Kernel and initrd remain byte-for-byte Golden. The candidate DTB is Golden plus this one provider node only. Golden remains the saved GRUB default and the test is one-shot.
