# E002b-r3g — Windows MCLK1 pad oracle

Date: 2026-08-27

## Question

Which X1E80100 TLMM pad must Linux select for the rear SP11 camera resource `cam_cc_mclk1_clk`?

## SP11 Windows evidence

A one-shot Windows boot was observed from SP7 using KDNET. With the target stopped after normal boot, the X1E TLMM control registers were read directly:

| Pad | TLMM control | Decode |
| --- | ---: | --- |
| GPIO96 | `0x00000244` | function 1 `cam_mclk`, no pull, drive code 1 = 4 mA, output enabled |
| GPIO97 | `0x00000244` | function 1 `cam_mclk`, no pull, drive code 1 = 4 mA, output enabled |
| GPIO98 | `0x000003c0` | not selected as camera MCLK in this state |
| GPIO99 | `0x00000200` | not selected as camera MCLK in this state |
| GPIO100 | `0x00000244` | X1E GPIO100 function 1 is `cam_aon`, not `cam_mclk` |

The installed SP11 rear-camera resource package already identifies its master clock as `cam_cc_mclk1_clk`. The installed front RGB and IR packages identify different camera clocks (`mclk4` and `mclk0` respectively), so the resource name is sensor-specific rather than generic.

## Linux contrast

Golden Linux after return from the Windows oracle read:

| Pad | TLMM control |
| --- | ---: |
| GPIO96 | `0x00000001` |
| GPIO97 | `0x00000001` |
| GPIO98 | `0x000003c0` |
| GPIO99 | `0x00000200` |
| GPIO100 | `0x00000001` |

Thus Linux r3f can enable the internal CAMCC MCLK1 branch at 19.2 MHz while GPIO97 remains GPIO/function 0 with pull-down and output disabled.

## Independent X1E80100 routing evidence

Qualcomm's 2026 Hamoa/X1E80100 camera pinctrl series defines:

- `cam_mclk0_default` on GPIO96;
- `cam_mclk1_default` on GPIO97;
- `cam_mclk2_default` on GPIO98;
- `cam_mclk3_default` on GPIO99;
- camera AON clock on GPIO100.

The Hamoa camera overlay also pairs `CAM_CC_MCLK1_CLK` with a camera default pinctrl whose MCLK pin is GPIO97.

Public references:

- `arm64: dts: qcom: hamoa: Add camera MCLK pinctrl`, v2, 2026-05-08: https://www.spinics.net/lists/kernel/msg6193734.html
- `arm64: dts: qcom: hamoa-iot-evk-camera-imx577: Add DT overlay`: https://www.spinics.net/lists/devicetree/msg898691.html

## Conclusion

**PROVEN for E002b-r3g:** rear `CAM_CC_MCLK1_CLK` must be routed to **GPIO97 / `cam_mclk`**.

For the first SP11 Linux correction, use the Windows-observed active electrical state exactly where Linux exposes matching pinconf controls:

- `pins = "gpio97"`;
- `function = "cam_mclk"`;
- `drive-strength = <4>`;
- `bias-disable`;
- `output-enable`.

Do not alter rails, reset, CCI routing/rate/address, sensor-ID transaction, CAMCC parent/rate, or CSI topology in the same experiment.
