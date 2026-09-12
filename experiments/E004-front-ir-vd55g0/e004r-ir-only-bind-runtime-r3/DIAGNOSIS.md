# E004r runtime outcome — preflight-only I2C adapter-number drift

E004r never crossed the camera-attempt boundary.

The candidate boot itself was valid and is preserved in the previous-boot journal. PREARM, INSTALL and ARM all passed. On the candidate boot, the runtime preflight loaded only i2c_qcom_cci and then looked specifically for /sys/bus/i2c/devices/2-0060.

The same physical IR DT node appeared as adapter instance 3 at address 0x60 on that boot (3-0060), so the hard-coded 2-0060 test failed.

No RUNTIME-PREFLIGHT.txt was written.
No ATTEMPT1-CONSUMED.marker was written.
No qcom_camss module was loaded.
No sp11_vd55g0 module was loaded.
No sensor write occurred.
No direct stream harness ran.
No receiver programming, capture, or illumination occurred.

This is an infrastructure naming issue only: Linux I2C adapter numbering is not a stable identity for this disposable graph.

SP11 was immediately returned to Golden and the E004r candidate was retired.

Next gate: identify the IR device dynamically by DT compatible microsoft,sp11-vd55g0 plus I2C address 0x60. The kernel test harness must likewise locate the matching I2C client by OF compatible/address instead of the bus-generated device name.
