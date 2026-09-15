# E004ev: pattern framing with averaging bypass

Only sensor behavior change from E004eu: DARKCAL_CTRL=2 (BYPASS_DARKAVG),
replacing full dark-calibration bypass 0. ST UM2829 Rev 2 table at page 56
register 0x032c documents this mode. Hypothesis: the block retains removal of
leading dark rows, preserving 644x604 framing while bypassing averaging.
E004eu contained eight leading dark/reference-like rows followed by 596 exact
horizontal ramps, then stalled. CSI line count was not measured; the height
explanation remains an inference to test.

Four frames, one stream attempt, standard V4L2 test_pattern=1, digital_gain=256.
Same firmware, exposure, DT, CAMSS and disabled GPIO outputs. Require the existing
capture/PM/kernel gates, then offline pattern analysis, Golden return and retirement.

Source: https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf
