# E004gg — actual Windows ARM64 flash-off instructions in an offline CPU emulator

**PASS:** This is new, fully offline instruction execution, complementary to E004gf's static control-flow review and the previously consumed E004gb normal live Windows trace. No new Windows boot, KDNET trace, camera capture, physical PMIC access, flash command, emitter activation, firmware install or Golden modification occurred. The imported Windows kernel services, Windows flash transport and PMIC register-update helper are **mocked in emulator memory**.

The existing `qccamflash8380.sys` and `qcpmic8380.sys` are each verified against the installed-image SHA-256 before their ORIGINAL machine-code bytes are mapped at their PE-preferred base in a temporary Unicorn AArch64 VM. The emulator executes the original flash command-wrapper RVA `0x4d58` and PMIC four-channel strobe callback RVA `0x285c0`. Only Windows logging/transport calls and the PMIC masked-write helper are intercepted. The Windows driver's real instructions compute its command/payload/register/mask/ordering and branch on injected return codes.

**Observed in the emulated original binary:** Flash wrapper `(0,0,0)` sends command `0x802f0fc8` with four zero payload bytes. A nonzero argument fixture verifies wrapper packing and catches an earlier incorrect hand-written expectation: wrapper `(1,0,1)` packs `[0,1,0,1]`, not `[1,0,1,0]`. The PMIC callback for OFF `(0,0,0,0)` requests `ee46` mask `80` value `00`, then `ee4e` mask `0f` value `00`; LED1 ON `(1,0,0,1)` instead requests `ee46`/`80` and `ee4e`/`09`. Injecting a failed result in the **first mocked helper** makes the original callback omit the second request; failing the **second** preserves both requests and returns an error. These are observed CPU branch/argument semantics, not measured changes in PMIC registers or physical LED current. No inference is made that successful PMIC module disable always extinguishes the emitter or that timer hardware enforces any physically safe duration.

Run from repository root:

```sh
python3 experiments/E004-front-ir-vd55g0/e004gg-windows-arm64-off-emulation/emulate_windows_off.py
python3 experiments/E004-front-ir-vd55g0/e004gg-windows-arm64-off-emulation/test_emulation.py
python3 experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/verify_result.py
```

The negative tests check hash drift, rejected malformed input/fault parameters, ON-path first/second helper errors, original OFF payload, and nonzero wrapper-argument packing. `evidence/RESULT.json` records only the modeled software requests, not proprietary binary bytes, image pixels or device data. Source images are read-only and remain in the existing local archive, **not committed**.

**Safety gate:** E004fs/E004ge stay BLOCKED. An emulated CPU, software-return-code injection and archived Windows trace cannot validate hardware-independent shutoff under a stuck sensor strobe or host crash, measured peak LED current, emitted pulse duration or calibrated optical irradiance. Do not install the uninstalled Linux flash patches or enable native IR based on this stage.
