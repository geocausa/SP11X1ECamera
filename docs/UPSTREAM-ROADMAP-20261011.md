## Current upstream alignment, checked 2026-10-11

Read UPSTREAM-OVERLAP-20261011.md before choosing an ISP integration base.
Fresh October5/6/7 proposals and review favour extending existing CAMSS/VFE.
Pin/review the full current RFC/dependencies, then add SP11 VFE680 blocks,
metadata/output grouping and lifetime changes on that structure. The new typed
field compilers remain source tests, not a submission ABI or startup proof.
Public VFE880 setup is a reference with hardware differences; no drop-in port.
Current source coverage130fields/270occurrences, both runtime profiles remain.
This updates the implementation order within W0/W1/W4, not their readiness gates.

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
