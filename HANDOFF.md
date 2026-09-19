**2026-09-19 E004gh original Windows ARM64 TIMER HANDLER CPU emulation PASS, HARDWARE STILL BLOCKED:** Ran SHA-pinned Windows qcpmic8380.sys instructions at RVA 26d50 inside offline AArch64 Unicorn VM, mocking only Windows logging and PMIC masked writes. Under explicit synthetic requests the handler encodes nominal 10ms→80, 200ms→93, 1280ms→ff; requested ee3e/ee41 for logical LED1 and ee3f/ee40 for other channels, plus an additional ee40 clear under this synthetic fixture. Five individually injected mocked-write failures confirm original paired-write error handling and abort before next logical LED. Archived consumed E004fx idle 93 matches the Windows *software encoding* for a nominal 200ms request; it does not prove active Windows timer state, electrical enforcement or physical optical pulse duration. E004gb Windows boot/KD/camera one-shot NOT repeated. Normal and negative offline tests PASS; no PMIC, camera, Windows boot, emitter or Golden mutation. E004fs/E004ge independent current/irradiance, true pulse and autonomous fault-off remain BLOCKED; see E004gh README/RESULT.

**2026-09-19 E004gg ORIGINAL WINDOWS ARM64 OFF-INSTRUCTION EMULATION PASS, NO HARDWARE:** Resumed after stream interruption and confirmed E004gf commit `55b026524e340dc597d7df83ffc9f3469c725ff3` synchronized on protected SP11 Golden. New offline Unicorn CPU execution maps byte-for-byte SHA-pinned Windows flash and PMIC ARM64 PEs into disposable in-memory VMs; intercepts only messaging and mocked PMIC helpers. Original flash OFF wrapper emits command 802f0fc8/payload [0,0,0,0]. Original PMIC callback requests ee46 mask 80 clear before ee4e mask 0f clear, and on a mocked failed FIRST request skips the second; second failure returns an error after both requests. LED1 ON fixture produces ee46=80 then ee4e=09. Nonzero flash-wrapper args revealed [0,1,0,1] packing, correcting an initial test expectation; all rerun negative tests PASS. Correlates, but does not REPEAT, consumed E004gb normal Windows KD evidence. This is REAL Windows CPU instruction emulation with MOCKED hardware services, NOT a Windows boot, real bus fault, actual LED off or independent timer/current/irradiance safety proof. No camera/Windows/KD, PMIC/emitter, boot, Golden or login modification. E004fs/E004ge stay BLOCKED; see E004gg README/RESULT.

**2026-09-19 E004gf Windows ARM64 STATIC + ARCHIVED-LIVE shutdown diagnosis PASS (NO NEW WINDOWS BOOT):** SHA-pinned installed `qccamflash8380.sys` + `qcpmic8380.sys` ARM64 disassembly confirms Windows type-0 OFF issues a mode command then an OFF command; the PMIC OFF callback requests module ee46 disable *before* channel-mask ee4e clear and short-circuits if the first write fails. Previously consumed E004gb live trace independently agrees with successful normal module-before-channel requests; its trace was only re-VERIFIED OFFLINE, not repeated. A four-case OFFLINE software fault model and eight static-instruction negative checks pass: failed module-off skips the channel-off request; neither static instructions nor a simulated bus failure measures the real electrical LED outcome. Uninstalled Linux rollback patch still does not guarantee autonomous fault-off. No camera, Windows, KD, PMIC, emitter, boot or Golden changes; E004fs/E004ge hardware safety gate remains BLOCKED. See E004gf README/RESULT.

**2026-09-19 E004ge physical illumination evidence gate — BLOCKED, PHYSICAL ACTION REQUIRED:** Rechecked Golden SP11 camera-idle state; SP11 USB inventory shows only root hubs, SP7 read-only PnP inventory only built-in cameras and no identifiable calibrated optical/electrical measurement instrument. No project dataset establishes the actual LED current/irradiance, optical pulse duration, autonomous host-halt/stuck-high/PMIC-failure OFF or exact hardware routing. E004ge adds an OFFLINE fail-closed five-category checklist, with negative tests PASS; even all asserted flags require independent expert measurement review, NEVER automatic emitter authorization. Qualified near-IR optical/electrical lab work on the exact SP11 is now the required physical action before Linux illumination. No new Windows/KD, camera, PMIC, emitter, reboot or login work; E004gb remains consumed, E004fs stays BLOCKED. See E004ge README/RESULT.

**2026-09-19 E004gd OFFLINE FULL-CHAIN IR TELEMETRY PASS:** After E004gc, independently reran all 16 immutable E004fe *sensor-generated pattern* RGB888 frames through the real RGB888→NV12 bridge, maintained HLOS parity worker and E004gc signal diagnostic on protected Golden with no device I/O. The processed buffer reproduces SHA256 `ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df`; every frame's six telemetry values match independent Python reference, and corruption in the last RGB/NV12 frame rejects the whole batch without partial output. Normal and ASan/UBSan tests PASS. These are generated patterns, NOT ambient optical images or faces; E004fu's optical buffers were not retained. E004gb/earlier identities remain consumed. No Windows/KD, camera, PMIC, emitter, login or reboot activity; E004fs physical current/irradiance, real pulse duration and autonomous host-crash/stuck-trigger shutdown remain BLOCKED. See `experiments/E004-front-ir-vd55g0/e004gd-offline-archived-pattern-telemetry/` README and pinned verifier.

**2026-09-19 E004gc OFFLINE HLOS signal diagnostics PASS:** A new strict 1..16-frame 644×604 neutral-NV12 diagnostic emits only aggregate per-frame luma, percentile, clipping and neighbor-contrast metrics after full-batch validation. Synthetic fixtures and ASan/UBSan PASS, existing HLOS Windows-oracle and 16-frame archived-pattern regressions PASS. This does not analyze E004fu's discarded optical frames and does not demonstrate face detection or recognition. No camera, LED, Windows, login/PAM or Golden mutation. See E004gc README/RESULT; E004gb is consumed; E004fs physical electrical/optical cutoff/current gate stays BLOCKED.

# SP11 Camera Linux Parity Handover — 2026-09-11 reconciled R27 frontier

**2026-09-19 E004gb Windows KDNET flash module/channel trace — PASS, CONSUMED, GOLDEN RETURNED:** Original KD dry and observer logs, Windows capture and single-use SP7 markers are archived byte-for-byte in `E004gb/evidence/ORIGINAL-WINDOWS-LOGS.zip` SHA256 `330afa1f20fc2714d8e8a172c6d754dbb4d32e5dc1a41e174825bb2c0eb0bfbf`. Live KD interpreter dry validated 11 target registers (including ee46 and ee4e), 8 excluded registers. During ONE normal bounded Windows OEM 12-frame IR preview, KD recorded 11 paired PMIC masked-helper read/write calls with return code 0: module ee46 00→80 then 80→00, channels ee4e 00→09 then 09→00, trigger pair ee4a/ee4d 01→05. No ee3e..ee41 timer register access hit these selected hooks in this session (NOT proof of timer state). These are Windows SOFTWARE helper requests and post-buffer values, NOT physical LED pulses, PMIC write readback, current/irradiance or independent fail-safe cutoff. Breakpoints cleared; SP7 KD stopped; SP11 rebooted into protected Golden boot `6ca88e8c-525b-4944-bffa-037a4337a01d` with original EFI BootOrder/GRUB FullIO entry, flash DT disabled and camera-idle guard PASS. `E004gb/verify_result.py` re-verifies original hashes and Golden return OFFLINE; `test_verify_result.py` rejects six tampered fixtures. **Never re-run E004gb or prior E004ga/E004fp/E004fr one-shot identities. Native Linux IR emitter OFF; E004fs physical optical safety/fault cutoff gate remains BLOCKED.** Next: independently establish current/irradiance, physical pulse width and autonomous host-crash/stuck-trigger shutdown; meaningful offline HLOS face-matching work can proceed separately without emitter or PAM/login installation.

**Historical E004gb preparation (superseded):** E004gb was subsequently completed, original evidence archived, and its one-shot identity consumed. Do NOT stage or repeat the Windows boot, KD hooks or OEM capture. See the current E004gb result above and the pinned offline verifier.

**E004ga Windows KDNET one-shot — ABORTED / CONSUMED, NO CAMERA PREVIEW (2026-09-19):** Live KD dry validation skipped BOTH required enable registers `ee46` and `ee4e`; earlier static checks did not execute WinDbg/MASM predicate semantics. No KD observer hooks armed, no OEM preview or new PMIC trace collected. SP7 KD breakpoints cleared, target resumed, Windows rebooted, KD job stopped. SP11 has returned to Golden boot `c017bcd7-4e86-45ed-8453-224646b6cc8e`, BootOrder/GRUB/camera-idle guard PASS; local HEAD matches origin. E004ga Windows identity is consumed and MUST NOT be rerun. SP7 original KD log SHA256 `3229becbccffc774c9b2a4026661278135fff1f6ab5dd36f557f52e75c8e4ace` (7539 B), located in SP7 E004GA stage; see E004ga/evidence/ABORTED.json and verify_abort.py. E004gb later passed live KD target/exclusion validation and completed; do not repeat either consumed experiment. E004fs IR emitter gate remains BLOCKED.


**E004ga fresh Windows KDNET enable/channel masked-RMW trace OFFLINE PREPARED / NOT ARMED (2026-09-19):** E004ga extends E004fp masked-PMIC observer with module enable `ee46` and channel mask `ee4e` alongside timers `ee3e..ee41`, triggers `ee4a..ee4d` and common `ee67` in a separately numbered normal OEM Windows IR preview (12 frames/5s, no images saved). Generator uses the FRESH installed qcpmic driver base and leaves target broken for dry/parser/breakpoint verification before explicit resume. Static test PASSED; no Windows boot or capture yet. Commit/push exact prepared E004ga scripts before BootNext and confirm SP7 KD+recovery, Golden clean/idle. Bounded Windows software requests are not independent optical safety authority; native Linux emitter remains off.\n\n**E004fz Linux flash error rollback (2026-09-19, OFFLINE PASS/UNINSTALLED):** The original isolated `qcom_flash_strobe()` could return from a fault after module-enable without a combined shutdown attempt. A new source-only patch `0004-qcom-flash-best-effort-error-disarm.patch` (after prior uninstalled `0003`) attempts channel disarm followed by module disable on all six failure stages, logs failures and preserves the initiating error. The actual modified C dispatcher passed ASan/UBSan fault injection including simulation of an SPMI bus failure with hardware potentially still ON, plus isolated Golden-kernel W=1 build. **A failed bus write can still leave emission ON; this patch is NOT an autonomous shutdown and must not be installed as an emitter-activation justification.** No physical current/pulse/irradiance or independent fault cutoff has been proven; E004fs remains blocked. KDNET/SP7 is available for a fresh, bounded Windows shutdown request/trace when useful, but is not a substitute for physical safety verification. See E004fz README and evidence/RESULT.json.\n\n**2026-09-19 E004fy read-only flash enable/trigger snapshot PASS, CONSUMED:** Six named idle PM8550/SID1 register bytes were read exactly once on protected Golden: module 0xee46=0x00 (bit7 clear); trigger selectors 0xee4a..0xee4d=0x01 each (Linux source software/level/active-high bits); channel mask 0xee4e=0x00 (all channels disabled). E004fx idle timer 0x93 configuration therefore did NOT imply an enabled flash output in this Golden state. Prior separate Windows E004fp preview observed selectors 0xee4a and 0xee4d change 0x01→0x05 for LED1 channels 1 and 4; do not attribute that transition to this idle Linux read. E004fy consumed before single bounded six-register passive observation, no PMIC writes, emitter or camera activation. Golden boot/EFI/GRUB/camera idle PASS; offline verifier `E004fy/verify_result.py` hash-pins evidence without re-reading hardware. **NEVER rerun E004fy.** E004fs optical current/pulse/independent host-fault shutdown still unproven; IR emitter stays OFF. KDNET/SP7 may be used for a separately staged Windows question when necessary.


**E004fx passive Golden timer-state read PASS / CONSUMED (2026-09-19):** One bounded 36-byte read of the precisely mapped PM8550 SID1 idle flash timer registers yielded `0x93` in all four `0xee3e..0xee41`. This is a config-byte observation only; the Windows handler would conditionally decode `0x93` as a nominal 200 ms request, NOT a measured LED pulse, physical cutoff or proof of an enabled module/channel. No PMIC writes, camera, flash driver installation, IR light or reboot occurred. Golden flash DT remains disabled, camera-idle and EFI/GRUB checks PASS. E004fx is consumed; NEVER re-run `read_once.py` or `prepare.py`. See E004fx `evidence/VERIFIED.json` and `verify_result.py`. Next distinct observation: module/channel enable and trigger registers; E004fs independent physical safety gate remains BLOCKED.

**E004fw Golden flash-PMIC mapping (2026-09-19):** Live read-only device-tree/SPMI metadata identifies the only flash-controller node as disabled PM8550 flash LED at SPMI `0-01`, base `0xee00`; the four-channel timer-register address candidates are `0xee3e..0xee41` on that controller. PMC8380 PMIC DT nodes on SIDs 3–6 are not the flash-controller parent. E004fw explicitly read NO PMIC register values and did not activate any hardware; 12 synthetic fail-closed mismatch tests pass. This does NOT prove physical wiring, timer state, safe LED power, or fail-safe shutdown. Next is a **fresh, narrowly bounded passive timer-register snapshot design** targeting the correctly identified node, without whole-regmap dumps or illumination. E004fs remains blocked.

**E004fv uninstalled source patch (2026-09-19):** The pinned original Linux PMIC timer encoder differs by one 10 ms step from the recovered Windows PMIC software handler. The new source-only patch 0003 aligns the Windows request→register-byte mapping across all 1271 allowed integer-ms values; actual patched C sanitizer tests and an isolated W=1 Golden-header module build passed. This is NOT a measured physical timer or independently safe LED cutoff: patch is NOT installed, IR emitter remains OFF, and E004fs hardware safety gate remains BLOCKED. See E004fv README/RESULT.json. The old text describing a 1270 ms encoded ceiling reflects where the uncorrected Linux formula first saturates; the Windows software handler maps 0xff to nominal 1280 ms, not a measured physical cutoff.

**E004fs source-level timer review (2026-09-19):** Hash-pinned Linux isolated flash driver code programs timer before arm but defaults to 1000 mA (versus Windows' observed 700 mA request), advertises up to 1280 ms while clamping the 7-bit encoded maximum to 1270 ms, and has 10 ms timer granularity. Windows' 1955 exposure lines under the *separate Linux* clock would hypothetically be 17.0494 ms, not an observed pulse. No PMIC timer readback, physical current/irradiance, or autonomous stuck-strobe/host-crash shutdown proof exists; **emitter activation remains blocked**. Offline checker `e004fs-emitter-timing-timeout-offline-review/verify_timeout_readiness.py` and six negative-path tests pass. Do not treat an E004fs offline PASS as emitter authorization.

**E004fu 2026-09-19 result:** Fresh one-shot test_pattern=0 ambient optical capture passed 16/16 RGB888 bridge-to-HLOS frames, clean stop/suspend/kernel and Golden return. Output remains very low contrast (steady mean 38.6–39.7/255); no usable face image or biometric matching proved. Image buffers and image hashes were not retained, and the temporary candidate was retired. E004fu is consumed; emitter remains OFF. See E004fu README, numeric RESULT.json and verify_result.py.

> **Current frontier — 2026-09-19 / E004fu live unilluminated optical HLOS capture PASS but low-contrast image; Golden restored, E004fs emitter authority next:** Native Linux IR remains unilluminated. E004fr recorded 114 contiguous sensor register writes during one 12-frame Windows IR preview, including 16 coarse-exposure programming groups (32 through 1955 lines) and frame-length values of 1955/2000 lines. KD and Windows original reports are archived with hash-checked offline verification. This is software write-observation evidence, not an electrical pulse-width/current measurement or proof of PMIC fail-safe timeout. E004fq remains a separately consumed, aborted attempt. The unsigned HLOS IR worker has only offline pixel-processing and archived-pattern format-bridge validation, not face authentication.


**Latest E004fq/E004fr update (2026-09-19):** E004fq Windows one-shot idle target/skip validation passed, but its generated breakpoint callback was rejected by KD's `Malformed string` parser before any camera capture. No IR preview or sensor write trace was collected. KD breakpoints were cleared, SP11 rebooted to protected Golden Ubuntu, unchanged boot order and camera-idle overlap guard verified. E004fq is consumed and cannot be retried. E004fr subsequently passed on a separate fresh Windows boot: KD accepted the observer, 12 IR frames acquired, 114 contiguous sensor register writes recorded, and SP11 returned to protected Golden. The current gate is E004fs offline pulse/current/PMIC timeout review before considering a bounded Linux emitter experiment; Linux emitter remains OFF. The independent HLOS bridge and IR pixel worker have now also passed **E004ft: one fresh live 16-frame generated-pattern camera capture processed in ordinary Linux userspace**, with clean camera stop, sensor suspension and Golden return. This establishes live camera-to-worker transport only, **not** unilluminated optical quality, liveness, face authentication or IR emitter safety. E004ft is consumed and retired; do not reuse it.

## Current continuous-control frontier — GV consumed/adjudicated PASS

GT limited redundant-write policy and GU helper integration are durable. GV then consumed exactly one fresh R27 stream. Six control ioctls G1..G6 succeeded, but because G4..G6 were bit-identical to current G3, V4L2 `cluster_changed()` suppressed those three before driver `.s_ctrl`. Thus the live run produced only bootstrap + G1..G3 sensor transactions and **no new post-G3 hardware write**.

The initial verifier expected one hardware transaction per successful ioctl and stopped on that incorrect assertion. After immediate archive, protected Golden return and candidate retirement, the verifier was corrected offline. The immutable evidence passes as `PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27`. No same-boot retry occurred.

GY then consumed exactly one fresh R27 one-shot and **PASSed**. A guarded G4 sentinel changed only digital gain 1471→1472 (+0.06798%), produced exactly one new post-G3 IMX681 hardware transaction, and G5..G26 stayed shadow-only. Golden return and retirement passed; no retry. The later native AEC tuples G5..G27 did not move, so GY proves transport/lifecycle but not production-native changed feedback.

GZ then closed offline response-threshold analysis: the tiny GY signal is below normal luma variability, and production native control is cap-censored G3..G27. HA closes a fail-closed one-native-write policy and HB integrates it at the exact DQBUF release boundary.

HC then consumed exactly one fresh R27 observer stream and returned **PASS_NO_CAP_RELEASE**. All eligible G4..G24 sources remained cap-active; G25/G26 were forced shadow by the evidence horizon; no post-G3 native write was issued. Hardware evidence is exactly bootstrap + startup G1..G3. STREAMOFF, kernel health, Golden return and candidate retirement passed with no retry.

HD closes that offline strategy. GO/GS/GV/GY/HC all end deeply cap-censored (>8× cap at G27), so merely extending the same static scene is not evidence-based. Windows DM proves a genuine below-cap ordinary preview regime (R7 ~0.917× cap; R8 first clamp), but not a transferable numeric lux threshold.

The next post-G3 native feedback live attempt therefore requires a **fresh identity plus a substantially brighter diffuse real scene**; HC must never be reused and no synthetic sensor delta is authorized. Until that physical condition is available, continue production integration and repeated-stream robustness work offline/safely.

HE/HF/HG/HH/HI/HJ production consolidation and bounded RGB handoff remain accepted without Golden promotion. **Front IR is now natively live through E004fe, and E004fn closes the normal Windows flash request sequence.** Linux has stock-libcamera capture and 16/16 processed monochrome frames; Windows requests 700 mA on logical LED1, selector 0, hardware/level/active-high trigger mode, arm then disable. Illumination on Linux remains unauthorized pending register-level PMIC and pulse-policy evidence.

**Next gate: E004fq actual VD55G0 sensor-exposure/strobe-envelope and PMIC-timer authority.** E004fp is consumed PASS and Golden-restored. The PMIC register writes are now live-proven; next determine the physical sensor exposure/strobe relationship and whether any separate timeout/timer programming is active or required. Prefer static authority first and keep native Linux illumination off.

---

## RECONCILED CURRENT FRONTIER — authoritative over the historical handoff below

Reconciled 2026-09-11 after a possible UI/turn overlap. Machine/Git/evidence state is authoritative, not visible chat chronology.

- durable checkpoint: `6985bb6f5993232df3483000581196e2a370acdc` (`camera: close R25-R27 offline authority`)
- branch: `experiment/e003-front-imx681-cphy`; local and origin matched at reconciliation
- GC: consumed Linux R5-R21 live PASS; archive manifest revalidated
- GI: consumed Linux R5-R24 live PASS; 24 QC10C frames; archive manifest revalidated
- GJ: consumed one-stream Windows R4-R27 combined AWB + Tintless/LSC PASS; 24/24 AWB bit-exact and 24/24 LSC byte-exact; archive manifest revalidated
- GK: offline R25-R27 PASS at `6985bb6`; R5-R24 regresses 20/20 against GI and R25-R27 is deterministic 3/3
- safe machine state at reconciliation: protected FullIO v19c Golden, empty `next_entry`, no camera nodes/modules, no camera process

GL, GM and GN are durably closed and pushed. GO then completed exactly one fresh R5..R27 Linux stream and **PASSed**: 27 QC10C frames, native AEC G1..G27, producer/IQ R5..R27, exactly three physical sensor writes, clean STREAMOFF and kernel health. SP11 returned to protected Golden and the GO candidate was retired.

After a GO PASS, stop mechanically extending R30/R33/etc. Pivot to continuous delayed sensor-control feedback, control-to-statistics timing, repeated/long streaming, production integration, then VD55G0 IR bring-up.

Continuous-control work is now closed through GP timing authority PASS, GQ continuous two-slot ring scheduler PASS, GR continuous helper integration PASS, and **GS live shadow scheduler PASS**.

GS consumed exactly one R27 stream: G1..G26 scheduler releases all hit their exact live boundaries, only G1..G3 performed physical sensor ioctls, G4..G26 produced 23 shadow releases, and kernel evidence contains exactly one bootstrap plus three real control transactions. STREAMOFF, Golden return and candidate retirement all passed.

Current frontier beyond the historical block: GY changed-transport PASS; GZ cap-censor analysis PASS; HA one-native-write policy PASS; HB helper integration PASS; HC prepared/unarmed/prearm PASS. The next live action is one HC observer stream only after its exact candidate is durably committed/pushed.

Before every meaningful mutation run `tools/camera-overlap-guard.sh` and inspect the intended stage path. If unexpected evidence exists, audit it first. Any one-shot attempt that may have started is consumed until proven otherwise. Never same-boot retry and never reuse a consumed identity.

The older FU/R18 handoff below is retained as historical evidence only.

---

## Resume command / first instruction for the next chat

Continue SP11 Camera from this HANDOFF on branch `experiment/e003-front-imx681-cphy`.

Current durable live-result checkpoint immediately before this handoff:

`aeb1b0df8876f54714380a028104dd50eddc6d2e`
(camera: record FU eighteen-frame live pass)

First verify the exact Git + Golden state below.

SP11 is reserved for Camera. Do not touch HostFabric work.

Do not reuse consumed one-shot identities. FU is consumed and retired.

Do not jump directly to unrestricted continuous streaming. The new frontier is bounded authority/work beyond R18.

---

## 1. Exact durable Git state

Repository:

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:

`experiment/e003-front-imx681-cphy`

Durable live-result checkpoint:

`aeb1b0df8876f54714380a028104dd50eddc6d2e`

Origin matched this checkpoint immediately before rewriting HANDOFF.

Important recent checkpoints:

- `c30a37a` — close Windows R18 Tintless/LSC authority
- `6328e59` — authorize bounded R16–R18 IQ content
- `7ed9347` — stage G15 publisher and R18 producer
- `767248e` — stage authorized eighteen-frame R18 transport
- `d572679` — stage FU eighteen-frame live candidate
- `9718a59` — make FT result repeatable
- `aeb1b0d` — record FU eighteen-frame live pass

Many old untracked historical artifacts across E002/E003 remain intentionally. Do not mass-clean them.

---

## 2. Exact current SP11 machine state

Hostname:

`SP11X1e`

OS/kernel:

- Ubuntu 26.04 LTS
- `7.1.5-sp11-render-parity-v4+`
- ARM64 / aarch64

Current boot is protected persistent Golden Linux.

Golden boot ID after FU:

`5c74a60a-e805-45b6-bdd5-983d66aaad6a`

Golden kernel cmdline boots from:

`/boot/sp11-7.1.5-audio-fullio-v19c/`

GRUB environment:

`saved_entry=sp11-audio-fullio-v19c`
`next_entry=`

Current Golden state:

- candidate qcom_camss absent
- candidate imx681 absent
- ov13858 absent
- no /dev/video*
- no /dev/media*

FU candidate boot artifacts are retired:

- `/etc/grub.d/99zv_sp11_camera_e003i_fu_eighteen_frame_r5_r18` absent
- `/boot/sp11-7.1.5-camera-e003i-fu-eighteen-frame-r5-r18` absent
- FU menu ID absent from generated grub.cfg
- Golden saved_entry unchanged

---

## 3. Windows/component authority through R18

### FH — recovered Windows AWB authority through R18

Status:

`PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT`

FH provides AWB/GainAdj differential authority through R18.

### FP — fresh Windows R4–R18 Tintless/LSC oracle

FP performed exactly one fresh Windows front-camera stream and captured R4..R18:

- Tintless stats: 0x12bec bytes/request
- trigger: 0x100 bytes/request
- final LSC staging: 0x18a0 bytes/request
- 15 entry hooks
- 15 post-stage hooks

Sequential native clean-room replay:

`15/15 byte-exact LSC0/LSC1/LSC2/GIC`

Bank parity:

`1,0,1,0,1,0,1,0,1,0,1,0,1,0,1`

FP returned Golden cleanly.

FP Windows evidence ZIP SHA256:

`f20d931b92cabb2533aaeea9cd205b63af21ee9cbc7791c91a07a52961393197`

FP Linux archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fp/windows-r4-r18-20260911`

FP final archive MANIFEST.sha256 file SHA256:

`290c0b238ff26e6f21f42626a6b40f8e18154a9ae18b1a22890eba8448c028a2`

### FQ — R16–R18 authority join

FQ combines:

- FO deterministic R16–R18 composition from immutable FN G13/G14/G15 continuation inputs
- FH Windows AWB authority through R18
- FP Windows Tintless/LSC authority through R18
- EB post-R6 stable GTM law

Status:

`PASS_OFFLINE_R16_R18_CONTENT_AUTHORIZED`

This is component differential authority, not a same-scene whole-capsule Windows oracle.

---

## 4. Offline bounded R18 stack

### FR — G1..G15 compiled C gain publisher

Status:

`PASS_OFFLINE_G1_G15_C_PUBLISHER`

Properties:

- exact existing 24-byte ABI
- request = generation + 3
- G1..G15 accepted
- G16 rejected
- only source delta from FK is upper bound 12 -> 15

gain-feed.c SHA256:

`c8b03597649ec5e1a6e5b62110eb61ab7cd6a29073a3ecdcf9194f439b410627`

### FS — live-capable R5..R18 producer

Status:

`PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION`

Offline proof:

- source: immutable FN G1..G15 paired stats + CQ gains
- R5..R15 reproduce the real FN live capsules 11/11 byte-exact plus key metadata
- R16..R18 match FQ-authorized hashes exactly
- two independent FS runs are deterministic
- live-capable scheduler/control/submission path preserved

Authorized R16–R18 capsule hashes:

- R16: `78b40962f9eb72a27a674050278c5cf309eff4f2d635952bd7e3e52e83188588`
- R17: `553803b3575bcebdd1dbbdf71bf68db8a82326a8a3dea3706cf2f674af120012`
- R18: `0b8e01730173acd8efe18ff4f459d450a98e436531b29c486531862eeaac9427`

### FT — eighteen-frame transport

Status:

`PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT`

Proof:

- CAMSS W=1 PASS
- helper Werror PASS
- 18-frame buffer cycle:
  `0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1`
- paired AEC/stats generations G1..G18
- CQ gain publisher generations G1..G15
- IQ consumption requests R5..R18
- physical sensor-write schedule remains exactly sources G1/G2/G3 at boundaries G2/G3/G4
- scheduler unit test PASS G1..G18 with exactly 3 writes
- no FT camera runtime

Pinned generated source hashes:

- CAMSS:
  `a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c`
- helper:
  `24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce`
- schedule header:
  `092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf`

Important verifier note:

FT originally recorded a temporary-path-dependent qcom-camss.ko hash in RESULT.json. That non-authoritative field was removed. Two consecutive FT verifier runs now produce byte-identical RESULT.json with SHA256:

`915acb4d3130abb7a2cd2606ab13738f1c71f9734523d25516bbcd6cef7a5aa5`

---

## 5. FU live result — consumed PASS, never reuse

Directory:

`experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fu-eighteen-frame-live-r5-r18`

Durable pass record:

`ATTEMPT1-PASS.json`

Retirement record:

`RETIRE.txt`

Status:

`PASS_CAPTURE_FU_EIGHTEEN_FRAME_R5_R18`

Candidate HEAD:

`9718a59497a4b0783e358857167bbba4eba6cc28`

Candidate boot ID:

`3bb74578-1f93-4125-9b11-9b1a75efa4a2`

Exactly one FU camera stream attempt occurred.

No same-boot stream retry occurred.

The helper-consumed guard was created before streaming.

Helper result:

`HELPER_RC=0`

Transport result:

- exactly 18 QC10C frames
- DQBUF order:
  `0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1`
- native AEC accepted G1..G18
- paired TLBG + STATS3A captured G1..G18
- R5..R18 composed and submitted live
- kernel IQ consumption observed through R18
- STREAMOFF_OK
- bounded eighteen-frame kernel completion observed

Physical sensor writes:

exactly 3

Schedule:

- G1 released after completed G2 -> expected effect G4
- G2 released after completed G3 -> expected effect G5
- G3 released after completed G4 -> expected effect G6
- no later physical writes

Producer deadline:

all R5..R18 pipelines < 33.333333 ms

Maximum:

`28.516746 ms`

R18 live:

- capsule SHA256:
  `6714b533f3c866d41ceda8de69b1fd29ca3da6fa28d6ff775851c02ed2dc6ca2`
- AWB calibration slot 5
- AWB triangle 25

Kernel health:

PASS

FU does not claim unrestricted continuous AEC or an infinite scheduler.

---

## 6. FU external evidence

Archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fu/attempt1-pass-eighteen-frame-20260911T1822`

Final archive MANIFEST.sha256 file SHA256:

`a02b7b0916c1a5b56e2ce2d0555ff1ccd2904193bf63d7edf9448a54868a6d9b`

Compact evidence hashes:

- ATTEMPT1-PASS.json:
  `2ba823f10acb589ad4c849072a9b8b0be6ae17654675f83453d23098bd09c1a4`
- RUN.txt:
  `86186682b8f9c1bbef70436506979c01ca3cba9b1d5984ef9bf9602051b3cffb`
- LIVE-RESULT.json:
  `89d415282c23c0b5fbcdcd46f248b6c359c1839c24e6c0824e46f416033b0189`
- producer RESULT.json:
  `cbd3cb7f8c39f1f46fcfef91e5cdb446ae98cc8292c180e6df17e44c35c6465d`
- DMESG.txt:
  `0d31c7f8296c4c2e685d13166314c923f38c160e8dd012ebcb94e35d397e66b4`
- HELPER-CONSUMED.marker:
  `063171e5d17ed7b2889cf78eeec394a6c110e88a1b70a5d3eb5aa02c16b4d73f`
- GOLDEN-RETURN.txt:
  `02bcd593c27c4c4b843dbb326399fff584e0fc025b86ffc4a36cdda6478bd659`
- RETIRE.txt:
  `37edcf38af1ba7cd632d47478eb08f398dad6db2421e4bf9a3975ff6c6928c12`

---

## 7. Fresh continuation inputs now available

FU captured paired Linux statistics through G18.

FS consumed G1..G15 for R5..R18.

Therefore FU preserves fresh continuation inputs not yet consumed by the live IQ producer:

- G16 STATS3A/TLBG -> natural source for R19
- G17 STATS3A/TLBG -> natural source for R20
- G18 STATS3A/TLBG -> natural source for R21

Native AEC also produced CQ residual ISP gain observations through G18 in RUN.txt.

Use the immutable external FU archive as the source. Do not modify archived evidence in place.

---

## 8. Current authority boundary beyond R18

AWB/GainAdj:

- FH Windows differential authority stops at R18.
- R19..R21 are not yet Windows-authorized.

Tintless/LSC:

- FP Windows clean-room differential authority stops at R18.
- R19..R21 are not yet Windows-authorized.

GTM:

- EB's post-R6 stable output law remains available, but any new use must record that inference explicitly.

Producer mechanics:

- fresh Linux continuation inputs G16..G18 exist.
- the current production algorithms can be exercised offline.
- this does not authorize R19..R21 content by itself.

Therefore **both AWB/GainAdj and Tintless/LSC authority must be extended beyond R18 before any R19..R21 Linux live candidate is created.**

Do not silently extrapolate FH or FP past R18.

---

## 9. Recommended next frontier — bounded R19..R21 offline/Windows authority first

Suggested sequence:

1. Create an offline-only continuation/composability stage from immutable FU G16/G17/G18:
   - G16 -> R19
   - G17 -> R20
   - G18 -> R21
2. Prove deterministic composition and preserve exact regression to the real FU R5..R18 live capsules.
3. Extend Windows AWB/GainAdj authority through R21.
4. Extend Windows Tintless/LSC authority through R21.
   - Prefer one fresh bounded Windows stream only if the existing proven hooks can safely collect the needed evidence together.
   - Otherwise keep AWB and Tintless/LSC as separate bounded one-stream authority captures.
5. Join R19..R21 component authority explicitly.
6. Only after authority closes:
   - extend compiled C gain publisher through G18
   - extend live-capable producer through R21
   - extend bounded transport to 21 frames
   - verify everything offline
   - create a fresh one-shot Linux live identity
7. Still do not jump directly to unrestricted continuous/infinite streaming.

Suggested next labels if free:

- FV — offline R19..R21 continuation/composability
- FW — Windows AWB authority through R21
- FX — Windows Tintless/LSC authority through R21
- FY — R19..R21 authority join
- FZ — G1..G18 compiled publisher
- GA — R5..R21 producer
- GB — twenty-one-frame transport
- GC — fresh one-shot twenty-one-frame Linux live candidate

Verify labels are unused before creating them.

---

## 10. Closed / historical stages — do not rewrite history

Important closed stages include:

- EM — PASS_OFFLINE_R7_R9_COMPOSITION
- EN — historical R5-R9 producer integration; preserve its stale-publisher verifier gap
- EL — PASS_OFFLINE_JOIN
- ES — PASS_OFFLINE_NINE_FRAME_TRANSPORT
- EJ/EK — front AWB OTP source proven natively on Linux
- EB — Windows GTM authority / post-R6 stable law
- ED — Windows Tintless/LSC authority through R12
- FH — recovered Windows AWB authority through R18
- FI — Windows Tintless/LSC authority through R15
- FJ — R13–R15 content authority join
- FK — G1..G12 C publisher
- FL — R5..R15 producer
- FM — fifteen-frame transport
- FN — consumed live PASS through R15
- FO — R16–R18 continuation/composability
- FP — consumed Windows R4–R18 Tintless/LSC PASS
- FQ — R16–R18 content authority join
- FR — G1..G15 C publisher
- FS — R5..R18 producer
- FT — eighteen-frame transport
- FU — consumed live PASS through R18

Consumed Linux one-shot identities include:

EA / EO / EQ / ER / ET / EV / EZ / FF / FN / FU

Never reuse a consumed identity.

---

## 11. Safety rules that remain mandatory

- Golden default is sacred:
  `saved_entry=sp11-audio-fullio-v19c`
- candidate boots must be one-shot via next_entry / grub-reboot
- one camera stream attempt per candidate boot maximum
- on any failure: preserve evidence, no same-boot stream retry, whole-machine reboot to Golden
- never reuse consumed candidate identities
- every new live attempt needs a fresh identity
- preserve raw external evidence and checksums
- do not mass-clean historical untracked artifacts
- do not claim continuous AEC from bounded tests
- do not touch HostFabric work in this continuation
- do not extend Linux live IQ past the proven content-authority boundary without a fresh offline/Windows authority gate

---

## 12. Human summary

The Linux front-camera stack now has a successful bounded live run through **R18**.

FU completed eighteen real QC10C frames, captured paired 3A/TLBG through G18, submitted dynamic IQ R5..R18, performed only the original three delayed physical IMX681 writes, cleanly STREAMOFF'd, passed kernel-health validation, and returned to Golden. The consumed candidate was retired.

Fresh continuation inputs G16/G17/G18 now exist for natural R19/R20/R21 work. The blocker is no longer Linux transport or producer mechanics; it is authority beyond R18. Both Windows AWB/GainAdj and Windows Tintless/LSC differential authority currently stop at R18.

The next safe move is therefore offline R19..R21 continuation plus bounded Windows authority extension before another Linux live candidate.
