# Rear OV13858 QTI power classification

Source is the local read-only Windows oracle file `com.surface.sensormodule.rfc_ov13858.bin`, SHA-256 `f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14`. No vendor blob is committed.

The v3.4 QTI `sensorDriverData` header points to six-entry power-up symbol id 9 and six-entry power-down symbol id 10. Each `powerSetting` record is three little-endian u32 values: config type, config value, delay.

Power-up id 9 decodes to:

1. type 8, value 0, delay 1 — RESET asserted;
2. type 1, value 1, delay 1 — VANA on;
3. type 2, value 1, delay 1 — VDIG on;
4. type 3, value 1, delay 1 — VIO on;
5. type 0, value 24000000, delay 10 — MCLK request in generic sensor data (board resource oracle overrides actual Denali MCLK to proven 19.2 MHz);
6. type 8, value 1, delay 30 — RESET released.

Power-down id 10 decodes to:

1. type 0 / MCLK off;
2. type 8 / RESET asserted;
3. type 4 / VAF off;
4. type 3 / VIO off;
5. type 2 / VDIG off;
6. type 1 / VANA off.

Public CamX sensor-schema documentation identifies config types as MCLK, VANA, VDIG, VIO, VAF, RESET, STANDBY. The rear sensor's power-up sequence therefore requests only VANA/VDIG/VIO; VAF is not sensor power-up ownership.

Voltage/resource correspondence from the board resource oracle is mechanically natural:

- VIO = LDO6_M = 1.8 V;
- VDIG = LDO1_M = 1.2 V;
- VANA = LDO5_M = 2.8 V;
- VAF = LDO16_B = 2.9 V.

E002k-A tests the one remaining hardware question: can the accepted rear identity/stream path operate with LDO16_B never voted by the OV13858 driver?

Public schema references:
- https://device.report/m/cd4258c496fa3bc2d4f36b3fbfc6b64aa5b813f834017254d6f9e878fe323c66.pdf
- https://gitcode.csdn.net/69e3271c0a2f6a37c5a0b944.html
