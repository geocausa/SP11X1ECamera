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
   source. Add proper monochrome processing within libcamera, with packing,
   padding, brightness and boundary tests; do not label mono data as Bayer.
3. **Sensor integration is incomplete.** Add the VD55G0 gain helper and measured
   black-level policy, characterize control delays, and report board orientation
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
E004fb; never reuse it. Start a fresh identity for the next hardware run.
Keep Golden the permanent default. No protected SecureISP runtime activation.
Native code is in `src/front-ir-vd55g0/native/`; experiment results are under
`experiments/E004-front-ir-vd55g0/`. Proprietary firmware and raw captures stay
local and ignored. Only exact intended source/evidence paths are staged.
