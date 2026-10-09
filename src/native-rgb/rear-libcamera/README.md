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
