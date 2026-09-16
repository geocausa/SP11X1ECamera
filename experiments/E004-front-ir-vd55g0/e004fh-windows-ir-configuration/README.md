# E004fh: installed Windows IR configuration

Prepared read-only collection; no camera/flash commands or debugger attach.

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
