# E004ei — interval-corrected AEC shadow runtime

First live runtime after E004eh restored Windows low/high interval semantics in target aggregation method 11.

This is deliberately a fresh one-shot using the promoted canonical package. The front path remains `--post-g3-write-policy shadow`; `--allow-one-native-write` is absent. The current room lighting is no longer a test variable because E004eg disproved the prior lighting hypothesis.

Primary acceptance:

- 27/27 front frames and normal route/suspend/kernel-health gates;
- corrected AEC recurrence must no longer reproduce the old runaway/cap-saturation pattern caused by scalar point collapse;
- zero later native writes;
- if Windows decision 4 (`APPLY_ONE_NATIVE`) occurs naturally, it is logged only as `PROD_POST_G3_POLICY_SHADOW` and is not applied.

No same-boot retry is authorized.

## Live result

E004ei completed one fresh 27-frame shadow-only candidate run and returned to Golden. All route, suspend and kernel-health gates passed; there were zero later native writes and no retry.

The interval correction materially changes startup behavior. G1..G3 now ramp through bounded native tuples, and G4 is the first capped maximum tuple. Its pre-cap Short convergence is `6612848061`, only about 7.8% above the `6133333088` preview cap. G4, G5 and G6 all resolve to the exact same capped IMX681 tuple: `FLL=7116 / VB=4956 / EXP=7108 / AGAIN=960 / DGAIN=1471 / ISP=0x3f801646`.

The old HA pure-shadow policy suppresses G4 because the cap is active. That suppression has an N+2 optical consequence at G7. The request loop nevertheless commits G4's capped output into software history before the scheduler decides not to write it. Therefore G1..G6 remain causally usable, but G7+ no longer represents a Windows-equivalent recurrence: software history assumes a G4 tuple that physical IMX681 never received.

This makes the old “wait under pure shadow until cap release” strategy circular after the interval fix. The next gate is a Windows request-7 oracle to determine whether corrected G4/request7 is the first normal capped startup-fill tuple. No synthetic sensor delta is proposed.
