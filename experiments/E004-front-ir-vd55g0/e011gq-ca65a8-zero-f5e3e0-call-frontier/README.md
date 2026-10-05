# E011GQ — CA65A8 zero result to F5E3E0 call frontier

Four source-exact placements execute the leaf helper call at `0xCACE48 -> 0xCA65A8` with `x0=36`, `w1=115`, and `w2=0`. The original leaf path returns `0`. The parent resumes at `0xCACE4C`; the zero-result branch and nonzero retained-pointer branch are both taken, leaving receiver `+0x4c = 0` and producing the next call state `x0 = RVA 0x1370780`, `x1 = 0x7fffffff`.

Execution stops at `0xCACE90` before calling `0xF5E3E0`. Its first dependency is a 16-byte source block at RVA `0x1370780`, which E011GR must source-qualify before executing the scan.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
