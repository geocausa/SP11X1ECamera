# SP11 VD55G0 identity/revision probe

This module is a deliberately bounded diagnostic for the first Linux VD55G0 live gate.

It is **not** the ST camera driver and uses the private compatible
`microsoft,sp11-vd55g0-idprobe`, so the pristine ST driver cannot bind to the
E004b candidate node.

The module:

- keeps reset asserted while resources are established;
- requests CAM_CC_MCLK0 at 19.2 MHz and checks the achieved rate;
- enables VDDIO, VCORE, then VANA in the Windows D0 ordering;
- checks 1.800 V / 1.152 V / 2.800 V Linux setpoints before releasing reset;
- deasserts reset;
- performs only two combined I2C address-pointer/read transactions:
  register 0x0000 (model) and register 0x0004 (revision);
- logs raw bytes plus little- and big-endian interpretations;
- reasserts reset and powers VANA, VCORE/VDDIO and MCLK off before probe returns.

There are no sensor register-data writes, patch/firmware upload, sensor boot or
configuration calls, V4L2 registration, streaming operations, or illumination
controls.

The 5 ms inter-step delay is a conservative Linux safety delay, **not a
Windows-parity timing claim**. The Windows AeoB DELAY unit remains unresolved.
