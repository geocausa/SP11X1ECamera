# SP11 Camera Linux Parity Handover — 2026-09-11

## Resume command / first instruction for the next chat

Continue SP11 Camera from this `HANDOFF.md` on branch `experiment/e003-front-imx681-cphy`, durable HEAD **`0eca3e86448919523075f4ebe6ff8e73407769e7`** (`camera: stage fresh nine-frame R5-R9 live successor`).

**First verify the exact live state below. Do not redo EM/EN/EL/ES work.** ET is the current frontier: it is already **installed but unarmed**, has **never run**, and its root prearm currently passes. If the state still matches this handover, arm ET exactly once, reboot into the one-shot candidate, run its bounded nine-frame R5-R9 flow once, archive/pin on any failure, reboot to Golden with no same-boot retry, and only then update/commit the result.

SP11 is reserved for Camera. Do not touch HostFabric/PiSlave project state other than using the existing PiMaster/PiSlave connection as transport/control. SP7 may be used for Windows/KDNET oracle work if a new oracle is genuinely required, but **ET should not require Windows**.

---

## 1. Exact durable Git state

Repository:

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:

`experiment/e003-front-imx681-cphy`

Durable HEAD / origin at handover:

`0eca3e86448919523075f4ebe6ff8e73407769e7`

Recent durable sequence:

- `0eca3e8` — `camera: stage fresh nine-frame R5-R9 live successor`
- `8f383e5` — `camera: expose R7-R9 transport consumption proof`
- `1420701` — `camera: extend bounded transport through R9`
- `b6724e2` — `camera: record ER R9 transport boundary`
- `eb56c82` — `camera: stage fresh corrected R5-R9 live successor`
- `d0f7d44` — `camera: make R5-R9 prearm deterministic`
- `7f7f687` — `camera: stage corrected bounded R5-R9 successor`
- `e542cf9` — `camera: close EO R9 GainAdj selector failure`
- `72c7706` — `camera: stage bounded R5-R9 live one-shot`
- `cff46df` — `camera: give R5-R9 producer its own manifest identity`
- `ba418db` — `camera: extend bounded producer through R9 offline`
- `2b7e438` — `camera: compose template-free IQ state through R9`
- `73a0237` — `camera: join calibrated AWB into IQ scalars`
- `fe5c7bc` — `camera: prove Linux front AWB OTP source`

Tracked/staged content was clean at handover. `git status` contains many old **untracked historical artifacts** across E002/E003. They predate the current frontier. **Do not mass-clean or delete them.** ET prearm passes with them present because it checks tracked/staged cleanliness, not historical untracked debris.

---

## 2. Exact machine state at handover

SP11 hostname:

`SP11X1e`

Current OS/kernel:

`7.1.5-sp11-render-parity-v4+`

Current boot is persistent **Golden Linux**, not a camera candidate.

GRUB environment:

```text
saved_entry=sp11-audio-fullio-v19c
next_entry=
```

At handover:

- no `qcom_camss` camera candidate module loaded
- no `imx681` camera candidate module loaded
- no `ov13858` camera candidate module loaded
- no `/dev/video*`
- no `/dev/media*`

Golden must remain the persistent fallback throughout all candidate work.

---

## 3. Current frontier: ET

Directory:

`experiments/E003-front-imx681-cphy/e003i-front-native-productionization/et-nine-frame-live-r5-r9-runtime`

Status from README:

**STAGED / NO CAMERA RUNTIME YET.**

ET has never performed a camera stream attempt.

### ET is already installed, but not armed

`INSTALL.txt` records:

```text
schema=sp11-e003i-et-install-v1
status=INSTALLED_UNARMED
time=2026-09-11T12:57:20,531139355+01:00
head=0eca3e86448919523075f4ebe6ff8e73407769e7
```

Installed candidate boot dir:

`/boot/sp11-7.1.5-camera-e003i-et-nine-frame-r5-r9`

Installed GRUB script:

`/etc/grub.d/99zq_sp11_camera_e003i_et_nine_frame_r5_r9`

GRUB menu ID:

`sp11-camera-e003i-et-nine-frame-r5-r9-one-shot`

Candidate installation hashes:

- GRUB script: `538df70d80bf7d2a4b93b8c9214ae22ff83e64959304d2ad71ee76db2af5f14f`
- initrd: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- vmlinuz: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- front-only DTB: `019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f`
- ET CAMSS module: `bfabd559846b93beee4574543aa0ad5f42ea427c55a83daccc39faf6c6e50f9d`

No ET `ARM.txt`, `RESULT.json`, `ATTEMPT1-PASS.json`, `ATTEMPT1-FAILURE.json`, or `RETIRE.txt` existed at handover.

### ET prearm is currently PASS

Fresh handover-time invocation:

```text
ET_ROOT_PREARM=PASS ES_NINE_FRAME=PASS CW_MODULE=72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1 EN_R5_R9=PASS EP_R9_SELECTOR=PASS
```

The prearm must be rerun before arming. If it does not produce the same PASS class, stop and investigate; do not force the boot.

---

## 4. Exact ET live sequence if state still matches

From repo root:

```bash
D=experiments/E003-front-imx681-cphy/e003i-front-native-productionization/et-nine-frame-live-r5-r9-runtime

# 1. Reconfirm Golden + deterministic prearm.
"$D/prearm-check.sh"
sudo -n grub-editenv /boot/grub/grubenv list

# 2. Arm exactly one ET boot.
"$D/arm-once.sh"
sudo -n grub-editenv /boot/grub/grubenv list
# Must show saved_entry=sp11-audio-fullio-v19c and
# next_entry=sp11-camera-e003i-et-nine-frame-r5-r9-one-shot

# 3. Reboot.
sync
sudo -n systemctl reboot
```

After SP11 returns in the ET candidate boot, verify the ET cmdline marker and consumed `next_entry`, then:

```bash
D=experiments/E003-front-imx681-cphy/e003i-front-native-productionization/et-nine-frame-live-r5-r9-runtime

# load.sh runs runtime-preflight before loading modules.
"$D/load.sh"

# Media setup + R4 bootstrap control preparation.
"$D/prepare.sh"

# EXACTLY ONE stream attempt. This script archives before returning and
# runs verify-live.py automatically only if helper rc == 0.
"$D/invoke-once.sh"
```

### Critical one-shot rule

**One candidate boot may perform at most one camera stream attempt.**

On any helper/runtime/verification failure:

1. Do **not** call `invoke-once.sh` again.
2. Preserve/archive everything immediately.
3. Pin the failure evidence.
4. Reboot the whole machine to Golden.
5. Retire ET and create a new candidate identity for any retry.

No same-boot retry.

On apparent success, still reboot to Golden before declaring the candidate complete. Then run:

```bash
"$D/golden-return-check.sh"
```

Retire/remove the consumed ET GRUB entry and boot directory only after evidence is preserved and Golden return is proven, following the existing EO/ER/EK retirement pattern.

---

## 5. ET PASS criteria

`verify-live.py` is the authority. A PASS requires all of the following:

- helper rc 0
- `STREAMON_OK_ASYNC`
- `STREAMOFF_OK`
- EN producer PASS
- kernel consumption markers:
  - `E003I_ES_IQ_CONSUMED R=7 FRAME=7 SLOT=0`
  - `E003I_ES_IQ_CONSUMED R=8 FRAME=8 SLOT=1`
  - `E003I_ES_IQ_CONSUMED R=9 FRAME=9 SLOT=0`
- kernel bounded nine-frame completion line
- exactly nine video generations
- exactly nine TL_BG generations
- exactly nine 3A generations
- buffer cycle `0,1,2,3,0,1,2,3,0`
- AEC ownership G1..G9 / requests G+3
- exactly three physical sensor writes:
  - G1 released at completed G2 -> affects G4
  - G2 released at completed G3 -> affects G5
  - G3 released at completed G4 -> affects G6
- no physical sensor writes from G4 onward
- producer rows exactly:
  - G1 -> no IQ submit
  - G2 -> R5
  - G3 -> R6
  - G4 -> R7
  - G5 -> R8
  - G6 -> R9
- CQ ISP gain identity matches native AEC/gain-feed generation and request
- R5..R9 capsules each exactly 41088 bytes and self-hash match producer manifest
- R7..R9 module bank/Demux/AWB/LSC/GTM content verifies against the clean sources
- EB stable GTM SHA: `074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa`
- R7/R8/R9 end-to-end producer pipeline each `< 33.333333 ms`
- clean kernel health (no SMMU deadlock, vblank timeout, Oops, soft lockup, panic)
- Golden return PASS afterward

A successful ET run is still **bounded nine-frame integration**, not unrestricted continuous AEC.

---

## 6. Why ET exists / do not redo these closed stages

### EM — request7+ template-free composer

Directory:

`em-post-r6-template-free-composer`

Status:

`PASS_OFFLINE_R7_R9_COMPOSITION`

EM composes R7/R8/R9 without reading raw Windows R7/R8/R9 main or DMI capsules.

Inputs/sources:

- E static/template-free framing
- deterministic bank parity
- DV Demux/BLS using EA generation-tagged CQ ISP gain
- EL calibrated AWB GainAdj -> PDPC/WB
- DS sequential DynamicLsc/Tintless driven by preserved EA G1..G6 TL_BG/3A
- EB stable post-R6 GTM
- invariant DMI sections only when proven invariant

Deterministic Linux composition regression hashes:

- R7 `681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e`
- R8 `79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e`
- R9 `1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda`

These are Linux composition regression hashes, not a claim of whole-capsule byte equality to Windows R7-R9.

### EN — bounded producer through R9

Directory:

`en-r5-r9-producer-integration`

Offline producer integration already extends G2..G6 -> R5..R9.

Do not create another producer fork unless ET finds a real content defect.

### EL — calibrated AWB scalar join

Directory:

`el-calibrated-awb-scalar-join`

Status:

`PASS_OFFLINE_JOIN`

Closed facts:

- Windows gain differential 8/8
- stateful GainAdj triangle selector differential 8/8
- EA scalar regression: 7/7 PDPC/WB words x 6 generations
- Linux physical calibration source is bound through EJ/EK

### EJ/EK — per-device calibration source

EJ:

`PASS_10_OF_10_BIT_EXACT`

EK:

`PASS_LIVE_LINUX_PHYSICAL_OTP`

The front EEPROM 12-byte AWB window was read natively on Linux and exactly matched the Windows oracle. Do not hard-code the formerly solved reciprocal calibration constants as production authority.

### EB — GTM post-R6

Status:

`PASS_WINDOWS_ORACLE`

R6 through R12 GTM payload is byte-stable under the bounded scene/oracle. R6/R7/R8/R9 coherent GTM SHA:

`074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa`

Do not carry forward the older 0076 R6 GTM payload; EB is the coherent post-R6 authority.

### ED — evolving LSC/Tintless

Status:

`PASS_WINDOWS_ORACLE_CLEANROOM_REPLAY`

Sequential LSC/Tintless clean replay is proven R4..R12. R7+ LSC must remain sequential; do not freeze R6.

---

## 7. Consumed/retired live candidates and what they proved

### EA — earlier bounded six-frame sensor + Demux PASS

EA proved the current-first scheduling design through six frames and clean Golden return. It is historical proof only; its identity is consumed.

### EO — consumed failure, do not reuse

EO exposed an R9 GainAdj selector issue. EP/EL closed that failure with the real stateful selector / multi-side behavior. EO is retired.

### EQ — retired preflight-only candidate

EQ failed before camera runtime due to a nondeterministic tracked verifier/result timing artifact. That harness defect was fixed. EQ identity must not be reused.

### ER — consumed live failure, do not reuse

ER status:

**ATTEMPT1 CONSUMED / FAIL-CLOSED at the R9 transport window; Golden return PASS; candidate retired.**

ER proved the corrected IQ content live through G6 and composed R9 successfully. Its failure was not IQ content:

- production CAMSS runner still stopped after six hardware frames
- R7/R8 were FIFO-enqueued but not consumed
- runner closed/purged provider after frame6
- G6 then composed R9, but outer ingress returned `-EBUSY` because `live_active` was already cleared

This is why ES/ET exist. Do not optimize producer timing to solve ER; the root cause was the six-frame transport window.

ER raw evidence:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-er/attempt1-fail-r9-transport-20260911T1157`

### ES — transport fix, offline PASS

Directory:

`es-nine-frame-r7-r9-transport`

Status:

`PASS_OFFLINE_NINE_FRAME_TRANSPORT`

ES extends only the bounded transport/runner to nine frames. Offline proofs:

- CAMSS W=1 build PASS with Golden vermagic
- helper `-Werror` PASS
- scheduler test PASS
- hardware frames 1..9
- buffer cycle `0,1,2,3,0,1,2,3,0`
- new kernel consumption requests R7/R8/R9
- AEC generations G1..G9
- CQ gain feed intentionally only G1..G6 (enough for R5..R9)
- physical sensor writes remain exactly G1..G3

ET is the fresh live successor using ES.

---

## 8. Safety / behavior rules to preserve

- Golden default is sacred: `saved_entry=sp11-audio-fullio-v19c`.
- Candidate boots are one-shot only via `next_entry`/`grub-reboot`.
- One camera stream attempt per candidate boot maximum.
- On failure: preserve evidence, no same-boot retry, whole-machine reboot to Golden.
- Never reuse consumed EO/EQ/ER/EA identities.
- Fresh successor identity required after any ET live failure.
- Do not claim unrestricted continuous AEC from bounded nine-frame PASS.
- Preserve raw external evidence and checksums; commit only compact/appropriate tracked evidence.
- Do not clean historical untracked repo artifacts unless independently reviewed; many are old evidence/build residues.
- Do not touch HostFabric work in this camera continuation.

---

## 9. If ET passes

After Golden return and evidence preservation:

1. Write compact ET PASS result / README update / Golden-return evidence.
2. Retire consumed ET boot artifacts.
3. Commit/push the ET live result.
4. Only then design the next step toward sustained/continuous operation.

The next architectural work after an ET PASS is **not more R7–R9 reverse engineering**. It is extending the now-proven nine-frame transport/producer model into a longer-running/reusable scheduler while preserving:

- generation/request identity
- current-first IQ concurrency
- sequential Tintless/LSC state
- stateful AWB GainAdj selector state
- CQ gain feed ordering
- sensor visibility/release law
- VFE slot/buffer lifetime
- clean stop/recovery behavior

Any longer-running candidate should first be proven offline and must still begin as a bounded fresh one-shot, not jump directly to “infinite” streaming.

---

## 10. Short human summary

The project is no longer blocked on understanding R7–R9 IQ. That work is already done. The remaining immediate question is whether the **nine-frame transport extension can consume the already-composed R7/R8/R9 capsules live at the correct hardware boundaries**.

ET is installed, unarmed, prearm PASS, and has never run. That is the exact frontier.
