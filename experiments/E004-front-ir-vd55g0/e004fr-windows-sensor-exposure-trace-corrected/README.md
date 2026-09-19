# E004fr — corrected bounded Windows VD55G0 sensor-exposure observer

Status: **PASS — CONSUMED 2026-09-19; GOLDEN RESTORED.**

E004fq is **consumed and aborted**. Its single Windows boot established the fresh auxiliary-sensor driver address and passed all idle target/skip checks, but the live `arm.kd` hit KD's `Malformed string` parser error because an inner `.printf` string was unescaped inside the outer breakpoint callback string. No sensor observation or preview occurred. The debugger was cleared and SP11 returned to Golden; E004fq must not be retried or reused.

E004fr preserves the E004fq read-only capture scope (one normal Surface IR Camera Front preview; at most 12 frames/five seconds; no properties set and no images saved). The only KD generator repair is escaping the callback's internal `.printf` quotes for the outer `bp0` command, plus changing its final command to **remain broken** after installing the breakpoint. The observer must not run until the operator confirms an error-free arm, exactly one expected breakpoint and no unrelated breakpoints. The module base printed from E004fq is historical and **must be rediscovered on any new Windows boot**.

Offline evidence: E004fr `verify_static.py` passes against the exact pinned installed Windows sensor package and driver. SP7 PowerShell generated `arm.kd` with escaped `\"` inner quotes; the emitted `arm.kd` contains no standalone `g` and ends at `E004FR_ARMED_STAY_BROKEN`. **This only validates generated text, not that the command is accepted by a live KD parser.** The first actual parser check requires a fresh, separately checkpointed Windows one-shot; any parser error consumes that identity.

## Fresh execution contract (future)

1. Require clean project head synchronized with GitHub, protected Golden, empty GRUB `next_entry`, no camera modules/nodes/clients, and unchanged BootOrder. Verify the SP7 true-PTY KD host, and stage the exact E004fr scripts and their checksums. Check the Windows direct BootNext helper in read-only mode.
2. Checkpoint/push the prepared candidate, then use the existing **one-shot** Windows BootNext only for a **fresh E004fr** attempt. Never reuse E004fq or its live module address.
3. Break into Windows via SP7 KD, resolve the current `surfacecamauxsensor8380` base, generate E004fr commands for that actual address, run `validate.kd` while idle, and require all target/skip markers with no parser error.
4. Run `arm.kd` while the target is still broken; require `E004FR_ARMED_STAY_BROKEN`, no parser error, and `bl` showing exactly one enabled breakpoint at the fresh module-base-plus-`0xa350`. On any failure: `bc *; bl; g`, no capture, return Golden; this identity is consumed.
5. Only if the arm gate passes, manually send `g`, invoke `capture.ps1` **once** on SP11 Windows, then break back in on SP7. Clear breakpoint(s), verify empty `bl`, resume. Do not retry the capture in the same boot.
6. Reboot to protected Golden, archive exact KD and bounded capture evidence; verify BootOrder, Golden, camera idle, and retire the one-shot. Review observed exposure/strobe/timer policy **before** any Linux emitter activation.

No protected camera or unsigned DSP worker is loaded in this stage. Native Linux illumination remains **OFF** until exposure/pulse envelope and a defensible timeout policy are closed. The parallel HLOS pixel-processing work is separate and provides no emitter authority.

## Actual live result — PASS, retired

One fresh Windows BootNext on 2026-09-19. The fresh `surfacecamauxsensor8380.sys` module base was `fffff8013c080000`; observer at `fffff8013c08a350`. Idle target/skip validation passed, then KD accepted the correctly escaped callback as exactly one enabled breakpoint while the target remained broken. After explicit resume, one ordinary read-only Surface IR Camera Front preview acquired **12 NV12 644×604 frames** and stopped successfully. The standard Windows exposure API reported Auto=True and 5,000 ticks (0.5 ms) throughout; this API readback does **not** directly describe sensor coarse integration.

The KD observer logged **114 contiguous register-write events** during this one bounded session. Registers `0x044e/0x044f` (coarse exposure low/high bytes) were each written 16 times, yielding 16-bit coarse line counts `32, 47, 71, 154, 243, 357, 853, 1234, 1866, 1955, 1955, 1955, 1955, 1955, 1955, 1955`. The `0x0458/0x0459` frame-length writes produced nine `1955`-line configurations then seven `2000`-line configurations; analogue gain register `0x044d` also varied. These are **16 register-programming groups, not an asserted one-to-one mapping to the 12 acquired frames**. Two lifecycle writes targeted `0x0201` and `0x0202`. No `0x0467..0x046e` GPIO/strobe write appeared during this bounded preview; the sensor's static first-start configuration remains separate authority.

After capture, KD `bc *; bl` displayed an empty breakpoint list, Windows resumed and rebooted to Golden Ubuntu. Fresh Linux boot ID `c0f10a70-e405-4917-b34f-e2e113e640a0`, saved GRUB default `sp11-audio-fullio-v19c`, empty next_entry, BootCurrent `0005`, unchanged BootOrder `0005,0004,0000,0001,0002,0006`, no camera nodes/modules/clients, overlap guard PASS. E004fr is **consumed**; no same-boot retry. Native illumination remained OFF.

`evidence/ORIGINAL-WINDOWS-LOGS.zip` preserves the **original raw KD log** (SHA-256 `e51fe8ac39c4dcada637bf914c18c891ab81d27e974bffc0bd330f4201223722`) and **original UTF-16 Windows capture report** (SHA-256 `079dd61665adbfe21c5f5316078e9cebb91d5462ddb05e4be79dda5233cebb78`). The latter was recovered via a temporary **read-only** NTFS mount, which was unmounted immediately afterwards. Run `python3 verify_result.py` to check exact original hashes, all write counts, exposure/frame-length sequences, capture bounds and cleanup; `evidence/RESULT.json` records the bounded interpretation.

**Remaining gate:** sensor write calls and static ST strobe semantics do not electrically measure IR pulse width, radiated power, or prove fail-safe PMIC current/timer/timeout handling. Existing E004fp timer-register absence was limited to one Windows preview. Review physical line-time/pulse limits and a conservative independent shutdown mechanism before considering a separate Linux emitter candidate. The HLOS worker is still an ordinary offline pixel-processing prototype, not a face-unlock implementation.
