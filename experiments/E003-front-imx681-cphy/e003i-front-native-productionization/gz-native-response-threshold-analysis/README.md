# E003i-GZ — native response-threshold analysis after GY

Status: **PASS OFFLINE / threshold censored by preview cap / no larger live sentinel authorized.**

GY proved the transport seam with one real changed G4 sensor transaction, but its +1 digital-gain-LSB step was intentionally tiny. GZ asks the next question before risking a larger live perturbation: did that step produce a measurable native response, and can the production controller threshold be inferred from the evidence?

The answer is **no, for two independent reasons**.

First, the sentinel is only +0.06798% sensor digital gain. Exact FrameLuma replay shows ordinary steady-frame variation is much larger. Even the quietest comparison run (GS) has >1% steady luma coefficient of variation; GY itself is several percent. GY and the no-sentinel GV run happen to be nearly equal at G7, but their pre-effect trajectories differ enough that this cannot be treated as a causal matched-pair measurement.

Second, and more important, exact native AEC replay proves the output is **hard-censored by the Windows-derived preview cap**. From G3 through G27 the unconstrained Short convergence remains above `E003I_PREVIEW_CAP_MAX=6133333088`, the cap output is exactly that maximum every frame, T681 stays at the same maximum preview operating point, and the native IMX681 tuple is fixed at FLL=7116 / EXP=7108 / AGAIN=960 / DGAIN=1471. At G7 the unconstrained Short request is roughly 8.4x the cap. This is saturation, not evidence of a small controller deadband.

Therefore GY cannot identify the native changed-output threshold, and simply choosing a larger synthetic gain step would be guesswork. The safe next engineering gate is an **offline controlled cap-release / bright-scene acceptance plan**: define how to detect native convergence crossing below the preview cap and how to bound the first production-native changed control when that occurs. No new camera runtime is authorized by GZ.
