# E004fj: idle Windows PMIC state observation

**PASS live idle PMIC state; Golden return verified.** Read-only observation of 32 bytes in the confirmed PMIC driver.
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

## Live result and handling of the initial lookup failure

The initial debugger module list did not contain qcpmic8380. The command file
aborted on symbol resolution before its trailing g, so the target was manually
resumed immediately. A later read-only .reload populated the module list; it
was followed by g. A final brief break read the planned 32 bytes using the
verified current module base and resumed in the same command line. No data was
written and no camera was opened. All failed and successful output is retained.
For future KD work, refresh module lists before resolution and monitor errors:
a trailing g inside a command file is not a reliable recovery after syntax or
symbol failures. This identity is consumed and must not be reused.

The initialized driver global contains register-access identifier 1, initialization
argument 1, old table NULL, new table base+39470, and pairing bytes [3,2,4,4].
Together with E004fi this confirms Windows selects sources 1 and 4 for logical
LED1, with nominal splitting of the configured 700 mA into 350 mA each.
This is software configuration evidence, not measured optical power or pulse
limits. The emitter remained under ordinary Windows ownership; no flash request
was sent by this experiment.

SP11 resumed successfully over PiMaster and restarted to Golden boot
15ea0beb-c042-4a22-a833-97b8c0e019e8. BootOrder is unchanged, next_entry empty,
and camera nodes/modules/processes absent. After target shutdown, only this
experiment's debugger child process was stopped on SP7. The original host log
hash is in DEBUGGER-CLOSED.txt. Archived text is normalized for line endings and
trailing whitespace; verify_state.py checks the snapshot against the discovered
module base, exact driver hash and Golden-return evidence.
