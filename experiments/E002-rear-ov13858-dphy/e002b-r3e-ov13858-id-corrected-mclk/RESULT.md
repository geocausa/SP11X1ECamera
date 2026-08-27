# E002b-r3e result — corrected CAMCC OV13858 identity probe

Status: SAFE BUS-LEVEL FAILURE / QUARANTINE

## Result

The accepted r3d DTB (correct X1E CAMCC `bi_tcxo_div2` / `bi_tcxo_ao_div2` parents) was reused byte-for-byte. The accepted isolated RPMh provider and previously-vetted OV13858 identity shim were loaded from the candidate-only initrd.

Runtime crossed the complete known rear-camera power/clock sequence:

1. LDO6_M enabled at 1.8 V
2. LDO1_M enabled at 1.2 V
3. LDO5_M enabled at 2.8 V
4. LDO16_B enabled at 2.9 V
5. MCLK1 accepted at the Windows-derived 19.2 MHz rate
6. reset-release path completed far enough to attempt the CCI transaction
7. first OV13858 chip-ID transfer returned `-ENXIO` (`-6`)
8. teardown disabled LDO16_B, LDO5_M, LDO1_M, LDO6_M cleanly

Post-probe all four custom camera regulators reported `state=disabled` and `num_users=0`. FullIO audio and Wi-Fi remained healthy.

## Boundary

The experiment has moved beyond regulator and MCLK bring-up. The remaining failure is a CCI/I2C NACK boundary. Before another powered Linux attempt, verify from the Windows oracle:

- exact rear sensor slave address / address representation
- CCI controller + master selection and bus frequency
- GPIO110 reset polarity, initial state, release state, and delays
- first successful identification transaction/register sequence

Do not infer these from another X1E board. If the static Surface/Qualcomm blobs do not settle them unambiguously, use SP7 KD into a one-shot SP11 Windows boot and trace `\\_SB.CAMS` D0 bring-up.
