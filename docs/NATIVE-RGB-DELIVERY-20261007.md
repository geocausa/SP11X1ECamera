## 2026-10-07 exposure response/readback hardware proven; gains still ambiguous

Fresh response02 source9c648fd8/kernel audit31/libcamera build09 passes320 standard
cam2560x1440 NV12 frames at30.00003fps,324 actual isolated IPA results,1625 owner
checks/325 retirements,18 grouped sensor ioctls and328 typed defaults. All19 reads
of known FLL/exposure/analogue/digital registers match commanded values,error0.
CCI write completion alone is no longer the only actuation evidence. Readback
confirms retained register values,not their optical pixel effect.

Exposure1000/2000 changes show six sharp,repeatable statistics and processed-Y
responses at command SOF+2,with stable restored baselines and unchanged receiver/
video source observations. Same offset seen in response01 retrospectively after
removing unsupported15%-of-absolute-luma threshold. Metering units/zero point are
unqualified; use response above measured noise,8 analyzer tests pass. Fresh02
qualifies exposure's empirical response delay2. First-row exposure timestamp is
still unproven. Analogue0/512 and digital256/512 writes/readbacks succeed but
responses remain ambiguous; no gain delay accepted,no copied delay2.

Both01/02 captured640 app frames/648 IPA results overall. All STOPs clean,error0,
sensors standby,graph neutral,no SOF after final STOP,critical0,Golden unchanged.
02 UTC capture17:29:35.803..17:29:47.897 on2026-10-07; current Golden
8dffb0ec-59fd-4ca5-8103-34b098d5cd21. Both response IDs consumed/retired; all26
candidate IDs retired,30 completed sensor streams,52 candidate/Golden boots.
Failure counters5 prestream/3 poststart qualification failures unchanged; response
capture PASS and unqualified gain timing are intentionally separate. No candidate
boot/unit/writer/FW remains. dc9ca301 GitHub sync issue is resolved.

NEXT isolate analogue/digital gain response in the already-proven native front
RAW path,using bounded baseline/raised/restored plateaus and known-register reads,
then compare hardware statistics/processed output and matched Windows same scene/
lighting/timestamps. Do not repeat the same ambiguous ISP experiment or infer a
brightness defect from low Y. Metering interpretation and physical illumination
remain unresolved. RAW work is a diagnostic,not a CPU image ISP or release path.
Automatic AE/AWB/DelayedControls still disabled/unqualified; SensorTimestamp absent.
Rear ISP/focus,dynamic tables,production ABI/clock policy,independent tuning,
soak/switch/fault and Windows optical acceptance remain. Earlier NEXT is history.
Evidence: docs/NATIVE-RGB-FRONT-CONTROL-RESPONSE-01/02-20261007.json,analysis
correction,readback audit31 and libcamera build09. Originals/pixels/logs private SP11.

## 2026-10-07 native grouped frame-length response hardware PASS

Fresh control-timing02 source74fef62f/kernel audit30/libcamera build08 physically
passes128 standard cam2560x1440 NV12 frames and132 actual isolated IPA results.
Six complete sensor V4L2 control-cluster writes at SOF16/32/48/64/80/96 alternate
FLL7108/3554, exposure1000/analogue0/digital256 unchanged. Initial setup plus six
successful CCI transactions are uniquely bracketed by userspace ioctls.
All six measured receiver interval responses start at command SOF+2; plateaus
15.00266/30.00534/15.00279/30.00533/15.00276/30.00541fps. CCI duration2.336-3.186ms.
Restored baseline at96 and held30fps through STOP. No brightness input is used.

128 app/statistics/IPA pairs,133 retirements,665 owner checks,136 typed defaults,
clean STOP,error0,all sensors standby,neutral graph,no SOF after final STOP,
critical kernel faults0,Golden hashes unchanged. Returned Golden
 a2506d21-9074-4cf6-87c9-b3a0f13828e1. timing01/02 consumed and retired; all24
candidate IDs retired,28 completed sensor streams,48 candidate/Golden boots.
5 prestream/3 poststart qualification failures; latest failure was01 analysis
precision, with successful capture/control writes. Its FAILED evidence remains.
No test boot/unit/writer/firmware remains. Private pixels/tuning/logs stay SP11.

01 used an incorrect individual5% period criterion on IRQ arrival observations.
Corrected acceptance uses plateau mean3%,median5% and disjoint30/15fps onset bands;
real-trace checks plus CCI-error/missing-commit/no-response negative checks pass,
and fresh02 independently confirms all six SOF+2 responses. IRQ times include
arrival jitter and are not first-row sensor exposure timestamps.

NEXT: separately measure exposure,analogue and digital control response under
stable-light screening and repeated up/down changes,with CCI completion/frame/
statistics identity. Do not copy the observed FLL offset2 to other controls or
publish applied-frame metadata. Standard DelayedControls parameters remain
unqualified,automatic AE/AWB disabled,SensorTimestamp absent. Metering units and
AE targets,dynamic tables,rear processed ISP/focus,production ABI/clock policy,
independent tuning,soak/switch/fault and matched Windows quality acceptance remain.
No diagnosed brightness defect; match physical camera/scene/position/lighting/time
and record weather/light changes. User rainy/cloudy report persists; no matched
Windows reference. Earlier NEXT statements are history.
Evidence: docs/NATIVE-RGB-FRONT-CONTROL-TIMING-02-20261007.json; failed01 and analysis
qualification are retained alongside kernel audit30/libcamera build08 reports.

## 2026-10-07 native receiver frame-start and restart hardware PASS

Kernel audit29/libcamera build07 physically pass both actual standard IPA paths.
Pipeline05 sourceb08bc32f:80 standard cam2560x1440 NV12 frames30.00469fps,
84 isolated IPA metering results,84 consecutive libcamera frameStart callbacks,
85 receiver IRQ SOFs,425 owner checks,88 typed defaults. Lifecycle05 source81f04f6e:
same CameraManager/Camera1/80/80 restart/reacquire passes161 app frames and173
signed threaded IPA results; app SOF counts5/84/84,IRQ counts6/85/85 reset from0
each start; final STOP has no later SOF/phase events. Stream IDs6/7/10,880 owner
checks,185 typed defaults; longer runs30.00582/30.00572fps. No module reload.

All241 app frames across these four streams matched hardware statistics/IPA.
All241 steady observations had SOF-count minus VIDEO source0. Receiver SOF IRQ
observation to VIDEO IRQ20.204-20.355ms in pipeline05; IRQ to completion2.877-
3.248ms. These observations are not first-row exposure identity or sensor-control
latency. SensorTimestamp remains absent; automatic AE/AWB remains disabled.

All STOPs clean,error0,all sensors standby after each stop,final graph neutral,
critical kernel faults0,Golden hashes unchanged. Both05 IDs consumed and retired;
all22 candidate IDs retired,26 completed sensor streams,44 candidate/Golden boots;
prior5 prestream/2 poststart failures unchanged. Latest Golden boot
33010f45-c44b-4faa-923a-953e90113de3. No candidate boot/unit/writer/FW remains.
Private original tuning, logs and optical pixels stay on SP11.
Evidence: docs/NATIVE-RGB-FRONT-FRAME-SYNC-05-20261007.json and
 docs/NATIVE-RGB-FRONT-FRAME-SYNC-LIFECYCLE-05-20261007.json.

NEXT: bounded grouped sensor exposure/analogue/digital/frame-length response and
measured per-field delays with CCI completion + receiver/frame/statistics times,
stable-light screening and repeated up/down steps. Use standard DelayedControls
only with those measurements. IMX681 already has a four-control atomic V4L2
cluster with VBLANK master; do not copy another sensor's priorityWrite=true,
which splits VBLANK into a separate ioctl. See current timing plan.
Metering normalization, AE/AWB/dynamic tables,rear ISP/focus,public ABI/clock
policy,independent tuning and soak/switch/fault/Windows optical acceptance remain.
No matched Windows reference; fixed low Y is no proven brightness defect.
Match physical camera/scene/position/lighting/time, including weather changes.
Earlier NEXT statements are history. No bespoke daemon/CPU image ISP/AI/OEM runtime.

## 2026-10-07 native receiver frame-start hardware PASS; lifecycle05 next

Fresh pipeline05 sourceb08bc32f/audit29/libcamera build07 passed80 standard cam
2560x1440 NV12 frames at30.00469fps,80 app/statistics pairs and84 actual isolated
IPA metering results. Standard CSID1 V4L2 FRAME_SYNC delivered84 consecutive
libcamera frameStart callbacks; owning ISR observed85 source-qualified bit4
SOFs at30.00535fps. All80 steady VIDEO sources had SOF-count minus source0;
latest receiver SOF observation preceded VIDEO IRQ by20.204-20.355ms and
completion followed VIDEO IRQ by2.877-3.248ms. This is interrupt phase observation,
not first-row exposure identity, sensor-control latency or SensorTimestamp proof.

425 owner checks/85 retirements,88 typed defaults,clean STOP,error0,neutral graph,
all sensors standby,critical faults0,Golden hashes unchanged. Candidate boot
 ae0cb572-f768-49c8-8cb0-0b86ba7ebba6 returned Golden54041d3b-e446-4720-844a-8c1e48300c37.
Pipeline05 consumed and retired;21 consumed identities/42 candidate-Golden boots,
23 completed sensor streams; prior5 prestream/2 poststart failures unchanged.
Evidence: docs/NATIVE-RGB-FRONT-FRAME-SYNC-05-20261007.json.

Fresh lifecycle05 is the next one-use qualification: same CameraManager/Camera
1/80/80 restart/reacquire with audit29/build07, signed threaded actual IPA, SOF
sequence reset and final-stop silence in addition to existing queue/owner/standby
checks. Its public API binary builds Werror; no stream yet. Never reuse spent IDs.
Then measure grouped sensor exposure/analogue/digital/frame-length delays before
standard DelayedControls and automatic feedback. AE/AWB, metering normalization,
rear ISP/focus, public ABI/clock policy, independent tuning and optical acceptance
remain. No matched Windows reference; fixed low Y is no proven brightness defect.
Match camera/scene/position/lighting/capture time, including rainy/cloudy changes.
Earlier NEXT statements are history. No bespoke daemon/CPU image ISP/AI/OEM runtime.

## 2026-10-07 current native front IPA: both standard paths hardware-proven

Actual libcamera build06/audit27 now passes isolated standard cam80 capture and
signed threaded same-CameraManager/Camera1,80,80 restart/reacquire. Pipeline04
source90837d1d delivered80 NV12 frames30.00485fps with84 metering results,
425 owner checks and88 typed requests. Lifecycle04 source964de842 delivered161
app frames,173 metering results across fresh streams6,7,10,880 owner checks and
185 typed defaults; longer captures30.00543/29.98823fps. No module reload.
All stops clean, sensors suspended after each stop, final graph neutral,
Golden hashes unchanged, critical faults0. Returned Golden boot
b2e5554f-6b33-4aca-8e7f-ffac7b241ecf. Pipeline04/lifecycle04 consumed and retired;
all20 candidate identities retired,22 completed sensor streams,40 candidate/
Golden boots. Pixels/original tuning remain private SP11.

The actual IPA maps eight read-only shared statistics buffers, meters exact
stream/sequence/completion-time identities and produces qualified mask0 typed
defaults. Metadata buffers wait for matching IPA results before requeue; app and
startup/spare completion also requires metering. Stop barriers precede unmapping.
Build06 Werror9 tests OK/2 VIMC skips. No bespoke daemon or CPU image ISP.

NEXT concrete blocker: native frame-start events and measured sensor-control
delays before automatic exposure/gain. Source audit shows the current VFE17x SOF
handler is a no-op and VFE core ops expose no event subscription. CSID680 Epoch0
and BUF_DONE counters are not exposure/SOF proof. Qualify an actual receiver SOF
source, standard V4L2_EVENT_FRAME_SYNC sequence/association and grouped sensor
change effects; use libcamera DelayedControls only with measured delays. See
docs/NATIVE-RGB-FRONT-CONTROL-TIMING-PLAN-20261007.md. Meter normalization, AWB and
dynamic ISP tables still require qualification. SensorTimestamp remains absent.

Fixed settings/low Y do not establish a brightness defect; matched Windows same
physical camera/scene/position/lighting and time-proximate captures required.
Rear processed ISP/focus, public ABI/clock policy, independent tuning and long-run/
switch/fault/Windows optical acceptance block product completion. Actual IPA is
no longer absent. Earlier NEXT statements are history. Evidence:
docs/NATIVE-RGB-FRONT-IPA-04-20261007.json and
docs/NATIVE-RGB-FRONT-IPA-LIFECYCLE-04-20261007.json.

## 2026-10-07 actual native front IPA physically verified

Fresh pipeline04 used90837d1d/audit27/libcamera build06. Standard cam delivered
80 hardware2560x1440 NV12 frames at30.00485fps through a real isolated libcamera
IPA. Eight shared statistics buffers produced84 ordered metering results;
all80 app frames matched stream/sequence/completion time. The IPA produced88
typed mask0 defaults. Kernel passed425 owner checks/85 retirements; cam exit0,
STOP clean, graph neutral, all sensors standby, critical faults0, Golden hashes
unchanged. Returned boot2aa4c3a8-f6c6-4d6a-b805-b8c0586b7f48. Pipeline04 consumed
and retired; all older candidate identities remain retired.

Actual IPA is now hardware-proven. Automatic AE/AWB feedback, sensor control
delays, first-row exposure timestamp and optical metering normalization remain
unqualified. Fixed settings and low Y do not establish a brightness defect;
matched Windows camera/scene/lighting/capture-time comparison remains required.
Next lifetime gate uses fresh lifecycle04 with the same actual IPA in its signed
standard threaded path:1/80/80 restart/reacquire, stop barriers/shared maps and
fresh stream identities. Then qualify sensor timing and control feedback.
Rear ISP/focus, dynamic tables, public ABI/clock policy, independent tuning and
long-run/switch/fault/Windows optical acceptance still block product completion.
See docs/NATIVE-RGB-FRONT-IPA-04-20261007.json; earlier NEXT statements are history.

# Native SP11 camera delivery state — 2026-10-07

## 2026-10-07 user requirement: compare brightness under real conditions

Low measured Y is an observation, not an established Linux brightness defect.
Compare with Windows on the same physical camera, scene, position and lighting,
as close in time as dual boot permits. Record capture timestamps, time separation,
resolution/frame rate, automatic/manual settings, available exposure/gain and
output colour/range interpretation. Changes in daylight, weather or lighting
between captures confound brightness attribution; use stable lighting or repeat
the pair. The user reports rainy/cloudy conditions today; do not assume daylight
brightness or compare a night capture with an unrelated daytime Windows image.
Current captures have no matched Windows brightness reference, so their optical
cause remains undetermined. This requirement applies to front and rear acceptance.


The product is native Linux front/rear camera support with hardware ISP processing
and standard libcamera pipeline/IPA controls. It is not complete. The user's
acceptance of libcamera supersedes the original literal kernel-only constraint.
No bespoke camera daemon, loopback, CPU pixel ISP, AI/effects or Windows binary
execution belongs in the release path.

## Machines, sources and authority

| Resource | Role | Current use |
|---|---|---|
| SP11 Linux ARM64, via PiMaster | Build and hardware target | Golden FullIO v19c default; kernel7.1.5-sp11-render-parity-v4+ |
| SP11 Windows | Same physical sensors/ISP reference | Demand-driven register/algorithm/quality oracle; not release runtime |
| SP7 | Recovery and Windows KD | Recovery/debug only |
| SP11X1ECamera-driver | Current maintained source | work/native-rgb-driver-20261007 |
| SP11X1ECamera-clean/native/legacy | Prior experiments and retained evidence | Preserve; import only reviewed/hash-pinned needed sources |
| e003i-front-production-src + build-runtime-v4-headers-20260826 | Compatible kernel build toolchain | External modules, W=1/-Werror, fresh outputs |
| Qualcomm camera-driver82ac3a6 | Published hardware programming authority | BUSv3, VFE680, CDM validation; no invented reset/register mapping |
| libcamera pinned ff740913 | Standard Linux control/pipeline framework | Front pipeline physically passes80 cam frames; IPA remains |

Protected Golden assets/default are never overwritten. Original vendor tuning,
raw traces and optical pixels remain private on SP11. No system suspend tests.
Eighteen one-use candidate identities are consumed and retired; none may be rearmed.

## Verified implementation

| Component | Physical or build evidence | Limit |
|---|---|---|
| Front IMX681 timing controls | Read-only720MHz pixel rate, HBLANK2912,1.2GHz link-frequency menu; two-FLL measurements | Full native array/selection geometry still needs authority |
| Correct SP11 OV13858 source | Board supplies/reset/runtime PM;120 rear RAW frames and verified stop | Rear processed ISP output not proved |
| Native front linear NV12 queue | 80 sequential2560x1440 frames at29.989fps; four reused buffers and reversed queue order;405 ownership checks | Fixed manual IQ, restart/reacquire passed; no long soak/live3A |
| FULL storage/8-bit programming | Published packer3, linear MODE guard, UV half height, complete readbacks, local CDM helper audit | Linear restart/reacquire passed; compressed transition unqualified |
| Stop/return | Explicit STREAMOFF during queue operation; all sensors suspended, graph neutral, Golden unchanged, zero critical faults | Finite drain/restart/reacquire passed; fault/long soak remain |
| Frame-associated statistics |80 video/metadata pairs with matching identity/timestamps and valid AEC luma;405 ownership checks | Experimental QXS1 format; IPA remains |
| libcamera control/statistics helpers | ARM64 Werror build;8 passes,2 VIMC-dependent skips | Front pipeline passes80 app frames; actual IPA absent |
| Typed front ISP scalars |80 pairs,84 accepted requests,5 negative cases; measured2x gain/reset response;1979 sanitizer checks | Data-only firmware qualified; dynamic tables/live3A remain |
| Kernel-owned startup |80 pairs via data-only firmware; raw control absent; missing/corrupt profile rejected;405 owner checks | Fixed board/mode digest; independent tuning distribution and final ABI remain |
| Standard libcamera front application |80 NV12 frames at29.9919fps,80 statistics pairs,425 owner matches,88 typed requests; clean stop/release | Fixed manual; dark output, no IPA/3A or rear processed capture |
| Front libcamera lifecycle |Same CameraManager/Camera captures1,80,80 frames with restart/reacquire;880 owner checks and185 typed requests; sensors standby after each stop | No long soak/switch/fault or automatic controls |
| Rear composition |52 fragments compile against real types | Nonadaptive startup inputs and runtime composition incomplete |

NV12-01 stopped before ISP programming: truthful sensor array timing plus the
generic PIX clock margin exceeded X1E's admitted727MHz maximum. NV12-02 used
that existing maximum only for the exact diagnostic mode; requested727000000Hz,
rounded727000000Hz, actual727000048Hz. No new OPP or fabricated pixels/cycle
ratio was introduced. Production load voting remains a separate qualification.

The continuous NV12 frames have Y means3.68–3.94 and maximum11, with UV near128.
This proves hardware-written NV12 buffers, not colour, exposure, focus or Windows
quality. A dark physical scene, fixed exposure and tuning/processing behaviour
must be distinguished before drawing an optical conclusion.

Evidence: NATIVE-RGB-TIMING-03-20261007.json,
NATIVE-RGB-NV12-01-20261007.json, NATIVE-RGB-NV12-02-20261007.json,
NATIVE-RGB-NV12-BUILD-20261007.json and NATIVE-RGB-LIBCAMERA-BUILD-20261007.json.

## Why progress stalled

1. Historical NEXT pointers directed work into tiny Windows metadata/control-flow
   steps, even when those steps did not unblock a native Linux camera requirement.
2. Mock-only fragments and compile success were mixed with hardware readiness.
   Actual integration exposed real-type mismatches and a stale rear ACPI source.
3. The front runtime grew named frame/capsule/result fields through frame27.
   That is a bounded experiment, not a reusable continuous queue.
4. Native timing metadata, ordinary FULL storage, stream ownership and host3A
   were separate unresolved dependencies. Extending captured capsules could not
   resolve those architecture boundaries.
5. Readiness/handoff records preserved obsolete software-service and kernel-only
   policies. The authoritative prefixes and structured state now identify the
   approved native/libcamera workstream and the exact bounded hardware proof.

## Remaining delivery gates, in dependency order

**1. Continuous front queue and request contract.**
The isolated native path now runs one serialized two-slot queue beyond the old
27-frame bound. Queue01 passed80 delivered frames, including changed buffer order
and explicit STREAMOFF;81 retirements had405 consumed-owner checks. Its two command
slots preserve synchronous CDM BL_DONE and full DMA-owner retirement before reuse.
This establishes short continuous capture, not a long soak, restart or optical gate.

The qualified front profile mode removes the raw-command control and loads
validated data-only tuning through the kernel firmware loader. Original tuning
remains private; independent distribution is still unresolved.
Frame-associated statistics now pass80 pairs on the V4L2 metadata queue.
Typed validated scalar parameters now pass84 real requests and measured hardware
gain/reset response. Complete dynamic semantic tables and request association for libcamera.
Expose scalar/ROI/table values with bounded sizes and supported ranges; the kernel
owns register addresses, CDM framing and DMA binding. Do not expose arbitrary
MMIO, vendor binary execution or unvalidated command streams as product APIs.
DMI bank selection and per-request IQ cadence need a source-qualified rule;
blindly replaying request4 forever is not a substitute.

Already passed: native NV12 queue reuse beyond the old27-frame bound, ordered
delivery, explicit STREAMOFF, stop-before-free, neutral graph and standby.
Finite capture tail now passes using retired internal spare buffers. Remaining:
fault/long-soak/switch qualification, full typed tables and automatic request controls.
Same-object restart and release/reacquire now pass161 frames in one boot; stream
profile/FIFO lifetime and the old diagnostic one-start guard were corrected.
Use fresh identities; do not extend one named frame at a time.

**2. libcamera pipeline and IPA runtime.**
Front graph/request/statistics integration now passes the standard cam app with
fixed manual settings. pipeline01 tail starvation was diagnosed and corrected;
pipeline02 passed and both identities retired. Actual IPA/3A remains.
Discover this exact media graph, configure front/rear modes and streams, associate
sensor controls/ISP parameters/statistics with libcamera requests, and connect
the already-tested helpers. Implement 3A inside standard libcamera IPA code.
Verify exposure/gain control changes and statistic latency on hardware before
closed-loop tuning. Choose an ordinary pipeline-supported clock policy from
qualified active-pixel throughput and actual resource votes.

Acceptance: standard libcamera app gets processed hardware NV12 without a
bespoke daemon, loopback or software pixel ISP; controls respond correctly,
AE/AWB converge and failures return owned resources safely.

**3. Rear native ISP.**
Supply only the missing reviewed nonadaptive startup semantics, integrate the
existing bounded source fragments with actual ownership/completion logic, and
prove rear processed output/stop before enabling normal application selection.
Use Windows or KD only to resolve a specific absent hardware/algorithm rule.

Acceptance: rear native frames, safe switching, no stale cross-sensor requests,
and repeat open/close. RAW success alone cannot open this gate.

**4. Optical and product acceptance.**
Compare front and rear against Windows using controlled lighting, scene,
distance, resolution, frame rate and exposure. Measure colour/white balance,
detail/noise, clipping, frame cadence, exposure transitions and rear focus.
Resolve the very dark diagnostic output first. Validate repeat starts, long
capture, application switching, idle power and sensor runtime PM.
AI/effects remain excluded unless a concrete hardware contract requires an
inert presence; no such requirement has been established.

## Execution discipline

Every change must identify the product blocker it removes, its exact source
authority and a falsifiable build/hardware/optical result. A failed one-use boot
is recorded and retired; only a specific reviewed change earns a fresh identity.
A compile-only result never becomes a runtime PASS. A four-frame result never
becomes continuous or quality PASS. Keep one authoritative checkout and current
handoff; historical experiment chains are evidence, not an automatic work queue.

Timestamp audit: current pairing proves matching buffer-completion times only.
Kernel buffer return uses ktime_get_ns; mapping it to SensorTimestamp does not
meet the first-row-exposure/CLOCK_BOOTTIME semantics. Build04 removes that metadata field; physical pipeline03 verifies its absence
while delivering80 hardware frames. Sensor timing remains unqualified. Do not call this optical timing
proof or feed that mislabeled timestamp into automatic-control delay handling.
