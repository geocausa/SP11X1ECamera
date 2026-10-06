# E011HS — CA9880 return 26 through CA94E8 epilogue to CA634C frontier

Four exact placements load receiver `+0x20 = 26` at `0xCA9880`, execute the original `CA94E8` epilogue, restore the saved register frame and stack pointer, and return at `0xCA9898` to `0xCA634C`. Execution stops before the caller instruction.

E011HT reuses the accepted E011FZ caller frame/register authority to qualify the caller branch chain and output-buffer zero write, stopping before the new `[sp+0x478]` dependency. No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
