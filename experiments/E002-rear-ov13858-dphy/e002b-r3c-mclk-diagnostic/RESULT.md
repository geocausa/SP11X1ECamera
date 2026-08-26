# E002b-r3c result — no-power MCLK diagnostic

This diagnostic bound to the existing rear `1-0010` DT node after unloading the failed r3b sensor shim. It deliberately never called any regulator/reset API and never called `clk_prepare_enable()`.

Observed with all four camera regulators disabled / zero users:

- MCLK1 branch initial rate: **38,400,000 Hz**
- requested rate: **19,200,000 Hz**
- `clk_round_rate(MCLK1, 19.2M)`: **19,200,000 Hz**
- `clk_set_rate(MCLK1, 19.2M)`: **-EINVAL**
- MCLK1 remained 38.4 MHz
- parent source initial rate: **38,400,000 Hz**
- `clk_round_rate(parent, 19.2M)`: **19,200,000 Hz**
- `clk_set_rate(parent, 19.2M)`: **-EINVAL**
- parent and branch remained 38.4 MHz

This proves r3b failed in CCF rate-tree construction/programming before MCLK enable and before any I2C transaction.

Root-cause evidence found immediately afterward:
- Golden DT contains `bi_tcxo_div2` and `bi_tcxo_ao_div2` fixed-factor clocks.
- Historical SP11 baseline CAMCC node used these divided clocks as its XO inputs.
- E002a/r3a/r3b camera overlay mistakenly supplied full-rate `RPMH_CXO_CLK` / `RPMH_CXO_CLK_A` instead.
- X1E CAMCC's MCLK table has `F(19200000, P_BI_TCXO, 1, 0, 0)`, so feeding 38.4 MHz directly creates the observed impossible parent-rate tree.

Next gate: correct CAMCC parent inputs to Golden `bi_tcxo_div2` / `bi_tcxo_ao_div2` and repeat this same rate-only test with no camera power.
