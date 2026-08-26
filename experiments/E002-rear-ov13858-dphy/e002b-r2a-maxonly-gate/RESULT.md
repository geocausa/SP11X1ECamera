# E002b-r2a result — SAFE FAIL at constraint validation

The max-only DT constraint experiment was electrically inert but rejected by the regulator core:

- `vreg_l6m_camera_e002b_r1: invalid voltage constraints`
- `vreg_l16b_camera_e002b_r1: invalid voltage constraints`
- both isolated camera qcom-rpmh-regulator provider devices failed with `-EINVAL`.

Golden remained intact: Wi-Fi, playback and capture all enumerated; CAMSS/CCI/CAMCC were suspended; MCLK1 stayed disabled; no sensor or probe module existed.

Exact core rule: when a regulator has voltage enumeration, constraints are optional only when min=max=0. Otherwise both min and max must be >0. Therefore this kernel's DT parser cannot express `REGULATOR_CHANGE_VOLTAGE` without also setting `apply_uV=true`.

Next architecture: replace the experimental qcom provider instances with a camera-only external RPMh regulator provider. It will use exported `cmd_db_read_addr()`/`rpmh_write()`, register normal regulator devices with programmatic constraints and `apply_uV=false`, and attach each regulator to its DT child `of_node` so normal supply phandles work. First gate is provider-only: no sensor and no RPMh writes.
