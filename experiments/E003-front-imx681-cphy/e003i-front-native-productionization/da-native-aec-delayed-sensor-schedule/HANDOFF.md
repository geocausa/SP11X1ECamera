# DA handoff

Status: PASS offline.

For a six-frame bounded native-AEC runtime, bootstrap IMX681 to `FLL=3562, VBLANK=1402, exposure=3554, analogue=0, digital=0x0100`.

Process generation G with CU/CV but retain the tuple for one completed generation. Apply G1's tuple immediately after G2 completion, G2's after G3, and G3's after G4. CY measures write-after-N -> first effect N+2, so these first appear at G4/G5/G6 respectively, matching W's logical request G+3.

Do not use CY G1..G6 as a continuous CP history fixture: its manual exposure step breaks controller causality. Do not extend CH beyond its proven in-table domain based on that diagnostic mismatch.
