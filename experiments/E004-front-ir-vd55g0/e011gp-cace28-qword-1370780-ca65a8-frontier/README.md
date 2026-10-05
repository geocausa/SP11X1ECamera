# E011GP — CACE28 qword authority to CA65A8 call frontier

The previously unresolved receiver-relative `+0x648` qword is source-owned, not a new native runtime secret. Accepted E011FO gives the second formatter's `x3` as image RVA `0x1370780`; the original `0x7AC38` wrapper saves that `x3` in the exact stack slot propagated by E011FP/FU/FX into receiver `+0x18`. Therefore the qword consumed at `0xCACE28` is exactly image RVA `0x1370780`.

Four source-exact placements execute the original read at `0xCACE28` through `0xCACE44`. The value is retained in `x20` and receiver `+0x40`; known receiver fields produce `x0=36`, `w1=115`, `w2=0`, and `w21=0x7fffffff`. Execution stops at `0xCACE48` before calling leaf helper `0xCA65A8`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
