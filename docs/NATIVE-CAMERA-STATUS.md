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

> Current RGB driver status and next gates are in
> [NATIVE-RGB-ENGINEERING-AUDIT-20261007.md](NATIVE-RGB-ENGINEERING-AUDIT-20261007.md).
> The earlier statuses/plans below are historical, not current release readiness.

# Native camera stack status — 2026-09-17

Branch: `experiment/e004-front-ir-vd55g0`. Scope: SP11, SP7 and PiMaster.
This is the current ordinary-memory Linux route. It does not claim Windows Hello
security parity, completed image quality, or an upstream-ready driver.
The original five locally modified handoff/state files remain untouched.

## Mechanically proven

| Milestone | Evidence | Result |
| --- | --- | --- |
| Native IR transport | E004es | Four complete 644x604 Y10P frames |
| Sensor test pattern | E004ev | Four exact full-frame horizontal ramps, no leading dark rows |
| Buffer reuse and real timing | E004ew | 16 sequences through four buffers; actual clock 137.6 MHz |
| Standard exposure | E004ex | Requested/applied 1000 lines, unity analogue/digital gain |
| Stock libcamera discovery | E004ey | Ubuntu 0.7.0-1ubuntu2, simple/qcom-camss pipeline, MONO/R10_CSI2P |
| Stock application capture | E004ez | Stock cam owns 16 complete requests and stream lifecycle |
| Standard selection API | E004fa | All four full-array rectangles; no libcamera rectangle errors |
| Non-unity analogue gain | E004fb | Applied code 16 (2x), stock cam 16 frames, clean PM and kernel |
| Native processed monochrome | E004fe | 16 complete RGB888 pattern frames including frame zero; clean PM and kernel |

Each completed candidate returned to Golden FullIO v19c and was retired. Latest
captures are bounded runs of roughly a third of a second, not endurance proof.
E004fa's original live log collector failed; its exact-boot persistent journal
recovered successful start/controls/stop/power-off evidence. Original failed
runtime evidence is retained. E004fb replaces line-count slicing with tested
same-boot timestamp filtering and passes directly.

The native sensor exposes exposure, analogue gain, digital gain, test pattern,
link frequency, pixel rate and fixed blanking through V4L2. Selection reports
(0,0)/644x604 including borders, following the fixed board mode and ST convention.
The nominal 420 MHz link request is unchanged; 137.6 MHz is measured sensor timing,
not a measurement of link frequency. Status snapshots are sequential reads, not
atomic frame-associated metadata.

RGB retains its earlier bounded nondefault readiness; consult the canonical
`src/sp11-camera-stack/READINESS.json` and E004eo evidence. This IR work does not
promote RGB, protected-worker or complete-stack readiness.

## Current blockers and next work

1. **Useful IR scene signal remains unproven.** Normal captures remain close to
   black, including longer exposure and 2x analogue gain. Illumination GPIOs stay
   disabled. Establish the optical/illumination cause with same-machine evidence;
   do not treat RAW transport or an exact generated ramp as image quality.
2. **Processed monochrome output is missing in stock libcamera.** It advertises
   packed samples, but the selected EGL software ISP rejects R10_CSI2P. The CPU
   conversion and statistics paths also require Bayer layouts in inspected 0.7.0
   source. E004fc now implements native CPU monochrome conversion and statistics,
   with normal and sanitizer tests passing. E004fe now proves 16 live processed
   pattern frames including the first frame; ordinary scene quality remains open.
3. **Sensor integration is incomplete.** The generic gain helper passes offline;
   E004fe proves live binding. Establish measured black-level policy, characterize control delays, and report board orientation
   from verified firmware/DT facts. Current app control inventory exposes only
   Contrast/Gamma; kernel exposure/gain are proven, app request controls are not.
4. **Lifecycle and desktop integration remain.** Test repeated start/stop,
   failure recovery, long capture, suspend/resume, camera switching, then
   PipeWire/portal/application use. No general-purpose camera service is installed.
5. **Upstream consolidation remains.** The maintained kernel candidate is still
   board-specific. Separate Denali power/DT facts from generic sensor support,
   provision firmware separately, and align with the reviewed ST driver approach.

## Upstream direction and primary references

A September 2 VD55G-family patch series proposes VD55G0 support. It is a proposal,
not proof of acceptance. Review asks to extend existing support rather than add
and remove duplicate drivers. Our measured timing, dark-row handling and board
facts need to be assessed against that shared implementation.

- Proposed driver: https://lkml.iu.edu/2609.0/05703.html
- Integration review: https://lkml.iu.edu/2609.0/07837.html
- libcamera sensor interface: https://docs.libcamera.org/master/sensor_driver_requirements.html
- ST reference: https://github.com/STMicroelectronics/vd55g0-linux-driver
- ST integration manual: https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf

## Resume rules

Read AGENTS.md and this status, then inspect HEAD/origin, live boot, active
processes and consumed/retired records. Latest retired hardware identity is
E004fe; never reuse it. Start a fresh identity for the next hardware run.
Keep Golden the permanent default. No protected SecureISP runtime activation.
Native code is in `src/front-ir-vd55g0/native/`; experiment results are under
`experiments/E004-front-ir-vd55g0/`. Proprietary firmware and raw captures stay
local and ignored. Only exact intended source/evidence paths are staged.

## Offline integration checkpoint: E004fc

An isolated upstream libcamera 0.7.0 build now includes the generic VD55G0 gain
helper and true RAW10 monochrome processing. Four focused tests pass; the mono
processing tests also pass with address/undefined-behaviour sanitizers. Automatic
CPU selection and a colour-free generic tuning fallback are included. Patches
reapply byte-exactly to the recorded upstream base. No system library was replaced.
E004fd captured 16 processed frames but failed: frame zero used stale zero IPA
parameters; frames 1..15 are verified neutral ramps. The candidate is retired.
E004fe fixes asynchronous parameter ordering and passes all 16 frames, including
frame zero. Both candidates are retired. Next investigate useful optical signal.
See E004fc/README.md and MONO-MANIFEST.json for exact coverage and limitations.

## Offline illumination checkpoint: E004ff/E004fg

The exact exported Windows flash extension specifies 700 mA; matching driver
fallback/default values corroborate configuration, not measured current.
E004fj now proves the active PMIC channel pairing. Pulse timing, duty cycle and
effective safety timeout remain unresolved. No Linux emitter activation has occurred.

E004fg supplies a small generic qcom-flash patch: external strobe now shares the
software path's current-budget, flash-current and timeout preparation. The
baseline failure reproduces in an offline callback model; the patch passes 16
cases normally and with sanitizers, compiles as an isolated module with W=1,
and passes strict checkpatch. No system driver was installed. See E004fg for
scope and limitations. Next obtain same-machine emitter routing/timing evidence.

E004fh confirms 700 mA in the installed Windows flash device registry and exact
archive matches for all four running flash/PMIC driver binaries. It was a
read-only collection, with no camera or illumination command. Golden return
98b67104-e3eb-4091-8b6c-180fd054bd06 and unchanged boot order are verified.
E004fj observes the installed PMIC driver's initialized four-channel table in an
idle Windows RAM snapshot. Logical LED1 uses native one-based sources 1 and 4;
LED2 uses 2 and 3. Combined with E004fi, the configured 700 mA request maps to
350 mA per LED1 channel. This is configuration/driver arithmetic, not measured
current or optical output. No camera or flash command was sent. The initial
symbol lookup failed and was recovered by resuming, refreshing module metadata,
and then reading one 32-byte snapshot; the full sequence is preserved.
Golden return 15ea0beb-c042-4a22-a833-97b8c0e019e8 is verified.

E004fk finds and fixes a second generic qcom-flash issue: the lower-level helper
changes trigger mode while a channel may still be armed. Patch 0002 clears this
LED's channel mask before configuring trigger registers, then enables only after
all configuration succeeds. Fifteen register-model cases pass normally and with
sanitizers, including seven injected failures. The combined source also passes
E004fg's 16 callback cases, W=1 module build and strict checkpatch. Both patches
reapply exactly. Patch 0001 alone is not an adequate integration candidate.
Neither patch is installed; physical bus-error behavior and concurrency remain
unproven.

Next establish Windows sensor strobe edge shifts, exposure/duty-cycle limits,
PMIC trigger configuration and timeout behavior before native emitter activation.
The installed 700 mA setting alone is not a pulse-duration specification.


## Windows timing checkpoint: E004fl/E004fm

E004fl replays the exact saved initial sensor packet: GPIO1 strobe, zero edge
shifts and 100-line initial exposure. Static PMIC decoding yields hardware,
level-sensitive, active-high triggering. The input selector is platform-dependent;
Windows also clears an unresolved common bit at ee67. A separate timer helper's
1270 ms setting is not proven active for this sensor and is not board pulse policy.

E004fm acquired 12 ordinary Windows IR frames and stopped cleanly. Its partial
trace confirms an actual 700 mA LED1 request. A debugger expression error required
removing the breakpoint and resuming; later selector/timer requests were not
captured. Standard exposure readback remained 0.5 ms in auto mode, not proven
sensor exposure. Both errors and recovery are retained. Golden return is verified
on boot aec4c427-6fee-4590-9a30-c6eaa888295f. Next validate logger syntax before a
fresh Windows identity. No native illumination activation has occurred.


E004fn closes the flash-request sequence gap on a fresh Windows boot: seven idle
logger checks passed, followed by five auto-resuming hits around a successful
12-frame capture. Requests were current [700,0,0] mA, input selector 0, trigger
words [1,1,0,1,0], LED1/module arm and disable. With the proven active PMIC table,
this matches Linux's selector-0, hardware, level, active-high configuration for
sources 1 and 4. No timer request appeared at this helper; live timer state and
actual sensor pulse envelope remain open. Standard exposure still reported 0.5 ms
in auto mode and is not promoted to physical timing evidence. Golden return
cd5253ff-bffa-495f-895d-79831524a6ff is verified. Both native flash patches remain
uninstalled. Next resolve actual sensor exposure and PMIC timeout/common-bit
state before emitter activation.

## E004fo consumed observer attempt / E004fp correction

E004fo did start one fresh Windows one-shot, but its first idle KD validation failed because the generated expression used unsupported `&&`/`||` operators. By the experiment contract that command error consumed the identity; subsequent same-boot observations are retained only as diagnostics and are not accepted register-level Windows authority. The recovered debugger log is hash-pinned in E004fo evidence.

Those diagnostics exposed two concrete observer defects. At `qcpmic8380+0x23af8`, the one-byte read result is in `[sp+0x18]`; `x21` is not yet that buffer. The helper then overwrites `w24` at `+0x23b0c`, so the original POST filter on `w24` suppressed every post-write record. Static disassembly proves the original register is preserved in low 16 bits of `w27` at `+0x23aac`, and `x21` holds the final one-byte write buffer by `+0x23bec`. E004fp is prepared as the fresh corrected identity using those lifetimes and KD-compatible single `&`/`|` expressions. Both Python and PowerShell generators pass the static equivalence check. Native illumination remains off.

## Windows PMIC register checkpoint: E004fp

E004fp closes the PMIC register-write uncertainty from E004fn on a fresh bounded
Windows identity. A corrected idle-validated KD observer captured seven paired
`qcpmic8380.sys` masked read/modify/write operations during one 12-frame IR
preview; every read and write returned status 0. The four trigger registers
`ee4a..ee4d` first received mask `0x70` / requested `0x00` while retaining
`0x01`. Paired LED1 registers `ee4a` and `ee4d` then changed from `0x01` to
`0x05` under mask `0x07`. Common register `ee67` bit 0 changed from 1 to 0 under
mask `0x01`. Combined with E004fl's exact handler decoding, this live-proves the
Windows selector-0 hardware, level-sensitive, active-high trigger programming for
LED1 sources 1 and 4 and the previously unresolved common-bit clear.

No access to PMIC timer registers `ee3e..ee41` appeared in this single bounded
session. That absence does not establish global timer state or prove the timer is
unneeded. The Windows standard exposure API again reported Auto=True / 0.5 ms,
which is not direct sensor-register exposure evidence. Physical emitter current,
optical output and pulse width remain unmeasured. Both native qcom-flash patches
remain uninstalled and native illumination remains disabled. E004fp returned
cleanly to protected Golden boot `e60ab8bd-9e89-4d98-9d4f-2f897ec99248` with
unchanged BootOrder, empty `next_entry` and overlap guard PASS. Next close actual
VD55G0 exposure/strobe-envelope timing and any required PMIC timer/timeout policy
before native emitter activation.
