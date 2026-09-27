# E008v — rear normal BF ROI stage attribution

Parent: E008u commit ee8e3683f3925422dbc73e6a2bca460044c5032c.
Status: COMPLETED, bounded stream pass; ROI intermediate not observed. See RESULT.md.

Question: Does the normal packet1→2 ROI position transition originate in
the AF/BAF ROI mapper, or in BFStats25 validation/pre-hardware handling?

Evidence: E008u's clean packet0 selector-1 DMI is 300/300 exact with the
4064x2286 active crop. Normal packet1 differs in left/top/width/height;
packet2/3 differ in top/width/height, while packet2/3/steady are equal in the
retained private corpus. IDs/flags match. A speculative vertical size fit is
not source authority and must not enter the driver.

Method: inspect same-SP11 user-mode DeviceMFT and AF source/loaded-process
ownership. If the original Windows rear4K session executes those stages, use
non-halting user-mode observation only to record the AF semantic ROI stage,
BFStats25 post-validation stage and final 25-record output for one bounded
session. Keep all raw memory, logs, DMI and optical frames private on SP11.
Commit only source-derived law and aggregate exact-comparison counts.

No on-target kernel debugger or kernel breakpoint. SP7 external KD is
available only if a separately identified kernel edge needs it. Future
scheduled Windows tasks must use the persisted atomic CreateNew entry guard
and be unregistered after one invocation.

Expected discrimination: either the upstream AF mapper changes position
between the first two normal packets, or the BFStats25 transform does. The
conclusion must be proven by request-labelled observations, not inferred
from final DMI coordinates.

Rollback: BootNext selects Windows once; persistent EFI order boots protected
Golden Linux on ordinary reboot. Do not change saved Golden GRUB entry,
Windows BCD kernel-debug policy, IR illumination, or native rear ISP runtime.
Return to Linux and verify kernel, boot identity, Golden, no camera nodes/
modules, and tracked repository status before source implementation.
