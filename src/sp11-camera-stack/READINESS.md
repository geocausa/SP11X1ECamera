# SP11 camera stack readiness

## RGB-only software-first delivery decision (2026-09-23)

Finish and validate a usable opt-in software-processing front1080p /
rear4K RGB camera service FIRST. Once its actual app-delivered image,
throughput and lifecycle gates pass, report the result and ask the user
whether to pursue Qualcomm native hardware-ISP Windows-image parity.
The ISP path and protected IR/Hello are NOT prerequisites for an
honestly labelled RGB-only software release. Historic ~65–70%
software and ~30–40% Qualcomm hardware-ISP figures are rough
engineering estimates for RGB usability, not measured completion
or image-parity percentages. Earlier 1080p/4K V4L2 software transport
and the recent 640x480 libcamera software-ISP proof are SEPARATE
implementations and cannot be called one finished 1080p/4K pipeline.
Authoritative stages and acceptance/decision gates:
[RGB-PHASED-ROADMAP.md](RGB-PHASED-ROADMAP.md).

## Promotion decision

**Hold full 1:1 default promotion.**

The canonical hardware package has passed bounded runtime acceptance. RGB application transport has passed approximately60-second near30fps runs at front1080p/rear4K. Bounded systemd start/stop and sequential uid1000 apps passed E004kw with both named devices visible. E004la additionally proved repeated uid1000 client opens and recovery after a deliberately killed client while each publisher stayed running. Persistent daily operation, normal powered-on sensor/publisher restart, hours-long reliability and calibrated image quality remain unproven. SP11 Linux OS system standby/resume is separately unsupported and MAY CRASH THE OS: it is explicitly OUT OF CAMERA TEST SCOPE, not a camera-regression gate. Calling the stack fully Windows-equivalent or making it the final default while protected IR/Windows Hello cannot legitimately execute would overstate parity.

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

E004kr extends direct transport to front1080p:1800distinct app frames at30.0247fps, source30.0061fps over60s. Intentional SIGTERM/STREAMOFF, exited processes/readers and neutral graph passed before a short rear120app-frame session and the same controlled stop. Both sampled images were nearly black. This proves bounded transport and planned cancellation/handoff, not calibrated image quality, arbitrary reopen or permanent daily service. OS system standby/resume remains expressly excluded from camera tests. E004kr is consumed and retired on Golden.

E004kp subsequently removed the rear RAW/NV12 pipes and separate publisher, using direct mmap capture and V4L2 output with unchanged pixels. Rear2400sources achieved29.9496fps over80.101s and1800distinct app frames achieved30.0684fps over59.830s; source gaps0, one Gst offset gap, clean neutral shutdown and Golden return. This closes the bounded rear throughput gap, not day-long reliability or calibrated image quality. Front remains at E004km throughput pending direct transport.

E004km delivered1800 complete distinct front1080p and rear4K frames to independent standard V4L2/GStreamer applications in sequential sessions. Source2400frames each had no sequence gaps. Front app26.9873fps and rear app13.7766fps are observed over different source/app windows, not30fps parity. Both sampled scenes were dark; no calibrated scene comparison exists. The front path is a separate pRAA RAW10 software proxy, not a QC10C decoder or Windows ISP replacement. E004km is consumed, retired and returned to Golden. Historical hardware/IQ-control claims below do not establish end-to-end image quality.

## E004lz maintained physical RGBSession integration (2026-09-23)

New distinct safeguarded one-shot physically PASSED the MAINTAINED
RGBSession + exact 119-link Media Controller and ordinary source
publisher backends. Front1080p 448 and rear4K 446 full contiguous
software RAW→NV12 source/app-compatible frames, 0 source sequence
gaps. Both ordinary uid1000 endpoints completed three separate
120-frame normal app processes and an intentional client kill
followed by recovery under the SAME source publisher invocation.
Stop143/STREAMOFF, complete real neutral→front→neutral→rear→neutral
graph, lease and independent FD release passed. Golden returned and
E004lz boot/services/assets retired, consumed and documented in
e004lz RESULT/CONSUMED/evidence. It was FINITE ~15s per camera,
not a persistent/daily-user service or unlimited-client proof.
Both sampled images remained near-black meanY≈16, meaning real
controlled-lit exposure, image quality and Windows ISP parity are
still UNPROVEN. E004ly independently proved ~115s per camera with
the prior separate scripted route rather than this new controller.

## E004mb real morning-light RGB detail check (2026-09-23)

**Image quality is now an observed release blocker, not just
uncalibrated:** real 90-frame ordinary-app front1080p and rear4K
probes under morning corner light produced front mean Y~16.3,
p99 18 and rear mean Y~16.0, p99 16, with negligible spatial
contrast. Neither camera produced statistically distinguishable
scene detail. Current V4L2 sensor controls stayed at their
fixed readback values; this test made NO exposure/gain writes.
The source RAW signal and physical light at each lens remain
unmeasured, so do NOT claim scene darkness alone explains this
or that the software converter is definitely at fault.
Bounded root selector, independent apps, stop/STREAMOFF and
Golden return all passed; one-shot consumed/retired.
Next finite safely guarded test: paired RAW source versus NV12
scalar histogram and controlled supported-exposure engineering,
NO IR or OS system sleep.

## E004ma root-private RGB selector (2026-09-23)

An independent guarded one-shot proved the maintained root Unix-socket
selector commands front→rear→off→quit on real native CAMSS, front1080p /
rear4K NV12 ordinary uid1000 V4L2 clients. Three normal 120-distinct
frame app openings and intentional SIGKILL/recovery per camera retained
the same publisher. Both returned to native graph neutral with IR off;
Golden recovered, candidate retired/consumed. This closes *bounded
physical selector control*, not persistent everyday camera installation.

Both front and rear sampled luma Y ~16. A genuinely distinguishable
scene, correct exposure, dynamic range, colour and calibrated image
quality remain unproven despite successful real optical frame delivery.
Next: guarded finite daylight/low-light RAW-vs-Y in-memory scene
diagnosis; no user-image archive, IR or system sleep.

## E004ly guarded high-resolution software publisher trial (2026-09-23)

Independent fresh one-shot real hardware front1080p and rear4K
RAW10→NV12 opt-in continuous source publisher proof PASSED.
Front captured/published 3452 frames over 115.004s; rear 3444 over
114.957s, both zero source-sequence gaps. Each standard V4L2 endpoint
remained discoverable and ordinary uid1000 apps completed first,
reopen and post-SIGKILL recovery (three normal 120-frame app opens)
under the SAME publisher invocation. Intentional planned 143 stop
verified STREAMOFF; all camera users closed and complete native
media graph neutral between cameras and after rear. IR off, Golden
returned safely; candidate retired and identity consumed.
See e004ly RESULT.json/CONSUMED.json/evidence.

**Not a finished daily camera service:** two separately bounded
~115s publishers; maintained RGBSession state-machine still
source-only rather than live integrated; general multi-client
session ownership, production installation, extended uninterrupted
operation, light/exposure/image quality and matched Windows visual
parity remain unresolved. Both scenes sampled nearly black. The
separately proven 640x480-XRGB8888 libcamera processed path must
not be conflated with this 1080p/4K RAW→NV12 software path.

## E004lx guarded processed RGB soak and reopen (2026-09-23)

A new single-use, isolated root-sealed libcamera v0.7.0 test delivered
3600 real processed 640x480-XRGB8888/sRGB frames in FOUR independent
front→rear→front→rear processes (900 contiguous frames each). All four
had no observed sensor-control errors and each returned the COMPLETE
native media graph to neutral after app exit. Each had 889 steady
intervals after the first ten with no >250ms gap. First front/rear
openings had no large early gap; reopened front and rear each had one
~1s startup pause (999185us and 966638us). The previous E004lw
all-interval strict validator rightly failed on this pause; E004lx
separately reports startup vs steady cadence and does NOT claim
seamless switching. This proves bounded 2-minute processed transport
and clean independent reopen/neutral shutdown, not permanent daily
operation, native full-resolution processed RGB or Windows ISP parity.
Root-only experimental access is NOT general OS-enforced multiclient
ownership. The one-shot boot/service/private build is consumed and
retired, Golden recovered unmodified; no live camera on Golden.
See E004lx RESULT/CONSUMED/evidence.

**Next RGB product gate:** build a non-default, opt-in, independently
owned and recoverable RGB camera service with simultaneous selectable
front/rear *published* endpoints or equivalent verified ordinary-app
handoff. Verify actual libcamera-processed output through normal
unprivileged app readers and clean stop/reopen, investigate the
repeatable ~1s early-frame interruption, then validate acceptable
processed resolution and controlled-light image quality. GStreamer
libcamerasrc, videoconvert and v4l2sink are installed on Golden and
a synthetic 120-frame BGRx640x480→NV12 conversion passes offline;
this is ONLY a bridge prerequisite, not a live camera-to-loopback
or ordinary desktop client proof. Do not activate experimental camera
devices on protected Golden.

**OS sleep exclusion:** user reports SP11 Linux standby/suspend/resume
is not reliably implemented and may crash the whole OS. Never put it
into system sleep for a camera test. Normal guarded reboots and
powered-on camera open/stop/reopen tests remain authorized. Sensor
runtime-PM idle checks are distinct from OS system sleep.

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
