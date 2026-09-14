# E004dz — canonical package same-boot rear→front handoff

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

This is the product-activation acceptance for the canonical package built in E004dv/E004dw and filesystem-tested in E004dy.

One fresh one-shot boots the canonical unified rear+front+IR DTB, then loads all camera modules strictly from `/usr/lib/sp11-camera-stack/hardware/modules`. It executes the accepted rear colorbar oracle plus eight normal rear frames, returns routing to neutral and requires all three sensors suspended, then runs the installed front production launcher for one R27 stream under `shadow`, returns to neutral again and requires all three suspended.

The rear/front transition is therefore exercised in the same boot under the final three-camera DTB and IR-gated CAMSS authority. IR remains bind/configure/standby only. No receiver harness, direct IR stream, illumination, Linux SecureISP, protected ownership or SecurePD action is allowed.

One candidate, one attempt, no same-boot retry, mandatory Golden return, candidate retirement and package uninstall afterward.

## Attempt 1 — PASS / Golden restored / package removed

Fresh package-backed candidate boot `cf96bf28-1793-4240-a6b5-7a5c1a94fa1c` passed the same-boot rear→front handoff. Rear produced the exact Windows-authoritative colorbar and eight normal frames at 30.066146 fps. Routing then returned to neutral and all three sensors suspended before the installed front production launcher ran its accepted 27-frame `shadow` stream. Front sequences were 0..26, producer returned 24 PASS rows, all AWB selections were ordinary triangle mode, and there were zero later native writes.

IR remained bind/configure/standby only. The CSIPHY0 gate was armed but never selected, and there was no direct IR stream, illumination or Linux SecureISP action. Final routing was neutral and all three sensors were suspended.

SP11 returned to protected Golden FullIO v19c on boot `63e0ee9f-959a-445e-b27b-a73c25d52bad`. The candidate was retired and the canonical package was uninstalled, leaving all package product paths absent again.

This closes the canonical package activation acceptance for the non-protected RGB stack under the final unified three-camera authority.
