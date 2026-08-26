# E002a preflight — CAMSS + CCI0 infrastructure only

E002a deliberately adds **no sensor node**, **no camera GPIO/pinctrl state**, and **no sensor regulator/MCLK sequencing**.
It only adds the infrastructure required for a later rear-camera probe:

- X1E80100 CAMCC
- CCI0 with two empty 1 MHz I2C master buses
- integrated X1E80100 CAMSS (the implementation already present in the deployed v4 kernel)

The CAMSS graph has an empty `ports` container, so the v4 driver has no external async endpoint to bind in E002a.

## PHY supplies

The deployed v4 CAMSS implementation uses the older shared-supply binding. For this rear-only experiment that shared pair is deliberately mapped to the X1E CSI0/1 rail pair used by CSIPHY1:

- `vdd-csiphy-0p8-supply = vreg_l2c_0p8`
- `vdd-csiphy-1p2-supply = vreg_l1c_1p2`

No CSIPHY is enabled until streaming, which E002a does not perform.

## Artifacts

- Golden v19c DTB SHA256: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`
- E002a overlay DTBO SHA256: `f761cd11ab221da22e2ffa23d1b395824ffc663154b94bd2c6033ccf73c813e5`
- E002a merged DTB SHA256: `dc229b994bd01cccae0d282166b243317f673aa55a84cc9e3da768458cdb6117`

A sorted decompile diff (`base-to-e002a.diff`) contains no removed Golden lines. The only additions are the three infrastructure nodes and their `__symbols__` entries.
