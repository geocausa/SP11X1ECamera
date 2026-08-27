# E002e rear transport-mode audit

## Exact Windows oracle input

Local-only source: the installed Surface rear QTI sensor package `com.surface.sensormodule.rfc_ov13858.bin`, SHA-256:

`f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14`

No proprietary blob or full vendor register table is committed.

`tools/qti_sensor_summary.py` mechanically decodes three rear RAW10 / VC0 / 30-fps modes, all with output-pixel-clock metadata `474240000 Hz`:

| mode | output | crop start | QTI line length | QTI frame length |
|---:|---:|---:|---:|---:|
| 0 | 4076x2806 | 0,0 | 1122 | 3214 |
| 1 | 4064x2286 | 6,260 | 1122 | 3214 |
| 2 | 3736x2802 | 170,2 | 1122 | 3214 |

With RAW10 over four D-PHY lanes, `474.24 MHz * 10 / 4 = 1.1856 Gbit/s/lane`, hence DDR link frequency **592.8 MHz**.

The mode-0 vendor register block contains 207 operations. Compared by final register value against upstream's `mipi_data_rate_1080mbps` + `mode_4224x3136_regs`:

- Windows unique registers: 207;
- upstream merged unique registers: 202;
- shared registers: 199;
- identical shared values: 180;
- changed shared values: 19;
- Windows-only addresses: 8;
- upstream-only addresses: 3.

Key factual deltas include:

- PLL: `0x0300 07->05`, `0x0301 01->00`, `0x0302 c2->f7`;
- output: `0x3808/09 = 0x0fec` = 4076, `0x380a/0b = 0x0af6` = 2806;
- static VTS: `0x380e/0f = 0x0c88` = 3208;
- line-length register remains `0x380c/0d = 0x0462` = 1122;
- MIPI timing: `0x4837 0e->0d`.

The QTI metadata frame length (3214) differs from the static mode-table VTS (3208). This is not treated as a contradiction: the normal OV13858 lifecycle writes VTS through the frame-length/VBLANK control after the static mode table. E002e does not program either value and leaves reconciliation for the Surface-mode register gate.

## E002e scope decision

E002e changes **transport metadata only**:

- sensor endpoint gains `link-frequencies = <592800000>`;
- native driver's full-resolution link-frequency control changes from 540 MHz to 592.8 MHz, producing V4L2 pixel-rate `474240000` by the driver's existing RAW10/four-lane formula;
- the driver validates at probe that the endpoint is D-PHY, four lanes, and exactly 592.8 MHz;
- a DT-selected no-stream guard rejects `.s_stream(1)` with `-EOPNOTSUPP` **before** runtime-PM power-up.

The E002c PLL arrays and all sensor mode register arrays are byte-identical in E002e. No Surface crop or PLL register programming is introduced yet.

Next gate after E002e: encode the focused Windows-derived Surface mode/PLL delta, initially mode 0 only, while retaining the no-stream guard until register programming can be validated in standby.
