# E003i-HL — fresh repeated-stream shadow R27 candidate

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HL is the fresh successor to consumed HK. The camera/package policy is unchanged: HJ production artifacts, exactly two sequential 27-frame streams, explicit `shadow` post-G3 policy, zero post-G3 physical writes authorized, and no same-stream retry.

The only intended harness repair is the pre-stream Bash bug found in HK: stream-number assignment now occurs before any expansion that references it. `invoke-twice.sh` is sourceable without executing `main`; an offline self-test overrides only the launcher function and exercises the exact live marker/variable/grep path for streams 1 and 2, including fail-closed marker reuse. ShellCheck and Bash syntax are also mandatory before prearm.

HL uses a new GRUB/cmdline/boot identity and must never reuse HK evidence or boot artifacts.
