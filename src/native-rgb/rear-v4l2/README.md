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
