# E004hs — original three-callback SPMI interface and complete direct controller-call audit (OFFLINE PASS)

**2026-09-20.** The planned new live debugger setup was blocked BEFORE any fresh Windows boot or new SP7 KD connection. This stage therefore completed a **distinct, original OEM ARM64 offline audit ONLY**. The lower-layer WinDbg runbook is retained below as an **unexecuted proposal**; the controller timer filter has NOT been verified against a real Windows controller-positive hit or timer transaction. SP11 remains on the SAME protected Golden Linux boot. Do not label E004hs a new KD session or a timer first-writer result.

## New original-driver source findings

The original SHA256-pinned `qcspmi8380.sys` WDF interface output at stack base `sp+0x110` publishes **THREE adjacent bus-facing functions**: `+0x28 → qcspmi8380+0x13a0` (standalone read), `+0x30 → +0x1660` (direct write) and `+0x38 → +0x1920` (masked read–modify–write). The **first read callback at +0x13a0** is an additional entry beyond E004hl/E004hq's focus on the two write-capable slots. Its normalized direct call to the same controller at **+0x15b4** sets `w0=1`, meaning software READ, not a possible independent writer of `0x93` through this particular direct call.

A scan of **all executable sections of that exact original ARM64 image** identified exactly FOUR direct `bl` callsites to common controller `qcspmi8380+0x64d8`:

| Original SPMI callsite | Immediate enclosing original callback | Controller `w0` | Operation in original code |
| --- | --- | --- | --- |
| `+0x15b4` | standalone interface read `+0x13a0` | 1 | Read |
| `+0x1870` | direct interface write `+0x1660` | 0 | Write |
| `+0x1b38` | masked interface `+0x1920` | 1 | Read first byte |
| `+0x1b70` | masked interface `+0x1920` | 0 after preceding successful read | Write recomposed byte |

The masked path branches away from its write when the earlier controller read returns nonzero; `+0x1b54..+0x1b64` combines old byte, caller mask and requested byte, and its `+0x1b70` direct controller call reuses the preceding success return in `w0`. This enumerates **the original image's direct calls only**, not indirect calls, other drivers/bus engines, pre-OS firmware, or proof any specific interface entry was ever invoked.

All four callsites use the same controller-entry argument registers: `w0` operation (0 write, 1 read), `w1` upstream control argument, `w2` normalized bus, `w3` normalized SID, `w4` composed register start, `x5` data pointer and `w6` byte count. These values **differ from the incoming packed-selector/mask calling conventions at provider callback entries**. This original whole-driver map makes the unexecuted common-controller observer a genuinely different, potentially broader instrument than the consumed +0x1660/+0x1920 entry watches. Its synthetic filter accepts only WRITE and a 1–256-byte start-address span overlapping `ee3e..ee41`; original code has NOT been proved incapable of calls with longer sizes. The offline calculation is not a live WinDbg filter test, and a controller software request would not alone verify PMIC silicon completion or light safety.

Run the source-pinned offline audit:
```sh
python3 experiments/E004-front-ir-vd55g0/e004hs-early-common-spmi-controller-timer-watch/verify_contract.py
python3 experiments/E004-front-ir-vd55g0/e004hs-early-common-spmi-controller-timer-watch/test_contract.py
```

The original SPMI hash, 51 selected ARM64 operation/interface/callsite opcodes, entire original executable's direct-controller caller set, prior consumed E004hr result and explicit no-live-session/no-native-IR limits are verified. **51 in-memory original opcode mutations and 22 synthetic timer-filter positive/negative/input cases PASS.** This is an offline original software-routing result. **First `0x93` timer writer, actual live controller request, independent physical emitter current/irradiance/pulse and autonomous host-failure off remain UNKNOWN.** E004fs/E004ge gate remains BLOCKED; Linux emitter/flash/PAM OFF.

## Unexecuted live-controller experiment proposal (NOT an observed trace)

# E004hs — fresh early COMMON SPMI controller timer-write observer

**PREPARED; NOT RUN.** Unlike consumed E004hp (direct callback +0x1660) and E004hr (alternate masked callback +0x1920), this distinct observation will attach to their ORIGINAL SHARED CONTROLLER HELPER `qcspmi8380+0x64d8`, including both provider paths if they reach that controller. No Camera preview, flash/PMIC/LED command, manual register write, kernel install or Linux IR action permitted. One fresh SP11 Windows boot only, then independent protected Golden return.

Original SHA-pinned qcspmi8380.sys: direct callback +0x1660 prepares w0=0 (software write), w1=original upstream argument forwarded, w2=normalized bus, w3=normalized SID, **w4=16-bit register address**, x5=buffer, **w6=byte count** before bl +0x64d8 at +0x1870. The alternate masked callback +0x1920 calls the SAME +0x64d8 controller helper for one-byte READ at +0x1b38 (w0=1), and on successful read constructs a byte, calls controller helper again with w0=0 at +0x1b70 (write). Hence a controller-entry observer must select w0=0 AND an address range using **w4 + w6**, not incorrectly use the alternate callback's w4 (mask), not the direct callback's incoming w2 packed selector. Controller prologue at +0x64d8 saves w4 as w22, w6 as w26; neither original interface callback identity is an independent host-failure emitter cutoff.

Preboot guards: SP11 tracked-clean synced original branch, protected Golden v19c, EFI BootOrder and direct one-time Windows 0006 check-only, camera idle, original kernel and saved GRUB unchanged; SP7 KD stopped/new unique directory and log. Start SP7 KD with local-only original key BEFORE one-time Windows boot. At first KD pause confirm BOTH modules absent then `sxe ld:qcspmi8380; g`. At original SPMI module-load pause (prior to natural device initialization) disassemble ORIGINAL `u qcspmi8380+0x64d8 L8`, `u qcspmi8380+0x64dc L5` and validate expected prologue. Arm two separate code breakpoints before resuming:
- PERSISTENT CONDITIONAL timer-span *write* observer at ORIGINAL `+0x64d8`: `bp /w "(@w0 == 0) && (@w6 >= 1) && (@w6 <= 256) && ((@w4 & 0xffff) <= 0xee41) && (((@w4 & 0xffff) + @w6) > 0xee3e)" qcspmi8380+0x64d8 ".echo E004HS_COMMON_CONTROLLER_TIMER_WRITE_SPAN; .time; r w0; r w1; r w2; r w3; r w4; r w6; r lr; gc"`. Real timer span positive only if marker emitted while control/prologue validated. `w0=0` classifies original controller SOFTWARE write. Do not log x5/payload, read PMIC flash state, or hold an active transaction at a manual pause.
- Separate UNFILTERED ONE-SHOT positive control at ORIGINAL `+0x64dc`: `bp /1 qcspmi8380+0x64dc ".echo E004HS_COMMON_CONTROLLER_NONTIMER_POSITIVE; .time; r w0; r w1; r w2; r w3; r w4; r w6; gc"`. This sits AFTER PACIBSP: do NOT infer raw original caller from its potentially pointer-authenticated LR. This control can hit a read or write; classify w0. The timer filter at +0x64d8 must REMAIN ACTIVE and resolved after the positive, never use /1 on timer filter. Use individual WinDbg `r w0` etc. (never combined malformed form).

If the positive-control one-shot misses, filtered breakpoint fails/resolves elsewhere, or the debugger command syntax errors, report observer **INCONCLUSIVE**, don't claim no writes. No matching timer marker with a valid controller positive plus active timer breakpoint only bounds NO OBSERVED timer-span controller write during this natural Windows boot/idle window, not before module load/pre-OS/firmware/reset, other bus engines, a disabled emitter, or actual physical PMIC write. A matching marker is a SOFTWARE controller request; do NOT assert first writer without earlier init coverage/payload/readback, or optical safety.

At bounded natural Windows idle before any Camera UI, manually pause, inspect `.time; .lastevent; bl`, clear ALL breakpoints/load exception, close original log and `g`. Normally reboot Windows to protected Golden Linux and stop KD; independently check NEW Golden boot ID/GRUB/EFI/order/camera idle/clean tracked repo before filing original SP7 log evidence. No KDNET key or proprietary OEM PE may enter Git. E004fs/E004ge physical emitted-current/irradiance/pulse/autonomous host-failure qualification remains BLOCKED; Linux emitter/PAM OFF.
