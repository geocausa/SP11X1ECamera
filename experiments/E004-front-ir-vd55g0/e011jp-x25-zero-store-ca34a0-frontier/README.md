# E011JP — x25 zero store to CA34A0 call frontier

PASS. E011JP source-qualifies `x25` as RVA `0x18A2968` from its original prologue construction and accepted local save/restore, executes the idempotent zero store at `0x5BEDA4`, follows `0x5BEDA8 -> 0x5BE658`, forms `x0=RVA 0xF7B310`, and stops before `0x5BE660 -> 0xCA34A0`.

NEXT E011JQ qualifies that helper call before execution and advances only to the following `0xCE7A48` frontier. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
