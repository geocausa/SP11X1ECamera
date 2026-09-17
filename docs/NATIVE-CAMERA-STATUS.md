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
