# SP11 Camera Linux Parity Handover — 2026-09-11

## Resume command / first instruction for the next chat

Continue SP11 Camera from this HANDOFF on branch experiment/e003-front-imx681-cphy.

Current live-result checkpoint immediately before this handoff:
e8362499abf9cb7d6416c23d0eb70e5d7e2998fa
(camera: record FF bounded twelve-frame live pass)

First verify the exact Git + Golden live state below.

SP11 is reserved for Camera. Do not touch HostFabric work.

Do not reuse any consumed one-shot identity. In particular FF is consumed and retired.

Do not create or arm an R13+ Linux live candidate yet. The next frontier is offline authority work beyond R12.

---

## 1. Exact durable Git state

Repository:
/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera

Branch:
experiment/e003-front-imx681-cphy

Durable live-result checkpoint:
e8362499abf9cb7d6416c23d0eb70e5d7e2998fa

Origin matched this checkpoint immediately before rewriting HANDOFF.

Important recent checkpoints:

07a4bb6
camera: close FA R12 AWB oracle with dynamic calibration slot

e2f8ead
camera: stage corrected R12 producer and twelve-frame transport

3084da4
camera: stage fresh twelve-frame R12 live successor

99e2b54
camera: make FD offline result deterministic

e836249
camera: record FF bounded twelve-frame live pass

The repository still contains many old untracked historical artifacts across E002/E003. They predate this frontier. Do not mass-clean or delete them.

---

## 2. Exact current SP11 machine state

Hostname:
SP11X1e

OS/kernel:
Ubuntu 26.04 LTS
7.1.5-sp11-render-parity-v4+
ARM64 / aarch64

Current boot is protected persistent Golden Linux.

Golden boot ID after FF:
4627eb33-da49-491d-a664-eff098e4b3e4

Golden kernel cmdline boots from:
/boot/sp11-7.1.5-audio-fullio-v19c/

GRUB environment:
saved_entry=sp11-audio-fullio-v19c
next_entry=

Current Golden state:
- qcom_camss candidate module absent
- imx681 candidate module absent
- ov13858 candidate module absent
- no /dev/video*
- no /dev/media*

FF Golden-return record:
experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ff-twelve-frame-live-r5-r12/GOLDEN-RETURN.txt

Golden-return SHA256:
4620e5ca2ade4ef6bc74734617dc374bb891ed42975ffd2d8cbf7a8dad1cfe81

FF candidate boot artifacts are retired:
- /etc/grub.d/99zt_sp11_camera_e003i_ff_twelve_frame_r5_r12 is absent
- /boot/sp11-7.1.5-camera-e003i-ff-twelve-frame-r5-r12 is absent
- FF menu ID is absent from generated grub.cfg
- Golden saved_entry is unchanged

---

## 3. Progress from ET to FF

ET exposed the stale gain-feed publisher bound and failed closed at G4/request7.

EU corrected the C publisher offline without rewriting closed EN.

EV then performed one bounded nine-frame live PASS through R9:
- R5..R9 live
- exactly nine QC10C frames
- exactly three physical sensor writes
- Golden return PASS
- candidate retired

EW / EX / EY extended the bounded path offline through R11:
- EW compiled gain publisher G1..G8
- EX producer R5..R11
- EY eleven-frame transport

EZ then performed one bounded eleven-frame live PASS through R11:
- R5..R11 live
- exactly eleven frames
- exactly three physical sensor writes
- Golden return PASS
- candidate retired

FA performed one bounded Windows front-camera oracle stream through R12.

FB recovered the missing Windows calibration-slot selector and proved:
- historical EG: 8/8 bit-exact
- FA: 9/9 bit-exact
- FA transition R4 slot3 high -> R5..R12 slot5 midpoint
- selector is scene-dependent, not a globally fixed slot

FC / FD / FE then extended the corrected path offline:
- FC compiled gain publisher G1..G9, G10 rejected
- FD producer R5..R12 using FB dynamic calibration-slot selection
- FE twelve-frame transport
- FE CAMSS W=1 PASS
- FE helper Werror PASS
- FE scheduler G1..G12 PASS
- physical sensor write schedule remains exactly G1/G2/G3

FF was the fresh live successor and is now consumed.

---

## 4. FF live result — consumed PASS, never reuse

Directory:
experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ff-twelve-frame-live-r5-r12

Durable pass record:
ATTEMPT1-PASS.json

Retirement record:
RETIRE.txt

Status:
CONSUMED_PASS_BOUNDED_TWELVE_FRAME_R5_R12

Candidate HEAD:
99e2b5447fc6f4a8b240b38188048ddfb461c7cf

Exactly one FF camera stream attempt occurred.

No same-boot stream retry occurred.

Helper result:
HELPER_RC=0

Transport result:
- exactly 12 QC10C frames
- DQBUF order 0,1,2,3,0,1,2,3,0,1,2,3
- native AEC accepted G1..G12
- paired TLBG + STATS3A captured G1..G12
- R5..R12 composed and submitted live
- STREAMOFF_OK
- bounded twelve-frame kernel completion observed

Kernel IQ consumption observed:
- R7 / frame7 / slot0
- R8 / frame8 / slot1
- R9 / frame9 / slot0
- R10 / frame10 / slot1
- R11 / frame11 / slot0
- R12 / frame12 / slot1

Physical sensor writes:
exactly 3

Schedule:
- G1 released after completed G2 -> expected effect G4
- G2 released after completed G3 -> expected effect G5
- G3 released after completed G4 -> expected effect G6
- no later physical writes

Producer deadline:
all R5..R12 pipelines < 33.333333 ms

Maximum:
26.872330 ms

Kernel health:
PASS

FF does not claim unrestricted continuous AEC or an infinite scheduler.

---

## 5. FF dynamic AWB result and verifier false-negative

Live FB/FD calibration-slot sequence across producer generations G1..G9:

5,5,7,5,5,5,5,5,5

R12 live:
- calibration slot 5
- AWB triangle 25

The helper completed successfully with RC=0.

The first post-run verifier then produced a false negative because the verifier incorrectly required calibration slot 5 for every live generation. It rejected legitimate G3 slot 7.

This was a verifier assumption defect, not a runtime failure.

Important safety result:
- no second stream was executed
- raw runtime evidence was externally archived before correcting the verifier

The corrected verifier independently replays FB DynamicCalibratedAWB over the exact live trigger sequence and proves:
FB_DYNAMIC_AWB_REPLAY=PASS_9_OF_9

Corrected complete capture status:
PASS_CAPTURE_FF_TWELVE_FRAME_R5_R12

The tracked verify-live.py now validates scene-dependent slot/region/triangle/published-gain replay rather than hard-coding slot 5.

---

## 6. FF external evidence

Pinned raw archive:
/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ff/attempt1-pass-twelve-frame-20260911T1630

Final archive MANIFEST.sha256 file SHA256:
e8c7d8d01265cd596a42da0b512fa34ee0c05cc03610fe6d5ac98bff166aeae5

Compact evidence hashes:

RUN.txt:
a6e2d55b9aa39768d480d5a916bb17beeff9d1f3bc76e44c5accecce806328cc

producer RESULT.json:
cf07e8ecea8be388ac6faedf02fbc38cb1f25a1182872ffa242e3a9d01669461

LIVE-RESULT.json:
69ac7ff9539cb52f1029a33ce2d83e1a4c4b981b471adde05ae0987829ce3a01

DMESG.txt:
7eaedfa017355d8845492f364608edf399db20ce78fb40a501c731e31ba7a6cf

GOLDEN-RETURN.txt:
4620e5ca2ade4ef6bc74734617dc374bb891ed42975ffd2d8cbf7a8dad1cfe81

RETIRE.txt:
ebb8279c049628821b90f64da68678ec9495bf007dcf11f29efa579644975514

Corrected verify-live.py archive SHA256:
aa3ae9b09bb5b786aea6dc3de467f4e5d255169afc2cf6d57338ffc518f2f7e7

---

## 7. Current component authority boundary

GTM:

EB Windows R4..R12 authority:
PASS_WINDOWS_ORACLE

EB proves:
post_r6_gtm_output_law = stable

LSC / Tintless:

ED Windows R4..R12 authority:
PASS_WINDOWS_ORACLE_CLEANROOM_REPLAY

ED clean LSC replay:
9/9 byte-exact LSC0/LSC1/LSC2/GIC

AWB / GainAdj:

FB authority:
PASS_EG_8_OF_8_FA_9_OF_9_BIT_EXACT

FA Windows same-stream evidence extends through R12.

FB proves dynamic calibration-slot selection through the available EG + FA Windows samples.

Integrated producer:

FD:
PASS_OFFLINE_R5_R12_DYNAMIC_CAL_SLOT_INTEGRATION

FD explicitly does not claim a whole-capsule Windows R12 byte oracle.

Transport:

FE:
PASS_OFFLINE_TWELVE_FRAME_TRANSPORT

Live:

FF:
CONSUMED_PASS_BOUNDED_TWELVE_FRAME_R5_R12

Critical boundary:
the Windows-backed content authority currently stops at R12.

Do not silently assume AWB or LSC/Tintless behavior for R13+ merely because the Linux algorithms can keep running.

---

## 8. Useful FF data for the next offline stage

FF captured paired Linux statistics through G12.

The producer consumed G1..G9 for R5..R12.

Therefore FF also preserves fresh, unused continuation inputs:
- G10 STATS3A/TLBG
- G11 STATS3A/TLBG
- G12 STATS3A/TLBG

Native AEC also produced CQ residual ISP gain observations through G12.

These can be used offline to explore R13..R15 composition without another Linux camera stream.

Use the external FF archive as the immutable authority source.

Do not modify the archived evidence in place.

---

## 9. Closed / historical stages — do not rewrite history

EM:
PASS_OFFLINE_R7_R9_COMPOSITION

EN:
closed R5-R9 producer integration; preserve its historical stale-publisher verifier gap

EL:
PASS_OFFLINE_JOIN; historical fixed-calibration behavior was sufficient for EG but is superseded for dynamic selection by FB

ES:
PASS_OFFLINE_NINE_FRAME_TRANSPORT

EJ/EK:
front AWB OTP source proven natively on Linux

EB:
Windows GTM authority through R12

ED:
Windows LSC/Tintless authority through R12

FA:
consumed Windows R12 AWB oracle stream; preserve raw evidence

FB:
dynamic calibration-slot replay authority

FC:
PASS_OFFLINE_G1_G9_C_PUBLISHER

FD:
PASS_OFFLINE_R5_R12_DYNAMIC_CAL_SLOT_INTEGRATION

FE:
PASS_OFFLINE_TWELVE_FRAME_TRANSPORT

Consumed one-shot Linux identities include:
EA / EO / EQ / ER / ET / EV / EZ / FF

Never reuse a consumed identity.

---

## 10. Safety rules that remain mandatory

- Golden default is sacred:
  saved_entry=sp11-audio-fullio-v19c
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

## 11. Recommended next frontier — FG offline only first

No FG directory existed at the time of this handoff, so FG is available as the suggested next label.

Create an offline-only stage such as:
fg-r13-r15-continuation-authority

Goal:
determine whether R13..R15 IQ content can be justified before another Linux live stream.

Recommended sequence:

1. Use immutable FF archived G10/G11/G12 STATS3A + TLBG and AEC gain observations.
2. Extend the producer in scratch/offline form only:
   - G10 -> R13
   - G11 -> R14
   - G12 -> R15
3. Prove deterministic composition and deadline feasibility offline.
4. Audit component authority separately:
   - GTM may inherit EB's proven post-R6 stable output law, but record the inference explicitly.
   - do not assume LSC/Tintless beyond ED R12.
   - do not assume AWB/GainAdj differential parity beyond FA/FB R12.
5. For any component without a defensible post-R12 law, obtain fresh authority before Linux live:
   - preferred: a fresh bounded same-machine Windows oracle extending the relevant sequence to at least R15/R16
   - alternative: a clean recovered-code/tuning proof that establishes the post-R12 state law strongly enough to replace another Windows stream
6. Only after R13..R15 content authority is closed:
   - create a fresh gain publisher extension through the required source generation
   - create a fresh R5..R15 producer
   - create a fresh 15-frame transport
   - verify all offline
   - then create a fresh one-shot Linux live identity
7. Still do not jump directly to an unbounded/infinite stream.

The next work should therefore be offline analysis first, not another immediate camera boot.

---

## 12. Human summary

The project has moved well past the old ET failure.

The Linux camera stack now has a successful bounded live run through R12: twelve real frames, dynamic IQ through R12, three correctly delayed physical sensor writes, clean STREAMOFF, and Golden recovery.

The new useful discovery from FF is that Windows-style AWB calibration selection is genuinely scene-dependent: one live generation selected slot 7 while the others selected slot 5. FB replay independently confirmed this was correct, and the first verifier failure was only a bad hard-coded test assumption.

The remaining blocker to safely extending live parity is no longer the 12-frame transport. It is content authority beyond R12. The next useful progress is to consume FF's already-captured G10..G12 stats offline and close R13..R15 AWB/LSC authority before another live candidate is allowed.
