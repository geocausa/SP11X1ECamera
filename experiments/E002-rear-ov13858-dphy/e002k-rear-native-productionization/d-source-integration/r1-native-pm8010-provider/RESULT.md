# E002k-D-R1 result — ACCEPTED

The provider-only one-shot boot passed.

- Native `qcom-rpmh-regulator` bound `17500000.rsc:regulators-8` (PM8010 ID `m`).
- `vreg_l6m_camera` registered at 1.8 V, `num_users=0`.
- `vreg_l5m_camera` registered at 2.8 V, `num_users=0`.
- `vreg_l1m_camera` registered at 1.2 V, `num_users=0`.
- All three report `state=unknown`, i.e. no consumer enable state was asserted.
- Regulator summary confirms parent topology: L1 <- S5J, L6 <- S4C, L5 <- BOB1.
- No camera/CAMSS/CCI node existed and no media/video node appeared.
- No PM8010/regulator registration error was logged.
- Wi-Fi, playback and capture remained healthy.
- Golden remained the saved GRUB default and the one-shot entry was consumed.

Conclusion: the stock kernel's native PM8010 RPMh provider can represent the three rear sensor rails safely. The temporary camera-specific RPMh provider is no longer required as a provider mechanism. Next gate replaces only that shim in the already-accepted E002k-C camera DT and requires byte-identical color-bar output plus 16-frame stability.
