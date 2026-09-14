# E004dt — current-scene front post-G3 cap audit

Status: **PASS OFFLINE / NO RUNTIME**.

This experiment corrects a semantic trap in the E004ds front transcript. `RELEASED_SOURCES=G1..G26` describes release of delayed scheduler ownership; it does **not** mean the Windows preview convergence cap was released.

The actual post-G3 native-write decision is `e003i_ha_decide()`. For an eligible source to permit one native write, the result must be `E003I_HA_APPLY_ONE_NATIVE` (decision 4), which requires the convergence value to be below the preview cap, `cap == conv`, a changed native tuple, and no previous later write.

E004ds instead recorded G4..G24 as `HB_NATIVE_CAP_RELEASE_SHADOW ... DECISION=2`, where decision 2 is `E003I_HA_SHADOW_CAP_ACTIVE`. Every convergence value remained above `6133333088`, while capped convergence remained exactly `6133333088`. G25/G26 were the expected evidence-horizon shadows.

The final production accounting was therefore exactly:

- startup/native control IOCTLs: 3;
- later native writes: 0;
- later shadows: 23;
- cap-active shadows: 21;
- unchanged shadows: 0;
- already-applied shadows: 0;
- horizon shadows: 2;
- policy-disabled shadows: 0.

The especially important zero is **policy-disabled shadows**. If the shadow-policy run had reached a real APPLY_ONE_NATIVE opportunity, production code would have logged `PROD_POST_G3_POLICY_SHADOW`. It did not.

Therefore a fresh `cap-release-one-shot` run in the same scene is already predicted to make zero later writes and would not close the native-feedback proof. We deliberately do not consume a candidate merely to reconfirm that.

The remaining proof is genuinely environmental: wait for a naturally changed/brighter optical scene that produces decision 4 under shadow observation, then use a fresh one-shot with `--post-g3-write-policy cap-release-one-shot --allow-one-native-write`. Do not synthesize or force the convergence condition.
