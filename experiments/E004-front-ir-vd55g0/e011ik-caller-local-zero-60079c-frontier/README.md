# E011IK — caller local zero to 0x60079C epilogue frontier

PASS. The source-owned caller local at `[sp+4]` is qualified as zero: `0x6003D8` selects `WZR` on the accepted nonzero allocation path and `0x600400` stores it, with no later direct store before the consumer. E011IK executes `0x6006DC` and confirms the zero branch at `0x6006E0` selects `0x60079C`.

NEXT E011IL advances through the outer epilogue and accepted opaque process-cookie checker. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
