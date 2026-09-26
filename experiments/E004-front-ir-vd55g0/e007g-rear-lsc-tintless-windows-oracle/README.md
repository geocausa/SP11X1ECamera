# E007g — rear OV13858 LSC/Tintless Windows oracle

Parent Git: `e0d0fa8c` (E007f rear DMI provider integration PASS).

Status: **PREPARED / WINDOWS ONE-SHOT NOT YET CONSUMED**.

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
