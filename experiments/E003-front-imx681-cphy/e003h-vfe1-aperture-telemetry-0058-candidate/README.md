# E003h 0058 candidate — read-only VFE1 aperture telemetry

This candidate reuses the exact consumed 0057 CAMSS and mode2 sensor modules. It changes no camera programming. In addition to the persistent RT-CDM observer, a required root observer maps physical VFE1 `0x0ac71000..+0x3fff` read-only and preserves full active snapshots plus low-register transitions. One helper invocation only; no retry; mandatory Golden reboot.
