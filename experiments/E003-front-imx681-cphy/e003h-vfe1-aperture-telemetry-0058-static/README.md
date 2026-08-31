# E003h 0058 — VFE1 aperture telemetry

0058 changes no camera programming. It reuses the exact consumed 0057 CAMSS/sensor behavior and adds a persistent read-only `/dev/mem` sampler of physical VFE1 `0x0ac71000..0x0ac74fff` while the bounded helper owns the powered front pipeline.

The target is the unresolved Windows-live VFE680 low-TOP cluster: `diag_config`, `core_cfg_3`, stats throttle 0..2, and `core_cfg_4..6`. The sampler also records the complete 0x4000 aperture so later comparisons do not require another run. No Linux register value is changed by this gate.
