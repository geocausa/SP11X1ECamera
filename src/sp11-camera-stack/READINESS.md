# SP11 camera stack readiness

## Promotion decision

**Hold full 1:1 default promotion.**

The canonical non-protected product is ready and has passed its package-backed runtime acceptance, but the project goal is wider than RGB camera usability. Calling the stack fully Windows-equivalent or making it the final default while protected IR/Windows Hello cannot legitimately execute would overstate parity.

## Ready now

- unified rear RGB + front RGB + IR device-tree authority;
- exact canonical CAMSS, IMX681, OV13858 and VD55G0 module set;
- simultaneous three-sensor bind;
- Windows-exact CSIPHY0 IR receiver programming/readback (96/96);
- rear RGB exact colorbar + normal streaming under the three-camera authority;
- front RGB production R27 streaming with Windows-authoritative IQ/AWB behavior under the same authority;
- same-boot rear→neutral→front handoff from the canonical installed package;
- deterministic package build/staging;
- bounded install/update/uninstall and real-filesystem lifecycle with zero activation side effects;
- maintained offline Windows-exact protected worker source and exact SecurePD proxy/native ABI.

The non-protected product may therefore be treated as **ready for guarded, non-default use**.

## Not honestly complete yet

### Protected IR / Windows Hello

The protected provider, CPZ sample backing, FastRPC FD handoff lifetime, SecurePD worker ABI and worker implementation are mechanically closed. The exact worker is still unsigned and cannot be admitted by the production SP11 CDSP trust policy using any credential or signing service currently available to this project.

This is an external trust/admission blocker, not missing Linux algorithm code. Do not weaken verification to get runtime output.

### Front post-G3 changed native feedback

The one-write production policy is implemented and bounded, but the latest live scene remained preview-cap-active for every eligible G4..G24 source. There was no legitimate APPLY_ONE_NATIVE opportunity to prove. Wait for a naturally changed/brighter scene and observe decision 4 under `shadow` before consuming a fresh `cap-release-one-shot` candidate.

## Default rule

Do not make the current package the project's final 1:1/default camera stack until the protected IR/Hello admission blocker is resolved and its end-to-end runtime passes. A separate user decision could still choose the proven RGB/non-protected subset as a convenience default, but that would be a product-policy choice, not proof of complete Windows parity.
