# E004ei — interval-corrected AEC shadow runtime

First live runtime after E004eh restored Windows low/high interval semantics in target aggregation method 11.

This is deliberately a fresh one-shot using the promoted canonical package. The front path remains `--post-g3-write-policy shadow`; `--allow-one-native-write` is absent. The current room lighting is no longer a test variable because E004eg disproved the prior lighting hypothesis.

Primary acceptance:

- 27/27 front frames and normal route/suspend/kernel-health gates;
- corrected AEC recurrence must no longer reproduce the old runaway/cap-saturation pattern caused by scalar point collapse;
- zero later native writes;
- if Windows decision 4 (`APPLY_ONE_NATIVE`) occurs naturally, it is logged only as `PROD_POST_G3_POLICY_SHADOW` and is not applied.

No same-boot retry is authorized.
