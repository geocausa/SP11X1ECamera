# E003i DO — Windows internal-cap branch producer oracle

Status: **PREPARED_UNEXECUTED**.

Purpose: bind the two remaining ordinary-preview inputs used by the DN native internal exposure cap without guessing: the bank9:data10 lookup that produces the internal `w12` rescale-disable branch and the compact output field at `+0x98`.

The capture is evidence-only on normal SP11 Windows front preview. It records the same-call CapExposure entry and exit tuples, the lookup return/valid/value at RVA `0x3d35e4`, final `w12`, convergence config `+0x2c`, compact `+0x98`, and selected history1 Short if the conditional rescale path executes. The debugger auto-detaches after exactly decimal 18 completed cap calls. The holder starts/stops the camera normally. No exposure targets are injected.

Safety: one-shot direct Windows `BootNext=0006`; persistent GRUB Golden remains `sp11-audio-fullio-v19c`; no Linux camera module or candidate is armed. Raw debugger evidence stays outside Git. Return to Golden after capture.
