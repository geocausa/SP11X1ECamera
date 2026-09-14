# E004dm — Windows CTrigleAdjV1 fallback port for front RGB

Status: **PASS OFFLINE / production source patched / no camera runtime**.

E004dl exposed the remaining front-RGB AWB parity hole at live generation G21. Linux failed closed with `RG/BG point outside stateful CTrigleAdjV1 mesh` while the pinned Windows implementation has two additional stateful fallback paths that had deliberately not been ported.

## Windows authority

Pinned binary:

`QcDeviceMFT8380.dll`

SHA-256:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Relevant implementation is `CamX::CTrigleAdjV1::GetCurrentTriangle` at RVA `0x6bfcc0`, with `GetTriangleRatio` at RVA `0x6c0ae0` in the existing Ghidra authority cache.

The decompile proves four selection behaviors for this profile:

1. normal stateful contained-triangle selection;
2. multi-side neighbor walking (already ported earlier, e.g. EO `10 -> 8 -> 16`);
3. **anti-cycle fallback**: per-call triangle visit counters are incremented on every move; when a target triangle is visited more than twice, Windows returns that triangle with a flag causing `GetTriangleRatio` to use the triangle **centroid** instead of the outlying decision point;
4. **boundary fallback**: if the walk reaches neighbor `255`, Windows keeps the boundary triangle as current state, selects the two vertices on that boundary edge, projects the calibrated RG/BG point onto the edge, and interpolates only those two vertex curves. `Run` handles the `0xff` selector return with weights `(w, 1-w, 0)`.

Windows also contains a generic two-boundary/all-three-side pair resolver. The pinned IMX681 topology has 18 triangles with one boundary neighbor, 26 with zero, and **no triangle with two boundary neighbors**, so that generic corner is unreachable for this profile. Its literal logic is retained in the production source but is not needed for profile acceptance.

## E004dl G21 closure

The consumed E004dl F1 evidence was reduced to a compact G1..G21 fixture. At G21:

- raw decision: RG `0x3eeb99c7`, BG `0x3f2385de`;
- dynamic calibration slot `2` / region `2`;
- calibrated mesh point: `0x3eecc4d1 / 0x3f27afef`;
- current triangle entering the call: `4`;
- exact Windows walk: `4 -> 36 -> 4 -> 36 -> 4 -> 36`;
- visit counts at fallback: triangle 4 = `2`, triangle 36 = `3`;
- Windows therefore selects **centroid fallback triangle 36**;
- interpolation centroid bits: `0x3e96e1b5 / 0x3f4cc848`;
- exact float32 weights: `0x3eaaaaab / 0x3eaaaab2 / 0x3eaaaaa4`;
- GainAdj final RGB: `1.0 / 1.0 / 1.0` bit-exact;
- published gains: `0x400b1531 / 0x3f800000 / 0x3fc86348`.

This is why the prior Linux `seen`-set termination was wrong: Windows deliberately tolerates an oscillating neighbor walk and resolves it by centroid interpolation.

## Reachable two-vertex regression

A deterministic point outside triangle 0 boundary edge 2 exercises the ordinary Windows two-vertex path using real profile tuning:

- point bits `0x3f103665 / 0x3f3fb49f`;
- pair `(vertex 0, vertex 2)`;
- projection weight `0x3f01fc71`;
- selector mode `two_vertex`;
- selector return semantics `0xff`;
- third vertex/weight are absent/zero.

This validates the reachable boundary path separately from G21's centroid fallback.

## Regression safety

The production-source implementation is replayed against every preserved Windows selector/GainAdj oracle used by the accepted front stack:

- EG: 8/8 requests bit-exact;
- FA: 9/9;
- FH: 15/15;
- FW: 18/18.

Normal requests remain in `triangle` mode, preserving triangle identity, vertices, float32 weights, final GainAdj RGB and published gains bit-for-bit.

## Production integration

Only committed `src/front-imx681` runtime source is changed; historical E003 experiment code remains untouched. `live-iq-producer.py` now also emits `awb_selection_mode` and selector visit counts into runtime evidence so centroid/two-vertex fallback use is observable.

No Linux camera runtime, Windows boot, module load, GRUB mutation, SecureISP action or protected-path action is performed by E004dm.

## Next gate

Build a fresh production package from the committed source and run a fresh one-shot RGB alternating soak. The soak must remain no-retry, require neutral topology between every leg, and return to protected Golden on any fail-closed condition.
