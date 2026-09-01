# E003h 0073 request6 offline oracle

Accepted offline only. The exact Windows request6 steady pair is a 0x958 main list plus a 0x8000 DMI slot. After zeroing the already-proven dynamic IQ holes and per-stream period_cfg, request6 has the same command skeleton as requests4/5.

Request5 -> request6 changes: 23/24 dynamic register fields and DMI payloads LSC0, LSC1, GIC0, GTM0.

A request6 capsule was built locally with request_id 6 using the existing materializer contract. Capsule SHA256 `f9b6b6bef1d13cafb27d4ff9af6f6d36abe6643aff512dcd108da62ef8300647`; raw Windows bytes and capsule stay local/untracked. No Linux request6 runtime is authorized or executed.

The attempted Windows trigger-struct breakpoint did not fire; no trigger vector is claimed. The remaining producer task is to capture/derive the exact common IQ trigger inputs and reproduce request6 from Chromatix rather than from the captured request6 payload.
