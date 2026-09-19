# E004gf — Windows ARM64 flash shutdown control flow and offline fault-model analysis

**PASS: static disassembly against the original hash-pinned Windows ARM64 drivers, reconciled with E004gb's already collected live trace; offline software-only fault-path model.** This is a new, strictly offline identity. It does not repeat E004gb's consumed Windows boot, debugger hooks, camera capture, or flash requests. No Windows driver was executed by this stage; the word "dynamic" here means the previously recorded E004gb real Windows execution evidence plus new offline fault-model execution, NOT a new live fault-injection experiment.

## Exact code-level findings

The installed archive's `qccamflash8380.sys` and `qcpmic8380.sys` are SHA-256 checked before disassembly. The type-0 Windows flash OFF path at flash RVA 0x5c88..0x5cec sends the mode command at RVA 0x5cd0, then **unconditionally sends an OFF command** at RVA 0x5ce4, and combines their returned status words. Static disassembly at PMIC RVA 0x28678..0x287c8 shows the PMIC OFF handler attempts the **module bit-7 update at ee46 first**; its nonzero return branches immediately to failure, bypassing the subsequent ee4e channel-mask update. A successfully returned module-off request can still be followed by a failed channel-off request. This is an ordering/error-control-flow observation, not evidence of what physical LEDs do.

E004gb's **separate, previously completed** bounded OEM preview saw Windows request module `ee46: 80→00` before channels `ee4e: 09→00`, with recorded successful helper return codes. This supports the normal request order but does **not** exercise an injected hardware fault; its after-call debugger buffer is not a physical PMIC readback.

The bounded offline fault-path model exercises four combinations of software success/failure for the two requested writes: if module-off fails, channel-off is **not attempted** by this PMIC handler; if it succeeds and channel-off fails, a channel enable mask remains in the model. No simulation result is a claim that the actual physical emitter remains on: the actual circuit, PMIC timer and effect of module-disable are unmeasured. If the module bit actually cuts LED power, failed channel clearing after successful module-off might not cause emission, but it can leave channel configuration armed for later module enable; the precise hardware consequence remains to be proven. Conversely, failure of the first write gives this handler no second chance to request channel-off. No conclusion is drawn about other independent PMIC hardware protective actions.

The previously developed **UNINSTALLED** Linux patch `0004-qcom-flash-best-effort-error-disarm.patch` tries channel disarm and module disable on software failure rather than short-circuiting both attempts, but neither that patch nor the Windows flow can guarantee LED-off if bus writes fail or the host crashes.

## Reproduce

From the repository root run:

```sh
python3 experiments/E004-front-ir-vd55g0/e004gf-windows-flash-failure-off-static-dynamic/verify_shutdown.py
python3 experiments/E004-front-ir-vd55g0/e004gf-windows-flash-failure-off-static-dynamic/test_shutdown.py
python3 experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/verify_result.py
```

The first command verifies exact file hashes, presence and order of relevant ARM64 call/branch/register instructions, and the existing normal live trace's result contract. The negative-path test deliberately substitutes a NOP for each checked instruction in memory and verifies the static anchors reject the changes, then runs the four fault-model cases. The independent E004gb verifier checks the original immutable archives without booting Windows.

**Remaining distinction:** These findings strengthen the software fault-path diagnosis. They cannot calibrate optical irradiance/current, measure physical LED pulse width, independently validate PMIC timer enforcement, or demonstrate autonomous host-failure/stuck-strobe shutdown. E004fs/E004ge illumination gates remain BLOCKED; no LED, camera, boot, PMIC, firmware, protected Golden, or PAM/login mutation occurred.
