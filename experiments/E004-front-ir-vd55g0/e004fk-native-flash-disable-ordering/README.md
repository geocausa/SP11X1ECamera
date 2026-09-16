# E004fk: disable channels before changing trigger mode

**PASS offline; both flash-driver patches remain uninstalled.**

Review of the actual register helper found a second issue outside E004fg's
callback model: set_flash_strobe changes trigger configuration before it clears
the channel enable bits. Switching an armed channel from hardware to software
trigger could briefly drive the output. E004fg inherits this helper behavior;
its callback tests did not cover register ordering. E004fg alone is therefore
not an adequate integration candidate.

Patch 0002 disables this LED's complete channel mask first and records the
successful disable. It then configures every channel's trigger and enables the
mask only after all writes succeed. Other LEDs' channel bits are preserved.
A failure after disabling leaves the LED cached as disabled; failure of the
initial disable returns immediately without changing trigger registers. A bus
error cannot establish physical off-state and is not claimed to do so.

This is a generic qcom-flash fix layered on E004fg's patch 0001. The source anchor,
installed module tree, device tree and Golden boot payload remain unchanged.
No sensor GPIO or emitter register was touched during this experiment.

## Validation

- The actual helper extracted from the E004fg source reproduces armed-mode
  writes in the offline register model.
- Patched helper passes 15 cases, normally and with address/undefined-behaviour
  sanitizers: software/hardware mode, enable/disable, initially armed/disarmed,
  unrelated-channel preservation and seven injected register-operation failures.
- E004fg's 16 callback contract cases also pass with the combined source,
  normally and with sanitizers.
- Both patches reapply byte-exactly to the recorded upstream source.
- Isolated module builds cleanly with W=1; strict checkpatch reports zero errors,
  warnings or checks (signoff check disabled for this unsubmitted development patch).

The register model tracks whether configuration changes while channels remain
enabled. It does not emulate optical emission, regmap concurrency or partial bus
transactions. No endurance, physical pulse, suspend/resume or failure-of-power
claim follows from these tests. Other upstream current-accounting failure cleanup
is unchanged and remains a separate review item.

## Reproduce

Apply patches 0001 then 0002 from src/front-ir-vd55g0/illumination to a disposable
copy of the hash-pinned original drivers/leds/flash/leds-qcom-flash.c. Put the
result in this experiment's build/source, with a Makefile containing
`obj-m += leds-qcom-flash.o`.

Run test_strobe_registers.py with --baseline pointing to E004fg's source,
--patched pointing to this source and --output to an evidence JSON path. Run
E004fg/test_strobe_contract.py with the original upstream source as --baseline
and this source as --patched. Build the isolated module against the prepared
Golden build anchor using W=1. Exact hashes and results are in evidence/RESULT.json.

## Next gate

E004fh/E004fj establish installed Windows current and active channel pairing.
Before a Linux illumination experiment, establish the Windows-used sensor edge
shifts, exposure envelope, PMIC trigger configuration and timeout behavior.
The 700 mA setting alone is not a pulse-duration or duty-cycle specification.
Golden FullIO v19c remains permanent; Linux SecureISP remains inactive.
