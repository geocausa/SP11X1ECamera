# SP11 RGB cameras — user-selected native Qualcomm ISP / Windows OEM path

LATEST DECISION (2026-09-23 ~19:36 BST): User explicitly chose
the SECOND originally optional track: work toward FRONT+REAR
native Qualcomm hardware ISP with SAME physical SP11 Windows
OEM camera stack/tuning as the oracle, prioritizing image
detail, exposure, blue/colour and quality over more cosmetic
CPU software-Bayer experiments. The earlier SOFTWARE-FIRST
proposal is superseded as a PRIORITY, not erased as evidence.
Last complete E004ne RGB 1080p/4K software path remains an
opt-in safe fallback; no native processed ISP first frame,
OEM Windows optical parity or ordinary native-ISP service
has yet been independently proven. E004ng/E004nh original
full trial failures and SP7 lower LCD fault still apply.
Protected IR/Hello is separately deferred, IR remains OFF
and Linux OS system suspend/hibernate remains prohibited.
Never load Windows kernel .sys or user .dll as Linux native
camera code, distribute proprietary OEM tuning/firmware or
enable an unverified Windows camera firmware loader.

Exact Windows ISP/rear MSHW0491 device-package audit and
next bounded Windows oracle/portable Linux engineering gates:
experiments/E004-front-ir-vd55g0/e004ni-native-isp-windows-rear-oracle-source-audit/README.md.
Existing extensive E003h front Windows CamX IQ/RT-CDM VFE1
and 007x live state are valuable inputs; do NOT treat
front-specific sensor mode, LSC or PIX transport as
proven rear OV13858 readiness. The Linux front and rear
RAW10 software-to-NV12 results proved image transport
and cadence but NOT an OEM-like hardware ISP image.

## Historical software-first plan (superseded as active priority;
## retain its measured fallback acceptance requirements)


### 2026-09-23 source-only OEM rear ISP audit — active next route

The SAME SP11 Windows DriverStore was mounted private READ-ONLY
and unmounted after inspecting EXACT selected sensor extension,
platform, ISP firmware, AVStream DeviceMFT and MSHW0491 tuning.
The selected OV13858 rear tuning and sensor module hashes match
older Windows live driver inventory. Full details including
MSHW0491 vs unrelated MSHW0561 variant, default/multiframe
photo settings, CamX module ownership and Linux first processed
frame blockers are in E004ni/README.md. This does NOT mean
OEM tuning can run on Linux or that the Windows driver has
been ported. Qualcomm's 2026 upstream CAMSS Offline Processing
Engine series targets Agatti/Shikra, NOT proven X1E-compatible;
do not confuse it with our Spectra/VFE native route.
Next run a fresh bounded SAME-device Windows REAR 4K/video
vs actual high-quality STILL oracle, verify selected tuning
and actual per-frame ISP stage/metadata, then safely port
the independently understood Linux native ISP boundary
behind Golden-preserving one-shot gates. Keep the known
SP7 lower-panel LCD fault out of controlled colour data.

## Planning snapshots — NOT objective completion metrics

As of 2026-09-23, the prior conversation estimated approximately
65–70% for a usable software-processing front1080p/rear4K RGB
solution, and 30–40% for a usable Qualcomm native hardware-ISP RGB
solution overall. These are subjective engineering estimates, not
measured work completion, schedule promises or Windows image-quality
parity percentages. Front hardware ISP has more evidence than rear;
neither backend has a measured Windows-visual-parity percentage.

Do not conflate the evidence: earlier real optical Linux 1920x1080
front and 3840x2160 rear NV12 to independent standard V4L2 apps
was through a separate RAW-to-NV12 SOFTWARE conversion route
(E004kr/E004kp/E004kw). The newer pinned libcamera software ISP
delivered only 640x480 XRGB8888/sRGB processed output, albeit
3600 frames in four front/rear/front/rear independent processes,
with all four native graphs neutral afterwards (E004lx). The
libcamera test did NOT prove high-resolution processed video,
normal-user access or permanent daily-use camera service.
Both reopened libcamera streams had a roughly 1s early-frame
pause even though subsequent steady cadence passed.

## Stage 1 — current priority: usable Linux software RGB

Acceptance for the RGB-only first usable release:
1. Integrate ONE tested software-processing path delivering genuinely
   captured, correctly formatted front 1920x1080 NV12 and rear
   3840x2160 NV12 through ordinary independent unprivileged
   application-facing camera endpoints. The earlier RAW-to-NV12
   converter may be productionized instead of requiring libcamera
   Soft ISP to reach those resolutions, PROVIDED measured image
   quality, throughput and integration are sufficient. Do not
   substitute the libcamera 640x480 preview for native resolution.
2. Implement selectable named front/rear endpoints, safe exclusive
   camera/media-route ownership, no concurrent conflicting backends,
   predictable service start/stop, true STREAMOFF/neutral shutdown,
   close/reopen and error/crash recovery, and safe rollback.
3. Verify actual 1080p/4K app-delivered frame size, useful frame rate,
   latency, CPU/thermal performance and meaningful image quality in
   controlled lit scenes (exposure, colour, orientation, noise and
   detail). Diagnose and record the observed approximately 1s
   early-frame reopen interruptions: steady-state success is NOT
   proof of seamless switching. Test sustained capture and repeated
   normal-powered-on service lifecycle.
4. Treat any initial release as RGB-only, opt-in/non-default until
   the functional and hardware safety gates pass. Do not claim
   exact Windows ISP image parity or protected Windows Hello parity
   from successfully delivering 1080p/4K software RGB frames.

All physical tests still require fresh root-private source-pinned
single-use guarded candidates, verified Golden recovery, full neutral
media-graph checks, IR OFF, and no reuse of consumed identities.
SP11 Linux OS-level suspend/standby/resume/hibernate/hybrid sleep
is NOT IMPLEMENTED RELIABLY and is excluded from camera tests;
do not label this platform limitation a camera failure. Normal
guarded reboots and ordinary sensor stop/reopen are allowed.

## E004md actual low-light gain response (2026-09-23)

E004ma selector, E004mb morning dark-scene probe and E004mc same-frame
RAW/NV12 source diagnosis are completed, archived and retired. A newer
unique E004md guarded trial measured physical front source RAW8-upper
p99 21→36 and uid1000 NV12 app Y p99 20→34 after supported gain edits.
The rear source p99 rose 17→21 and app p99 16→20 after supported
gain and bounded exposure edits. Both sensors had exact baseline
control readback restoration and controlled publisher stop143. This
confirms real gain-response data, NOT visibly recognizable images,
calibrated RAW black level/colour, normal dynamic 3A, or Windows parity.
The enclosing E004md runner FAILED due to a stale predecessor-status
string check AFTER inner tests; final independent candidate graph/FD
checks did not run. Automatic Golden recovery verified and all E004md
assets retired. Never retry that identity. Before any fresh guarded
physical trial, run tools/camera-validator-contract.py on its fresh
runner/paired validator and prevent stale cross-experiment literals;
prioritize offline gain/exposure policy and controlled-lit RGB scene
visibility with source-format/black-level checks. Keep IR off and
never initiate OS system sleep. Evidence: E004md RESULT.json.

The camera-free standalone full-precision RAW10 primitive at
`rgb/iq/raw10_unpack.h` preserves both previously discarded low bits
and validates the native front/rear packing and rear stride padding.
It is unit-tested but not integrated into the live publishers. In a
FRESH guarded lit-scene candidate, test real black-level/channel
statistics before any auto-exposure or tone-curve claim; neither
this offline primitive nor E004md gain-response numbers establish
recognizable images.

The maintained direct publishers now contain a default-disabled
`SP11_CAMERA_ALLOW_RAW_PROFILE` diagnostic for sparse same-frame full
10-bit R/G0/G1/B source statistics. Both front/rear fake-device lifecycle
suites and synthetic native full-frame packing tests pass. It was physically exercised in the fresh guarded E004mf/E004mg
one-shots; a raw histogram still cannot prove recognizable detail
or an optical black-level calibration.

## E004mg private local RGB optical proof — image usability still open

A new source-pinned E004mg physical one-shot captured real front1080p
and rear4K RGB PNGs **only on SP11** (`~/Pictures/SP11-Camera-Private-E004mg/`).
Numerical analysis of the locally downsampled images found front
luminance p99=9 (99.74% below20) and rear p99=0 (all below20):
physical frame delivery is proven but visually usable imagery is NOT.
Independent same-boot NV12 app Y p99 was 27/17 at baseline and 60/25
after bounded reversible visible RGB sensor gain. Native RAW10 full10
source and same-frame paired RAW8/NV12 checks passed. The RGB PNG and
NV12 studio-range Y values have different scales and can clip near
video black; no converter-only root cause or true optical black level
is established. Both photos are private and not committed/exported.
E004mg consumed/retired, Golden recovered. Prioritize source black
reference and supported exposure control, then opt-in offline-verified
tone mapping and a fresh guarded controlled-light recognizability gate.
A source-only optional NV12 nominal video-range output mapping has since
passed SP11 synthetic GStreamer dark-value round-trip and exhaustive
integer/opt-in publisher fake-device tests; without the flag, front/rear
converter ELFs remain byte-identical to their E004mg-era equivalents.
It has NOT been physically tested and does not compensate for the dark
rear native RAW sensor or establish colour/black/exposure calibration.

## E004mh physical opt-in video-range and private baseline/gain image gate

A completely fresh/consumed E004mh boot physically ran both source-locked
studio-range-enabled front1080/rear4K software publishers, ordinary UID1000
applications, same-frame RAW10/NV12 diagnostics, and bounded native sensor
gain/exposure with exact restore. Four original RGB PNGs remain ONLY ON
SP11 at `~/Pictures/SP11-Camera-Private-E004mh/` (0700/0600). All
normal STREAMOFF/native graph neutral/Golden return checks passed and
candidate assets were retired, IR off, no Linux OS system sleep.

Downsampled RGB PNG luma p99 front baseline/gain 22/51 and rear 15/20;
independent NV12 app Y p99 front 37/62 and rear 31/37. Real front
source RAW-upper8 p99 26→56.3333 and rear17→27. The baseline rear
RAW10 green is still tightly clustered around code64–70; that is NOT
a verified optical black offset, and amplified signal may include noise.
Earlier E004mg non-studio-range preview p99 front9/rear0 was captured
under separate uncontrolled morning light. Thus the synthetic range
fix is independently verified and physical studio-range images are no
longer numerically zero, but a matched scene luminance ratio and
recognizable visual detail remain UNPROVEN, especially at the rear.
Normal publisher release/default still excludes studio range opt-in;
no colour/AE/black-level calibration or Windows ISP parity is claimed.

Next, obtain a controlled visible-light target/black reference and
validate optical source/exposure plus a bounded noise-preserving tonal
processing proposal offline BEFORE a fresh camera one-shot; never reuse
E004mh. Do not substitute another delivery-only PASS for the usability
gate or activate protected IR/OS system sleep.

## E004wn fresh Windows oracle: current rear corner is rendered bright

The rear camera may physically face a darker, relatively featureless corner
(as reported by the user), so comparing front vs rear physical signal is NOT
an equivalent scene exposure test. To check that explanation, a new
single-use E004wn Windows-only numeric oracle sampled exact SP11 front1080
and rear4K colour WinRT NV12 at 11:16 BST, about 18min after E004mh
Linux. Windows rear mean Y=148.24–148.55, P01=119–120, P99=169,
with **zero** sampled Y below32, and 8x8 tile means std ~11.2. Windows
front mean Y~123.27–123.70. Both ExposureControl.Auto=true, nominal
ticks5000 (not a native sensor-register exposure readback). This
Windows rear capture is NOT similarly near-black to the recent Linux
rear app baseline Y P99=31/adjusted37 or Linux RGB PNG P99=15/20.

A dark/featureless corner alone is therefore insufficient as a factual
explanation for *both* platforms' current rendered output, but it remains
possible that lighting/direction changed or Windows automatic exposure
compensates for the corner. The capture times, raw/native sensor exposure
units, image processing and data summary statistics were NOT matched.
Do NOT diagnose sensor failure or calculate a cross-OS brightness ratio.
Use a deliberately fixed bright and dark physical target, confirm field
of view and illuminance in both boots, collect comparable native NV12
Y histograms plus Linux RAW10 channel and exposure/gain metadata, and
then test bounded automatic-exposure/tonal processing in a fresh guarded
Linux one-shot. E004wn task was retired and SP11 returned to protected
Golden; never reuse E004wn, E004mh or other consumed identity. IR OFF,
no Linux OS system sleep.

## E004mp bounded rear extra analogue gain: signal rises, usability still open

New E004mp one-shot ran source-locked front1080/rear4K RGB, UID1000 apps,
full10 RAW10 channel histograms, same-frame RAW-upper8/NV12 telemetry
and exact native control restoration. Only the **rear analogue gain target**
changed versus E004mh (256→512); rear trial exposure3200 and digital
gain2048 were unchanged, frame timing/FPS unchanged and IR OFF.
The rear source green0 RAW10 P01/P99 baseline64/70→gain73/140;
p99−p01 6→67, while ordinary-app NV12 Y p99 31→48 and private
RGB preview downsampled Y p99 15→30. The gain-dependent shift of P01
means full10 code64 is not a calibrated optical black value. More
spatial contrast MAY mean optical scene detail and/or fixed pattern noise.
Local-only 12x16-tile image brightness correlation rear baseline/gain
r0.806 and E004mh-vs-E004mp gain r0.977 suggests a repeatable pattern,
but cannot identify it as usable scenery or prove SNR/scene recognition.

All four original PNGs remain ONLY on SP11 at
`~/Pictures/SP11-Camera-Private-E004mp/` (directory0700/photos0600),
no pixel data/image hashes committed or sent. Candidate consumed and
retired after automatic protected Golden boot
`b3692bba-238a-4885-8f3b-9332c8284b51`, native neutral and clean
overlap guard. The rear native exposure current mode max is3206 lines,
and trial3200 is almost full-frame; longer exposure needs explicit
separate VBLANK/FPS verification rather than a silent control tweak.
Next controlled fixed-lit target/actual black/noise and per-gain
RAW10 scene checks must precede robust automatic exposure or tone
mapping. Windows E004wn rendered a much brighter rear at another time,
but scenes/time and statistics were not matched. Default/Golden camera
still not enabled, IR OFF, no Linux OS-level sleep.

## Camera-free fixed-frame envelope and temporal source preparation (after E004mp)

A read-only E004mp evidence validator now checks exact native V4L2
bounds, previous control readbacks/restoration and ordered full10
Bayer channel quantiles. Under the accepted current frame timings,
front exposure3546 leaves 4 lines vs active max3550 and rear3200
leaves 6 vs max3206. It explicitly REFUSES to promote an uncalibrated
p01 to sensor black or approve further native writes/AE/tone mapping
without a dark reference and a lit target. An independent camera-free
front/rear RAW10 two-frame temporal/spatial aggregate primitive has
passed synthetic constant/fixed-pattern/temporal-jitter tests but is
NOT integrated into live publishers and has captured NO NEW frames.
Stable spatial correlation can arise from sensor FPN as well as a
scene; temporal changes can reflect illumination flicker or motion.

Admission for the *next* physical one-shot is an actual distinguishable,
visibly lit target IN BOTH physical fields of view, a separate dark
reference, bounded timestamps/exact controls and private on-SP11 image
verification. Do not run another uncontrolled dark-corner gain trial
or silently change FPS/IR/Golden/Linux OS-level sleep. See
`src/sp11-camera-stack/rgb/iq/FIXED-TARGET-ACCEPTANCE.md`.

## E004wp fresh Windows oracle: rear receives ample rendered luminance

At 11:58 BST a **new** one-shot SP11 Windows Color VideoRecord NV12
oracle sampled eight 4K rear frames: Y mean149.15–150.41, P01 118–119,
P99 169–171, zero samples below64; 8x8 tile-mean Y std11.46–12.06
and horizontal64px/vertical32px mean absolute Y changes~3.3. The
front1080 mean Y124.87–125.19. WinRT RGB ExposureControl.Auto=true
for both; nominal ticks5000 is not verified equivalent to native
Linux sensor-register exposure. This independently reinforces fresh
E004wn Windows rear mean Y~148 at 11:16 BST, so Windows can render
the current corner *brightly*, with nonzero spatial contrast. It
cannot alone establish recognizable objects or sensor RAW scene SNR.
A 960x540 rear luma-derived grayscale PNG remains strictly LOCAL on
SP11 Windows user-private Documents E004wp folder (Geoca/SYSTEM/
Administrators ACL), NEVER exported/hash committed; user can inspect
it locally to confirm scene geometry. No Windows vs Linux same-time,
identical exposure/light/metrics experiment was achieved.

E004wp unique Windows identity was consumed, single-use task retired,
auto-return to protected Golden Linux verified at boot
`fe4bcab8-a209-4466-819e-0ce7fbeabc03`. No camera processes,
IR/illumination or Linux system sleep. Next meaningful Linux ISP/AE
quality test still requires a fixed visible scene and dark reference;
not another uncontrolled rear corner gain run.

## E004ng + E004nh six-patch screen colour reconstruction and SP7 lower LCD defect caveat

User reports SP7 LCD has a THICK FAULTY BAND along LOWER EDGE.
E004ng original six-patch known digital RGB chart occupied
entire SP7 screen, so old approximate patch WHITE/BLUE colour
evidence can include this faulty region and screen geometry
was not independently registered. E004ng original full
one-shot also failed front 630->660 gain window28.454<29fps,
candidate consumed/auto Golden retired; its real observed
magenta image and native two-green-site mismatch are
diagnostic ONLY, not proof of actual sensor BGGR Bayer
pattern or actual loss of blue. The maintained rear media
format reports GRBG and MUST NOT be altered by guesswork.

Fresh E004nh opt-in only rear SOFTWARE BGGR hypothesis
was source-locked and synthetic Bayer-primary tested.
NEW KNOWN CYAN/RED/GREEN/BLUE/GRAY/WHITE target confined
to UPPER60% of SP7 1368x912 display, BOTTOM40% black/
untrusted and EXCLUDED from chart due defective LCD.
SP7 interactive task visible19:15–19:23, removed after
physical capture; desktop restored. Genuine E004nh camera
captured original private front1080/rear4K baseline+gain
optical previews, real rear three full10 RAW10 sequential
pairs, front/rear native sensor controls EXACT restored,
selector front->rear->off->quit, both source full-run
near30fps zero source gaps and every rear gain interval
>=29fps. But actual FRONT gain frame630–660 interval
28.0310fps < immutable29fps gate, so ORIGINAL E004nh
full-run FAILED, its downstream independent bt601 and
final119-edge neutral checks were NOT executed. Candidate
no GPU/panic/thermal fault, automatically returned Golden
boot3b1410be-fe1c-4148-a17d-1630a5deaf33, unique
root/GRUB/boot/systemd assets retired and identity
CONSUMED NEVER REARM. Golden normal CFA/IR/camera/tone
defaults unchanged.

Original photos never left SP11. Local independent
whole-image bright Y>96 RGB scalar means changed from
older E004ng GRBG/full-screen(196.423,126.612,195.523)
predominantly MAGENTA to new E004nh opt-in BGGR/upper60
(103.427,165.751,123.292) GREEN-DOMINANT. Since
screen placement/content geometry differs and OLD photo
may include user's known faulty lower LCD, these
UNREGISTERED global aggregates do NOT independently
prove physical sensor BGGR order, per-patch accurate
RGB, blue reconstruction, actual fine detail, white
balance or OEM Windows ISP parity. This is an important
isolated software CFA hypothesis requiring a fresh
controlled same-upper-screen chart, independently
REGISTERED patch ROI and native per-site RAW10 sensor
response under matched controls; no premature normal
camera promotion. Text-only results E004nh/RESULT.json
and evidence/REAL-PRIVATE-OLDER-GRBG-VS-NEW-UPPER60-
BGGR-GLOBAL-COLOUR-SCALARS.json. Four private original
front/rear baseline/gain photos only same SP11 owner
geoca dir0700/photos0600.

## E004ne real screen-scene independent acceptance PASS; older OEM Windows photo still brighter

After original E004nd new-scene run FAILED original RAW10
early frame600/601 sampling just91.489ms after native controls
settled (strict min>=300ms), new distinct unique consumed
E004ne source-locked physical trial boot0b39c7b1-3b60-4a69-
aa08-4da5a4eddbd3 kept strict>=300ms requirement and
instead audited two LATE actual gain RAW10 consecutive native
pairs630/631 and660/661, measured1704.143ms and2705.642ms
after actual native gain settled. Baseline90/91 also valid.
ORIGINAL full trial PASSED raw sensor source and 29fps whole
plus four real 30frame gain intervals on both front1080 and
rear4K, zero source gaps, actual native control readback/
restoration, ordinary UID1000 app both cameras baseline/gain,
strict real V4L2 source and GStreamer consumer bt601, front->
rear->off->quit selector and original independent final
119-edge complete media graph neutral/GPU checks. Newly
repositioned rear gain native NV12-Y p01/p50/p99=29/31/141
spread112: genuine nonflat image, high gain dark-only rear
tone/temporal CORRECTLY BYPASSED, NOT a fake dim-scene
enhancement. Front gain tone pilot not claimed in this FOV.

Candidate automatically returned protected Golden bootafc8da03-
2eba-40fa-a451-313929ec2148; unique camera root/GRUB/boot/
systemd fully retired, saved Golden boot intact, normal RGB
camera/IR/processing default unchanged. Four original
front/rear baseline/gain private photos ONLY same SP11
user-private dir0700/files0600.

Separate older real OEM Windows E004wq rear 4K Color
WinRT private original photos were read on SAME SP11
via Windows NTFS mounted STRICT READ-ONLY underneath
root-only0700 directory and cleanly unmounted immediately
after scalar processing. New E004ne real Linux rear4K
gain preview vs old OEM Windows original matched480x270
display-luma mean Windows60.25587 vs Linux36.35741;
Y>=96 bright fraction Windows25.4753% vs Linux10.6535%.
Coarse sigma8 correlation0.900138 (bounded shift best
0.91043) supports matching broad scene despite different
time/lighting/target content, while fine highpass
correlation0.030744 does NOT prove matched fine detail
or screen text. Prior E004nd Linux mean36.923, so merely
fixing source settle timing did NOT make image brighter.
Windows OEM auto exposure vs Linux fixed native tuple,
provisional original Windows BT709 colour preview vs Linux
BT601 consumer, screen image content/light and independent
25–40min boot times remain uncontrolled. Do not claim
full Windows ISP parity, actual object recognition,
calibrated white balance or genuine pixel-perfect matched
source. A labelled user-private optical side-by-side
derived from originals was generated ONLY SP11
~/Pictures/SP11-Camera-Private-E004ne/
PRIVATE-SP11-REAR-E004WQ-OEM-WINDOWS-vs-E004NE-LINUX.png
owner geoca dir0700/photo0600, NEVER share/export it.
Git has scalar-only numerical comparison and code, no
photo/pixel array/RAW/thumb/photo hash.

Same original E004ne session proves native rear RAW10 signal DID
increase under gain: sampled full10 G0 p99 baseline100 -> gain628
and RAW-upper8 p99 24 ->144. Ordinary rear UID1000 app p99
baseline153 -> gain141 is not evidence gain darkened the sensor:
baseline dark-scene tone artificially raised native input Yp99
37 to153; later high-gain nonflat scene correctly BYPASSED
tone with input/output Yp99 both141. Comparing processed
baseline/gain as if both were untoned native exposure is invalid.
Bounded sampled blue RAW10 max906/1023 at gain calls for
per-channel highlight-headroom checks, but is not a measured
full-frame clipping rate or optical black calibration. Windows
OEM auto-exposure, scene content and lighting are NOT matched;
do not boost gain merely to equalise global Windows mean.
See scalar-only E004ne/evidence/
SCALAR-ONLY-NATIVE-GAIN-VS-DISPLAY-TONE-CONFOUND.json.
No image/pixels/RAW/photo hashes exported; Golden camera unchanged.

Next independent target: native auto exposure and true
shadow signal/detail versus fixed supported exposure/gain,
known illuminated and dark reference, controlled
lighting/registration and non-oscillating bounded adjustment
that does not alter FPS/VBLANK or overbrighten noise.
No automatic Golden daily camera promotion yet.
Evidence E004ne/RESULT.json and evidence/
PRIVATE-CROSS-OS-NEW-REAR-LINUX-vs-OEM-WINDOWS-SCALARS.json.

## E004nd/E004wq original rear photos after moving SP11 toward SP7 screen: Windows and Linux same scene locally compared

Fresh distinct E004nd Linux real rear4K candidate captured current rear scene original RGB PNG and native input gain Y p01/p50/p99 30/32/141, versus old corner E004nc31/34/38. Real native front1080/rear4K UID1000 apps, selector front->rear->off->quit, native control restore, automatic protected Golden return and candidate retirement. ORIGINAL E004nd full one-shot FAILED separate RAW10 gain pair frame600 timestamp91.489ms after exposure/gain controls settled, less than required300ms; later frame6301095.513ms after settle passed timing. This test failure is not evidence of a machine crash or full pass.

NEW separate Windows E004wq OEM rear4K Color WinRT actually captured eight native NV12 frames (native Y mean67.26-67.49, p99=175) and eight front1080 frames. Windows user-private original rear 960x540 colour photo and same-frame grayscale photo verified with Geoca/SYSTEM/Administrators-only ACL. Source-locked single-use task set 300s automatic reboot BEFORE camera access, exited0 and retired, protected Golden Linux return observed. All real optical images, thumbnails, raw pixels, private SP7 screen content and photo hashes remain ONLY on SP11, never chat/Fabric/Git/other hosts.

Same SP11 read-only NTFS matched Windows original OEM grayscale and Linux original rear4K gain RGB, both using EXACT original 4K native8x pixel stride to480x270. Windows matched display grayscale mean60.2559 median45, Linux displayed RGB mean36.923 median15.353. Windows Y>=96 bright area25.4753%, Linux10.8102%; 99.7645% of Linux bright region is within Windows bright region. Coarse sigma8 spatial correlation0.902659 (small-shift best0.912981) supports shared broad screen-like scene, but screen text/object identity was NOT independently recognized. Fine sigma2 highpass correlation0.000851 (best small shift0.091969) does NOT establish identical optical fine detail or camera noise. Different native exposure/ISP, provisional Windows BT709 preview render, changing screen content and captures ~10 minutes apart: no exact scene match, true sensor colour calibration, measured white balance or full Windows ISP parity verdict. Windows NTFS cleanly unmounted.

Labeled same-SP11 user-private side-by-side genuine original Windows LEFT and Linux RIGHT photo:
 /home/geoca/Pictures/SP11-Camera-Private-E004wq/PRIVATE-SP11-REAR-NEW-SP7-SCREEN-WINDOWS-vs-LINUX.png
dir0700/photo0600, NOT exported. Original Windows photos remain only SP11 Windows user Documents, original Linux photos only SP11 user-private Pictures. Normal Golden camera/IR/tone/temporal unchanged. E004nd/E004wq consumed, never rearm. Source and global-scalar-only evidence: E004wq/RESULT.json, E004wq/SCALAR-ONLY-REAL-WINDOWS-LINUX-NEW-SCREEN.json. Next independently test safe Linux rear highlight/shadow rendering, actual exposure/gain and fixed lit/neutral/dark references without losing 4K30 or prematurely enabling optional tone by default.

## E004nc real front1080/rear4K ordinary app BT601 matrix caps, but independent full-run rear darkness gate fails

A fresh consumed source-locked E004nc physical candidate boot
92954eda-392b-4557-924c-1d39151a7c23 captured both visible
RGB cameras at full 1080p/4K and reported BOTH independent
real V4L2 S_FMT/G_FMT NV12 explicit SMPTE170M colorspace=1,
ycbcr/quantization/transfer DEFAULT=0. Strict Linux UAPI
effective normalization accepts 601/limited/709 and still
rejects unspecified or wrong actual colorspace. All FOUR
ordinary UID1000 front/rear baseline/gain app probes,
90 frames each, independently negotiated actual v4l2src
NV12 input bt601 AND I420 consumer bt601. Real front
source30.005fps/rear29.948fps, zero gaps, four separate
30frame gain windows each>=29fps, exact native controls
restored, front->rear->off->quit selector and three rear
full10 RAW10 temporal source pairs passed.

ORIGINAL full E004nc one-shot runner FAILED its pre-existing
rear tone/temporal visual-quality gate: actual rear gain scene
was still a very dark near-flat corner, native preview input
Y p01=31/p50=34/p99=38 spread7 below min8, so the
rear Y-only tone SAFELY BYPASSED and temporal filtered0 frames.
Original independent rear filter acceptance therefore failed
as intended; original downstream independent BT601 validator,
front tone and final complete119-edge graph neutral gate did
NOT run. A separate read-only POSTHOC run of only the
colour-specific validator on SAME original physical scalar
source and UID1000 app metadata PASSED; do NOT relabel
original full runner pass. No actual optical neutral colour
chart, true signal detail, scene lighting or matched Windows
ISP colour parity has been verified.

Automatic reboot reached protected Golden boot
4d68e367-b5e6-44dd-bf4f-0123366449c5, no matching
candidate GPU/thermal/panic fault, unique candidate root/
GRUB/boot/systemd assets retired. Four original photos ONLY
SP11 owner geoca private dir0700/photos0600; Git contains
scalar/text evidence exclusively, no optical photos/pixels/
RAW/thumbs/image hashes. Normal camera/IR/tone/temporal
defaults unchanged. Next make colour metadata/app-caps
acceptance independent of dark-rear preview IQ rather than
lower the flat-scene tone bypass or produce unproven detail.
See E004nc/RESULT.json, ORIGINAL-GATE-FAILURE.txt and
POSTHOC-REAL-BT601-SOURCE-AND-UID1000-APP-CAPS.json.

## E004nb prestream V4L2 exact readback: explicit colorspace retained, 3 default zero fields

Fresh consumed/retired E004nb distinct one-shot physically logged first
front1080 V4L2 NV12 requested `(colorspace=1,ycbcr=1,quant=2,xfer=1)`
and successful returned `S_FMT` AND separately queried `G_FMT`
`(1,0,0,0)` with unchanged expected geometry and no errors.
V4L2 UAPI defines zero as DEFAULT for these three trailing fields;
for an NV12 YCbCr stream with explicit SMPTE170M colorspace,
header mappings give effective 601/limited/709 respectively.
Original literal exact equality was overly strict, so candidate
failed before sensor streaming, zero front/rear photos/frames,
selector failed closed. This does NOT prove negotiated real UID1000
GStreamer source/consumer caps or actual colour improvement.
Candidate automatically returned Golden, unique assets retired,
no new GPU/panic/thermal marker, prior E004my full RGB pass intact.
Next source-only strict effective-default normalization and negative
camera-free tests; any REAL colour claim requires a new separately
source-locked one-shot checking both actual v4l2src and independent
normal UID1000 consumer caps plus all original FPS/neutral gates.
See E004nb/RESULT.json + evidence/front-SERVICE-STDERR.txt.

## E004na physical original trial FAIL PRE-STREAM: exact loopback S_FMT metadata readback mismatched

After entirely synthetic 1080p/4K proof of existing provisional
BT.601 NV12 Y/Cb/Cr encoder vs unspecified GStreamer BT.709
decoder at HD/UHD, a NEW single-use original E004na trial
attempted explicit SMPTE170M(1)/YCBCR601(1)/limited quant2/
xfer709(1) V4L2 output. First FRONT publisher S_FMT returned
a struct that failed its exact FOUR-field echo gate; original
stderr E004NA_V4L2_BT601_NATIVE_LOOPBACK_S_FMT_COLOUR_TAG_MISMATCH,
captured=0/published=0. Actual front UID1000 app got zero frames,
no rear source frames, no actual real native front/rear BT.601
caps or FPS/brightness measurement on E004na, no original
optical photos created. Selector failed closed. The original
program only printed a generic mismatch, **NOT actual returned
colour field integers**. We CANNOT assert which V4L2 field was
different, whether loopback normalized the metadata, or
whether the physical source had a colour problem.

Candidate Linux boot25434aee-c0fb-40ba-8128-62ffb6984227
automatically returned protected Golden boot
c6312e00-f579-4ba2-a276-365fc311ce1f without matching
GPU/GMU/DPU fault, panic or thermal shutdown. Unique E004na
is fully consumed/retired including root/GRUB/boot/systemd
stages, no active camera/IR and normal Golden settings
unchanged. Previous independently PASSED E004my original
front1080/rear4K brightness/29fps/full neutral remains valid.
Do NOT rearm E004na or claim the new colour metadata
works on actual UID1000 video. Next inspect actual
v4l2loopback V4L2 S_FMT implementation camera-free,
then a fresh unique sealed bounded diagnostic that prints
*all returned fields* prior to rejection IF software source
analysis cannot isolate the mismatch. Don't weaken strict
colour/FPS/source gate or turn normal camera settings on.

## E004na high-resolution colour matrix/metadata mismatch: synthetic proof, candidate-only fix

Current software Bayer->NV12 Y/Cb/Cr uses provisional BT.601-like
coefficients, yet prior loopback publisher output V4L2 colorspace
was unspecified. Actual SP11 synthetic-only GStreamer
appsrc->videoconvert->RGB selected BT.709 at 1920x1080 and
3840x2160, while 128x64 defaulted BT.601. Known generated red
RGB(192,32,32) round-tripped HD/UHD default to RGB(203,44,29),
but explicit BT.601 returned RGB(190,29,31). The previously
validated Y-only studio-range test used a neutral low-res patch
and could not expose this chroma-matrix error.

The new candidate-only flag SP11_RGB_NV12_BT601_TAG=1 for both
maintained RGB publisher sources requests exact V4L2
SMPTE170M/YCBCR_601/limited-quantization/XFER_709 metadata
and fails BEFORE stream-on if S_FMT returns a different tag.
Default normal camera remains unchanged. Tests on generated
colour patches, exact 1080p and 4K real GStreamer consumer
geometry, struct negative fields and opt-in front/rear fake
lifecycle PASS; NO actual physical UID1000 V4L2 caps yet.
A new distinct guarded single-use candidate must check native
real consumer negotiated BT.601 plus strict old source/FPS/
sensor controls/final-neutral acceptance before claiming
a real physical colour-matrix match. Not sensor colour chart
calibration, white balance, gamma, optical detail or
Windows OEM ISP parity.

## E004mz two-boot PRIVATE same-host fine vs coarse image-repeatability: detail still unproven

Read only eight existing E004mx/E004my owner-private front1080/rear4K
baseline/gain RGB original photos locally on protected Golden SP11,
no hardware/IR/reboot/pixel transfer and synthetic scalar-correlation
unit tests PASS. Identical 4x original pixel sampling and Gaussian
lowpass sigma8 / fine highpass sigma2, plus bounded +/-8 original
pixel shift search: FRONT gain highpass cross-boot corr0.841871,
coarse corr0.990579, BUT near-black front baseline highpass
corr0.806122 and same-boot front baseline-vs-gain highpass
corr0.445/0.431. Repeated FRONT fine-scale image pattern may
be actual optical structure OR persistent sensor/demosaic patterns,
not proof recognized scene detail. REAR gain coarse corr0.999493,
fine highpass cross-boot only0.047818 (not improved by bounded
shift), baseline fine corr0.087524; same-boot baseline/gain
fine corr<0.008. Coarse spatial shape persists in dark rear
corner while the fine variations do NOT persist at identical
pixel coordinates. Cannot attribute them conclusively to
temporal noise instead of scene/pose/focus/light differences.
Do NOT sharpen rear current dark-corner output based on an
apparent histogram spread, claim recovered detail from Y-only
tone, or claim fixed-pattern sensor defect. Known lit
optical target/dark reference/colour chart remain absent.

All original optical PNGs strictly SP11-private; Git has only
scalar results, scripts and generated-array synthetic tests.
Golden default front/rear camera/IR/tone/temporal unchanged.
Evidence E004mz/SCALAR-ONLY-PRIVATE-SP11-REPEATABILITY.json.
Next camera-free RAW10 Bayer->NV12 colour pattern validation,
then controlled target and independent optical dark reference
before a new distinct physical IQ one-shot.

## E004my new source-pinned real FRONT1080 gain tone plus rear4K NEON: ORIGINAL complete independent trial PASS

Unlike E004mx (original validator FAILED, posthoc real-text
analysis passed), fresh distinct one-shot E004my source-locked
candidate boot9319f52d-daf3-43e1-afc8-6b1f45d3921e
successfully ran the ORIGINAL corrected independent real front
gain-only NV12 Y output brightness checker to completion,
including separately original real UID1000 app p50>=106/p99>=154,
unmodified front baseline p99<=37, same-frame front native
RAW10/converted untoned source comparison and unchanged UV.
Real front source30.0311fps zero sequence gaps, each of four
settled high-gain 30frame intervals30.2703/29.7609/29.9367/
29.9514fps all met unchanged>=29fps requirement. Existing rear
NEON 4K comparator source29.8243fps with gain window
29.9727/29.9661/29.9139/30.0018fps each>=29,
gaps0, three real RAW10 full10 consecutive source pairs.
All exact supported front/rear native gain/exposure controls
restored, ordinary uid1000 app front->rear->off->quit exclusive
selector, complete independent FINAL 119-edge media-graph
neutral proof, no GPU GMU/Adreno/DPU/panic/thermal fault.

Automatic firmware reboot returned to protected Golden Linux
boot725cbcd3-9339-446b-ad42-f0d3e31ac3d7 on 2026-09-23
15:55:13 BST. Distinct E004my consumed NEVER rearm; unique
root/GRUB/boot/systemd candidate retired, normal camera/IR/
tone/temporal defaults unchanged. E004mu's earlier GPU and
firmware-reboot hang cause is still UNKNOWN.

SP11-private same-host original front/rear baseline/gain
photo scalar-only analysis: front baseline display gray mean15.097
p99 20, front toned gain gray mean106.122 p99 155,
rear baseline14.077 p99 15 and rear toned gain142.646
p99 163. Front gain ~0.30% 4x-stride RGB samples had any
channel>=250; uncalibrated highlight/demosaic/colour and
actual optical scene detail still require independent
fixed visible target and separate known dark reference.
Photos remain ONLY on SP11 user-private
~/Pictures/SP11-Camera-Private-E004my/ 0700/0600;
no pixels/photos/thumbs/RAW/photo hashes uploaded or committed.
This is a REAL 1080p/4K fps/brightness/selector/neutral SUCCESS,
but NOT OEM Windows ISP visual IQ, true noise/SNR, real
object recognizability, native AE/white balance or an
everyday configured camera service. DO NOT silently enable
default tone/exposure profiles. See E004my/RESULT.json and
REAL-FRONT-GAIN-TONE-RESULT.json, FINAL-NATIVE-NEUTRAL-PROOF.txt
and LOCAL-SP11-ONLY-PRIVATE-RGB-AGGREGATES.json.

## E004mx front1080 opt-in display-luma lift: REAL measurement, original independent acceptance FAIL (validator typo)

A fresh E004mx one-shot source-locked candidate captured real
front1080/rear4K native RAW10->NV12 visible RGB in ordinary UID1000
applications with exact supported sensor control readback/restoration.
An isolated FRONT-only gain-gated studio-range Y preview LUT
left native front baseline untoned (Yp99~37), and under the
ALREADY independently supported front gain tuple transformed source
videoYp01~30/p50~33/p99~57 to displayYp01=100/p50=106/p99=154.
Front ordinary app measured 90 source-backed gain frames with sparse
median>=106/p99>=154, versus prior E004mv untoned front gain
median~34/p99~61. Real front704 frames/23.430015s=30.0469fps,
zero source gaps, combined converter+tone12.989ms; independent
front high-gain 30frame window FPS29.899,30.0707,30.0171,29.9861,
ALL meeting unchanged29fps. Existing rear-only 4K NEON branch passed
29.9475fps and all four separate gain FPS windows>=29 as control,
and three real full10 rear RAW10 temporal source pairs passed.

Actual E004mx original full one-shot FAIL_RC=1: original installed
Python front timestamp parser included a literal ASCII backspace
instead of intended regex word boundary before frame=. Native front
570/600/630/660/690 timestamps WERE present, but the independent
original validator falsely reported MISSING. This failure aborted
runner before its independent final neutral post-check; do NOT
claim complete candidate acceptance from subsequently re-running
the corrected script OFFLINE on already captured real scalar logs,
even though it re-parsed all front gain/FPS/control evidence PASS.
E004mx selector itself completed front->rear->off/quit and restored
controls; automatic reboot to protected Golden Linux
610a672b-fdb1-4289-be9f-1c8fc44a79dd completed, GPU GMU/DPU
fault absent in candidate journal; consumed unique root/GRUB/boot/
systemd stage RETIRED and Golden idle. Earlier E004mu GPU/failed
firmware reboot root cause STILL UNKNOWN. Never rearm E004mx.

LOCAL private PNG scalar-only front display check E004mv old gain
mean19.628/p99 47 (~87.1% samples below25) versus E004mx new
gain mean106.338/p99 155 (0% below25), baseline still gray mean
~15/p99 21. New gain ~0.34% pixels with any RGB channel>=250;
this is not a colour/ISP parity or true image detail assessment.
Different boots/time/light, no known neutral chart or identifiable
optical target; no photos or pixels viewed by assistant, exported to
chat/Git or other devices. Four originals remain only on SP11
~/Pictures/SP11-Camera-Private-E004mx/ owner geoca dir0700/files0600.
Source-only corrected validator and 35 offline regression tests
PASS. To certify the full independent FRONT preview candidate, a
NEW separately guarded unique physical one-shot must complete the
fixed original script through neutral/GPU/safety and automatic
Golden return; normal maintained front camera/front tone OFF remains
unchanged until optical/colour/noise and routine service acceptance.
Evidence E004mx/RESULT.json + evidence/POSTHOC-FRONT-TONE-VALIDATION.json
+ SP11-LOCAL-FRONT-TONE-PRIVATE-RGB-SCALARS.json.

## E004mw SP11-private existing photo scalar quality audit + software-first brightness policy

Read only four existing E004mv original front/rear baseline/gain user
photos LOCALLY on SP11, without activating cameras, moving pixel
files or exporting pictures/hashes/thumbnails/per-tile images.
Four-channel means and 4x-stride luma aggregate show front gain RGB
still extremely dark (display gray mean19.628/p99 47, ~87.1% samples
below25), whereas rear gain toned display gray mean144.493/p99 166.
Both baseline photos remain near-black. Front current fixed native
gain alone did NOT produce the Windows-like bright appearance.
Rear reconstructed green pixel 2x2 parity spread ~5.03 display
levels vs baseline~0.23, with real rear RAW10 G0 vs G1 p50 code
87 vs80 at high gain. This could arise from CFA/ISP/sensor/scene
or uncalibrated low-light processing; no sensor defect, green
correction, calibrated colour balance, true black, sharpness or
recognizable scene is demonstrated by these aggregate scalars.
No gray card, colour chart or controlled known dark optical reference
has been verified. Review full E004mw scalar-only report before any
white balance or sharpening changes.

Maintained IQ preview_brightness_policy.py is camera-free only and
returns non-executable bounded front/rear baseline/trial profile
plans: no sensor writes or new native gain values, actual>=29fps
and 30 consecutive source frames, exact sensor register/control
bounds readback, IR-off/exclusive route, no native frame-timing
change, no highlights clipping, and once-only gain probe with
flat/too-dark trial rejection. Tests PASS on synthetic controls.
Actual closed-loop automatic exposure and front/rear visual IQ
are NOT yet validated. Normal Golden camera remains unchanged.

## E004mv opt-in AArch64 rear NEON: real 4K near-30fps PASS

After user permission to continue guarded hardware work despite an
earlier firmware restart leaving SP11 powered off, a BRAND-NEW unique
E004mv one-shot physically PASSED native front1080/rear4K RGB
and ordinary UID1000 apps, real full10 RAW10 source, exact supported
sensor control baseline/trial/restoration, independent front/rear/off
routes and final neutral graph with no IR or native FPS/VBLANK changes.
Fast explicitly opt-in rear Y-only 16-lane NEON is bit-for-bit equal
to earlier scalar algorithm on all generated full4K NV12 source,
history, chroma and summary stats across motion/scene-change tests.
Real rear filter141 frames mean CPU0.318ms vs E004mu 3.831ms;
combined real conversion+tone+filter20.454ms vs23.695ms;
true source711 frames/23.739465s=29.9501fps zero source gaps.
Separate measured high-gain 30frame windows achieved29.8803,
30.0039,29.9136,30.0933fps; each passed SAME strict29fps
gate vs E004mu physical fail28.8485fps overall, ~24.7-24.9fps
under higher gain. Do not relax FPS gate.

No Adreno GPU fault/GMU OOB timeout/DPU hangcheck in this candidate
boot; one successful automatic reboot to protected Golden
08c11e69-283f-47e5-acea-e7e8431429e8 does NOT identify or solve
earlier E004mu GPU/final-firmware-restart failure. Unique candidate
consumed and fully retired; Golden saved_entry intact/next_entry
empty, default RGB camera + rear tone/temporal OFF/unchanged, IR off.
Four original front/rear optical RGB PNGs stay ONLY SP11 in private
~/Pictures/SP11-Camera-Private-E004mv/ owner geoca dir0700/files0600;
Git evidence text/scalars only, no private pixels/photo hashes.

The achieved near-30fps real source plus exact synthetic filter
output does NOT establish visible optical object detail, true noise,
correct colour/white balance, safe low-contrast motion, bounded
native auto exposure, Windows IQ parity or reliable routine camera
service. Continue software-first, no automatic daily filter activation.
Future physical tests require fresh single-use guarded boot and user
is aware firmware may again require physical power-on on failure.
See E004mv/RESULT.json and evidence/REAL-REAR-TEMPORAL-PREVIEW-RESULT.json.

## E004mu rear 4K opt-in temporal-filter physical failure and reboot safety HOLD

On new uniquely guarded source-locked E004mu Linux boot, real
front1080/rear4K full10 source and UID1000 app/selector/control restore
passed, and rear opt-in temporal filter processed137 actual frames
with mean CPU3.831ms. At a sparse sample frame the original unfiltered
consecutive luma RMS was5.058 vs filtered output to *previous filtered*
RMS3.515 display Y: these reference different histories and do NOT
calibrate true SNR, motion detail or noise reduction. The real source
reported707 frames/24.507338s =**28.8485fps** and combined mean
conversion/filter23.695ms, zero source sequence gaps. Strict29fps
gate **FAILED**, vs E004ms29.949 and E004mt29.908fps with mean
conversion20.132/20.197ms. Candidate last four high-gain 30frame
intervals ~24.7–24.9fps; DO NOT lower gate to declare success.

Separate GPU/display fault at14:12:49–50 before rear filtering started:
5 GMU OOB timeouts, one Adreno fault and DPU hangcheck involving
`gnome-shell`; other12/13 accessible persisted boot journals lack
that fault. Cannot attribute it to camera kernel, filter or subsequent
reboot failure. Service exited at14:13:30 after validator rejection,
requested reboot; Linux journal reached reboot.target14:13:43 and
closed normally. No new boot logged until user manually powered on
SP11 at14:34:38; firmware reboot handoff/power-state cause unverified.
No kernel panic/OOM/thermal shutdown/new crash dump; thermal peak49.2C,
watchdog warning also in prior SUCCESSFUL reboots. Candidate E004mu
fully consumed/retired and SP11 protected Golden boot57150330-c0a84e72-
b7a3-f8ae790354ed guard PASS, normal camera default unchanged.

**HOLD further unattended experimental camera reboots** until a
separate safe independent reboot/firmware handoff and out-of-band
power recovery mechanism is confirmed. Continue source-only temporal
CPU optimization, real30fps baseline validation and motion/detail
policy research without live camera or system reboot. Preserve
private SP11-only four E004mu original optical PNGs; Git evidence
text/scalars only. See E004mu/RESULT.json and
E004mu/evidence/READONLY-GPU-REBOOT-POSTMORTEM.json.

## Existing Windows rear grayscale preview reviewed locally without reboot

A read-only/no-recovery Windows NTFS mount on SP11 provided the earlier
E004wp 960x540 PRIVATE rear grayscale display preview to an SP11-only
numeric analysis; it was unmounted immediately after. Its native
Windows oracle script sampled source 4K luma at 4x pixel stride,
**not** PIL bilinear resize. E004mt native Linux private 4K RGB was
compared using the SAME 4x source pixel stride and local grayscale
conversion. Windows preview local meanY_display155.895/highpass
Gaussian8 std3.607; Linux toned private RGB local meanY_display144.932/
highpass std4.052. Linux 4x-decimated highpass cannot be directly
compared to an earlier separately bilinear downsampled Linux image
with highpass std~1.154: interpolation discards substantial fine
variation. Windows vs Linux cross-OS highpass correlation~-0.001;
lighting, exposure, time, framing and processing were not registered.
These sharpness/gradient proxies include noise and aliasing; do NOT
claim Windows-recognizable scene, OEM parity or that Linux lacks fine
detail solely from mismatched resampling. The independent Linux-vs-
Linux E004ms/E004mt highpass corr~0.05 used identical bilinear methods
on both and is reported separately. Private photos/pixels/hashes
never left SP11; root-private NTFS ro,norecover mount removed. No OS
reboot, IR, normal camera configuration or experimental boot touched.
Evidence E004mt/evidence/SP11-LOCAL-WINDOWS-LINUX-PRIVATE-CORNER-DETAIL-SCALARS.json.

## E004mt source-frame temporal RAW10 quality gate after E004ms

The NEW guarded E004mt one-shot passed actual front1080/rear4K
independent app/lifecycle and exact native RGB-control restoration and
three rear full10 native source consecutive frame-pair comparisons
before QBUF. Native sequence gaps zero and 31–34ms capture spacing.
At baseline rear green Bayer full10 sampled pixel std~0.78 codes and
frame-pair difference RMS~0.84 codes, 12x16 coarse tile correlation
0.973. At bounded trial exposure3200/analogue512/digital2048, sampled
per-frame spatial std9.07–9.20 codes, paired temporal difference
RMS5.52–5.53 codes, coarse tile correlation0.9957–0.9964. High
coarse correlation DOES NOT identify true optical scene or exclude
sensor FPN; substantial per-pixel variation means brighter preview
should not be marketed as recovered fine detail or calibrated SNR.

SP11-private photos across independent E004ms/E004mt Linux boots:
rear brighter-gain grayscale full corr0.9795, Gaussian smoothed0.9923,
**highpass corr0.0498**; same method front gain highpass corr0.8743.
This is a reproducible DIFFERENCE between smooth rear shading and
fine-scale repeatability in available corner images, not a calibrated
fixed scene/dark reference or proof rear cannot image meaningful
features under adequate lighting. The ordinary-user app rear mean
NV12 Y142.332–143.221 after gated preview tone, still near fresh
Windows E004wp auto-rendered rear mean149–150 from a separate time,
NOT same physical sensor exposure/colour/detail or windows ISP parity.

Unique E004mt consumed and fully retired after automatic protected
Golden return boot `9798e796-694a-4568-ab14-f0ede5266ac9` with
safety guard PASS, no camera modules/nodes/processes or pending boot;
normal maintained Golden camera and default-OFF tone unchanged.
Four original photos remain private ONLY on SP11
`~/Pictures/SP11-Camera-Private-E004mt/`, dir0700/file0600;
scalar-only logs archived. The next engineering gate is genuinely
measured native noise under known lit and dark optical references,
and motion-aware temporal denoising/exposure policy offline before
fresh physical testing. No assertion that Windows-like brightness
implies true optical detail.

## E004ms first real opt-in rear brightness near current Windows range

After E004mr failed pre-stream and was retired, a distinct new E004ms
source-pinned one-shot added durable root-private selector tracing and
successfully delivered actual front1080p/rear4K RAW-to-NV12 video to
ordinary UID1000 apps. Exact native RGB controls were restored,
source RAW10 paired/full10 and service/graph shutdown evidence passed,
IR OFF, no Linux OS system sleep. A **rear-only, opt-in** studio-range
Y preview LUT bypasses flat baseline and engages only when the bounded
rear exposure3200/analogue512/digital2048 produces sufficient sampled
luminance spread. The real rear ordinary app baseline meanY30.22–30.23,
p01=30, p99=31, tile std0.22; trial with live LUT meanY145.46–145.67,
p01=125, p99=167, tile std9.8–9.87. Root-private rear RGB PNG
aggregate meanY144.399/p99=165, no endpoint-clipped Y pixels; front
was NOT tone-adjusted. E004wp Windows current rear auto-exposed native
NV12 had meanY149.15–150.41/p99=169–171/tile std11.46–12.06.
Therefore Windows-like rear *rendered brightness* is physically possible
through Linux software; these different-time scenes and different
exposure controls do NOT prove color, recognizable detail, true SNR,
calibrated black, white balance, full Windows ISP parity, dynamic AE or
safe routine day-to-day camera integration. Y-only tone does not
recover genuinely absent source signal and can amplify sensor FPN.

E004ms fresh one-shot consumed and fully retired after automatic
protected Golden return boot
`5e400c52-4c3f-4c69-ab7e-19065f514527`; Golden normal output
remains unchanged and candidate tone default-OFF. Four original PNGs
remain user-private **only on SP11** at
`~/Pictures/SP11-Camera-Private-E004ms/` folder0700/photos0600;
no pixels, photos or image hashes exported. Future work: controlled
lit/dark optical RAW10 sensor-noise and color measurements, bounded
adaptive native exposure/gain within fixed-mode max3206 lines rear,
day/night/tone clipping/flicker safeguards, and a separate fresh guarded
end-to-end opt-in normal-service test before productionization. No
manual user-side reboot or photo inspection is required for the tests
and diagnosis accomplished here.

## Software RGB service integration in progress (2026-09-23)

Maintained source:
\`src/sp11-camera-stack/rgb/service/session.py\` defines a
single-owner front/rear session state machine. It requires an
injected real backend to prove a fresh authorized camera boot and
exclusive lease, complete neutral/selected native graph before/after
each camera, actual publisher STREAMOFF and process exit, no remaining
source/client FDs and IR-off readback. Unsafe/uncertain operations
poison it: no speculative rollback or further link writes. Fifteen
camera-free simulated-device lifecycle/failure tests pass. **This is
source-only, not a functional installed camera service.** The real
kernel-backed adapter and guarded physical multi-app acceptance
remain necessary.

Both maintained RAW→NV12 direct publishers now support an explicit
\`SP11_CAMERA_ALLOW_CONTINUOUS=1\` compile-time opt-in coupled to the
separate one-shot boot token. Normal/default builds DENY the
\`continuous\` argument. The experimental mode has a four-hour hard
deadline and returns STOPPED=143 only after intentional termination
and verified STREAMOFF. Nine fake-device scenarios per camera pass,
including intentional signal-stop after four published buffers;
**continuous capture has NOT yet been live-tested on SP11**.
Do not claim a persistent daily camera service until the new mode
and controller/backend are separately accepted on real front1080p
and rear4K hardware, through ordinary application readers.

## Stage 1 real-software-publisher service integration in progress

E004ly separately demonstrated physical 1080p-front and 4K-rear
software RAW→NV12 capture/publication for about 115s each, with
same-invocation uid1000 app first/reopen/SIGKILL/recovery, verified
STREAMOFF and full native media graph neutral between/after.
The one-shot was CONSUMED and RETIRED and Golden returned safely.
Actual sampled frames were nearly black; no calibrated image quality.

The next maintained backend implementation lives in
src/sp11-camera-stack/rgb/service/{session.py,media_backend.py,
rgb_device_backend.py,candidate_owner.py,candidate_driver.py}.
35 camera-free injected-failure tests pass. This joins the exclusive
RGBSession with the exact Media Controller route policy, pinned
root-only candidate owner, live source-format configuration and
verified publisher stop contract. Fresh distinct E004lz physically
validated this maintained controller against both actual cameras at
front1080p/rear4K, uid1000 first/reopen/kill/recovery app sessions,
stop143/STREAMOFF and full graph neutrality. E004lz was consumed,
retired and Golden returned. This proves bounded real hardware
integration, NOT a default or genuinely opt-in enduring normal-use
service; controlled-lit image quality and general-client/long-run
reliability still require acceptance. Do not count an opt-in one-shot
as a daily service.

Next acceptance candidate E004ma exercises root-private
selector.py/rgbctl.py opt-in front/rear/off/quit commands as a
separate process from the three normal uid1000 app opens and one
killed/recovered app per camera. It retains both discoverable named
front1080p/rear4K endpoints, but only one real source is active.
A source-only selector is not a production normal-user camera
interface until actual guarded optical test and duration/IQ/user
permissions are independently accepted. Direct root-only
selection is a temporary administrative interface, not automatic
app-driven routing or Windows camera UX equivalence.

## Decision gate — when software RGB acceptance passes

Report the measured real front1080p/rear4K output, visual quality,
CPU/latency/FPS, reopen behaviour and remaining limitations to the
user. Ask whether to (a) retain software-only processing, (b)
prioritize Qualcomm native hardware ISP for Windows-like image
quality, or (c) validate and offer both as mutually exclusive,
user-selectable processing backends. This decision is NOT YET MADE;
do not automatically pursue a hardware-ISP build as a prerequisite
for shipping the first usable software RGB release.

## Stage 2 — optional Qualcomm hardware ISP, after user decision

If selected, validate the existing front native 2560x1440 QC10C
compressed TP10-UBWC ISP output with an exact supported memory
layout, import/decompression or separately proven native linear
output; check colourimetry and buffer synchronization. NEVER treat
QC10C compressed output as Bayer RAW10 or NV12. Integrate existing
derived native IMX681 IQ/AWB/3A work with actual live output pixels,
develop and verify the corresponding rear hardware ISP output/tuning
path, and compare measured front1080p/rear4K results against Windows
on the SAME SP11 under matched lit scenes, including exposure,
colour, white balance, detail, noise, motion, dynamic range, FPS
and latency. Earlier dark, unmatched Windows/Linux samples cannot
establish parity. Only offer optional user backend selection if BOTH
are independently production-safe with strictly exclusive routing.

Hardware-ISP path means a NATIVE LINUX implementation controlling
the same Qualcomm hardware that Windows uses, not running Windows
drivers inside Linux. RGB software usability, optional Windows ISP
visual parity and protected IR/Hello remain three DISTINCT outcomes.

Evidence:
- experiments/E004-front-ir-vd55g0/e004lx-guarded-startup-steady-rgb-reopen-one-shot/RESULT.json
- experiments/E004-front-ir-vd55g0/e004kr-direct-dual-stop-session-one-shot/
- experiments/E004-front-ir-vd55g0/e004kp-direct-rear-mmap-one-shot/
- src/front-imx681/desktop-output-contract.json
- src/front-imx681/userspace/iq/README.md
- src/sp11-camera-stack/rgb-desktop-output-contract.json
- src/sp11-camera-stack/READINESS.md

### 2026-09-23 E004mf visible-light measurement (consumed)

Normal front1080 and rear4K UID1000 application sessions, RAW10 full-bit per-channel scalar and same-frame RAW8/NV12 profile passed. Morning baseline/gain Y p99 front27/59, rear17/25; rear baseline RAW10 green p99 ~70 is clustered near ~16–18 upper8, front green p99 ~119. E004mf Golden returned and assets retired. No image pixels retained, so recognizable scene, calibrated black, colour or Windows IQ parity remain unproven; next attempts must use a new unique guarded identity and never activate IR or Linux OS sleep.

### 2026-09-23 E004kt Windows morning reference (consumed)

Fresh Windows WinRT NV12 CPU luminance scalar eight samples/camera gave mean Y front123.17–123.58 and rear151.48–151.90 with Auto=true nominal5000 ticks; no pixel exports/IR or control writes. Linux E004mf earlier morning baseline app p99 front27/rear17 (gain59/25) is NOT the same luminance statistic, time or controlled scene, so only a qualitative brightness discrepancy. The prior Windows E004ks reference was much darker under different lighting; do not infer a calibrated cause. Investigate source black level, Linux exposure controls and bounded tone mapping next. Windows returned Golden, inert future scheduled task retired, no default changes.
