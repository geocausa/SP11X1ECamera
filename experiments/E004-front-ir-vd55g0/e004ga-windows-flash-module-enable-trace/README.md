# E004ga — fresh bounded Windows flash enable and shutdown-request trace

Status: **OFFLINE PREPARED / NOT ARMED OR CONSUMED.** This is a fresh experiment; E004fp/E004fr and all prior Windows/camera attempts are consumed and must never be reused.

## Specific question

During one *ordinary Windows OEM-controlled* Surface IR Camera Front preview, does the installed PMIC masked-register helper access flash module enable `0xee46`, channel-enable mask `0xee4e`, individual trigger selectors `0xee4a–0xee4d`, timer fields `0xee3e–0xee41` and common selector `0xee67`? Record each successful or failed paired read-modify-write byte on these **13 target addresses** only, including normal stop when observed. The earlier E004fp Windows trace checked only timers, four selectors and common bit, so its absence of module/channel writes was not evidence about these registers.

This Windows observation must not modify flash, sensor, PMIC or exposure settings from KD. The supplied `capture.ps1` performs one ordinary OEM Windows IR preview only: at most 12 frames or five seconds, no image saved, property setters forbidden. Any OEM illumination remains under **Windows' own driver**; no Linux emitter test is attempted. Windows request/return status can indicate *software* shutdown attempts, never measured optical light-off, autonomous stuck-trigger protection, current/irradiance or safe exposure.

## Gates and recovery

Before boot: require SP11 protected Golden with clean tracked tree, no active camera, an empty GRUB next_entry, unchanged BootOrder, and HEAD exactly pushed to GitHub; test SP7 KD true PTY, original debugger credentials and independent SP7→SP11 recovery. Check the one-shot Windows direct BootNext helper with `--check-only`, then commit/push the exact prepared scripts and bound. Do not reuse E004fp's historical module base: rediscover the current installed `qcpmic8380.sys` module base under KD after Windows boots and verify the exact driver identity against existing pinned E004fi authority.

`generate_kd.py --pmic-base FFFFFFFFFFFFFFFF --output DIR` requires a real current, aligned module base. Its `validate.kd` runs *while the target is broken*, without hardware writes or preview; require all target/skip tests and packed-register recovery. `arm.kd` installs exactly two auto-resuming hooks at current module-base+`0x23af8` and +`0x23bec`, then stays **broken** for operator confirmation of breakpoint list and parser success. **Only then** explicitly resume, invoke `capture.ps1` once and stop the reader. On a parser/breakpoint/capture error, consume this experiment and return Golden without retry. After capture, break into KD, `bc *; bl` (empty), resume Windows, reboot Golden, verify BootOrder/GRUB/camera idle and retire the one-shot. Original KD/capture logs must be hashed before editing or paraphrasing.

The masked-register helper may not service every module/enable register. A missing record means only **no hook hit during this bounded preview**, never proof that a timer, module or channel state was globally unchanged. It does not establish physical LED current or fail-safe off. No Linux flash patches may be installed or native emitter activated based on this test; E004fs remains BLOCKED.
