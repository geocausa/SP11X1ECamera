# E002b-r3d — corrected CAMCC XO-parent, no-power MCLK gate

Purpose: prove the X1E CAMCC MCLK rate tree after correcting E002a's parent-clock mistake, without powering the rear sensor.

## Root-cause correction
E002a/r3a/r3b supplied CAMCC with full-rate `RPMH_CXO_CLK` and `RPMH_CXO_CLK_A`. On SP11 these are 38.4 MHz. Golden already provides the X1E fixed-factor inputs expected by CAMCC:
- `bi_tcxo_div2` = 19.2 MHz
- `bi_tcxo_ao_div2` = 19.2 MHz active-only counterpart

Historical SP11 baseline CAMCC wiring also used these divided clocks.

r3d changes CAMCC parents only to `bi_tcxo_div2` / `bi_tcxo_ao_div2`. Golden DT removals: **0**.

## Electrical scope
The rear DT client remains only to provide an MCLK consumer handle. The candidate initrd contains:
- accepted camera-only RPMh provider module;
- `sp11_mclk_diag` only.

The OV13858 power probe is **not present**. `sp11_mclk_diag` calls get/round/set rate only and never calls regulator/reset APIs or `clk_prepare_enable()`.

Expected result: initial MCLK tree at 19.2 MHz or legal transition to 19.2 MHz with `clk_set_rate()==0`, while all four camera regulators remain disabled/0 users.

Artifacts:
- DTB SHA256 `4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233`
- provider module SHA256 `ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`
- MCLK diagnostic SHA256 `a83ad8bda0733aa8d541f948c22ca70b9c0825baee00d21c625727ad5e7d699b`
- initrd SHA256 `d07d915d480379fa093571995d260d1c46ec2984da49ee7f1f9c026e379bec9b`
