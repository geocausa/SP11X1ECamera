# E004gs — independent Windows PMIC timer-initialization diagnostic

Identity NEW, separate from consumed E004gb. User explicitly authorized SP11 reboot and SP7 KDNET. Previous E004gb scripts, original Windows capture, and hardware writes must not be replayed or modified.

## Stage 1: passive Windows boot, no camera preview

Confirm SP11 is on its unchanged protected Golden Linux and current branch is clean/synchronized. Preserve original EFI BootOrder, one-shot Direct Windows EFI entry and GRUB saved Golden entry. On SP7 use existing KDNET *connection configuration only* with fresh E004gs logs; do not run or modify E004gb observer scripts. Boot Windows once using one-time BootNext. Verify actual Windows state and debugger attachment. Do not start Capture/Camera or request flash/emitter. Identify the **fresh** actual PMIC module base, only then derive current code addresses from the SHA-pinned original image. Read-only initial debugger inspection: loaded module identity, timer-handler RVA 0x26d50 and 0x26f30, flash timer wrapper RVA 0x4dd0, PMIC helper RVA 0x23968, PMIC timer dispatch table RVA 0x39470, and current PnP/power state. Never infer the module base from consumed E004gb.

Potential bounded fresh KD breakpoints: both PMIC timer callbacks and flash timer wrapper; record arguments, caller stack and return only, at most 64 total hits, no writes/injected errors/forced strobe. The Windows camera must not be started as part of the initial passive stage. Disarm breakpoints, stop KD, save original redacted diagnostics in new evidence. If KD link not available or any guard fails, abort diagnostics, return via ordinary Windows restart to unchanged Golden default, and report the exact unmet prerequisite. Do not reuse E004gb trace/capture.

## Required return and safety

Persistent GRUB saved_entry stays sp11-audio-fullio-v19c, no persistent EFI BootOrder or flash DT change, Windows BootNext consumed. After Windows reboot, verify Linux new boot ID, unchanged Golden kernel, no camera module/node/process, unchanged branch/evidence and no native emitter activation. Never arm Linux IR or install 0003/0004 during this run. A Windows software timer request is NOT proof of autonomous PMIC shutoff or calibrated optical power. Physical emitter gate E004fs/E004ge remains BLOCKED.
