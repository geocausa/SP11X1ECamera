# E004fj: idle Windows PMIC state observation

Prepared read-only debugger observation of 32 bytes in the confirmed PMIC driver.
Hypothesis: SP11 selects the four-channel table at driver RVA 39470 and pairing
bytes [3,2], which E004fi maps conditionally to LED sources 1 and 4.

Use SP7's existing KDNET configuration locally without printing its secret. Start
a true PTY debugger only after Windows has booted and the driver's file hash is
confirmed. Commands read the driver state at RVA 3b8c8, print the expected table
address and resume immediately. No camera opening, flash ioctl, register write,
code change, breakpoint installation or protected Linux runtime is involved.
If the driver has not initialized this state, record inconclusive; do not trigger
a camera merely to populate it. Use a fresh follow-up identity if needed.

SP11 may briefly lose PiMaster while broken in; SP7 is the debugger control plane.
Keep an automatic g at the end of the command file. Do not leave the target
stopped. After collection, ordinary Windows restart returns to permanent Golden.
Verify empty GRUB next_entry, unchanged BootOrder and no camera activity before
closing. Retain compact log and hashes, not a kernel dump or credential.

Baseline camera HEAD c0df76c13f25addf51cc6da1b5da20961352cd19. Golden boot
98b67104-e3eb-4091-8b6c-180fd054bd06, FullIO v19c, no camera nodes or modules.
E004fg remains an offline, uninstalled patch. E004fi remains conditional until
the snapshot resolves actual branch selection; physical optical behavior and
pulse limits remain separate questions.
