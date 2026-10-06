# E011KA — factory epilogue return-object frontier

PASS. E011KA completes the `0x5BDE08` factory epilogue from `0x5BE374`, restores all saved nonvolatile registers and `SP`, executes `AUTIBSP/RET` at `0x5BE38C..0x5BE390`, preserves `x0=RVA 0x17A70D0`, and returns to the accepted E011DS caller resume RVA `0x5B826C`. Execution stops there before caller logic.

NEXT E011KB qualifies the restored caller `x26` destination, stores the returned factory object at `[x26+0x70]`, and stops before `0x5B8274` reads returned-object offset `+0xC0`. No new camera Start, reboot, rear runtime, or kernel build is used.
