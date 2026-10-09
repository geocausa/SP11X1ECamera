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

## 2026-10-08 rear27 live public FULL unmap on hardware, clean release PASS

Fresh27/build35 retires the old public FULL attachment before physical stop:
ret0/released1/old-valid1, replacement FULL pinned1, old eight auxiliary buffers
pinned8, all stop flags0, no VB2 completion/requeue. Actual live observation
matches both ten-WM ledgers, replacement command receipts and all readback masks
1023; owner1, events14 drained, stable Epoch3. This is real mapping retirement,
not merely a read-only observation. Scope is first FULL only, not all outputs.
Two real libcamera DMA-BUF Requests complete at 3840x2160 linear NV12/stride3840/
12441600 bytes without CPU pixel access/copy. All four subsequent physical stops
and remaining DMA/owner/arena release PASS; dma_pinned0. All sensors bound/
suspended; IFE/CSID/PHY clocks idle. Ten VFE/eight IPP phases errors0.
No hazards/watchdog; service success0; verified automatic Golden return
6de92f65-627e-40f5-b71e-1272cfbaf638. 27 consumed/retired; units disabled; no
camera modules/nodes/jobs/armed experiments. Native52/60IDs120boots failed20;
combined67IDs134boots. Whole-generation live retirement, persistent rear
Requests, rear IPA/SensorTimestamp and optical parity remain unproven.
NEXT retire/recycle old auxiliary outputs and command sets, integrate persistent
rear scheduler/Requests, then typed semantic IPA/statistics/controls and matched
Windows quality. Current rear remains two Requests. Front calibration deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-27-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear27 live old FULL retirement source qualified

Fresh build35 compiles three ARM64 W1/Werror modules. All 16 hosted checks PASS.
After exact old/new ten-WM completion, synchronous replacement command receipts,
current exclusive owner and matching live readbacks, the finite runner can unmap
only the old public FULL attachment. No false stop facts. Its ledger remains,
its eight auxiliary allocations stay pinned, and the replacement FULL remains
mapped until all four physical stop barriers. Retired marker binds owner/request;
duplicate retirement and premature auxiliary release are rejected.
GCC/Clang actual helper tests20150 assertions/583 negatives each; actual reclaimer
590 assertions/165 negatives covers retired and ordinary cleanup. Actual lifecycle
fault models and 44 graph/log parser negatives PASS. Source only: not yet installed,
armed or hardware attempted. NEXT fresh single-use27 live FULL hardware proof
with automatic Golden return, then whole-generation retirement/persistent requests.
Rear26 hardware replacement observation remains PASS. Whole-generation live
retirement, rear continuous capture, rear IPA/SensorTimestamp/optical parity remain
unproven. Front calibration deferred. Golden28b279ae-c16c-42ae-a7ae-d74edb91bdab.
Counts unchanged Native51/59IDs118boots failed20; combined66IDs132boots.
Evidence docs/NATIVE-RGB-REAR-GENERATION-27-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear26 live replacement observed on hardware, clean release PASS

Fresh26/build34 completes two real libcamera DMA-BUF Requests at 3840x2160
linear NV12/stride3840/12441600 bytes, no CPU pixel access/copy. Actual SPSC
queue publishes/consumes12 events. Before physical stop, read-only observer
PASS: old/new ten-WM complete, four command BL_DONE receipts, all three
replacement readback masks1023, owner1, stable drained event cursor12 and
Epoch3. No live DMA release was attempted or authorized by observation.
Kernel ret0 packets1111/epochs2; all four physical stops, mappings/owner/arena
released; dma_pinned0. All sensors bound/suspended; IFE/CSID/PHY clocks idle.
Ten VFE/eight IPP scalar phases errors0; no kernel hazards/watchdog; service
success0. Verified automatic Golden28b279ae-c16c-42ae-a7ae-d74edb91bdab return.
26 consumed/retired; units disabled; no nodes/modules/jobs/armed experiments.
Native51 completed/59IDs118boots failed20; combined66IDs132boots.
NEXT explicit live generation retirement and persistent rear request queue,
then typed semantic IPA/statistics/controls and matched Windows quality.
Rear remains bounded to two Requests; live mapping retirement, continuous
rear, rear IPA/SensorTimestamp and optical parity still unproven. Event queue
hardware proof is bounded12 events, not wrap/long soak. Front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-26-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear26 read-only live replacement source qualified

Fresh build34 compiles three ARM64 W1/Werror modules. All 15 hosted checks
PASS, including actual SPSC event queue and read-only replacement observer.
Observer requires both ten-WM ledgers complete, four command BL_DONE receipts,
distinct DMA spans, matching enabled/programmed/consumed replacement addresses,
current owner and stable drained event snapshot. It runs before physical stop;
no MMIO writes, IRQ ACK, DMA puts/frees, VB2 completions or live reuse authority.
GCC/Clang observer16479 assertions/473 invalid or racing cases each; actual
clean lifecycle3745/62steps60faults, public3958/64steps62faults. Parser rejects
18 malformed/incomplete observations; retained media graph admission still PASS.
Failed frozen33 preserved; Linux current macro collision fixed in fresh34.
Source ready, not yet installed/armed/attempted. NEXT install/fresh single-use26
hardware proof with mandatory Golden return, then live retirement/persistent
requests and semantic IPA. Rear libcamera remains bounded to two requests.
Continuous rear, live DMA retirement and optical parity still unproven.
Maintenance reboot Golden2c19627c-2c51-45be-bd54-2d2d824af838 verified; camera
counts unchanged Native50/58IDs116boots failed20; combined65IDs130boots.
Front calibration deferred. Evidence docs/NATIVE-RGB-REAR-GENERATION-26-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear continuous event-queue prerequisite source-qualified

Rear25 real libcamera DMA-BUF 4K NV12 two requests + clean release remains PASS.
Fixed 16-record history was nearly full (15 events) after just two frames.
Maintained event queue now uses monotonic producer/consumer sequences and
release/acquire publication; IRQ reuses storage only after exact owner/
sequence and every observed WM have been consumed by the runner.
Overflow, counter wrap, stale/malformed records fail closed. No new hardware
ACK/control writes and no live image DMA release authority.
Fresh build32 compiles all three ARM64 W1/Werror modules. All 13 checks PASS:
actual queue GCC/Clang ASAN/UBSAN,76922 assertions each,1024 sequential and4096
concurrent events; actual runner clean model3733/62steps60faults, public
model3946/64steps62faults; remaining mapping/layout/transport/sensor/clock/CSR
checks PASS. Source only; no install, arm, stream or reboot. Counts unchanged.
NEXT live generation replacement/retirement, persistent rear queue/libcamera
request recycling, typed rear semantic IPA/statistics/controls and optical
comparison. Never fake full-stop facts to authorize live mapping reuse.
Latest hardware Golden 0104d011-6c45-4b27-9079-d7ccf60436da,25 retired.
Native50/58IDs116boots failed20; combined65IDs130boots. No armed jobs.
Front calibration deferred; continuous rear and optical parity still unproven.
Evidence docs/NATIVE-RGB-REAR-EVENT-QUEUE-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear25 real libcamera two-request DMA-BUF capture PASS

Fresh rear25/build31 and isolated rear libcamera build02 complete two real
CameraManager/FrameBufferAllocator/application Requests at 3840x2160 NV12.
Exported/imported DMA-BUF buffers, logical Y8294400/UV4147200, stride3840,
exact sequences0/1 and completion timestamps; SensorTimestamp omitted.
Camera stop/release and neutral links PASS. Both ten-WM generations complete:
ret0 packets1111 epochs2 events15; all four stops, DMA lease release,
owner and command arena release1; dma_pinned0. All sensors bound/suspended.
Ten VFE/eight IPP scalar phases error0. No hazards/watchdog; service exit0.
Automatic verified Golden return 0104d011-6c45-4b27-9079-d7ccf60436da.
25 consumed/retired; units disabled; no armed jobs. Own changes committed.
Native50 completed/58 IDs/116 boots/20 failed; combined65 IDs/130 boots.
First real rear libcamera requests and DMA-BUF import hardware qualification.
NEXT continuous rear event queue/live generation retirement and normal typed
semantic IPA/adaptive controls. Current rear handler remains two-frame private
startup qualification. Completion history16/events15 makes longer stream
unsupported. Never fake stop facts to recycle mappings.
Continuous rear, independent rear IPA, exposure timing and optical quality
parity remain unproven. Front calibration deferred; maintained front unchanged.
Evidence docs/NATIVE-RGB-REAR-GENERATION-25-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear25 real libcamera request candidate prepared

Rear24 standard V4L2 MMAP 4K NV12 two-frame clean release remains PASS.
Rear25/build31 adds candidate rear min_queued_buffers=2 for libcamera's empty
STREAMON then ordinary request queueing. Three ARM64 W1/Werror modules and
all 13 hosted checks PASS. Separate standard rear libcamera transport handler,
library build rear-v4l2-20261008-02, six hardware-independent tests PASS,
zero warnings. Real application exports/imports DMA-BUF, two Requests,
logical NV12 planes and stop/release. No CPU pixel maps/read/copy/software ISP.
Prepared, not hardware attempted/armed. NEXT fresh25 libcamera two requests
and DMA-BUF stop/release proof, then continuous kernel queue and semantic IPA.
Handler is explicitly finite qualification, not final automatic rear product.
Continuous audit: rear latch history is 16 events; ledger/mapping retirement
currently requires full stop. Establish live retirement before buffer reuse;
never fake stop facts. Completion times are not SensorTimestamp.
Native counts unchanged49/57IDs114boots failed20; combined64IDs128boots.
Golden fc78315d-81e3-4c67-acd6-f8995f8e60e3;24 retired. Front deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-25-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear24 standard V4L2 4K NV12 two-frame capture PASS

Fresh rear24/build30 passes standard S_FMT/REQBUFS/QBUF/STREAMON/DQBUF x2,
STREAMOFF and REQBUFS(0). 3840x2160 NV12, stride3840, bytesused12441600
for both completed public MMAP buffers; no CPU pixel copy/software ISP.
Independent retained DMA-BUF FULL mappings release only after verified
CSID/BUS/RTCDM/source stops. Both ten-WM generations, commands and pipeline
owner retire: ret0 packets1111 epochs2 events9, all completion/release1,
dma_pinned0. Borrowed FULL size12441600; static0=1/static1=0/programmedboth1.
All sensors bound/suspended. All observed VFE/IPP errors zero; no hazards,
watchdogfalse, service exit0. Automatic verified Golden return
fc78315d-81e3-4c67-acd6-f8995f8e60e3. 24 consumed/retired; units disabled.
Native49 completed/57 IDs/114 boots/20 failed; combined64 IDs/128 boots.
First public V4L2 MMAP delivery; fourth linear and second clean-release boot.
NEXT continuous rear buffer retirement/replacement and ordinary libcamera/
IPA typed semantic request pipeline. Current worker is exactly two frames,
uses private compiled qualification profile and completion-time timestamps.
Rear continuous/libcamera, DMABUF import hardware, exposure timing and optical
quality parity unproven. Front calibration deferred. No armed jobs.
Evidence docs/NATIVE-RGB-REAR-GENERATION-24-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear24 public V4L2 mapping/worker candidate prepared

Rear23 hardware clean 4K NV12 release remains PASS. Fresh rear24/build30
builds three ARM64 W1/Werror modules. All 13 hosted checks PASS, including
actual independent DMA-BUF leases, all-or-none reclaim, runner fault models,
linear layout, sensor/transport/clocks and real-graph/probe admission.
Standard V4L2 MMAP worker now source-connected for exactly two 3840x2160
NV12 frames; retained independent maps protect pages/IOVAs through VB2
cancellation and uncertain stop; faulted pair retained on VFE until reboot.
Candidate source-qualified, not yet hardware attempted or armed.
NEXT fresh rear24 STREAMON/DQBUF x2/STREAMOFF/REQBUFS0 hardware proof,
then continuous rear queue and normal libcamera/IPA typed semantic controls.
Private compiled profile remains qualification only. Completion timestamps
are not exposure timestamps. DMABUF import hardware, rear libcamera,
continuous delivery and optical quality remain unproven; front deferred.
Counts unchanged48/56IDs112boots failed20; combined63IDs126boots.
Golden f6afd4f8-cdf2-4d91-a57f-f587315001ed. Rear23 retired.
Evidence docs/NATIVE-RGB-REAR-GENERATION-24-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear public-buffer DMA admission compiled and tested

Rear23 physical clean NV12 release remains PASS. Actual rear VB2 mapping
admission is now source-qualified: exact 4K NV12 ACTIVE single-plane buffer,
every mapped SG entry contiguous and inside 32-bit DMA aperture, advertised
plane covered; ignores orig_nents and cached first addr. No CPU pixel/MMIO
access or allocation/free/completion authority. GCC/Clang ASAN/UBSAN/Werror:
658 assertions, 155 negative cases, 64 valid partitions each.
Fresh native-rgb-rear-v4l2-20261008-01 builds three ARM64 W1/Werror modules,
zero diagnostics. Source only: no install, public callback, stream or reboot.
NEXT borrowed FULL ownership/mapping lifetime through stop/failure, ordinary
V4L2 worker/queue and rear libcamera typed semantic IQ, continuous metadata.
Application delivery and optical quality still unproven. Front calibration
deferred. Counts unchanged48/56IDs112boots failed20; combined63IDs126boots.
Golden f6afd4f8-cdf2-4d91-a57f-f587315001ed;23 retired; no armed jobs.
Evidence docs/NATIVE-RGB-REAR-V4L2-DMA-ADMISSION-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear23 clean native NV12 completion and release PASS

Fresh rear23/build28 completes both ten-WM generations at 3840x2160 NV12,
stride3840/image12441600 bytes. All CSID/BUS/RTCDM/source stop barriers pass.
ret0, packets1111, epochs2, events13, both complete1; dma_pinned0,
DMA_reclaimed1, owner_released1, arena_released1. Ledgers and pipeline PM release.
Physical reclaim log confirms static0=1/static1=0, both programmed1, matching
the maintained repair and faithful hosted fixture. All sensors bound/suspended;
IFE/CSID clock enable and prepare counts zero after release. No kernel hazards,
watchdogfalse; automatic verified Golden return f6afd4f8-cdf2-4d91-a57f-f587315001ed.
23 consumed/retired; units disabled; no camera modules/nodes or armed jobs.
Native48 completed/56 IDs/112 boots/20 failed; Windows7/7/14; combined63/126.
Three fresh linear NV12 hardware completions; first qualified clean release.
NEXT public V4L2 NV12 buffers and normal libcamera transport/lifecycle.
Rear continuous/application delivery and optical quality remain unproven;
front calibration deferred. No pixels, tuning arrays or image hashes exported.
Evidence docs/NATIVE-RGB-REAR-GENERATION-23-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear23 maintained reclaim repair prepared

Fresh build28 compiles three ARM64 modules W1/Werror without diagnostics.
Maintained native-rear-reclaim.inc requires slot0 disabled/static preparation,
both programmed exact-complete ledgers, all four stop barriers and the matching
owner epoch. Slot1 is Epoch-retargeted; no fabricated prepared_disabled flag.
All allocation/aux WM identities are checked before any free. Failure paths pin.
The earlier positive fixture missed slot1=false; faithful actual reclaimer test
now passes 356 assertions / 93 negative cases with GCC/Clang ASAN/UBSAN/Werror.
All ten hosted checks pass. Candidate23 is unarmed; NEXT one fresh boot verifies
DMA/ledgers/owner/PM/commands release and all sensors suspended, then public V4L2.
Native47 completed /55 IDs /110 boots /20 failed; Windows7/7/14; combined62/124.
Golden13dcbbd9-5dc6-4c32-9e22-ba18175073b8. Front calibration remains deferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-23-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear22 reproduced linear output; software reclaim guard mismatch

Secondfresh4K NV12 generationpair completes; allstopflags1, packets1111/epochs2
events6. ReclaimreturnsEPROTO; DMA/owner/PM/commands conservativelyheldtillGolden.
Sourceguardwronglyrequires slot1 prepared_disabled, but onlyslot0 is disabled-
preloaded; slot1 is Epoch-retargeted/enabled. No pretendflag or sameboot retry.
Firsthostfixturemissedreal slot1=false. NEXTcorrectmaintainedreclaimer torequire
pair-levelstatic/slot0 proof andboth programmed exactcomplete ledgers;
testactualslot1false positive, then fresh23/sourcebuild28.
Native47completed55IDs110boots failed20; Windows7/7/14; combined62/124.
Golden13dcbbd9-5dc6-4c32-9e22-ba18175073b8 hashes/EFI/NTFSverified,hazards0/watchdogfalse.
22retired unitsdisabled nojobsarmed. PublicV4L2/qualitystillunproven.
Evidence docs/NATIVE-RGB-REAR-GENERATION-22-20261008.json. Earlierentrieshistorical.

## 2026-10-08 rear22 native NV12 clean release candidate prepared

Freshbuild27 W1/Werror3modules0diagnostics,10hostchecks PASS.
Onlysuccessful diagnostic poststop hold bypassed; all hardwareconfiguration
and stop/reclaim helpers unchanged21. Actualreclaimer349assertions90negatives
allallocationsvalidatedbeforeanyfree; commandrelease requiresRTCDMstop.
Actualrunner3539assertions/60steps58faultmodels; successfulallstoponce and
reclaimmockonce. Linear6508/geometry578/VFE466/transport/NoC/sensor/graph/CSR PASS.
NEXTfresh22 boot; requirecomplete2generations/allstop then output/ledger/owner/
PM/commandrelease and sensorssuspended. Failurepathsretain mandatoryGolden.
No counts changed native47/54IDs108boots Windows7/7/14 combined61/122.
PublicV4L2/libcamera/opticalquality stillunproven; frontcalibrationdeferred.
Evidence docs/NATIVE-RGB-REAR-GENERATION-22-PREP-20261008.json.
Earlierentrieshistorical.

## 2026-10-08 rear21 cold native 4K NV12 hardware completion passed

FULL3840x2160 linearNV12 stride3840/image12441600,22eight-bitround/clamp
and BUSgeometry readbacks admitted beforeenable. Both10-WMoutputgenerations
complete; packets1111/epochs2/events12 and allsource/CSID/BUS/RTCDMstopflags1.
NoC240M/IFE594M/CSID300M;11poweredCSRphases CCIF/overflow/imagesize0,
UBWCcommon remainscold6; noFULLcompression/meta/addresswrites.
Pixelsnotread/saved; ordinaryV4L2/libcamera delivery/continuous/quality unproven.
Native47streams54IDs108boots failed19; Windows7/7/14; combined61IDs122boots.
Golden6484b59a-14cb-459a-9b6a-01d694bfd3de hashes/EFI/NTFSverified,hazards0/watchdogfalse.
21retired unitsdisabled, nojobsarmed. Nextfresh22/sourcebuild27:
qualify clean post-stop DMA/ledger/command/owner/PM release beforepublicbuffers.
Evidence docs/NATIVE-RGB-REAR-GENERATION-21-20261008.json.
Earlierentrieshistorical.

## 2026-10-08 rear21 cold native linear NV12 candidate prepared

Freshsourcebuild26 W1/Werror all3 modules0diagnostics. Exactmode1/route/tuning,
commandorder/NoC240M/auxiliaries retained. FULL3840x2160 linearNV12 stride3840,
Y0 UV8294400 image12441600 allocation12443648; FULL8bit/DS10bit.
Coldonly; noFULLcompression/meta/addresswrites. Actualstaged GCC+Clang
layout6508assertions46readbackfaults12coldneg6DMAneg; geometry578,
compressedregression570; VFE466/prefix6writes; pinning3302/56steps55faults.
Transport/sensormodes/NoC/CSR/119edgegraph PASS. Default rear runtime denied.
NEXTinstallverifyfresh21 and physicallinear completion/stop; pixelsnotread,
publicV4L2/libcamera delivery and opticalquality stillunproven.
Counts unchanged native46streams53IDs106boots; Windows7/7/14; combined60/120.
Evidence docs/NATIVE-RGB-REAR-GENERATION-21-PREP-20261008.json.
Earlierentrieshistorical.

## 2026-10-08 rear20 maintained NoC correction confirmed on second fresh boot

Both19and20 complete2outputgenerations each, packets1111/epochs2 allstopflags1.
MaintainedrearNoC240M viaCCF physicallyqualified; TOPIPP/CCIF/imagesize0 allphases.
20 events14; do not treat varyingeventcounts as identicalframes or optical proof.
Sensorstartupfix8freshboots; hardwarecompletion2freshboots. Native46streams53IDs
106boots failed19; Windows7IDs14boots; combined60IDs120boots.
Golden 2840c662-c15e-45c8-89af-80a3024bb7f4 3hash/EFI/NTFSverified, hazards0/watchdogfalse.
20retired, unitsdisabled, nofreshcandidate/jobsarmed. DMA/PM/ownerheldthroughreboot.
NEXT completedrearbuffer delivery via standardV4L2/libcamera, native linearNV12
and continuouscapture, then matchedWindowsopticalquality; frontcalibrationdeferred.
Rearpublicruntime/continuousdelivery/opticalquality are NOT complete.
Nextfreshcandidate21/sourcebuild26. Evidence docs/NATIVE-RGB-REAR-GENERATION-20-20261008.json. Earlierentrieshistorical.

## 2026-10-08 rear20 maintained NoC correction fresh repetition ready

NoC240M floor viaCCF integrated inmaintainednative rearconfigure afterWMdisabled
admission/beforeVFEprefix. Candidateonlyclockhook removedfromactualbuild25.
Sensor/CSI/packet/IQbinding unchanged19. Explicitsourceinventory/includeclosure
updated. W1/Werror0all3; sevenhostedchecksPASS; VFE299assertions includesnoc
clockfailurebeforeprefixwrites; pinning3266/55steps54faults/reclaim0.
NEXTinstallverifyfresh20; requiretwooutputgenerations allstopflags and fault0.
Countsunchanged59combinedIDs118boots. Evidence docs/NATIVE-RGB-REAR-GENERATION-20-PREP-20261008.json. Earlierentrieshistorical.

## 2026-10-08 rear19 first native output completion: NoC clock floor fixes stall

Onlyfunctionalchange CCFNoCfloor19.2->240M. PhysicalRT/NRT=240M, IFE594M/
CSID300M. Packets1111 epochs2 events8, bothoutputgenerationscomplete, all
sensor/CSID/BUS/RTCDM stopflags1; TOPIPP/CCIF/imagesize0 allphases.
No opticalpixelread/quality/continuouslibcamera deliveryclaim. DMA/PM/ownerheld
throughmandatoryGolden. Golden 7baa3a64-03f8-498f-866b-5e94d298a3e6 hashes/EFI/NTFSverified;
nohazard/watchdog,19retired/unitsdisabled. Native45streams52IDs104boots failed19;
Windows7IDs14boots; combined59IDs118boots. NEXTintegrateinmaintainedrear path
and fresh20/build25 repetition. Evidence docs/NATIVE-RGB-REAR-GENERATION-19-20261008.json. Earlierentrieshistorical.

## 2026-10-08 rear19 candidate-only legal NoC clock floor ready

Exactcamcc legalNoCrates240/300/400M, sharedRT/NRTsource; CAMSSresourcerates0.
ObservedNoC19.2M despiteICC2GB/s; causalhypothesisunproven. Candidateonly
CCFfloor240M beforeVFEprefix/sensor, preservehigher; no directCSR/IQ/packetchange.
Freshbuild24 correctedsignednesscaughtbyhostbuild23 beforeinstall. ThreeW1/Werror
0diagnostics; sevenhostedchecksPASS: NoC66assertions12negatives7faults GCC+Clang;
pinning3265assertions55steps54faults/reclaim0. NEXTinstallverifyfresh19.
No countschanged58combinedIDs116boots. Evidence docs/NATIVE-RGB-REAR-GENERATION-19-PREP-20261008.json.
Earlier entries below are historical.

## 2026-10-08 rear18 geometry matches; camera NoC clock rate observed

SpecificCFG0/period/bounds all0 exactlyWindows. No simple moduleworddifference.
FaultTOPmodule21/CCIF00900000 persists;6freshmode1boots, rearcomplete0.
CCFpoweredposttrigger IFE1=594M CSID=300M but cameraNoC RT/NRT=19.2M;
ratecausality unproven, next auditDT/controllerfreqtable/ICCvotes.
Golden c73eb834-7e4c-450c-bc3f-13d270dac110 3hash/EFI/NTFSverified; hazards0/watchdogfalse.
18retired unitsdisabled DMA/PM/ownerheldthroughreboot. Native44streams51IDs102boots
failed19; Windows7streams7IDs14boots; combined58IDs116boots. Nextcandidate19/build23.
Evidence docs/NATIVE-RGB-REAR-GENERATION-18-20261008.json. Earlier entries below are historical.

## 2026-10-08 rear18 sparse period/bounds and actual clocks ready

Freshbuild22 onlyadds3sourceproven scalarCSRreads696c/6970/74 and CCF
clockrate/count snapshots aroundtrigger. No hardwarewrites added; sensor/
CSI/VFE/packets/retarget byte-identical17. All3W1/Werror0diagnostics; six
requiredhostedchecksPASS. GoldenCCF parser checked actualcamera rows.
NEXT install/verify/fresh18 and compare Windowszero; no guessed configuration.
Countsunchanged57combinedIDs114boots. Evidence docs/NATIVE-RGB-REAR-GENERATION-18-PREP-20261008.json.
Earlier entries below are historical.

## 2026-10-08 Windows sparse period/bounds reference completed

Rear4K1667distincttimestamps, phase59scalarrows eachonce. Period696c and
bounds6970/74 all0 atpreCTRL/firstEpoch, controlsalso0, CCIF/TOPfault0.
No patternwords/pixels/front/configwrites. Taskgone/SP7clean/identityretired.
Golden 22f64b3f-d6eb-4e3b-84f6-0a52e031aeac verified3hash/EFI/NTFS. CountsNative50IDs100boots
failed18/streams44; Windows7IDs14boots streams7; combined57IDs114boots.
NEXT Linux18 compare addedscalarfields and actual camera clocks; no blindzero.
Evidence docs/NATIVE-RGB-WINDOWS-REAR-SPARSE-02-20261008.json. Earlier entries below are historical.

## 2026-10-08 exact sparse period/bounds source audit and Windows02 prep

CFG0zero matchesWindows; no simple enablecorrection. Same-SP11 fullPack method
uses scalarword3 periodfields5bits at0/8 fixed15; word4/5 paired14bitbounds.
Derivednames/axesnotofficial; patternwords6964/6968 excluded. Named56VFE+3CSID
sourcevalidated9negatives. FreshWindowsSPARSE02 prepared notarmed/consumed.
NEXT freshWindows period/bounds reference then matchingLinux18; no blindwrite.
Countsunchanged56combinedIDs112boots. Evidence docs/NATIVE-RGB-REAR-SPARSE-GEOMETRY-SOURCE-AUDIT-20261008.json and docs/NATIVE-RGB-WINDOWS-REAR-SPARSE-02-PREP-20261008.json.
Earlier entries below are historical.

## 2026-10-08 rear17 specific module control mismatch disproved

FreshWindows controls6960/6b60=0; Linux17 same0 everypoweredphase while
TOPIPPmodule21/CCIF00900000 persists. Do not blindly clear already-zero controls.
Sensorstartupfix now5freshboots; completedrearframes0, packets1110/epochs1.
Golden 0e0d9458-4cc1-4a14-9005-c293667e0289 hashes/EFI/NTFS verified; hazards0/watchdogfalse.
17retired unitsdisabled, DMA/PM/owner heldthroughreboot. Native44streams50IDs100boots
failed18; Windows6streams6IDs12boots; combined56IDs112boots. Nextcandidate18/build22.
NEXT source-qualified modulegeometry and configurationactivation audit.
Evidence docs/NATIVE-RGB-REAR-GENERATION-17-20261008.json. Earlier entries below are historical.

## 2026-10-08 rear17 exact sparse module control comparison ready

Freshbuild21 adds only CFG0 scalar reads6960/6b60 to proven16. Sensor/CSI/VFE
control/packet/retarget code byte-identical16. Sharednamed53VFE+3CSID validator
now verifies exact module source audit and sameSP11 DLL identity;9negatives PASS.
All3 W1/Werror zero diagnostics; required six hostedcheckreports PASS.
NEXT install/verify/fresh17 boot; compare Windows0/0 controls before correcting.
No countschanged. Evidence docs/NATIVE-RGB-REAR-GENERATION-17-PREP-20261008.json. Earlier entries below are historical.

## 2026-10-08 Windows sparse module reference completed

Installed MFT/driver identities exact. Rear4K reader1679distincttimestamps;
preCTRL/firstEpoch each once, both CFG0 controls6960/6b60=0, TOPIPP64=0,
CCIFc64=0. No pixels/front/configwrites. Taskgone, SP7clean, identityretired.
Golden ba87227a-1f1e-4579-873a-8b2ef8ce3acf verified hashes/EFI/NTFS.
Counts native44streams49IDs98boots failed17; Windows6streams6IDs12boots;
combined55IDs110boots. NEXT freshLinux17 CFG0readback, then evidence-basedchange.
Evidence docs/NATIVE-RGB-WINDOWS-REAR-SPARSE-01-20261008.json. Earlier entries below are historical.

## 2026-10-08 targeted sparse module Windows reference prepared

Fresh E-NATIVE-REAR-SPARSE-WINDOWS-01 prepared, not armed/consumed.
Only added specific scalarCFG0 words6960/6b60, exact same-SP11 DLL source;
53VFE+3CSID named whitelist validated with9negativecases. No fullpatterns,
DMA addresses, pixels, or hardwareconfiguration writes. Manual-only entryguarded
rear4K reader; SP7 one-use autoresuming preCTRL/firstEpoch breakpoints.
NEXT verify installedMFT and driver then fresh Windows episode/Goldenreturn.
No counts changed; native49IDs98boots failed17, Windows5IDs10boots.
Evidence docs/NATIVE-RGB-WINDOWS-REAR-SPARSE-01-PREP-20261008.json. Earlier entries below are historical.

## 2026-10-07 current full rear source-input preflight and internal startup handoff

Standard libipa now provides caller-policy AF default rectangle geometry and
source-derived nonnegative binary32 AEC weight Q4/AWB quad conversion. AF mode,
zoom, PD scales and fractions remain caller-owned; no captured transient zoom
becomes a driver constant. All float fields are finite-admitted, output is atomic
on error, Q4 ties/one-ULP neighbors and negative zero/subnormal bounds are checked.
Retained source headers remain pinned and unchanged; staged weight C aggregate
initializer is spelled out solely for C++ Werror compatibility.

Actual built libipa scalar/AF/weights -> current complete native_rear composer
and REAL semantic types/providers/allocator/materializer matches every present
retained startup register word: 714/705/504/345 = 2268/2268, period low5 source bits.
All four DMI shapes match. Clean LSC4/GTM4/GIC3 and BF selector1 four slots match.
No captured RT-CDM output words are INPUTS. Source-forward observed semantic
BG/RS inputs, caller transient zoom and source-produced BPC/LSC/GTM remain SAME
SP11 private. Fixed zero black/unused weights/enables are explicit bounded
diagnostic policy; cold initialization/AFD/transient zoom policy and independent
release tuning/complete adaptive libipa algorithms are NOT proven.

GCC+Clang ASAN/UBSAN full current preflight414 assertions each. Input production
uses existing validated clean source algorithms, actual built libipa and selected
CST tuning; no optional OEM archaeology or repeated closed arithmetic tests.
Evidence includes mixed source/caller policies; exact commands do NOT prove
Linux physical ISP operation, optical quality, fresh live provenance or NV12.

native-rear-startup-entry.inc connects typed inputs synchronously to the actual
E008N single-use wrapper: complete composition before owned command materialization,
then existing prepared runner seam. Heap semantics are erased/freed on every return;
the synchronous wrapper retains only copied command/DMI bytes, never semantic
provider pointers. Uncertain command arenas remain independently pinned. This is
an INTERNAL source contract; no V4L2 callback/public UAPI/rear IPA runtime installed.
Default production authorization STILL DENIED. Real full types/materializer/E008N
and actual prepared validator tested:109 assertions/32 allocation cases per compiler,
zero runner calls, invalid generations and repeated use reject, clean denial frees.
Route and unused runner body are host models; host-only consumption resets explore
independent cases, production has NO reset.

Libcamera build15 Werror zero warnings,10 testsPASS/2 missing-VIMC SKIP.
Build14 first failed C++ aggregate spelling; corrected staged-copy spelling in15.
Kernel build13 W1/Werror PASS,zero stderr,not installed. Build12 first rejected
changed consumer digest before staging; new integration pins corrected13.
Private preflight01 first used wrong stage path and exited before checking;
actual stage11/camss preflight02 PASS. Attempts/job logs retained; no hardware IDs.
9 source composition tests and hygiene/diff/manifest checks PASS.
Evidence docs/NATIVE-RGB-REAR-SOURCE-INPUTS-20261007.json.

Golden5a4d7226-d3b1-4c39-b94f-9d16ce4572ce unchanged; no new camera stream,
candidate/install/reboot. Native44streams/33IDs/66boots;Windows2/2/4;combined70/35.
Rear FIRST, front calibration deferred, lights last user OFF. Pixels/photos/RAW/
spatial arrays/image-derived hashes/OEM originals stay SAME SP11 only.
NEXT bounded physical rear generation/consumed-address/stop proof with uncertain
DMA retained through reboot, typed runtime transport and independent release
IPA tuning/adaptive producers; qualified linear output and matched-scene optics.
User authorizes autonomous milestone progression; no approval pauses at source
milestones. Earlier NEXT and source-gate entries below are historical.

## 2026-10-07 complete integer rear startup integration and partial-start cleanup

Current main-path composition now includes BF ROI finalization plus explicit
calculated CST/BPC-ABF inputs, the previously validated E011AS inactive cold BF
gamma derivatives, and all four scalar/geometry/statistics/stable/adaptive DMI
families in native_rear_compose_startup. Existing52 immutable fragment parents
remain pinned; E011AS derivatives are separately SHA-pinned integration inputs.
Do not repeat Windows AF/BF lineage or previously closed scalar/geometry work.

native_rear_bind_startup_iq uses request-tagged integer AF rectangles; no frozen
transient zoom or captured coordinates. It lowers the supported interior even
BAF/5x5/BF mapping; unsupported clamp/stripe/overlap shapes reject. Real E008T
filter/coring/gamma seeds are reused. CST and BPC-ABF calculated states remain
explicit caller tuning inputs, validated before changing any of four packets.
Cold packet0 has explicit inactive gamma and no invented dummy gamma table.

The complete sleepable composer snapshots all caller inputs, constructs a fresh
four-packet set, validates every family/phase/ID, then publishes readiness/sealing
only on success. All errors/allocation failures preserve the caller destination.
Cached recursive provider self-pointers are rebound at the final stable address
before heap scratch is securely cleared/freed. Real provider/allocator/materializer
host tests prove operation after scratch release and complete all-or-none clearing
on a late packet3 production error. Inputs in this complete test are SYNTHETIC:
configuration completeness is proven, independent tuning/IPA runtime is NOT.

Current E008K runner now marks possible RT-CDM/BUS/CSID/CSIPHY/sensor exposure
BEFORE each attempted start. Every modeled partial-start failure receives stop
attempts; uncertain hardware remains pinned/owner unsafe. Generation U64_MAX
rejects before allocation/owner effects. Fault tests bypass authorization ONLY
in disposable host code; production authorization functions still return
-EOPNOTSUPP. Physical IRQ/consumed-IOVA/stop/reclaim remains unqualified.

Final source build11 W=1/Werror PASS,zero diagnostics,not installed.
GCC+Clang ASAN/UBSAN:
- BF/tuning binder125953 assertions each; same-SP11 BF selector1 exact1200/1200,
  all4 startup payloads; source-forward caller AF rectangle from observed zoom
  is oracle-only, upstream transient zoom policy remains unproven.
- Complete REAL full semantic types/providers/DMI/layout/allocator/materializer:
  592 assertions each, synthetic inputs, simulated host DMA/allocations.
- Actual runner orchestration2297 assertions/53 injected failures each; lifecycle
  helpers and reclaim mocked, no hardware proof.
- Affected prepared consumer regression387 assertions each;9 composition testsPASS.
Build08 failed incorrect MNDS member name; corrected09/10/11pass. A whole-host
negative initially corrupted CST in phase3 where CST is NOT emitted; changed to
BF for the intended late failure. Fault-fixture PM expectation corrected for
already-proven successful stop/reclaim before a final owner-release failure.
Original attempts preserved; no hardware attempt/candidate/reboot/install.

Evidence docs/NATIVE-RGB-REAR-STARTUP-INTEGRATION-20261007.json.
Golden5a4d7226-d3b1-4c39-b94f-9d16ce4572ce idle unchanged.
Native44streams/33IDs/66boots,Windows2/2/4,combined70boots/35IDs unchanged.
Rear FIRST; front calibration deferred. Lights last user OFF. All pixels/RAW/
images/spatial arrays/image-derived hashes/OEM originals remain SAME SP11 only.
Backend10bit compressed/private, NOT NV12; no optical quality parity claimed.
NEXT independent IPA statistics/tuning/adaptive input production and typed runtime
delivery; integrate the clean retained-source full preflight, then bounded physical
rear generation/consumed-address/stop proof and qualified linear output.
User authorizes autonomous progress across milestones; do not ask permission or
end a turn merely because one source step passed. Earlier NEXT is history.

# Native RGB driver integration

The approved architecture also includes [libcamera](libcamera/README.md).
The kernel-only builder below remains the hardware source build; it does not
implement the libcamera pipeline.

This is the current kernel-driver workstream for front IMX681 and rear OV13858.
Read [the engineering audit](../../docs/NATIVE-RGB-ENGINEERING-AUDIT-20261007.md)
for scope, evidence, architectural limits and delivery gates.

## What this builds

- Maintained front CAMSS, including the existing E004IK–IP NV12 negotiation and
  memory-layout planners and the physically exercised QC10C mapped-SG guard.
- 52 rear source fragments with original paths and hashes, including E011I's
  source-only post-stop reclaim candidate and E011Z's startup adaptive binder.
- IMX681 with measured read-only timing controls and OV13858 with the actual
  SP11 board-power/runtime-PM source, rebuilt with W=1 and -Werror.

Hardware identity 03 verified the front timing ABI during 240 sequential RAW
frames, then captured 120 rear RAW frames. All STREAMOFF checks, sensor standby,
neutral routing and protected Golden asset hashes passed. This establishes
sensor/RDI transport, not native processed output or Windows image-quality parity.
See docs/NATIVE-RGB-TIMING-03-20261007.json.

It builds no custom userspace product runtime. Python and compiler commands here
are developer tooling. The front bounded runner remains diagnostic; rear hardware ISP runtime remains denied; current front linear NV12 evidence
is described in the engineering audit. These modules are **not a completed
camera stack or an installation authorization**.

## Build

Use a new output path outside the repository:

```sh
python3 src/native-rgb/build.py \
  --out /home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-NEW-IDENTITY \
  --kernel-source /home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src \
  --kernel-output /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826 \
  --jobs 4
```

Omit the two kernel arguments to stage and audit sources without compilation.
Existing output directories are refused. Source hashes are checked before
creating output. Only manifest-listed kernel sources are admitted.

The builder applies the reviewed retained NV12/DMA overlays, copies the original
rear fragments, and applies the rear integration patch with zero fuzz.
E011I replaces the earlier E008K runner without adding a runtime caller.
E008T's BF composer is adapted from mock-only packet/bootstrap types to the real
E008O packet/set types. All packet identities are admitted before BF mutation;
ready or sealed sets are refused. This does not close BF ROI adjustment/parity.
E011Z is included after the real E008O definitions; its unused binder declaration
is annotated only in staging so W=1 can check it in the actual kernel translation
unit. Its nonadaptive semantic inputs are still required.

E004IO's added DMA include temporarily moves around a context line while applying
the pinned rear patch and is restored before compiling. Every final source digest
is written to source-manifest.json. The build produces build-result.json with
module digests and vermagic. Absolute build/debug paths may change module bytes;
the reproducibility guarantee here is deterministic source composition.

```sh
python3 src/native-rgb/test_composition.py
```

The checks cover changed/outside source rejection, identical independently staged
sources, refusal to overwrite an existing candidate, include integration and
retained DMA/runtime gates. Kbuild separately checks actual ARM64 types, calls
and module dependencies.


## Rear source validation

After a fresh kernel source build, run the hosted actual allocator, command-layout,
validator and scalar-binder checks against its staged sources:

```sh
python3 src/native-rgb/test-rear-prepared-commands.py \
  --staged /absolute/fresh-build/camss \
  --report /absolute/fresh-build/hosted-handoff.json
```

GCC and Clang use address/undefined-behavior sanitizers. Semantic materialization
and hardware callbacks are explicit mocks; this checks ownership, packet separation,
atomic failure cleanup and validation, not complete register semantics or DMA.
The private scalar verifier separately links actual built libipa with the actual
C kernel binder and E006Z register packer. Its inputs stay on SP11 and its report
contains only aggregate counts. Neither test authorizes a hardware submission.

The geometry composer has a separate actual-packer sanitizer suite:

```sh
python3 src/native-rgb/test-rear-startup-geometry.py \
  --staged /absolute/fresh-build/camss \
  --report /absolute/fresh-build/geometry-hosted.json
```

On SP11 only, add `--private-retained-oracle` to compare the retained original
corpus locally. Only aggregate counts enter the report. Address multisets must
match the actual E007Y source skeleton for each phase; undefined OEM period upper
bits are excluded, with Linux producing zero there. This test does not grant
readiness, seal a bootstrap, touch hardware or establish image-quality parity.

Statistics geometry/binding has its own actual-packer suite:

```sh
python3 src/native-rgb/test-rear-startup-statistics.py \
  --staged /absolute/fresh-build/camss \
  --report /absolute/fresh-build/statistics-hosted.json
```

On SP11 only, `--private-retained-oracle` compares the locally decoded scalar
control inputs through the real binder/packers. Geometry candidates come from
source-closed cold/normal presets. The comparison does not prove an independent
IPA control producer; absent packet families have explicit synthetic controls.
The kernel binder is for a sleepable startup context and uses a checked temporary
allocation, cleared and freed on every path. No readiness or hardware grant.

## Current next implementation — rear first

User2026-10-07 deferred front calibration until rear finished. Fresh rear-only
Windows screen/light-OFF baseline PASS; see rear-windows-reference/README.md
and docs/NATIVE-RGB-WINDOWS-REAR-SCREEN-01-20261007.json. Optical originals
remain PRIVATE on same SP11; healthy upper-screen ROI registration still needed.

Front linear NV12, continuous queue, metadata/typed parameters, standard
pipeline/IPA and full-rate manual request controls/lifecycle are physically
qualified in the current audit. Front meter/AE/AWB/IQ remains incomplete.

The prepared-command consumer and integer scalar binding are now source-qualified.
Each rear phase is materialized once into an independent arena; the runner validates
and consumes those outputs without rebuilding them. The existing libipa scalar
producer supplies an internal 208-byte envelope, validated atomically against all
four kernel packet identities. This is not a published ABI or a connected rear
runtime. See docs/NATIVE-RGB-REAR-COMMAND-HANDOFF-20261007.json and
 docs/NATIVE-RGB-REAR-SCALAR-BINDING-20261007.json for the exact evidence limits.

The current-mode geometry/disable/period composer is also source-qualified:
GCC and Clang each pass 565 sanitizer assertions and the same-SP11 retained oracle
matches 207/207 semantic instances. It enforces the existing top-left CSID window
and 10-bit backend; that surface is not linear NV12. See
 docs/NATIVE-RGB-REAR-GEOMETRY-20261007.json. It preserves unrelated state/readiness.

The statistics geometry composer and four-packet binder now pass source checks:
757 sanitizer assertions with each compiler and 126/126 retained binding/packer
observations. Cold presets and caller-owned RS overrides are distinct. Scalar
controls in that comparison are decoded semantic inputs; an independent rear IPA
control producer and runtime API are still open. See
 docs/NATIVE-RGB-REAR-STATISTICS-20261007.json for the exact proof boundary.

Next compose BPC/ABF, BF/AF, explicit CST tuning and DMI inputs into four complete
packet-isolated semantic states, and supply independent IPA statistics controls. Reuse the precise composition-gaps
table in the audit and52 gathered fragments, measured OV13858 RAW/power and
validated NV12 planners. Physical exact-generation completion, serialized owner
and shutdown evidence precede any reclaim/activation; rear ISP runtime remains
denied until those contracts are independently established.

Qualcomm VFE680 uses external CSID completion and does not advertise global
reset. Do not invent a separate-VFE-IRQ or reset prerequisite. Do not revisit
optional OEM metadata/names or promote compilation to processed-frame proof.
