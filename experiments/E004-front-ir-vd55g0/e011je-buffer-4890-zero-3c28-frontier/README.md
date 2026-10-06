# E011JE — buffer +0x4890 zero to +0x3C28 frontier

PASS. E011JE reuses the accepted zero-backed enumeration-buffer lifetime to qualify `buffer+0x4890 = 0`, executes `0x5BE470/0x5BE474`, and stores zero to outer local `x26+0x474`. Execution then reaches `0x5BE47C` with constant `0x3C28` selected, before forming the next source pointer.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JF qualifies the `buffer+0x3C28` source for the exact `0x5BE480 -> 0xCAE7C0` bounded copy.
