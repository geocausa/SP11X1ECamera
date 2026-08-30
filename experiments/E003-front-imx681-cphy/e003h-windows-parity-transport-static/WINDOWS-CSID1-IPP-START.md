# E003h — same-machine Windows CSID1 IPP start oracle and Linux 0042 parity delta

Date: 2026-08-30

## Result

The previous VFE1 Epoch0 timeout is **not** explained by a missing Windows IFE `0x804` MMIO start action. Exact same-machine `qccamisp8380.sys` plus the live IFE `0x804` KD capture prove the IFE command only stores `camera_use_case=2` and `frames_to_skip=0`; its only downstream consumers special-case use-case 4. For the front use-case 2 session the ordinary per-resource frame-drop values are used, and the existing VFE1 BUS oracle already proves period `0`, pattern `1` for all nine active clients.

The next upstream boundary is CSID1. Here opcode `0x804` has materially different semantics: when `frames_to_skip == 0`, the CSID dispatcher calls `DAL_csid_start`, which iterates every active CSID path and invokes the path-enable HAL. The front session uses path ID 5, IPP.

No new powered Linux camera run was performed for this checkpoint.

## Exact Windows identities

`qccamisp8380.sys`:

- bytes: `376560`
- SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`

Same-machine CSID/IFE companion KD log:

- `windows-ife-cdm/raw/E003H_IFE_CDM_COMPANION_EXACT_20260828.log`
- bytes: `136290`
- SHA-256: `3d9d1beb74641c8e699f045abcc79384c52d5365780dd3134a99ab0dbd42e194`

Same-machine route MMIO capture:

- `../e003g-windows-csid-vfe-oracle/raw/E003G_ROUTE_ORACLE_20260828.log`
- bytes: `2457712`
- SHA-256: `fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca`

Fail-closed derived oracle:

- `extract_csid1_ipp_start_oracle.py`
- `windows-csid1-ipp-start-oracle.json`
- oracle SHA-256: `01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda`
- schema: `sp11-e003h-windows-csid1-ipp-start-v1`
- `accepted: true`
- `runtime_authorized: false`

## IFE `0x804` closure

The separate fail-closed IFE `0x804` oracle proves:

- manager call opcode: `0x804`;
- IFE dispatcher branch RVA: `0x2366c`;
- payload word0: frames to skip;
- payload word1: camera use case;
- exact front live values: `skip=0`, `usecase=2`;
- branch has no direct MMIO and no hardware-start call;
- the only two downstream field consumers override frame-drop state only for `camera_use_case == 4`;
- front use-case 2 therefore uses ordinary resource frame-drop fields already represented by the captured BUS recipe.

Consequence: do **not** invent an IFE start MMIO write or a new Linux IFE-start runtime stage from this opcode.

## CSID `0x804` exact start semantics

The CSID dispatcher compares opcode `0x804` at RVA `0x218d8` and enters the branch at RVA `0x21b4c`. It stores the two logical fields and, when `frames_to_skip == 0`, calls `DAL_csid_start` at RVA `0x24260`.

`DAL_csid_start` iterates the active path array and invokes the registered path-enable callback. IPP is path ID `5`.

The full-CSID path-enable HAL at RVA `0x1b3d0`, path-5 branch RVA `0x1b48c`, writes in this exact order:

1. CSID1 `+0x304 = 0x00000001` — IPP control enable;
2. CSID1 `+0x0b0 = 0x3cbc601c` — IPP IRQ mask;
3. CSID1 `+0x080 = 0x00000001` — TOP IRQ mask.

The initial full-CSID builder at RVA `0x1a870` separately proves:

- CSID1 `+0x0a0 = 0x019fb800` — RX IRQ mask;
- CSID1 `+0x090 = 0x0001ffff` — BUF_DONE IRQ mask;
- CSID1 `+0x334 = 0x00130013` — IPP epoch config;
- CSID1 `+0x324 = 0` — exact zero write. The semantic register name is intentionally not promoted beyond the proven offset/value.

The captured CSID1 descriptor-1 `0x803` packet0 independently contains:

- `+0x330 = 0`;
- `+0x37c = 1`;
- `+0x380 = 0`;
- `+0x35c = 0x0eff0000`;
- `+0x360 = 0x086f0000`;
- `+0x384 = 0x0000001f`;
- `+0x388 = 0x08700f00`.

Packets 1–3 repeat the 3840x2160 crop (`+0x35c/+0x360`).

## Same-machine live cross-check

Two successful Windows live passes independently reproduce the complete front boundary:

- wrapper CSID1 IO path: `+0x004 = 0x00000101`;
- RX: `+0x200 = 0x11300000`, `+0x204 = 1`;
- IPP RAW10: `+0x300 = 0x802b2000`;
- IPP enabled: `+0x304 = 1`;
- IPP CFG1: `+0x310 = 0x00007241`;
- zero writes: `+0x324 = 0`, `+0x330 = 0`;
- crop: `+0x35c = 0x0eff0000`, `+0x360 = 0x086f0000`;
- format measurement: `+0x384 = 0x1f`, `+0x388 = 0x08700f00`;
- masks: `TOP=1`, `BUF_DONE=0x1ffff`, `RX=0x019fb800`, `IPP=0x3cbc601c`.

Do not freeze observed values at `+0x340`, `+0x398`, or `+0x39c`: static Windows code classifies them as status/timestamp/readback state. `+0x398` also changes between live passes.

## Linux 0042

Canonical patch:

- `0042-x1e-csid1-ipp-start-windows-parity.patch`
- SHA-256: `0f21697369369be11d0692268f71ea2af3768346c9a63e5eb2d03f67c57e3414`

The patch is scoped to the already fail-closed X1E80100 front mode0 predicate. It adds only the Windows-proven deltas:

- initial RX mask `0x019fb800`;
- initial BUF_DONE mask `0x0001ffff`;
- exact `+0x324=0` and `+0x330=0` writes;
- after IPP control enable, exact IPP mask `0x3cbc601c`, then TOP mask `1`;
- read-only CSID1 snapshot on the already-bounded Epoch0 timeout before teardown.

It deliberately does **not** add a CSID `REG_UPDATE_CMD` write because no such write is proven in the captured Windows CSID initial/start boundary.

Timeout telemetry reads:

- wrapper CSID1 route;
- CSID register-update readback;
- TOP and BUF_DONE status/masks;
- RX status/mask, RX CFG0/CFG1, packet count, ECC and CRC;
- IPP status/mask/control/CFG/crop/drop/format-measure state;
- raw `+0x340/+0x398/+0x39c` observations without treating them as configuration.

## Static Linux gate

`qcom-camss.ko` builds cleanly against the protected Golden build anchor:

- SHA-256: `c67ce602f88be5db2ffecd816879081d74f996f7884e8661bea252d924f7098e`
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Strict checkpatch on the git-style patch with repository-appropriate `--no-signoff`:

- `0 errors, 0 warnings, 0 checks`.

`inspect_csid1_ipp_start_linux.py` is fail-closed. Its accepted output is:

- `csid1-ipp-start-linux-inspection.json`
- SHA-256: `6d79f9ba9ff1265a372f37dd49717cf44208cbe3e413ccb3f0b0b385b3823430`
- status: `PASS`.

The inspector also copies the three touched current source files into a throwaway tree, reverse-applies `0042`, verifies forward application, re-applies it, and requires all three resulting files to be byte-identical to the current source.

## Runtime boundary

No runtime is authorized by this static checkpoint. The next mechanical step is to build and inspect an exact one-shot candidate package containing the `0042` module while preserving Golden as the saved/default recovery entry. Only after that package is fully identified and the existing provenance gate remains green should a single new diagnostic run be authorized.

If that run again reaches sensor-on but times out before VFE1 Epoch0, the new pre-teardown CSID snapshot will partition the failure:

- no RX packet activity: receiver/CSID ingress boundary;
- RX traffic but no IPP progression: CSID1 IPP configuration/start boundary;
- IPP activity with no VFE1 Epoch0: move the blocker downstream into VFE1/IFE ingress/top prerequisites.

No same-boot retry is permitted.
