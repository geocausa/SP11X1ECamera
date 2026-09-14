# E004ec — side-light post-G3 shadow observation

Fresh shadow-only observation requested after turning on the side room lights. The main light remains off because it may shine directly into the camera.

This one-shot uses the canonical package, binds all three sensors, streams only the front RGB R27 production path with `post_g3_policy=shadow`, and records the recovered Windows post-G3 decision for G4..G24. It does **not** allow a later native write.

A useful scene is proven only if `PROD_POST_G3_POLICY_SHADOW` appears: that marker means the decision logic reached APPLY_ONE_NATIVE (decision 4), but shadow policy intentionally suppressed the hardware write. `HB_NATIVE_CAP_RELEASE_SHADOW ... DECISION=2` remains cap-active and is not a write opportunity.
