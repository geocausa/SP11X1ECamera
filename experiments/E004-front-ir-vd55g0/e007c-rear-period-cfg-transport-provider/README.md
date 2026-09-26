# E007c — rear VFE680 PERIOD_CFG transport-state provider

Parent Git: `d5a5c525` (E007b BFStats25 compile PASS).

Status: **STAGED / COMPILE-ONLY**.

## Purpose

Close the final startup register materialization contract, VFE680 `PERIOD_CFG` at `0x008C`, at the boundary actually proven by Windows.

This is **not** an IQ producer. Existing same-SP11 E003h evidence proves:

- the value is already populated before qccamisp DEVICE_START / IFE 0x803 reaches the observed KMD handler;
- the downstream KMD transport does not mutate it;
- each start has two logical opaque caller values;
- packet 0 uses value 0;
- packets 1, 2 and 3 use one shared value 1;
- the exact values vary between starts and therefore must never be frozen into Linux.

## Interface correction

E006m intentionally exposed `period_cfg` through its generic scalar callback, but that callback receives only `(ctx, reg)`. It therefore cannot express the proven packet-dependent mapping.

E007c adds a packet-aware startup wrapper:

- explicit `e007c_period_cfg_state` containing two opaque values plus a validity mask;
- `e007c_period_cfg_lookup(..., packet, reg, value)`;
- packet mapping `0 -> value[0]`, `1/2/3 -> value[1]`;
- all non-period registers delegate unchanged to the existing E006m resolver.

This keeps packet identity explicit and avoids encoding it in hidden mutable context.

## What this closes

On compile PASS, all **714/714 startup register materialization contracts** have a concrete clean-room provider boundary.

That does **not** mean camera-stack parity is complete. The Linux side still needs the upstream transport-state producer that supplies the two period values from the equivalent stream/request state; E007c deliberately leaves that dependency explicit.

Other remaining parity work is primarily live DMI/IQ/3A state production and non-submitting integration.

## Safety

No captured period value is embedded. No module install/load, camera access, MMIO, DMI submission or RT-CDM FIFO submission is authorized by this checkpoint.
