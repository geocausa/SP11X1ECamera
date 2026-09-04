# E003i-E — template-free 0076 capsule composer

This checkpoint removes the **41,088-byte captured capsule as a production input**.

`build-template-free-0076-capsules.py` reconstructs requests 4, 5 and 6 from the individual normalized startup/steady command sources, individual DMI source state, the exact historical module-value sources used by the accepted 0076 regression, and the fresh atomic LSC staging/Titan680 packing proof. It never opens an existing full capsule.

The generated binaries are not tracked. In a clean run they land under `/tmp/e003i-template-free-0076` and reproduce the accepted 0076 identities exactly:

- R4 `1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa`
- R5 `8e447a662a47e47db7dd211d6a109d590531309f944e52b729a4351b5a00da11`
- R6 `c88e7a75f228fac7b69a4a122fd618aa054bdbf98e83ff541be9c20177844583`

## Stable composition boundary

Across these three accepted capsules, 31/36 sections are invariant. Only five sections are request-generated: the nine-module value record, LSC0, LSC1, the Windows GIC wire alias derived from LSC0+LSC1, and GTM0. Request ID is the only changing header field.

This gives production a stable layering boundary. The next producer stage generates those request-state pieces from live trigger/3A, calibration, Tintless/ALSC and TMC state. It does **not** need another capsule format, another kernel control path, or a 41 KB binary template.

The 0076 regression module records are deliberately classified as compatibility fixtures. They came from the historical R4/R5/R6 Windows source sessions used by 0076 and must not be mislabeled as one fresh atomic 3A stream. The LSC refresh is the fresh 2026-09-04 atomic front authority.

No Linux camera runtime is performed or authorized here.
