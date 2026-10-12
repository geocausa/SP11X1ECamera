## Internal C-PHY preparation checkpoint, 2026-10-12

Candidate17 compiles a dormant Qualcomm2.1.2 numerical preparation helper.
Explicit frequency bounded before doubling;28 nominal symbol-rate bins;
logical trios1..3, duplicate/unused-entry rejection; nonzero16-bit settle counter;
atomic output publication. No MMIO/power/reset or runtime caller; no generic
PHY ABI change. Counter bounds do not qualify MIPI timing or its clock domain.
Four ARM64 objects W=1/-Werror0warnings; same-source external provider module
links against candidate16's7.2.0 symbols with zero warnings. Candidate17 full
Image not built/booted; candidate16 remains the latest full kernel checkpoint.
GCC/Clang ASAN/UBSAN each6150 valid cases+150 atomic range+21 atomic errors;
9 pin rejections,3file replay PASS. Original PHY files unchanged except Makefile.
Per-file checkpatch clean; one FILE_PATH_CHANGES advisory covered by existing
MAINTAINERS wildcards; advisory-reviewed check clean, no signoffs/submission.
Evidence:docs/UPSTREAM-CPHY-CONFIG-VALIDATION-20261012.json; reproduction:
src/upstream/phy/CPHY-CONFIG-20261012.md.
NEXT qualified receiver timing and GPL sequence, typed PHY configure/consumer
routing, sensor/power graph and guarded hardware; CDM physical retirement open.
Both private consumers/all14 readiness blockers remain. Golden, inactive daily
services, original evidence and calibration preserved; no installation/runtime
or system sleep change. Prior checkpoint4ff3c0f5 is committed/pushed.

## Public PHY/platform integration checkpoint, 2026-10-12

Candidate16 combines own CAMSS patches0001..0009 with12 selected public PHY
v17/API v17/platform v6 patches. Only2 contexts rebased; original bodies and
adaptation separately pinned, with original author/review tags preserved for
the original publications only. Final portable replay:16changed files and47
unchanged CAMSS/ISP files;18 reference pin rejections and retained/nested-output
guards PASS. Four retained AArch64 objects W=1/-Werror0warnings; scoped binding
examples and disabled Denali OLED DTB/schema validation PASS.
Full ARM64 Image/modules W=1 link PASS, with baseline warnings and zero
camera/PHY/ISP warnings. Evidence:
docs/UPSTREAM-X1E-DEPENDENCIES-VALIDATION-20261012.json.
Reproduction:src/upstream/platform/X1E-DEPENDENCIES-20261012.md.

C-PHY v9 pixel-rate fallback discrepancy reproduced in the actual pinned V4L2
helper:75 cases,100 D-PHY controls,3 explicit link controls and4 error controls
per GCC/Clang ASAN/UBSAN. Existing IMX681 explicit1.2GHz/2.4Gsymbol/s link is
unaffected by that fallback. Public GPL2.1.2 reader:28bins/2688 cases per
compiler,16128 dynamic settle writes/8064 default CDR writes. Table settle bytes
are placeholders; missing-table no-op/out-of-range clamp are not admission.
See docs/UPSTREAM-CPHY-RATE-AUDIT-20261012.json and
docs/UPSTREAM-CPHY-PUBLIC-READER-20261012.json. Host fixtures model MMIO/sleep.

The standalone PHY still implements D-PHY only. NEXT typed C-PHY configure,
explicit sensor frequency, dynamic settle/supported-rate validation, public
GPL sequence/CSID routing and sensor/power graph. CDM provider wiring, command/
image ownership and physical retirement/recovery remain open. Both private
startup consumers/all14 readiness blockers remain;15 readiness unit tests PASS.
No installation/boot/capture/service/system-sleep changes. Protected Golden,
inactive daily camera services, original evidence and calibration preserved.
Earlier handoffs below are historical; current source counts are9own+12public.

## Dormant CDM2.1 power ownership checkpoint, 2026-10-12

Patch0009 adds parent-supplied PM/clock ownership and a pre-MMIO owned reset
guard. Partial acquisition unwinds only its references; every reset attempt
retains power. Unused release is blocked after reset/quarantine; post-reset
retirement/recovery and release remain unimplemented. No parent runtime calls,
DT/provider routing, capture or installed stack changes.
Candidate14 ARM64 CAMSS/generic ISP objects W=1/-Werror0warnings; GCC/Clang
ASAN/UBSAN201 power+659 reset+899 binding cases/423965 assertions each,
18 pin rejection controls, six exact kernel bulk functions executed.
9patch/17file replay;46 other CAMSS files unchanged. Standard checkpatch has one
FILE_PATH_CHANGES advisory; recursive CAMSS MAINTAINERS covers the new files.
Ignored-advisory and four per-file checks clean; no signoffs/submission claim.
Evidence:docs/UPSTREAM-CDM21-POWER-VALIDATION-20261012.json; reproduction:
src/upstream/camss/CDM21-POWER-20261012.md. Candidate13, failed host fixture and
first replay preserved. Hosted models do not prove hardware/provider contracts.
Both private startup consumers/all14 blockers remain; Golden and daily stack/
evidence/calibration preserved. NEXT exact provider routing, command/image
lifetime and physical retirement/recovery before runtime admission; exact VFE
fields, compatible full build and hardware qualification.

## Dormant CDM2.1 resource binding checkpoint, 2026-10-12

Patch0008 binds named platform register extent and an exclusive NO_AUTOEN IRQ,
with managed-group rollback and atomic output publication. Binding performs no
MMIO/power operation. Reset enables IRQ only after fresh version/mask/drain/
clear/pause/epoch admission; pre-enable failures do not nest disable depth.
Active pre-command status is cleared and faults without counting ACKs; caller
rejects the fault before issuing reset. This supersedes pre-command ignore in10.
Candidate12 ARM64 CAMSS/generic ISP objects W=1/-Werror0warnings; GCC/Clang
ASAN/UBSAN899 binding+659 reset hosted cases/257422 assertions each;12 pin
rejection controls. New patch checkpatch0warnings;8patch/15file replay;47 other
CAMSS files unchanged. Candidate11 source/build/first patch/pass fixture retained.
Evidence:docs/UPSTREAM-CDM21-BINDING-VALIDATION-20261012.json; reproduction:
src/upstream/camss/CDM21-BINDING-20261012.md. Managed cleanup, IRQ depth and
MMIO are hosted models, not physical teardown/concurrency/DMA evidence.
No parent probe/runtime calls or DT/resource/IRQ/PM/clock changes; current
upstream X1E binding has no CDM resources. Both private startup consumers/all14
readiness blockers remain. Daily2/Golden and original evidence preserved.
NEXT reviewed CDM DT and power/clock ownership, command/image allocation and
physical retirement; exact VFE core/Bayer/precision, compatible full provider
build and fresh hardware qualification without private startup/carrier fallback.

## Dormant CDM2.1 kernel backend checkpoint, 2026-10-12

Patch0007 adds an actual CAMSS-compiled internal reset/IRQ backend. No parent
runtime hooks, DT/resource/IRQ/PM binding, submission, allocation or DMA release.
Exact revision read before writes; four-bank mask/drain/clear, reject pre-command
status, one reset command, unique four-bank ACKs, final late-fault check and
empty FIFO readbacks. Errors quarantine and disable the exclusive Linux IRQ;
pause request/readback is not pause completion or DMA retirement certification.
Candidate10:ARM64 CAMSS/generic ISP objects W=1/-Werror0warnings; GCC/Clang
ASAN/UBSAN659 hosted cases/233600 assertions each;12 pin rejection controls.
Seven patches/15files replay;44 earlier CAMSS source files unchanged. Standard
checkpatch has one reviewed FILE_PATH_CHANGES advisory; existing CAMSS entry
covers these paths; per-file/advisory-reviewed checks clean. No signoffs invented.
Candidate09 and corrected initial host fixture preserved; evidence:
docs/UPSTREAM-CDM21-BACKEND-VALIDATION-20261012.json; reproduction:
src/upstream/camss/CDM21-BACKEND-20261012.md. Source-only, not runtime admission.
Both private startup dependencies/all14 readiness blockers remain. No capture,
module/DT/runtime/service/boot changes; Golden and daily2 remain preserved.
NEXT parent CDM resource/IRQ/PM and command/image ownership integration;
exact VFE core/Bayer/precision, compatible full build and physical qualification.

## CDM 2.1 observation checkpoint, 2026-10-12

Own source helper bounds four public FIFO counts and observes four unique reset
ACK banks in a serialized epoch; duplicates/stale epochs cannot advance it and
unexpected status latches a fault. No MMIO/submission/free or retirement claim.
Public CDM2.1 lacks pause-complete status; CDM3.1 fields are not substituted.
GCC/Clang ASAN/UBSAN each:12048 actual-public-decoder snapshots,24 IRQ bank
orders,111298 assertions PASS;9 reference pin rejections. ARM64 object and
checkpatch:0warnings. Eight exact public GPL files pinned; three used by oracle.
Evidence:docs/UPSTREAM-CDM21-STATE-VALIDATION-20261012.json; repro:
src/upstream/isp-config/CDM21-STATE-PROVENANCE.md. Epoch is software bookkeeping,
not hardware IRQ freshness; all hardware ordering/retirement gates remain.
Both private startup consumers and all14 readiness blockers remain.
No capture/runtime/boot/service changes. Prior CSID candidate08 preserved.
NEXT integrate owned CDM FIFO/reset/IRQ resources with physical stop/retirement;
resolve exact VFE core/Bayer/precision, build compatible provider and qualify.

## CSID680 shared initialization checkpoint, 2026-10-12

Patch0006 selects the exact public complete software reset and receiver cutoff;
old reset IRQ is masked/drained/cleared before fresh completion, stuck status
rejects and timeout leaves TOP masked with handler drained. This is power-up
initialization only, not a streaming stop or physical DMA retirement proof.
Candidate08 ARM64 CAMSS/generic ISP objects W=1/-Werror:0warnings. GCC/Clang:
102 freshness/failure cases +26 actual public reset comparisons each PASS;
5 tool-input rejection cases;6-patch/10-file replay;prior completion source
unchanged. Nine exact Qualcomm GPL source files pinned. Evidence:
docs/UPSTREAM-CSID680-RESET-VALIDATION-20261012.json; repro:
src/upstream/camss/CSID680-RESET-20261012.md. Candidate07 source/build/style
attempt retained;08 corrects comment spelling only. Initial halt-enum fixture
error corrected with named public enum choices;no initial pass claimed.
No capture/reboot/module/DT/runtime/power changes;both private consumers remain.
NEXT exact core/Bayer/precision and owned CDM/FIFO/image resource integration,
including separately established physical stop/IRQ retirement, then qualification.

## Completion integration checkpoint, 2026-10-12

Storage headroom restored by removing only reproducible build intermediates
(9276964864 allocated bytes), retaining source/final artifacts/calibration/evidence.
The next real CAMSS integration slice initializes CSID680 completion status and
bounds hardware/port/line/output/group routing; composite scan takes one mapping
snapshot. Candidate06 strict ARM64 CAMSS/generic ISP objects: zero warnings.
GCC/Clang2630 actual-function hosted cases each, six pin-rejection cases and
five-patch/ten-file replay pass. Evidence:
docs/UPSTREAM-CAMSS-COMPLETION-VALIDATION-20261012.json.
This supports resource integration but is not physical DMA/IRQ retirement,
a processed provider or runtime independence. Both private consumers remain.
The author VFE680 branch was rechecked and is still the pinned8fba1208 source;
no new exact core/Bayer field encoder was found in the checked public sources.
NEXT exact core/Bayer/precision and owned CSID/VFE/CDM integration, physical
stop/IRQ retirement, then fresh no-private-input hardware qualification.

## Processed input checkpoint, 2026-10-12

A separate public-derived CSID680 RAW10 IPP register plan now passes actual
GPL-function comparison and ARM64 object checks. Seven writes prepare the
disabled input path; the target is CSID, distinct from VFE CDM. Evidence:
docs/UPSTREAM-CSID680-IPP-VALIDATION-20261012.json.
The prepared source pieces cover input decode, front processing and FULL NV12
bus setup, with no private input in these helpers. A full provider still needs
exact VFE core/Bayer/precision and safe owned-resource linking/retirement.
Reuse Claude's measured front/rear calibration and generators, then revalidate
domains on the independent path. Both installed private consumers remain.

## Current checkpoint, 2026-10-12

Independent front processing and disabled FULL NV12 bus setup now pass host
and ARM64 object checks. The new bus setup derives its34 fields from exact
public VFE680 definitions and bounded extents, with no private input or enable.
Evidence docs/UPSTREAM-VFE680-NV12-VALIDATION-20261012.json;
input audit docs/UPSTREAM-VFE680-INPUT-AUDIT-20261012.md.
VFE680 uses TOP4 and expects core setup via CDM; older CAMIF3 logic and
different TOP4.1x addresses do not resolve its bit fields.
NEXT exact core/Bayer routing/precision, independent CSID and owned bus/CDM
binding with physical DMA/IRQ retirement. Both installed private consumers remain.
No source result waives provenance, upstream review or hardware gates.

## Current implementation priority, checked 2026-10-11

Windows runtime dependency removal comes first. A new independent front
processing builder now emits1204bytes/81 register commands with zero DMI:
explicit module disables, public demosaic parameters, mathematical BT.601,
derived geometry/rounding and final enables. GCC/Clang sanitizer and ARM64
kernel-object checks pass. This is not a complete startup provider; both
installed private consumers remain. Read
src/upstream/isp-config/FRONT-MINIMAL-PROVENANCE-20261011.md and
docs/UPSTREAM-FRONT-MINIMAL-VALIDATION-20261011.json for source pins and limits.

NEXT resolve VFE680 core/Bayer routing, internal precision and bypass, then
bind independently generated CSID/NV12/CDM setup with physical DMA/IRQ retirement.
No unknown setting may come from a private carrier, schema or retained
steady-update fallback. Compile a fresh candidate before optical qualification.
Rear GRBG needs a separate provider. Add open tuning/statistics afterward.

Supporting CAMSS work: posted74-patch RFC replay325 Git blobs; prepared full
public base; four local source patches compile CAMSS/generic ISP objects.
Candidate03 preserves allocator-paired stop/release and passes688 host cases
per compiler. VFE680 is still RDI-only; full kernel/modpost/PIX/hardware and
public generated-header provenance remain unqualified. This changes W0/W1
implementation order, not any readiness gate.

# SP11 RGB camera upstream implementation plan

Date: 2026-10-11. User authorised planning and implementation of the remaining
work, eliminating private Windows runtime dependencies and preparing upstream
submissions. Sending mail or publishing a submission requires an explicit user
instruction. This plan is engineering work, not a guarantee of maintainer acceptance.

## Baseline and working arrangement

- Preserve Claude's daily stack at `5317d52801ae300eab7a39ec517f248e69fcd0df`,
  branch `work/native-rgb-driver-20261007`, as the functional comparison baseline.
- New work: `work/upstream-open-stack-20261011`, checkout
  `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream`.
- Running SP11: Golden kernel `7.1.5-sp11-render-parity-v4+`, opt-in daily camera
  DT/modules, camss build 48 and libcamera tree 21. Both bridges active.
- GRUB saved default is `sp11-audio-fullio-v19c`; `next_entry` is empty.
- Other dirty/untracked work remains in the original checkout; it is not staged.
- Work on SP11 through PiMaster. No system suspend/hibernate tests. No changes to
  unrelated audio/touch/display/power stacks. Protect Golden payloads and modules.
- Camera pixels, proprietary settings and driver packages remain private on SP11.
  Existing Windows observations are a private behavioural comparison, never a build
  input for the new stack. Open tuning is generated from standard mathematics or
  independently recorded measurements with provenance.
- Free disk space was about 6.4 GiB at audit. Avoid duplicate full kernel builds
  and large image captures until space is budgeted; preserve original evidence.

## Current dependency inventory

| Dependency | Observed consumer | Replacement and required proof |
|---|---|---|
| Front 36,744-byte private profile `qcom/sp11/imx681-2560x1440-nv12-v1.bin` | `native-front-profile-kernel.inc`, SHA-pinned loader, reconstructed carrier | Generate functional mode/register setup and open tuning directly. Both cold start and repeated streaming must succeed with no private loader or fallback. |
| Rear 16,672-byte private input `/lib/firmware/qcom/sp11/rear-generation-20261007-60.bin` | `native-rear-generation-hook.inc`, typed startup input | Independently generate scalar, geometry, statistics, IQ and adaptive LSC/GTM state; retain validated DMA/stop lifetime until replacement is proved. The rear file lives outside daily2's firmware directory. |
| Own measured front LSC and ABF binary tables | Front loader overrides | Retain measurement provenance; publish generator and open textual calibration. Generate exact bytes reproducibly, then deliver them through the agreed ISP parameter interface. A generated binary is not intrinsically proprietary. |
| Windows-derived defaults in schema/constant/module enable code | Kernel composition and inactive experiment branches | Inventory all fields, distinguish functional observations from tuning, replace tuning and unexplained defaults, and remove legacy fallback from the curated submission. Renaming/re-encoding copied tuning does not make it open. |
| Experimental selectors/switches and private paths | Kernel and install/build scripts | Remove from production series; use normal media entities, formats, parameters and statistics. No hardcoded lab paths in submitted runtime code. |
| Userspace I2C autofocus plus camera-only RPMh workaround | Webcam bridge and private DT additions | Standard actuator subdevice and standard regulator DT/provider after root-cause testing. No raw I2C/root requirement for application use. |
| Webcam bridge rendering | Local camera product | Integrate approved hardware ISP and/or software processing through libcamera. Loopback bridge remains an optional local app; upstream camera correctness cannot depend on it. |

The source tree has no tracked `.sys/.dll/.bin` payloads, but that alone does not
prove independence. The curated build and runtime dependency graph must be checked.

## Ordered work and completion gates

| Stage | Tasks | Depends on | Done when |
|---|---|---|---|
| W0 Baseline and source audit | Record exact source/build/machine state; map every loaded/input file and generated or embedded table; list license/author/primary reference; identify current upstream bases and related maintainer series; budget storage. | None | Both camera consumer graphs recorded; every unknown/private item is a visible blocker; reproducible baseline retained. |
| W1 Open front startup | Implement neutral/open gamma, colour conversion, shading and black level; derive functional DEMUX, scalers/crop, statistics and output configuration; generate safe module enables/denoise defaults; rebuild CDM startup without a private profile or a private schema-value fallback. | W0 | Host bounds/packing tests, actual kernel compile and guarded cold-boot/stop/reopen tests pass with private firmware inaccessible and no legacy loader. Own calibrated settings can replace neutral bring-up defaults later. |
| W2 Open rear startup | Replace all four-packet scalar inputs; derive active 4064x2286 GRBG geometry and 3840x2160 NV12 output correctly; replace statistics and IQ state, LSC/GTM/ABF/BF tables; keep addresses from actual DMA allocations, never traces. | W0; shared W1 compiler | Native 4K source stream, manual controls and AE run without `rear-generation-*.bin`; register/table sources and generation are fully documented; stop/reopen ownership checks pass. |
| W3 Power and lens | Diagnose standard PM8550 LDO16 boot hang with preserved pre-systemd logs and single-variable candidates; review parent rails/constraints/deferred probing and RPMh acknowledgement; reuse an existing compatible actuator driver only if protocol and power behaviour match, otherwise write DW9800 driver/binding; expose standard focus controls and smooth park/runtime PM. | W0 | Standard regulator topology cold-boots repeatedly, rail enables only for its consumer, focus works through V4L2, failure/stop powers down safely. Temporary provider and userspace I2C are unnecessary. |
| W4 Kernel interfaces and cleanup | Rebase on current media/PHY maintainer trees; split C-PHY, board topology, CSID/VFE, CDM, processed output and parameter/statistics support; remove experiment switches and format-based sensor identification; support deterministic resource arbitration; evaluate the generic V4L2 ISP block format before introducing custom serialization; define typed validated buffers, epochs, stale rejection and UAPI layouts with documentation/compatibility. | W0; W1/W2 prove requirements | Small buildable patches with clear dependencies, no arbitrary raw register replay from userspace, unchanged buffer/DMA safety, maintainer-aligned API proposal, locking/error/unbind checks. |
| W5 Sensor/board series | Minimise/document IMX681 mode/init; upstream controls, formats, timings and runtime PM; add only necessary OV13858 changes; review clock/regulator/reset supplies and graph endpoints; write DT schemas and board patches including lens linkage/rotation/orientation. Remove unneeded IR placeholder/private parity paths from RGB export. | W0; W3 for focus DT | `dt_binding_check`, scoped `dtbs_check`, style/build tests, runtime-PM/readback and cold-start/stream-stop checks pass. Separate existing mainline support from genuinely missing code. |
| W6 libcamera | Use normal CameraSensor/Lens abstractions, one hardware-aware pipeline, clean asynchronous IPA protocol and typed params/stats; remove environment-selected lab protocols and private paths; AE/AWB/AF exposure metadata correspond to the image frame; implement resource contention predictably. | W4 API; W5 devices | Native `cam`/qcam and application capture work without loopback bridge; manual/auto controls verified; library tests and applicable compliance checks pass. |
| W7 Open image processing | Establish identity/neutral tests first; measure black level/noise/shading across gains; independently calibrate CCM/AWB/tone; migrate bridge processing through an accepted hardware or software path; test denoise/temporal motion, clipping, halos, detail, colour under varied lighting; account for CPU/power/latency. | W1/W2; W6 | Held-out scenes/illuminants and motion tests meet declared tolerances; open tuning regenerates from owned scalar inputs; no private tuning tables or bridge-only requirements. Windows parity is measured separately from upstream readiness. |
| W8 Lifecycle and product validation | Cold boots, repeated start/stop/reopen, long soaks, both camera switching, simultaneous-open contention, consumer/process stalls, disconnect/service restart, low memory/allocation and invalid-param errors; native rear 4K and front mode checks; frame provenance/drops/timestamps; sensor idle and memory reclaim. Check audio/touch/display/USB regressions while OS remains awake. Record system-suspend coverage as unvalidated on SP11; require suitable hardware before claiming complete system power-management coverage. | W1-W7 as applicable | Automated results fail on actual capture errors, invalid/dropped/repeated frames and forbidden kernel faults; measurements tied to exact source; power and resource lifetimes proved. Prior full-system hang is explicitly tracked, never dismissed by one passing rerun. |
| W9 Export and review | Curate separate kernel/libcamera series, no historical experiments/private data; SPDX, copyright, DCO, attribution, bindings/UAPI docs, tests and cover letters; verify all patches build in sequence; identify recipients from actual target tree; prepare review messages early for interfaces, implementation series when qualified. | Individual qualified components; full pipeline last | Clean fresh-machine builds have only declared open inputs; dependency gate passes; reviewer can reproduce each claim. User reviews the concrete submission before it is sent. |

W1/W2 are the first implementation priority. W3 can be researched independently;
small sensor/PHY components can be prepared before the whole ISP pipeline is complete.
Coordination is an early design requirement, not something to defer until a large
pipeline rewrite is finished. This plan does not assume upstream accepts a new
driver when an existing compatible driver or an in-flight patch series can be used.

## First implementation slice

`src/upstream/isp-config/open_config.py` creates data-only primitives for both
camera modes from mathematics and observed Linux mode geometry. It contains no
profile reader. It derives NV12 storage, a Bayer-aligned example metering grid,
BT.601 coefficients preserving neutral greys after quantisation, identity CCM,
identity/standard sRGB gamma and unity LSC. Numerical tests exercise bounds,
signed fields, all neutral 8-bit values, primary colours and endpoint reconstruction.

This is deliberately labelled a partial compiler. It does not yet create a
complete kernel startup carrier, select DMI addresses, program a scaler or
establish a hardware statistics layout. The metering grid is an example policy,
not a promise to match the existing front/rear layout. Neither camera's installed
private dependency has been removed by this source-only work.

`docs/UPSTREAM-COMPONENTS-20261011.json` tracks 14 required components.
`tools/check-upstream-readiness.py` refuses missing/blocked components, unreviewed
provenance, private dependencies, unpinned evidence and unqualified hardware.
It is a manifest consistency gate; independent audit of the exported dependency
graph and maintainer review are still mandatory.

Next concrete slice: derive front scaler/CST/stats/module setup register groups
from the mode and verified public definitions, enumerate all remaining private
scalar fields, implement a new provider without importing private data, then
compile and test a fresh guarded candidate. Rear geometry is kept distinct.

## Second implementation slice: typed front field compiler

`sp11-cdm.h` now generates bounded contiguous register and DMI commands from
kernel-owned inputs; `sp11-front-fields.h` produces sparse CST/CCM coefficients
and FULL round/clamp commands. Public CDM revision/hashes and functional field
provenance are recorded. GCC/Clang sanitizer checks and an SP11 kernel-header
compile pass. 34 distinct fields cover 74 occurrences in the existing source
inventory. This is still a partial compiler, not a complete startup provider.
Source qualification and the precise hardware admission gates are documented in
`src/upstream/isp-config/FRONT-FIELDS-PROVENANCE-20261011.md`. Both installed
private dependencies remain; no new module was loaded and no camera capture
or reboot was performed. The readiness gate cannot waive required camera
hardware qualification through a manifest flag.

## Hardware experiment admission and rollback

Before each mutation, run the overlap guard and confirm current HEAD, active
build/capture processes and proposed output paths. Before boot work additionally
verify Golden payload hashes, saved default and empty pending boot entry. Source
work may occur while daily bridges idle; runtime changes may not race application
capture or another turn. An unexpected experiment directory is audited first.

Record a unique identity, hypothesis, exact source, kernel/DT/initrd hashes,
private input policy, expected observations and rollback before camera access.
Use a separate candidate module/DT directory and one-shot GRUB entry. Preserve
Golden. Every attempted identity is retired; no automatic replay after timeout.
Require all DMA/source/CSID/CDM stop proofs before freeing memory. A hardware
watchdog does not prove pre-systemd recovery; verify early boot logging/recovery
before revisiting the regulator hang. Never run OS-level suspend tests.

## Authoritative design references

- Kernel patch process: https://docs.kernel.org/process/submitting-patches.html
- Camera sensor guidance: https://docs.kernel.org/driver-api/media/camera-sensor.html
- Media UAPI: https://docs.kernel.org/userspace-api/media/index.html
- ISP parameter formats: https://docs.kernel.org/userspace-api/media/v4l/v4l2-isp.html
- libcamera architecture: https://docs.libcamera.org/master/libcamera_architecture.html
- Pipeline guide: https://docs.libcamera.org/master/guides/pipeline-handler.html
- IPA guide: https://docs.libcamera.org/master/guides/ipa.html
- Existing project primary Qualcomm GPL C-PHY source/verification is documented
  in `docs/PROVENANCE-AND-UPSTREAM-PATH-20261010.md`; pin the exact public source
  revision and retain original authorship before exporting the table.

External series and current maintainer branches must be rechecked when preparing
patches. Earlier project notes naming a series version do not establish its current
status. No maintainers have been contacted by this work.
