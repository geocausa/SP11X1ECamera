# E011IL — outer epilogue/cookie return to 0x5F8EA8 frontier

PASS. E011IL executes the original `0x60079C..0x6007C4` epilogue, reuses the accepted opaque process-cookie contract at `0x11F0`, confirms the cookie failure path is not entered, restores the saved frame and entry SP, and returns to the accepted E011DV caller site at `0x5F8EA8`. `x0` carries the nonzero owned object pointer.

NEXT E011IM executes the parent compare/store/status branch. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
