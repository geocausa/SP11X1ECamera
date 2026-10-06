# E011IP — zero enumeration fields to 0x160A260 frontier

PASS. E011IP proves the E011DV-published 18832-byte enumeration buffer remains source-owned zero through the accepted `0x600368` return, then executes the helper's zero-backed field loads. The signed byte at offset `0x2828` is zero, so `0x5F9610` branches to `0x5F9684`; `x20` becomes zero and execution stops before `0x5F968C` reads global `RVA 0x160A260`.

NEXT E011IQ resolves that global using accepted authority first, Ghidra second, and the Windows KD oracle only if required. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
