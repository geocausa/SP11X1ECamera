# Current camera handoff — E003i DL, 2026-09-10

Read this before historical PROJECT_STATE/state sections. SP11 is back on Golden. DB attempt4 evidence is archived and the candidate boot entry/bundle are retired. No new camera run is armed. Current experiment is **DL: exact G4 replay + omitted Windows internal CapExposure stage**.

## Proven now

- Unchanged DJ/CU/CV exactly reproduce attempt4's first three sensor tuples and G4 -142.
- G4 Short convergence = 24,819,566,146; serialized T681 upper product = 6,133,333,272.
- Failure snapshots are intact and generation-matched; caller recurrence and output stay unchanged on failure.
- Windows PopulateOutput unconditionally calls CapExposure before publishing convergence. Native DJ/CG omit it.
- DC's controller cap flag and DG's post-convergence injection do not test that internal stage.
- Golden return passed; no camera modules, next_entry empty, saved FullIO v19c unchanged. Windows boot entry preserved.

## Next smallest work

Recover the **ordinary request-local internal cap bounds and branch inputs**, then implement the complete native pre-publication cap stage offline. Use the pinned archived DLL first; use the established SP7/Windows oracle tooling when runtime values are necessary. The exact target is the internal stage, not the old controller cap loop:

1. At PopulateOutput call 0x3ce03c, capture the seven compact input qwords, convergence+0x98 min/max block (seven records, stride0x50, qwords +0x18/+0x40), common +0x230 field, PredGain and cap branch inputs.
2. At return 0x3ce040, capture the matching seven output qwords and updated PredGain. Keep request identity and ordinary-preview profile explicit.
3. Recover the bounds' pre-convergence arbitration producer and any normal-profile conditional adjustment. Do not substitute serialized knees for request-local fitted bounds without proof.
4. Replay the full cap (conditional rescale/history snap, per-lane limits, lane ordering, predictive-gain update) against same-request Windows fixtures.
5. Integrate additively after native convergence and before CH arbitration; replay archived G1..G4 and the existing Windows corpora. Only then consider a fresh bounded Linux candidate.

Do not relax CH's ordinary policy-0 rejection. Do not adjust the delay solely from DQBUF timings. DB's full-tuple ioctl is much slower than CY's isolated step, and G4 brightness stays baseline-like; that association remains a separate issue to verify once the missing cap stage is closed. A later diagnostic should preserve G5/G6 even after G4 AEC fails.

## Artifacts and logistics

Repo: /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
Branch: experiment/e003-front-imx681-cphy
Runtime base: 8bc6598440f5ddeb36587e140bf64f48eaee38bf
Archive: /home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-db/attempt4-live-g4-fail-20260910T181907
DLL: /home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll
DLL SHA256: c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35

Verification: verify-dl.py, verify-cap-stage.py, REPLAY.txt, RESULT.json, CAP-STAGE-RESULT.json, SOURCE-HASHES.json.
Persist raw/proprietary material outside Git. Preserve existing untracked work. Continue front-camera scope; rear/IR and unrestricted continuous AEC are not closed.
