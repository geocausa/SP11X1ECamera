# E003c pre-runtime result

Status: **READY FOR ONE-SHOT NATIVE-BIND TEST**.

## Candidate

- native external V4L2 driver: `imx681.c`, bind-only;
- module SHA-256: `411c71a3e4d70ecdde6a80e41cba6f6a4a279af79b3076c20061e558ee5da67c`;
- srcversion: `E9DD300C13909125CA27C6E`;
- exact Golden vermagic;
- 38/38 imported symbol CRCs exactly match Golden;
- candidate DTB: `a698603969880be9ac986e543fe0c772a75551cfd0d1d27422fd84375e48da9b`;
- reproducible initrd A/B: `fd68e7299a245b80e78fde044da62924885fe68396f2c152f13caf04e3d0c079`.

## Hard gates

- versus E003b DT: exactly eight changed DTS lines, all confined to node/compatible/supply naming;
- no front endpoint or remote-endpoint;
- no mode register table;
- no `cci_write()` or multi-write call;
- no executable-code reference to sensor MODE_SELECT `0x0100`;
- `.s_stream(1)` returns `-EOPNOTSUPP` before PM/I2C work;
- modes 0..4 are metadata only;
- initrd delta versus accepted R3 is exactly five entries.

## Runtime acceptance

Require:

1. both IDs: `0x0004 = 0x0aff` and `0x0016 = 0x0681`;
2. native `imx681` driver bound to CCI1/master1 client;
3. V4L2 subdevice bind completes;
4. runtime PM returns MCLK4/LDO3_M/LDO7_B to zero and GPIO237 reset-low;
5. a deliberate stream attempt is blocked with `-EOPNOTSUPP` and does not alter PM/electrical state;
6. no front CAMSS/CSIPHY2 media link; no C-PHY programming;
7. Wi-Fi, audio, touch and rear camera remain healthy;
8. return to byte-exact Golden.
