# E004gv — fresh early-boot KDNET PMIC initialization observation

## Hypothesis and why this is NEW

The SHA-pinned installed OEM qcpmic8380.inf declares PMIC driver service StartType SERVICE_BOOT_START, LoadOrderGroup Filter. The original E004gt KDNET trace says System Uptime **10.969 seconds** when connection was established. Consequently its post-connect breakpoints (and those in E004gs) cannot establish that initial PMIC setup was or was not executed during those first ~11 seconds. This E004gv identity targets kernel startup timing and the first timer-register writer; it does NOT rerun an OEM preview or the completed postboot hooks.

The original PMIC masked-write helper is at RVA 0x23968. Its ARM64 prologue copies caller arguments w0 (bus), w1 (SID/context), w2 (register address), w3 (mask), w4 (requested byte); both timer callbacks call it with w2 drawn from contiguous table [0xee3e,0xee3f,0xee40,0xee41]. The helper's internal read/modification invokes the raw request at RVA 0x24098, then an indirect low-level write after computing a combined bus/address selector. This identifies a distinct generic-register-writer site but does NOT prove all firmware/kernel/host routes pass through it.

## One-time experiment plan — NOT EXECUTED AT PREP

SP7: validate original new KDNET key exists locally, debugger binary and no active KD job; start a brand-new, independently logged `kd.exe -d -bonc` before Windows boots. Microsoft documents -d as breaking after the first module load on reboot; -bonc breaks as soon as the debugger session begins. The early-break condition must be *observed*, not assumed.

SP11: require clean tracked HEAD and upstream, unchanged Golden v19c, BootNext empty, no camera process, and an independent SP7 recovery path. Use the existing Golden-protecting tool for ONE Windows Direct EFI BootNext. The earliest debugger break records `.time; vertarget; lm m qcpmic8380; lm m qccamflash8380` and exact kernel uptime. If PMIC has ALREADY loaded, classify early boot initialization as MISSED, do not claim a first-writer trace, and continue Windows without any camera activation. If PMIC is NOT loaded, set `sxe ld:qcpmic8380`, resume, inspect module load BEFORE running any PMIC breakpoint; if the image loads, disassemble the live generic helper and arm a conditionally filtered, limited read-only watch for w2 addresses 0xee3e..0xee41. If load timing, address checks, debugger setup or state is ambiguous, stop the diagnostic rather than inject fault, restart drivers, force a strobe or mutate a PMIC register.

Observe idle/boot only, for at most a few minutes. Do NOT start OEM camera preview or Linux emitter; do not inject exceptions, change PMIC registers, stop or restart PMIC drivers, try a stuck-high trigger, or hold the target paused during a camera session. Clear every KD breakpoint, disable load event, close the original trace, normally reboot Windows to unchanged Golden, verify Golden with camera-idle guard, and archive original non-secret logs with SHA256. One Windows boot is consumed regardless of whether the KD initial break precedes PMIC initialization. E004gb/E004gs/E004gt consumed IDs must never be replayed.

**Evidence bounds:** A no-hit result where the PMIC was already loaded is INCONCLUSIVE for the first writer. Neither an observed software timer write nor a stored 0x93 byte demonstrates physical pulse, current, irradiance, or autonomous cutoff. E004fs/E004ge stay BLOCKED and native Linux IR/PAM remain OFF.

Official KD options reference: https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/kd-command-line-options
