# E011JQ — CA34A0 wrapper to CA3450 frontier

PASS. E011JQ executes the caller transfer `0x5BE660 -> 0xCA34A0`, source-pins the exact accepted wrapper body, preserves callback RVA `0xF7B310`, executes only the wrapper prologue, and stops before `0xCA34AC -> 0xCA3450`. The callback registration itself is not executed here.

NEXT E011JR must establish the retained encoded-exit-table state before executing `0xCA3450`; E011DU is the accepted existing-table registration authority, but current runtime table state must be inherited explicitly rather than guessed. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
