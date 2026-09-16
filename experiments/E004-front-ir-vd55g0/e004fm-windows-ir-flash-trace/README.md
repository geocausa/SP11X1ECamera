# E004fm: bounded Windows IR flash-request observation

Prepared, not yet consumed. Baseline camera HEAD 75a7991; permanent Golden
FullIO v19c, boot 15ea0beb-c042-4a22-a833-97b8c0e019e8. No native driver installed.

Question: which PMIC input selector and trigger/timer payloads does ordinary
Windows IR preview actually request, and what exposure values does its standard
controller report? E004fl establishes exact helper and payload formats.

Use one fresh Windows boot and one bounded normal Surface IR Camera Front
preview (at most 12 acquired frames or five seconds after StartAsync). Keep
Windows' existing exposure/current controls unchanged. No proprietary/protected
control SETs or direct flash requests. No images are saved. capture.ps1 reads
standard ExposureControl properties and timestamps and always attempts teardown.
Each WinRT wait has a 30-second deadline; any failure consumes this identity.
Controller readings are not sensor-register or physical pulse measurements.

Verify the installed qccamflash8380 hash matches E004fh. On SP7, verify no other
KD/WinDbg process, reuse the configured KDNET transport privately, and refresh
the module list before locating qccamflash8380. Use the fresh verified base.
Install one auto-resuming breakpoint at its helper RVA 4ac0. Log command/size
and at most 20 payload bytes only when pointer and size are valid, then resume.
Disable this breakpoint after 32 hits. Do not modify registers, arguments,
return values, device state, code semantics or camera control values. Debugger
pauses can affect frame timing; this run does not prove uninstrumented latency.
Never leave SP11 stopped: monitor via SP7 and send g immediately on command errors.

After preview cleanup, remove this experiment's breakpoint, resume, record
Windows recovery and restart normally into Golden. Verify saved_entry unchanged,
next_entry empty, BootOrder unchanged and no camera modules/processes/nodes.
Stop only this experiment's owned KD process after target shutdown. Retain the
bounded request log, script, hashes and conclusions. Never same-boot retry.

Exposure API reference:
https://learn.microsoft.com/en-us/uwp/api/windows.media.devices.exposurecontrol?view=winrt-26100

Remaining limitations: absent timer requests do not prove timer hardware state;
standard exposure may be unsupported/stale; the exact input-selector request
does not alone measure pin routing. If insufficient, next use a fresh identity
for the smallest remaining observation. Linux illumination and SecureISP stay off.
