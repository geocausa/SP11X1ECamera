# E004dz — canonical package same-boot rear→front handoff

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

This is the product-activation acceptance for the canonical package built in E004dv/E004dw and filesystem-tested in E004dy.

One fresh one-shot boots the canonical unified rear+front+IR DTB, then loads all camera modules strictly from `/usr/lib/sp11-camera-stack/hardware/modules`. It executes the accepted rear colorbar oracle plus eight normal rear frames, returns routing to neutral and requires all three sensors suspended, then runs the installed front production launcher for one R27 stream under `shadow`, returns to neutral again and requires all three suspended.

The rear/front transition is therefore exercised in the same boot under the final three-camera DTB and IR-gated CAMSS authority. IR remains bind/configure/standby only. No receiver harness, direct IR stream, illumination, Linux SecureISP, protected ownership or SecurePD action is allowed.

One candidate, one attempt, no same-boot retry, mandatory Golden return, candidate retirement and package uninstall afterward.
