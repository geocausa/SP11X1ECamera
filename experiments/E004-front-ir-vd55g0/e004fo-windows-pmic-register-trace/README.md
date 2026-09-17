# E004fo: Windows PMIC flash register-level trace

Status: **PREPARED / no live execution yet**.

E004fn proved the normal Windows IR flash request sequence at the flash driver boundary. E004fo moves one layer lower and observes only the installed `qcpmic8380.sys` masked-register helper during one ordinary bounded IR preview. It does not call a PMIC function, set exposure/current, save images, or activate anything beyond what the normal Windows camera path already does.

## Question

For the live Surface IR path, what register bytes does Windows actually read/modify/write for:

- safety timer `0xee3e..0xee41`;
- trigger selection/mode `0xee4a..0xee4d`;
- common trigger bit `0xee67`?

This gate is deliberately separate from live sensor-exposure tracing.

## Exact static hook authority

The hash-pinned E004fi disassembly shows every relevant callback calling `qcpmic8380+0x23968` with register in `w2`, mask in `w3`, and requested value in `w4`. Inside that helper:

- `+0x23af4` returns from the one-byte register read; at `+0x23af8`, `w24` is the target register, `w23` is the mask, `x21` points at the pre-update byte and `[sp+0x10]` retains the requested byte;
- the helper applies `(old & ~mask) | (requested & mask)`;
- the underlying bus write returns at `+0x23bec`; `w0` is its return status and `x21` points at the final byte submitted.

`generate_kd.py` therefore installs two auto-resuming, filtered breakpoints at exactly those post-call sites. Only the nine register addresses above are logged. Each hook self-disables at 64 relevant hits. The idle validation script exercises the same debugger expression/formatter using literals and a one-byte mapped PE read before any camera open, then deliberately stays broken so the validated observer can be armed without a second debugger break-in.

## Live contract

1. Start from protected Golden Linux, clean tracked tree, HEAD exactly at pushed branch tip, empty GRUB `next_entry`, unchanged persistent BootOrder.
2. Create a fresh Windows direct one-shot with `tools/sp11-camera-windows-oracle-oneshot.sh`.
3. On SP7 KD, `.reload`, verify exact installed `qcpmic8380.sys` hash/base, generate the command files for that fresh base, and run `validate.kd` while idle.
4. Only if validation is clean, arm both hooks and resume.
5. Run `capture.ps1` exactly once: Surface IR preview, maximum 12 acquired frames / five seconds, CPU memory preference, no property SETs and no saved image.
6. Break in, remove both breakpoints, verify empty breakpoint list, resume and shut Windows down normally.
7. Return immediately to Golden Linux, archive evidence, verify BootOrder/Golden/camera-idle state, then retire and push.

No same-boot retry. A debugger command error consumes the Windows identity; remove breakpoints/resume and return Golden. No Linux illumination is authorized by this experiment.

## Acceptance

The result must mechanically pair relevant PRE/POST records, retain bus return status, and state exactly which timer/common/trigger registers were observed. Absence of a timer write during the bounded session is evidence only for that session; it does not by itself prove reset/default timer state. Physical current, optical power and pulse width remain unmeasured.
