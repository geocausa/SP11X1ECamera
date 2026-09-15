# E004en — natural cap-release one-shot live proof

Fresh Windows E004em proves that, in the current natural ambient scene, request7 Short is below the Windows preview cap: `4503849882 < 6133333088`. The Windows-authoritative T681/IMX681 conversion gives a real changed request7 tuple (`FLL=7116 / VB=4956 / EXP=7108 / AGAIN=960 / DGAIN=1080 / ISP=0x3f801c09`). No target or exposure value was injected.

E004en uses the existing `cap-release-one-shot` production policy unchanged. G1..G3 retain the proven startup path. For G4..G24, HA may permit exactly one natural native tuple only if convergence is strictly below the preview cap, the cap is a no-op, the tuple differs from the last successful physical tuple, and the one-write latch is clear. After a successful later write, all remaining later sources are shadow-only; G25/G26 remain horizon-shadowed. The launcher requires explicit `--allow-one-native-write` authorization.

Valid outcomes are `PASS_ONE_NATURAL_CAP_RELEASE_WRITE` or `PASS_NO_CAP_RELEASE_SCENE_SHIFTED`. Either consumes the one-shot and requires immediate Golden return. No retry and no synthetic control delta are allowed.

## Live result

E004en achieved the missing production-native changed post-G3 feedback proof. On the single consumed run, G4/request7 naturally produced `CONV=4074449535` and capped output `4074449535`, both below the fixed Windows-derived preview maximum `6133333088`. HA therefore allowed exactly one real changed sensor tuple: `FLL=6492 / VB=4332 / EXP=6484 / AGAIN=960 / DGAIN=1072 / ISP=0x3f800000`, for optical effect at G7. Total sensor-control ioctls were exactly four (startup G1..G3 plus G4), with zero startup-fill override, zero synthetic delta, and zero second later writes. The one-write latch then produced 20 `ALREADY_APPLIED` shadows plus the two bounded horizon shadows.

The camera runtime itself completed all 27 frames with neutral final route, all sensors suspended before/after and clean kernel health. The initial `run-once.sh` exit was caused only by an observation-verifier bug after capture: it incorrectly asserted logged `CONV < CAP`. The logged `CAP` field is the capped output, while HA's fixed ceiling is `6133333088`; the correct release condition is `CONV == capped_output < fixed ceiling`. The verifier was corrected offline after Golden return and the camera was **not rerun**.

Fresh Windows E004em and Linux E004en also track closely through the causally usable request7..10 window despite being sequential captures. This is supporting parity evidence, not a claim that the physical scene was identical at every instant.
