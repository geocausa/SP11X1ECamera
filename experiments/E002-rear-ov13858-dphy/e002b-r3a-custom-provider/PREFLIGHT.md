# E002b-r3a — camera-only RPMh provider gate

Purpose: prove that the four Windows-derived rear-camera RPMh resources can be resolved and exposed as isolated Linux regulators without touching the Golden regulator providers and without sending any RPMh votes.

## Inheritance
- Kernel: exact FullIO v19c / `7.1.5-sp11-render-parity-v4+` payload.
- DT base: literal deployed FullIO v19c DTB.
- Camera substrate: accepted E002a CAMCC + CCI0 + CAMSS infrastructure.
- Golden DT statements removed: **0**.
- Golden `/lib/modules` additions: **0**.

## r3a DT delta
Adds one platform device under `/soc@0/rsc@17500000`:
`microsoft,sp11-camera-rpmh-regulators`

Its four child resources are:
- `ldom6` → 1.8 V
- `ldom1` → 1.2 V
- `ldom5` → 2.8 V
- `ldob16` → 2.9 V

There is deliberately **no sensor node, reset GPIO, MCLK consumer, regulator consumer, CSI endpoint, or stream path** in r3a.

## Provider behavior
`sp11_camera_rpmh_regulator.ko` uses exported `cmd_db_read_addr()` to resolve resources and registers standard Linux regulator devices using programmatic constraints with `apply_uV=false`.

RPMh writes exist only in regulator consumer operations (`set_voltage` while enabled, `enable`, `disable`). r3a has no consumers, so successful probe must send **zero votes**.

Module SHA256:
`ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`

DTB SHA256:
`11164e2c8e49bce4619294c21c9933e7bbd9188d323ca88bef290c458fa5f744`

Candidate initrd SHA256:
`c95592fc7e7a007da76fc53e65d4974ca4ba9b7498fc41bf86e07e0dfa037d19`

The initrd preserves the Golden uncompressed cpio byte-for-byte through its original trailer offset and has exactly four semantic path deltas: the provider module, its directory, one init-top loader, and the explicit ORDER entry.

## Acceptance
- provider module loads and binds;
- all four command-db resources resolve;
- all four regulators register;
- no provider registration errors;
- no sensor device exists;
- camera MCLKs remain disabled;
- Wi-Fi remains associated;
- FullIO playback and capture remain present;
- existing Golden `regulators-0` remains bound;
- saved GRUB default remains `sp11-audio-fullio-v19c`.
