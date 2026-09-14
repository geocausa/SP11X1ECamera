# E004 front-IR protected-camera handoff — 2026-09-14

## Mission / authority

Goal is **1:1 Windows camera parity**. Windows is always the behavioral oracle. Static Windows reverse engineering is fallback/explanation; Qualcomm/Linux sources are informative only and must never override observed Windows behavior.

Camera work stays on **SP11, SP7 and PiMaster only**. SP11 Golden Linux / FullIO v19c remains the safety baseline. Windows may be entered with the established one-shot Boot0006 oracle entry whenever a concrete ambiguity needs the authoritative answer. **Linux SecureISP runtime is still not authorized.** Do not enable CPZ/SecureISP/protected ownership runtime merely to test.

Repo: `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`
Branch: `experiment/e004-front-ir-vd55g0`

At handoff creation the protected-image algorithm checkpoint is **`3326334 camera: prove Windows SWASF CD90 byte exact`**. A final handoff commit will follow this file; new chat must first read `git log -5 --oneline --decorate` and verify origin matches HEAD.

## Safety state at handoff

SP11 is back on Golden Linux:

- kernel `7.1.5-sp11-render-parity-v4+`
- saved GRUB entry `sp11-audio-fullio-v19c`
- `next_entry` empty
- camera overlap guard passes
- no camera nodes/modules/runtime active
- no Linux SecureISP/CPZ/protected ownership transition was used in E004dh

Always run `./tools/camera-overlap-guard.sh` before/after risky transitions and before sealing a checkpoint.

Root tracked files already dirty from older work and deliberately untouched by this handoff:
`CONTINUE.md`, `HANDOFF.md`, `PROJECT_STATE.md`, `README.md`, `state/project.yaml`.
There are many unrelated E002/E003 untracked artifacts. Never sweep/add/delete them.

## Protected-camera architecture already closed

Windows has three distinct secure lifetimes and Linux parity must preserve them:

1. external VTL1 protected samples;
2. SecureISP internal CP_CAMERA buffer;
3. secure CSI/protected-worker bracket.

Do **not** move secure-memory policy into `vd55g0.c`; protected-sample ownership belongs at CAMSS/VB2.

The Linux implementation direction remains CPZ/SecurePD-style trusted execution with:

- external protected sample ownership: CP_CDSP only;
- internal protected target ownership: CP_CDSP + CP_CAMERA;
- HLOS CPU access excluded while protected;
- secure FastRPC context bank candidate CB9 kept disabled-by-default;
- dma-buf FD handoff with Windows `cbCaptured` extent preserved;
- unmap/detach before reclaim;
- fail-closed state transitions.

Major earlier checkpoints include `79d9c6a` external FastRPC handoff, `ab2db30` external CPZ backing lifetime, `2bdc258` integrated protected provider compile, `bbb3c90` disabled secure FastRPC bank, and `e1306bf` missing secure CDSP context-bank identification.

## E004dh: Windows-authoritative image algorithm status

Directory:
`experiments/E004-front-ir-vd55g0/e004dh-swab-exact-offline-port/`

Run the gate verifier first:

`experiments/E004-front-ir-vd55g0/e004dh-swab-exact-offline-port/verify_e004dh.py`

Current result is deliberately partial because full SWASF integration is not yet done.

### Windows live tuning — closed

Authoritative Surface FaceAuth IR profile: **644×604 NV12 @ 60 fps**, FaceAuthMode + SecureMode enabled.

Windows selected SWABF:

- threshold 128;
- weights `2000,1990,1960,1911,1846,1670,1452,1213,973,750,556,395,270,177,142,112`;
- packed 0x22 payload SHA-256 `8443115a763d9f5e425cdf7415250f129bad6f028e1b1c18ade86c17a4f392aa`.

Windows selected SWASF 0x804 payload SHA-256:
`6cc727315a8d640ab40211f031efdfe28f12e8f2be90f8c8a3a785bb63ccfc0c`.

Primary files:

- `oracle/windows-live/SWABF-derived-from-live-cache.bin`
- `oracle/windows-live/SWASF-derived-from-live-cache.bin`
- `WINDOWS-ORACLE.md`

### SWABF — closed byte-for-byte

The scalar SWABF implementation is Windows-proven exact, including full **644×604 NV12** camera geometry. Windows and scalar outputs matched byte-for-byte across the complete 583,464-byte frame.

Source:
`scaffold/sp11-swabf-reference.c`

### SWASF helper/C230 — closed

The 5×5 extrema helper and C078 activity metric have direct Windows oracle vectors and scalar equivalents.

`FUN_18001c230` is fully closed:

- 232 direct basis cases exact;
- 4096 randomized direct Windows cases exact;
- Windows/scalar aggregate SHA-256 `f926c06b87b2679132cd9ac41b0a590578e712e353ce91732a646b584756d035`.

Sources:

- `scaffold/sp11-swasf-helpers.c`
- `scaffold/sp11-swasf-c230.c`

### C3E8 — closed byte-for-byte

Windows `FUN_18001c3e8` uses an 8-pixel horizontal tile. Its prefilter is the exact five-point cross median:

`median(left, center, right, up, down)`

with coordinate replication/clamping at image boundaries.

The complete C3E8 scalar stage is Windows-proven exact:

- 512 deterministic random images;
- 1024 independent tiles;
- all three scratch products compared;
- zero unexpected writes;
- Windows/scalar SHA-256 `aa35e4c06de41305edd1eabb365161bb639bd6d982226ffe6e216ec27a7ff90f`.

Source:
`scaffold/sp11-swasf-c3e8.c`

Checkpoint: `8c7a522 camera: prove Windows SWASF C3E8 byte exact`.

### CD90 final combine — NOW CLOSED byte-for-byte

`FUN_18001cd90` is the last nonlinear SWASF combine. Its scalar implementation is:
`scaffold/sp11-swasf-cd90.c`.

A self-consistent debugger capture at the real Windows function entry/return proved the live arguments, runtime tables and tuning pointer. The real destination changed from:

`5a5a5a5a5a5a5a5a` → `00000518293b4c5f`

and the scalar candidate reproduced it exactly.

Then Windows generated a deterministic **4096-case / 32768-lane** direct CD90 oracle after normal SWASF init. Full Windows vector-set SHA-256:

`86b1851e1023d4659a50b89ff8f9ace26fe5ec344ee434066e2c5d9887702785`

`verify_cd90_random_vectors.py` now reports:

`E004dh CD90 Windows random vectors: PASS (4096 cases / 32768 lanes)`

Therefore the shipping-path CD90 combine is closed and `RESULT.json` has `cd90_final_combine_exact=true`.

Important artifacts:

- `oracle/windows-cd90-random-vectors/vectors.bin`
- `oracle/windows-cd90-random-vectors/tune.bin`
- `verify_cd90_random_vectors.py`
- `CD90-ORACLE.md`
- checkpoint `3326334 camera: prove Windows SWASF CD90 byte exact`

## Full-frame Windows fixtures already preserved

The authoritative 644×604 synchronized oracle set is under:
`oracle/windows-sync-oracle/`

Key files:

- `input-644x604-nv12.bin`
- `windows-trustlet-sync-swabf-644x604.bin`
- `windows-trustlet-sync-swasf-644x604-stable.bin`
- `windows-trustlet-sync-swasf-644x604-race-a.bin`
- `windows-trustlet-sync-swasf-644x604-race-b.bin`
- `SYNC-ORACLE-SUMMARY.txt`

Windows occasionally showed tiny luma-only differences at its eight-worker partition boundaries. Preserve these as Windows scheduling behavior; do not silently normalize them away. The stable fixture is the primary deterministic target, while race fixtures document Windows' own nondeterminism.

## Immediate next work — do this first in new chat

The reverse-engineering hole is essentially gone. The remaining E004dh task is **integration**, not invention:

1. Verify HEAD/origin and Golden safety state.
2. Run `verify_e004dh.py`; it must pass.
3. Integrate the already-proven SWABF + C3E8 + CD90 scalar stages into the existing offline parity worker in `e004dg-offline-parity-worker`.
4. Preserve Windows' request split: synthetic branch, early copy + 0x80 tail, later SWABF → SWASF + 0x80 tail.
5. Run the integrated offline worker against `oracle/windows-sync-oracle/input-644x604-nv12.bin` and compare complete output to the stable Windows SWASF fixture byte-for-byte.
6. Investigate only genuine mismatches against Windows. If differences occur solely at the documented Windows worker-partition race locations, preserve/report that distinction rather than altering the algorithm.
7. Only after the full integrated Windows differential passes may `SP11_WORKER_ESWAB_PENDING` be removed/replaced.
8. Build/partial-link the resulting Hexagon-v73 worker and prove zero unresolved symbols.
9. Seal E004dh with `RESULT.json`, verifier, safety evidence, commit and push.

Do **not** use Linux SecureISP runtime for this closure. If the integrated offline result exposes a behavioral ambiguity, one-shot Windows is authorized and is the deciding oracle.

## What comes after E004dh

Once complete offline SWAB/SWASF parity is sealed, return to the protected-worker delivery problem. The memory/ownership plumbing is mostly established; the production protected environment's code-admission/signing policy remains a separate integration constraint. Do not bypass signature verification. Existing same-machine SecurePD examples prove the trusted protected-buffer CPU-processing pattern but are not themselves the camera algorithm.

Overall camera-stack progress estimate at handoff: about **78% toward genuine 1:1 Windows parity**. Reverse-engineering understanding is around 90%+, while end-to-end protected Linux runtime proof remains the deliberately deferred portion.

## New-chat bootstrap sentence

`Continue the SP11 camera project from experiments/E004-front-ir-vd55g0/HANDOFF-NEW-CHAT-20260914.md on branch experiment/e004-front-ir-vd55g0. Windows is authoritative; SP11/SP7/PiMaster only; Linux SecureISP runtime is not authorized. First verify HEAD/origin + Golden safety + verify_e004dh.py, then integrate the Windows-proven SWABF/C3E8/CD90 stages into the offline parity worker and close the 644x604 full-frame differential without removing SP11_WORKER_ESWAB_PENDING until it passes.`
