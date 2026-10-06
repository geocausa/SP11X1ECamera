# E011JH — selector zero/native globals to 0x5BE510 frontier

PASS. Source audit finds nine exact materializations of zero-fill selector block `RVA 0x1798508`, all immediate readers and no direct writer/address escape; bytes `+1/+2` are therefore zero. E011JH reuses accepted native `0x160A218=0` and `0x1608858=1`, executes the source branches, and reaches `0x5BE510` with `w23=0`, `w20=0`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JI follows that selector decision tree to the x19 function-pointer block frontier.
