# E003i CG — native qword convergence input

Status: **PASS (native/offline)**.

CG closes the public-domain mismatch between CF and the existing BU convergence wrapper. Windows feeds convergence with linear Short/Long/Safe exposure qwords, not precomputed double log coordinates. CG therefore accepts those qwords directly and reproduces Windows' absolute convergence-coordinate conversion internally.

The exact Windows order is:

`uint64 exposure -> UCVTF float32 -> log10f float32 -> FMUL float32 by 1/log10f(1.03f) -> widen to double`

The reciprocal scale is exact bits `0x429bcc0c`. The intermediate float32 `log10f` rounding matters: the historical BU helper combined the log and scale multiply in double and can be one ULP different. A concrete trap is qword `1093437165`: Windows/CG gives `0x443006f5`; the older combined expression gives `0x443006f6`.

CG retains BU's already-narrowed ordinary normal-streaming/AEC-unlocked convergence state, history projection and fixed profile. It changes the current-target public boundary to qwords and corrects the common absolute log1.03 scalar helper used by convergence.

No live camera, module load, sensor write, MMIO, Windows boot or reboot is used.
