# SP11 Camera Linux Parity Handover — 2026-09-11

## Resume command / first instruction for the next chat

Continue SP11 Camera from this HANDOFF on branch `experiment/e003-front-imx681-cphy`.

Current durable live-result checkpoint immediately before this handoff:

`492cf97b153fa4785448568aee123a9bf8abc8c9`
(camera: record FN bounded fifteen-frame live pass)

First verify the exact Git + Golden state below.

SP11 is reserved for Camera. Do not touch HostFabric work.

Do not reuse consumed one-shot identities. FN is consumed and retired.

Do not jump directly to unrestricted continuous streaming. The new frontier is bounded authority/work beyond R15.

---

## 1. Exact durable Git state

Repository:

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:

`experiment/e003-front-imx681-cphy`

Durable live-result checkpoint:

`492cf97b153fa4785448568aee123a9bf8abc8c9`

Origin matched this checkpoint immediately before rewriting HANDOFF.

Important recent checkpoints:

- `45c6c52` — close Windows R15 Tintless/LSC authority
- `6c2e142` — authorize bounded R13–R15 IQ content
- `bf9e631` — stage G12 publisher and R15 producer
- `600056f` — stage authorized fifteen-frame R15 transport
- `597770a` — stage FN fifteen-frame live candidate
- `492cf97` — record FN bounded fifteen-frame live pass

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

Golden boot ID after FN:

`bcdcc155-15d8-4fe1-853d-65526affc4d8`

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

FN candidate boot artifacts are retired:

- `/etc/grub.d/99zu_sp11_camera_e003i_fn_fifteen_frame_r5_r15` absent
- `/boot/sp11-7.1.5-camera-e003i-fn-fifteen-frame-r5-r15` absent
- FN menu ID absent from generated grub.cfg
- Golden saved_entry unchanged

---

## 3. Windows authority work that closed R13–R15

### FH — recovered Windows AWB authority

FH recovered same-stream Windows AWB/GainAdj evidence through R18 without another Windows stream.

Status:

`PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT`

This provides AWB/GainAdj differential authority through R18.

### FI — fresh Windows R4–R15 Tintless/LSC oracle

FI performed exactly one fresh Windows front-camera stream and captured R4..R15:

- Tintless stats: 0x12bec bytes/request
- trigger: 0x100 bytes/request
- final LSC staging: 0x18a0 bytes/request

Sequential clean-room replay through the native Tintless/DX DynamicLsc path:

`12/12 byte-exact LSC0/LSC1/LSC2/GIC`

Bank parity:

`1,0,1,0,1,0,1,0,1,0,1,0`

FI returned Golden cleanly.

FI external archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fi/windows-r4-r15-20260911`

Final FI archive MANIFEST.sha256 file SHA256:

`eda7b5339be0788c0505be7ae77f530f7f73475ca56579efd7f1c3f20296242d`

### FJ — R13–R15 authority join

FJ combines:

- FG deterministic R13–R15 composition from immutable FF continuation inputs
- FH Windows AWB authority through R18
- FI Windows Tintless/LSC authority through R15
- EB post-R6 stable GTM law

Status:

`PASS_OFFLINE_R13_R15_CONTENT_AUTHORIZED`

---

## 4. Offline bounded R15 stack

### FK — G1..G12 compiled C gain publisher

Status:

`PASS_OFFLINE_G1_G12_C_PUBLISHER`

Properties:

- exact existing 24-byte ABI
- request = generation + 3
- G1..G12 accepted
- G13 rejected
- only source delta from FC is upper bound 9 -> 12

gain-feed.c SHA256:

`93e284bca519366817324962278d5403c05cdc7fd0454b8a4e8fe683d2b90b2e`

### FL — live-capable R5..R15 producer

Status:

`PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION`

Offline proof:

- source: immutable FF G1..G12 paired stats + CQ gains
- R5..R12 reproduce the real FF live capsules 8/8 byte-exact plus key metadata
- R13..R15 match FJ-authorized hashes exactly
- two independent FL runs are deterministic
- live-capable scheduler/control/submission path preserved

### FM — fifteen-frame transport

Status:

`PASS_OFFLINE_FIFTEEN_FRAME_TRANSPORT`

Proof:

- CAMSS W=1 PASS
- helper Werror PASS
- 15-frame buffer cycle:
  `0,1,2,3,0,1,2,3,0,1,2,3,0,1,2`
- paired AEC/stats generations G1..G15
- CQ gain publisher generations G1..G12
- IQ consumption requests R5..R15
- physical sensor-write schedule remains exactly sources G1/G2/G3 at boundaries G2/G3/G4
- scheduler unit test PASS
- no FM camera runtime

Pinned generated source hashes:

- CAMSS:
  `592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6`
- helper:
  `f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4`
- schedule header:
  `b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d`

---

## 5. FN live result — consumed PASS, never reuse

Directory:

`experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fn-fifteen-frame-live-r5-r15`

Durable pass record:

`ATTEMPT1-PASS.json`

Retirement record:

`RETIRE.txt`

Status:

`PASS_CAPTURE_FN_FIFTEEN_FRAME_R5_R15`

Candidate HEAD:

`597770a1df9521116f68b8b977cb9c91030edede`

Candidate boot ID:

`263d0c11-6eac-484c-bccd-faf08a88fd08`

Exactly one FN camera stream attempt occurred.

No same-boot stream retry occurred.

Helper-consumed guard was present before streaming.

Helper result:

`HELPER_RC=0`

Transport result:

- exactly 15 QC10C frames
- DQBUF order 0,1,2,3,0,1,2,3,0,1,2,3,0,1,2
- native AEC accepted G1..G15
- paired TLBG + STATS3A captured G1..G15
- R5..R15 composed and submitted live
- kernel IQ consumption observed through R15/F15/S0
- STREAMOFF_OK
- bounded fifteen-frame kernel completion observed

Physical sensor writes:

exactly 3

Schedule:

- G1 released after completed G2 -> expected effect G4
- G2 released after completed G3 -> expected effect G5
- G3 released after completed G4 -> expected effect G6
- no later physical writes

Producer deadline:

all R5..R15 pipelines < 33.333333 ms

Maximum:

`27.722582 ms`

R15 live:

- capsule SHA256:
  `d0675afea740b46070ef4864ec12cea8ab72771ddc47984c65aa5a067962503c`
- AWB calibration slot 5
- AWB triangle 25

Kernel health:

PASS

FN does not claim unrestricted continuous AEC or an infinite scheduler.

---

## 6. FN external evidence

Archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fn/attempt1-pass-fifteen-frame-20260911T1735`

Final archive MANIFEST.sha256 file SHA256:

`a12e84d235f5b4af5e313cd36f0f2952356a34ff1e80468ebd89c29355551a62`

Compact evidence hashes:

- ATTEMPT1-PASS.json:
  `9b850a9cfcc401acd9b5f7f6b24efba40909b75438427cdf69fd9d9cda834348`
- RUN.txt:
  `49ffcebb59b38118d3a6656814962416bb2f9b1b2c3a2ad77592123b3b937c47`
- LIVE-RESULT.json:
  `00407b6cea78511a0eec7bb8ae01919f9ac6178f3ddbdb99f3e17a07c7fc89cd`
- producer RESULT.json:
  `eed4d99df47d97b8de9fdd7bdd2cc71689a4bf0c1bb49160cc437a74027f14e8`
- DMESG.txt:
  `a7910203d29730113ed9bc21fe95931becbc417137de119b4a602e1730f26c9f`
- GOLDEN-RETURN.txt:
  `64edf02c9fd1d05847ddf63ae804b6a6f60972520422b4d4ab51f6a2e118e0ad`
- RETIRE.txt:
  `0e2bd19e71cf5d08effb3dfa69362b54f6fa867ae4e79d5fe0b2936676d93b9f`

---

## 7. Fresh continuation inputs now available

FN captured paired Linux statistics through G15.

FL consumed G1..G12 for R5..R15.

Therefore FN preserves fresh continuation inputs that have never been consumed by the live IQ producer:

- G13 STATS3A/TLBG
- G14 STATS3A/TLBG
- G15 STATS3A/TLBG

Native AEC also produced CQ residual ISP gain observations through G15 in RUN.txt.

These are the natural offline inputs for:

- G13 -> R16
- G14 -> R17
- G15 -> R18

Use the immutable external FN archive as the source. Do not modify archived evidence in place.

---

## 8. Current authority boundary

AWB/GainAdj:

- FH Windows authority already extends through R18.

GTM:

- EB's post-R6 stable output law remains available, but any new use should record that inference explicitly.

Tintless/LSC:

- FI Windows clean-room differential authority currently stops at R15.

Therefore the main blocker to a safe R16..R18 Linux live extension is Tintless/LSC authority beyond R15, not the producer mechanics or AWB.

Do not silently extrapolate FI past R15.

---

## 9. Recommended next frontier — bounded R16..R18 offline first

Suggested sequence:

1. Create an offline-only continuation stage from immutable FN G13/G14/G15:
   - G13 -> R16
   - G14 -> R17
   - G15 -> R18
2. Prove deterministic composition and deadline feasibility with the current production algorithms.
3. Use FH as AWB/GainAdj differential authority through R18.
4. Obtain fresh Tintless/LSC authority through R18 before Linux live.
   Preferred path:
   - one fresh bounded Windows R4..R18 Tintless/trigger/final-LSC-staging oracle using FI's already-proven debugger hooks and one-stream holder.
5. Join the component authority explicitly.
6. Only after authority closes:
   - extend compiled C gain publisher through G15
   - extend live-capable producer through R18
   - extend bounded transport to 18 frames
   - verify all offline
   - create a fresh one-shot Linux live identity
7. Still do not jump directly to unrestricted continuous/infinite streaming.

Suggested next stage labels if free:

- FO — offline R16..R18 continuation/composability
- FP — Windows R4..R18 Tintless/LSC oracle
- FQ — R16..R18 authority join
- FR — G1..G15 compiled publisher
- FS — R5..R18 producer
- FT — eighteen-frame transport
- FU — fresh one-shot eighteen-frame Linux live candidate

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

Consumed Linux one-shot identities include:

EA / EO / EQ / ER / ET / EV / EZ / FF / FN

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
- do not extend Linux live IQ past the proven content-authority boundary without a fresh offline gate

---

## 12. Human summary

The Linux front-camera stack now has a successful bounded live run through R15.

FN completed fifteen real QC10C frames, captured paired 3A/TLBG through G15, submitted dynamic IQ R5..R15, performed only the original three delayed physical IMX681 writes, cleanly STREAMOFF'd, passed kernel-health validation, and returned to Golden. The consumed candidate was retired.

The next useful frontier is R16..R18. Linux already has fresh continuation inputs G13..G15 from FN, and Windows AWB authority through R18 already exists via FH. The remaining content-authority gap is Tintless/LSC beyond R15. Close that offline/with a bounded Windows oracle before creating another Linux live candidate.
