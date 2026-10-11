# Standard rear lens regulator: first source investigation, 2026-10-11

Status: source lead only; root cause and replacement hardware qualification OPEN.
No DT/kernel/module/reboot changes were made in this investigation.

## Observations

The failed v1 builder at commit d49b2612 added PM8550 LDO16 with fixed 2.9 V
constraints AND `regulator-initial-mode = <0x03>`, plus a regulator-output
consumer. The project records two boot hangs, including one with cameras off.
Those runs do not isolate which registration/power operation hung.

The retained Linux qcom-rpmh-regulator.c source has these behaviours:

- Initial enabled state is -EINVAL (unknown), not false.
- Voltage selection is cached while that state is unknown. Consequently fixed
  voltage constraints alone do not demonstrate an immediate voltage vote.
- Mode selection calls rpmh_regulator_vrm_set_mode_bypass, which sends its
  request with wait_for_ack=true, even before a consumer enables the rail.
- Enable OR disable from unknown state with a cached voltage first sends that
  voltage synchronously, then the enable/disable request.
- The camera-only workaround has no initial-mode registration request and
  sends voltage, mode and enable together only on its consumer's enable path.

This gives a plausible early-registration RPMh acknowledgement lead, not proof
that mode 0x03, voltage, the consumer or the standard provider is defective.
Source inspected: 02-kernel/e003i-front-production-src/drivers/regulator/
qcom-rpmh-regulator.c on SP11; recheck against the chosen current upstream base.
The v1 source is retained by git history. Current pstore directory is empty,
so there is no retained panic record establishing the exact blocked call.

## Smallest discriminating test series (not armed)

1. Verify working Golden recovery and persistent early kernel logs for a hang
   before systemd. An ordinary systemd watchdog cannot establish this recovery.
2. Source-pin a fresh camera-off candidate adding the standard LDO16 node with
   its voltage constraints, omitting initial-mode and omitting the consumer.
   Log provider registration and first RPMh request/return; inspect whether
   disable-unused later emits a voltage/disable request.
3. Separate fresh candidate adds the output consumer while still camera-off;
   observe probe/deferred-probe and enable state without forcing a rail vote.
4. Only after repeatable cold boots, invoke the consumer once using standard
   regulator paths; trace voltage/mode/enable ordering and bounded completion.
5. Compare an initial-mode-only variant only after early-boot recovery/logging
   is established. Never bundle unrelated kernel/DT changes or repeat an
   already-consumed identity.
6. Final solution must use the standard regulator/provider model and an
   actuator subdevice with runtime PM; the temporary camera-only provider and
   raw-I2C bridge are excluded from the curated upstream series.

Do not modify a generic RPMh driver to match the workaround before the blocked
operation and required hardware semantics are independently established.
