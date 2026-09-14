# E004ec — side-light post-G3 shadow observation

Fresh shadow-only observation requested after turning on the side room lights. The main light remains off because it may shine directly into the camera.

This one-shot uses the canonical package, binds all three sensors, streams only the front RGB R27 production path with `post_g3_policy=shadow`, and records the recovered Windows post-G3 decision for G4..G24. It does **not** allow a later native write.

A useful scene is proven only if `PROD_POST_G3_POLICY_SHADOW` appears: that marker means the decision logic reached APPLY_ONE_NATIVE (decision 4), but shadow policy intentionally suppressed the hardware write. `HB_NATIVE_CAP_RELEASE_SHADOW ... DECISION=2` remains cap-active and is not a write opportunity.

## Side-light result

The fresh side-light observation completed 27/27 front frames with shadow policy and zero later native writes. All 21 eligible G4..G24 decisions remained `SHADOW_CAP_ACTIVE` (decision 2); there were zero `PROD_POST_G3_POLICY_SHADOW` markers, so the scene did not produce an APPLY_ONE_NATIVE opportunity. The best observed convergence remained about 16.54B versus the 6.13B preview cap. SP11 returned to Golden, the candidate was retired and the package was removed.
