# SP11 Camera Linux Parity Handover — 2026-09-11 reconciled R27 frontier

## Current continuous-control frontier — GV consumed/adjudicated PASS

GT limited redundant-write policy and GU helper integration are durable. GV then consumed exactly one fresh R27 stream. Six control ioctls G1..G6 succeeded, but because G4..G6 were bit-identical to current G3, V4L2 `cluster_changed()` suppressed those three before driver `.s_ctrl`. Thus the live run produced only bootstrap + G1..G3 sensor transactions and **no new post-G3 hardware write**.

The initial verifier expected one hardware transaction per successful ioctl and stopped on that incorrect assertion. After immediate archive, protected Golden return and candidate retirement, the verifier was corrected offline. The immutable evidence passes as `PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27`. No same-boot retry occurred.

GY then consumed exactly one fresh R27 one-shot and **PASSed**. A guarded G4 sentinel changed only digital gain 1471→1472 (+0.06798%), produced exactly one new post-G3 IMX681 hardware transaction, and G5..G26 stayed shadow-only. Golden return and retirement passed; no retry. The later native AEC tuples G5..G27 did not move, so GY proves transport/lifecycle but not production-native changed feedback.

GZ then closed offline response-threshold analysis: the tiny GY signal is below normal luma variability, and production native control is cap-censored G3..G27. HA closes a fail-closed one-native-write policy and HB integrates it at the exact DQBUF release boundary.

HC then consumed exactly one fresh R27 observer stream and returned **PASS_NO_CAP_RELEASE**. All eligible G4..G24 sources remained cap-active; G25/G26 were forced shadow by the evidence horizon; no post-G3 native write was issued. Hardware evidence is exactly bootstrap + startup G1..G3. STREAMOFF, kernel health, Golden return and candidate retirement passed with no retry.

HD closes that offline strategy. GO/GS/GV/GY/HC all end deeply cap-censored (>8× cap at G27), so merely extending the same static scene is not evidence-based. Windows DM proves a genuine below-cap ordinary preview regime (R7 ~0.917× cap; R8 first clamp), but not a transferable numeric lux threshold.

The next post-G3 native feedback live attempt therefore requires a **fresh identity plus a substantially brighter diffuse real scene**; HC must never be reused and no synthetic sensor delta is authorized. Until that physical condition is available, continue production integration and repeated-stream robustness work offline/safely.

HE/HF/HG/HH/HI/HJ production consolidation is PASS; HR/HS/HT/HU/HV/HW/HX/HY are PASS. **HZ closes the production handoff decision offline.** Front HY and rear E002k-D-R3 are both independently production-stream proven, but there is not yet one safe full-stack DTB. The front authority intentionally disables rear OV13858 and owns CAMSS `port@2`; rear authority owns `port@1`. Shared CAMSS also conflicts in IOMMU fwspec and RT-CDM1 resources. Therefore direct front-DTB promotion, rear/front node concatenation, and replacement of Golden as saved default are all blocked.

**Next gate: IA offline unified rear+front shared-CAMSS authority analysis.** Derive one evidence-backed common CAMSS authority on exact current Golden before building a combined DTB. The brighter-scene native-feedback gate stays parked.

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
