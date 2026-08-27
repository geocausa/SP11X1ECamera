# E003b — front IMX681 electrical identity only

Goal: prove the physical Sony IMX681 identity on SP11 without creating any CSI/C-PHY endpoint or V4L2 sensor.

## Windows-derived D0 sequence

1. common camera domain enabled by the CAMCC/CCI consumers;
2. GPIO237 held low (reset asserted);
3. MCLK4 set/enabled at 19.2 MHz;
4. LDO3_M = 1.8 V;
5. LDO7_B = 2.8 V;
6. AeoB delay 1 (identity shim uses conservative 1 ms);
7. GPIO237 high (reset released);
8. AeoB delay 10 (identity shim uses conservative 10 ms);
9. CCI1/master1 FAST (400 kHz), Linux address 0x10;
10. read 16-bit register 0x0004 and require value 0x0aff.

D3 is reset low, delay, MCLK4 off, LDO7_B off, LDO3_M off.

## Dynamically proven Windows pins

- GPIO100 = MCLK4/cam_aon pad;
- GPIO235/236 transition idle -> active -> idle with the targeted Surface Camera Front reader and are CCI1/master1;
- GPIO237 transitions low -> high -> low with the same reader and is reset.

## Hard isolation boundary

E003b adds no front `port`, no endpoint, no `remote-endpoint`, and no C-PHY configuration. The probe module contains no V4L2/media code and powers down immediately after the two-byte identity read. CSIPHY2 must remain unused.
