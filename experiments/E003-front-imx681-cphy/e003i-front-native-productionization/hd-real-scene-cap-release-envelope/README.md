# E003i-HD — real-scene cap-release envelope

Status: **PASS OFFLINE / no camera runtime.**

HC was a correct no-op on the sensor after G3: the scene never released the Windows-derived preview cap. HD asks whether we should simply wait longer, inject a larger sensor perturbation, or change the optical scene.

The evidence is unusually clear. HD replays the exact native AEC stack over **five independent real 27-frame Linux captures**: GO, GS, GV, GY and HC. Every one is cap-active from G3 through G27. By G27 every run is still more than 8× above `E003I_PREVIEW_CAP_MAX`; none is trending toward a natural release in the same static scene. A longer same-scene run therefore has no evidence-based reason to solve this gate.

The Windows DM oracle provides the missing counterexample: ordinary Windows preview requests R1..R7 are below the same cap, with R7 at about 0.917× cap, and R8 is the first request that clamps. Thus the cap is not a permanent controller state; a genuine ordinary below-cap regime exists.

We **cannot turn that into an exact brightness/lux threshold** because DM and HC are different live captures and the exposure recurrence is history-dependent. Request-number ratios are useful only as regime separation, not as a photometric calibration.

## Engineering decision

- Do not rerun HC.
- Do not invent a larger synthetic gain/exposure step.
- Do not just extend the same dark/static observation indefinitely.
- The next production-native feedback proof needs a **fresh identity under a substantially brighter, diffuse real scene**, while reusing HA/HB's exact one-write cap-release gate.
- For a 27-frame proof, G4..G24 may be eligible and G25/G26 remain forced shadow so a two-frame optical effect cannot escape the evidence window.
- Direct sun or lasers into the camera are not an acceptable stimulus.

This introduces a real physical/environment dependency. While that dependency is unavailable, useful project work should continue on repeated-stream robustness and production integration without claiming the post-G3 native feedback gate closed.
