# Windows oracle methodology

Windows on the same SP11 is the reference for hardware behaviour. The Linux implementation must be independently written.

## Static evidence

Use read-only inspection where possible:

- SYSTEM hive hardware IDs and selected driver packages;
- ACPI tables/resources;
- camera INF and extension INF metadata;
- hashes and structural observations from Surface/QTI configuration packages;
- firmware/resource package names and public symbol/string vocabularies.

Do **not** commit the proprietary files themselves.

The selected sensor packages expose Qualcomm Chromatix metadata including fields related to `sensorSlaveAddress`, I2C frequency, power settings, resolution/mode data, stream configuration, lane assignment and C-PHY/D-PHY combo mode. Board-resource packages expose clocks, GDSCs, GPIO/delay resource classes and PMIC vote names.

## Dynamic evidence

For each sensor, collect the smallest possible Windows trace:

1. cold/idle baseline;
2. open one camera only;
3. request one known mode;
4. allow a short stable stream;
5. alter one control if needed (exposure/gain);
6. stop and close;
7. return to idle.

Derive power-resource order and delays, CCI/I2C bus/address, sensor-identification sequence, MCLK rate, reset/standby polarity, CSI PHY/link configuration, mode/register sequence, and stream-on/off lifecycle.

Use SP7/KD only when higher-level observation cannot establish a fact cleanly.

## Clean-room boundary

Allowed repository material: independently written code, register traces, resource/mode tables derived from observation, hashes, filenames, field names and experimental conclusions.

Do not redistribute Microsoft/Qualcomm binaries or proprietary tuning payloads.
