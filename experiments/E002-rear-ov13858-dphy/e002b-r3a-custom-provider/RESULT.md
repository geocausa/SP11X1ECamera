# E002b-r3a result — PASS

Provider-only one-shot boot succeeded.

Resolved command-db resources:
- `ldob16` → `0x00041400`, target 2.9 V
- `ldom5` → `0x00041500`, target 2.8 V
- `ldom1` → `0x00042000`, target 1.2 V
- `ldom6` → `0x00040d00`, target 1.8 V

Kernel log confirmed all four regulators registered and the provider reported `4 rails, no votes sent`.

Acceptance checks:
- provider bound to `/soc@0/rsc@17500000/camera-rpmh-regulators`;
- no sensor client was present;
- no OV13858 probe module was loaded;
- CCI/CAMSS/CAMCC runtime-suspended;
- Wi-Fi associated to GEOCA;
- `MultiMedia1 Playback` present;
- `MultiMedia3 Capture` present;
- saved GRUB default remained `sp11-audio-fullio-v19c`;
- only known `casper-md5check.service` failure remained.

This validates the external camera-only RPMh-provider architecture and supersedes the failed DT-only r1/r2/r2a regulator approaches.
