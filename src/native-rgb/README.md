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
