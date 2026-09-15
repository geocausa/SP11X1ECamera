# E004en — natural cap-release one-shot live proof

Fresh Windows E004em proves that, in the current natural ambient scene, request7 Short is below the Windows preview cap: `4503849882 < 6133333088`. The Windows-authoritative T681/IMX681 conversion gives a real changed request7 tuple (`FLL=7116 / VB=4956 / EXP=7108 / AGAIN=960 / DGAIN=1080 / ISP=0x3f801c09`). No target or exposure value was injected.

E004en uses the existing `cap-release-one-shot` production policy unchanged. G1..G3 retain the proven startup path. For G4..G24, HA may permit exactly one natural native tuple only if convergence is strictly below the preview cap, the cap is a no-op, the tuple differs from the last successful physical tuple, and the one-write latch is clear. After a successful later write, all remaining later sources are shadow-only; G25/G26 remain horizon-shadowed. The launcher requires explicit `--allow-one-native-write` authorization.

Valid outcomes are `PASS_ONE_NATURAL_CAP_RELEASE_WRITE` or `PASS_NO_CAP_RELEASE_SCENE_SHIFTED`. Either consumes the one-shot and requires immediate Golden return. No retry and no synthetic control delta are allowed.
