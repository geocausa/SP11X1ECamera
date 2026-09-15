# E004el — exact G4/request7 startup-fill live observation

E004ei proved that pure shadow becomes causally invalid at G7 because the corrected controller first reaches the cap plateau at G4/request7 but HA suppresses that tuple. E004ej then proved Windows requests 7..9 are naturally on the same plateau and that Windows request7 and Linux G4 quantize to the exact same physical IMX681 tuple.

E004el performs one fresh bounded run with the opt-in `g4-startup-fill-shadow` policy. It requires the explicit one-write authorization flag. G1..G3 use the existing startup path; G4 may be written only if every guarded field matches the E004ej tuple. G5+ are shadow-only regardless of later decision. Thus the maximum control ioctls are exactly four and no synthetic control delta exists.

Acceptance requires 27 frames, exact G4 allow/write at the completed-G5 boundary with effect G7, zero later native writes, neutral final route, all sensors suspended before/after, healthy kernel, and no retry. The key observation is G7+ convergence after the physical sensor has actually entered the Windows request7 plateau state.

## Live result

E004el completed exactly one fresh 27-frame run and returned to Golden. The guarded G4/request7 tuple passed every exact field check and was physically written once at the completed-G5 boundary for optical effect at G7. Total sensor-control ioctls were exactly four: startup G1/G2/G3 plus G4. There were zero later native writes, no retry, no synthetic delta, neutral final routing, all sensors suspended before/after, and clean kernel health.

Crucially, every controller output from G4 through G27 is the same physical plateau tuple (`FLL=7116 / VB=4956 / EXP=7108 / AGAIN=960 / DGAIN=1471 / ISP=0x3f801646`). Therefore shadowing G5+ does **not** create the history/physical mismatch seen in E004ei: the software-retained cap exposure and the actual sensor state agree throughout the plateau.

The first fully causal post-effect interval, G7..G24, remains above the preview cap for every source. No `APPLY_ONE_NATIVE` opportunity appears in the current dark/ambient room. This restores the original scene gate on a sound causal basis: the next live observation must use a naturally brighter scene while retaining the exact G4 startup-fill behavior; it must still shadow any later changed tuple until a separate fresh write experiment is prepared.
