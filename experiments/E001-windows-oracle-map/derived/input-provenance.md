# E001 input provenance

Raw Windows files are **not committed**. This file records only selected filenames and SHA-256 identities.

Sensor AeoB resources:
- `CAMF_RES_MSHW0490.bin` — `379a03154511922428ea27f56de625f579f39ca483fb97398953278b6b5f2851`
- `CAMS_RES_MSHW0491.bin` — `2d356bbfaf07ced1e5c03014a5c496b12107f5dc489c4333052565d5a5a5dcc2`
- `CAMI_RES_MSHW0492.bin` — `fb058d3c966f4b48412d48c2de7f58b861103a8aa06f0bb8c1d198e12431d908`
- `CAMP_RES_MSHW0495.bin` — `e79e5dccbe78b370cc120e3212dfe72076310a2a23798d009527062303074c2d`

The local decoded front/rear/IR AeoB resources are exact-text matches to the corresponding `qcom-aeob-dumps` Surface Pro 11 corpus. The local common platform `CAMP_RES_MSHW0495` is **not** an exact match to that public corpus, so local Windows remains authoritative for platform behavior.

Selected sensor modules were identified in E000 and are tracked by hash in the project oracle manifest. Use `oracle/windows-e000-inventory.md` for the full selected-file identity list.
