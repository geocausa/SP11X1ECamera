# E003i continuation handoff — 2026-09-05

This file is the durable restart point for a fresh ChatGPT conversation. It intentionally distinguishes **proved**, **implemented but not runtime-tested**, and **still open** items.

## Size erratum — E003i-T

This handoff contained an arithmetic typo in the TL_BG raw-size summary: `768 × 0x50` is **`0xF000` (61,440)**, not `0x25800` (153,600). The stage-N parser code and `PARSER-PROOF.json` were already correct. E003i-S later proved bytes `0xF000..0x25800` are zero in all six Linux live generations and both preserved Windows live dumps. E003i-T therefore corrects the production snapshot ABI to `0xF000` raw / `0xF020` including the 32-byte generation header. Historical `0x25800` lines below describe the superseded mistaken assumption.

## Repository / machine state

- Branch: `experiment/e003-front-imx681-cphy`
- Base HEAD before this handoff: `7415398e392fef258df0769ffaa7471e2716deff` (`camera: decode Titan680 Tintless BG raw stats`)
- SP11 is back on persistent Golden Linux after the one-shot Windows oracle.
- Golden kernel: `7.1.5-sp11-render-parity-v4+`
- Golden cmdline includes `clk_ignore_unused pd_ignore_unused`.
- GRUB saved entry: `sp11-audio-fullio-v19c`; `next_entry` empty.
- `qcom_camss`, `imx681`, and `ov13858` are unloaded on Golden.
- SP7 KD was explicitly stopped after the oracle; no KD process intentionally remains.
- The repo has substantial old untracked build/runtime debris. Do not mass-add or clean it. Stage only files created for the active checkpoint.

## Major runtime closure already achieved

The bounded Linux six-frame request path is closed by the 0076 runtime:

- DQBUF indices `[0,1,2,3,0,1]`
- sequences `[0,1,2,3,4,5]`
- request6 executed
- RT-CDM stopped at `last_userdata=6`, `error=0`, `faulted=0`
- the earlier A3 failure was a 1 s userspace DQBUF watchdog failure, not a kernel/IQ failure; 0076 used a 5 s diagnostic watchdog and passed.
- Camera one-shot boots must inherit Golden `clk_ignore_unused pd_ignore_unused`; the missing flags caused an intermittent early DPU/SMMU/soft-lockup boot failure.

## E003i productionization checkpoints

Current source progression under `e003i-front-native-productionization/`:

- `a-source-audit`: exact successful CAMSS oracle reconstructed from true Golden.
- `b-dual-source-foundation`: rear + front dual-camera source/DT foundation.
- `c-provider-control-plane`: removed disposable firmware/sysfs/module-param one-shot control plane.
- `d-v4l2-iq-ingress`: standard V4L2 execute-on-write IQ capsule ingress.
- `e-template-free-capsule`: no 41,088-byte captured capsule template dependency.
- `f-native-iq-backends`: banks/scalars/LSC/GTM producer classes isolated.
- `g-cleanroom-lsc-upstream`: clean-room pre-Tintless front producer from tuning + physical OTP.
- `h-integrated-lsc-chain`: removed captured pre/output mesh and staging dependencies.
- `i-cleanroom-tintless`: complete validated front Tintless path clean-room; active native DeviceMFT boundary is empty. Outer-wrapper closure checkpoint `12eb61e`.
- `j-cleanroom-gtm`: GTM curve math/Titan680 packing clean-room; still requires live TMC/ADRC request state. Checkpoint `bba6f8f`.
- `k-cleanroom-lsc-backend`: pure Linux/Python LSC backend, no DeviceMFT and no Unicorn. Checkpoint `89ae3a8`.
- `l-deferred-live-iq-ingress`: R4-only preprime + deferred R5/R6 production at their real steady gates. Checkpoint `7fb6b33`.
- `m-stats-only-lsc-request-state`: LSC live boundary reduced to raw Tintless stats + ordinary trigger/tuning state; x1/x3/x4/wrapper/core are constructed locally. Checkpoint `13a76f2`; geometry-label correction `a2c901e`.
- `n-titan680-tlbg-parser`: clean Titan680 raw Tintless-BG parser. Current HEAD `7415398`.

## Titan680 raw Tintless-BG parser — PROVED

Static reverse engineering of the exact Surface `QcDeviceMFT8380.dll` recovered the Titan680-specific Tintless parser.

Validated format:

- front Tintless grid: **32 × 24 = 768 regions**
- each region covers **120 × 90 pixels**
- hardware raw record: **0x50 bytes**
- complete client-13 raw payload: **768 × 0x50 = 0x25800 bytes (153,600)**
- parsed Tintless record: **0x64 bytes**
- captured x2 bounded read authority: **0x12bec bytes**
- Titan680 parser identifies hardware as `0x60800` and produces parsed flags `3`, matching the Windows x2 object.
- stage-N inverse/forward proof reconstructs synthetic raw from Windows parsed fixtures, reparses it, and reproduces R4/R5/R6 x2 byte-for-byte over the exact bounded authority.

Linux CAMSS already has the required hardware path:

- per-slot TL_BG coherent DMA exists already
- programmed into Windows-matching BUS client **13**
- completion group/event **0x0e** exists already
- aux buffer is `0x48000`, larger than the required `0x25800`
- slot ownership prevents rebinding until TL_BG completion retires

Therefore a new stats hardware engine is NOT required. The production task is to snapshot/expose the existing first `0x25800` bytes at the TL_BG completion boundary with an explicit generation tag.

## Fresh Windows live TL_BG oracle — PARTIALLY CLOSED

A one-shot Windows boot was entered through the existing EFI `BootNext` direct-Windows entry. Persistent Golden was not replaced.

Live camera host on this Windows boot:

- process command: `svchost.exe -k Camera -s FrameServer`
- live PID observed: decimal `14804` / hex `0x39d4`
- corresponding EPROCESS during this boot: `ffffb48fcb91f100` (VOLATILE; re-resolve next boot)
- DeviceMFT base during the later gated runs: `0x00007ffe660e0000` (VOLATILE; re-resolve every process/boot)
- `TitanStatsParser::ParseTintlessBGStats` RVA: `0x5f09d0`
- Tintless wrapper RVA: `0xc95fd0`

Dynamic proof obtained:

1. Parser hit exposed raw client-13 pointer in X1 and parsed-output pointer in X3.
2. The next observed Tintless wrapper call received **exactly that parser output pointer as its X2 stats object**.
3. Thus the parser output is passed directly to Tintless; there is no additional hidden conversion between Titan680 parser and the clean LSC backend's x2 contract.

Fresh raw captures retained on SP7 (do not delete):

`C:\Users\SurfacePro7\Documents\KDNET\Codex\E003I-TLBG-CFG1.bin`
- bytes: `153600`
- SHA256: `2457121f3708a446f6bd669a0e10e87150af50cb4aeca2727086dc082daf3eec`

`C:\Users\SurfacePro7\Documents\KDNET\Codex\E003I-TLBG-HIT2.bin`
- bytes: `153600`
- SHA256: `fd15ce6cca96fad1a81c8618749706d3097643f3ff66aa3c7ba41296e969849c`

`C:\Users\SurfacePro7\Documents\KDNET\Codex\E003I-PARSED-HIT1.bin`
- bytes: `76780` (`0x12bec`)
- SHA256: `88a1537c668ee0e759edb3cdf91554f68164accf6b464943dd8f35db837ad3d3`

Historical Sept-4 x2 hashes do NOT match the fresh parsed object because this is a different live scene. Do not use cross-run x2 hashing to infer request identity.

### Timing correlation still OPEN

Static CamX evidence says stats consumers use a `request - maximumPipelineDelay` source and the accepted Linux runner has priming replay0 → replay1 → replay2 → replay3 → steady request4. This makes a four-request mapping highly plausible, but the exact live cycle-2 parser-hit count before the first Tintless request was **not successfully persisted** during the final gated KD attempt.

Do NOT promote the inferred mapping to authority until the gated dynamic correlation is re-run or another exact request-id source proves it.

A clean gated helper exists on SP11 Windows:

`C:\Users\geoca\Documents\E003H-WinRT-TwoCycle-Gated.ps1`

It performs cycle1, stops, prints `E003H_GATE_WAIT`, waits on stdin, then starts cycle2. Recommended next oracle procedure:

1. Start the gated helper as a persistent pipe job.
2. Let cycle1 finish and wait at `E003H_GATE_WAIT`.
3. Confirm FrameServer PID (`svchost -k Camera -s FrameServer`) and resolve EPROCESS + DeviceMFT base in KD.
4. Open a KD logfile on SP7 (`.logopen /t ...`) so evidence survives PiSlave job-store restarts.
5. Arm process-scoped parser breakpoint at `base + 0x5f09d0` and Tintless breakpoint at `base + 0xc95fd0`.
6. Use a KD pseudo-register parser counter. Auto-log every parser `(N, raw pointer, parsed pointer)` and every Tintless `(N, x2 pointer)`, then `gc`.
7. Resume target, release gated helper stdin, let cycle2 run once.
8. Close KD log and archive it. The number/order of parser outputs before first Tintless closes the request-delay mapping.

The last attempt was intentionally abandoned after PiSlave/KD job-store instability; no conclusion was drawn from the incomplete log.

## Next Linux implementation after timing oracle

The next kernel/source stage should be bounded and transport-only:

1. At TL_BG event `0x0e`, while the aux slot is still ownership-protected, copy/snapshot exactly the first `0x25800` bytes.
2. Associate the snapshot with an explicit monotonically increasing hardware/source generation; never expose an unlabeled "latest stats" buffer.
3. Provide read-only userspace access through the existing V4L2 surface (a bounded compound payload/event/ring is preferred over a private ioctl).
4. Preserve current teardown semantics: unsafe teardown pins ownership until reboot; do not free/reuse uncertain DMA.
5. Userspace: raw TL_BG → stage-N parser → stage-M stats-only LSC backend → stage-E template-free capsule → stage-L deferred V4L2 IQ ingress.
6. R4 remains preprimed for the bounded compatibility path until the exact request-delay/source mapping is closed. R5/R6 can then be generated from their proven delayed live stats source at the existing steady gates.

## Separate remaining GTM production gap

GTM/Titan680 curve generation is already clean-room (`j-cleanroom-gtm`), but the production backend still needs **live Linux TMC/ADRC request state**. Do not confuse this with the now-closed GTM math. After live TL_BG/LSC plumbing, trace/acquire the request-local TMC state required by stage J, then feed both generated LSC and GTM into the same template-free capsule composer.

## Runtime safety contract remains

- Windows is the oracle; Linux must be compared against it, not approximated.
- Use hardened camera boot params: `clk_ignore_unused pd_ignore_unused`.
- Unique one-shot GRUB entries for risky runtime experiments; persistent saved entry stays Golden.
- One authorized helper invocation per candidate boot.
- No same-boot retry after helper/hardware ambiguity.
- On failure: archive immediately, reboot Golden, analyze offline.
- For actual capture helper use a persistent PiMaster job so command timeout cannot kill a pinned kernel state.

## Fresh-chat first commands

On SP11 Linux:

```bash
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
git status --short --branch
git log -12 --oneline --decorate
cat experiments/E003-front-imx681-cphy/e003i-front-native-productionization/o-live-stats-handoff/CONTINUATION-HANDOFF-20260905.md
```

Then verify Golden (`sp11_entry=7.1.5-sp11-fullio-v19c`, camera modules absent, GRUB `next_entry` empty) before any new runtime action.
