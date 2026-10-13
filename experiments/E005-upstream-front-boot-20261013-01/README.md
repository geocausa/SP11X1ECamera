# E005: isolated upstream front26 boot, identity and runtime PM

Hypothesis: the fully built 7.2 source26 graph, joined to the retained
E003b/native power sequence in sensor25, can boot on SP11, register the
IMX681 on CCI1/master1 and shut its rails, MCLK4 and reset down cleanly
through ordinary sensor runtime PM. This run does not stream or capture.

This is a temporary headless boot. The generic new kernel lacks the
Golden-specific Surface Aggregator/audio/touch integration; it is not a
daily-system parity qualification. OS suspend/hibernate is excluded.

## Evidence reused

Source/build checkpoint: 1a6d3ca196010d2265ba30f13cd7b57904471fe8.
See docs/UPSTREAM-FRONT-GRAPH-BUILD-20261013.json and
docs/UPSTREAM-IMX681-POWER-VALIDATION-20261013.json.
Use retained endpoint23, FLL24, power25 and full graph26.
Do not repeat isolated regulator provider runs or rediscover proven wiring.

Kernel release: 7.2.0-sp11-upstream-front26.
Image SHA256: 70116a152dd25b9b3a4351a07006996639e5274fe340aaf6d047c1ec5b79b040.
DTB SHA256: 2168463ae4b8bab65f47b1ee2c86e5710c6d78004f6edc9dba751cac8297bddf.
The generated initrd and installed files are pinned before arming.

## Changes and expected observations

prepare-package.py installs only a distinct module release and decoded
copies of existing Wi-Fi firmware in the kernel-version-specific firmware
directory. The new kernel lacks firmware decompression; its WCN7850 PCI ID
requires ath12k_wifi7. These normal Wi-Fi dependencies remain only on SP11.
No proprietary camera firmware, calibration or tuning enters the package.

A copied mkinitramfs and copied distribution hooks omit the distribution's
blanket Qualcomm firmware sweep. System hooks, common firmware and original
mkinitramfs stay untouched. NVMe, Wi-Fi and PCI power-sequencing dependencies
are verified before installing an unarmed menu entry.

install-candidate.py creates a separate /boot/sp11-upstream-front-20261013-01
directory, conditional observer/return units, an independent180-second
return timer, private evidence directory and a distinct GRUB menu entry.
It does not arm or reboot. Golden v19c assets/default/module tree and daily
branch remain protected. No modules are loaded in the current Golden boot.

The one-use observer starts only with the exact boot token, entry and
kernel release. The attempt marker is consumed before camera modules load.
The new kernel boots with camera modules blacklisted; explicit requests
then load CCI, PHY, IMX681 and CAMSS. Expected: IMX681 model0x0681, registered
media graph, runtime suspended, both child rail num_users0, MCLK4 references0
at the retained19.2MHz rate, reset237 read low, and clean module unloading.
Cached regulator microvolts are not electrical voltage measurements.

## Rollback and limits

Golden stays the saved default. GRUB's next_entry is used once only.
The observer's ExecStopPost requests Golden on success or failure; the
independent timer requests Golden after180 seconds without needing network.
panic=30 covers kernel panic. These userspace mechanisms cannot recover a
pre-userspace hard lock; no hard-lock recovery claim is made.
A consumed attempt is never rearmed or retried in the same boot.

Retain detailed logs/media metadata on SP11. Commit only derived results,
source and permitted pins. Record candidate/returned boot IDs and protected
asset hashes after the run, retire the one-use entry/units, and leave no
pending boot. Registration/runtime PM does not qualify RAW timing, streaming,
DMA stop/reopen, privacy behavior, hardware ISP/libcamera/IPA or Windows1:1.
Both private startup consumers and all14 release categories remain open.

## Initrd preparation correction

The first initrd stage stopped before boot: its local Wi-Fi hook assumed a
positional argument under set -u. The distro invokes hooks with no arguments.
The fixed hook uses ${1:-}. recover-initrd.py reconciles every installed
module against the qualified build and every decoded Wi-Fi file against
the original installed compressed file before writing a fresh initrd02
stage. The failed stage is preserved and no runtime attempt was consumed.
