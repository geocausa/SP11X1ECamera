# E007g — rear OV13858 LSC/Tintless Windows oracle

Parent Git: `e0d0fa8c` (E007f rear DMI provider integration PASS).

Status: **PASS — WINDOWS ONE-SHOT CONSUMED / CLEAN REPLAY 15/15 EXACT**.

## Goal

Capture one fresh request-labelled OV13858 rear mode-1 LSC/Tintless sequence from the original Windows stack and use it to validate the existing clean-room/native Tintless + LSC chain for rear parity.

This is necessary because the historical `E003H_20260902_TINTCTX` raw capsule was deleted by System Restore and only a subset was later carved. Its derived oracle remains accepted, but the full request5→request6 raw state needed for a new clean-C differential is no longer present.

## Reused accepted boundaries

The experiment intentionally reuses two already-accepted mechanisms rather than inventing new hooks:

1. **Rear stream holder:** the E004nw/E004ny Windows WinRT path selecting exactly:
   - `Surface Camera Rear`
   - `Color`
   - `VideoRecord`
   - `NV12 3840x2160`

2. **LSC oracle hooks:** the FP request-labelled DeviceMFT hooks:
   - entry RVA `0x88e1e8`
   - post-staging RVA `0xa03b34`

At entry the hook reads the request label, the current Tintless stats pointer and request trigger block. At post it dumps only the bounded LSC staging region.

## Capture scope

For requests R4..R18 inclusive, private Windows evidence contains only:

- Tintless stats: `0x12bec` bytes;
- trigger block: `0x100` bytes;
- final LSC staging: `0x18a0` bytes.

No optical frame bytes are read or stored by the holder. The WinRT reader only counts 3840x2160 frame handles.

The CDB script automatically clears both breakpoints, closes its log, detaches and exits when R18 staging is captured.

## One-shot discipline

The holder uses `FileMode.CreateNew` for `SCRIPT-ENTRY-CONSUMED.marker`. A consumed or uncertain identity cannot be rerun.

The stream waits at `WAIT_START` before `StartAsync`. CDB must be attached and both breakpoints armed before `START.GO` is created.

No future Scheduled Task trigger is permitted. If a logged-on-user task is used, it is registered without a trigger, started exactly once, and unregistered immediately.

## Existing rear clean authority

No calibration recapture is required:

- rear tuning `com.surface.tuned.rfc_ov13858.bin`
  SHA-256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`;
- retained OV13858 runtime calibration slot
  SHA-256 `fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18`;
- rear/default LSC41 tree and golden calibration arithmetic are already source-locked;
- clean Tintless mode-2 core is already independently implemented;
- Titan680 LSC staging pack and GIC wire alias are already closed.

## Acceptance plan

After return to Golden Linux:

1. structurally validate all 15 request captures;
2. derive LSC0/LSC1/LSC2/GIC from each staging buffer;
3. reconstruct rear request-local pre-Tintless mesh from rear tuning + calibration + trigger + rear geometry;
4. feed captured Tintless stats into the clean native core sequentially;
5. require byte-exact LSC0/LSC1/LSC2/GIC against Windows for the complete captured sequence.

Only then may the rear LSC/Tintless producer be considered closed for E006g binding.

No Linux camera runtime, DMI submission or RT-CDM submission is authorized by this oracle.

## Actual one-shot result — PASS

The prepared identity was consumed once on the original SP11 Windows stack. The gated holder remained at `WAIT_START` until ARM64 CDB had both DeviceMFT hooks armed and enabled. Only then was `START.GO` created.

The rear holder selected exactly `Surface Camera Rear / Color / VideoRecord / NV12 3840x2160`, started successfully, acquired 139 valid 4K frame handles in the bounded five-second interval, stopped successfully and disposed the reader/capture objects. It did not copy optical frame bytes.

CDB captured exactly 15 entry hits and 15 post-staging hits for R4..R18, with no `E007G_FAIL`, then cleared both breakpoints, closed its log and detached automatically at R18. The private capture consists of:

- 15 × 76,780-byte Tintless stats objects;
- 15 × 256-byte trigger blocks;
- 15 × 6,304-byte LSC staging objects.

The Windows-private 45-file manifest SHA-256 is
`65318dade08d8655edb3d5e4ec25c797ae21819baad0be59e540a18d45056ecf`.
No raw capture payload is committed.

SP11 then returned normally to protected Golden Linux, boot ID
`ce993597-725f-4899-a3f9-1372a46121ee`, kernel
`7.1.5-sp11-render-parity-v4+`. Persistent BootOrder remained
`0005,0004,0000,0001,0002,0006`, GRUB saved entry remained
`sp11-audio-fullio-v19c`, `next_entry` was empty, and the overlap guard passed with no camera node/module/process.

## Clean rear replay — PASS

`replay-clean.py` closes the complete rear LSC/Tintless producer chain against the fresh private oracle:

1. exact rear/default LSC41 tree selection from SHA-pinned `rfc_ov13858`;
2. exact float32/float64 generic interpolation arithmetic;
3. exact rear golden/OV13858 calibration-slot application;
4. generic source-locked LSC geometry resampling;
5. clean native mode-2 Tintless core initialized from the preserved OV13858 mode-1 `x1` configuration;
6. exact wrapper temporal carry;
7. Q10 conversion, Titan680 LSC0/LSC1/LSC2 packing and proven GIC wire alias.

The generic geometry implementation first differential-checks byte-for-byte against the already-accepted front implementation. It then derives the rear geometry directly from the source equations:

- full: 4076×2806;
- output: 4064×2286;
- crop: (6,260);
- half-resolution mesh steps: 128×96;
- centering residual: 16×9.

The fresh request sequence exercises more than one tuning state:

- R4: direct CCT leaf `0x2a0`;
- R5/R6: exact interpolation across `0x29e -> 0x2a0` (4200→4800 CCT gap);
- R7..R18: direct CCT leaf `0x29e`.

For **every request R4 through R18**, clean generated LSC0, LSC1, LSC2 and the GIC alias are byte-identical to Windows. LSC2 is zero throughout, while LSC0/LSC1/GIC evolve request-to-request exactly with the captured Tintless state.

Therefore the rear OV13858 mode-1 **LSC/Tintless algorithm/state/wire producer is closed byte-exactly** for this full sequential oracle. The remaining engineering work is production binding/scheduling, not algorithm reconstruction.

The Windows partition was mounted read-only only for offline validation and was unmounted immediately afterwards. No Linux camera runtime, DMI submission or RT-CDM submission occurred.
