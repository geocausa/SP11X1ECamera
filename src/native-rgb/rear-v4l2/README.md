## 2026-10-09 rear56 live libcamera exposure/gain and response timing proven

Real standard libcamera ExposureTime/AnalogueGain controls now reach the
OV13858 while streaming.12 separate changes have exact sensor-register
readbacks (exposure1600/3206lines, gain128/1024) inside libcamera set-control
clock boundaries. Three400-request sessions/1200 actual Requests completed;
four application buffers reused.288 completed full-frame global Y samples.
Exposure changes and gain changes caused reversible brightness response.
Observed first three-frame-consistent Y response2-3 sequence counts after
scheduled triggers64/128/192/256 (3-4 after last completion at apply).
This scoped observation is not a universal sensor-latch delay, atomic pair,
SOF timestamp, per-request exposure metadata association or visual parity.

All four stops, exact owner/DMA/arena/cache release, neutral graph, all
three sensors suspended and five camera clocks idle passed every session.
No reported runtime kernel hazards/watchdog. Final dmesg retains2/3;
session1 ring history rotated. All original strict per-session checks
passed before rotation; retained scalar proofs remain. Do not require
earlier ring history or weaken current-session marker admission.
Automatic Goldenf8af5d50-9fab-4e7d-8489-4884c01a8e37, hashes unchanged.
56 consumed/retired/unarmed; units disabled. NEVER retry consumed56.
Source6184bc73a9217c883fe6c61be93228d6138a0d69, build69/lib12.
9 private native NV12 frames/27 previews remain sealed SAME SP11 only.
Diagnostic userspace reads2500761600bytes (snapshot plus96Y means/session);
kernel pixel reads/copies0. This is not new performance qualification.
Current56 scene is darker than55; fresh matched Windows/lighting stability
is not established. No day/night or output/color/detail parity conclusion.

Native105 streams/88 IDs/176 boots; Windows8 streams/8 IDs/16 boots;
combined96 IDs/192 boots. Evidence
docs/NATIVE-RGB-REAR-GENERATION-56-20261009.json.
NEXT owner-bound rear hardware ISP statistics delivery to native libcamera
IPA, bounded automatic exposure/gain with measured settling admission, then
tone/color/detail against fresh Windows references. Adaptive IPA/AE remain
unimplemented; expose no fabricated ExposureTime metadata. Front calibration
and cadence optimization remain deferred. No OS sleep.
Earlier entries are historical.

## 2026-10-09 rear56 live exposure/gain control timing source qualified

Automatic exposure priority continues after Windows01/Linux55 comparison.
Rear libcamera now translates bounded standard ExposureTime/AnalogueGain
controls into existing sensor V4L2 controls. Unknown, non-scalar, non-finite
or out-of-range controls fail before I2C. Validate buffer binding first.
Gain uses upstream OV13858 code128 per1x; current qualified window1-8x.
Exposure uses actual mode1 VT clock432732960Hz/pixels-per-line4488,
4-3206lines; configure verifies pixel rate/HBLANK424/VBLANK928.
No group-hold, atomic exposure/gain pair, automatic AE or per-frame
control metadata/SensorTimestamp is claimed.

Fresh56/build69/lib12 retains all55 ISP/queue/lifetime protections.
Read-only live sensor helper checks only changed exposure/gain register
under existing sensor lock, with no public ctrl lookup/reentrant lock.
Original register writes unchanged; streaming flag only scopes diagnostics.
Probe schedules separate exposure up/down then gain up/down after64/128/
192/256 completions.96 completed full-Y means around edges and3 native
snapshots per session are SAME SP11 only; global scalar facts may export.
Extra diagnostic reads796262400bytes/session are explicit, not performance.

39 actual selected checks PASS.3 ARM64 W1/Werror modules0diagnostics;
libcamera6 tests and strict manual pipeline compile PASS0warnings.
Actual shared C++ helper4130assertions/19negatives each GCC/Clang ASANUBSAN;
sensor helper34/14 each, parser87negatives; optical55/39 each.
Previous guarded overlapping builder refused before staging; serialized
build then passed. Source fixture/comment/foreign-identity corrections
remain in original logs.56 remains unconsumed, unarmed, not installed.
Evidence docs/NATIVE-RGB-REAR-GENERATION-56-PREP-20261009.json.
NEXT clean pushed checkpoint, guarded install/one-shot56, measure actual
live control latency and reversible image response, automatic Golden.
Image quality first; no automatic exposure or quality parity claim.
Earlier entries are historical.

## 2026-10-09 actual Windows01 / Linux55 private native comparison complete

One-shot GRUB Windows quality01 completed eight distinct OEM rear 4K NV12
samples; three native originals remain private on the SAME SP11. Exposure
and ISO auto flags true; their nominal numbers are not sensor readbacks.
White-balance auto is null/unproven. Windows task unregistered, identity
consumed/retired, clean release and Golden return verified. Never retry01.

Fresh Linux55/build68/lib11 completed 3x400 real libcamera Requests with
four reused application buffers, default/high/default actual sensor
readbacks 1600/128 -> 3206/1024 -> 1600/128, digital BGR1024, pattern0.
All four stops, owner/DMA/arena/cache release and sensor/graph/clock cleanup
passed; no kernel hazard/watchdog. Golden3a0fcc8a-5d9f-49e2-81ce-644e19f382de
verified unchanged, next_entry empty, units disabled;55 consumed/retired.

Native Windows saved bytes reproduce original scalar metrics. SAME-SP11
read-only NTFS comparison completed, partition unmounted. Windows native
Y means84.106-85.216 versus Linux default8.029-8.038 / restored7.032-7.045,
high61.036-61.286. High-setting coarse scene correlation0.9499-0.9507,
original orientation, approximate8-native-pixel shift. Windows within-run
coarse correlation0.9998. Linux writes were386-416seconds after reference;
file times are not capture times. This supports broadly similar content,
not identical lighting/content or quality parity. Chroma differs;
matrix/range/transfer and actual Windows controls are not matched.
No reliable ambient day/night, true SNR, focus/color/visual parity proof.
Private unscaled native-Y comparison is available locally on SP11 only.

Counts: native102 streams/87 consumed IDs/174 boots; Windows8/8/16;
combined95 IDs/190 boots. Source17bd8267ddb830b47fed690faa7056b7d5546d8d.
Evidence docs/WINDOWS-REAR-QUALITY-20261009-01.json,
docs/NATIVE-RGB-REAR-GENERATION-55-20261009.json and
docs/WINDOWS01-LINUX55-PRIVATE-COMPARISON-20261009.json.
NEXT bounded native libcamera IPA automatic exposure/gain with qualified
sensor-control timing, then tone/color/detail calibration against private
Windows references. Image quality remains first; performance deferred.
User authorizes future one-shot Windows comparisons whenever useful.
Earlier entries are historical.

## 2026-10-09 on-demand Windows quality oracle; fresh Linux55 comparison ready

User explicitly authorizes repeated one-shot GRUB Windows reference captures
when useful, including changing daytime/nighttime illumination, then Linux
comparison. Permanent Golden remains unchanged. SP11/SP7/PiMaster only.
Windows quality01 source: rear OEM4K nativeNV12, eight unique timestamps,
three private native frames after stop/release; nominal automatic exposure/
ISO/WB read only. Atomic CreateNew entry guard and300s Windows return reboot
before camera APIs; fresh interactive Geoca task must be retired.
SP7 synthetic metrics35assertions/13negatives +actual WinRT NV12 lock/copy
PASS with no camera activated. Code and global scalar facts only may travel.
Fresh Linux55/build68/lib11 retains54 default/high/default controls and all
ISP/queue/lifetime/Golden safeguards;38 selected checks/3 ARM64 W1/Werror/
6 libcamera tests PASS,0diagnostics. Exact55 optical model54assertions/
38negatives each; compile-bound probe/analyzer identity preflight passed.
Neither new identity has run/consumed at this source checkpoint.
NEXT one-shot Windows quality01, automatic Golden, fresh Linux55, same-SP11
private native comparison. Scene registration and temporal illumination
must be measured; brightness alone does not certify detail/color/SNR/parity.
Evidence docs/WINDOWS-REAR-QUALITY-20261009-01-PREP.json and
docs/NATIVE-RGB-REAR-GENERATION-55-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear54 natural-scene exposure/gain response proven

User confirmed lit scene and uncovered rear lens for this comparison.
1200 actual libcamera Requests in three400 same-boot sessions completed.
Existing sensor controls and actual readbacks match default/high/default:
exposure1600/3206/1600lines, analogue128/1024/128, digitalBGR1024,
test_pattern0 all. Unchanged sensor/mode/VTS/ISP/queue/lifetime policy from53.
Scene Y means10.440-10.824 default1,78.753-89.744 high2,
11.935-13.967 restored-default3; p99s30 /190-205 /29-36.
High scene median65-85 versus defaults7-15; black fraction8.29-14.61%
versus54.22-71.65% default. No degenerate/identical flags in nine frames.
Substantial reversible brightness response to manual exposure/gain proven.
Supports underexposure/missing automatic controls as a next engineering focus;
does not establish full root cause, identical scene/lighting stability, or
visual/color/focus/denoise/Windows parity.54 defaults brighter than53, so do not
claim cross-boot brightness difference was caused by a source-policy change.
All four stops/owner/DMA/arena/cache release, sensors suspended,
graph neutral and five camera clocks idle each; no kernel hazards/watchdog.
Automatic Golden9bd8e4bb-aeb0-49f7-8b94-206749402374, hashes unchanged.
54 consumed/retired/unarmed, units disabled; never retry.
9 native NV12 frames111974400bytes/27 unverified previews remain sealed SP11.
Scalar facts only exported; kernel pixel reads/copies0; diagnostic timing
does not promote new performance qualification.38checks/build67/lib10.
Native99streams/86IDs/172boots,12pre-stream/24after-start failures;
combined93IDs/186boots. Manual photometric response PASS, optical-quality and
automatic-control gates still PENDING. Performance remains deferred.
NEXT private visual/color/focus screening and matched Windows photometry;
native libcamera IPA automatic exposure/gain with qualified control timing.
Evidence docs/NATIVE-RGB-REAR-GENERATION-54-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear54 controlled exposure/gain source PASS; hardware pending

User confirms current rear lens uncovered and scene lit.
Fresh54/build67/lib10 compares scene default/high/default:
exposure1600/3206/1600 lines, analogue register128/1024/128,
test_pattern0 each, digitalBGR1024. Uses existing V4L2 controls only;
strict cached binary UAPI and actual register match required per session.
No sensor/mode/VTS/ISP/queue/lifetime source-policy change from completed53.
Photometric models24 assertions/40negatives; actual installed UAPI compiled.
Exact54 optical probe/analyzer preflight passed; current54 optical model
53 assertions/37negatives each GCC/Clang ASAN/UBSAN; stale53 path rejected.
38 selected checks/3 ARM64 W1/Werror modules/6 libcamera tests allPASS,
zero diagnostics. Historical observer baseline corrected; superseded optical
and sensor report scope/failed qualification logs retained before hardware.
54 unconsumed/uninstalled/unarmed at this source checkpoint.
53 retired: bright sensor pattern, nearly black scene; image-quality BLOCKED.
NEXT guarded fresh54 same3x400 capture, native private optics and original
all-owner/four-stop/Golden safeguards. No visual/Windows parity claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-54-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear53 scene/pattern/scene completed; scene quality blocked

1200 actual libcamera Requests in three400 same-boot sessions completed.
Lock-safe retained sensor control pointers/readback fix proven on hardware.
Actual controls agree: exposure1600 lines, analog128, digitalB/G/R1024,
test_pattern0/1/0; original ISP/queue/lifetime unchanged.
Scene Y means2.816-2.899, every scene p99=9: still nearly black.
Internal sensor color bars span Y0-255, mean126.531/std84.882.
Static identical bar frames expected; not stale-buffer or corruption proof.
Bright pattern narrows next investigation toward optical signal and sensor
photometric configuration; does not clear all natural-data ISP processing.
53 scene lighting not independently confirmed;49 user lit/uncovered confirmation
remains historical. No visual/color/Windows optical parity or root-cause claim.
All four stops/owner/DMA/arena/cache release each, sensors suspended,
graph neutral and five camera clocks idle; no kernel hazards/watchdog.
Automatic Golden2e99dffe-0fd7-4df0-9820-a51d05401379, protected hashes unchanged.
53 consumed/retired/unarmed, units disabled; never retry53 or52.
9 native NV12 frames111974400bytes/27 unverified previews sealed SAME SP11.
Only global scalar metrics exported; kernel pixel reads/copies0.
37 source checks/build66/lib09; diagnostic capture not performance promotion.
Native96streams/85IDs/170boots,12pre-stream/24after-start failures;
combined92IDs/184boots. Image quality remains BLOCKED; performance deferred.
NEXT fresh bounded natural-scene exposure/gain response with actual register
verification, then matched Windows photometry/optical comparison.
Evidence docs/NATIVE-RGB-REAR-GENERATION-53-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear53 locked sensor readback source PASS; hardware pending

Fresh53/build66/lib09 fixes52 diagnostic mutex recursion. Exposure/analog/
digital/testpattern pointers retained at original control creation; helper
asserts existing sensor mutex held, performs no lookup or lock acquisition.
Actual old52 helper triggers modeled recursive acquisition under held lock;
fixed helper passes45 assertions/18negatives each GCC/Clang ASAN/UBSAN.
41 control/parser negatives;141 CAMSS sources equal52 except identity.
Exact53 probe/analyzer preflight passed;52 optical assertions/36negatives each
GCC/Clang verify current53 header including stale52 root rejection.
37 selected sourcechecks/3 ARM64 W1/Werror modules/6 libcamera tests allPASS,
zero diagnostics. Prior optical01 report using52 model preserved/superseded by02.
ISP/queue/lifetime/owner proof unchanged; same3x400 scene/pattern/scene plan.
53 source qualified only, not installed/armed/consumed at this checkpoint.
52 retired after delayed automatic Golden recovery, no clean-stop/optics claim.
49 near-black native image remains BLOCKED; performance deferred; no parity.
NEXT guarded fresh53 actual capture; never retry52.
Evidence docs/NATIVE-RGB-REAR-GENERATION-53-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear52 sensor diagnostic mutex deadlock; Golden recovered

Actual52 entered owner/session1 and sensor mode4064x2286/VTS3214, then hung
before sensor controls readback or capture completion. Source shows new helper
v4l2_ctrl_find calls find_ref_lock->mutex_lock on control handler's lock, which
is the already-held ov13858 mutex in s_stream. Diagnostic introduced recursive
locking. No actual hung-task stack; deterministic source path and last log
support this diagnosis. Service75s timeout killed main; capture survivedSIGKILL.
Original RESULT remains STARTED/session1; service timeout and journal preserved.
No completed Requests/images qualified; no clean candidate DMA/stop claim.
Golden af7a7ecc-dfd2-43df-91aa-9c82bcb7e3a5 recovered without user intervention,
after delayed shutdown. Protected hashes unchanged; no kernel hazards.
Watchdog did not fire: shutdown stopped timer before90s. Do not claim bounded
90s recovery.52 consumed/retired/unarmed, units disabled, never retry.
Native93streams/84IDs/168boots,12pre-stream/24after-start failures.
Combined91IDs/182boots.49 near-black image-quality defect remains BLOCKED.
NEXT fresh53 retained control pointers with already-held-lock tests; exact53
probe/analyzer rebuilt lib09, then scene/pattern/scene. Performance deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-52-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear52 exact optical identity source PASS; hardware pending

Fresh52/build65/lib08 probe and analyzer are both bound to exact private root52;
actual no-hardware identity checks passed.35 optical negatives include11 wrong
directory/identity cases, retaining all original DMA READ/layout/save safeguards.
37 checks/3 ARM64 W1/Werror modules/6 libcamera tests passed with0 diagnostics.
Binary cached test_pattern readback, actual sensor exposure/gain/pattern
readbacks and three400 scene/pattern/scene preserved.141 CAMSS sources match51
except identity, retaining unchanged ISP/queue/lifetime. Guard's source-only
builder inventory includes only the new exact build-optical-v2 command.
52 not yet installed/armed/consumed at this source checkpoint.
49 near-black native picture remains BLOCKED. No optics/parity/full-stack claim.
50 and51 consumed/retired; never retry. NEXT guarded52 actual diagnostic.
Evidence docs/NATIVE-RGB-REAR-GENERATION-52-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear51 pre-stream probe identity failure; retired safe

Numeric cached test_pattern0 readback passed. CameraManager discovered camera,
but optical probe rejected directory51: binary lib07 is compile-bound to49.
Reusing lib07 for51 was an integration error. No sensor start/mode/kernel
attempt/result marker, no Requests, no optical files. Raw probe stderr preserved.
Runtime's missing-session-marker error masked the earlier probe admission error.
NEXT fresh52 rebuilt lib08/probe with exact52 directory and explicit no-hardware
identity preflight before install/arm; add stale path negatives. Keep numeric
sensor controls +scene/pattern/scene, all private optics and lifecycle guards.
51 consumed/retired/unarmed, units disabled. Automatic Golden
b5d6e524-2631-4324-ad68-9b35a0532202; hashes unchanged/no hazards/watchdog.
Native93 streams/83IDs/166boots;12pre-stream failures,23after-start.
Combined90 IDs/180boots. Latest optical49 remains near-black BLOCKED; no parity.
Evidence docs/NATIVE-RGB-REAR-GENERATION-51-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear51 sensor/pattern diagnostic source PASS; hardware pending

Image-quality defect49 remains blocked: nearly black native NV12 in a user-
confirmed lit/uncovered scene. Fresh51/build64 reuses immutable libcamera07.
37 source checks and3 ARM64 W1/Werror modules passed, zero diagnostics.
Sensor reads exposure/analog/digitalBGR/test pattern after normal control setup
before STREAMING; mismatch/read error aborts. Existing control writes preserved.
Three400 sessions use sensor test_pattern0/1/0 (scene/colorbars/scene).
41 actual helper assertions and17 failure cases each GCC/Clang ASAN/UBSAN;
41 parser and binary-control negatives. Binary VIDIOC_G_CTRL readback
replaces CLI menu-text parsing; installed UAPI definitions compiled and checked.141 CAMSS sources match49 except identity. Private optical
capture/stop/release, exactonce consumption, independent watchdog and automatic
Golden return unchanged. No images or image hashes exported, no parity claim.
Source qualified only:51 not installed/armed/consumed at that source checkpoint.
NEXT guarded install and fresh51 scene/pattern/scene, then diagnose.
Evidence docs/NATIVE-RGB-REAR-GENERATION-51-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear50 pre-stream harness failure; Golden safe; no optical data

50 consumed once, stopped at cached test_pattern CLI-text readback before any
sensor start:0 sensor starts/0 kernel attempt/mode/result markers/0 Requests.
Error sensor cached test pattern readback; actual CLI text was not retained.
Menu-label formatting is suspected, not an observed root cause. Replace this
fragile text comparison with checked binary VIDIOC_G_CTRL readback in fresh51.
Raw failure preserved;50 retired/unarmed, units disabled. Automatic Golden
fc38c6fb-8188-4e9b-a04f-c19d5e0274f5; protected hashes unchanged, no hazards or
watchdog. Native93 streams/82 consumedIDs/164 boots;11 pre-stream failures/
23 after-start failures; combined89 IDs/178 boots.
49 remains latest completed optical capture:9 near-black native frames in
user-confirmed lit/uncovered scene. Image quality BLOCKED; no parity.
NEXT fresh51 scene/pattern/scene, actual sensor exposure/gain/pattern registers,
binary cached control admission, unchanged ISP/queue/lifetime/Golden safeguards.
Evidence docs/NATIVE-RGB-REAR-GENERATION-50-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear50 sensor/pattern diagnostic source PASS; hardware pending

Image-quality defect49 remains blocked: nearly black native NV12 in a user-
confirmed lit/uncovered scene. Fresh50/build63 reuses immutable libcamera07.
37 source checks and3 ARM64 W1/Werror modules passed, zero diagnostics.
Sensor reads exposure/analog/digitalBGR/test pattern after normal control setup
before STREAMING; mismatch/read error aborts. Existing control writes preserved.
Three400 sessions use sensor test_pattern0/1/0 (scene/colorbars/scene).
41 actual helper assertions and17 failure cases each GCC/Clang ASAN/UBSAN;
37 parser negatives.141 CAMSS sources match49 except identity. Private optical
capture/stop/release, exactonce consumption, independent watchdog and automatic
Golden return unchanged. No images or image hashes exported, no parity claim.
Source qualified only:50 not installed/armed/consumed at this checkpoint.
NEXT guarded install and fresh50 scene/pattern/scene, then diagnose.
Evidence docs/NATIVE-RGB-REAR-GENERATION-50-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear49 capture PASS; image quality BLOCKED near black

User priority: image quality before further cadence optimization.
Nine real native 3840x2160 NV12 snapshots from three400 libcamera sessions:
Y means2.735-2.813/255; every frame p99=9 and >99.998% Y<=16.
User confirmed lit scene and uncovered lens. Nearly black output fails the
usable image gate. Frames vary; no constant or identical-frame finding.
Exposure/ISP root cause unknown. Color space unspecified; three local decode
interpretations per frame are unverified, not color or Windows parity.
9 raw frames111974400 bytes and27 previews remain private SAME SP11 only.
Scalar analysis only exported. DMA_BUF READ START/END before Request reuse;
private disk writes after camera release. Unchanged kernel ISP/queue/lifetime.
1200 actual Requests; all four stops, owner/DMA/arenas/cache release and
sensors/clocks/graph idle. No kernel hazards/watchdog. Automatic Golden
7affb8ed-babf-496b-a041-f8e55482f96a; protected hashes unchanged.
49 consumed/retired/unarmed, units disabled.36 sourcechecks/build62/lib07.
Native93 streams/81 consumed IDs/162 boots; combined88 IDs/176 boots.
NEXT diagnose sensor actual exposure/gains and internal test pattern versus
scene with fresh identity50 and original capture/stop/Golden safeguards.
Further performance optimization/longsoak deferred until usable image baseline.
Evidence docs/NATIVE-RGB-REAR-GENERATION-49-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear49 private optical source qualified; hardware pending

User priority image quality first. Fresh49/build62/lib07 retains48 kernel ISP/
queue/lifetime policy; libcamera handler unchanged. New optical probe retains
original400 Request/metadata/reuse/stop flow and snapshots sequences15/79/199
each session. Exact same-FD Y/UV offsets/lengths/extent; DMA READ START/map/copy/
unmap/END before requeue. Save3 native NV12 files/session only AFTER camera
release;9 frames111974400 diagnostic bytes total, sealed root0700/0600 SP11.
Private local scalar analyzer and27 decoder-hypothesis previews; pixels/photos/
spatial arrays/image hashes never Git/chat/exported. Color-space metadata is
unspecified; BT601-limited/BT709-limited/full previews are unverified hypotheses.
No visual or Windows optical parity claim from scalar screening.
36 sourcechecks PASS;3 ARM64 W1/Werror modules;6 libcamera tests/compile0warnings.
Actual optical helper GCC/Clang ASAN/UBSAN37assertions+24negatives each;
9 decoder vectors,12 optical probe parser negatives, real sealed synthetic
file/preview/error models PASS. Original Request flow comparison exact.
49 unconsumed/uninstalled/unarmed. Latest actual hardware48, counts unchanged:
native90 streams/80IDs160boots;combined87IDs174boots.
NEXT fresh49 bounded native optical capture/scalar image screening, automatic
Golden return, retirement, then fix dominant picture defect/compare Windows.
Front deferred, no OS sleep; image quality remains unknown.
Evidence docs/NATIVE-RGB-REAR-GENERATION-49-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 user priority: rear image quality before more optimization

The user directs actual image quality to be the immediate next gate.
Latest48 transport remains qualified and consumed/retired; its1200-request
probe never read pixels, so picture quality is still unknown. Freeze further
cadence optimization/longer soak while establishing a usable rear picture.
NEXT fresh one-use short capture from the CURRENT native hardware-ISP/
libcamera NV12 path, private frames/previews SAME SP11 ONLY, image integrity/
geometry/exposure/color/focus screening, then matched Windows comparison.
Fix the dominant picture defect first; adaptive3A/focus/tuning remain open.
Original all10 owner/retirement/four-stop proofs and Golden fallback remain.
No consumed identity retry, no OS sleep, no optical bytes exported.
No new hardware capture performed by this priority update; counts unchanged.
Plan docs/REAR-IMAGE-QUALITY-GATE-20261009.md.
Earlier immediate-next instructions are superseded by this user direction.

## 2026-10-09 rear48 startup preallocation hardware PASS; no long gaps

1200 actual4K linearNV12 Requests, three400 sessions, four reused appbuffers.
Callback29.9543/29.9619/29.9609fps;0 >50ms gaps across all1197 intervals.
Full400 maxgaps33.556/35.885/35.901ms; no first-handoff stall observed.
First rolling FULL+8AUX allocation moved before pipeline power:1.715456/
5.104026/2.282674ms; same-owner exact nextgen transfer once each, FIFO intact.
Original all10 consumed snapshot/ledger/owner and all4 stops unchanged.
400 handoffs/updates each;1203VB2 completions include3 STOP extras.
397 cachehits/2 rolling misses each +1 prestartup mapping each;1191hits/
6rolling misses+3 prestartup maps;9 total new mappings.400 logical retirements
each;3 cached mappings physically flushed after all4 stops each. Rolling FULL
get399/AUXalloc3192 vs FULLretire400/AUXfree3200: preallocation accounted.
1209epochs/3591events,retries0; clean owner/DMA/arenas/graph/all3sensors/5clocks
each; no hazards/watchdog. Automatic Golden89ea6ddb-103d-46d5-a756-c003f06e94d5,
protected hashes unchanged.48 consumed/retired/unarmed; units disabled.
35 sourcechecks/build61/lib06; changes+scalar evidence committed.
Native90streams/80IDs160boots,combined87IDs174boots; failedafterstart23.
This is one candidate boot with3 starts, not universal startup/longsoak parity.
First callback latency246.561/424.371/375.751ms; no overall latency improvement
claim. Timing association supports preallocation; causality remains inference.
NEXT independent-boot repeat, longer capture/stop-reopen soak, then semantic
IPA3A/controls/SensorTimestamp/SOF and Windows optical parity. Front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-48-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear48 startup allocation source qualified; hardware pending

Fresh48/build61, unchanged lib06/probe400. First rolling FULL+8AUX set is
allocated before pipeline power/MMIO/sensor start. Its pending VB2 wrapper
stays on the FIFO; whole allocations are checked against BOTH startup sets
and command arenas. Exact owner+next generation required for a one-time move.
Original rolling bind/alias/all10 consumed proof and all4 stops remain.
Uncertain hardware failure retains the spare descriptor with the faulted pair.
Rolling allocation/cache accounting explicitly subtracts the one preallocation;
logical retirement still occurs every handoff. No timestamp shifting.
35 source checks PASS; three ARM64 W1/Werror modules, zero diagnostics.
Actual new helper GCC/Clang ASAN/UBSAN:84 assertions each,10 allocation/API
failure stages,12 stale-take cases;67 parser negatives. Original source tokens
match47 after removing only declared startup-spare hooks.
48 unconsumed/uninstalled/unarmed; latest hardware47 three400/1200 PASS.
Counts remain native87 streams/79IDs158 boots; combined86IDs172 boots.
NEXT fresh48 same three400 Requests, first-handoff timing comparison, Golden
return/retirement. Causality/startup reliability/longsoak/IPA3A/SOF/optical
parity unqualified; front deferred. No OS sleep; all pixels stay on SP11.
Evidence docs/NATIVE-RGB-REAR-GENERATION-48-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear47 three400-request qualification PASS; no late long gaps

1200 real4K linearNV12 Requests, three400 sessions, four reused appbuffers.
Callback29.9547/29.8835/29.9569fps over399 intervals each; final1200 aggregate
validated before PASS. No >50ms gaps after first80 in any session (960 late
intervals total). Full400 long-gap counts0/1/0; sole63.687ms gap at session2
sequence1, prepare5.143142ms+collect56.516185ms. Startup issue intermittent;
46 saw first-handoff gap all3,45 only1. Allocation deadline causality unproven.
397 mapping hits/3misses each;1191hits/9misses total,0 rolling FULL physicalunmaps,
3cachedmaps physically flushed after all4 stops each/9total. Original all10
owner/consumed-address ledger/snapshot proof unchanged; 1200 handoffs/commits.
1203 VB2 completions (3extra STOP races),1210epochs/3474events,retries0.
All stops/owner/DMA/arena/neutralgraph/sensors/idleclocks PASS each; no hazards/
watchdog. Golden bfa198ec-9b36-486a-b026-1589f251f057 automatic return; hashes unchanged.
47 consumed/retired/unarmed, units disabled.34 sourcechecks/build60/lib06.
46 immutable raw final240 harnessFAIL retained; 47corrected fulltrial PASS.
Native87streams/79IDs158boots,combined86IDs172boots/failedafterstart23.
Extended bounded duration~13.3s each qualified; longsoak/strictgapfree30fps/
IPA3A/SOF/controls/optical parity still unqualified; front deferred.
NEXT target first rolling handoff preparation/collection phase, then longer
soak/lifecycle and automatic controls/SOF/Windows optical parity.
Evidence docs/NATIVE-RGB-REAR-GENERATION-47-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear47 final1200 aggregate source qualified; hardware pending

Fresh47/build60/unchanged lib06 retains46 camera/queue/cache/probe policy.
Corrects final aggregate: three independently completed400 Request sessions
and actual1200 sum required before PASS. Per-session epoch lower bound400.
34 source checksPASS; three ARM64 W1/Werror modules0diagnostics. Real immutable
46 scalar result accepted by corrected aggregate, rejected by actual old240
check;57 partial/mixed/miscounted/wrong-owner negatives PASS.46 rawFAIL preserved.
Probe/queue/cache/gap source unchanged; source model checks repeat passed.
47 unconsumed/uninstalled/unarmed.46 physically completed1200 with all cleanup
but final harnessFAIL; latest full qualification45. Counts native84streams/
78IDs156boots,combined85IDs170boots/failedafterstart23. Golden dda8274c safe.
NEXT fresh47 three400 capture/1200 aggregate qualification, Golden return and
retire47. No consumed identity retry. Startup gap/longsoak/IPA3A/SOF/optics
still incomplete; front calibration deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-47-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear46 three400 captures physically clean; final aggregate harness failed

All1200 real4K NV12 Requests completed; three400 sessions callback29.8859/
29.8841/29.8859fps.397 cache hits/3misses each; all4 stops/cacheflush/owner/DMA/
arena/graph/sensors/clocks cleanup PASS. Each has one62.5ms gap at sequence1;
no >50ms gaps after first80. Prefix kernel/application timestamps exact.
Raw final status FAIL: final aggregate mistakenly still required240 despite
recorded1200. This is a harness failure, not promoted to full qualification PASS.
All three physical completed streams counted; failed-after-start counter23.
1203 VB2,1212epochs/3380events,retries0; no hazards/watchdog.46 consumed/retired.
Golden dda8274c-5a6f-4292-aa34-a8fd24735a3f; protected hashes unchanged; units disabled.
Native84streams/78IDs156boots,combined85IDs170boots. Latest full qualification45.
NEXT fresh47 final1200 total validation+real retained46 scalar negative tests,
rerun three400 under fresh identity then automatic Golden return/retire.
Never retry46; immutable raw failure preserved. Product/long-soak/IPA/SOF/
optical parity incomplete. Front calibration deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-46-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear46 three400-request duration extension source qualified; hardware pending

Fresh46/build59/lib06 targets3x400=1200 real4K NV12 Requests/four reusedbuffers.
Actual kernel queue/cache/gap observer byte-identical to45; userspace pipeline
unchanged. Probe retains original request/metadata/release flow, target400/
timeout20s and scalar timing only. First80 kernel/application prefix must match;
all400 gap count/max ordinal and >50ms late gap count now explicit.
33 checksPASS,3 ARM64 W1/Werror modules0diagnostics,6 libcamera Werror testsPASS.
Actual probe stats GCC/Clang ASAN/UBSAN1218 assertions each/1200 synthetic
completions with no-gap/first-prefix/late-gap fixtures; strict type/count parser.
46 unconsumed/uninstalled/unarmed. Latest hardware45 localized one64ms gap at
first handoff, prepare5.04ms+collect57.05ms; causal fix not established.
Counts native81streams/77IDs154boots,combined84IDs168boots unchanged.
Golden cf960bf7 safe. NEXT one46 three400 captures, automatic Golden return
and retire46. Extended bounded duration, not long-soak qualification.
IPA3A/SOF/controls/optical parity remain incomplete; front calibration deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-46-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear45 gap localized to first rolling handoff; three captures PASS

240 real4K NV12 Requests; callback29.6112/29.9916/29.9672fps. Kernel first80
completion timestamps exactly match application span/min/max each session.
>50ms gap counts1/0/0. Sole64.002ms gap at session1 sequence1 (first handoff):
prepare5.040897ms,collect57.047934ms,retire1.748422ms. Sessions2/3 maxima35.994/
33.554ms. Localizes this run's gap to startup transition; allocation deadline
causality not proven. Queue/cache/lifetime policy unchanged from44.
All3 four-stop/cacheflush/DMA/owner/arena/graph/sensor/clock cleanup PASS;
243 VB2 completions,250 epochs/892events; retries0; no hazards/watchdog.
Golden cf960bf7-4050-4dae-8db6-e509ebc87d33 automatic return; protected hashes unchanged.
45 consumed/retired, units disabled.32 source checks/build58/lib05.
Native81 streams/77IDs154boots,combined84IDs168boots.
NEXT longer three400-request captures to determine whether late gaps recur;
then targeted startup optimization and IPA3A/SOF/controls/optics. Front deferred.
Strict gap-free30fps, long soak and product parity remain unqualified.
Evidence docs/NATIVE-RGB-REAR-GENERATION-45-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear45 scalar gap timing source qualified; hardware pending

Fresh45/build58 adds scalar first80 completion gap counts/positions and rolling
stage maxima plus stage timings associated with the largest gap. Existing lib05
and capture unchanged. V4L2 microsecond completion timestamps must match the
application prefix exactly; extra STREAMOFF completions excluded. No per-frame
logs, pixel reads, MMIO/IRQ changes or timing-based lifetime authority.
All44 queue tokens identical after exact observer-tag removal; mapping cache,
strict all10 owner/consumed-address proofs and four-stop flush unchanged.
32 checksPASS; three ARM64 W1/Werror modules zero diagnostics. Actual timing
helpers/log GCC+Clang ASAN/UBSAN264 assertions each/240-buffer prefix models,
strict parser negatives and existing28019/211 queue models retained.
45 unconsumed/uninstalled/unarmed; latest hardware44 near30fps all3 sessions.
Counts native78streams/76IDs152boots,combined83IDs166boots unchanged.
Golden c88f40bf safe. NEXT one45 three80-request captures and automatic Golden
return; retire45. Residual gap cause/long soak/IPA3A/SOF/optics unqualified.
Front deferred. Evidence docs/NATIVE-RGB-REAR-GENERATION-45-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear44 mapping cache hardware PASS; all3 sessions near30fps

Three independent80-request sessions delivered240 real4K linearNV12 Requests,
four reused buffers,243 VB2 completions. Callback29.6292/29.643/29.9696fps;
43 baseline15.164/29.947/15.2704. Sustained half-rate absent in44 short trial.
Each owner1/2/3:77 cache hits/3 fresh mapping misses,80 exact proven retired
mapping transfers;3 cached mappings held to4 physical stops, then all3 freed.
231 hits/9 rolling map misses total,0 rolling physical FULL unmaps,9 final
cache flush frees. Current active mapping separately reclaimed at stop.
Prepare+retire3.283/3.432/3.025ms per handoff vs43's9.940/7.757/10.077ms.
Original all10 consumed-address/owner/ledger/snapshot and stop guards unchanged;
FULL retired logically before cache move, physically released after4 stops.
Max completion gaps62.236/62.100/33.550ms; queue epoch deltas81/81/80.
Near30fps from first session proven in this3x80 trial; strict gap-free30fps,
residual gap timing/location/cause and long-soak reliability NOT qualified.
All stops/DMA/owner/arena release, sensors suspended, neutral graph/idle clocks
PASS each; retries0/0/0;251epochs/760events; no hazards/watchdog.
Automatic Goldenc88f40bf-b0c2-4cb7-aa35-a7ded9f0488a/protected hashes unchanged.
44 consumed/retired, units disabled/static watchdog inactive; no armed jobs.
Exact runtime result44 identity fixed/tested;43 raw legacy label preserved.
31 source checksPASS/build57+unchanged libcamera05. Native78/76IDs152boots,
combined83IDs166boots. No optical reads; IPA3A/SOF/controls/optics incomplete.
NEXT remove residual long completion gaps and longer capture/lifecycle tests;
then semanticIPA3A/SensorTimestamp and matched Windows optics. Front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-44-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear44 owner-bound FULL mapping cache source qualified; hardware pending

Fresh44/build57 keeps proof-retired FULL DMA-BUF mappings per exclusive owner.
Cache move follows the ORIGINAL last all10 consumed-address/owner snapshot;
take requires same DMA-BUF, owner/generation and unchanged mapped span. Original
pair/aux/retirement checks remain; cache alias/dirty state rejects before exposure.
At most4 mappings cached; full cache falls back to original proven live unmap.
Cache physical flush validates all entries and all4 stops before releasing;
clean reopen requires cache idle. Uncertain generation/cache stays pinned.
31 checksPASS,3 ARM64 W1/Werror0 diagnostics; actual cache GCC/Clang ASAN/UBSAN
models3owners/240handoffs and missing-stop/foreign/alias/stale failures.
44 exact result identity constant tested;43 legacy label defect preserved.
56 extractor failure and57 fixture compile repair logs preserved; no hardware.
Libcamera05 unchanged.44 unconsumed/uninstalled/unarmed; latest hardware43.
Native75/75IDs150boots,combined82IDs164boots; Golden37184b04 safe.
NEXT one44 three80-request capture/cache/cadence comparison and automatic
Golden return; retire44. Uniform30fps/IPA3A/SOF/optics/longsoak still unproven.
Front deferred; product incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-44-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear43 proves mapping overhead; slow cadence also occurs in session3

Three80-request captures PASS;240 real4K linearNV12 Requests/four reused
buffers,243 VB2 completions, all4 stops/owner/DMA/arena cleanup and sensors/
graph/clocks idle each. Rates15.164/29.947/15.2704fps; slow sessions1 AND3.
FULL DMA-BUF mapping get+put6.69/4.90/6.56ms per handoff, accounting for
67.3/63.2/65.1% of prepare+retire. AUX alloc+free3.00/2.62/3.27ms; zero0.098ms.
No pixel reads, queue policy change or timing-based release authority.
Three owners1->2->3, snapshot retries0/0/0,404epochs/878events; no hazards/watchdog.
Automatic Golden37184b04-09d9-466c-bf49-beea1fb192a5; protected hashes unchanged.
43 consumed/retired; units disabled/inactive. Never retry43.
Raw runtime JSON inherited identity40 label; immutable result preserved.
Exact43 kernel session markers, one-use root/boot manifest and CONSUMED agree;
label was not used for admission. Fix descriptor and add assertion in next harness.
30 source checks PASS/build55, unchanged libcamera05; native75/75IDs150boots,
combined82IDs164boots. Uniform30fps/IPA3A/SOF/optics/longsoak unproven.
NEXT per-session retained FULL mapping cache with exact retired-generation/
owner proof before reuse and all4 physical stops before final cache flush.
Front calibration deferred; product incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-43-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear43 DMA operation timing source qualified; hardware pending

Fresh43/build55+unchanged libcamera05 adds aggregate timings for FULL mapping
get/put and eight auxiliary allocate/zero/free operations. Queue-only reset
excludes startup; final log precedes stop. No control/release predicate reads
the timing fields. Whole-source tokens equal42 after exact observer removal.
All10 consumed-address/owner/ledger/snapshot proofs, mappings and4stops unchanged.
30 source checks PASS;3 ARM64 W1/Werror modules0 diagnostics; actual queue
GCC/Clang ASAN/UBSAN28019 assertions/211 negatives each.
Fresh43 unconsumed/uninstalled/unarmed.54 source assembly filename error
preserved;55 fresh successful build; whitespace-only comparison fixture fixed.
Latest hardware42 remains240 real4K NV12 Requests/3clean sessions, rates
15.1686/29.9479/29.9452fps; first-session uniform30fps not qualified.
Golden607ade99 safe, protected payload unchanged; native72/74IDs148boots,
combined81IDs162boots. No optical reads. Front deferred; product incomplete.
NEXT one43 scoped timing comparison, automatic Golden return and retire;
then remove measured per-handoff overhead without weakening retirement.
Evidence docs/NATIVE-RGB-REAR-GENERATION-43-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear42 reaches ~30fps in two sessions; first-session consistency open

Measured change removes only the extra rolling handoff epoch wait; all10
replacement address readbacks, exact consumed-address/owner/ledger snapshots,
live FULL+8aux retirement and4-stage physical stop remain mandatory.
Fresh42/build53+unchanged libcamera05 delivered3same-boot80-request captures:
240 real4K linearNV12 Requests/four reused buffers,243 VB2 completions.
Callback interval rates15.1686/29.9479/29.9452fps. Sessions2/3 each80sensor
epochs for80 handoffs,160 real full-cadence Requests total. First session
remained slow (158epochs/80handoffs); uniform30fps startup NOT yet qualified.
Measured baseline41 callback10.2426/14.9776/12.0093fps; aggregate237-interval
rate12.113->22.605fps (1.866x), using identical libcamera05 probe.
Completion wait55.73/25.45/25.37ms per handoff; explicit epoch wait0 in all3.
Prepare4.76/3.54/3.59ms,retire5.31/4.28/4.32ms. Allocation/retirement crossing a
frame deadline is a next hypothesis, not yet independently proven causality.
No pixel reads/copy, command replay, IRQ mask/ACK or MMIO-value changes.
All4 stops and DMA/owner/arena cleanup PASS each;3 sensors suspended,
neutral graph and ISP clocks idle each. Snapshot retries1/0/0 recovered safely.
No hazards/watchdog; automatic distinct Golden607ade99-8f89-4728-be8e-495fca08e681,
protected hashes unchanged.42 consumed/retired, service/timer disabled,
static watchdog inactive; no armed jobs/nodes/modules. Never retry40..42.
29 source checksPASS,3 ARM64 W1/Werror0 diagnostics; actual queue GCC/Clang
ASAN/UBSAN28019 assertions/211 negatives each and68 measurement negatives.
Native72/74IDs148boots/pre10/failed-after-start22; combined81IDs162boots.
NEXT consistent30fps from first session by investigated allocation/mapping/
retirement deadline work, preserving strict consumed-address/owner proof;
then longer lifecycle/soak, semanticIPA3A/controls/SensorTimestamp and matched
Windows optical parity. Front calibration deferred; product incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-42-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear42 measured scheduler change source qualified; hardware pending

Fresh42/build53 removes ONLY the extra rolling per-handoff epoch wait.
The latest stable exact-owner/full ledger snapshot still precedes the handoff.
All10 address writes/readbacks and source-locked RUP/AUP are unchanged.
Every FULL and auxiliary mapping remains held until the original exact all10
consumed-address completion and stable retirement proof, or4 physical stops.
No register-value/mask/ACK changes, command replay, new pixel read or release
authority from timing. The actual queue's other source tokens equal baseline.
29 source checks PASS;3 ARM64 W1/Werror modules0 diagnostics; retained queue
GCC/Clang ASAN/UBSAN80 model completions and211 negatives each. Measurement
parser requires policy1 and epoch-wait0; existing ownership/failure gates intact.
Libcamera05 unchanged from hardware41. 42 unconsumed/uninstalled/unarmed.
Baseline41:240 real4K NV12 Requests/3clean same-boot sessions; ~29.95sensor epochs/s,
callback10.24/14.98/12.01fps; collection56--57ms and added epoch wait2--30ms.
41 retired, Golden8b3227b1-2960-45a6-8720-3ffcecc6295c, no hazards/watchdog.
Native69/73IDs146boots/pre10/failed-after-start22; combined80IDs160boots.
NEXT one42 three80-request comparison boot, automatic Golden return and retire.
Full-rate/adaptiveIPA3A/SensorTimestamp/optics/longsoak still unproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-42-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear41 hardware cadence baseline PASS; targeted scheduler change next

Three independent same-boot80-request libcamera sessions passed at4K linear
NV12/four reused buffers:240 actual Requests,243 VB2 completions, owner1->2->3.
Every session completed all4 stops and DMA/owner/arena cleanup, all3 sensors
suspended, neutral graph and ISP clocks idle. No hazards/watchdog. Automatic
distinct Golden8b3227b1-2960-45a6-8720-3ffcecc6295c; protected hashes unchanged.
41 consumed/retired, service/timer disabled, static watchdog inactive.
No armed test, camera jobs/nodes/modules. Never retry consumed40/41.

Read-only baseline measures sensor-pipeline epochs29.948/29.953/29.954Hz,
not sensor SOF timestamps. Real79-interval callback rates10.2426/14.9776/12.0093fps.
Each handoff spends56.2--57.3ms in completion collection; per-handoff explicit
epoch wait averages29.84/1.94/17.30ms and accounts for most session variation.
Prepare3.53--4.68ms,retire4.29--5.34ms. Startup0.247--0.272s, teardown0.090--0.130s.
Thus startup overhead is not the major bottleneck. No queue policy changed.
NEXT fresh42 removal of extra per-handoff epoch wait; preserve strict owner/
all10 consumed-address/live-retirement proof, mappings and4-stop failure path.
Compare measured cadence and all3 clean sessions before any performance claim.
Source29 checksPASS; native69/73IDs146boots/pre10/failed-after-start22,
combined80IDs160boots. Full rate/IPA3A/SensorTimestamp/optics/longsoak incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-41-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear41 read-only cadence source qualified; hardware pending

Fresh41/build52+libcamera05 adds aggregate stage timing around the exact
qualified rear40 queue calls and branches. No per-frame logging, pixel read,
address/IRQ changes, DMA-policy change or timing-based retirement authority.
GCC/Clang compiled actual kernel formatter is admitted by the actual parser;
67 malformed timing negatives. Removing only instrumentation reproduces
the complete qualified queue source (whitespace normalized).
Application probe separates79 callback intervals/driver-completion timestamp
gaps from start/stop overhead. Driver timestamps are NOT sensor SOF timestamps.
All29 source checks PASS,3 ARM64 W1/Werror modules0 diagnostics; six standard
libcamera Werror testsPASS. Retained ownership/reclaim/gate/snapshot negatives
remain. Source-harness invocation/fixture/access repairs logged, no hardware
attempt; original failure logs retained. 41 unconsumed/uninstalled/unarmed.
Latest hardware PASS40 remains3same-boot sessions/240 real4K NV12 requests,
Golden5aafe7af-4479-4a75-b998-ee5ccc65450a. Never retry consumed40.
Native66/72IDs144boots/pre10/failed-after-start22; combined79IDs158boots.
NEXT one41 timing-baseline boot, automatic Golden return, retire; measured
bottleneck repair then full-rate/IPA3A/controls/SensorTimestamp/optics/longsoak.
Front calibration deferred; full rate and optical parity remain unproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-41-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear40 three same-boot captures and clean shutdown hardware PASS

Fresh40/build51+libcamera04: three independent open/configure/start/80 real
reused Requests/stop/release sessions in ONE boot,240 actual application
Requests total; four application DMA-BUFs per session,4K linearNV12,
stride3840/image12441600/two logical planes. No reboot/module reload/OS sleep
between sessions. Unique owner epochs1->2->3; both guards completed3/unpoisoned.
Each session:81 live VB2 completions/80handoffs+source-locked RUP commits,
4 physical stops and DMA/owner/command arena cleanup.243 kernel completions
include3 extras racing STREAMOFF; only240 application successes claimed.
All3 sensors bound/runtime-suspended, media graph neutral and ISP clocks idle
after EACH session. Startup22 exact serialized BL receipts/4 arenas retired
each, no command replay.898IRQ records drained through16-slot wrap,518epochs.
Snapshot retries0/1/0: original strict proof recovered one real IRQ/epoch race
without reprogramming, disabling IRQs or releasing an uncertain mapping.
Rates14.2641/11.5617/14.187fps including start/stop; aggregate13.21089fps.
Full rate, adaptiveIPA/3A, SensorTimestamp, matched optics and long soak incomplete.
Service success0, no kernel hazards/watchdog. Automatic distinct Golden
5aafe7af-4479-4a75-b998-ee5ccc65450a; protected hashes unchanged.
40 consumed/retired, service+timer disabled/static watchdog inactive;
no armed test/nodes/modules/jobs. Never retry36..40. Source28 unconsumed.
28 source checks PASS,3 ARM64 W1/Werror0 diagnostics,233 admission negatives.
Native66/72IDs144boots/pre10/failed-after-start22; combined79IDs158boots.
37..39 clean hardware captures but harness failures remain documented, never
promoted to full qualification successes.40 fully passed its3-session harness.
NEXT full-rate/cadence profiling then semantic IPA/statistics/3A/controls/
SensorTimestamp and matched Windows optics; longer lifecycle/soak afterward.
Front calibration deferred until rear finished. Product stack incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-40-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear40 exact per-session command owner parser qualified

39's two hardware captures were clean; only parser owner=1 assumption failed
successful owner2 command retirement. Fresh40/build51 keeps hardware behavior,
takes exact session owner1/2/3 in command-retirement parser and blocked-state
checks. No blanket acceptance of arbitrary owner values.
28 checks PASS,3 ARM64 W1/Werror0 diagnostics;233 admission negatives.
Actual staged C marker/gate/snapshot/command log formats:13 emitted records
per GCC/Clang, including command owners1/2/3, all parsed by actual runtime.
All mandatory parsers checked against actual two-session39 scalar records and
a clearly synthetic third-owner fixture. No fixture presented as hardware.
40 unconsumed/uninstalled/unarmed;libcamera04 unchanged;3sessions/240Requests target.
39 retired, Golden76bb4540 safe, no watchdog/hazards, protected hashes intact.
Native63/71IDs142boots/pre10/failed-after-start22; combined78IDs156boots.
NEXT one40 hardware boot, strict3sessions, mandatory Golden return and retire40.
Two-session restart proven38/39; full-rate/adaptiveIPA/optics/soak incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-40-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear39 two clean captures; owner1 parser assumption exposed

Two same-boot libcamera processes each delivered80 real Requests,160 total,
four reused buffers.81 VB2 completions/80handoffs+commits each, owner1->2.
All4stops and DMA/owner/arena cleanup PASS each; no kernel hazards/watchdog.
Explicit unique session markers and rotation-tolerant scoping worked.
Command retirement record carries the actual owner epoch, not a bool.
Runtime parser retained owner=1 from historical single-use proof and rejected
successful owner2 retirement in session2; session3 not started.
Three-session qualification FAIL; two-session restart proof remains valid.
39 consumed/retired, units disabled; Golden76bb4540-da51-4b1a-a7d7-dacd55705373,
protected hashes unchanged. Never retry39.
Native63/71IDs142boots/pre10/failed-after-start22; combined78IDs156boots.
NEXT fresh40/build51 parser takes exact session owner; actual emitted command
retirement formats tested for1/2/3 and retained owner2 logs before hardware.
Evidence docs/NATIVE-RGB-REAR-GENERATION-39-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear39 explicit session scope qualified; hardware pending

38 completed two clean80-request same-boot captures but harness history-prefix
check rejected ring rotation before session3. First real snapshot race recovered.
Fresh39/build50 emits identity39/session1,2,3 before each transaction.
Runtime scopes strict mandatory records to the unique current session marker.
Old ring history may rotate; missing/duplicate/foreign current markers fail.
Actual retained38 scalar records with synthetic labels/history rotation and
actual compiled current marker/gate/snapshot formats pass real runtime parsers.
27 checks PASS,3 ARM64 W1/Werror modules0 diagnostics;200 runtime negatives.
Bounded snapshot-EAGAIN proof retry, full cleanup and permanent failure gates
unchanged. Libcamera04 unchanged,3 independent80-request opens remain target.
39 unconsumed/uninstalled/unarmed;38 retired, no hazards/watchdog, Golden d695ef7f safe.
Native61/70IDs140boots/pre10/failed-after-start22; combined77IDs154boots.
NEXT one39 boot, strict3sessions/240Requests, mandatory Golden return and retire39.
Two-session restart proven38; three-session qualification pending.
Full rate, adaptiveIPA/3A, SensorTimestamp, matched optics and long soak incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-39-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear38 two clean same-boot captures; log-history harness failure

Two independent libcamera processes each delivered80 real reused Requests,
160 total,4K linearNV12/four buffers per session. Same boot, no module reload.
Owner epochs1->2; each81 VB2 completions/80handoffs+commits and4 clean stops,
DMA/owner/arena releases. First session used1 bounded-EAGAIN snapshot retry:
hardware read/drain repair now exercised; second used0. No hardware errors/hazards.
All3 sensors suspended and neutral graph proven before session2; ISP clocks
idle after both. Second final sensor state not recorded by stopped harness.
Rates11.8539/13.0545fps including start/stop, full rate still unqualified.
Harness required complete dmesg history as prefix; kernel ring rotation
invalidated that condition after session2. Third session did not start.
Three-session qualification FAIL; two-session same-boot restart hardware proven.
38 consumed/retired, units disabled; Golden d695ef7f-7361-4a4d-ab29-728a26ce39d1,
no watchdog, protected hashes unchanged. Never retry38.
Native61/70IDs140boots/pre10/failed-after-start22; combined77IDs154boots.
NEXT fresh39/build50 unique per-session markers and rotation-tolerant strict
record scoping; then complete3sessions/240Requests and mandatory Golden return.
Evidence docs/NATIVE-RGB-REAR-GENERATION-38-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear38 emitted scalar format fixed and qualified; hardware pending

Fresh38/build49 fixes only the added snapshot log's literal backslash-n.
Actual staged kernel format strings compile and their real stdout is accepted
by the actual runtime parsers under GCC/Clang; the exact retired37 malformed
formatter is compiled too and rejected. No synthetic replacement log in this check.
26 checks PASS;3 ARM64 W1/Werror modules0 diagnostics,170 runtime negatives,
snapshot retry2506 assertions/33negatives and gate179/31 each GCC/Clang.
Bounded snapshot-EAGAIN read/drain and strict fatal-error admission retained.
Three same-boot open/configure/start/80Requests/stop/release sessions required,
with neutral graph,3 idle sensors and idle ISP clocks between each.
38 unconsumed/uninstalled/unarmed; libcamera04 unchanged.
37 had one clean80-request capture, then failed harness log format before session2.
36/37 retired, never retry; Golden d2af624e safe, protected hashes unchanged.
Native59/69IDs138boots/pre10/failed-after-start22; combined76IDs152boots.
NEXT one38 hardware boot and mandatory Golden return, then retire38.
No same-boot restart hardware proof, full-rate/adaptiveIPA/optics/soak claim yet.
Evidence docs/NATIVE-RGB-REAR-GENERATION-38-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear37 one clean80-request capture; harness record failure

37/build48 delivered80 actual reused libcamera Requests through4 buffers,
4K linearNV12,elapsed5.64215s/rate14.179fps including start/stop.
81 live VB2 completions,80 handoffs/commits,338 exact-owner events,163epochs.
All4 stops, DMA/owner/arena release succeeded; both gates completed1,unpoisoned.
New scalar queue-snapshot log contained a literal backslash-n suffix.
Strict harness rejected that malformed record and did not start session2.
Three-session qualification FAIL; no same-boot restart proof yet.
Snapshot retries0: new bounded path not exercised by a race on this hardware run.
37 consumed/retired, units disabled; automatic Golden d2af624e-1718-422c-9057-714a76b6246f,
no watchdog or kernel hazards; protected hashes unchanged. Never retry37.
Native59/69IDs138boots/pre10/failed-after-start22; combined76IDs152boots.
NEXT fresh38/build49: corrected actual formatter, compiled-log parser regression,
then three same-boot80-request sessions. Full rate/3A/optics/soak still incomplete.
Evidence docs/NATIVE-RGB-REAR-GENERATION-37-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear37 snapshot race repair qualified; hardware pending

36 first rolling stream rejected-EAGAIN after2 VB2 buffers/1 handoff.
All startup/BL22/first-generation FULL+8aux/command retirement proofs succeeded;
later strict observation can race IRQ publication or epoch advancement.
Fresh37/build48 drains exact-owner events and repeats only snapshot-EAGAIN,
bounded256 attempts at250-500us; original ownership/address/completion proof
remains required. Hardware/address/owner errors remain immediately fatal.
Old mappings remain held; a FULL release is never repeated if AUX proof races.
No reprogramming, command replay or IRQ disabling occurs in a snapshot retry.
Three clean sessions remain the target; all per-session failure gates retained.
25 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; actual retry functions
GCC/Clang ASAN/UBSAN with persistent races, partial retirement and fatal errors.
170 runtime admission negatives; hardware APIs in hosted checks are models.
37 unconsumed/uninstalled/unarmed; libcamera04 unchanged. Hardware35 latest PASS.
36 consumed/retired, no watchdog/kernel hazards; Golden11f64619 safe, hashes intact.
Native58/68IDs136boots/pre10/failed-after-start22; combined75IDs150boots.
NEXT one37 boot, three sessions/240 Requests; mandatory Golden return then retire.
No same-boot restart hardware proof, full-rate/adaptiveIPA/optics/soak claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-37-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear36 failed first rolling stream; safely retired

36/build47 completed startup packets and22 exact BL receipts, retired all4
command arenas and the first FULL+8aux generation, then completed2 live VB2
buffers. First rolling stream ended with-11 after1 handoff/RUP commit,
cursor14: no completed80-request application session, no restart hardware proof.
Live observer returns-EAGAIN when IRQ publication/epoch changes during the
strict snapshot; source investigation targets a bounded drain-and-reobserve
path that retains all old mappings until the original complete proof succeeds.
Any actual ownership/address/error failure must remain fatal and pin state.
Both session gates poisoned (attempted1/completed0); no second start occurred.
Automatic Golden11f64619-454f-41df-b03f-e60b5feab79a succeeded; no kernel hazards,
no watchdog, protected hashes unchanged.36 consumed/retired, units disabled.
Never retry36. Latest successful hardware remains35 with80 actual Requests.
Native58/68IDs136boots/pre10/failed-after-start22; combined75IDs150boots.
NEXT fresh37/build48 repair transient queue snapshot admission and repeat3sessions.
Evidence docs/NATIVE-RGB-REAR-GENERATION-36-20261009.json.
Earlier entries are historical.

## 2026-10-09 rear36 same-boot restart source qualified; hardware pending

Fresh36/build47 permits exactly three serialized rear sessions in one boot.
Both outer and arena gates require full clean teardown and increasing owner
epochs; any failed attempt permanently poisons admission. No reset API.
Outer candidate remains single-use with mandatory automatic Golden return.
Libcamera04 unchanged: three independent open/configure/start/80 reused
Requests/stop/release processes; four application buffers per session.
Neutral graph, all three sensors runtime-suspended and idle ISP clock counts
required between sessions; no module reload, reboot or OS sleep between them.
24 checks PASS; three ARM64 W1/Werror modules, zero diagnostics.
Actual staged gate/clean predicate/arena wrapper: GCC and Clang ASAN/UBSAN,
179 assertions and31 negatives each,12 fault stages; hardware APIs modeled.
Runtime160 strict admission negatives (103 retained graph/queue +57 restart/clock).
36 unconsumed/uninstalled/unarmed. Latest hardware PASS remains35,80 Requests.
Native57/67IDs134boots/pre10/failed-after-start21; combined74IDs148boots.
NEXT one36 hardware candidate: three sessions/240 Requests, then retire36.
No same-boot restart hardware proof, full-rate, adaptive3A, optics or soak claim.
Never retry consumed33/34/35. Source28 remains unconsumed.
Evidence docs/NATIVE-RGB-REAR-GENERATION-36-PREP-20261009.json.
Earlier entries are historical.

## 2026-10-08 rear35 continuous reused Requests and clean shutdown hardware PASS

Fresh35/build46 + libcamera04:80 actual application Requests completed through
four reused DMA-BUF buffers,3840x2160 linearNV12,stride3840/image12441600,
two logical planes; zero pixel reads/CPUcopy, no SensorTimestamp.
81 VB2 buffers completed live,80 output handoffs and source-locked RUP/AUP
commits,318 exact-owner IRQ records drained through16-slot queue wrap,203epochs.
Current mapping stays held until all10 replacement consumed addresses and stable
owner proof permit old FULL+8aux retirement; final current mapping held to4stops.
Startup4command arenas retired after exact22BL receipts, no DMAcommand replay.
Application80 vs kernel81 is an extra completion racing STREAMOFF, not an
additional application success. Strict sequences/planes/timestamps checked.
Elapsed6.96817s including startup/stop,11.4808fps delivered: full rate unqualified.
All4 physical stops/DMA/owner/arena cleanup PASS; all3sensors bound/suspended,
IFE594MHz CSID/PHY300MHz counts0;10VFE/8IPP error phases0, hazards0, no watchdog.
Automatic Golden36563c89-5d18-40bc-8fa1-ba366c5d79c8; protected hashes unchanged.
35 consumed/retired, units disabled; no armed tests/nodes/modules/jobs.
22 source checks PASS,3 ARM64 W1/Werror0; queue GCC/Clang26529 assertions/211
negatives each; fixed output commit537 assertions/15 negatives each,103parser
negatives, waitqueue271 assertions plus rejected omitted-initializer control.
33 pre-sensor QBUF waitqueue Oops and34 third-generation commit timeout are
fully retired;35 fixes held. Never retry33/34/35. Source28 still unconsumed.
Native57/67IDs134boots/prestream10/failed-after-start21; combined74IDs148boots.
NEXT same-boot rear restart/open-close and recovery; then full-rate delivery,
semantic IPA/statistics/3A/controls/SensorTimestamp and matched Windows optics.
Single-use startup remains; no repeat lifecycle/long soak/adaptive3A/optics claim.
Front calibration deferred until rear finished.
Evidence docs/NATIVE-RGB-REAR-GENERATION-35-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear35 source-locked output commit qualified, hardware pending

34 hardware fixed the QBUF waitqueue fault and delivered1 VB2 buffer while live.
Generation3 address writes alone produced no consumed receipts: timeout-110,
IPP33epochs/12events, no overflow/errors/hazards; mappings conservatively held
until automatic Golden8be04a9a-5760-416c-9f4e-25c2a16ad619.34 consumed/retired,
units disabled, no watchdog, protected hashes unchanged. Never retry34.
Source startup packets end with CSID RUP/AUP0x01f501f5 at named register0x18.
Fresh35/build46 applies that exact commit after all10 address readbacks under
exclusive rear-owner/epoch/live-path guards; no command-DMA resubmission.
22 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; actual fixed MMIO helper
GCC/Clang537 assertions,15 negatives each; queue26529 assertions/211 negatives/
80 model frames each. Runtime103 negatives. All hardware APIs are models.
35 unconsumed/uninstalled/unarmed; libcamera04 unchanged. NEXT35 real80 Requests.
Hardware32 remains latest clean success; no persistent rear proof yet.
Native56/66IDs132boots/prestream10/failed-after-start21; combined73IDs146boots.
No adaptive IPA, SensorTimestamp, full-rate/soak or optical parity claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-34-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-35-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear34 queue initialization repaired, source qualified, hardware pending

33 consumed/retired after a pre-sensor kernel Oops in QBUF3: rear worker started
without initializing the shared buffer waitqueue. No packets or frames; mandatory
return to Golden6a092b27-5fae-40d7-8ffd-5900bd57a007 succeeded, protected hashes
unchanged; units disabled, no watchdog. Never retry33.
Fresh34/build45 initializes the queue at video registration before any callback.
21 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; actual QBUF/start/join
GCC/Clang271 assertions each plus omitted-initializer negative control rejected.
Rolling queue28030 assertions/211 negatives/80 simulated frames each retained.
libcamera04 unchanged. NEXT one-use34 hardware80 reused4K NV12 requests.
34 unconsumed/uninstalled/unarmed; hardware32 remains latest success.
Native55/65IDs130boots/prestream10/failed-after-start20; combined72IDs144boots.
No continuous rear/adaptive IPA/SensorTimestamp/full-rate/optical parity claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-33-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-34-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear33 continuous Request queue source qualified, hardware pending

Fresh33/build44 + libcamera04 passed20 pre-install checks; all3 ARM64 modules
W1/Werror with zero diagnostics. Actual rolling queue/ledger/address writes/live
output retirement: GCC and Clang ASAN/UBSAN each28030 assertions,80 model
completions,211 negative cases. Runtime/graph admission102 negatives.
Hardware APIs are models; no rear continuous hardware proof yet.
Four application DMA-BUF Requests reuse buffers until80 real completions;
all10 replacement consumed addresses and stable owner observation precede live
FULL/8aux retirement and VB2 delivery. Startup commands retired once, no command
resubmission; fixed startup ISP settings. Stop joins worker before cancellation.
Latest physical success remains32: two4K linear NV12 Requests and clean release.
33 unconsumed/uninstalled/unarmed; automatic Golden return + independent watchdog
required. Superseded43/lib03 remained source-only, never installed/consumed.
Golden8ec205f1-a1c1-4493-96ad-3f6d9e6a1395; native55/64IDs128boots, prestream9,
failed-after-start20; combined71IDs142boots. Source28 remains unconsumed/uninstalled.
NEXT install and qualify33 persistent rear capture, then restart/lifecycle,
semantic IPA/statistics/controls/SensorTimestamp and matched Windows optics.
No rear adaptive IPA, SensorTimestamp, full-rate, long-soak or optics claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-33-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear32 live command retirement and clean return hardware PASS

Fresh32/build42 frees all4 startup command arenas while exclusive rear ISP live,
after exact22 serial FIFO0 BL_DONE receipts/current completion and stable complete
replacement ownership. ret0/released4/tombstone-valid1/arenas-pinned0/owner1/
BL-complete22/stop-flags0/VB2-complete0/requeue0. Software sequence is not hardware
Request ID. All packet allocations zero; retained owner/last receipt validates
post-stop cleanup without double free. Commands are not rewritten/resubmitted.
First FULL+old8aux retired live again; both ledgers and replacement FULL+8aux
held until4 physical stops. All10 replacement WM masks1023,13 events drained,
stableEpoch3. Two real libcamera DMA-BUF 3840x2160 linear NV12 Requests,
stride3840/image12441600; zero pixel reads/copy, SensorTimestamp absent.
All4 stops/DMA/owner/arena cleanup PASS; all3 sensors bound/runtime-suspended,
IFE594MHz CSID/PHY300MHz counts0;10VFE/8IPP errors0, hazards0, no watchdog.
Automatic Golden 8ec205f1-a1c1-4493-96ad-3f6d9e6a1395 verified, protected hashes unchanged.
32 consumed/retired, units disabled; no armed tests/nodes/modules/jobs.
Source19 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; GCC/Clang retirement
harness15609 cumulative assertions/1580 negatives each, graph parser86 negatives.
Native55 completed/64IDs128boots/prestream9/failed-after-start20;
combined71IDs142boots. Source28 still unconsumed/uninstalled.
NEXT persistent rear Request scheduler, separately guarded command reuse and
safe early delivery; then semantic IPA/statistics/controls/SensorTimestamp and
matched Windows optics. Front calibration deferred; continuous rear/optical
parity and command address reuse remain unproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-32-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear32 live command retirement source qualified

Fresh32/build42 all3 ARM64 modules W1/Werror with zero diagnostics;19 checks PASS.
Actual command allocator/layout/receipts/live free/tombstone harness GCC/Clang
ASAN/UBSAN/Werror each15609 cumulative assertions and1580 retirement negatives,
including66 cross-type command CPU aliases,192 command/aux CPU aliases and88
command/output DMA overlaps including FULL mapped tails. Hardware APIs are models.
All exact22 receipts, current FIFO completion, exclusive owner, completed ledgers
and stable live replacement observation precede all4 command arena frees.
Retired packet zero state and retained owner/last receipt are verified before
post-stop cleanup; no command reuse/resubmission or early VB2 delivery.
Graph/runtime parser86 negatives,16 new strict retirement-record cases.
Build40 and41 superseded source-only, never installed/consumed; build42 current.
NEXT fresh32 one-use hardware qualification with automatic Golden return.
31 remains latest hardware PASS. Native54/63IDs126boots/prestream9/after-start20;
combined70IDs140boots. Golden aa8479b7-fe8d-45ec-a41f-10d86bb26f89.
32 unconsumed/uninstalled/unarmed; rear continuous capture and optics unproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-32-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear31 exact22 command receipts live-qualified, clean return PASS

Fresh31/build39 physically verifies4 packets/22 serialized FIFO0 BL_DONE
receipts sequence1..22 bound to exact packet request/owner/slab allocation.
Dedicated ISR completion record survives separate INLINE in source/tests;
hardware receipt check ret0 while camera live and all4 command slabs pinned.
Sequence is software serialization, not hardware Request ID; no command live
free/rewrite/requeue. All10 replacement WM masks1023, nine events drained,
stable Epoch3; both ledgers complete. Old FULL+all8 auxiliary allocations
retired live again, replacement FULL+eight auxiliaries retained until four stops.
Two actual libcamera DMA-BUF Requests at3840x2160 linear NV12/stride3840/
12441600bytes; zero pixel reads/copy. Complete clean stops/DMA/owner/arena release.
All3 sensors bound/suspended, IFE/CSID/PHY clocks idle; tenVFE/eightIPP error
phases zero. Service success0, no watchdog/kernel hazard. Automatic Golden
aa8479b7-fe8d-45ec-a41f-10d86bb26f89 verified; protected hashes unchanged.
31 consumed/retired, units disabled; no armed tests/nodes/modules/jobs.
Earlier30 protocol rejection retired before sensor Start; original IRQ cause
was not directly logged and is not claimed as independently observed.
Native54 completed/63IDs126boots/prestream9/failed-after-start20;
combined70IDs140boots. Source28 still unconsumed/uninstalled.
NEXT independent live command arena retirement/recycling with exact receipts,
then persistent rear Request scheduler and safe early delivery. Semantic rear
IPA/statistics/controls/SensorTimestamp and matched Windows optics follow;
front calibration deferred, continuous rear/optical parity remain unproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-31-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear31 dedicated BL_DONE receipt source qualified

Fresh31/build39 all3 ARM64 modules W1/Werror0; all18 checks PASS.
Dedicated ISR record publishes BL_DONE sequence/base/length/status before
completion wake. Separate INLINE cannot overwrite it; FIFO receipt wait and
current check consume that release/acquire record, retaining sticky error and
exact request/owner/allocation/22-BL binding. Existing generic commit/wait
behaviour stays intact. Actual hosted FIFO/IRQ-record tests GCC/Clang each
762 assertions/40 negatives; packet/allocator/layout tests9935/350 each,
including16 mixed BL_DONE/INLINE receipt matrices. Hardware APIs are models.
Read-only eligibility only: all4 command slabs stay until physical stop.
NEXT fresh31 hardware qualification with automatic Golden return.
30 was consumed/retired pre-stream protocol failure, not a camera frame failure;
its physical IRQ cause is not independently observed. Hardware29 remains the
latest successful proof. Native53/62IDs124boots/prestream9/after-start20;
combined69IDs138boots. Golden d37972ea-7752-4066-8b5e-c6ff6901f59f.
31 is unconsumed/uninstalled/unarmed; continuous rear/live command recycling/
optical parity unproven; front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-31-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear30 receipt protocol gate rejected before sensor Start, retired

Fresh30/build38 booted and packet0 completed, slot0 enabled. Packet1 receipt
path returns EPROTO(-71) before any sensor Start: packets1000/epochs0/events0/
frames0, all exposed DMA/commands intentionally held through recovery reboot.
No physical live receipt eligibility or live command retirement proof.
Two cold boots completed; service exit1, no watchdog/kernel hazard. Automatic
Golden d37972ea-7752-4066-8b5e-c6ff6901f59f verified; all protected hashes unchanged.
30 consumed/retired; units disabled, no armed tests/nodes/modules/processes.
Native53 completed/62IDs124boots/prestream9/failed-after-start20; combined69IDs138boots.
Working hypothesis: last_irq_status is overwritten by generated INLINE
IRQ in packet1, so strict post-synchronize BL_DONE-only snapshot rejects.
Do not present this as a physically observed IRQ cause yet. NEXT dedicated
BL_DONE record, INLINE overwrite fault proof, fresh31/build39 hardware test.
Latest successful hardware29 remains authoritative. Front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-30-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear30 exact command receipts source qualified, hardware29 retained

Fresh source build38 compiles all3 ARM64 modules W1/Werror with zero diagnostics.
All18 pre-install checks PASS. Actual allocator/layout/packet/receipt helpers
GCC/Clang ASAN/UBSAN each9919 receipt assertions/350 negatives; actual staged
FIFO wait/commit/current checks each686 assertions/40 negatives. Actual live
output release50339 assertions/1245 negatives and post-stop reclaim739/216
remain PASS; retained119-edge graph/strict scalar parsers now70 negatives.
Capture all22 serialized FIFO0 BL_DONE receipts under the submit mutex, bind
each to exact slab/DMI/dynamic allocations, packet Request and current owner,
then observe unchanged all-ten-WM live replacement and current final receipt.
Sequence is a software serialization tag, not a hardware Request identity.
No live command frees/rewrites/requeue; all4 command slabs remain until stop.
MMIO/IRQ/DMA APIs in hosted checks are models; physical receipt proof pending.
NEXT install/verify fresh30 one-use candidate and automatic Golden return;
then independent live command retirement/recycling, persistent rear Requests,
safe early delivery, semantic IPA/SensorTimestamp/optics. Front deferred.
Latest hardware29 remains: first FULL and eight auxiliaries retired live,
two real4K libcamera Requests, clean stop/release and Golden return PASS.
Source30 unconsumed/uninstalled/unarmed; counts unchanged native53/61IDs122boots
failed20; combined68IDs136boots. Golden a516a2a1-3bd5-44d4-8abc-64b2d68df545,
protected hashes unchanged. Evidence docs/NATIVE-RGB-REAR-GENERATION-30-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear29 live old FULL and all auxiliary outputs retired, clean release PASS

Fresh29/build37 physically frees old eight auxiliary allocations before stop,
after old FULL mapping retirement: aux ret0/released8/old-valid1; replacement
FULL pinned1/all8 auxiliaries pinned; all stop flags0, no early VB2 completion
or request/address reuse. Both ten-WM ledgers, replacement command receipts and
all live readback masks1023 match;14 events drained, stable Epoch3. Scope is
the first completed output generation only. Old ledgers/command arenas remain
owned until physical stop; live command retirement/recycling is still unproven.
Two real libcamera Requests complete at3840x2160 linear NV12/stride3840/
12441600bytes with zero pixel bytes read/copied. All four subsequent physical
stops and remaining DMA/owner/arena release PASS; dma_pinned0. All sensors
bound/suspended, IFE/CSID/PHY clocks idle,10 VFE/eight IPP error phases zero.
No kernel hazards or watchdog; service success0. Verified automatic Golden
return a516a2a1-3bd5-44d4-8abc-64b2d68df545; protected payload hashes unchanged.
29 consumed/retired; units disabled; no camera nodes/modules/jobs/armed tests.
Native53 completed/61IDs122boots failed20; combined68IDs136boots.
NEXT independently qualify live command arena retirement/recycling, persistent
rear Request scheduler and safe early buffer delivery; then semantic rear IPA/
statistics/controls/SensorTimestamp and matched Windows optics. Rear still two
Requests, continuous delivery/optical parity unproven. Front calibration deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-29-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear29 old auxiliary live retirement source qualified

Fresh source build37 compiles three ARM64 W1/Werror modules with zero diagnostics.
All16 pre-install checks PASS. Actual shared guard/release helper GCC/Clang
ASAN/UBSAN50339 assertions/1245 negatives each, including old/new DMA and length
bindings, all120 CPU aliases and210 live readback races; actual post-stop
reclaimer739 assertions/216 negatives each. Real graph/parser57 negatives PASS.
The finite exclusive runner retires old eight auxiliary allocations only after
old FULL live retirement, both ten-WM completions, replacement command receipts,
current ownership, drained events and all ten replacement address readbacks.
Old ledgers/command arenas and all replacement outputs remain pinned until
physical stop. No false stop flags, early VB2 delivery or address requeue.
Source only, uninstalled/unarmed/unconsumed; latest hardware proof remains27.
NEXT fresh single-use29 hardware proof with automatic Golden return, then
command arena recycling and persistent rear Requests; semantic IPA/optics follow.
Front calibration deferred. Golden6de92f65-627e-40f5-b71e-1272cfbaf638; counts
unchanged native52/60IDs120boots failed20; combined67IDs134boots.
Evidence docs/NATIVE-RGB-REAR-GENERATION-29-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear auxiliary ownership guard source qualified, hardware27 retained

Recovered clean HEAD/origin f79fc746 on Golden6de92f65-627e-40f5-b71e-1272cfbaf638.
Before auxiliary recycling, the actual live FULL guard now requires each of the
16 auxiliary allocations' full DMA address and length to match its completed
request ledger, and rejects all120 CPU allocation aliases within/across sets.
The expanded fault matrix reproduced old build35 accepting changed auxiliary DMA.
Fresh source build36 passes three ARM64 W1/Werror modules, zero diagnostics.
Six relevant GCC/Clang ASAN/UBSAN checks PASS; actual live helper24494 assertions/
751 negatives each, including168 new ownership faults with no release/mutation.
Observer, actual post-stop reclaimer, public/coherent lifecycle and threaded
event queue regressions PASS. Hardware/MMIO/IRQ/DMA APIs in these checks are
explicit host models. No new hardware attempt, install, arm, camera start or
reboot. Source-only identity28 is unconsumed; boot assets are not installed.
Golden payload hashes verified unchanged. Latest hardware proof remains27:
two real libcamera4K Requests and old FULL mapping live retirement/clean stop.
Old auxiliary/command live release and persistent rear Requests remain unproven.
NEXT guarded old auxiliary retirement, separate command arena recycling and
persistent request scheduler; then semantic IPA/statistics/controls and optics.
Front calibration remains deferred. Counts unchanged native52/60IDs120boots
failed20; combined67IDs134boots.
Evidence docs/NATIVE-RGB-REAR-AUX-BINDING-20261008.json.
Earlier entries are historical.

# Rear public V4L2 buffer integration

Rear23 proves two 4K native NV12 generations and clean output/ledger/owner/PM/
command release on physical SP11. The public video queue is not connected yet.

native-rear-video-dma.inc validates an ACTIVE VB2 buffer on the exact VFE1 PIX
endpoint and exact single-plane NV12 format. It walks every DMA-mapped SG entry,
uses mapped nents rather than orig_nents, rejects gaps/overlap/zero length/
32-bit overflow and checks the complete advertised plane fits. The output is
published only after all checks pass. It ignores cached buffer addr[0].
It neither maps CPU pixels nor writes MMIO, allocates, frees, completes a buffer
or grants hardware ownership.

The pure arithmetic and actual adapter pass GCC/Clang ASAN/UBSAN/Werror tests:
658 assertions, 155 negative cases and 64 valid mapped-segment partitions each.
The optional linear overlay compiles this adapter in a fresh source-only ARM64
build with three modules, W1/Werror, zero diagnostics. It installs no callback.
Evidence: docs/NATIVE-RGB-REAR-V4L2-DMA-ADMISSION-20261008.json.

Next connect an explicitly borrowed public FULL surface to the ten-WM ledger,
keeping auxiliary and command allocations independently owned. Retain the
actual VB2 mapping through hardware stop on every cancellation/close/failure
path; never pass borrowed output through dma_free_coherent. Then connect the
ordinary streaming worker/queue and rear-specific libcamera configuration and
typed semantic IQ. The one-use diagnostic and private compiled profile are
validation tools, not the production camera API. Continuous frames, metadata
pairing and matched-scene optical quality require physical application tests.

build-once.py creates a fresh external build path and never installs or boots.
Consumed/source build paths must not be overwritten; select a fresh suffix for
the next source revision. Run test-video-dma.py against that staged tree.
