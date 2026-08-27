# E002k-D-R2 result — ACCEPTED

The accepted E002k-C rear camera path operates unchanged on the stock kernel's native PM8010-M regulator provider. The temporary `microsoft,sp11-camera-rpmh-regulators` device/module is absent.

Runtime proof:

- built-in `regulators-8` bound before the unchanged accepted OV13858 module;
- OV13858 bound successfully (I2C adapter number drifted to `3-0010`, which is not a hardware change);
- native `dovdd`/`dvdd`/`avdd` rails are LDO6_M 1.8 V / LDO1_M 1.2 V / LDO5_M 2.8 V;
- one standard sensor-generated color-bar frame was exactly 14,321,824 bytes with SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`, byte-identical to the accepted E002j/k reference;
- with test pattern disabled, 16/16 normal frames arrived, sequences 0..15, all 14,321,824 bytes, measured mean cadence ~30.065 fps;
- sensor runtime PM returned suspended/usage 0;
- all three native PM8010 camera regulators returned disabled/users 0;
- MCLK1/CSIPHY clocks returned to enable count 0;
- no camera/CAMSS/CSIPHY fault appeared;
- Wi-Fi, audio playback and audio capture remained healthy;
- Golden remained saved default and the one-shot was consumed.

Conclusion: **native PM8010-M regulator integration is accepted. The temporary camera RPMh provider is retired from the rear-camera design.**

Next: integrate the proven OV13858 + generic X1E camera infrastructure + Denali rear topology into the isolated exact-Golden kernel source and compile it as a clean patch series. Runtime kernel integration remains isolated until compile/source audits pass.
