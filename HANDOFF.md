# SP11 Camera Linux Parity Handover — 2026-09-11

## Resume command / first instruction for the next chat

Continue SP11 Camera from this HANDOFF on branch experiment/e003-front-imx681-cphy.

Result checkpoint immediately before this handoff:
f4bba70c070bd4a52a81dd652657b30ccae044af
(camera: record ET gain-feed failure and EU fix)

First verify the exact live state below. Do not redo EM/EN/EL/ES work. ET is consumed and retired; never reuse its one-shot identity. EU is an offline correction only and has performed no camera runtime. The next live attempt must use a fresh candidate identity derived from ET/ES transport but source the corrected G1..G6 C gain-feed publisher from EU.

SP11 is reserved for Camera. Do not touch HostFabric work.

---

## 1. Exact durable Git state

Repository:
/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera

Branch:
experiment/e003-front-imx681-cphy

Durable result checkpoint:
f4bba70c070bd4a52a81dd652657b30ccae044af

The repository still contains many old untracked historical artifacts across E002/E003. They predate this frontier. Do not mass-clean or delete them.

The result checkpoint modifies only:
- ET compact failure/retirement evidence + README
- new EU offline publisher proof

Closed EM/EN/EL/ES files were not modified.

---

## 2. Exact machine state after ET

SP11 hostname:
SP11X1e

OS/kernel:
Ubuntu 26.04 LTS
7.1.5-sp11-render-parity-v4+
ARM64 / aarch64

Current boot is persistent Golden Linux.

Golden-return boot ID from ET:
32193d8d-31ae-4147-b2e3-8be4e1fb6752

GRUB environment after return:
saved_entry=sp11-audio-fullio-v19c
next_entry=

After Golden return:
- no qcom_camss candidate module loaded
- no imx681 candidate module loaded
- no ov13858 candidate module loaded
- no /dev/video*
- no /dev/media*

ET Golden-return authority:
experiments/E003-front-imx681-cphy/e003i-front-native-productionization/et-nine-frame-live-r5-r9-runtime/GOLDEN-RETURN.txt

Status:
ET_GOLDEN_RETURN=PASS

ET candidate boot artifacts are retired:
- /etc/grub.d/99zq_sp11_camera_e003i_et_nine_frame_r5_r9 is absent
- /boot/sp11-7.1.5-camera-e003i-et-nine-frame-r5-r9 is absent
- ET menu ID is absent from generated grub.cfg
- Golden saved_entry is unchanged

---

## 3. ET live result — consumed failure, do not reuse

Directory:
experiments/E003-front-imx681-cphy/e003i-front-native-productionization/et-nine-frame-live-r5-r9-runtime

ET performed exactly one real camera stream attempt.

No same-boot stream retry was performed. The consumed marker blocked re-entry before a second stream could occur.

Durable failure record:
ATTEMPT1-FAILURE.json

Retirement record:
RETIRE.txt

Status:
CONSUMED_FAIL_G4_GAIN_FEED_PUBLISHER_BOUND

What passed before the failure:
- Golden -> one-shot ET boot transition
- ET cmdline marker present
- next_entry consumed
- ET runtime preflight PASS
- ES-nine-frame CAMSS + CW IMX681 load PASS
- media + R4 bootstrap preparation PASS
- STREAMON succeeded
- G1/G2/G3 native AEC accepted
- R5 from G2 submitted successfully
- R6 from G3 submitted successfully
- six completed video frames validated before the later pin
- G1 and G2 physical sensor releases occurred at completed G2/G3
- Golden return PASS
- ET candidate retirement PASS

Observed live failure:
EN_GAIN_FEED_FAIL G=4 REQUEST=7 RC=-22

Producer then reported:
RuntimeError: gain feed timeout/hup

The runner later pinned while handling the seventh dequeue:
PINNED_FOR_REBOOT: unexpected completed buffer ordering

Important interpretation:
The seventh-buffer ordering pin is secondary fallout after producer loss. The first causal defect is the G4/request7 gain-feed publication failure.

R5 live capsule SHA256:
f7d4adbe3b83472d9994aad01ffd40f66ede1d620257fc696be949a59a789f0b

R6 live capsule SHA256:
bed48bbfa4af03c1444c81063bc78f551445b8492e158b686c99b453f23ef94f

R7 was never composed/submitted in ET because the C gain publisher rejected G4 before the producer could consume it.

Only two delayed AEC sensor writes were released in this failed run. The G3 release at completed G4 was not reached because the gain-feed failure occurs earlier in the audit-thread ordering.

---

## 4. ET root cause

ET helper logic correctly publishes CQ residual gain for:
target <= 6U

But the copied C publisher inherited the older DZ validation:
generation > 3U -> -EINVAL

Therefore:
- G1 -> request4 passes
- G2 -> request5 passes
- G3 -> request6 passes
- G4 -> request7 returns -EINVAL
- producer sees pipe timeout/HUP
- R7/R8/R9 path is never reached

This is a harness/integration-bound defect, not evidence that EM R7-R9 IQ content is wrong.

The closed EN stage stated G1..G6 publication in its README/helper source, but its verifier accidentally:
- required gain-feed.c to remain byte-identical to DZ
- tested six records by writing directly into the pipe from Python
- therefore bypassed the actual C publisher function that still rejected G4+

Do not modify/reopen EN just to erase history. Preserve EN as the closed stage that exposed this latent verifier gap.

---

## 5. EU — fresh offline correction, PASS

Directory:
experiments/E003-front-imx681-cphy/e003i-front-native-productionization/eu-six-generation-gain-feed-publisher

Status:
PASS_OFFLINE_G1_G6_C_PUBLISHER

EU copies the gain-feed wire ABI without changing closed EN and changes only:
generation validation upper bound 3 -> 6

EU compiled C proof verifies:
- G1 accepted
- G2 accepted
- G3 accepted
- G4 accepted
- G5 accepted
- G6 accepted
- G7 rejected
- malformed request identity rejected
- request remains generation + 3
- wire ABI remains 24 bytes

EU gain-feed.h SHA256:
60adc6456b9806f50e14c0e3158a74dc49995549af1627e1604ad0496212de79

EU gain-feed.c SHA256:
2dbd4856294fe3aceecc1f7027643b6a0c559e7ce5469d902846b9073a466b3c

EU has performed no camera runtime.

---

## 6. External ET evidence

Pinned raw archive:
/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-et/attempt1-fail-pinned-gainfeed-order-20260911T1324

Final archive manifest SHA256:
22cc2500fa5ae667e742a2f2d1a45c5697f100bf2bd574525291dd47479e88a7

Compact evidence hashes:
- RUN.txt
  5667610d80a39bc9a8dce556afd3ec1c9f94ba1a61c13cab364f8c062aae8ba3
- producer RESULT.json
  580988199d1464ef420da5eaa7b6e14181985920bf4a4c56c0b6ed4aeafc590b
- DMESG.txt
  5369102caef1972264b501fb8ffa837fd497385fd229602a343cf65b18cef2a7
- GOLDEN-RETURN.txt
  7957617f6d8043881fc3792f01b84377cbff3d7955d5bbc00e4acf035b3e7aea
- RETIRE.txt
  05e81dfe767b24239bbea834e3def28a2a37a64c949854c6b7eda1b8a102e5bc

---

## 7. Closed work — do not redo

EM:
PASS_OFFLINE_R7_R9_COMPOSITION

EN:
closed R5-R9 producer integration; preserve its historical result and verifier gap as evidence

EL:
PASS_OFFLINE_JOIN

ES:
PASS_OFFLINE_NINE_FRAME_TRANSPORT

EJ/EK:
front AWB OTP source proven natively on Linux

EB:
post-R6 GTM stable authority preserved

ED:
sequential LSC/Tintless replay proven

EO/EQ/ER/ET:
consumed identities; never reuse

---

## 8. Safety rules that remain mandatory

- Golden default is sacred:
  saved_entry=sp11-audio-fullio-v19c
- candidate boots must be one-shot via next_entry/grub-reboot
- one camera stream attempt per candidate boot maximum
- on any failure: preserve evidence, no same-boot stream retry, whole-machine reboot to Golden
- consumed EA/EO/EQ/ER/ET identities must never be reused
- any new live retry needs a fresh identity
- preserve raw external evidence and checksums
- do not mass-clean historical untracked artifacts
- do not claim continuous AEC from bounded tests
- do not touch HostFabric work in this continuation

---

## 9. Recommended next step

Create a fresh live successor identity after ET, suggested next label EV if no conflicting stage is introduced.

The successor should:
1. inherit ET/ES nine-frame transport unchanged
2. keep the already-proven EN/EP producer and EM/EL/ED/EB content path
3. source gain-feed.c + gain-feed.h from EU rather than the stale EN/DZ publisher
4. add an offline prearm assertion that calls the actual compiled C publisher for G1..G6
5. improve the DQBUF failure log to print actual index/bytesused/sequence before pinning
6. build and verify offline
7. install unarmed
8. reconfirm Golden + deterministic prearm
9. arm exactly one fresh boot
10. perform at most one nine-frame stream attempt
11. preserve evidence and reboot to Golden regardless of PASS/FAIL

Do not jump directly to a continuous/infinite stream candidate yet.

---

## 10. Human summary

ET was useful even though it failed. The nine-frame candidate got through startup and R5/R6 live, then exposed a simple but important integration bug: the C gain publisher still thought only G1-G3 were legal even though the new producer needs G1-G6.

That bug is now isolated and proven fixed offline in EU without rewriting the already-closed EN stage. SP11 is safely back on Golden, ET is retired, and the raw failure evidence is pinned. The next live move is a fresh one-shot successor using EU's six-generation publisher.
