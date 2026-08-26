# E002b-r3e — OV13858 identity probe on accepted corrected-MCLK DT

r3e reuses the **exact accepted r3d DTB byte-for-byte**. There is no DT change from the no-power MCLK PASS.

Accepted r3d facts:
- CAMCC uses Golden `bi_tcxo_div2` / `bi_tcxo_ao_div2` parents;
- MCLK1 branch/source are 19.2 MHz;
- `clk_set_rate(19.2M)` succeeds;
- all camera rails remain isolated;
- Wi-Fi/audio remain intact.

The only r3e change is the candidate-initrd payload: replace `sp11_mclk_diag` with the already-vetted `sp11_ov13858_probe` while retaining the accepted camera-only RPMh provider and provider-bound loader guard.

Exact artifacts:
- kernel SHA256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a` (Golden)
- DTB SHA256: `4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233` (exact r3d PASS DTB)
- provider SHA256: `ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`
- OV13858 probe SHA256: `c945eb7e3f8aa4c142d4bf2f86c996fcd1b858764855d09518654b414de698be`
- initrd SHA256: `88940f9252480db2393b4cde80d6452f140470657d3b782666c5b6da65f48344`

Expected sequence remains Windows-derived:
LDO6_M 1.8V → LDO1_M 1.2V → LDO5_M 2.8V → delay → LDO16_B 2.9V → MCLK1 19.2MHz → release GPIO110 reset → delay → CCI bus1 address 0x10 register 0x300a, expected three-byte ID `0x00d855` → teardown.

No CSI endpoint and no streaming are present.
