# E003i CI — native ordinary AEC request recurrence

Status: **PASS (native/offline)**.

CI composes the already-verified ordinary front AEC pieces into a warmed-up multi-frame request loop:

`CF final target qwords -> CG convergence -> CH post-convergence T681 -> retained exposure history`

The loop owns the exact temporal state that Windows convergence needs after warm-up:

- F-1 Short/Long/Safe retained post-T681 exposure qwords + predictive gain;
- F-2 Short/Long/Safe retained post-T681 exposure qwords + predictive gain;
- F-3 Safe retained post-T681 exposure qword.

The predictive-gain recurrence is now closed mechanically. BA identifies convergence `+0xd8` as `PredGain`; `PopulateOutput` copies it to output `+0x70`; `runEndOfFrame` persists output `+0x70` to history `+0x178`; the next `RunConvProcesss` reloads history `+0x178` into `+0xd8`.

CI intentionally keeps current analyzer `sourceExposure[S1]` as an explicit request input. Its exact request-local producer is the next closure boundary and is not guessed here. Likewise CI is a warmed-up loop: F-1/F-2/F-3 are seeded explicitly rather than inventing startup behavior.

The verifier executes 256 independent eight-request sequences (2,048 requests total). At every request it independently invokes CF, CG and CH, requires complete output structures to match byte-for-byte, and checks the committed recurrence state.

No live camera, module load, sensor write, MMIO, Windows boot or reboot is used.
