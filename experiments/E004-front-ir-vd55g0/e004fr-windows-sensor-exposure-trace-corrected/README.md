# E004fr — corrected bounded Windows VD55G0 sensor-exposure observer

Status: **PREPARED / OFFLINE STATIC PASS / NO E004fr WINDOWS BOOT OR CAPTURE**.

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
