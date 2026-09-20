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

### Front post-G3 changed native feedback — CLOSED by E004en

The original scene-gated evidence gap was resolved in E004en on
2026-09-15. The single, consumed one-shot ran 27 front-RGB frames and
observed one naturally changed post-G3 native tuple applied to IMX681
at source G4/request7 for effect at G7. It used no synthetic control
delta, second later write or same-boot camera rerun. The candidate was
retired and returned to protected Golden Linux. The earlier cap-active
observation remains historical context, NOT a current blocker. Do not
repeat the consumed E004en identity or demand another scene change.

### Native front-IR illumination and offline face processing — SEPARATE BLOCKED PATH

E004fu demonstrated 16 live ambient/unilluminated VD55G0 optical captures,
but the steady grayscale signal was low (mean 38.6–39.7/255, max 48)
and NOT validated for facial authentication. E004hi/HZ/IA demonstrate
an uninstalled ordinary Linux HLOS pixel/transaction/public visible-light
YuNet/SFace diagnostic; public-fixture inference is neither live VD55G0
near-IR face validation nor Windows Hello security or protected processing.

E004ge still lacks calibrated optical radiometry, measured electrical/
optical pulse and current, independently verified stuck-high strobe/
host-failure autonomous LED-off, physically reviewed hardware cutoff,
and exact wiring/routing evidence for native Linux IR illumination.
The discovered idle PMIC timer 0x93 is not that physical proof. Do NOT
enable native IR illumination, enroll a user or attach this offline
prototype to PAM/login on the strength of software and register evidence.

Protected Windows Hello parity is separately blocked by legitimate
production SecurePD worker signing/admission; neither a nonprotected
HLOS image nor weakening trusted-worker verification can replace it.

## Default rule

Do not make the current package the project's final 1:1/default camera stack until the protected IR/Hello admission blocker is resolved and its end-to-end runtime passes. A separate user decision could still choose the proven RGB/non-protected subset as a convenience default, but that would be a product-policy choice, not proof of complete Windows parity.
