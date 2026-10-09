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

# Rear libcamera public request qualification

Isolated standard libcamera pipeline for two rear 4K NV12 requests using exported/imported DMA-BUF application buffers. Kernel hardware ISP produces all pixels. The handler does not map pixels, implement a software ISP, or provide a camera daemon.

The candidate remains finite and uses the private compiler-bound startup profile. It proves application request transport and lifetime, not continuous capture, independent rear IPA, adaptive IQ, exposure timestamps or Windows quality parity. Maintained front pipeline/IPA sources are unchanged.

Continuous work must replace the fixed 16-entry completion history with a consumed event queue and establish live buffer retirement before releasing any mapping while hardware runs. Existing rear retirement only authorizes full-stop release; never substitute false stop proofs to recycle a live mapping.
