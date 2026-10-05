# E011GT — CAB288 local formatting to CAD1F0 call frontier

E011GT executes the source-owned helper-local writes at `0xCAB288/0xCAB28C` and the deterministic format path under receiver flags `+0x28 = 0`, byte `+0x39 = 0x73`, and result `+0x48 = 1`. E011GA placement authority resolves receiver `+0x8` as receiver-relative `+0x4c0`. The path computes `w24 = -1` and reaches the exact call tuple at `0xCAB3EC -> 0xCAD1F0`: `x0=receiver+0x460`, `x1=helper-local+8`, `x2=0`, `x3=receiver+0x20`, `x4=receiver+0x4c0`.

The call is not executed. E011GU executes only the zero-count fast path and continues to the second `CAD1F0` call frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
