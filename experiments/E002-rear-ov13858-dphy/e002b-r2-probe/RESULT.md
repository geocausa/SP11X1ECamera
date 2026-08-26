# E002b-r2 result — SAFE FAIL at regulator permission gate

r2 booted normally with the entire FullIO v19c Golden system intact. The candidate-initrd probe module loaded and matched the rear client at `1-0010`, but the first attempted operation was rejected before any camera rail or clock changed:

`sp11-ov13858-probe 1-0010: error -EPERM: set LDO6_M 1.8 V failed`

## Safety / regression result

- Wi-Fi UP and associated to GEOCA;
- MultiMedia1 Playback present;
- MultiMedia3 Capture present;
- existing Golden PM8550-B provider bound normally;
- both isolated camera-only RPMh providers bound normally;
- all four camera rails remained 0 users / 0 mV;
- MCLK1 remained enable count 0;
- no sensor I2C identity transaction occurred;
- no CSI endpoint or stream existed.

Therefore r2 did **not** electrically power the camera. The isolation architecture worked as intended.

## Exact cause of `-EPERM`

In this v4 regulator core, `regulator_check_voltage()` requires `REGULATOR_CHANGE_VOLTAGE` in the regulator constraint valid-ops mask. OF parsing sets that bit only when `constraints->min_uV != constraints->max_uV`.

- r1/r2 isolated rails intentionally had no min/max constraints -> both zero -> voltage changes forbidden -> `-EPERM`.
- original broken E002b used fixed min=max constraints -> `apply_uV=true`, causing registration-time voltage synchronization and the PM8550-B provider failure.

The safe next experiment is a no-sensor constraint gate with **max-only** constraints:

- min_uV remains 0;
- max_uV is the Windows voltage for each rail;
- min != max -> `REGULATOR_CHANGE_VOLTAGE` allowed;
- both min and max are not nonzero -> `apply_uV` remains false;
- provider registration should therefore remain electrically inert.

Only after that gate passes should the rear identity probe be retried.
