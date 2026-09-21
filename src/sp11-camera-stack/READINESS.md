# SP11 camera stack readiness

## Promotion decision

**Hold full 1:1 default promotion.**

The canonical hardware package has passed bounded runtime acceptance. RGB application transport now works, but sustained30fps, persistent service lifecycle and calibrated image quality remain unproven. Calling the stack fully Windows-equivalent or making it the final default while protected IR/Windows Hello cannot legitimately execute would overstate parity.

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

The non-protected hardware package supports **guarded, bounded non-default experiments**. This is not a complete daily-use RGB application stack.

## Current RGB application evidence (2026-09-21)

E004kr extends direct transport to front1080p:1800distinct app frames at30.0247fps, source30.0061fps over60s. Intentional SIGTERM/STREAMOFF, exited processes/readers and neutral graph passed before a short rear120app-frame session and the same controlled stop. Both sampled images were nearly black. This proves bounded transport and planned cancellation/handoff, not calibrated image quality, arbitrary reopen, suspend or permanent daily service. E004kr is consumed and retired on Golden.

E004kp subsequently removed the rear RAW/NV12 pipes and separate publisher, using direct mmap capture and V4L2 output with unchanged pixels. Rear2400sources achieved29.9496fps over80.101s and1800distinct app frames achieved30.0684fps over59.830s; source gaps0, one Gst offset gap, clean neutral shutdown and Golden return. This closes the bounded rear throughput gap, not day-long reliability or calibrated image quality. Front remains at E004km throughput pending direct transport.

E004km delivered1800 complete distinct front1080p and rear4K frames to independent standard V4L2/GStreamer applications in sequential sessions. Source2400frames each had no sequence gaps. Front app26.9873fps and rear app13.7766fps are observed over different source/app windows, not30fps parity. Both sampled scenes were dark; no calibrated scene comparison exists. The front path is a separate pRAA RAW10 software proxy, not a QC10C decoder or Windows ISP replacement. E004km is consumed, retired and returned to Golden. Historical hardware/IQ-control claims below do not establish end-to-end image quality.

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
