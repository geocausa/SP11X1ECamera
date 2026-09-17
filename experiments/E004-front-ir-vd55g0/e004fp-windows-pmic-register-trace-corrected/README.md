# E004fp: corrected Windows PMIC flash register-level trace

Status: **PREPARED / not executed.** Fresh identity after consumed E004fo.

E004fo was consumed by an idle KD parser error and then revealed two observer defects during non-acceptance same-boot diagnostics: the PRE old byte was addressed incorrectly, and the POST filter used `w24` after that register had been clobbered. E004fp carries only the mechanically corrected observer into a new Windows one-shot. No E004fo runtime identity, module base, breakpoint file, or same-boot state may be reused.

## Question

During one ordinary bounded Windows IR preview, what bytes does the installed `qcpmic8380.sys` actually read/modify/write for timer `0xee3e..0xee41`, trigger `0xee4a..0xee4d`, and common trigger bit `0xee67`, and what are the write return statuses?

## Corrected static hook authority

The hash-pinned E004fi disassembly mechanically establishes the register lifetimes used by this observer:

- `+0x23af8`: post-read site; target register is `w24`, mask is `w23`, old/read byte is `[sp+0x18]`, requested byte is `[sp+0x10]`, read status is `w0`.
- `+0x23aac`: `w27 = w24 | (...) << 16`, preserving the original register in low 16 bits.
- `+0x23b0c`: `w24` is overwritten/reused and therefore is not valid for the post-write filter.
- `+0x23bcc`: final RMW byte is stored through `x21`.
- `+0x23bec`: post-write return site; register is `w27 & 0xffff`, final byte is `[x21]`, write status is `w0`.

The generator uses KD-compatible single `&`/`|` boolean composition and emits an idle test for packed-register recovery in addition to target/skip filter cases. `verify_static.py` checks those register-lifetime facts against the archived disassembly and verifies Python/PowerShell generator equivalence.

## Live contract

1. Start protected Golden Linux with clean tracked tree, branch HEAD exactly pushed, empty GRUB `next_entry`, unchanged persistent BootOrder, no camera nodes/modules/processes.
2. Arm one fresh direct Windows BootNext with `tools/sp11-camera-windows-oracle-oneshot.sh`; this boot is E004fp and is consumed as soon as Windows/debug execution may have started.
3. On SP7 KD, `.reload`, verify the fresh `qcpmic8380.sys` base and exact installed binary authority, generate new command files for that base, and execute `validate.kd` while idle.
4. Require all target/skip markers plus `E004FP_DRY_POSTREG ... reg=ee4a`, with no command/parser error. Any debugger command error consumes E004fp: remove breakpoints if needed, resume, and return Golden without a retry.
5. Only after a clean idle gate, arm both auto-resuming hooks and run `capture.ps1` exactly once: Surface IR preview, at most 12 acquired frames / five seconds, CPU memory, no property SETs, no saved image.
6. Break in once after capture, remove both breakpoints, verify an empty breakpoint list, resume and reboot/shut down normally.
7. Return immediately to Golden Linux; archive KD and capture evidence, verify BootOrder/Golden/camera-idle state, retire E004fp, then commit/push.

## Acceptance

Pair relevant PRE/POST records by order/register, retain read/request/final bytes and bus return status, and state exactly which timer/trigger/common registers were observed. Timer absence during this bounded session is only bounded-session evidence. Physical current, optical power, pulse width and actual sensor exposure remain unmeasured unless separately proven. Linux emitter activation remains prohibited by E004fp itself.
