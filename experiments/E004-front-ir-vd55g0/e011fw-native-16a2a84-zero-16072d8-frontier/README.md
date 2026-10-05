# E011FW: native `0x16A2A84` zero branch to `0x16072D8` frontier

Status: **PASS_NATIVE_16A2A84_ZERO_BRANCH_TO_16072D8_FRONTIER**.

E011FW joins bounded same-boot SP7 KDNET authority to the accepted E011FV path. The 4-byte writable cell at RVA `0x16A2A84` measured `0` both before and after one successful front-only NV12 1920x1080 reader start in the same process/module context. The older E011DY loader-model zero is therefore no longer being used as native authority for this cell.

Across four source-exact cases, original `0xCAD8B8` reads the qualified zero, the `0xCAD8BC` nonzero branch is not taken, and original `0xCAD8C0`/`0xCAD8C4` form the next dependency address. Sixteen new original instruction visits are qualified in total and 2,620 altered contracts are rejected. Execution stops before `0xCAD8C8`; the 16-byte value at RVA `0x16072D8` is not read or claimed yet.

The Windows oracle used one new front-camera start and one controlled reboot back to Golden Linux. No rear-camera start or kernel build occurred. NEXT **E011FX** resolves the current native `0x16072D8` value; its older file-initial pointer-pair geometry remains model/source evidence only until then. Native rear runtime remains denied.
