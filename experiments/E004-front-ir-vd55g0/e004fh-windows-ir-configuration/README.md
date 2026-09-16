# E004fh: installed Windows IR configuration

**PASS installed configuration; Golden return verified.** No camera/flash commands or debugger attach.

Hypothesis: the installed QCOM0C27 flash device uses the 700 mA setting found
in the exact exported extension INF. This checks binding and configuration,
not measured light current, PMIC channel mapping, pulse duration or duty cycle.

The collector queries present flash/PMIC PnP devices, selected driver and parent
properties, flash-related values under the flash device's registry key, and
hashes of five named installed drivers. It creates one JSON evidence file at
C:\SP11Camera\E004fh\configuration.json and refuses to overwrite an existing
result. It does not open a camera, issue a flash ioctl or attach a debugger.

Baseline: camera repository 7623ae06d844894cbe55cc77c7ccc987d2a347f7;
Golden 7.1.5-sp11-render-parity-v4+, saved FullIO v19c, empty GRUB next_entry,
boot ad301aa8-ce0f-49c9-9ba9-5e254a8aea50. No camera modules or processes.
E004fg module remains uninstalled. Historical five dirty files are preserved.

Boot with the existing verified tools/sp11-camera-windows-oracle-oneshot.sh:
UEFI BootNext selects the direct Microsoft loader once; persistent BootOrder
and Golden payload are unchanged. After collection use ordinary Windows restart
to return to persistent Golden, verify the overlap guard, and archive only the
bounded derived JSON. If PiMaster is temporarily absent, allow network startup
and check independently from SP7; do not infer a crash from a timeout.

## Result

Windows build 26200, boot 2026-09-16T12:29:29Z, reports flash device
ACPI/QCOM0C27/19 healthy, service qcFlash, version 1.0.4258.7900. The device's
Device Parameters registry key contains IrLedCurrentMilliampere DWORD 700.
The running flash, PMIC, PMIC Apps and PMIC GLink driver files all hash-match
the exported local archive. This is live configuration evidence, not a current
measurement or proof of the physical LED channel.

The initial file-based script launch was blocked by Windows' default execution
policy. All policy scopes were Undefined, with no organization policy set. The
same read-only queries were executed as ordinary inline shell commands; no
execution policy was changed. The collector's System32/drivers hash list is
empty because these drivers live in DriverStore. A follow-up Win32_SystemDriver
query resolved their real paths, and Get-FileHash produced driver-bindings.json.

JSON evidence is normalized from tool output. Original Windows files remain at
the recorded paths; their byte hashes are retained in WINDOWS-RETURN.txt.
SP11 returned to Golden boot 98b67104-e3eb-4091-8b6c-180fd054bd06, no camera
modules/processes, empty next_entry, unchanged persistent UEFI BootOrder.
E004fh is complete; do not overwrite its Windows output or reuse the identity.
