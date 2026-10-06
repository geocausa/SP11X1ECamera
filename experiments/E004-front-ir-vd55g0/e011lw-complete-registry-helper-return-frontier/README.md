# E011LW — complete registry helper return

PASS. The accepted cached registry object is reloaded, the 0x220-byte local frame is restored, the source-exact stack-cookie epilogue completes under the accepted cookie contract without exporting the cookie, saved registers are restored, and `0x5B80A8` returns at `0x5B9068` to original caller RVA `0x5DE844` with x0 still identifying registry object RVA `0x17A4230`.

NEXT E011LX follows the caller's descriptor-count reduction only far enough to the second registry-helper call frontier. Product scope remains normal front/rear RGB parity.
