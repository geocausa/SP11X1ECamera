# Native camera stack status — 2026-09-16

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
