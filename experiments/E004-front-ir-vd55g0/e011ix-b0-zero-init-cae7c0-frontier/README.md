# E011IX — 0xB0 zero initialization to 0xCAE7C0 frontier

PASS. E011IX follows the accepted nonzero allocation branch, executes the exact source zero-initialization loop, proves all 176 allocated bytes are cleared, preserves the allocation in `x24`, and reaches `0x5BE3B8 -> 0xCAE7C0` with `x0=allocation+0x30`, `x1=0x80`, `x2=RVA 0x13DBC80`, and `x3=-1`. The call is not executed here.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011IY source-qualifies the `0x13DBC80` string, executes only this bounded construction copy, and stops before the following imported-function call.
